import type { Roster } from "@/types/contracts";
import { ButtonPrimary } from "@/components/ButtonPrimary";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function playbookLine(agent: Roster["agents"][number]): string {
  const fromTraits = agent.traits.playbook ?? agent.traits.one_liner;
  if (typeof fromTraits === "string" && fromTraits.trim()) return fromTraits;
  if (agent.agent_class === "competitor") return "Matches if the fork steals share; otherwise holds.";
  if (agent.agent_class === "analyst") return "Notes only. Does not move the market.";
  return agent.archetype?.replace(/_/g, " ") ?? agent.role.replace(/_/g, " ");
}

export function RosterConfirm({
  roster,
  onConfirm,
  onEdit,
  pending,
}: {
  roster: Roster;
  onConfirm: () => void;
  onEdit: () => void;
  pending: boolean;
}) {
  return (
    <section className="roster-preview mx-auto max-w-5xl px-6 py-10" aria-label="Confirm roster">
      <h1 className="text-3xl font-semibold tracking-tight">Confirm the market</h1>
      <p className="mt-2 mb-6 text-muted-foreground">
        Five users, one competitor, one analyst. Same roster on Run A and Run B.
      </p>
      <Table className="research-table">
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Class</TableHead>
            <TableHead>Archetype</TableHead>
            <TableHead>WTP / price</TableHead>
            <TableHead>Playbook</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {roster.agents.map((agent) => (
            <TableRow key={agent.agent_id}>
              <TableCell>{agent.agent_id}</TableCell>
              <TableCell>{agent.agent_class ?? agent.role}</TableCell>
              <TableCell>{agent.archetype ?? "—"}</TableCell>
              <TableCell>
                {String(agent.traits.willingness_to_pay ?? agent.traits.current_price ?? "")}
              </TableCell>
              <TableCell className="max-w-xs text-muted-foreground">{playbookLine(agent)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="mt-6 flex flex-wrap items-center gap-4">
        <ButtonPrimary type="button" disabled={pending} onClick={onConfirm}>
          Confirm and run analysis
        </ButtonPrimary>
        <button type="button" className="app-nav__action" onClick={onEdit} disabled={pending}>
          Edit product
        </button>
      </div>
    </section>
  );
}
