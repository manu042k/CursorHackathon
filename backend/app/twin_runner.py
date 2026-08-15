"""Twin runner: same roster and seed, one variable on B. Architecture §7."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from app.agents.port import DecisionPort, decide_validated
from app.contracts import (
    AgentDecision,
    AgentDecisionRequest,
    AgentLog,
    CreateExperimentRequest,
    Roster,
    RosterAgent,
    RunId,
    Status,
    VariableType,
)
from app.history import history_summary
from app.market import Market, market_from_roster, parse_price_delta
from app.roster.fixed_grok_bot import build_roster
from app.store import write_artifact

ALIGNMENT_ERROR = "alignment_broken"
FLOAT_EPS = 1e-9

OnRound = Callable[[RunId, int, float, float], Awaitable[None] | None]
OnDecision = Callable[[dict[str, Any]], Awaitable[None] | None]


@dataclass
class TwinResult:
    id: str
    status: Status
    error: str | None
    experiment: CreateExperimentRequest
    roster: Roster
    opening: dict[str, float | dict[str, float]]
    run_a: dict[str, Any]
    run_b: dict[str, Any]
    call_order: list[tuple[str, str, int]] = field(default_factory=list)


def agent_by_id(roster: Roster, agent_id: str) -> RosterAgent:
    return next(a for a in roster.agents if a.agent_id == agent_id)


def observation_order(roster: Roster) -> list[str]:
    buyers = [a.agent_id for a in roster.agents if a.agent_id.startswith("buyer_")]
    rest: list[str] = []
    if any(a.agent_id == "competitor" for a in roster.agents):
        rest.append("competitor")
    if any(a.agent_id == "analyst" for a in roster.agents):
        rest.append("analyst")
    return buyers + rest


def check_alignment(run_a: dict[str, Any], run_b: dict[str, Any], applies_from_round: int) -> None:
    """Rounds before the intervention must match. Failure voids the causal claim."""
    if applies_from_round <= 1:
        return
    for round_n in range(1, applies_from_round):
        traj_a = run_a["trajectory"][round_n - 1]
        traj_b = run_b["trajectory"][round_n - 1]
        for key in ("share", "mrr", "current_price", "competitor_price"):
            if abs(float(traj_a[key]) - float(traj_b[key])) > FLOAT_EPS:
                raise AlignmentBroken(ALIGNMENT_ERROR)
        logs_a = [log for log in run_a["agent_logs"] if log["round"] == round_n]
        logs_b = [log for log in run_b["agent_logs"] if log["round"] == round_n]
        if [log["decision"] for log in logs_a] != [log["decision"] for log in logs_b]:
            raise AlignmentBroken(ALIGNMENT_ERROR)
        if [log["agent_id"] for log in logs_a] != [log["agent_id"] for log in logs_b]:
            raise AlignmentBroken(ALIGNMENT_ERROR)


class AlignmentBroken(Exception):
    def __init__(self, error: str = ALIGNMENT_ERROR) -> None:
        super().__init__(error)
        self.error = error


async def _run_one(
    *,
    experiment_id: str,
    experiment: CreateExperimentRequest,
    roster: Roster,
    adapter: DecisionPort,
    run_id: RunId,
    market: Market,
    forked_price: float,
    call_order: list[tuple[str, str, int]],
    on_round: OnRound | None,
    on_decision: OnDecision | None,
) -> dict[str, Any]:
    order = observation_order(roster)
    trajectory: list[dict[str, float | int]] = []
    agent_logs: list[dict[str, Any]] = []

    for round_n in range(1, experiment.rounds + 1):
        if run_id == RunId.B and round_n >= experiment.applies_from_round:
            market.current_price = forked_price

        snap_price = market.current_price
        snap_comp = market.competitor_price
        decisions: dict[str, AgentDecision] = {}

        for agent_id in order:
            agent = agent_by_id(roster, agent_id)
            status = "subscribed" if agent_id in market.subscribed else "churned"
            request = AgentDecisionRequest(
                experiment_id=experiment_id,
                run_id=run_id,
                agent_id=agent_id,
                round=round_n,
                current_price=snap_price,
                competitor_price=snap_comp,
                persona=dict(agent.traits),
                status=status,
                history_summary=history_summary(agent_logs, round_n),
            )
            call_order.append((run_id.value, agent_id, round_n))
            decision = await decide_validated(adapter, request)
            decisions[agent_id] = decision
            agent_logs.append(
                AgentLog(
                    round=round_n,
                    agent_id=agent_id,
                    run_id=run_id,
                    decision=decision.decision,
                    reason=decision.reason,
                    confidence=decision.confidence,
                ).model_dump(mode="json")
            )
            if on_decision is not None:
                maybe_decision = on_decision(
                    {
                        "run_id": run_id.value,
                        "round": round_n,
                        "agent_id": agent_id,
                        "decision": decision.decision,
                        "reason": decision.reason,
                        "confidence": decision.confidence,
                        "current_price": snap_price,
                    }
                )
                if maybe_decision is not None:
                    await maybe_decision

        for agent_id in market.buyer_order:
            choice = decisions[agent_id].decision
            if choice in {"churn", "switch"}:
                market.subscribed.pop(agent_id, None)

        competitor = decisions.get("competitor")
        if competitor is not None:
            if competitor.decision == "match":
                market.competitor_price = snap_price
            elif competitor.decision == "undercut":
                market.competitor_price = min(snap_comp, snap_price - 1)

        row = {
            "round": round_n,
            "share": market.share(),
            "mrr": market.mrr(),
            "current_price": snap_price,
            "competitor_price": snap_comp,
        }
        trajectory.append(row)
        if on_round is not None:
            maybe = on_round(run_id, round_n, row["share"], row["mrr"])
            if maybe is not None:
                await maybe

    return {"trajectory": trajectory, "agent_logs": agent_logs}


async def run_twin(
    experiment: CreateExperimentRequest,
    experiment_id: str,
    adapter: DecisionPort,
    roster: Roster | None = None,
    root: Path | None = None,
    on_round: OnRound | None = None,
    on_decision: OnDecision | None = None,
) -> TwinResult:
    if experiment.variable_type != VariableType.price_change:
        raise ValueError("only price_change is supported")
    roster = roster or build_roster(experiment.random_seed)
    opening_market = market_from_roster(
        roster, experiment.current_price, experiment.competitor_price
    )
    opening = opening_market.snapshot()
    forked_price = parse_price_delta(experiment.current_price, experiment.variable_delta)
    call_order: list[tuple[str, str, int]] = []

    write_artifact(experiment_id, "experiment", experiment.model_dump(mode="json"), root=root)
    write_artifact(experiment_id, "roster", roster.model_dump(mode="json"), root=root)

    run_a = await _run_one(
        experiment_id=experiment_id,
        experiment=experiment,
        roster=roster,
        adapter=adapter,
        run_id=RunId.A,
        market=opening_market.copy(),
        forked_price=forked_price,
        call_order=call_order,
        on_round=on_round,
        on_decision=on_decision,
    )
    write_artifact(experiment_id, "run_a", run_a, root=root)

    run_b = await _run_one(
        experiment_id=experiment_id,
        experiment=experiment,
        roster=roster,
        adapter=adapter,
        run_id=RunId.B,
        market=opening_market.copy(),
        forked_price=forked_price,
        call_order=call_order,
        on_round=on_round,
        on_decision=on_decision,
    )
    write_artifact(experiment_id, "run_b", run_b, root=root)

    try:
        if opening_market.snapshot() != opening:
            raise AlignmentBroken(ALIGNMENT_ERROR)
        check_alignment(run_a, run_b, experiment.applies_from_round)
        status = Status.complete
        error = None
    except AlignmentBroken as exc:
        status = Status.failed
        error = exc.error

    return TwinResult(
        id=experiment_id,
        status=status,
        error=error,
        experiment=experiment,
        roster=roster,
        opening=opening,
        run_a=run_a,
        run_b=run_b,
        call_order=call_order,
    )
