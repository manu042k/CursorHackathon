import type { ExperimentPaper } from "@/types/contracts";

export function firstMajorRound(paper: ExperimentPaper): number {
  const { share_a: a, share_b: b } = paper.metrics;
  for (let i = 0; i < a.length; i += 1) {
    if (Math.abs(a[i] - b[i]) >= 8) return i + 1;
  }
  let best = 1;
  let bestGap = -1;
  for (let i = 0; i < a.length; i += 1) {
    const gap = Math.abs(a[i] - b[i]);
    if (gap > bestGap) {
      bestGap = gap;
      best = i + 1;
    }
  }
  return best;
}
