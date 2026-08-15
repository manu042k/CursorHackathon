"""Assemble ExperimentPaper from twin artifacts. Attribution/narrative filled in later stories."""

from __future__ import annotations

from pathlib import Path

from app.contracts import (
    CreateExperimentRequest,
    ExperimentLogs,
    ExperimentPaper,
    MetricSeries,
    Roster,
    Status,
    SummaryNarrative,
)
from app.attribution import attribute_result, attribute_runs
from app.narrative import build_receipt, grounded_narrative
from app.store import read_artifact, write_artifact
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


def _paper_rounds(raw: list) -> list:
    allowed = {"round", "delta", "top_contributors"}
    return [{key: row[key] for key in allowed if key in row} for row in raw]


def _narrative(experiment, metrics, divergence, run_a, run_b) -> SummaryNarrative:
    try:
        return grounded_narrative(experiment, metrics, divergence, run_a, run_b)
    except Exception:
        return SummaryNarrative(text="", citations=[])


def paper_from_result(result: TwinResult) -> ExperimentPaper:
    attribution = attribute_result(result)
    divergence = _paper_rounds(attribution["divergence_by_round"]) if attribution else []
    metrics = metrics_from_runs(result.run_a, result.run_b)
    return ExperimentPaper(
        id=result.id,
        status=result.status,
        experiment=result.experiment,
        roster=result.roster,
        receipt=build_receipt(result.experiment, result.roster),
        metrics=metrics,
        divergence_by_round=divergence,
        summary_narrative=_narrative(
            result.experiment, metrics, divergence, result.run_a, result.run_b
        ),
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
        divergence = _paper_rounds(attribution.get("divergence_by_round", []))
    except FileNotFoundError:
        attribution = attribute_runs(run_a, run_b, roster)
        write_artifact(experiment_id, "attribution", attribution, root=root)
        divergence = _paper_rounds(attribution.get("divergence_by_round", []))
    metrics = metrics_from_runs(run_a, run_b)
    narrative = SummaryNarrative(text="", citations=[])
    try:
        stored = read_artifact(experiment_id, "attribution", root=root)
        raw = stored.get("summary_narrative")
        if raw:
            narrative = SummaryNarrative.model_validate(raw)
    except FileNotFoundError:
        pass
    if not narrative.citations:
        narrative = _narrative(experiment, metrics, divergence, run_a, run_b)
    return ExperimentPaper(
        id=experiment_id,
        status=Status.complete,
        experiment=experiment,
        roster=roster,
        receipt=build_receipt(experiment, roster),
        metrics=metrics,
        divergence_by_round=divergence,
        summary_narrative=narrative,
        logs=ExperimentLogs(
            run_a=run_a.get("agent_logs", []),
            run_b=run_b.get("agent_logs", []),
        ),
    )
