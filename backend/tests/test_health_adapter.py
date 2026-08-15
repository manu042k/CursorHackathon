"""US-B7: /health and adapter on the paper so fixture is never labeled Cursor."""

from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.main import app
from app.registry import ExperimentRegistry
from tests.test_http_experiments import PAYLOAD, _wait_paper


def test_health_and_paper_disclose_adapter(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    health = client.get("/health").json()
    assert health["ok"] is True
    assert health["adapter"] == "fixture"
    created = client.post("/experiments", json=PAYLOAD)
    paper = _wait_paper(client, created.json()["id"]).json()
    assert paper["receipt"]["adapter"] == "fixture"
    assert paper["experiment"]["adapter"] == "fixture"
