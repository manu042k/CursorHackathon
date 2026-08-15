from app.roster.research.sources import fetch_reddit, fetch_web


class _FakeResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        import json

        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_reddit_maps_listing(monkeypatch):
    payload = {
        "data": {
            "children": [
                {
                    "data": {
                        "id": "abc",
                        "subreddit": "saas",
                        "title": "Price hike",
                        "selftext": "We might churn",
                        "score": 40,
                        "num_comments": 9,
                        "created_utc": 1700000000,
                        "over_18": False,
                        "permalink": "/r/saas/abc/",
                    }
                }
            ]
        }
    }
    monkeypatch.setattr(
        "app.roster.research.sources.urllib.request.urlopen",
        lambda *args, **kwargs: _FakeResp(payload),
    )
    items = fetch_reddit("saas", ["Notion"])
    assert items[0]["id"] == "abc"
    assert items[0]["source"] == "reddit"
    assert items[0]["score"] == 40


def test_web_maps_hn(monkeypatch):
    payload = {
        "hits": [
            {
                "objectID": "1",
                "title": "Notion pricing",
                "points": 120,
                "num_comments": 40,
                "created_at_i": 1700000000,
                "url": "https://example.com/notion",
            }
        ]
    }
    monkeypatch.setattr(
        "app.roster.research.sources.urllib.request.urlopen",
        lambda *args, **kwargs: _FakeResp(payload),
    )
    items = fetch_web(["Notion"])
    assert items[0]["source"] == "web"
    assert items[0]["score"] == 120
