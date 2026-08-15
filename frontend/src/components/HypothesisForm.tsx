"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ButtonPrimary } from "@/components/ButtonPrimary";
import { Receipt } from "@/components/Receipt";
import { RunProgress } from "@/components/RunProgress";
import { ApiDownError, createExperiment, getHealth } from "@/lib/api";
import type { Adapter, CreateExperimentRequest, RoundCompleteEvent } from "@/types/contracts";
import { hypothesisSentence } from "@/lib/price";
import { subscribeExperimentEvents } from "@/lib/sse";

const GROK_BOT: CreateExperimentRequest = {
  product_name: "Grok Bot",
  product_description:
    "Always-on AI teammates with their own cloud computer. They sign into your tools, finish jobs end to end, and only come back for approval.",
  current_price: 120,
  market_size: 30,
  competitor_count: 1,
  competitor_price: 100,
  buyer_price_sensitivity: "medium",
  rounds: 8,
  random_seed: 42,
  variable_type: "price_change",
  variable_delta: "+20%",
  applies_from_round: 1,
  adapter: "fixture",
};

export function HypothesisForm() {
  const [productName, setProductName] = useState(GROK_BOT.product_name);
  const [productDescription, setProductDescription] = useState(GROK_BOT.product_description);
  const [currentPrice, setCurrentPrice] = useState(String(GROK_BOT.current_price));
  const [competitorPrice, setCompetitorPrice] = useState(String(GROK_BOT.competitor_price));
  const [delta, setDelta] = useState(GROK_BOT.variable_delta);
  const [fromRound, setFromRound] = useState(String(GROK_BOT.applies_from_round));
  const seed = GROK_BOT.random_seed;
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [startedId, setStartedId] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [ticks, setTicks] = useState<RoundCompleteEvent[]>([]);
  const [failed, setFailed] = useState<string | null>(null);
  const [adapter, setAdapter] = useState<Adapter>("fixture");
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
      onComplete: (id) => router.push(`/experiments/${id}`),
      onFailed: (message) => setFailed(message),
    });
    return stop;
  }, [startedId, router]);

  const price = Number.parseFloat(currentPrice) || 0;
  const roundN = Number.parseInt(fromRound, 10) || 1;
  const sentence = useMemo(
    () => hypothesisSentence(productName || "this product", price, delta || "+0%", roundN),
    [productName, price, delta, roundN]
  );

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setStartedId(null);
    setTicks([]);
    setFailed(null);
    setPending(true);
    const body: CreateExperimentRequest = {
      ...GROK_BOT,
      product_name: productName,
      product_description: productDescription,
      current_price: price,
      competitor_price: Number.parseFloat(competitorPrice) || 0,
      variable_type: "price_change",
      variable_delta: delta,
      applies_from_round: roundN,
      random_seed: seed,
      adapter,
    };
    try {
      const created = await createExperiment(body);
      setStartedId(created.id);
    } catch (err) {
      const message =
        err instanceof ApiDownError
          ? err.message
          : "API is not running.";
      setError(`${message} Open the prepared Grok Bot paper.`);
    } finally {
      setPending(false);
    }
  }

  if (startedId) {
    return <RunProgress ticks={ticks} failed={failed} />;
  }

  return (
    <form className="setup" onSubmit={onSubmit}>
      <div className="setup__story">
        <p className="setup__kicker">You are testing</p>
        <h1 className="setup__sentence">{sentence}</h1>
        <p className="setup__honesty">
          Divergence is causal inside this simulation — not a market forecast.
        </p>
        <ButtonPrimary type="submit" disabled={pending}>
          Run this experiment
        </ButtonPrimary>
        <p>
          <Link href="/experiments/grok-bot-seed-42" className="button-secondary">
            Open the prepared Grok Bot paper
          </Link>
        </p>
        {error ? (
          <p className="setup__error" role="alert">
            {error}{" "}
            <Link href="/experiments/grok-bot-seed-42" className="button-secondary">
              Open the prepared Grok Bot paper
            </Link>
          </p>
        ) : null}
      </div>
      <div className="setup__fields">
        <fieldset>
          <legend>Product</legend>
          <label>
            Name
            <input name="product_name" value={productName} onChange={(e) => setProductName(e.target.value)} />
          </label>
          <label>
            Description
            <input
              name="product_description"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
            />
          </label>
          <label>
            Current price
            <input
              name="current_price"
              value={currentPrice}
              onChange={(e) => setCurrentPrice(e.target.value)}
              inputMode="decimal"
            />
          </label>
          <label>
            Competitor price
            <input
              name="competitor_price"
              value={competitorPrice}
              onChange={(e) => setCompetitorPrice(e.target.value)}
              inputMode="decimal"
            />
          </label>
        </fieldset>
        <fieldset>
          <legend>The one change</legend>
          <label>
            Type
            <input name="variable_type" value="price_change" readOnly />
          </label>
          <label>
            Delta
            <input name="variable_delta" value={delta} onChange={(e) => setDelta(e.target.value)} />
          </label>
          <label>
            From round
            <input
              name="applies_from_round"
              value={fromRound}
              onChange={(e) => setFromRound(e.target.value)}
            />
          </label>
        </fieldset>
        <div className="method-strip" aria-label="Method">
          <p className="method-strip__label">Method</p>
          {cursorReady ? (
            <label className="method-strip__cursor">
              <input
                type="checkbox"
                checked={adapter === "cursor"}
                onChange={(e) => setAdapter(e.target.checked ? "cursor" : "fixture")}
              />
              Use Cursor SDK
            </label>
          ) : null}
          <Receipt
            receipt={{
              random_seed: seed,
              prompt_hash: "—",
              roster_hash: "—",
              other_variables_changed: 0,
              adapter,
              runtime: "local",
              model: "—",
              tools: [],
            }}
          />
        </div>
      </div>
    </form>
  );
}
