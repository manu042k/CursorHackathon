"""US-B3/B5: FastAPI create, paper fetch, and SSE progress."""

from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid

from datetime import datetime, timezone
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.cursor_adapter import CursorSdkAdapter
from app.agents.fixture import FixtureAdapter
from app.attribution import attribute_result
from app.contracts import (
    Adapter,
    CreateExperimentRequest,
    CreateExperimentResponse,
    ExperimentListItem,
    HealthResponse,
    Status,
)
from app import settings
from app.cursor_client import cursor_lifespan
from app.ledger import InMemoryLedger, PostgresLedger
from app.paper import paper_from_disk, paper_from_result
from app.registry import ExperimentRegistry
from app.roster.generate import propose_roster
from app.store import (
    ARTIFACT_NAMES,
    HIDDEN_EXPERIMENT_IDS,
    disk_status,
    list_experiment_folders,
    read_artifact,
    write_artifact,
)
from app.twin_runner import run_twin

app = FastAPI(title="Counterfactual Replay", version="0.1.0", lifespan=cursor_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.registry = ExperimentRegistry()
app.state.cursor = None
app.state.adapter_factory = lambda: FixtureAdapter()


def _adapter_for(body: CreateExperimentRequest):
    if body.adapter == Adapter.cursor and getattr(app.state, "cursor", None) is not None:
        return CursorSdkAdapter(app.state.cursor)
    return app.state.adapter_factory()


def _research(experiment_id: str, body: CreateExperimentRequest) -> None:
    registry: ExperimentRegistry = app.state.registry
    registry.set_status(experiment_id, Status.researching)
    registry.append_event(experiment_id, "research_started", {"id": experiment_id})
    try:
        roster = propose_roster(body, adapter=body.adapter, experiment_id=experiment_id)
        write_artifact(experiment_id, "roster", roster.model_dump(mode="json"))
        registry.set_status(experiment_id, Status.roster_ready)
        registry.append_event(experiment_id, "research_complete", {"id": experiment_id})
    except Exception as exc:
        registry.set_status(experiment_id, Status.failed)
        registry.errors[experiment_id] = str(exc)
        registry.append_event(experiment_id, "failed", {"error": str(exc)})


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

    def on_decision(payload):
        registry.append_event(experiment_id, "decision", payload)

    ledger = None
    conn = None
    if settings.DATABASE_URL:
        try:
            conn = psycopg.connect(settings.DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO experiments (
                        id, status, product_name, product_description,
                        current_price, market_size, competitor_count, competitor_price,
                        buyer_price_sensitivity, rounds, random_seed,
                        variable_type, variable_delta, applies_from_round, adapter
                    ) VALUES (
                        %s, 'created', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        experiment_id,
                        body.product_name,
                        body.product_description,
                        body.current_price,
                        body.market_size,
                        body.competitor_count,
                        body.competitor_price,
                        body.buyer_price_sensitivity.value,
                        body.rounds,
                        body.random_seed,
                        body.variable_type.value,
                        body.variable_delta,
                        body.applies_from_round,
                        body.adapter.value,
                    ),
                )
                conn.commit()
            ledger = PostgresLedger(conn)
        except psycopg.Error as exc:
            registry.set_status(experiment_id, Status.failed)
            registry.errors[experiment_id] = f"database connection failed: {type(exc).__name__}"
            registry.append_event(
                experiment_id, "failed", {"error": f"database: {type(exc).__name__}"}
            )
            return
    else:
        ledger = InMemoryLedger()

    try:
        result = asyncio.run(
            run_twin(
                body,
                experiment_id,
                _adapter_for(body),
                on_round=on_round,
                on_decision=on_decision,
                ledger=ledger,
            )
        )
        registry.set_status(
            experiment_id,
            Status.running_b if result.status != Status.failed else Status.failed,
        )
        if result.status == Status.complete:
            registry.set_status(experiment_id, Status.attributing)
        paper = paper_from_result(result)
        attribution = attribute_result(result)
        if attribution is not None:
            attribution["summary_narrative"] = paper.summary_narrative.model_dump(mode="json")
            write_artifact(experiment_id, "attribution", attribution)
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
    finally:
        if conn:
            conn.close()


@app.post("/experiments", status_code=202, response_model=CreateExperimentResponse)
def create_experiment(body: CreateExperimentRequest) -> CreateExperimentResponse:
    experiment_id = f"exp_{uuid.uuid4().hex[:10]}"
    app.state.registry.set_status(experiment_id, Status.researching)
    write_artifact(experiment_id, "experiment", body.model_dump(mode="json"))
    threading.Thread(target=_research, args=(experiment_id, body), daemon=True).start()
    return CreateExperimentResponse(id=experiment_id, status=Status.researching)


@app.post(
    "/experiments/{experiment_id}/start",
    status_code=202,
    response_model=CreateExperimentResponse,
)
def start_experiment(experiment_id: str) -> CreateExperimentResponse:
    status = app.state.registry.status.get(experiment_id)
    if status != Status.roster_ready:
        raise HTTPException(status_code=409, detail="roster not ready")
    body = CreateExperimentRequest.model_validate(read_artifact(experiment_id, "experiment"))
    app.state.registry.set_status(experiment_id, Status.running_a)
    threading.Thread(target=_execute, args=(experiment_id, body), daemon=True).start()
    return CreateExperimentResponse(id=experiment_id, status=Status.running_a)


def _list_item_from_folder(folder: Path, registry: ExperimentRegistry) -> ExperimentListItem | None:
    experiment_path = folder / "experiment.json"
    if not experiment_path.is_file():
        return None
    try:
        body = json.loads(experiment_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    status = registry.status.get(folder.name)
    if status is None:
        status = Status(disk_status(folder))
    updated = datetime.fromtimestamp(experiment_path.stat().st_mtime, tz=timezone.utc)
    return ExperimentListItem(
        id=folder.name,
        status=status,
        product_name=str(body.get("product_name") or "Untitled"),
        variable_delta=str(body.get("variable_delta") or ""),
        current_price=float(body.get("current_price") or 0),
        competitor_price=float(body.get("competitor_price") or 0),
        rounds=int(body.get("rounds") or 4),
        updated_at=updated.isoformat(),
    )


@app.get("/experiments", response_model=list[ExperimentListItem])
def list_experiments() -> list[ExperimentListItem]:
    registry: ExperimentRegistry = app.state.registry
    items: list[ExperimentListItem] = []
    seen: set[str] = set()
    for folder in list_experiment_folders():
        item = _list_item_from_folder(folder, registry)
        if item is None:
            continue
        items.append(item)
        seen.add(item.id)
    for experiment_id, status in registry.status.items():
        if experiment_id in seen or experiment_id in HIDDEN_EXPERIMENT_IDS:
            continue
        paper = registry.papers.get(experiment_id)
        experiment = paper.experiment if paper else None
        items.insert(
            0,
            ExperimentListItem(
                id=experiment_id,
                status=status,
                product_name=experiment.product_name if experiment else "Untitled",
                variable_delta=experiment.variable_delta if experiment else "",
                current_price=experiment.current_price if experiment else 0,
                competitor_price=experiment.competitor_price if experiment else 0,
                rounds=int(experiment.rounds) if experiment else 4,
                updated_at=datetime.now(timezone.utc).isoformat(),
            ),
        )
    return items


@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: str, response: Response):
    registry: ExperimentRegistry = app.state.registry
    status = registry.status.get(experiment_id)
    if status in {
        Status.created,
        Status.researching,
        Status.running_a,
        Status.running_b,
        Status.attributing,
    }:
        response.status_code = 202
        return CreateExperimentResponse(id=experiment_id, status=status)
    if status == Status.roster_ready:
        try:
            roster = read_artifact(experiment_id, "roster")
        except FileNotFoundError:
            response.status_code = 202
            return CreateExperimentResponse(id=experiment_id, status=status)
        return {"id": experiment_id, "status": status.value, "roster": roster}
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
                await asyncio.sleep(0.2)
                break
            await asyncio.sleep(0.05)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    key_present = bool(os.environ.get("CURSOR_API_KEY", ""))
    configured = key_present and getattr(app.state, "cursor", None) is not None
    return HealthResponse(
        ok=True,
        cursor_configured=key_present,
        model=os.environ.get("CURSOR_MODEL", settings.CURSOR_MODEL) if key_present else None,
        adapter=Adapter.cursor if configured else Adapter.fixture,
    )


@app.get("/experiments/{experiment_id}/artifacts/{name}")
def get_artifact(experiment_id: str, name: str) -> dict:
    if name not in ARTIFACT_NAMES:
        raise HTTPException(status_code=404, detail="unknown artifact")
    try:
        return read_artifact(experiment_id, name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="artifact not found") from None
