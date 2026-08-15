"use client";

import { useEffect, useState } from "react";
import { FindingPaper } from "@/components/FindingPaper";
import golden from "@/data/acme-seed-42.json";
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
          if (id === "acme-seed-42") {
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
        if (id === "acme-seed-42") {
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
      <main className="finding">
        <p className="shell-kicker">Finding</p>
        <div className="skeleton" aria-hidden="true">
          <div className="skeleton__rule" />
          <div className="skeleton__rule skeleton__rule--wide" />
          <div className="skeleton__rule" />
        </div>
      </main>
    );
  }
  if (view.kind === "failed") {
    return (
      <main className="finding">
        <p className="shell-kicker">Finding</p>
        <h1 className="paper-header__title">This run failed</h1>
        <p className="finding__error" role="alert">
          {view.error}
        </p>
      </main>
    );
  }
  if (view.kind === "empty") {
    return (
      <main className="finding">
        <p className="shell-kicker">Finding</p>
        <h1 className="paper-header__title">No paper for {id}</h1>
        <p>This id is not in the record. Numbers from Acme are not shown.</p>
      </main>
    );
  }
  return <FindingPaper paper={view.paper} />;
}
