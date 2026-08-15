export default function ExperimentPaperPage({ params }: { params: { id: string } }) {
  return (
    <main className="shell-main">
      <p className="shell-kicker">Finding</p>
      <h1 className="shell-headline">{params.id}</h1>
    </main>
  );
}
