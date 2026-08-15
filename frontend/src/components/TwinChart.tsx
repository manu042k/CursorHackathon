"use client";

import { type KeyboardEvent } from "react";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { forkedPrice } from "@/lib/price";
import type { ExperimentPaper } from "@/types/contracts";

type Props = {
  paper: ExperimentPaper;
  selectedRound: number;
  onSelectRound: (round: number) => void;
};

export function TwinChart({ paper, selectedRound, onSelectRound }: Props) {
  const base = paper.experiment.current_price;
  const forked = forkedPrice(base, paper.experiment.variable_delta);
  const totalRounds = paper.experiment.rounds;
  const rounds = paper.metrics.share_a.map((_, i) => i + 1);

  function onKey(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      onSelectRound(Math.max(1, selectedRound - 1));
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      onSelectRound(Math.min(totalRounds, selectedRound + 1));
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
      </div>
      <div className="twin-chart__figures">
        <TrajectoryChart
          metric="share"
          seriesA={paper.metrics.share_a}
          seriesB={paper.metrics.share_b}
          selectedRound={selectedRound}
          onSelectRound={onSelectRound}
          appliesFromRound={paper.experiment.applies_from_round}
          totalRounds={totalRounds}
        />
        <TrajectoryChart
          metric="mrr"
          seriesA={paper.metrics.mrr_a}
          seriesB={paper.metrics.mrr_b}
          selectedRound={selectedRound}
          onSelectRound={onSelectRound}
          appliesFromRound={paper.experiment.applies_from_round}
          totalRounds={totalRounds}
        />
      </div>
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
