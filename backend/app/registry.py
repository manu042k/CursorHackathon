"""In-memory experiment status, SSE event log, and papers."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from app.contracts import ExperimentPaper, Status


@dataclass
class EventLog:
    items: list[tuple[str, dict]] = field(default_factory=list)
    done: bool = False


@dataclass
class ExperimentRegistry:
    status: dict[str, Status] = field(default_factory=dict)
    papers: dict[str, ExperimentPaper] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    events: dict[str, EventLog] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set_status(self, experiment_id: str, status: Status) -> None:
        with self._lock:
            self.status[experiment_id] = status
            self.events.setdefault(experiment_id, EventLog())

    def put_paper(self, paper: ExperimentPaper) -> None:
        with self._lock:
            self.papers[paper.id] = paper
            self.status[paper.id] = paper.status

    def append_event(self, experiment_id: str, name: str, data: dict) -> None:
        with self._lock:
            log = self.events.setdefault(experiment_id, EventLog())
            log.items.append((name, data))
            if name in {"complete", "failed"}:
                log.done = True

    def snapshot_events(self, experiment_id: str) -> tuple[list[tuple[str, dict]], bool]:
        with self._lock:
            log = self.events.get(experiment_id)
            if log is None:
                return [], False
            return list(log.items), log.done
