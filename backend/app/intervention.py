"""Apply exactly one intervention on Run B from applies_from_round."""

from __future__ import annotations

from dataclasses import dataclass

from app.contracts import CreateExperimentRequest, RunId, VariableType
from app.market import parse_price_delta


@dataclass(frozen=True)
class ForkSnapshot:
    current_price: float
    competitor_price: float
    competitor_count: int
    marketing_spend: float
    feature_change: str


def parse_spend(list_price: float, market_size: int, delta: str) -> float:
    text = delta.strip().lstrip("+")
    if text.endswith("%"):
        pct = abs(float(text[:-1]))
        return float(round(list_price * market_size * pct / 100.0))
    return abs(float(text))


def apply_fork(
    experiment: CreateExperimentRequest, run_id: RunId, round_n: int
) -> ForkSnapshot:
    baseline = ForkSnapshot(
        current_price=experiment.current_price,
        competitor_price=experiment.competitor_price,
        competitor_count=experiment.competitor_count,
        marketing_spend=0.0,
        feature_change="",
    )
    if run_id != RunId.B or round_n < experiment.applies_from_round:
        return baseline
    delta = experiment.variable_delta
    kind = experiment.variable_type
    if kind == VariableType.price_change:
        return ForkSnapshot(
            current_price=parse_price_delta(experiment.current_price, delta),
            competitor_price=baseline.competitor_price,
            competitor_count=baseline.competitor_count,
            marketing_spend=0.0,
            feature_change="",
        )
    if kind == VariableType.competitor_entry:
        return ForkSnapshot(
            current_price=baseline.current_price,
            competitor_price=parse_price_delta(experiment.competitor_price, delta),
            competitor_count=max(experiment.competitor_count, 1) + 1,
            marketing_spend=0.0,
            feature_change="",
        )
    if kind == VariableType.marketing_spend:
        return ForkSnapshot(
            current_price=baseline.current_price,
            competitor_price=baseline.competitor_price,
            competitor_count=baseline.competitor_count,
            marketing_spend=parse_spend(
                experiment.current_price, experiment.market_size, delta
            ),
            feature_change="",
        )
    return ForkSnapshot(
        current_price=baseline.current_price,
        competitor_price=baseline.competitor_price,
        competitor_count=baseline.competitor_count,
        marketing_spend=0.0,
        feature_change=delta.strip(),
    )
