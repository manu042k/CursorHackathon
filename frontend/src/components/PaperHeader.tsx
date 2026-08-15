import { forkedPrice } from "@/lib/price";
import type { ExperimentPaper } from "@/types/contracts";

export function PaperHeader({ paper }: { paper: ExperimentPaper }) {
  const base = paper.experiment.current_price;
  const forked = forkedPrice(base, paper.experiment.variable_delta);
  return (
    <header className="paper-header">
      <p className="paper-header__kicker">Finding</p>
      <h1 className="paper-header__title">
        Baseline ${base} vs {paper.experiment.variable_delta} → ${forked}
      </h1>
    </header>
  );
}

export function MetricCards({ paper }: { paper: ExperimentPaper }) {
  const share = paper.metrics.final_share_delta_pp;
  const mrr = paper.metrics.final_mrr_delta;
  const left = paper.metrics.final_churn_count_b;
  const shareVerb = share < 0 ? "fell" : share > 0 ? "rose" : "held";
  const mrrVerb = mrr > 0 ? "rose" : mrr < 0 ? "fell" : "held";
  return (
    <ul className="metric-cards">
      <li className={share < 0 ? "metric-cards__item metric-cards__item--danger" : "metric-cards__item metric-cards__item--success"}>
        <p className="metric-cards__value">
          {share > 0 ? "+" : ""}
          {share}pp
        </p>
        <p className="metric-cards__verb">
          share <strong>{shareVerb}</strong>
        </p>
      </li>
      <li className={mrr > 0 ? "metric-cards__item metric-cards__item--success" : "metric-cards__item metric-cards__item--danger"}>
        <p className="metric-cards__value">
          {mrr >= 0 ? "+$" : "-$"}
          {Math.abs(mrr)}
        </p>
        <p className="metric-cards__verb">
          MRR <strong>{mrrVerb}</strong>
        </p>
      </li>
      <li className="metric-cards__item">
        <p className="metric-cards__value">{left}</p>
        <p className="metric-cards__verb">
          buyers <strong>left</strong>
        </p>
      </li>
    </ul>
  );
}
