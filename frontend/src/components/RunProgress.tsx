import type { RoundCompleteEvent } from "@/types/contracts";

export function RunProgress({
  ticks,
  failed,
}: {
  ticks: RoundCompleteEvent[];
  failed: string | null;
}) {
  const latest = ticks[ticks.length - 1];
  const a = ticks.filter((tick) => tick.run_id === "A").map((tick) => tick.round);
  const b = ticks.filter((tick) => tick.run_id === "B").map((tick) => tick.round);
  return (
    <section className="run-progress">
      <h1 className="setup__sentence">Running · $49 vs $59</h1>
      {latest ? (
        <p className="run-progress__now">
          Run {latest.run_id} · round {latest.round} / 8
          <span>
            share {latest.share.toFixed(0)}% · MRR ${latest.mrr.toFixed(0)}
          </span>
        </p>
      ) : (
        <p className="run-progress__now">Waiting for the first round…</p>
      )}
      <div className="run-progress__cols">
        <div>
          <h2>Run A · baseline $49</h2>
          <ol>
            {Array.from({ length: 8 }, (_, i) => i + 1).map((round) => (
              <li key={`a-${round}`} className={a.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h2>Run B · +20% → $59</h2>
          <ol>
            {Array.from({ length: 8 }, (_, i) => i + 1).map((round) => (
              <li key={`b-${round}`} className={b.includes(round) ? "is-filled" : ""}>
                R{round}
              </li>
            ))}
          </ol>
        </div>
      </div>
      {failed ? (
        <p className="setup__error" role="alert">
          {failed}
        </p>
      ) : null}
    </section>
  );
}
