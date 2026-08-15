"""One live variable: price, rival entry, marketing, or a feature change."""

from app.contracts import CreateExperimentRequest, RunId
from app.intervention import apply_fork, parse_spend
from app.market import parse_price_delta
from app.roster.fixed_grok_bot import COMPETITOR_PRICE, FORK_PRICE, LIST_PRICE


def _req(**overrides) -> CreateExperimentRequest:
    payload = {
        "product_name": "Grok Bot",
        "product_description": "Always-on AI teammates.",
        "current_price": LIST_PRICE,
        "market_size": 30,
        "competitor_count": 1,
        "competitor_price": COMPETITOR_PRICE,
        "buyer_price_sensitivity": "medium",
        "rounds": 4,
        "random_seed": 42,
        "variable_type": "price_change",
        "variable_delta": "+20%",
        "applies_from_round": 3,
        "adapter": "fixture",
    }
    payload.update(overrides)
    return CreateExperimentRequest.model_validate(payload)


def test_price_change_only_on_b_from_round():
    exp = _req()
    early = apply_fork(exp, RunId.B, 2)
    late_a = apply_fork(exp, RunId.A, 3)
    late_b = apply_fork(exp, RunId.B, 3)
    assert early.current_price == LIST_PRICE
    assert late_a.current_price == LIST_PRICE
    assert late_b.current_price == FORK_PRICE
    assert late_b.competitor_price == COMPETITOR_PRICE
    assert late_b.marketing_spend == 0
    assert late_b.feature_change == ""


def test_competitor_entry_forks_rival_price_and_count():
    exp = _req(variable_type="competitor_entry", variable_delta="-20%")
    snap = apply_fork(exp, RunId.B, 3)
    assert snap.current_price == LIST_PRICE
    assert snap.competitor_price == parse_price_delta(COMPETITOR_PRICE, "-20%")
    assert snap.competitor_count == 2
    assert apply_fork(exp, RunId.A, 3).competitor_count == 1


def test_marketing_spend_is_dollars_on_b_only():
    exp = _req(variable_type="marketing_spend", variable_delta="+20%")
    snap = apply_fork(exp, RunId.B, 3)
    assert snap.marketing_spend == parse_spend(LIST_PRICE, 30, "+20%")
    assert snap.current_price == LIST_PRICE
    assert apply_fork(exp, RunId.A, 3).marketing_spend == 0


def test_feature_change_passes_delta_through():
    exp = _req(variable_type="feature_change", variable_delta="cut search")
    assert apply_fork(exp, RunId.B, 3).feature_change == "cut search"
    assert apply_fork(exp, RunId.A, 3).feature_change == ""
    assert apply_fork(exp, RunId.B, 2).feature_change == ""
