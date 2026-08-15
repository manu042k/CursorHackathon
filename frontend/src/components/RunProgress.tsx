import Link from "next/link";
import { OrchestrationGraph } from "@/components/OrchestrationGraph";
import { TrajectoryChart } from "@/components/TrajectoryChart";
import { RUN_ROUNDS } from "@/types/contracts";
import type { DecisionEvent, RoundCompleteEvent } from "@/types/contracts";

export function RunProgress({
  ticks,
  decisions,
  failed,
  basePrice,
  forkedPrice,
  appliesFromRound,
  experimentId,
  rounds = RUN_ROUNDS,
}: {
  ticks: RoundCompleteEvent[];
  decisions: DecisionEvent[];
  failed: string | null;
  basePrice: number;
  forkedPrice: number;
  appliesFromRound: number;
  experimentId: string;
  rounds?: number;
}) {
  const latest = ticks[ticks.length - 1];
  const latestDecision = decisions[decisions.length - 1];
  const a = ticks.filter((tick) => tick.run_id === "A").map((tick) => tick.round);
  const b = ticks.filter((tick) => tick.run_id === "B").map((tick) => tick.round);
  const shareA = ticks.filter((tick) => tick.run_id === "A").map((tick) => tick.share);
  const shareB = ticks.filter((tick) => tick.run_id === "B").map((tick) => tick.share);
  const selectedRound = latestDecision?.round ?? latest?.round ?? 1;
  const live = [...decisions].reverse().slice(0, 8);

  return (
    <section className="run-progress">
      <p className="setup__kicker">The fork is running</p>
      <h1 className="setup__sentence">
        Running · ${basePrice} vs ${forkedPrice}
      </h1>
      {latest ? (
        <p className="run-progress__now">
          Run {latest.run_id} · round {latest.round} / {rounds}
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

      <section className="agent-console-card run-progress__live" aria-live="polite">
        <header className="agent-console-card__head">
          <p>Live orchestration · nodes light as agents decide</p>
        </header>
        <OrchestrationGraph
          round={selectedRound}
          decisions={decisions}
          ticks={ticks}
          basePrice={basePrice}
          forkedPrice={forkedPrice}
          live
        />
      </section>

      <TrajectoryChart
        seriesA={shareA}
        seriesB={shareB}
        selectedRound={selectedRound}
        appliesFromRound={appliesFromRound}
        metric="share"
        totalRounds={rounds}
      />

      <div className="run-progress__cols">
        <div>
          <h2>Run A · baseline ${basePrice}</h2>
          <ol>
            {Array.from({ length: rounds }, (_, i) => i + 1).map((round) => (
              <li key={`a-${round}`} className={a.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h2>Run B · ${forkedPrice}</h2>
          <ol>
            {Array.from({ length: rounds }, (_, i) => i + 1).map((round) => (
              <li key={`b-${round}`} className={b.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
      </div>

      <section className="run-progress__feed" aria-label="Decision log">
        <p className="method-strip__label">Recent decisions</p>
        {live.length === 0 ? (
          <p className="setup__group-hint">Agents have not spoken yet.</p>
        ) : (
          <ul className="live-reasons live-reasons--light">
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

      {a.includes(rounds) && b.includes(rounds) ? (
        <p className="finding__next">
          <Link href={`/experiments/${experimentId}`} className="button-primary">
            See why it moved
          </Link>
        </p>
      ) : null}
      {failed ? (
        <p className="setup__error" role="alert">
          {failed}{" "}
          <Link href="/new" className="button-secondary">
            New experiment
          </Link>
        </p>
      ) : null}
    </section>
  );
}
