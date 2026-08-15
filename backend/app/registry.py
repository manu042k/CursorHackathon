"""In-memory experiment status for 202-while-running. Disk is the record."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.contracts import ExperimentPaper, Status


@dataclass
class ExperimentRegistry:
    status: dict[str, Status] = field(default_factory=dict)
    papers: dict[str, ExperimentPaper] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def set_status(self, experiment_id: str, status: Status) -> None:
        self.status[experiment_id] = status

    def put_paper(self, paper: ExperimentPaper) -> None:
        self.papers[paper.id] = paper
        self.status[paper.id] = paper.status
