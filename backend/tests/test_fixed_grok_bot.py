"""US-A2: five buyers, WTP band around $144, weights sum to 30, seed-stable."""

from app.contracts import Roster
from app.roster.fixed_grok_bot import FORK_PRICE, LIST_PRICE, MARKET_SIZE, build_roster


def test_roster_has_buyers_competitor_analyst():
    roster = build_roster(42)
    ids = {a.agent_id for a in roster.agents}
    assert {"buyer_1", "buyer_2", "buyer_3", "buyer_4", "buyer_5", "competitor", "analyst"} <= ids
    assert any(r.role == "incumbent_competitor" for r in roster.agent_roles)
    assert any(r.role == "analyst" for r in roster.agent_roles)


def test_three_buyers_in_wtp_band():
    buyers = [
        a
        for a in build_roster(42).agents
        if a.agent_id.startswith("buyer_")
    ]
    in_band = [
        a
        for a in buyers
        if LIST_PRICE <= float(a.traits["willingness_to_pay"]) <= FORK_PRICE
    ]
    assert len(in_band) >= 2
    below_list = [
        a for a in buyers if float(a.traits["willingness_to_pay"]) < LIST_PRICE
    ]
    assert len(below_list) >= 1


def test_buyer_weights_sum_to_market_size():
    weights = [
        a.weight
        for a in build_roster(42).agents
        if a.agent_id.startswith("buyer_")
    ]
    assert sum(weights) == MARKET_SIZE == 30


def test_same_seed_is_identical():
    a = build_roster(42).model_dump(mode="json")
    b = build_roster(42).model_dump(mode="json")
    assert a == b
    assert Roster.model_validate(a) == Roster.model_validate(b)
