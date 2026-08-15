"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listExperiments } from "@/lib/api";
import type { ExperimentListItem, Status } from "@/types/contracts";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function statusLabel(status: Status): string {
  if (status === "complete") return "Complete";
  if (status === "failed") return "Failed";
  return "Running";
}

function statusVariant(status: Status): "secondary" | "destructive" | "outline" {
  if (status === "complete") return "secondary";
  if (status === "failed") return "destructive";
  return "outline";
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
    <main className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Workspace</p>
          <h1 className="text-3xl font-semibold tracking-tight">Runs</h1>
        </div>
        <Button asChild>
          <Link href="/new">New experiment</Link>
        </Button>
      </div>
      {items == null ? (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-4/5" />
          </CardContent>
        </Card>
      ) : items.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>No runs yet</CardTitle>
            <CardDescription>
              Start a twin run. The paper will land here when both worlds finish.
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button asChild>
              <Link href="/new">New experiment</Link>
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <Card>
          <CardContent className="px-0 pt-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="px-6">Product</TableHead>
                  <TableHead>Change</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="px-6">When</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="px-6 font-medium">
                      <Link href={`/experiments/${item.id}`} className="hover:underline">
                        {item.product_name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {item.variable_delta} · ${Math.round(item.current_price)}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(item.status)}>{statusLabel(item.status)}</Badge>
                    </TableCell>
                    <TableCell className="px-6 text-muted-foreground">{when(item.updated_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </main>
  );
}
