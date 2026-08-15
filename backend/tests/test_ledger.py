from __future__ import annotations

import asyncio
import time

import psycopg
from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.contracts import CreateExperimentRequest, Status
from app.ledger import InMemoryLedger
from app.main import app
from app.registry import ExperimentRegistry
from app.twin_runner import run_twin

from tests.test_http_experiments import PAYLOAD, _wait_roster_ready


def _grok() -> CreateExperimentRequest:
    return CreateExperimentRequest.model_validate(PAYLOAD)

def test_seq_is_monotonic_and_unique():
    ledger = InMemoryLedger()
    s1 = ledger.append("exp_a", "experiment.created", payload={"product_name": "Grok Bot"})
    s2 = ledger.append("exp_a", "roster.frozen", payload={"roster_hash": "abc"})
    s3 = ledger.append("exp_b", "experiment.created", payload={"product_name": "Other"})
    assert (s1, s2, s3) == (1, 2, 1)
    assert [e["seq"] for e in ledger.events("exp_a")] == [1, 2]


def test_observed_and_decided_are_separate_rows():
    ledger = InMemoryLedger()
    ledger.append("e", "agent.observed", run_id="A", round=1, agent_id="buyer_1", payload={"current_price": 120})
    ledger.append("e", "agent.decided", run_id="A", round=1, agent_id="buyer_1", payload={"decision": "stay"})
    types = [e["event_type"] for e in ledger.events("e")]
    assert types == ["agent.observed", "agent.decided"]


def test_append_rejects_empty_observe_payload():
    ledger = InMemoryLedger()
    try:
        ledger.append("e", "agent.observed", payload={})
        raise AssertionError("expected ValueError")
    except ValueError as err:
        assert "payload" in str(err)


def test_run_twin_appends_observed_then_decided_and_only_milestone_json(tmp_path):
    ledger = InMemoryLedger()
    result = asyncio.run(
        run_twin(_grok(), "exp-ledger", FixtureAdapter(), root=tmp_path, ledger=ledger)
    )
    assert result.status == Status.complete
    events = ledger.events("exp-ledger")
    types = [row["event_type"] for row in events]
    assert types[0] == "agent.observed"
    assert types[1] == "agent.decided"
    assert types == ["agent.observed", "agent.decided"] * (len(types) // 2)
    names = sorted(path.name for path in (tmp_path / "exp-ledger").glob("*.json"))
    assert names == ["experiment.json", "roster.json", "run_a.json", "run_b.json"]


def test_database_down_fails_experiment(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("app.settings.DATABASE_URL", "postgresql://ledger@127.0.0.1:1/none")

    def boom(*_args, **_kwargs):
        raise psycopg.OperationalError("could not connect")

    monkeypatch.setattr("app.main.psycopg.connect", boom)
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    experiment_id = created.json()["id"]
    _wait_roster_ready(client, experiment_id)
    started = client.post(f"/experiments/{experiment_id}/start")
    assert started.status_code == 202
    deadline = time.time() + 5
    while time.time() < deadline:
        if app.state.registry.status.get(experiment_id) == Status.failed:
            break
        time.sleep(0.05)
    assert app.state.registry.status[experiment_id] == Status.failed
    assert "database" in app.state.registry.errors[experiment_id]
