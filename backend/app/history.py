"""Deterministic history_summary. No LLM. Architecture US-A6."""

from __future__ import annotations

from typing import Any


def history_summary(
    logs: list[dict[str, Any]], before_round: int, max_chars: int | None = None
) -> str:
    parts = [
        f"R{log['round']} {log['agent_id']}={log['decision']}"
        for log in logs
        if int(log["round"]) < before_round
    ]
    text = "; ".join(parts)
    if max_chars is None or len(text) <= max_chars:
        return text
    while parts and len("; ".join(parts)) > max_chars:
        parts.pop(0)
    return "; ".join(parts)
