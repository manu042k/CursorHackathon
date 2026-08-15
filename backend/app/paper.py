"""Assemble ExperimentPaper from twin artifacts. Attribution/narrative filled in later stories."""

from __future__ import annotations

from pathlib import Path

from app.contracts import (
    Adapter,
    CreateExperimentRequest,
    ExperimentLogs,
    ExperimentPaper,
    MetricSeries,
    Receipt,
    Roster,
    Runtime,
    Status,
    SummaryNarrative,
)
from app.store import read_artifact
from app.twin_runner import TwinResult


def metrics_from_runs(run_a: dict, run_b: dict) -> MetricSeries:
    share_a = [float(row["share"]) for row in run_a["trajectory"]]
    share_b = [float(row["share"]) for row in run_b["trajectory"]]
    mrr_a = [float(row["mrr"]) for row in run_a["trajectory"]]
    mrr_b = [float(row["mrr"]) for row in run_b["trajectory"]]
    churned = {
        log["agent_id"]
        for log in run_b.get("agent_logs", [])
        if str(log["agent_id"]).startswith("buyer_") and log["decision"] in {"churn", "switch"}
    }
    return MetricSeries(
        share_a=share_a,
        share_b=share_b,
        mrr_a=mrr_a,
        mrr_b=mrr_b,
        final_share_delta_pp=share_b[-1] - share_a[-1] if share_a else 0,
        final_mrr_delta=mrr_b[-1] - mrr_a[-1] if mrr_a else 0,
        final_churn_count_b=len(churned),
    )


def stub_receipt(experiment: CreateExperimentRequest, roster: Roster) -> Receipt:
    _ = roster
    model = "fixture" if experiment.adapter == Adapter.fixture else "composer-2.5"
    return Receipt(
        random_seed=experiment.random_seed,
        prompt_hash="sha256:pending",
        roster_hash="sha256:pending",
        other_variables_changed=0,
        adapter=experiment.adapter,
        runtime=Runtime.local,
        model=model,
        tools=[],
    )


def paper_from_result(result: TwinResult) -> ExperimentPaper:
    return ExperimentPaper(
        id=result.id,
        status=result.status,
        experiment=result.experiment,
        roster=result.roster,
        receipt=stub_receipt(result.experiment, result.roster),
        metrics=metrics_from_runs(result.run_a, result.run_b),
        divergence_by_round=[],
        summary_narrative=SummaryNarrative(text="", citations=[]),
        logs=ExperimentLogs(
            run_a=result.run_a.get("agent_logs", []),
            run_b=result.run_b.get("agent_logs", []),
        ),
    )


def paper_from_disk(experiment_id: str, root: Path | None = None) -> ExperimentPaper | None:
    try:
        experiment = CreateExperimentRequest.model_validate(
            read_artifact(experiment_id, "experiment", root=root)
        )
        roster = Roster.model_validate(read_artifact(experiment_id, "roster", root=root))
        run_a = read_artifact(experiment_id, "run_a", root=root)
        run_b = read_artifact(experiment_id, "run_b", root=root)
    except FileNotFoundError:
        return None
    divergence = []
    try:
        attribution = read_artifact(experiment_id, "attribution", root=root)
        divergence = attribution.get("divergence_by_round", [])
    except FileNotFoundError:
        pass
    narrative = SummaryNarrative(text="", citations=[])
    try:
        attribution = read_artifact(experiment_id, "attribution", root=root)
        raw = attribution.get("summary_narrative")
        if raw:
            narrative = SummaryNarrative.model_validate(raw)
    except FileNotFoundError:
        pass
    return ExperimentPaper(
        id=experiment_id,
        status=Status.complete,
        experiment=experiment,
        roster=roster,
        receipt=stub_receipt(experiment, roster),
        metrics=metrics_from_runs(run_a, run_b),
        divergence_by_round=divergence,
        summary_narrative=narrative,
        logs=ExperimentLogs(
            run_a=run_a.get("agent_logs", []),
            run_b=run_b.get("agent_logs", []),
        ),
    )
