import type { RunId } from "@/types/contracts";

/** Owner-facing names. API run_id stays A / B. */
export const RUN_LABEL: Record<RunId, string> = {
  A: "Current",
  B: "Changed",
};

export function runLabel(id: RunId | string): string {
  if (id === "A" || id === "B") return RUN_LABEL[id];
  return String(id);
}
