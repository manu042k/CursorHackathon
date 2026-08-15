"use client";

import { useState, type KeyboardEvent } from "react";
import { forkedPrice } from "@/lib/price";
import type { ExperimentPaper } from "@/types/contracts";

type Metric = "share" | "mrr";

type Props = {
  paper: ExperimentPaper;
  selectedRound: number;
  onSelectRound: (round: number) => void;
};

const WIDTH = 640;
const HEIGHT = 220;
const PAD = { top: 16, right: 12, bottom: 28, left: 44 };

export function TwinChart({ paper, selectedRound, onSelectRound }: Props) {
  const [metric, setMetric] = useState<Metric>("share");
  const seriesA = metric === "share" ? paper.metrics.share_a : paper.metrics.mrr_a;
  const seriesB = metric === "share" ? paper.metrics.share_b : paper.metrics.mrr_b;
  const base = paper.experiment.current_price;
  const forked = forkedPrice(base, paper.experiment.variable_delta);
  const rounds = seriesA.map((_, i) => i + 1);
  const min = Math.min(...seriesA, ...seriesB);
  const max = Math.max(...seriesA, ...seriesB);
  const span = max - min || 1;
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;
  const x = (round: number) => PAD.left + ((round - 1) / 7) * innerW;
  const y = (value: number) => PAD.top + innerH - ((value - min) / span) * innerH;
  const path = (series: number[]) =>
    series.map((value, i) => `${i === 0 ? "M" : "L"} ${x(i + 1)} ${y(value)}`).join(" ");
  const markerX = x(paper.experiment.applies_from_round);

  function onKey(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      onSelectRound(Math.max(1, selectedRound - 1));
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      onSelectRound(Math.min(8, selectedRound + 1));
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
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="twin-chart__svg" role="img">
        <line
          className="twin-chart__axis"
          x1={PAD.left}
          x2={PAD.left}
          y1={PAD.top}
          y2={HEIGHT - PAD.bottom}
        />
        <line
          className="twin-chart__axis"
          x1={PAD.left}
          x2={WIDTH - PAD.right}
          y1={HEIGHT - PAD.bottom}
          y2={HEIGHT - PAD.bottom}
        />
        <line
          className="twin-chart__marker"
          x1={markerX}
          x2={markerX}
          y1={PAD.top}
          y2={HEIGHT - PAD.bottom}
        />
        <path d={path(seriesA)} className="twin-chart__line twin-chart__line--a" />
        <path d={path(seriesB)} className="twin-chart__line twin-chart__line--b" />
        {rounds.map((round) => (
          <circle
            key={round}
            cx={x(round)}
            cy={y(seriesA[round - 1])}
            r={selectedRound === round ? 5 : 3}
            className="twin-chart__dot twin-chart__dot--a"
            onClick={() => onSelectRound(round)}
          />
        ))}
        {rounds.map((round) => (
          <circle
            key={`b-${round}`}
            cx={x(round)}
            cy={y(seriesB[round - 1])}
            r={selectedRound === round ? 5 : 3}
            className="twin-chart__dot twin-chart__dot--b"
            onClick={() => onSelectRound(round)}
          />
        ))}
      </svg>
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
