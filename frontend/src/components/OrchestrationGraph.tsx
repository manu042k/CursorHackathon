"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DEFAULT_AGENT_ORDER,
  DEFAULT_WTP,
  NODE_LAYOUT,
  PIPELINE_EDGES,
  agentLabel,
  shortDecision,
} from "@/lib/orchestration";
import type { AgentLog, DecisionEvent, RosterAgent, RoundCompleteEvent, RunId } from "@/types/contracts";

type Pick = { decision: string; reason: string; run_id: RunId };

const VIEW = { w: 720, h: 400 };

function atRound<T extends { round: number; agent_id: string }>(
  rows: T[] | undefined,
  round: number,
  agentId: string
): T | undefined {
  if (!rows) return undefined;
  for (let i = rows.length - 1; i >= 0; i -= 1) {
    if (rows[i].round === round && rows[i].agent_id === agentId) return rows[i];
  }
  return undefined;
}

function shareAt(ticks: RoundCompleteEvent[] | undefined, run: RunId, round: number): number | null {
  const hit = ticks?.find((tick) => tick.run_id === run && tick.round === round);
  return hit ? hit.share : null;
}

function wtpOf(agent: RosterAgent | undefined, agentId: string): string | null {
  const value = agent?.traits?.willingness_to_pay ?? DEFAULT_WTP[agentId];
  if (typeof value === "number") return `WTP $${Math.round(value)}`;
  return null;
}

export function OrchestrationGraph({
  round,
  logsA,
  logsB,
  decisions,
  ticks,
  basePrice,
  forkedPrice,
  roster,
  live = false,
  onSelectAgent,
}: {
  round: number;
  logsA?: AgentLog[];
  logsB?: AgentLog[];
  decisions?: DecisionEvent[];
  ticks?: RoundCompleteEvent[];
  basePrice: number;
  forkedPrice: number;
  roster?: RosterAgent[];
  live?: boolean;
  onSelectAgent?: (agentId: string) => void;
}) {
  const byId = useMemo(
    () => new Map((roster ?? []).map((agent) => [agent.agent_id, agent])),
    [roster]
  );
  const extra = useMemo(() => {
    const seen = new Set<string>(DEFAULT_AGENT_ORDER);
    const ids: string[] = [];
    for (const row of [...(logsA ?? []), ...(logsB ?? []), ...(decisions ?? [])]) {
      if (!seen.has(row.agent_id)) {
        seen.add(row.agent_id);
        ids.push(row.agent_id);
      }
    }
    return ids;
  }, [logsA, logsB, decisions]);
  const agents = useMemo(() => [...DEFAULT_AGENT_ORDER, ...extra], [extra]);

  const latest = decisions?.[decisions.length - 1];
  const [pinned, setPinned] = useState<string | null>(null);
  useEffect(() => {
    if (live && latest?.agent_id) setPinned(latest.agent_id);
  }, [live, latest?.agent_id, latest?.round, latest?.run_id]);

  function pick(run: RunId, agentId: string): Pick | null {
    const fromLogs = run === "A" ? atRound(logsA, round, agentId) : atRound(logsB, round, agentId);
    if (fromLogs) {
      return { decision: fromLogs.decision, reason: fromLogs.reason, run_id: run };
    }
    const fromLive = atRound(
      decisions?.filter((row) => row.run_id === run),
      round,
      agentId
    );
    if (fromLive) {
      return { decision: fromLive.decision, reason: fromLive.reason, run_id: run };
    }
    return null;
  }

  const selected = pinned && agents.includes(pinned) ? pinned : latest?.agent_id ?? null;
  const selectedA = selected ? pick("A", selected) : null;
  const selectedB = selected ? pick("B", selected) : null;
  const shareA = shareAt(ticks, "A", round);
  const shareB = shareAt(ticks, "B", round);

  function onNode(agentId: string) {
    setPinned(agentId);
    onSelectAgent?.(agentId);
  }

  return (
    <div className="orch">
      <p className="orch__caption">
        Orchestration · round {round}
        {live && latest ? ` · Run ${latest.run_id} · ${latest.agent_id}` : null}
      </p>
      <div className="orch__stage" aria-label="Agent orchestration graph">
        <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="orch__svg" aria-hidden="true">
          {PIPELINE_EDGES.map(([from, to]) => {
            const a = NODE_LAYOUT[from];
            const b = NODE_LAYOUT[to];
            if (!a || !b) return null;
            const x1 = (a.x / 100) * VIEW.w;
            const y1 = (a.y / 100) * VIEW.h;
            const x2 = (b.x / 100) * VIEW.w;
            const y2 = (b.y / 100) * VIEW.h;
            const liveEdge =
              live &&
              latest &&
              ((from === "price" && latest.agent_id === to) || latest.agent_id === from);
            return (
              <line
                key={`${from}-${to}`}
                className={liveEdge ? "orch__edge is-live" : "orch__edge"}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
              />
            );
          })}
        </svg>
        <div
          className="orch-node orch-node--market"
          style={{ left: `${NODE_LAYOUT.price.x}%`, top: `${NODE_LAYOUT.price.y}%` }}
        >
          <span>price</span>
          <em>
            A ${Math.round(basePrice)} · B ${Math.round(forkedPrice)}
          </em>
        </div>
        {agents.map((agentId, index) => {
          const layout = NODE_LAYOUT[agentId] ?? {
            x: 10 + (index % 5) * 20,
            y: 58,
          };
          const a = pick("A", agentId);
          const b = pick("B", agentId);
          const split = Boolean(a && b && a.decision !== b.decision);
          const speaking = live && latest?.agent_id === agentId && latest.round === round;
          const className = [
            "orch-node",
            split ? "is-split" : "",
            speaking ? "is-live" : "",
            selected === agentId ? "is-selected" : "",
            a || b ? "is-done" : "",
          ]
            .filter(Boolean)
            .join(" ");
          return (
            <button
              key={agentId}
              type="button"
              className={className}
              style={{ left: `${layout.x}%`, top: `${layout.y}%` }}
              onClick={() => onNode(agentId)}
            >
              <span>
                {agentLabel(agentId)}
                {wtpOf(byId.get(agentId), agentId) ? <i>{wtpOf(byId.get(agentId), agentId)}</i> : null}
              </span>
              <em>
                <b className={`decision-chip decision-chip--${a?.decision ?? "none"}`}>
                  A {shortDecision(a?.decision)}
                </b>
                <b className={`decision-chip decision-chip--${b?.decision ?? "none"}`}>
                  B {shortDecision(b?.decision)}
                </b>
              </em>
            </button>
          );
        })}
        <div
          className="orch-node orch-node--market"
          style={{ left: `${NODE_LAYOUT.outcome.x}%`, top: `${NODE_LAYOUT.outcome.y}%` }}
        >
          <span>share</span>
          <em>
            A {shareA == null ? "—" : `${Math.round(shareA)}%`} · B{" "}
            {shareB == null ? "—" : `${Math.round(shareB)}%`}
          </em>
        </div>
      </div>
      {selected ? (
        <div className="orch__why">
          <p>
            {agentLabel(selected)}
            {wtpOf(byId.get(selected), selected) ? ` · ${wtpOf(byId.get(selected), selected)}` : ""}
          </p>
          <p>
            <span className={`decision-chip decision-chip--${selectedA?.decision ?? "none"}`}>
              A {shortDecision(selectedA?.decision)}
            </span>
            {selectedA?.reason ?? (live ? "Waiting for Run A." : "No decision this round.")}
          </p>
          <p>
            <span className={`decision-chip decision-chip--${selectedB?.decision ?? "none"}`}>
              B {shortDecision(selectedB?.decision)}
            </span>
            {selectedB?.reason ?? (live ? "Waiting for Run B." : "No decision this round.")}
          </p>
        </div>
      ) : (
        <p className="orch__why">{live ? "Agents have not spoken yet." : "Select a node to read the reason."}</p>
      )}
    </div>
  );
}
