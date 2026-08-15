import type { AgentLog, ExperimentPaper, RosterAgent } from "@/types/contracts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function lastDecision(logs: AgentLog[], agentId: string): string {
  const rows = logs.filter((log) => log.agent_id === agentId);
  if (rows.length === 0) return "—";
  return rows[rows.length - 1].decision;
}

function buyers(paper: ExperimentPaper): RosterAgent[] {
  return paper.roster.agents.filter(
    (agent) => agent.agent_class === "buyer" || agent.agent_id.startsWith("buyer_")
  );
}

export function PersonaOutcomes({ paper }: { paper: ExperimentPaper }) {
  return (
    <section className="roster-preview paper-figure" aria-label="Persona outcomes">
      <h2>Who stayed, churned, or switched</h2>
      <Table className="research-table">
        <TableHeader>
          <TableRow>
            <TableHead>Buyer</TableHead>
            <TableHead>Run A</TableHead>
            <TableHead>Run B</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {buyers(paper).map((agent) => (
            <TableRow key={agent.agent_id}>
              <TableCell>{agent.agent_id}</TableCell>
              <TableCell>{lastDecision(paper.logs.run_a, agent.agent_id)}</TableCell>
              <TableCell>{lastDecision(paper.logs.run_b, agent.agent_id)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  );
}
