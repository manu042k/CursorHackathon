"""Experiment directory on disk. Atomic JSON writes. Architecture §ADR-2."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

ARTIFACT_NAMES = ("experiment", "roster", "run_a", "run_b", "attribution")


def data_root() -> Path:
    override = os.environ.get("DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "data" / "experiments"


def experiment_dir(experiment_id: str, root: Path | None = None) -> Path:
    return (root or data_root()) / experiment_id


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def write_artifact(experiment_id: str, name: str, payload: Any, root: Path | None = None) -> Path:
    if name not in ARTIFACT_NAMES:
        raise ValueError(f"unknown artifact {name}")
    path = experiment_dir(experiment_id, root) / f"{name}.json"
    write_json(path, payload)
    return path


def read_artifact(experiment_id: str, name: str, root: Path | None = None) -> Any:
    if name not in ARTIFACT_NAMES:
        raise ValueError(f"unknown artifact {name}")
    path = experiment_dir(experiment_id, root) / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))
