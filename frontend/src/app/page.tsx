import Link from "next/link";
import "./landing.css";

export default function HomePage() {
  return (
    <main className="landing">
      <p className="landing__kicker">Twin-run market sim</p>
      <h1 className="landing__title">
        Change one thing.
        <br />
        See who caused the rest.
      </h1>
      <p className="landing__lead">
        Same frozen roster, same seed, one price change. Divergence is causal inside
        this simulation — not a market forecast.
      </p>
      <p className="landing__actions">
        <Link href="/new" className="button-primary">
          New experiment
        </Link>
        <Link href="/runs" className="button-secondary">
          View runs
        </Link>
      </p>
      <ul className="landing__points">
        <li>
          <span>Twin runs</span>
          Baseline A against one intervention on B.
        </li>
        <li>
          <span>Live agents</span>
          Watch buyers and the competitor decide in order.
        </li>
        <li>
          <span>Trace</span>
          Open the paper and read the reasons that moved share.
        </li>
      </ul>
    </main>
  );
}
