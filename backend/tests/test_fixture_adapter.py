"""US-A4: fixture covers every agent-round-run with specific dollar reasons."""

import asyncio

from app.agents.fixture import FixtureAdapter
from app.contracts import AgentDecisionRequest, RunId
from app.roster.fixed_grok_bot import COMPETITOR_PRICE, FORK_PRICE, LIST_PRICE


def _run(coro):
    return asyncio.run(coro)


def test_covers_eight_rounds_two_runs_all_agents():
    adapter = FixtureAdapter()
    ids = adapter.agent_ids()
    assert "buyer_3" in ids and "competitor" in ids and "analyst" in ids
    for run in (RunId.A, RunId.B):
        price = LIST_PRICE if run == RunId.A else FORK_PRICE
        for round_n in range(1, 9):
            for agent_id in ids:
                persona = {}
                if agent_id.startswith("buyer_"):
                    agent = next(a for a in adapter.roster.agents if a.agent_id == agent_id)
                    persona = agent.traits
                decision = _run(
                    adapter.decide(
                        AgentDecisionRequest(
                            run_id=run,
                            agent_id=agent_id,
                            round=round_n,
                            current_price=price,
                            competitor_price=COMPETITOR_PRICE,
                            persona=persona,
                        )
                    )
                )
                assert len(decision.reason) >= 40
                assert "$" in decision.reason or "WTP" in decision.reason


def test_round_4_b_opens_divergence():
    adapter = FixtureAdapter()
    b3 = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.B,
                agent_id="buyer_3",
                round=4,
                current_price=FORK_PRICE,
                competitor_price=COMPETITOR_PRICE,
                persona={"willingness_to_pay": 140},
            )
        )
    )
    a3 = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.A,
                agent_id="buyer_3",
                round=4,
                current_price=LIST_PRICE,
                competitor_price=COMPETITOR_PRICE,
                persona={"willingness_to_pay": 140},
            )
        )
    )
    assert a3.decision == "stay"
    assert b3.decision in {"churn", "switch"}
    competitor_b = _run(
        adapter.decide(
            AgentDecisionRequest(
                run_id=RunId.B,
                agent_id="competitor",
                round=4,
                current_price=FORK_PRICE,
                competitor_price=COMPETITOR_PRICE,
            )
        )
    )
    assert competitor_b.decision == "match"
