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

export function RosterConfirm({
  roster,
  onConfirm,
  pending,
}: {
  roster: Roster;
  onConfirm: () => void;
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
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <ButtonPrimary type="button" className="mt-6" disabled={pending} onClick={onConfirm}>
        Confirm and run analysis
      </ButtonPrimary>
    </section>
  );
}
