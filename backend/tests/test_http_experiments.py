"""US-B3: POST /experiments 202, GET paper 200/202, validation, OpenAPI, CORS."""

from __future__ import annotations

import threading
import time

from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.contracts import AgentDecision, AgentDecisionRequest, Status
from app.main import app
from app.registry import ExperimentRegistry

PAYLOAD = {
    "product_name": "Acme Analytics",
    "product_description": "B2B analytics dashboard for e-commerce teams",
    "current_price": 49,
    "market_size": 30,
    "competitor_count": 1,
    "competitor_price": 45,
    "buyer_price_sensitivity": "medium",
    "rounds": 4,
    "random_seed": 42,
    "variable_type": "price_change",
    "variable_delta": "+20%",
    "applies_from_round": 1,
    "adapter": "fixture",
}


def _wait_paper(client: TestClient, experiment_id: str, timeout: float = 15.0):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = client.get(f"/experiments/{experiment_id}")
        if last.status_code == 200:
            return last
        time.sleep(0.05)
    raise AssertionError(last.status_code if last else None, last.text if last else None)


def test_post_returns_202_and_get_paper_when_complete(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    assert created.status_code == 202
    body = created.json()
    assert "id" in body
    assert body["status"] == Status.created.value
    paper = _wait_paper(client, body["id"])
    payload = paper.json()
    assert payload["status"] == "complete"
    assert payload["id"] == body["id"]
    assert payload["experiment"]["rounds"] == 4
    assert len(payload["metrics"]["share_a"]) == 4
    assert len(payload["logs"]["run_a"]) > 0


def test_get_202_while_running(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    gate = threading.Event()
    inner = FixtureAdapter()

    class GatedAdapter:
        async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
            if (
                request.round == 1
                and request.run_id.value == "A"
                and request.agent_id == "buyer_1"
            ):
                gate.wait(timeout=8)
            return await inner.decide(request)

    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: GatedAdapter()
    client = TestClient(app)
    try:
        created = client.post("/experiments", json=PAYLOAD)
        experiment_id = created.json()["id"]
        pending = client.get(f"/experiments/{experiment_id}")
        assert pending.status_code == 202
        assert pending.json()["id"] == experiment_id
    finally:
        gate.set()
        app.state.adapter_factory = lambda: FixtureAdapter()
    done = _wait_paper(client, experiment_id)
    assert done.status_code == 200


def test_rejects_rounds_not_eight_and_unknown_variable(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    bad_rounds = {**PAYLOAD, "rounds": 7}
    assert client.post("/experiments", json=bad_rounds).status_code == 422
    bad_var = {**PAYLOAD, "variable_type": "marketing_spend"}
    assert client.post("/experiments", json=bad_var).status_code == 422


def test_openapi_docs_available():
    client = TestClient(app)
    docs = client.get("/docs")
    assert docs.status_code == 200
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    assert "/experiments" in spec.json()["paths"]


def test_cors_localhost_3000():
    client = TestClient(app)
    response = client.options(
        "/experiments",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_list_experiments_hides_golden_and_includes_created(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    golden = tmp_path / "grok-bot-seed-42"
    golden.mkdir()
    (golden / "experiment.json").write_text(
        '{"product_name": "Hidden Golden", "variable_delta": "+20%", "current_price": 120, "competitor_price": 100, "rounds": 8}',
        encoding="utf-8",
    )
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    experiment_id = created.json()["id"]
    listed = client.get("/experiments")
    assert listed.status_code == 200
    ids = [row["id"] for row in listed.json()]
    assert experiment_id in ids
    assert "grok-bot-seed-42" not in ids
    row = next(item for item in listed.json() if item["id"] == experiment_id)
    assert row["product_name"] == "Acme Analytics"
    assert row["variable_delta"] == "+20%"
