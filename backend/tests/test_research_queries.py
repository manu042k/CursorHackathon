from app.contracts import Adapter, CreateExperimentRequest
from app.roster.research.queries import (
    allowlisted_subreddits,
    build_reddit_queries,
    infer_category,
)


def _body(**overrides) -> CreateExperimentRequest:
    payload = dict(
        product_name="Grok Bot",
        product_description="Always-on AI teammates with their own cloud computer.",
        current_price=120,
        market_size=30,
        competitor_count=1,
        competitor_price=100,
        buyer_price_sensitivity="medium",
        rounds=4,
        random_seed=42,
        variable_type="price_change",
        variable_delta="+20%",
        applies_from_round=1,
        adapter=Adapter.cursor,
    )
    payload.update(overrides)
    return CreateExperimentRequest(**payload)


def test_saas_product_infers_saas_and_allowlisted_subs():
    body = _body()
    assert infer_category(body) == "saas"
    assert "saas" in allowlisted_subreddits("saas")
    assert "all" not in allowlisted_subreddits("saas")


def test_subscription_box_infers_snacks_category():
    body = _body(product_description="A consumer subscription box of snacks")
    assert infer_category(body) == "snacks"


def test_queries_include_product_name_category_and_decision_words():
    queries = build_reddit_queries(_body())
    assert queries
    blob = " ".join(queries).lower()
    assert "grok bot" in blob
    assert "saas" in blob
    assert any(word in blob for word in ("price", "plan", "churn", "switch", "competitor"))
    assert all("site:reddit.com/r/" in q for q in queries)
    assert not any("/r/all" in q.lower() for q in queries)


def test_queries_include_description_tokens_and_comment_threads():
    queries = build_reddit_queries(_body())
    blob = " ".join(queries).lower()
    assert "teammates" in blob or "cloud" in blob
    assert any("inurl:comments" in q for q in queries)


def test_brand_only_query_is_never_emitted():
    for query in build_reddit_queries(_body()):
        assert "site:reddit.com \"" not in query
        assert "/r/" in query
