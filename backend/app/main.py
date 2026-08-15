"""US-B1: FastAPI entry with artifact GET. CORS and paper routes land in later stories."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.store import ARTIFACT_NAMES, read_artifact

app = FastAPI(title="Counterfactual Replay", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/experiments/{experiment_id}/artifacts/{name}")
def get_artifact(experiment_id: str, name: str) -> dict:
    if name not in ARTIFACT_NAMES:
        raise HTTPException(status_code=404, detail="unknown artifact")
    try:
        return read_artifact(experiment_id, name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="artifact not found") from None
