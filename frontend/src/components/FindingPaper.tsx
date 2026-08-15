import { Receipt } from "@/components/Receipt";
import { MetricCards, PaperHeader } from "@/components/PaperHeader";
import type { ExperimentPaper } from "@/types/contracts";

export function FindingPaper({ paper }: { paper: ExperimentPaper }) {
  return (
    <article className="finding">
      <PaperHeader paper={paper} />
      <p className="finding__narrative">{paper.summary_narrative.text}</p>
      <MetricCards paper={paper} />
      <Receipt receipt={paper.receipt} />
    </article>
  );
}
