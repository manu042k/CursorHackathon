"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";

export function AppNav() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-5xl items-center gap-6 px-6">
        <Link href="/" className="-ml-2 flex shrink-0 items-center overflow-hidden">
          <img
            src="/assets/butterfly-market.png"
            alt="Butterfly Market"
            className="h-16 w-[280px] object-cover object-center"
          />
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
