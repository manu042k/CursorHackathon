"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listExperiments } from "@/lib/api";
import type { ExperimentListItem, Status } from "@/types/contracts";

function statusLabel(status: Status): string {
  if (status === "complete") return "Complete";
  if (status === "failed") return "Failed";
  return "Running";
}

function statusClass(status: Status): string {
  if (status === "complete") return "runs-row__status is-complete";
  if (status === "failed") return "runs-row__status is-failed";
  return "runs-row__status is-running";
}

function when(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

export function RunHistory() {
  const [items, setItems] = useState<ExperimentListItem[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const next = await listExperiments();
        if (!cancelled) setItems(next);
      } catch {
        if (!cancelled) setItems([]);
      }
    }
    void load();
    const timer = window.setInterval(() => {
      void load();
    }, 4000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  return (
    <main className="runs">
      <p className="shell-kicker">Workspace</p>
      <div className="runs__head">
        <h1 className="shell-headline">Runs</h1>
        <Link href="/new" className="button-primary">
          New experiment
        </Link>
      </div>
      {items == null ? (
        <p className="runs__empty">Loading…</p>
      ) : items.length === 0 ? (
        <p className="runs__empty">No runs yet.</p>
      ) : (
        <ul className="runs__table">
          {items.map((item) => (
            <li key={item.id}>
              <Link href={`/experiments/${item.id}`} className="runs-row">
                <span className="runs-row__name">{item.product_name}</span>
                <span className="runs-row__meta">
                  {item.variable_delta} · ${Math.round(item.current_price)}
                </span>
                <span className={statusClass(item.status)}>{statusLabel(item.status)}</span>
                <span className="runs-row__when">{when(item.updated_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
