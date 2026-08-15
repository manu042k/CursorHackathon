"""Compare two Run A logs. If they differ, the causal identity claim is weakened."""

from __future__ import annotations


def decision_fingerprint(run: dict) -> list[tuple]:
    return [
        (int(log["round"]), str(log["agent_id"]), str(log["decision"]))
        for log in run.get("agent_logs", [])
    ]


def variance_disclosure(first_a: dict, second_a: dict) -> str | None:
    if decision_fingerprint(first_a) != decision_fingerprint(second_a):
        return (
            "Two baseline runs with the same prompt template differed; "
            "treat reasons as directional, not identical replays."
        )
    return None
