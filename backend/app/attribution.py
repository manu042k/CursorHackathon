"""Decision-diff attribution. Architecture §8.2 — method decision_diff_v1."""

from __future__ import annotations

from app.contracts import Contributor, DivergenceRound, Roster, Status
from app.twin_runner import TwinResult

METHOD = "decision_diff_v1"
SHARE_THRESHOLD_PP = 0.5
COMPETITOR_WEIGHT = 1.0
ANALYST_WEIGHT = 0.0


def _weight(agent_id: str, roster: Roster) -> float:
    if agent_id == "analyst" or agent_id.startswith("analyst"):
        return ANALYST_WEIGHT
    if agent_id == "competitor":
        return COMPETITOR_WEIGHT
    agent = next((a for a in roster.agents if a.agent_id == agent_id), None)
    return float(agent.weight) if agent is not None else 0.0


def _logs_by_round(run: dict, round_n: int) -> dict[str, dict]:
    return {
        log["agent_id"]: log
        for log in run.get("agent_logs", [])
        if int(log["round"]) == round_n
    }


def attribute_runs(run_a: dict, run_b: dict, roster: Roster) -> dict:
    traj_a = run_a["trajectory"]
    traj_b = run_b["trajectory"]
    rounds = min(len(traj_a), len(traj_b))
    prev_div = 0.0
    any_unattributed = False
    divergence_by_round: list[dict] = []

    for idx in range(rounds):
        round_n = int(traj_a[idx]["round"])
        share_a = float(traj_a[idx]["share"])
        share_b = float(traj_b[idx]["share"])
        divergence = share_a - share_b
        delta = divergence - prev_div
        prev_div = divergence

        logs_a = _logs_by_round(run_a, round_n)
        logs_b = _logs_by_round(run_b, round_n)
        agent_ids = list(dict.fromkeys([*logs_a.keys(), *logs_b.keys()]))

        differing: list[tuple[str, float, str]] = []
        for agent_id in agent_ids:
            dec_a = logs_a.get(agent_id, {}).get("decision")
            dec_b = logs_b.get(agent_id, {}).get("decision")
            if dec_a == dec_b:
                continue
            weight = _weight(agent_id, roster)
            if weight <= 0:
                continue
            reason = str((logs_b.get(agent_id) or logs_a.get(agent_id) or {}).get("reason", ""))
            differing.append((agent_id, weight, reason))

        contributors: list[Contributor] = []
        unattributed = False
        if abs(delta) > SHARE_THRESHOLD_PP:
            total = sum(weight for _, weight, _ in differing)
            if total <= 0:
                unattributed = True
                any_unattributed = True
            else:
                contributors = [
                    Contributor(
                        agent_id=agent_id,
                        contribution_pct=100.0 * weight / total,
                        reason=reason,
                    )
                    for agent_id, weight, reason in differing
                ]

        divergence_by_round.append(
            DivergenceRound(
                round=round_n,
                delta=delta,
                top_contributors=contributors,
            ).model_dump(mode="json")
        )
        if unattributed:
            divergence_by_round[-1]["unattributed"] = True

    return {
        "method": METHOD,
        "competitor_weight": COMPETITOR_WEIGHT,
        "analyst_weight": ANALYST_WEIGHT,
        "share_threshold_pp": SHARE_THRESHOLD_PP,
        "unattributed": any_unattributed,
        "divergence_by_round": divergence_by_round,
    }


def attribute_result(result: TwinResult) -> dict | None:
    if result.status != Status.complete:
        return None
    return attribute_runs(result.run_a, result.run_b, result.roster)
