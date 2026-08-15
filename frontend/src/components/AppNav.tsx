"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function AppNav() {
  const path = usePathname();
  return (
    <header className="app-nav">
      <Link href="/" className="app-nav__logo">
        Replay
      </Link>
      <p className="app-nav__title">Counterfactual</p>
      <nav className="app-nav__links" aria-label="Primary">
        <Link href="/runs" className={path.startsWith("/runs") ? "is-active" : ""}>
          Runs
        </Link>
        <Link href="/new" className={path.startsWith("/new") ? "is-active" : ""}>
          New experiment
        </Link>
      </nav>
    </header>
  );
}
