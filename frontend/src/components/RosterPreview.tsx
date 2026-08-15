import type { ExperimentPaper } from "@/types/contracts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export function RosterPreview({ paper }: { paper: ExperimentPaper }) {
  return (
    <section className="roster-preview" aria-label="Roster">
      <h2>Who is in the market</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Role</TableHead>
            <TableHead>Count</TableHead>
            <TableHead>Willingness to pay</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {paper.roster.agent_roles.map((role) => {
            const wtp = role.traits.willingness_to_pay_range;
            const range = Array.isArray(wtp) ? `WTP $${wtp[0]}–$${wtp[1]}` : "—";
            return (
              <TableRow key={role.role}>
                <TableCell>{role.role.replace(/_/g, " ")}</TableCell>
                <TableCell className="font-mono text-xs tracking-wide text-muted-foreground">
                  count {role.count}
                </TableCell>
                <TableCell className="font-mono text-xs tracking-wide text-muted-foreground">
                  {range}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </section>
  );
}
