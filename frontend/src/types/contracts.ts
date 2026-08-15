/** Frozen shared contract — architecture.md §9 and §11. Do not rename fields. */

export type RunId = "A" | "B";
export type Adapter = "cursor" | "fixture";
export type VariableType = "price_change";
export type BuyerDecision = "stay" | "churn" | "switch";
export type CompetitorDecision = "hold" | "undercut" | "match";
export type Status =
  | "created"
  | "running_a"
  | "running_b"
  | "attributing"
  | "complete"
  | "failed";
export type PriceSensitivity = "low" | "medium" | "high";
export type Runtime = "local";

export const ADAPTERS = ["cursor", "fixture"] as const satisfies readonly Adapter[];
export const STATUSES = [
  "created",
  "running_a",
  "running_b",
  "attributing",
  "complete",
  "failed",
] as const satisfies readonly Status[];
export const BUYER_DECISIONS = [
  "stay",
  "churn",
  "switch",
] as const satisfies readonly BuyerDecision[];
export const COMPETITOR_DECISIONS = [
  "hold",
  "undercut",
  "match",
] as const satisfies readonly CompetitorDecision[];
export const RUN_IDS = ["A", "B"] as const satisfies readonly RunId[];

export interface CreateExperimentRequest {
  product_name: string;
  product_description: string;
  current_price: number;
  market_size: number;
  competitor_count: number;
  competitor_price: number;
  buyer_price_sensitivity: PriceSensitivity;
  rounds: 8;
  random_seed: number;
  variable_type: VariableType;
  variable_delta: string;
  applies_from_round: number;
  adapter: Adapter;
}

export interface CreateExperimentResponse {
  id: string;
  status: Status;
}

export interface Receipt {
  random_seed: number;
  prompt_hash: string;
  roster_hash: string;
  other_variables_changed: 0;
  adapter: Adapter;
  runtime: Runtime;
  model: string;
  tools: [];
}

export interface MetricSeries {
  share_a: number[];
  share_b: number[];
  mrr_a: number[];
  mrr_b: number[];
  final_share_delta_pp: number;
  final_mrr_delta: number;
  final_churn_count_b: number;
}

export interface Contributor {
  agent_id: string;
  contribution_pct: number;
  reason: string;
}

export interface DivergenceRound {
  round: number;
  delta: number;
  top_contributors: Contributor[];
}

export interface AgentLog {
  round: number;
  agent_id: string;
  run_id: RunId;
  decision: string;
  reason: string;
  confidence: number;
}

export interface NarrativeCitation {
  agent_id: string;
  round: number;
  run_id: RunId;
}

export interface SummaryNarrative {
  text: string;
  citations: NarrativeCitation[];
}

export interface AgentRole {
  role: string;
  count: number;
  traits: Record<string, unknown>;
}

export interface RosterAgent {
  agent_id: string;
  role: string;
  weight: number;
  traits: Record<string, unknown>;
}

export interface Roster {
  agent_roles: AgentRole[];
  agents: RosterAgent[];
}

export interface ExperimentLogs {
  run_a: AgentLog[];
  run_b: AgentLog[];
}

export interface ExperimentPaper {
  id: string;
  status: Status;
  experiment: CreateExperimentRequest;
  roster: Roster;
  receipt: Receipt;
  metrics: MetricSeries;
  divergence_by_round: DivergenceRound[];
  summary_narrative: SummaryNarrative;
  logs: ExperimentLogs;
}

export interface HealthResponse {
  ok: boolean;
  cursor_configured: boolean;
  model: string | null;
  adapter: Adapter;
}

export interface DecisionEvent {
  run_id: RunId;
  round: number;
  agent_id: string;
  decision: string;
  reason: string;
  confidence: number;
  current_price: number;
}

export interface RoundCompleteEvent {
  run_id: RunId;
  round: number;
  share: number;
  mrr: number;
}

export interface CompleteEvent {
  id: string;
}

export interface FailedEvent {
  error: string;
}
