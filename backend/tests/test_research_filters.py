from datetime import datetime, timezone, timedelta
from app.roster.research.filters import filter_items

NOW = datetime(2026, 8, 15, tzinfo=timezone.utc)


def _item(**overrides):
    base = {
        "source": "reddit",
        "subreddit": "saas",
        "title": "We switched after a 20% price hike",
        "text": "SaaS seat price jumped; we churned to the cheaper competitor.",
        "score": 42,
        "num_comments": 12,
        "created_utc": (NOW - timedelta(days=30)).timestamp(),
        "nsfw": False,
        "removed": False,
        "stickied": False,
        "url": "https://reddit.com/r/saas/1",
        "category": "saas",
    }
    base.update(overrides)
    return base


def test_keeps_on_category_price_thread():
    kept = filter_items([_item()], now=NOW)
    assert len(kept) == 1


def test_drops_low_score_and_old_and_meme():
    items = [
        _item(score=2),
        _item(created_utc=(NOW - timedelta(days=800)).timestamp()),
        _item(title="lol", text="funny meme", score=500, num_comments=80),
        _item(subreddit="all", title="random"),
        _item(nsfw=True),
    ]
    assert filter_items(items, now=NOW) == []


def test_keeps_when_product_name_matches():
    item = _item(subreddit="productivity", title="Notion price hike", text="We might switch plans.")
    kept = filter_items([item], now=NOW, category="saas", product="Notion")
    assert len(kept) == 1
    items = [_item(url=f"https://reddit.com/r/saas/{i}", text=f"SaaS price plan {i} switch") for i in range(20)]
    kept = filter_items(items, now=NOW)
    assert len(kept) <= 8
