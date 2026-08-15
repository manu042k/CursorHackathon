"""US-A3: CursorSdkAdapter via AsyncAgent.prompt. Mocks when no live key."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

import pytest

from app.agents.cursor_adapter import (
    CursorSdkAdapter,
    DecisionRunError,
    DecisionStartupError,
    parse_agent_result,
)
from app.agents.prompts import DECISION_PROMPT_TEMPLATE, render_decision_prompt
from app.contracts import AgentDecisionRequest, RunId
from app.narrative import canonical_hash
from cursor_sdk import AgentOptions, CursorAgentError, LocalAgentOptions

GOOD_JSON = (
    '{"decision":"stay","reason":"Price $59 is $4 over my willingness to pay of $55; I stay this round.","confidence":0.7}'
)


@dataclass
class FakeResult:
    id: str = "run_1"
    agent_id: str = "agt_1"
    status: str = "completed"
    result: str = GOOD_JSON


def _run(coro):
    return asyncio.run(coro)


def test_prompt_kwargs_are_explicit_local_no_setting_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    captured = {}

    async def fake_prompt(message, options, *, client):
        captured["message"] = message
        captured["options"] = options
        captured["client"] = client
        return FakeResult()

    adapter = CursorSdkAdapter(
        client="client", prompt_fn=fake_prompt, api_key="test-key", model="composer-2.5"
    )
    request = AgentDecisionRequest(
        experiment_id="exp_t",
        run_id=RunId.B,
        agent_id="buyer_3",
        round=4,
        current_price=59,
        persona={"willingness_to_pay": 55},
    )
    decision = _run(adapter.decide(request))
    assert decision.decision == "stay"
    options = captured["options"]
    assert isinstance(options, AgentOptions)
    assert options.api_key == "test-key"
    assert options.model == "composer-2.5"
    assert list(options.tools) == []
    assert isinstance(options.local, LocalAgentOptions)
    assert options.local.cwd
    assert options.local.setting_sources is None
    local_json = options.local.to_json()
    assert not local_json.get("settingSources")
    assert captured["client"] == "client"


def test_cursor_agent_error_vs_run_status_error():
    async def boom(message, options, *, client):
        raise CursorAgentError("auth failed")

    adapter = CursorSdkAdapter(client="c", prompt_fn=boom, api_key="k")
    request = AgentDecisionRequest(run_id=RunId.A, agent_id="buyer_3", round=1, current_price=49)
    with pytest.raises(DecisionStartupError):
        _run(adapter.decide(request))

    async def failed_run(message, options, *, client):
        return FakeResult(status="error", id="run_bad")

    adapter = CursorSdkAdapter(client="c", prompt_fn=failed_run, api_key="k")
    with pytest.raises(DecisionRunError):
        _run(adapter.decide(request))


def test_parse_result_json_and_prompt_hash():
    parsed = parse_agent_result("```json\n" + GOOD_JSON + "\n```")
    assert parsed.decision == "stay"
    assert canonical_hash(DECISION_PROMPT_TEMPLATE).startswith("sha256:")
    request = AgentDecisionRequest(run_id=RunId.B, agent_id="buyer_3", round=4, current_price=59)
    text = render_decision_prompt(request)
    assert "buyer_3" in text
    assert "59" in text


@pytest.mark.skipif(not os.environ.get("CURSOR_API_KEY"), reason="no CURSOR_API_KEY")
def test_live_buyer_3_at_59_has_wtp_reason():
    """Opt-in live call. Key is read from the environment and never written to disk."""
    from cursor_sdk import AsyncAgent, AsyncClient
    from app.agents.cursor_adapter import CursorSdkAdapter as LiveAdapter

    async def go():
        async with await AsyncClient.launch_bridge() as client:
            adapter = LiveAdapter(client)
            decision = await adapter.decide(
                AgentDecisionRequest(
                    run_id=RunId.B,
                    agent_id="buyer_3",
                    round=4,
                    current_price=59,
                    persona={"willingness_to_pay": 55},
                )
            )
            assert "$" in decision.reason
            assert len(decision.reason) >= 40

    _run(go())
