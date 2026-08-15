import { Receipt } from "@/components/Receipt";
import type { Receipt as ReceiptModel } from "@/types/contracts";
import paper from "@/data/acme-seed-42.json";

export default function ExperimentPaperPage({ params }: { params: { id: string } }) {
  const receipt =
    params.id === "acme-seed-42" ? (paper.receipt as ReceiptModel) : undefined;
  return (
    <main className="shell-main">
      <p className="shell-kicker">Finding</p>
      <h1 className="shell-headline">{params.id}</h1>
      <Receipt receipt={receipt} />
    </main>
  );
}
