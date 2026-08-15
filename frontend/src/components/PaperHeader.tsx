import { forkedPrice } from "@/lib/price";
import type { ExperimentPaper } from "@/types/contracts";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function PaperHeader({ paper }: { paper: ExperimentPaper }) {
  const kind = paper.experiment.variable_type;
  const delta = paper.experiment.variable_delta;
  let title = `${kind} ${delta}`;
  if (kind === "price_change") {
    const forked = forkedPrice(paper.experiment.current_price, delta);
    title = `Baseline $${paper.experiment.current_price} vs ${delta} → $${forked}`;
  } else if (kind === "competitor_entry") {
    const forked = forkedPrice(paper.experiment.competitor_price, delta);
    title = `Rival $${paper.experiment.competitor_price} vs ${delta} → $${forked}`;
  }
  return (
    <header className="space-y-1">
      <p className="text-sm text-muted-foreground">Finding</p>
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
    </header>
  );
}

function fmtPp(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  const text = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  return `${rounded > 0 ? "+" : ""}${text}pp`;
}

export function MetricCards({ paper }: { paper: ExperimentPaper }) {
  const share = paper.metrics.final_share_delta_pp;
  const mrr = paper.metrics.final_mrr_delta;
  const left = paper.metrics.final_churn_count_b;
  const shareVerb = share < 0 ? "fell" : share > 0 ? "rose" : "held";
  const mrrVerb = mrr > 0 ? "rose" : mrr < 0 ? "fell" : "held";
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <Card className={share < 0 ? "metric-cards__item metric-cards__item--danger" : "metric-cards__item metric-cards__item--success"}>
        <CardHeader>
          <CardTitle className="metric-cards__value text-3xl font-semibold">{fmtPp(share)}</CardTitle>
          <CardDescription className="metric-cards__verb">
            share <strong>{shareVerb}</strong>
          </CardDescription>
        </CardHeader>
      </Card>
      <Card className={mrr > 0 ? "metric-cards__item metric-cards__item--success" : "metric-cards__item metric-cards__item--danger"}>
        <CardHeader>
          <CardTitle className="metric-cards__value text-3xl font-semibold">
            {mrr >= 0 ? "+$" : "-$"}
            {Math.round(Math.abs(mrr)).toLocaleString()}
          </CardTitle>
          <CardDescription className="metric-cards__verb">
            MRR <strong>{mrrVerb}</strong>
          </CardDescription>
        </CardHeader>
      </Card>
      <Card className="metric-cards__item">
        <CardHeader>
          <CardTitle className="metric-cards__value text-3xl font-semibold">{left}</CardTitle>
          <CardDescription className="metric-cards__verb">
            buyers <strong>left</strong>
          </CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
}
