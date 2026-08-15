"""DecisionPort: async structured I/O. Invalid JSON and generic reasons fail closed."""

from __future__ import annotations

import json
from typing import Any, Protocol

from app.contracts import AgentDecision, AgentDecisionRequest

REASON_MIN_LEN = 40
REASON_MAX_LEN = 400
GENERIC_DENYLIST = frozenset(
    {
        "i decided to churn",
        "because of the price",
        "ok",
        "looks good",
        "no comment",
        "n/a",
        "none",
        "idk",
        "stay",
        "churn",
        "switch",
    }
)


class DecisionError(ValueError):
    pass


class DecisionPort(Protocol):
    async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
        """Isolated one-shot. Reject empty/generic reasons."""


def parse_decision_json(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DecisionError("invalid json") from exc
    if not isinstance(payload, dict):
        raise DecisionError("invalid json")
    return payload


def validate_decision(payload: AgentDecision | dict[str, Any] | str) -> AgentDecision:
    if isinstance(payload, str):
        payload = parse_decision_json(payload)
    if isinstance(payload, AgentDecision):
        decision = payload
    else:
        try:
            decision = AgentDecision.model_validate(payload)
        except Exception as exc:
            raise DecisionError("invalid decision payload") from exc
    reason = decision.reason.strip()
    if reason.lower() in GENERIC_DENYLIST:
        raise DecisionError("generic denylist reason")
    if len(reason) < REASON_MIN_LEN:
        raise DecisionError("reason too short")
    if len(reason) > REASON_MAX_LEN:
        raise DecisionError("reason too long")
    return decision


async def decide_validated(port: DecisionPort, request: AgentDecisionRequest) -> AgentDecision:
    raw = await port.decide(request)
    return validate_decision(raw)
