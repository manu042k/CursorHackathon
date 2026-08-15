import type { AgentLog, ExperimentPaper } from "@/types/contracts";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function decisionAt(logs: AgentLog[], round: number): string {
  const row = logs.find((log) => log.agent_id === "competitor" && log.round === round);
  return row?.decision ?? "—";
}

export function CompetitorPath({ paper }: { paper: ExperimentPaper }) {
  const rounds = Array.from({ length: paper.experiment.rounds }, (_, i) => i + 1);
  return (
    <section className="roster-preview paper-figure" aria-label="Competitor path">
      <h2>Competitor reaction</h2>
      <Table className="research-table">
        <TableHeader>
          <TableRow>
            <TableHead>Round</TableHead>
            <TableHead>Run A</TableHead>
            <TableHead>Run B</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rounds.map((round) => (
            <TableRow key={round}>
              <TableCell>R{round}</TableCell>
              <TableCell>{decisionAt(paper.logs.run_a, round)}</TableCell>
              <TableCell>{decisionAt(paper.logs.run_b, round)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </section>
  );
}
