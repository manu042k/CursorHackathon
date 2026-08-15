"use client";

import { useId, type KeyboardEvent } from "react";

export type ChartMetric = "share" | "mrr";

type Props = {
  seriesA: number[];
  seriesB: number[];
  selectedRound: number;
  onSelectRound?: (round: number) => void;
  appliesFromRound: number;
  metric: ChartMetric;
  totalRounds?: number;
};

const WIDTH = 720;
const HEIGHT = 280;
const PAD = { top: 28, right: 20, bottom: 36, left: 52 };

function range(seriesA: number[], seriesB: number[]): { lo: number; hi: number } {
  const values = [...seriesA, ...seriesB];
  if (values.length === 0) return { lo: 0, hi: 1 };
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) return { lo: min - 1, hi: max + 1 };
  const pad = (max - min) * 0.14;
  return { lo: min - pad, hi: max + pad };
}

function ticks(lo: number, hi: number): number[] {
  const span = hi - lo || 1;
  return [0, 0.25, 0.5, 0.75, 1].map((t) => lo + span * t);
}

function fmt(metric: ChartMetric, value: number): string {
  if (metric === "share") return `${Math.round(value)}%`;
  return `$${Math.round(value).toLocaleString()}`;
}

export function TrajectoryChart({
  seriesA,
  seriesB,
  selectedRound,
  onSelectRound,
  appliesFromRound,
  metric,
  totalRounds = 4,
}: Props) {
  const uid = useId().replace(/:/g, "");
  const fillA = `fill-a-${uid}`;
  const fillB = `fill-b-${uid}`;
  const { lo, hi } = range(seriesA, seriesB);
  const span = hi - lo || 1;
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;
  const x = (round: number) => PAD.left + ((round - 1) / Math.max(1, totalRounds - 1)) * innerW;
  const y = (value: number) => PAD.top + innerH - ((value - lo) / span) * innerH;
  const baseY = HEIGHT - PAD.bottom;
  const rounds = Array.from({ length: totalRounds }, (_, i) => i + 1);

  const line = (series: number[]) =>
    series.map((value, i) => `${i === 0 ? "M" : "L"} ${x(i + 1)} ${y(value)}`).join(" ");

  const area = (series: number[]) => {
    if (series.length === 0) return "";
    const drawn = line(series);
    return `${drawn} L ${x(series.length)} ${baseY} L ${x(1)} ${baseY} Z`;
  };

  const markerX = x(appliesFromRound);
  const selectedX = x(selectedRound);
  const yTicks = ticks(lo, hi);
  const aVal = seriesA[selectedRound - 1];
  const bVal = seriesB[selectedRound - 1];
  const gap = aVal != null && bVal != null ? bVal - aVal : null;

  function onKey(event: KeyboardEvent<HTMLDivElement>) {
    if (!onSelectRound) return;
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
    <div className="twin-chart__frame" tabIndex={0} onKeyDown={onKey} aria-label="Twin trajectory">
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="twin-chart__svg" role="img">
        <defs>
          <linearGradient id={fillA} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#212121" stopOpacity="0.16" />
            <stop offset="100%" stopColor="#212121" stopOpacity="0" />
          </linearGradient>
          <linearGradient id={fillB} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1863dc" stopOpacity="0.22" />
            <stop offset="100%" stopColor="#1863dc" stopOpacity="0" />
          </linearGradient>
        </defs>
        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              className="twin-chart__grid"
              x1={PAD.left}
              x2={WIDTH - PAD.right}
              y1={y(tick)}
              y2={y(tick)}
            />
            <text className="twin-chart__ylabel" x={PAD.left - 8} y={y(tick) + 4} textAnchor="end">
              {fmt(metric, tick)}
            </text>
          </g>
        ))}
        <line className="twin-chart__axis" x1={PAD.left} x2={PAD.left} y1={PAD.top} y2={baseY} />
        <line
          className="twin-chart__axis"
          x1={PAD.left}
          x2={WIDTH - PAD.right}
          y1={baseY}
          y2={baseY}
        />
        <rect
          className="twin-chart__selection"
          x={selectedX - 10}
          y={PAD.top}
          width={20}
          height={innerH}
        />
        <line className="twin-chart__marker" x1={markerX} x2={markerX} y1={PAD.top} y2={baseY} />
        <text className="twin-chart__fork-label" x={markerX + 6} y={PAD.top + 12}>
          fork
        </text>
        {seriesA.length > 1 ? <path d={area(seriesA)} fill={`url(#${fillA})`} /> : null}
        {seriesB.length > 1 ? <path d={area(seriesB)} fill={`url(#${fillB})`} /> : null}
        {seriesA.length > 0 ? <path d={line(seriesA)} className="twin-chart__line twin-chart__line--a" /> : null}
        {seriesB.length > 0 ? <path d={line(seriesB)} className="twin-chart__line twin-chart__line--b" /> : null}
        {seriesA.map((value, i) => (
          <circle
            key={`a-${i}`}
            cx={x(i + 1)}
            cy={y(value)}
            r={selectedRound === i + 1 ? 6 : 4}
            className="twin-chart__dot twin-chart__dot--a"
            onClick={() => onSelectRound?.(i + 1)}
          />
        ))}
        {seriesB.map((value, i) => (
          <circle
            key={`b-${i}`}
            cx={x(i + 1)}
            cy={y(value)}
            r={selectedRound === i + 1 ? 6 : 4}
            className="twin-chart__dot twin-chart__dot--b"
            onClick={() => onSelectRound?.(i + 1)}
          />
        ))}
        {rounds.map((round) => (
          <text key={`x-${round}`} className="twin-chart__xlabel" x={x(round)} y={HEIGHT - 10} textAnchor="middle">
            R{round}
          </text>
        ))}
      </svg>
      <p className="twin-chart__readout">
        {aVal == null || bVal == null || gap == null ? (
          "Waiting for the first round…"
        ) : (
          <>
            R{selectedRound} · A {fmt(metric, aVal)} · B {fmt(metric, bVal)} · gap{" "}
            <strong>
              {gap > 0 ? "+" : ""}
              {metric === "share" ? `${Math.round(gap)}pp` : `$${Math.round(gap).toLocaleString()}`}
            </strong>
          </>
        )}
      </p>
    </div>
  );
}
