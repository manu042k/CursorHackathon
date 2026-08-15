import type { ExperimentPaper } from "@/types/contracts";

export function RosterPreview({ paper }: { paper: ExperimentPaper }) {
  return (
    <section className="roster-preview" aria-label="Roster">
      <h2>Who is in the market</h2>
      <ul>
        {paper.roster.agent_roles.map((role) => {
          const wtp = role.traits.willingness_to_pay_range;
          const range = Array.isArray(wtp) ? `WTP $${wtp[0]}–$${wtp[1]}` : "";
          return (
            <li key={role.role}>
              <span>{role.role.replace(/_/g, " ")}</span>
              <span>count {role.count}</span>
              <span>{range || "—"}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
