import Link from "next/link";

export function AppNav() {
  return (
    <header className="app-nav">
      <Link href="/" className="app-nav__logo">
        Replay
      </Link>
      <p className="app-nav__title">Counterfactual</p>
      <span className="app-nav__spacer" aria-hidden="true" />
    </header>
  );
}
