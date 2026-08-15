"""US-A1: DecisionPort async I/O, invalid JSON fails closed, FixtureAdapter stay/churn/switch."""

from __future__ import annotations

import asyncio
import inspect

import pytest

from app.agents.fixture import FixtureAdapter
from app.agents.port import DecisionError, DecisionPort, parse_decision_json, validate_decision
from app.contracts import AgentDecision, AgentDecisionRequest, RunId
from app.roster.fixed_grok_bot import FORK_PRICE, LIST_PRICE


def _run(coro):
    return asyncio.run(coro)


def test_decision_port_decide_is_async():
    assert inspect.iscoroutinefunction(DecisionPort.decide)


def test_invalid_json_raises_and_is_not_stay():
    with pytest.raises(DecisionError, match="invalid json"):
        parse_decision_json("{not json")
    with pytest.raises(DecisionError, match="invalid json"):
        validate_decision("not-json")
    with pytest.raises(DecisionError):
        validate_decision('{"decision": "stay"}')


def test_generic_denylist_and_short_reason_rejected():
    with pytest.raises(DecisionError, match="too short"):
        validate_decision(
            AgentDecision(decision="stay", reason="Price is high enough", confidence=0.9)
        )
    with pytest.raises(DecisionError, match="denylist"):
        validate_decision(
            AgentDecision(
                decision="churn",
                reason="I decided to churn",
                confidence=0.9,
            )
        )
    with pytest.raises(DecisionError, match="denylist"):
        validate_decision(
            AgentDecision(
                decision="churn",
                reason="Because of the price",
                confidence=0.9,
            )
        )
    padded = validate_decision(
        {
            "decision": "stay",
            "reason": "Price $49 is $7 over my willingness to pay of $42; I stay this round.",
            "confidence": 0.7,
        }
    )
    assert padded.decision == "stay"
    assert len(padded.reason) >= 40


def test_fixture_adapter_stay_churn_switch():
    adapter = FixtureAdapter()
    stay = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.A,
                agent_id="buyer_3",
                round=1,
                current_price=LIST_PRICE,
                persona={"willingness_to_pay": 140},
            )
        )
    )
    churn = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.B,
                agent_id="buyer_1",
                round=2,
                current_price=FORK_PRICE,
                persona={"willingness_to_pay": 105},
            )
        )
    )
    switch = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.B,
                agent_id="buyer_3",
                round=4,
                current_price=FORK_PRICE,
                persona={"willingness_to_pay": 140},
            )
        )
    )
    assert stay.decision == "stay"
    assert churn.decision == "churn"
    assert switch.decision == "switch"
    for decision in (stay, churn, switch):
        validated = validate_decision(decision)
        assert validated.decision == decision.decision
        assert len(validated.reason) >= 40
