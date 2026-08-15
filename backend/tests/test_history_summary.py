"""US-A6: history_summary is deterministic and model-free."""

from app.history import history_summary

LOGS = [
    {"round": 1, "agent_id": "buyer_3", "decision": "stay"},
    {"round": 1, "agent_id": "competitor", "decision": "hold"},
    {"round": 2, "agent_id": "buyer_3", "decision": "churn"},
]


def test_same_log_identical_summary():
    first = history_summary(LOGS, 3)
    second = history_summary(list(LOGS), 3)
    assert first == second
    assert first == "R1 buyer_3=stay; R1 competitor=hold; R2 buyer_3=churn"
    assert history_summary(LOGS, 1) == ""
"""US-A6: history_summary is deterministic and model-free."""

from pathlib import Path

from app.history import history_summary

LOGS = [
    {"round": 1, "agent_id": "buyer_3", "decision": "stay"},
    {"round": 1, "agent_id": "competitor", "decision": "hold"},
    {"round": 2, "agent_id": "buyer_3", "decision": "churn"},
]


def test_same_log_identical_summary():
    first = history_summary(LOGS, 3)
    second = history_summary(list(LOGS), 3)
    assert first == second
    assert first == "R1 buyer_3=stay; R1 competitor=hold; R2 buyer_3=churn"
    assert history_summary(LOGS, 1) == ""
    source = Path(__file__).resolve().parents[1].joinpath("app/history.py").read_text(encoding="utf-8")
    assert "Agent.prompt" not in source
    assert "AsyncAgent" not in source
