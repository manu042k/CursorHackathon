"""Decision prompt template. Identical for A and B; only the request JSON differs."""

from __future__ import annotations

import json

from app.contracts import AgentDecisionRequest

DECISION_PROMPT_TEMPLATE = (
    "You are {agent_id} in a controlled market experiment. "
    "Observe the request JSON and return only JSON "
    '{{"decision": string, "reason": string, "confidence": number}}. '
    "reason must be at least 40 characters and mention prices in dollars. "
    "No markdown."
)

REPAIR_SUFFIX = (
    " Your previous reply was invalid. Reply with a single JSON object only, "
    "keys decision, reason, confidence."
)


def render_decision_prompt(request: AgentDecisionRequest) -> str:
    header = DECISION_PROMPT_TEMPLATE.format(agent_id=request.agent_id)
    payload = json.dumps(request.model_dump(mode="json"), sort_keys=True)
    return f"{header}\n{payload}"
