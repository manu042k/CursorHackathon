"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ButtonPrimary } from "@/components/ButtonPrimary";
import { Receipt } from "@/components/Receipt";
import { RunProgress } from "@/components/RunProgress";
import { Alert } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { RosterConfirm } from "@/components/RosterConfirm";
import { ApiDownError, createExperiment, getExperiment, getHealth, startExperiment, waitRosterReady } from "@/lib/api";
import type {
  Adapter,
  CreateExperimentRequest,
  DecisionEvent,
  Roster,
  RoundCompleteEvent,
  VariableType,
} from "@/types/contracts";
import { VARIABLE_TYPES } from "@/types/contracts";
import { forkedPrice, hypothesisSentence } from "@/lib/price";
import { subscribeExperimentEvents } from "@/lib/sse";

const METHOD = {
  market_size: 30,
  competitor_count: 1,
  adapter: "fixture" as Adapter,
  random_seed: 42,
  buyer_price_sensitivity: "medium" as const,
};

const DELTA_HINT: Record<VariableType, string> = {
  price_change: "+20%",
  competitor_entry: "-20%",
  marketing_spend: "+20%",
  feature_change: "cut search",
};

function clampRounds(value: number): number {
  if (!Number.isFinite(value)) return 4;
  return Math.min(8, Math.max(3, Math.round(value)));
}

function clampRound(value: number, maxRounds: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(maxRounds, Math.max(1, Math.round(value)));
}

export function HypothesisForm() {
  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [currentPrice, setCurrentPrice] = useState("");
  const [competitorPrice, setCompetitorPrice] = useState("");
  const [variableType, setVariableType] = useState<VariableType>("price_change");
  const [delta, setDelta] = useState("");
  const [fromRound, setFromRound] = useState("");
  const [rounds, setRounds] = useState(4);
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [startedId, setStartedId] = useState<string | null>(null);
  const [experimentId, setExperimentId] = useState<string | null>(null);
  const [roster, setRoster] = useState<Roster | null>(null);
  const [pending, setPending] = useState(false);
  const [ticks, setTicks] = useState<RoundCompleteEvent[]>([]);
  const [decisions, setDecisions] = useState<DecisionEvent[]>([]);
  const [failed, setFailed] = useState<string | null>(null);
  const [cursorReady, setCursorReady] = useState(false);

  useEffect(() => {
    void getHealth().then((health) => {
      if (health?.cursor_configured) setCursorReady(true);
    });
  }, []);

  useEffect(() => {
    if (!startedId) return;
    const stop = subscribeExperimentEvents(startedId, {
      onRound: (event) => setTicks((prev) => [...prev, event]),
      onDecision: (event) => setDecisions((prev) => [...prev, event]),
      onComplete: (id) => {
        window.setTimeout(() => router.push(`/experiments/${id}`), 1800);
      },
      onFailed: (message) => setFailed(message),
    });
    return stop;
  }, [startedId, router]);

  useEffect(() => {
    if (!startedId || failed) return;
    const aDone = ticks.some((tick) => tick.run_id === "A" && tick.round === rounds);
    const bDone = ticks.some((tick) => tick.run_id === "B" && tick.round === rounds);
    if (!aDone || !bDone) return;
    let cancelled = false;
    const timer = window.setTimeout(() => {
      void getExperiment(startedId).then(({ status }) => {
        if (!cancelled && status === 200) router.push(`/experiments/${startedId}`);
      });
    }, 2200);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [ticks, startedId, failed, router, rounds]);

  const price = Number.parseFloat(currentPrice);
  const roundN = clampRound(Number.parseInt(fromRound, 10), rounds);
  const adapter: Adapter = cursorReady ? "cursor" : METHOD.adapter;
  const sentence = useMemo(() => {
    if (!productName.trim() || !delta.trim()) {
      return "Name the product and the one change.";
    }
    if (!Number.isFinite(price)) {
      return "Name the product and the one change.";
    }
    return hypothesisSentence(
      productName.trim(),
      price,
      delta.trim(),
      roundN,
      variableType,
      Number.parseFloat(competitorPrice)
    );
  }, [productName, price, delta, roundN, variableType, competitorPrice]);

  function resetToForm() {
    setError(null);
    setStartedId(null);
    setExperimentId(null);
    setRoster(null);
    setTicks([]);
    setDecisions([]);
    setFailed(null);
    setPending(false);
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setStartedId(null);
    setExperimentId(null);
    setRoster(null);
    setTicks([]);
    setDecisions([]);
    setFailed(null);
    setPending(true);
    if (!Number.isFinite(price) || !Number.isFinite(Number.parseFloat(competitorPrice))) {
      setError("Fill in the product and both prices.");
      setPending(false);
      return;
    }
    const body: CreateExperimentRequest = {
      product_name: productName.trim(),
      product_description: productDescription.trim(),
      current_price: price,
      market_size: METHOD.market_size,
      competitor_count: METHOD.competitor_count,
      competitor_price: Number.parseFloat(competitorPrice),
      buyer_price_sensitivity: METHOD.buyer_price_sensitivity,
      rounds: clampRounds(rounds),
      random_seed: METHOD.random_seed,
      variable_type: variableType,
      variable_delta: delta.trim(),
      applies_from_round: roundN,
      adapter,
    };
    try {
      const created = await createExperiment(body);
      const proposed = await waitRosterReady(created.id);
      setExperimentId(created.id);
      setRoster(proposed);
    } catch (err) {
      const message =
        err instanceof ApiDownError
          ? err.message
          : "API is not running.";
      setError(message);
    } finally {
      setPending(false);
    }
  }

  async function onConfirm() {
    if (!experimentId) return;
    setError(null);
    setPending(true);
    try {
      await startExperiment(experimentId);
      setStartedId(experimentId);
    } catch (err) {
      const message = err instanceof ApiDownError ? err.message : "API is not running.";
      setError(message);
    } finally {
      setPending(false);
    }
  }

  if (startedId) {
    return (
      <RunProgress
        ticks={ticks}
        decisions={decisions}
        failed={failed}
        basePrice={Number.isFinite(price) ? price : 0}
        forkedPrice={forkedPrice(Number.isFinite(price) ? price : 0, delta || "+0%")}
        appliesFromRound={roundN}
        experimentId={startedId}
        rounds={rounds}
      />
    );
  }

  if (roster && experimentId) {
    return (
      <div>
        {error ? (
          <Alert className="mx-auto mt-6 max-w-5xl border-destructive text-destructive">
            {error}
          </Alert>
        ) : null}
        <RosterConfirm
          roster={roster}
          pending={pending}
          onConfirm={() => void onConfirm()}
          onEdit={resetToForm}
        />
      </div>
    );
  }

  if (pending) {
    return (
      <section className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-sm text-muted-foreground">Research</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">Inferring the roster…</h1>
        <p className="mt-2 text-muted-foreground">
          Five users, one competitor, one analyst — then you confirm before analysis starts.
        </p>
      </section>
    );
  }

  return (
    <form className="mx-auto grid max-w-5xl gap-8 px-6 py-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]" onSubmit={onSubmit}>
      <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
        <p className="text-sm text-muted-foreground">You are testing</p>
        <h1 className="text-3xl font-semibold tracking-tight">{sentence}</h1>
        <p className="text-muted-foreground">
          Divergence is causal inside this simulation — not a market forecast.
        </p>
        <ButtonPrimary type="submit" disabled={pending}>
          Begin research
        </ButtonPrimary>
        {error ? (
          <Alert className="border-destructive text-destructive">
            {error}
          </Alert>
        ) : null}
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Product</CardTitle>
          <CardDescription>Name, what it does, and the two prices.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="product_name">Name</Label>
            <Input
              id="product_name"
              name="product_name"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="Product name"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="product_description">Description</Label>
            <Textarea
              id="product_description"
              name="product_description"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              placeholder="What the product does"
              rows={3}
              required
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="current_price">Your price</Label>
              <Input
                id="current_price"
                name="current_price"
                value={currentPrice}
                onChange={(e) => setCurrentPrice(e.target.value)}
                inputMode="decimal"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="competitor_price">Competitor price</Label>
              <Input
                id="competitor_price"
                name="competitor_price"
                value={competitorPrice}
                onChange={(e) => setCompetitorPrice(e.target.value)}
                inputMode="decimal"
                required
              />
            </div>
          </div>
        </CardContent>
        <Separator />
        <CardHeader>
          <CardTitle>The one change</CardTitle>
          <CardDescription>
            Only this differs between Current (no change) and Changed (this one move).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="variable_type">Type</Label>
            <Select
              value={variableType}
              onValueChange={(value) => setVariableType(value as VariableType)}
            >
              <SelectTrigger id="variable_type" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {VARIABLE_TYPES.map((kind) => (
                  <SelectItem key={kind} value={kind}>
                    {kind}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="variable_delta">Delta</Label>
              <Input
                id="variable_delta"
                name="variable_delta"
                value={delta}
                onChange={(e) => setDelta(e.target.value)}
                placeholder={DELTA_HINT[variableType]}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="applies_from_round">From round</Label>
              <Input
                id="applies_from_round"
                name="applies_from_round"
                value={fromRound}
                onChange={(e) => setFromRound(e.target.value)}
                placeholder="1"
                inputMode="numeric"
                min={1}
                max={rounds}
                required
              />
            </div>
          </div>
        </CardContent>
        <Separator />
        <CardContent className="space-y-3" aria-label="Method">
          <p className="text-sm font-medium">Method</p>
          <div className="space-y-2">
            <Label htmlFor="rounds">Rounds</Label>
            <Select
              value={String(rounds)}
              onValueChange={(value) => {
                const next = clampRounds(Number.parseInt(value, 10));
                setRounds(next);
                setFromRound((current) => {
                  if (!current.trim()) return current;
                  return String(clampRound(Number.parseInt(current, 10), next));
                });
              }}
            >
              <SelectTrigger id="rounds" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <input type="hidden" name="rounds" value={String(rounds)} />
              <SelectContent>
                {[3, 4, 5, 6, 7, 8].map((n) => (
                  <SelectItem key={n} value={String(n)}>
                    {n}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <p className="text-sm text-muted-foreground">
            {rounds} rounds · seed {METHOD.random_seed} · 5 users · 1 competitor · 0 other variables
          </p>
          <Receipt
            receipt={{
              random_seed: METHOD.random_seed,
              prompt_hash: "—",
              roster_hash: "—",
              other_variables_changed: 0,
              adapter,
              runtime: "local",
              model: "—",
              tools: [],
            }}
          />
        </CardContent>
      </Card>
    </form>
  );
}
