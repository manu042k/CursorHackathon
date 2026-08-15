"""Grounded narrative + receipt hashes. Architecture §8.3 and US-B6."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from app.contracts import (
    Adapter,
    CreateExperimentRequest,
    MetricSeries,
    NarrativeCitation,
    Receipt,
    Roster,
    RunId,
    Runtime,
    SummaryNarrative,
)

DECISION_PROMPT_TEMPLATE = (
    "You are {agent_id} in a controlled market experiment. "
    "Observe the request JSON and return only JSON "
    '{"decision": string, "reason": string, "confidence": number}. '
    "reason must be at least 40 characters and mention prices in dollars."
)

AGENT_MENTION = re.compile(r"\b(buyer_\d+|competitor|analyst)\b")


class NarrativeGroundingError(ValueError):
    pass


def canonical_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_receipt(experiment: CreateExperimentRequest, roster: Roster) -> Receipt:
    model = "fixture" if experiment.adapter == Adapter.fixture else "composer-2.5"
    return Receipt(
        random_seed=experiment.random_seed,
        prompt_hash=canonical_hash(DECISION_PROMPT_TEMPLATE),
        roster_hash=canonical_hash(roster.model_dump(mode="json")),
        other_variables_changed=0,
        adapter=experiment.adapter,
        runtime=Runtime.local,
        model=model,
        tools=[],
    )


def _log_keys(run_a: dict, run_b: dict) -> set[tuple[str, int, str]]:
    keys: set[tuple[str, int, str]] = set()
    for run in (run_a, run_b):
        for log in run.get("agent_logs", []):
            keys.add((str(log["agent_id"]), int(log["round"]), str(log["run_id"])))
    return keys


def validate_narrative(text: str, citations: list[NarrativeCitation], run_a: dict, run_b: dict) -> None:
    if not citations:
        raise NarrativeGroundingError("citations array required")
    logged = _log_keys(run_a, run_b)
    for citation in citations:
        key = (citation.agent_id, citation.round, citation.run_id.value)
        if key not in logged:
            raise NarrativeGroundingError(
                f"citation {citation.agent_id} r{citation.round} {citation.run_id.value} not in logs"
            )
    cited_ids = {c.agent_id for c in citations}
    for agent_id in AGENT_MENTION.findall(text):
        in_logs = any(agent_id == key[0] for key in logged)
        if not in_logs:
            raise NarrativeGroundingError(f"narrative mentions {agent_id} who is not in logs")
        if agent_id not in cited_ids:
            raise NarrativeGroundingError(f"narrative mentions {agent_id} without a citation")


def _top_driver(divergence_by_round: list[dict], run_b: dict) -> tuple[str, int, str]:
    best: dict | None = None
    best_abs = -1.0
    for row in divergence_by_round:
        contributors = row.get("top_contributors") or []
        if not contributors:
            continue
        magnitude = abs(float(row.get("delta", 0)))
        if magnitude >= best_abs:
            best_abs = magnitude
            best = {"round": int(row["round"]), **contributors[0]}
    if best is not None:
        return str(best["agent_id"]), int(best["round"]), str(best.get("reason", ""))
    logs = run_b.get("agent_logs") or []
    if not logs:
        raise NarrativeGroundingError("no logs to cite")
    first = logs[0]
    return str(first["agent_id"]), int(first["round"]), str(first.get("reason", ""))


def grounded_narrative(
    experiment: CreateExperimentRequest,
    metrics: MetricSeries,
    divergence_by_round: list[dict],
    run_a: dict,
    run_b: dict,
) -> SummaryNarrative:
    agent_id, round_n, reason = _top_driver(divergence_by_round, run_b)
    share = metrics.final_share_delta_pp
    mrr = metrics.final_mrr_delta
    share_text = f"{share:+.1f}pp"
    mrr_text = f"${mrr:+.0f}"
    snippet = reason if len(reason) <= 180 else reason[:177] + "..."
    text = (
        f"Raising price {experiment.variable_delta} changed share by {share_text} "
        f"and MRR by {mrr_text}, driven by {agent_id} at round {round_n}: “{snippet}”."
    )
    citations = [
        NarrativeCitation(agent_id=agent_id, round=round_n, run_id=RunId.B),
    ]
    validate_narrative(text, citations, run_a, run_b)
    return SummaryNarrative(text=text, citations=citations)
