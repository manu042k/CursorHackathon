"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function AppNav() {
  const path = usePathname();
  const onSetup = path === "/";
  return (
    <header className="app-nav">
      <Link href="/" className="app-nav__logo">
        Replay
      </Link>
      <p className="app-nav__title">Counterfactual</p>
      {onSetup ? (
        <Link href="/experiments/grok-bot-seed-42" className="app-nav__action">
          Open Grok Bot paper
        </Link>
      ) : (
        <Link href="/" className="app-nav__action">
          New experiment
        </Link>
      )}
    </header>
  );
}
