"""Research fetchers. Live Cursor path fills these; tests inject fakes. No X/TikTok/Facebook."""

from __future__ import annotations


def fetch_reddit(category: str, queries: list[str]) -> list[dict]:
    _ = category, queries
    return []


def fetch_web(queries: list[str]) -> list[dict]:
    _ = queries
    return []
