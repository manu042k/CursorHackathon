"""Frozen shared contract — architecture.md §9 and §11. Do not rename fields."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Adapter(str, Enum):
    cursor = "cursor"
    fixture = "fixture"


class VariableType(str, Enum):
    price_change = "price_change"


class RunId(str, Enum):
    A = "A"
    B = "B"


class BuyerDecision(str, Enum):
    stay = "stay"
    churn = "churn"
    switch = "switch"


class CompetitorDecision(str, Enum):
    hold = "hold"
    undercut = "undercut"
    match = "match"


class Status(str, Enum):
    created = "created"
    running_a = "running_a"
    running_b = "running_b"
    attributing = "attributing"
    complete = "complete"
    failed = "failed"


class PriceSensitivity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Runtime(str, Enum):
    local = "local"


class CreateExperimentRequest(FrozenModel):
    product_name: str
    product_description: str
    current_price: float
    market_size: int
    competitor_count: int
    competitor_price: float
    buyer_price_sensitivity: PriceSensitivity
    rounds: Literal[8] = 8
    random_seed: int
    variable_type: VariableType
    variable_delta: str
    applies_from_round: int
    adapter: Adapter


class CreateExperimentResponse(FrozenModel):
    id: str
    status: Status


class Receipt(FrozenModel):
    random_seed: int
    prompt_hash: str
    roster_hash: str
    other_variables_changed: Literal[0] = 0
    adapter: Adapter
    runtime: Runtime = Runtime.local
    model: str
    tools: list[str] = Field(default_factory=list)


class MetricSeries(FrozenModel):
    share_a: list[float]
    share_b: list[float]
    mrr_a: list[float]
    mrr_b: list[float]
    final_share_delta_pp: float
    final_mrr_delta: float
    final_churn_count_b: int


class Contributor(FrozenModel):
    agent_id: str
    contribution_pct: float
    reason: str


class DivergenceRound(FrozenModel):
    round: int
    delta: float
    top_contributors: list[Contributor] = Field(default_factory=list)


class AgentLog(FrozenModel):
    round: int
    agent_id: str
    run_id: RunId
    decision: str
    reason: str
    confidence: float


class NarrativeCitation(FrozenModel):
    agent_id: str
    round: int
    run_id: RunId


class SummaryNarrative(FrozenModel):
    text: str
    citations: list[NarrativeCitation] = Field(default_factory=list)


class AgentRole(FrozenModel):
    role: str
    count: int
    traits: dict[str, Any] = Field(default_factory=dict)


class RosterAgent(FrozenModel):
    agent_id: str
    role: str
    weight: float
    traits: dict[str, Any] = Field(default_factory=dict)


class Roster(FrozenModel):
    agent_roles: list[AgentRole] = Field(default_factory=list)
    agents: list[RosterAgent] = Field(default_factory=list)


class ExperimentLogs(FrozenModel):
    run_a: list[AgentLog] = Field(default_factory=list)
    run_b: list[AgentLog] = Field(default_factory=list)


class ExperimentPaper(FrozenModel):
    id: str
    status: Status
    experiment: CreateExperimentRequest
    roster: Roster
    receipt: Receipt
    metrics: MetricSeries
    divergence_by_round: list[DivergenceRound] = Field(default_factory=list)
    summary_narrative: SummaryNarrative
    logs: ExperimentLogs


class HealthResponse(FrozenModel):
    ok: bool
    cursor_configured: bool
    model: str | None = None
    adapter: Adapter


class RoundCompleteEvent(FrozenModel):
    run_id: RunId
    round: int
    share: float
    mrr: float


class CompleteEvent(FrozenModel):
    id: str


class FailedEvent(FrozenModel):
    error: str


class AgentDecisionRequest(FrozenModel):
    experiment_id: str = "acme-seed-42"
    run_id: RunId
    agent_id: str
    round: int
    current_price: float
    competitor_price: float = 45
    persona: dict[str, Any] = Field(default_factory=dict)
    status: str = "subscribed"
    history_summary: str = ""


class AgentDecision(FrozenModel):
    decision: str
    reason: str
    confidence: float

