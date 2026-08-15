"use client";

import { useMemo, useState } from "react";
import { OrchestrationGraph } from "@/components/OrchestrationGraph";
import { Button } from "@/components/ui/button";
import { forkedPrice } from "@/lib/price";
import { runLabel } from "@/lib/runs";
import type { AgentLog, ExperimentPaper, RosterAgent, RoundCompleteEvent } from "@/types/contracts";

function byAgent(logs: AgentLog[], round: number): Map<string, AgentLog> {
  return new Map(logs.filter((log) => log.round === round).map((log) => [log.agent_id, log]));
}

function wtpOf(agent: RosterAgent | undefined): string | null {
  const value = agent?.traits?.willingness_to_pay;
  if (typeof value === "number") return `WTP $${Math.round(value)}`;
  return null;
}

export function ReasonTrace({
  paper,
  selectedRound,
  onSelectRound,
}: {
  paper: ExperimentPaper;
  selectedRound: number;
  onSelectRound: (round: number) => void;
}) {
  const [everyone, setEveryone] = useState(false);
  const a = byAgent(paper.logs.run_a, selectedRound);
  const b = byAgent(paper.logs.run_b, selectedRound);
  const byId = useMemo(
    () => new Map(paper.roster.agents.map((agent) => [agent.agent_id, agent])),
    [paper.roster.agents]
  );
  const ids = useMemo(() => {
    const all = Array.from(new Set([...a.keys(), ...b.keys()]));
    if (everyone) return all;
    return all.filter((id) => (a.get(id)?.decision ?? "") !== (b.get(id)?.decision ?? ""));
  }, [a, b, everyone]);
  const splits = ids.filter((id) => (a.get(id)?.decision ?? "") !== (b.get(id)?.decision ?? ""));
  const ticks: RoundCompleteEvent[] = [
    ...paper.metrics.share_a.map((share, index) => ({
      run_id: "A" as const,
      round: index + 1,
      share,
      mrr: paper.metrics.mrr_a[index] ?? 0,
    })),
    ...paper.metrics.share_b.map((share, index) => ({
      run_id: "B" as const,
      round: index + 1,
      share,
      mrr: paper.metrics.mrr_b[index] ?? 0,
    })),
  ];

  function scrollTo(agentId: string, round: number) {
    onSelectRound(round);
    requestAnimationFrame(() => {
      document.getElementById(`trace-${agentId}`)?.scrollIntoView({ block: "nearest" });
    });
  }

  return (
    <section className="agent-console-card">
      <header className="agent-console-card__head">
        <p>
          Round {selectedRound} · {everyone ? "everyone" : "only decisions that differed"}
        </p>
        <Button
          type="button"
          variant="link"
          className="button-secondary button-secondary--on-dark h-auto p-0 text-primary-foreground"
          onClick={() => setEveryone((v) => !v)}
        >
          {everyone ? "Show differences" : "Show everyone"}
        </Button>
      </header>
      <OrchestrationGraph
        round={selectedRound}
        logsA={paper.logs.run_a}
        logsB={paper.logs.run_b}
        ticks={ticks}
        basePrice={paper.experiment.current_price}
        forkedPrice={forkedPrice(paper.experiment.current_price, paper.experiment.variable_delta)}
        roster={paper.roster.agents}
        onSelectAgent={(agentId) => {
          setEveryone(true);
          scrollTo(agentId, selectedRound);
        }}
      />
      {splits.length > 0 ? (
        <p className="agent-console-card__why">
          {splits.length === 1 ? "This is what caused the fork." : "These agents caused the fork."} Same
          person, two prices, two decisions.
        </p>
      ) : (
        <p className="agent-console-card__why">
          Current and Changed still agree this round. The worlds have not split yet.
        </p>
      )}
      <ul className="agent-console-card__citations">
        {paper.summary_narrative.citations.map((citation) => (
          <li key={`${citation.agent_id}-${citation.round}-${citation.run_id}`}>
            <button
              type="button"
              className="button-secondary button-secondary--on-dark"
              onClick={() => scrollTo(citation.agent_id, citation.round)}
            >
              {citation.agent_id} · R{citation.round} · {runLabel(citation.run_id)}
            </button>
          </li>
        ))}
      </ul>
      <div className="agent-console-card__rows">
        {ids.map((agentId) => {
          const logA = a.get(agentId);
          const logB = b.get(agentId);
          const differed = (logA?.decision ?? "") !== (logB?.decision ?? "");
          return (
            <article
              key={agentId}
              id={`trace-${agentId}`}
              className={differed ? "agent-console-card__agent is-split" : "agent-console-card__agent"}
            >
              <h3>
                {agentId}
                {wtpOf(byId.get(agentId)) ? <span>{wtpOf(byId.get(agentId))}</span> : null}
              </h3>
              <p className="agent-console-card__run">
                <span className={`decision-chip decision-chip--${logA?.decision ?? "none"}`}>
                  {runLabel("A")} {logA?.decision ?? "—"}
                </span>
                {logA?.reason}
              </p>
              <p className="agent-console-card__run">
                <span className={`decision-chip decision-chip--${logB?.decision ?? "none"}`}>
                  {runLabel("B")} {logB?.decision ?? "—"}
                </span>
                {logB?.reason}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
