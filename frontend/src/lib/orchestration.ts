/** Frozen observation order — buyers, then competitor, then analyst. */

export const GOLDEN_ROUNDS = 8;

export const DEFAULT_AGENT_ORDER = [
  "buyer_1",
  "buyer_2",
  "buyer_3",
  "buyer_4",
  "buyer_5",
  "competitor",
  "analyst",
] as const;

export type PipelineId = (typeof DEFAULT_AGENT_ORDER)[number];

/** Percent positions inside the orchestration frame. */
export const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  price: { x: 50, y: 12 },
  buyer_1: { x: 12, y: 42 },
  buyer_2: { x: 30, y: 42 },
  buyer_3: { x: 50, y: 42 },
  buyer_4: { x: 70, y: 42 },
  buyer_5: { x: 88, y: 42 },
  competitor: { x: 50, y: 70 },
  analyst: { x: 28, y: 90 },
  outcome: { x: 72, y: 90 },
};

export const PIPELINE_EDGES: Array<[string, string]> = [
  ["price", "buyer_1"],
  ["price", "buyer_2"],
  ["price", "buyer_3"],
  ["price", "buyer_4"],
  ["price", "buyer_5"],
  ["buyer_1", "competitor"],
  ["buyer_2", "competitor"],
  ["buyer_3", "competitor"],
  ["buyer_4", "competitor"],
  ["buyer_5", "competitor"],
  ["competitor", "analyst"],
  ["competitor", "outcome"],
];

export const DEFAULT_WTP: Record<string, number> = {
  buyer_1: 105,
  buyer_2: 128,
  buyer_3: 140,
  buyer_4: 155,
  buyer_5: 180,
};

export function agentLabel(agentId: string): string {
  if (agentId === "competitor") return "competitor";
  if (agentId === "analyst") return "analyst";
  return agentId.replace("_", " ");
}

export function shortDecision(value: string | undefined): string {
  if (!value) return "—";
  return value;
}
