import { ButtonPrimary } from "@/components/ButtonPrimary";

export default function HomePage() {
  return (
    <main className="shell-main">
      <p className="shell-kicker">Hypothesis</p>
      <h1 className="shell-headline">Change one thing. See who caused the rest.</h1>
      <p>
        <ButtonPrimary>Run this experiment</ButtonPrimary>
      </p>
    </main>
  );
}
