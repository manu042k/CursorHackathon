"""Deterministic history_summary. No LLM. Architecture US-A6."""

from __future__ import annotations

from typing import Any


def history_summary(logs: list[dict[str, Any]], before_round: int) -> str:
    parts = [
        f"R{log['round']} {log['agent_id']}={log['decision']}"
        for log in logs
        if int(log["round"]) < before_round
    ]
    return "; ".join(parts)
