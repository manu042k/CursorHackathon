"""Research fetchers. Live path hits Reddit + HN only. No X/TikTok/Facebook."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (compatible; CounterfactualReplay/0.1; +https://github.com/manu042k/CursorHackathon)"
)
TIMEOUT_S = 8


def _get_json(url: str) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def _reddit_item(child: dict) -> dict | None:
    data = child.get("data") if isinstance(child, dict) else None
    if not isinstance(data, dict):
        return None
    permalink = str(data.get("permalink") or "")
    return {
        "id": str(data.get("id") or ""),
        "source": "reddit",
        "subreddit": str(data.get("subreddit") or ""),
        "title": str(data.get("title") or ""),
        "text": str(data.get("selftext") or ""),
        "score": int(data.get("score") or 0),
        "num_comments": int(data.get("num_comments") or 0),
        "created_utc": float(data.get("created_utc") or 0),
        "nsfw": bool(data.get("over_18")),
        "removed": bool(data.get("removed_by_category")),
        "stickied": bool(data.get("stickied")),
        "url": f"https://www.reddit.com{permalink}" if permalink else str(data.get("url") or ""),
    }


def fetch_reddit(category: str, queries: list[str]) -> list[dict]:
    q = " ".join(part for part in queries[:2] if part).strip() or category
    encoded = urllib.parse.quote(q)
    payload = _get_json(
        f"https://www.reddit.com/search.json?q={encoded}&sort=comments&t=year&limit=25&raw_json=1"
    )
    children = None
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("children"), list):
            children = data["children"]
    if children is None:
        archive = _get_json(
            f"https://api.pullpush.io/reddit/search/submission/?q={encoded}&size=25"
        )
        if isinstance(archive, dict) and isinstance(archive.get("data"), list):
            children = [{"data": row} for row in archive["data"] if isinstance(row, dict)]
    if not isinstance(children, list):
        return []
    items: list[dict] = []
    for child in children:
        mapped = _reddit_item(child)
        if mapped:
            items.append(mapped)
    return items


def fetch_web(queries: list[str]) -> list[dict]:
    q = next((part.strip() for part in queries if part.strip()), "saas pricing")
    encoded = urllib.parse.quote(q)
    payload = _get_json(
        f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=story&hitsPerPage=20"
    )
    if not isinstance(payload, dict):
        return []
    hits = payload.get("hits")
    if not isinstance(hits, list):
        return []
    items: list[dict] = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        object_id = str(hit.get("objectID") or "")
        items.append(
            {
                "id": object_id,
                "source": "web",
                "subreddit": "",
                "title": str(hit.get("title") or ""),
                "text": str(hit.get("story_text") or hit.get("title") or ""),
                "score": int(hit.get("points") or 0),
                "num_comments": int(hit.get("num_comments") or 0),
                "created_utc": float(hit.get("created_at_i") or 0),
                "nsfw": False,
                "removed": False,
                "stickied": False,
                "url": str(hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"),
            }
        )
    return items
