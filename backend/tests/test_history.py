from app.history import history_summary


def test_history_summary_truncates_oldest_first():
    logs = [
        {"round": 1, "agent_id": "buyer_1", "decision": "stay"},
        {"round": 2, "agent_id": "buyer_1", "decision": "stay"},
        {"round": 3, "agent_id": "buyer_1", "decision": "churn"},
    ]
    text = history_summary(logs, 4, max_chars=40)
    assert "R3" in text
    assert len(text) <= 40
