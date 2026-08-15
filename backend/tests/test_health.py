"""US-X4: health + baseline variance disclosure."""

from fastapi.testclient import TestClient

from app.main import app
from app.variance import variance_disclosure


def test_health_reports_cursor_and_model(monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY", "sk-test")
    monkeypatch.setenv("CURSOR_MODEL", "composer-2.5")
    client = TestClient(app)
    body = client.get("/health").json()
    assert body["ok"] is True
    assert body["cursor_configured"] is True
    assert body["model"] == "composer-2.5"


def test_health_without_key_is_fixture(monkeypatch):
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    client = TestClient(app)
    body = client.get("/health").json()
    assert body["cursor_configured"] is False
    assert body["adapter"] == "fixture"
    assert body["model"] is None


def test_variance_disclosure_when_two_run_a_differ():
    a1 = {"agent_logs": [{"round": 1, "agent_id": "buyer_3", "decision": "stay"}]}
    a2 = {"agent_logs": [{"round": 1, "agent_id": "buyer_3", "decision": "churn"}]}
    note = variance_disclosure(a1, a2)
    assert note is not None
    assert "differed" in note
    assert variance_disclosure(a1, a1) is None
