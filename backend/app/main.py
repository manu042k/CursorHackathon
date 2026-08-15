"""US-B3/B5: FastAPI create, paper fetch, and SSE progress."""

from __future__ import annotations

import asyncio
import json
import threading
import uuid

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.fixture import FixtureAdapter
from app.attribution import attribute_result
from app.contracts import CreateExperimentRequest, CreateExperimentResponse, Status
from app.paper import paper_from_disk, paper_from_result
from app.registry import ExperimentRegistry
from app.store import ARTIFACT_NAMES, read_artifact, write_artifact
from app.twin_runner import run_twin

app = FastAPI(title="Counterfactual Replay", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.registry = ExperimentRegistry()
app.state.adapter_factory = lambda: FixtureAdapter()


def _execute(experiment_id: str, body: CreateExperimentRequest) -> None:
    registry: ExperimentRegistry = app.state.registry
    registry.set_status(experiment_id, Status.running_a)

    def on_round(run_id, round_n, share, mrr):
        registry.append_event(
            experiment_id,
            "round_complete",
            {
                "run_id": run_id.value,
                "round": round_n,
                "share": share,
                "mrr": mrr,
            },
        )

    try:
        result = asyncio.run(
            run_twin(
                body,
                experiment_id,
                app.state.adapter_factory(),
                on_round=on_round,
            )
        )
        registry.set_status(
            experiment_id,
            Status.running_b if result.status != Status.failed else Status.failed,
        )
        if result.status == Status.complete:
            registry.set_status(experiment_id, Status.attributing)
        attribution = attribute_result(result)
        if attribution is not None:
            write_artifact(experiment_id, "attribution", attribution)
        paper = paper_from_result(result)
        registry.put_paper(paper)
        if result.error:
            registry.errors[experiment_id] = result.error
            registry.append_event(experiment_id, "failed", {"error": result.error})
        else:
            registry.append_event(experiment_id, "complete", {"id": experiment_id})
    except Exception as exc:
        registry.set_status(experiment_id, Status.failed)
        registry.errors[experiment_id] = str(exc)
        registry.append_event(experiment_id, "failed", {"error": str(exc)})


@app.post("/experiments", status_code=202, response_model=CreateExperimentResponse)
def create_experiment(body: CreateExperimentRequest) -> CreateExperimentResponse:
    experiment_id = f"exp_{uuid.uuid4().hex[:10]}"
    app.state.registry.set_status(experiment_id, Status.created)
    write_artifact(experiment_id, "experiment", body.model_dump(mode="json"))
    threading.Thread(target=_execute, args=(experiment_id, body), daemon=True).start()
    return CreateExperimentResponse(id=experiment_id, status=Status.created)


@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: str, response: Response):
    registry: ExperimentRegistry = app.state.registry
    status = registry.status.get(experiment_id)
    if status in {
        Status.created,
        Status.running_a,
        Status.running_b,
        Status.attributing,
    }:
        response.status_code = 202
        return CreateExperimentResponse(id=experiment_id, status=status)
    if experiment_id in registry.papers:
        return registry.papers[experiment_id].model_dump(mode="json")
    paper = paper_from_disk(experiment_id)
    if paper is not None:
        return paper.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="experiment not found")


@app.get("/experiments/{experiment_id}/events")
async def experiment_events(experiment_id: str):
    registry: ExperimentRegistry = app.state.registry
    items, _done = registry.snapshot_events(experiment_id)
    if experiment_id not in registry.status and not items:
        raise HTTPException(status_code=404, detail="experiment not found")

    async def generate():
        idx = 0
        while True:
            batch, finished = registry.snapshot_events(experiment_id)
            while idx < len(batch):
                name, data = batch[idx]
                idx += 1
                yield f"event: {name}\ndata: {json.dumps(data)}\n\n"
            if finished:
                break
            await asyncio.sleep(0.05)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/experiments/{experiment_id}/artifacts/{name}")
def get_artifact(experiment_id: str, name: str) -> dict:
    if name not in ARTIFACT_NAMES:
        raise HTTPException(status_code=404, detail="unknown artifact")
    try:
        return read_artifact(experiment_id, name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="artifact not found") from None
