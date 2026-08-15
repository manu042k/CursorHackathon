from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

DECISION_WORDS = ("price", "plan", "churn", "switch", "competitor", "renew", "contract", "seat")
MEME_TITLES = {"lol", "meme", "joke", "lmao"}
MAX_AGE_DAYS = 540
MIN_SCORE = 10
MIN_COMMENTS = 3
CAP = 8


def filter_items(items: list[dict], *, now: datetime | None = None, category: str = "saas") -> list[dict]:
    clock = now or datetime.now(timezone.utc)
    kept: list[dict] = []
    seen_urls: set[str] = set()
    for item in items:
        if item.get("nsfw") or item.get("removed") or item.get("stickied"):
            continue
        if str(item.get("subreddit", "")).lower() == "all":
            continue
        if int(item.get("score") or 0) < MIN_SCORE:
            continue
        if int(item.get("num_comments") or 0) < MIN_COMMENTS:
            continue
        created = datetime.fromtimestamp(float(item["created_utc"]), tz=timezone.utc)
        if (clock - created).days > MAX_AGE_DAYS:
            continue
        title = str(item.get("title") or "").strip().lower()
        if title in MEME_TITLES:
            continue
        blob = f"{title} {item.get('text', '')}".lower()
        if category.lower() not in blob and category.lower() not in str(item.get("subreddit", "")).lower():
            continue
        if not any(word in blob for word in DECISION_WORDS):
            continue
        url = item.get("url")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        kept.append(item)
    per_source: dict[str, int] = defaultdict(int)
    capped: list[dict] = []
    for item in kept:
        source = item.get("source", "reddit")
        if per_source[source] >= CAP:
            continue
        per_source[source] += 1
        capped.append(item)
    return capped
