import { firstMajorRound } from "@/lib/rounds";
import type { ExperimentPaper } from "@/types/contracts";

function fmtPp(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  const text = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  return `${rounded > 0 ? "+" : ""}${text}pp`;
}

function verb(delta: number, up: string, down: string, flat: string): string {
  if (delta > 0) return up;
  if (delta < 0) return down;
  return flat;
}

export function FindingSummary({ paper }: { paper: ExperimentPaper }) {
  const exp = paper.experiment;
  const share = paper.metrics.final_share_delta_pp;
  const mrr = paper.metrics.final_mrr_delta;
  const left = paper.metrics.final_churn_count_b;
  const split = firstMajorRound(paper);
  const mrrAbs = Math.round(Math.abs(mrr)).toLocaleString();
  return (
    <section className="finding__summary" aria-label="Summary">
      <h2>What this run showed</h2>
      <p>
        {exp.product_name}: {exp.variable_type.replace(/_/g, " ")} {exp.variable_delta} from round{" "}
        {exp.applies_from_round}, held for {exp.rounds} rounds. Same seed, same roster, 0 other
        variables.
      </p>
      <ul>
        <li>
          Share {verb(share, "rose", "fell", "held")} {fmtPp(share)} on Run B versus baseline.
        </li>
        <li>
          MRR {verb(mrr, "rose", "fell", "held")} {mrr >= 0 ? "+$" : "−$"}
          {mrrAbs}.
        </li>
        <li>
          {left} buyer{left === 1 ? "" : "s"} left on B. The gap opened at R{split}.
        </li>
      </ul>
      <p className="finding__summary-claim">{paper.summary_narrative.text}</p>
      <p className="finding__summary-note">
        Causality is inside this frozen market, not a forecast of the real one.
      </p>
    </section>
  );
}
