"""Reddit + web research fetch via site-restricted search. No Reddit API. No X/TikTok/Facebook."""

from __future__ import annotations

from typing import Callable
from urllib.parse import urlparse

from app import settings

SearchFn = Callable[[str], list[dict]]
REDDIT_HOSTS = {"reddit.com", "www.reddit.com", "old.reddit.com", "np.reddit.com"}


def _brave_search(query: str) -> list[dict]:
    key = settings.BRAVE_SEARCH_API_KEY
    if not key:
        return []
    import httpx

    try:
        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": 8},
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": key,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        results = response.json().get("web", {}).get("results") or []
    except Exception:
        return []
    return _normalize_hits(
        {"url": row.get("url"), "title": row.get("title"), "description": row.get("description")}
        for row in results
    )


def _tavily_search(query: str, *, include_domains: list[str] | None = None) -> list[dict]:
    key = settings.TAVILY_API_KEY
    if not key:
        return []
    import httpx

    payload: dict = {
        "api_key": key,
        "query": query,
        "max_results": 8,
        "search_depth": "basic",
        "include_answer": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    try:
        response = httpx.post("https://api.tavily.com/search", json=payload, timeout=20.0)
        response.raise_for_status()
        results = response.json().get("results") or []
    except Exception:
        return []
    return _normalize_hits(
        {
            "url": row.get("url"),
            "title": row.get("title"),
            "description": row.get("content") or row.get("snippet") or "",
        }
        for row in results
    )


def _normalize_hits(rows) -> list[dict]:
    mapped: list[dict] = []
    for row in rows:
        url = str(row.get("url") or "")
        if not url:
            continue
        mapped.append(
            {
                "url": url,
                "title": str(row.get("title") or ""),
                "description": str(row.get("description") or ""),
            }
        )
    return mapped


def web_search(query: str) -> list[dict]:
    """Tavily first (AI search API), then Brave. Empty list if neither key is set."""
    provider = settings.SEARCH_PROVIDER
    reddit_domains = ["reddit.com"] if "site:reddit.com" in query else None
    use_tavily = provider in {"auto", "tavily"} and bool(settings.TAVILY_API_KEY)
    use_brave = provider in {"auto", "brave"} and bool(settings.BRAVE_SEARCH_API_KEY)
    if use_tavily:
        return _tavily_search(query, include_domains=reddit_domains)
    if use_brave:
        return _brave_search(query)
    return []


def map_search_hit(hit: dict, *, category: str | None = None, **kwargs) -> dict | None:
    if category is None:
        category = str(kwargs.get("category") or "")
    url = str(hit.get("url") or "")
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":")[0]
    if host not in REDDIT_HOSTS:
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2 or parts[0].lower() != "r":
        return None
    subreddit = parts[1].lower()
    if subreddit == "all":
        return None
    title = str(hit.get("title") or "")
    text = str(hit.get("description") or hit.get("text") or "")
    return {
        "source": "reddit",
        "id": url,
        "subreddit": subreddit,
        "title": title,
        "text": text,
        "score": None,
        "num_comments": None,
        "created_utc": None,
        "nsfw": False,
        "removed": False,
        "stickied": False,
        "url": url,
        "category": category,
    }


def map_web_hit(hit: dict, *, category: str) -> dict | None:
    reddit = map_search_hit(hit, category=category)
    if reddit is not None:
        return reddit
    url = str(hit.get("url") or "")
    if not url:
        return None
    return {
        "source": "web",
        "id": url,
        "subreddit": "",
        "title": str(hit.get("title") or ""),
        "text": str(hit.get("description") or ""),
        "score": None,
        "num_comments": None,
        "created_utc": None,
        "nsfw": False,
        "removed": False,
        "stickied": False,
        "url": url,
        "category": category,
    }


def fetch_reddit(
    category: str,
    queries: list[str],
    *,
    search_fn: SearchFn | None = None,
) -> list[dict]:
    search = search_fn or web_search
    items: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        try:
            hits = search(query)
        except Exception:
            continue
        for hit in hits:
            item = map_search_hit(hit, category=category)
            if item is None or item["url"] in seen:
                continue
            seen.add(item["url"])
            items.append(item)
    return items


def fetch_web(
    queries: list[str],
    *,
    category: str = "saas",
    search_fn: SearchFn | None = None,
) -> list[dict]:
    search = search_fn or web_search
    items: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        try:
            hits = search(query)
        except Exception:
            continue
        for hit in hits:
            item = map_web_hit(hit, category=category)
            if item is None or item["url"] in seen:
                continue
            seen.add(item["url"])
            items.append(item)
    return items
