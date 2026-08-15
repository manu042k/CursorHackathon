import type { ExperimentPaper, RosterAgent } from "@/types/contracts";

function band(agent: RosterAgent | undefined, agentId: string): string {
  const role = agent?.role ?? "";
  if (role.includes("price_sensitive") || agentId.startsWith("buyer_1") || agentId === "buyer_2" || agentId === "buyer_3") {
    return "price-sensitive";
  }
  if (role.includes("enterprise") || role.includes("loyal") || agentId === "buyer_4" || agentId === "buyer_5") {
    return "loyal";
  }
  if (agentId === "competitor" || role.includes("competitor")) return "competitor";
  return role || agentId;
}

export function AttributionBar({
  paper,
  selectedRound,
}: {
  paper: ExperimentPaper;
  selectedRound: number;
}) {
  const row = paper.divergence_by_round.find((item) => item.round === selectedRound);
  const contributors = row?.top_contributors ?? [];
  const top = contributors[0];
  const byId = new Map(paper.roster.agents.map((agent) => [agent.agent_id, agent]));

  return (
    <section className="attribution">
      {top ? (
        <p className="attribution__caption">
          {Math.round(top.contribution_pct)}% of this round's new gap is {band(byId.get(top.agent_id), top.agent_id)}
          {" "}({top.agent_id}).
        </p>
      ) : (
        <p className="attribution__caption">No decision-diff in round {selectedRound}.</p>
      )}
      <div className="attribution__bar" aria-label={`Round ${selectedRound} contribution`}>
        {contributors.length === 0 ? (
          <div className="attribution__empty">empty</div>
        ) : (
          contributors.map((item) => (
            <div
              key={item.agent_id}
              className={`attribution__seg attribution__seg--${band(byId.get(item.agent_id), item.agent_id)}`}
              style={{ width: `${item.contribution_pct}%` }}
              title={`${item.agent_id} ${item.contribution_pct}%`}
            />
          ))
        )}
      </div>
      {contributors.length > 0 ? (
        <ul className="attribution__legend">
          {contributors.map((item) => (
            <li key={item.agent_id}>
              <span className={`attribution__swatch attribution__seg--${band(byId.get(item.agent_id), item.agent_id)}`} />
              {band(byId.get(item.agent_id), item.agent_id)} · {Math.round(item.contribution_pct)}%
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
