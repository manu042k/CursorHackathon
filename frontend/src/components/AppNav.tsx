"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

export function AppNav() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-5xl items-center gap-4 px-6">
        <Link href="/" className="text-sm font-semibold tracking-tight">
          Replay
        </Link>
        <nav className="ml-auto flex items-center gap-2" aria-label="Primary">
          <Button asChild variant={path.startsWith("/runs") ? "secondary" : "ghost"} size="sm">
            <Link href="/runs">Runs</Link>
          </Button>
          <Button asChild size="sm">
            <Link href="/new">New experiment</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
