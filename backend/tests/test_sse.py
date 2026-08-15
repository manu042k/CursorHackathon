"""US-B5: SSE round_complete / complete / failed; reconnect does not rewrite artifacts."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.agents.fixture import FixtureAdapter
from app.main import app
from app.registry import ExperimentRegistry
from app.store import experiment_dir
from tests.test_http_experiments import PAYLOAD, _wait_paper


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    event_name = None
    for line in text.splitlines():
        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].strip()
        elif line.startswith("data:") and event_name:
            events.append((event_name, json.loads(line.split(":", 1)[1])))
            event_name = None
    return events


def _read_until_terminal(client: TestClient, experiment_id: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    with client.stream("GET", f"/experiments/{experiment_id}/events") as response:
        assert response.status_code == 200
        buf = ""
        for chunk in response.iter_text():
            buf += chunk
            while "\n\n" in buf:
                block, buf = buf.split("\n\n", 1)
                events.extend(_parse_sse(block + "\n\n"))
                if events and events[-1][0] in {"complete", "failed"}:
                    return events
    return events


def test_sse_round_complete_and_complete(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: FixtureAdapter()
    client = TestClient(app)
    created = client.post("/experiments", json=PAYLOAD)
    experiment_id = created.json()["id"]
    events = _read_until_terminal(client, experiment_id)
    rounds = [payload for name, payload in events if name == "round_complete"]
    assert len(rounds) == 16
    assert set(rounds[0]) == {"run_id", "round", "share", "mrr"}
    assert rounds[0]["run_id"] in {"A", "B"}
    assert 1 <= rounds[0]["round"] <= 8
    assert events[-1] == ("complete", {"id": experiment_id})
    decisions = [payload for name, payload in events if name == "decision"]
    assert len(decisions) >= 16
    assert {"run_id", "round", "agent_id", "decision", "reason", "confidence"} <= set(decisions[0])
    assert len(decisions[0]["reason"]) >= 20
    _wait_paper(client, experiment_id)

    folder = experiment_dir(experiment_id, tmp_path)
    assert (folder / "run_a.json").is_file()
    replay = _read_until_terminal(client, experiment_id)
    assert [name for name, _ in replay] == [name for name, _ in events]
    assert list(folder.glob("run_a.json")) == [folder / "run_a.json"]
    leftovers = list(folder.glob("run_a.json.*"))
    assert leftovers == []


def test_sse_failed_terminal(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.contracts import AgentDecision, AgentDecisionRequest, RunId

    inner = FixtureAdapter()

    class Broken:
        async def decide(self, request: AgentDecisionRequest) -> AgentDecision:
            if request.run_id == RunId.B and request.agent_id == "buyer_5" and request.round == 1:
                return AgentDecision(
                    decision="churn",
                    reason="Forced misalignment for the SSE failed-event test at round 1.",
                    confidence=0.99,
                )
            return await inner.decide(request)

    app.state.registry = ExperimentRegistry()
    app.state.adapter_factory = lambda: Broken()
    client = TestClient(app)
    payload = {**PAYLOAD, "applies_from_round": 3}
    created = client.post("/experiments", json=payload)
    experiment_id = created.json()["id"]
    events = _read_until_terminal(client, experiment_id)
    assert events[-1][0] == "failed"
    assert events[-1][1]["error"] == "alignment_broken"
    app.state.adapter_factory = lambda: FixtureAdapter()
