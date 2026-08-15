"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FindingPaper } from "@/components/FindingPaper";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import golden from "@/data/grok-bot-seed-42.json";
import { ApiDownError, getExperiment } from "@/lib/api";
import { subscribeExperimentEvents } from "@/lib/sse";
import type { ExperimentPaper } from "@/types/contracts";

type View =
  | { kind: "loading" }
  | { kind: "paper"; paper: ExperimentPaper }
  | { kind: "failed"; error: string }
  | { kind: "empty" };

export function PaperLoader({ id }: { id: string }) {
  const [view, setView] = useState<View>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    let stopEvents: (() => void) | undefined;

    async function load() {
      try {
        const { status, body } = await getExperiment(id);
        if (cancelled) return;
        if (status === 202) {
          setView({ kind: "loading" });
          stopEvents = subscribeExperimentEvents(id, {
            onRound: () => undefined,
            onComplete: () => {
              void load();
            },
            onFailed: (error) => setView({ kind: "failed", error }),
          });
          return;
        }
        if (status === 404) {
          if (id === "grok-bot-seed-42") {
            setView({ kind: "paper", paper: golden as unknown as ExperimentPaper });
            return;
          }
          setView({ kind: "empty" });
          return;
        }
        if (status === 200 && body && typeof body === "object") {
          const paper = body as ExperimentPaper;
          if (paper.status === "failed") {
            setView({ kind: "failed", error: "Engine status: failed. The causal claim is void." });
            return;
          }
          setView({ kind: "paper", paper });
          return;
        }
        setView({ kind: "empty" });
      } catch (err) {
        if (cancelled) return;
        if (id === "grok-bot-seed-42") {
          setView({ kind: "paper", paper: golden as unknown as ExperimentPaper });
          return;
        }
        if (err instanceof ApiDownError) {
          setView({ kind: "empty" });
          return;
        }
        setView({ kind: "empty" });
      }
    }

    void load();
    return () => {
      cancelled = true;
      stopEvents?.();
    };
  }, [id]);

  if (view.kind === "loading") {
    return (
      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-sm text-muted-foreground">Finding</p>
        <div className="skeleton mt-4 space-y-4" aria-hidden="true">
          <Skeleton className="skeleton__rule h-4 w-2/5" />
          <Skeleton className="skeleton__rule skeleton__rule--wide h-8 w-4/5" />
          <Skeleton className="skeleton__rule h-4 w-2/5" />
          <div className="grid grid-cols-3 gap-4 pt-4">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
        </div>
      </main>
    );
  }
  if (view.kind === "failed") {
    return (
      <main className="mx-auto max-w-5xl space-y-4 px-6 py-10">
        <p className="text-sm text-muted-foreground">Finding</p>
        <h1 className="paper-header__title text-3xl font-semibold tracking-tight">This run failed</h1>
        <p className="finding__error text-destructive" role="alert">
          {view.error}
        </p>
        <p className="finding__next">
          <Button asChild>
            <Link href="/new">New experiment</Link>
          </Button>
        </p>
      </main>
    );
  }
  if (view.kind === "empty") {
    return (
      <main className="mx-auto max-w-5xl space-y-4 px-6 py-10">
        <p className="text-sm text-muted-foreground">Finding</p>
        <h1 className="paper-header__title text-3xl font-semibold tracking-tight">No paper for {id}</h1>
        <p className="text-muted-foreground">This id is not in the record. Numbers from Grok Bot are not shown.</p>
        <p className="finding__next">
          <Button asChild>
            <Link href="/new">New experiment</Link>
          </Button>
        </p>
      </main>
    );
  }
  return <FindingPaper paper={view.paper} />;
}
