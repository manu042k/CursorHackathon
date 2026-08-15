"""US-B3: POST /experiments 202, GET paper 200/202, validation, OpenAPI, CORS."""

from __future__ import annotations

import threading
import time

from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.contracts import AgentDecision, AgentDecisionRequest, Status
from app.main import app
from app.registry import ExperimentRegistry
from app.store import read_artifact

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
            payload = last.json()
            if isinstance(payload, dict) and payload.get("status") == "complete":
                return last
        time.sleep(0.05)
    raise AssertionError(last.status_code if last else None, last.text if last else None)


def _wait_roster_ready(client: TestClient, experiment_id: str, timeout: float = 5.0):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = client.get(f"/experiments/{experiment_id}")
        if last.status_code == 200:
            payload = last.json()
            if isinstance(payload, dict) and payload.get("status") == "roster_ready":
                return last
        time.sleep(0.05)
    raise AssertionError(last.status_code if last else None, last.text if last else None)


def _start_after_roster(client: TestClient, payload: dict | None = None) -> str:
    created = client.post("/experiments", json=payload or PAYLOAD)
    experiment_id = created.json()["id"]
    _wait_roster_ready(client, experiment_id)
    started = client.post(f"/experiments/{experiment_id}/start")
    assert started.status_code == 202
    return experiment_id


def test_post_returns_202_and_get_paper_when_complete(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    assert created.status_code == 202
    body = created.json()
    assert "id" in body
    assert body["status"] == Status.researching.value
    _wait_roster_ready(client, body["id"])
    started = client.post(f"/experiments/{body['id']}/start")
    assert started.status_code == 202
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
        experiment_id = _start_after_roster(client)
        pending = client.get(f"/experiments/{experiment_id}")
        assert pending.status_code == 202
        assert pending.json()["id"] == experiment_id
    finally:
        gate.set()
        app.state.adapter_factory = lambda: FixtureAdapter()
    done = _wait_paper(client, experiment_id)
    assert done.status_code == 200


def test_rejects_rounds_outside_3_to_8_and_unknown_variable(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 2}).status_code == 422
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 9}).status_code == 422
    assert client.post("/experiments", json={**PAYLOAD, "rounds": 7}).status_code == 202
    for kind in ("price_change", "competitor_entry", "marketing_spend", "feature_change"):
        assert client.post("/experiments", json={**PAYLOAD, "variable_type": kind}).status_code == 202
    bad_var = {**PAYLOAD, "variable_type": "ad_auction"}
    assert client.post("/experiments", json=bad_var).status_code == 422


def test_rejects_applies_from_round_past_rounds(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    body = {**PAYLOAD, "rounds": 4, "applies_from_round": 5}
    assert client.post("/experiments", json=body).status_code == 422


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


def test_create_does_not_start_twin_until_start(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    assert created.status_code == 202
    assert created.json()["status"] == "researching"
    experiment_id = created.json()["id"]
    time.sleep(0.2)
    pending = client.get(f"/experiments/{experiment_id}")
    assert pending.status_code in {200, 202}
    body = pending.json()
    assert body["status"] in {"researching", "roster_ready"}
    try:
        read_artifact(experiment_id, "run_a")
        raise AssertionError("twin started before /start")
    except FileNotFoundError:
        pass
    _wait_roster_ready(client, experiment_id)
    started = client.post(f"/experiments/{experiment_id}/start")
    assert started.status_code == 202
    paper = _wait_paper(client, experiment_id)
    assert paper.status_code == 200
