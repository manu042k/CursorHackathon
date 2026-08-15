"use client";

import { useMemo, useState } from "react";
import type { AgentLog, ExperimentPaper } from "@/types/contracts";

function byAgent(logs: AgentLog[], round: number): Map<string, AgentLog> {
  return new Map(logs.filter((log) => log.round === round).map((log) => [log.agent_id, log]));
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
  const ids = useMemo(() => {
    const all = Array.from(new Set([...a.keys(), ...b.keys()]));
    if (everyone) return all;
    return all.filter((id) => (a.get(id)?.decision ?? "") !== (b.get(id)?.decision ?? ""));
  }, [a, b, everyone]);

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
        <button type="button" className="button-secondary button-secondary--on-dark" onClick={() => setEveryone((v) => !v)}>
          {everyone ? "Show differences" : "Show everyone"}
        </button>
      </header>
      <ul className="agent-console-card__citations">
        {paper.summary_narrative.citations.map((citation) => (
          <li key={`${citation.agent_id}-${citation.round}-${citation.run_id}`}>
            <button
              type="button"
              className="button-secondary button-secondary--on-dark"
              onClick={() => scrollTo(citation.agent_id, citation.round)}
            >
              {citation.agent_id} · R{citation.round} · {citation.run_id}
            </button>
          </li>
        ))}
      </ul>
      <div className="agent-console-card__rows">
        {ids.map((agentId) => {
          const logA = a.get(agentId);
          const logB = b.get(agentId);
          return (
            <article key={agentId} id={`trace-${agentId}`} className="agent-console-card__agent">
              <h3>{agentId}</h3>
              <p className="agent-console-card__run">
                <span>A {logA?.decision ?? "—"}</span>
                {logA?.reason}
              </p>
              <p className="agent-console-card__run">
                <span>B {logB?.decision ?? "—"}</span>
                {logB?.reason}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
