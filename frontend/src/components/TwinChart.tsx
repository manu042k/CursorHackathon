"use client";

import { useState, type KeyboardEvent } from "react";
import { TrajectoryChart, type ChartMetric } from "@/components/TrajectoryChart";
import { forkedPrice } from "@/lib/price";
import type { ExperimentPaper } from "@/types/contracts";

type Props = {
  paper: ExperimentPaper;
  selectedRound: number;
  onSelectRound: (round: number) => void;
};

export function TwinChart({ paper, selectedRound, onSelectRound }: Props) {
  const [metric, setMetric] = useState<ChartMetric>("share");
  const seriesA = metric === "share" ? paper.metrics.share_a : paper.metrics.mrr_a;
  const seriesB = metric === "share" ? paper.metrics.share_b : paper.metrics.mrr_b;
  const base = paper.experiment.current_price;
  const forked = forkedPrice(base, paper.experiment.variable_delta);
  const rounds = seriesA.map((_, i) => i + 1);

  function onKey(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      onSelectRound(Math.max(1, selectedRound - 1));
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      onSelectRound(Math.min(seriesA.length, selectedRound + 1));
    }
  }

  return (
    <section className="twin-chart" tabIndex={0} onKeyDown={onKey} aria-label="Twin trajectory">
      <div className="twin-chart__toolbar">
        <p className="twin-chart__legend">
          <span className="twin-chart__swatch twin-chart__swatch--a" />
          Run A · ${base}
          <span className="twin-chart__swatch twin-chart__swatch--b" />
          Run B · ${forked}
        </p>
        <div className="twin-chart__toggle" role="tablist">
          <button
            type="button"
            className={metric === "share" ? "is-active" : ""}
            onClick={() => setMetric("share")}
          >
            Share (%)
          </button>
          <button
            type="button"
            className={metric === "mrr" ? "is-active" : ""}
            onClick={() => setMetric("mrr")}
          >
            MRR ($)
          </button>
        </div>
      </div>
      <TrajectoryChart
        seriesA={seriesA}
        seriesB={seriesB}
        selectedRound={selectedRound}
        onSelectRound={onSelectRound}
        appliesFromRound={paper.experiment.applies_from_round}
        metric={metric}
        totalRounds={seriesA.length || 4}
      />
      <div className="round-pills" role="list">
        {rounds.map((round) => (
          <button
            key={round}
            type="button"
            role="listitem"
            className={selectedRound === round ? "round-pills__item is-active" : "round-pills__item"}
            onClick={() => onSelectRound(round)}
          >
            R{round}
          </button>
        ))}
      </div>
    </section>
  );
}
