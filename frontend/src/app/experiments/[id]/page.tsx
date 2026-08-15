import { FindingPaper } from "@/components/FindingPaper";
import paper from "@/data/acme-seed-42.json";
import type { ExperimentPaper } from "@/types/contracts";
import "../paper.css";

export default function ExperimentPaperPage({ params }: { params: { id: string } }) {
  if (params.id !== "acme-seed-42") {
    return (
      <main className="shell-main">
        <p className="shell-kicker">Finding</p>
        <h1 className="shell-headline">{params.id}</h1>
      </main>
    );
  }
  return <FindingPaper paper={paper as unknown as ExperimentPaper} />;
}
