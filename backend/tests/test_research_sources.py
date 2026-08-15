from app.roster.research.sources import fetch_reddit, fetch_web, map_search_hit, web_search


def test_fetch_reddit_without_key_returns_empty(monkeypatch):
    monkeypatch.setattr("app.roster.research.sources.settings.BRAVE_SEARCH_API_KEY", "")
    monkeypatch.setattr("app.roster.research.sources.settings.TAVILY_API_KEY", "")
    assert fetch_reddit("saas", ['site:reddit.com/r/saas "Grok Bot" saas (price)']) == []


def test_fetch_web_without_key_returns_empty(monkeypatch):
    monkeypatch.setattr("app.roster.research.sources.settings.BRAVE_SEARCH_API_KEY", "")
    monkeypatch.setattr("app.roster.research.sources.settings.TAVILY_API_KEY", "")
    assert fetch_web(["saas pricing"]) == []


def test_map_search_hit_keeps_allowlisted_reddit_thread():
    item = map_search_hit(
        {
            "url": "https://www.reddit.com/r/saas/comments/abc/price_hike/",
            "title": "We switched after a SaaS price hike",
            "description": "Seat price jumped; comments about churn.",
        },
        category="saas",
    )
    assert item is not None
    assert item["source"] == "reddit"
    assert item["subreddit"] == "saas"
    assert item["score"] is None
    assert "comments/abc" in item["url"]


def test_map_search_hit_drops_r_all_and_non_reddit():
    assert (
        map_search_hit(
            {"url": "https://www.reddit.com/r/all/comments/x", "title": "noise", "description": "price"},
            category="saas",
        )
        is None
    )
    assert (
        map_search_hit(
            {"url": "https://example.com/blog/pricing", "title": "SaaS price", "description": "plan"},
            category="saas",
        )
        is None
    )


def test_fetch_reddit_uses_injected_search_and_skips_network():
    hits = [
        {
            "url": "https://www.reddit.com/r/saas/comments/1/we_switched",
            "title": "SaaS price hike",
            "description": "We churned after a plan change.",
        }
    ]

    def fake_search(query: str) -> list[dict]:
        assert "site:reddit.com/r/" in query
        return hits

    items = fetch_reddit("saas", ['site:reddit.com/r/saas "Grok Bot" saas (price)'], search_fn=fake_search)
    assert len(items) == 1
    assert items[0]["subreddit"] == "saas"


def test_web_search_prefers_tavily_over_brave(monkeypatch):
    monkeypatch.setattr("app.roster.research.sources.settings.TAVILY_API_KEY", "tvly-test")
    monkeypatch.setattr("app.roster.research.sources.settings.BRAVE_SEARCH_API_KEY", "brv-test")

    def fake_tavily(query: str, *, include_domains=None):
        assert "saas" in query
        assert include_domains == ["reddit.com"]
        return [{"url": "https://www.reddit.com/r/saas/comments/z/x", "title": "tavily", "description": "hit"}]

    def boom(query: str):
        raise AssertionError("brave should not run when tavily is configured")

    monkeypatch.setattr("app.roster.research.sources._tavily_search", fake_tavily)
    monkeypatch.setattr("app.roster.research.sources._brave_search", boom)
    hits = web_search('site:reddit.com/r/saas "Grok Bot" saas (price)')
    assert hits[0]["title"] == "tavily"


def test_web_search_uses_brave_when_tavily_missing(monkeypatch):
    monkeypatch.setattr("app.roster.research.sources.settings.TAVILY_API_KEY", "")
    monkeypatch.setattr("app.roster.research.sources.settings.BRAVE_SEARCH_API_KEY", "brv-test")

    def fake_brave(query: str):
        return [{"url": "https://www.reddit.com/r/saas/comments/b/x", "title": "brave", "description": "hit"}]

    monkeypatch.setattr("app.roster.research.sources._brave_search", fake_brave)
    hits = web_search("saas pricing")
    assert hits[0]["title"] == "brave"
