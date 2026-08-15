"""US-X3: fixture adapter end-to-end — submit, paper, receipt, trace logs."""

from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.main import app
from app.registry import ExperimentRegistry
from tests.test_http_experiments import PAYLOAD, _start_after_roster, _wait_paper


def test_fixture_end_to_end_paper_and_trace(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    experiment_id = _start_after_roster(client)
    paper = _wait_paper(client, experiment_id).json()
    assert paper["experiment"]["adapter"] == "fixture"
    assert paper["receipt"]["adapter"] == "fixture"
    assert len(paper["metrics"]["share_a"]) == 4
    assert len(paper["metrics"]["share_b"]) == 4
    logs = paper["logs"]["run_b"]
    r4 = [row for row in logs if row["round"] == 4]
    assert any(row["agent_id"] == "buyer_3" for row in r4)
    assert any(row["agent_id"] == "competitor" for row in r4)
    assert any(row["decision"] != "stay" for row in r4 if row["agent_id"].startswith("buyer_"))
