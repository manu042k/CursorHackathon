"""US-B2: twin runner applies one variable, frozen order, alignment check."""

from __future__ import annotations

import asyncio

from app.agents.fixture import FixtureAdapter
from app.contracts import AgentDecision, AgentDecisionRequest, CreateExperimentRequest, RunId, Status
from app.market import parse_price_delta
from app.roster.fixed_grok_bot import COMPETITOR_PRICE, FORK_PRICE, LIST_PRICE
from app.store import read_artifact
from app.twin_runner import observation_order, run_twin


def _grok(**overrides) -> CreateExperimentRequest:
    payload = {
        "product_name": "Grok Bot",
        "product_description": (
            "Always-on AI teammates with their own cloud computer. They sign into "
            "your tools, finish jobs end to end, and only come back for approval."
        ),
        "current_price": LIST_PRICE,
        "market_size": 30,
        "competitor_count": 1,
        "competitor_price": COMPETITOR_PRICE,
        "buyer_price_sensitivity": "medium",
        "rounds": 4,
        "random_seed": 42,
        "variable_type": "price_change",
        "variable_delta": "+20%",
        "applies_from_round": 1,
        "adapter": "fixture",
    }
    payload.update(overrides)
    return CreateExperimentRequest.model_validate(payload)


def _run(coro):
    return asyncio.run(coro)


class RecordingAdapter:
    def __init__(self, inner: FixtureAdapter | None = None) -> None:
        self.inner = inner or FixtureAdapter()
        self.requests: list[AgentDecisionRequest] = []

    async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
        self.requests.append(request)
        return await self.inner.decide(request)


class MisalignedAdapter:
    """Diverges on B before the intervention round — must fail alignment."""

    def __init__(self) -> None:
        self.inner = FixtureAdapter()

    async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
        if request.run_id == RunId.B and request.agent_id == "buyer_5" and request.round == 1:
            return AgentDecision(
                decision="churn",
                reason="Forced misalignment for the alignment check unit test at round 1.",
                confidence=0.99,
            )
        return await self.inner.decide(request)


def test_parse_plus_twenty_percent_is_fork_price():
    assert parse_price_delta(LIST_PRICE, "+20%") == FORK_PRICE
    assert parse_price_delta(49, "+20%") == 59


def test_four_rounds_both_runs(tmp_path):
    adapter = FixtureAdapter()
    result = _run(run_twin(_grok(), "exp-four", adapter, root=tmp_path))
    assert result.status == Status.complete
    assert len(result.run_a["trajectory"]) == 4
    assert len(result.run_b["trajectory"]) == 4
    assert [row["round"] for row in result.run_a["trajectory"]] == list(range(1, 5))
    assert [row["round"] for row in result.run_b["trajectory"]] == list(range(1, 5))
    stored_a = read_artifact("exp-four", "run_a", root=tmp_path)
    stored_b = read_artifact("exp-four", "run_b", root=tmp_path)
    assert len(stored_a["trajectory"]) == 4
    assert len(stored_b["agent_logs"]) == 4 * len(observation_order(result.roster))


def test_intervention_only_on_b_from_applies_from_round(tmp_path):
    adapter = RecordingAdapter()
    result = _run(
        run_twin(_grok(applies_from_round=3), "exp-from-3", adapter, root=tmp_path)
    )
    assert result.status == Status.complete
    for req in adapter.requests:
        if req.round < 3:
            assert req.current_price == LIST_PRICE
        elif req.run_id == RunId.A:
            assert req.current_price == LIST_PRICE
        else:
            assert req.current_price == FORK_PRICE
    for row in result.run_a["trajectory"]:
        assert row["current_price"] == LIST_PRICE
    assert result.run_b["trajectory"][0]["current_price"] == LIST_PRICE
    assert result.run_b["trajectory"][1]["current_price"] == LIST_PRICE
    assert result.run_b["trajectory"][2]["current_price"] == FORK_PRICE


def test_observation_order_buyers_then_competitor(tmp_path):
    adapter = FixtureAdapter()
    result = _run(run_twin(_grok(), "exp-order", adapter, root=tmp_path))
    expected = observation_order(result.roster)
    assert expected[:5] == ["buyer_1", "buyer_2", "buyer_3", "buyer_4", "buyer_5"]
    assert expected[5] == "competitor"
    for run in ("A", "B"):
        for round_n in range(1, 5):
            chunk = [
                agent_id
                for rid, agent_id, rnd in result.call_order
                if rid == run and rnd == round_n
            ]
            assert chunk == expected
    round_one_a = [log for log in result.run_a["agent_logs"] if log["round"] == 1]
    assert [log["agent_id"] for log in round_one_a] == expected


def test_buyers_see_s0_competitor_sees_s1_after_churn(tmp_path):
    adapter = RecordingAdapter()
    _run(run_twin(_grok(), "exp-s1", adapter, root=tmp_path))
    round1 = [r for r in adapter.requests if r.round == 1 and r.run_id == RunId.A]
    buyers = [r for r in round1 if r.agent_id.startswith("buyer_")]
    competitor = next(r for r in round1 if r.agent_id == "competitor")
    assert len({id(r) for r in buyers}) == 5
    buyer_shares = {r.share for r in buyers}
    assert len(buyer_shares) == 1
    assert competitor.share <= next(iter(buyer_shares))
    buyer_idx = [
        i
        for i, r in enumerate(adapter.requests)
        if r.round == 1 and r.run_id == RunId.A and r.agent_id.startswith("buyer_")
    ]
    comp_idx = next(
        i
        for i, r in enumerate(adapter.requests)
        if r.round == 1 and r.run_id == RunId.A and r.agent_id == "competitor"
    )
    assert max(buyer_idx) < comp_idx


def test_alignment_broken_sets_failed(tmp_path):
    result = _run(
        run_twin(
            _grok(applies_from_round=3),
            "exp-broken",
            MisalignedAdapter(),
            root=tmp_path,
        )
    )
    assert result.status == Status.failed
    assert result.error == "alignment_broken"
