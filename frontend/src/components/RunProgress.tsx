import Link from "next/link";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import type { DecisionEvent, RoundCompleteEvent } from "@/types/contracts";

export function RunProgress({
  ticks,
  decisions,
  failed,
  basePrice,
  forkedPrice,
  appliesFromRound,
  experimentId,
}: {
  ticks: RoundCompleteEvent[];
  decisions: DecisionEvent[];
  failed: string | null;
  basePrice: number;
  forkedPrice: number;
  appliesFromRound: number;
  experimentId: string;
}) {
  const latest = ticks[ticks.length - 1];
  const latestDecision = decisions[decisions.length - 1];
  const a = ticks.filter((tick) => tick.run_id === "A").map((tick) => tick.round);
  const b = ticks.filter((tick) => tick.run_id === "B").map((tick) => tick.round);
  const shareA = ticks.filter((tick) => tick.run_id === "A").map((tick) => tick.share);
  const shareB = ticks.filter((tick) => tick.run_id === "B").map((tick) => tick.share);
  const selectedRound = latest?.round ?? 1;
  const live = [...decisions].reverse().slice(0, 12);

  return (
    <section className="run-progress">
      <p className="setup__kicker">The fork is running</p>
      <h1 className="setup__sentence">
        Running · ${basePrice} vs ${forkedPrice}
      </h1>
      {latest ? (
        <p className="run-progress__now">
          Run {latest.run_id} · round {latest.round} / 8
          <span>
            share {latest.share.toFixed(0)}% · MRR ${latest.mrr.toFixed(0)}
          </span>
        </p>
      ) : latestDecision ? (
        <p className="run-progress__now">
          Run {latestDecision.run_id} · {latestDecision.agent_id} is deciding round {latestDecision.round}
        </p>
      ) : (
        <p className="run-progress__now">Waiting for the first round…</p>
      )}

      <TrajectoryChart
        seriesA={shareA}
        seriesB={shareB}
        selectedRound={selectedRound}
        appliesFromRound={appliesFromRound}
        metric="share"
      />

      <div className="run-progress__cols">
        <div>
          <h2>Run A · baseline ${basePrice}</h2>
          <ol>
            {Array.from({ length: 8 }, (_, i) => i + 1).map((round) => (
              <li key={`a-${round}`} className={a.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h2>Run B · ${forkedPrice}</h2>
          <ol>
            {Array.from({ length: 8 }, (_, i) => i + 1).map((round) => (
              <li key={`b-${round}`} className={b.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
      </div>

      <section className="agent-console-card run-progress__live" aria-live="polite">
        <header className="agent-console-card__head">
          <p>Live reasons · why each agent moved</p>
        </header>
        {live.length === 0 ? (
          <p className="agent-console-card__why">Agents have not spoken yet.</p>
        ) : (
          <ul className="live-reasons">
            {live.map((item, index) => (
              <li key={`${item.run_id}-${item.agent_id}-${item.round}-${index}`}>
                <p className="live-reasons__meta">
                  <span>Run {item.run_id}</span>
                  <span>R{item.round}</span>
                  <span>{item.agent_id}</span>
                  <em className={`decision-chip decision-chip--${item.decision}`}>{item.decision}</em>
                  <span>${Math.round(item.current_price)}</span>
                </p>
                <p className="live-reasons__text">{item.reason}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {a.includes(8) && b.includes(8) ? (
        <p className="finding__next">
          <Link href={`/experiments/${experimentId}`} className="button-primary">
            See why it moved
          </Link>
        </p>
      ) : null}
      {failed ? (
        <p className="setup__error" role="alert">
          {failed}{" "}
          <Link href="/" className="button-secondary">
            New experiment
          </Link>
        </p>
      ) : null}
    </section>
  );
}
