import { PaperLoader } from "@/components/PaperLoader";
import "../../paper.css";

export default async function ExperimentPaperPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <PaperLoader id={id} />;
}
