import { PaperLoader } from "@/components/PaperLoader";
import "../paper.css";

export default function ExperimentPaperPage({ params }: { params: { id: string } }) {
  return <PaperLoader id={params.id} />;
}
