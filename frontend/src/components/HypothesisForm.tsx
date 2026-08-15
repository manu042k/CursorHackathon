"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ButtonPrimary } from "@/components/ButtonPrimary";
import { Receipt } from "@/components/Receipt";
import { RunProgress } from "@/components/RunProgress";
import { ApiDownError, createExperiment, getExperiment, getHealth } from "@/lib/api";
import type {
  Adapter,
  CreateExperimentRequest,
  DecisionEvent,
  PriceSensitivity,
  RoundCompleteEvent,
} from "@/types/contracts";
import { forkedPrice, hypothesisSentence } from "@/lib/price";
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

function clampRound(value: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(8, Math.max(1, Math.round(value)));
}

export function HypothesisForm() {
  const [productName, setProductName] = useState(GROK_BOT.product_name);
  const [productDescription, setProductDescription] = useState(GROK_BOT.product_description);
  const [currentPrice, setCurrentPrice] = useState(String(GROK_BOT.current_price));
  const [competitorPrice, setCompetitorPrice] = useState(String(GROK_BOT.competitor_price));
  const [sensitivity, setSensitivity] = useState<PriceSensitivity>(GROK_BOT.buyer_price_sensitivity);
  const [delta, setDelta] = useState(GROK_BOT.variable_delta);
  const [fromRound, setFromRound] = useState(String(GROK_BOT.applies_from_round));
  const [seed, setSeed] = useState(String(GROK_BOT.random_seed));
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [startedId, setStartedId] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [ticks, setTicks] = useState<RoundCompleteEvent[]>([]);
  const [decisions, setDecisions] = useState<DecisionEvent[]>([]);
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
    const aDone = ticks.some((tick) => tick.run_id === "A" && tick.round === 8);
    const bDone = ticks.some((tick) => tick.run_id === "B" && tick.round === 8);
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
  }, [ticks, startedId, failed, router]);

  const price = Number.parseFloat(currentPrice) || 0;
  const roundN = clampRound(Number.parseInt(fromRound, 10));
  const seedN = Number.parseInt(seed, 10) || GROK_BOT.random_seed;
  const sentence = useMemo(
    () => hypothesisSentence(productName || "this product", price, delta || "+0%", roundN),
    [productName, price, delta, roundN]
  );

  function resetDefaults() {
    setProductName(GROK_BOT.product_name);
    setProductDescription(GROK_BOT.product_description);
    setCurrentPrice(String(GROK_BOT.current_price));
    setCompetitorPrice(String(GROK_BOT.competitor_price));
    setSensitivity(GROK_BOT.buyer_price_sensitivity);
    setDelta(GROK_BOT.variable_delta);
    setFromRound(String(GROK_BOT.applies_from_round));
    setSeed(String(GROK_BOT.random_seed));
    setAdapter("fixture");
    setError(null);
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setStartedId(null);
    setTicks([]);
    setDecisions([]);
    setFailed(null);
    setPending(true);
    const body: CreateExperimentRequest = {
      ...GROK_BOT,
      product_name: productName.trim() || GROK_BOT.product_name,
      product_description: productDescription.trim() || GROK_BOT.product_description,
      current_price: price,
      competitor_price: Number.parseFloat(competitorPrice) || 0,
      buyer_price_sensitivity: sensitivity,
      variable_type: "price_change",
      variable_delta: delta.trim() || GROK_BOT.variable_delta,
      applies_from_round: roundN,
      random_seed: seedN,
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
    return (
      <RunProgress
        ticks={ticks}
        decisions={decisions}
        failed={failed}
        basePrice={price}
        forkedPrice={forkedPrice(price, delta || "+0%")}
        appliesFromRound={roundN}
        experimentId={startedId}
      />
    );
  }

  return (
    <form className="setup" onSubmit={onSubmit}>
      <div className="setup__story">
        <p className="setup__kicker">New experiment</p>
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
          <p className="setup__group-hint">Edit these. Grok Bot is only a starting point.</p>
          <label>
            Name
            <input
              name="product_name"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="Grok Bot"
              required
            />
          </label>
          <label>
            Description
            <textarea
              name="product_description"
              value={productDescription}
              onChange={(e) => setProductDescription(e.target.value)}
              placeholder="What the product does"
              rows={3}
              required
            />
          </label>
          <div className="setup__row">
            <label>
              Your price
              <input
                name="current_price"
                value={currentPrice}
                onChange={(e) => setCurrentPrice(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
            <label>
              Competitor price
              <input
                name="competitor_price"
                value={competitorPrice}
                onChange={(e) => setCompetitorPrice(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
          </div>
          <label>
            Buyer price sensitivity
            <select
              name="buyer_price_sensitivity"
              value={sensitivity}
              onChange={(e) => setSensitivity(e.target.value as PriceSensitivity)}
            >
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
          </label>
        </fieldset>
        <fieldset>
          <legend>The one change</legend>
          <p className="setup__group-hint">Only this differs between Run A (baseline) and Run B.</p>
          <label>
            Type
            <input name="variable_type" value="price_change" readOnly />
          </label>
          <div className="setup__row">
            <label>
              Delta
              <input
                name="variable_delta"
                value={delta}
                onChange={(e) => setDelta(e.target.value)}
                placeholder="+20%"
                required
              />
            </label>
            <label>
              From round
              <input
                name="applies_from_round"
                value={fromRound}
                onChange={(e) => setFromRound(e.target.value)}
                inputMode="numeric"
                min={1}
                max={8}
                required
              />
            </label>
          </div>
          <p className="setup__field-hint">Try +20%, −10%, or +5. Rounds are 1–8.</p>
        </fieldset>
        <div className="method-strip" aria-label="Method">
          <p className="method-strip__label">Method</p>
          <p className="setup__group-hint">8 rounds · 30 buyers · 1 competitor · 0 other variables</p>
          <label>
            Seed
            <input
              name="random_seed"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              inputMode="numeric"
              required
            />
          </label>
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
              random_seed: seedN,
              prompt_hash: "—",
              roster_hash: "—",
              other_variables_changed: 0,
              adapter,
              runtime: "local",
              model: "—",
              tools: [],
            }}
          />
          <p>
            <button type="button" className="button-secondary" onClick={resetDefaults}>
              Reset to Grok Bot defaults
            </button>
          </p>
        </div>
      </div>
    </form>
  );
}
