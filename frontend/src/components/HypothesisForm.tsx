"use client";

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
import { RUN_ROUNDS } from "@/types/contracts";
import { forkedPrice, hypothesisSentence } from "@/lib/price";
import { subscribeExperimentEvents } from "@/lib/sse";

const METHOD = {
  market_size: 30,
  competitor_count: 1,
  rounds: 4 as const,
  variable_type: "price_change" as const,
};

function clampRound(value: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(RUN_ROUNDS, Math.max(1, Math.round(value)));
}

export function HypothesisForm() {
  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [currentPrice, setCurrentPrice] = useState("");
  const [competitorPrice, setCompetitorPrice] = useState("");
  const [sensitivity, setSensitivity] = useState<PriceSensitivity | "">("");
  const [delta, setDelta] = useState("");
  const [fromRound, setFromRound] = useState("");
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
    const aDone = ticks.some((tick) => tick.run_id === "A" && tick.round === RUN_ROUNDS);
    const bDone = ticks.some((tick) => tick.run_id === "B" && tick.round === RUN_ROUNDS);
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

  const price = Number.parseFloat(currentPrice);
  const roundN = clampRound(Number.parseInt(fromRound, 10));
  const sentence = useMemo(() => {
    if (!productName.trim() || !Number.isFinite(price) || !delta.trim()) {
      return "Name the product and the one price change.";
    }
    return hypothesisSentence(productName.trim(), price, delta.trim(), roundN);
  }, [productName, price, delta, roundN]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setStartedId(null);
    setTicks([]);
    setDecisions([]);
    setFailed(null);
    setPending(true);
    if (!sensitivity || !Number.isFinite(price) || !Number.isFinite(Number.parseFloat(competitorPrice))) {
      setError("Fill in the product, prices, and sensitivity.");
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
      buyer_price_sensitivity: sensitivity,
      rounds: METHOD.rounds,
      random_seed: Math.floor(Math.random() * 1_000_000_000),
      variable_type: METHOD.variable_type,
      variable_delta: delta.trim(),
      applies_from_round: roundN,
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
        rounds={RUN_ROUNDS}
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
        {error ? (
          <p className="setup__error" role="alert">
            {error}
          </p>
        ) : null}
      </div>
      <div className="setup__fields">
        <fieldset>
          <legend>Product</legend>
          <p className="setup__group-hint">Enter the product and prices.</p>
          <label>
            Name
            <input
              name="product_name"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="Product name"
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
              required
            >
              <option value="" disabled>
                Select
              </option>
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
                placeholder="1"
                inputMode="numeric"
                min={1}
                max={RUN_ROUNDS}
                required
              />
            </label>
          </div>
          <p className="setup__field-hint">Try +20%, −10%, or +5. Rounds are 1–{RUN_ROUNDS}.</p>
        </fieldset>
        <div className="method-strip" aria-label="Method">
          <p className="method-strip__label">Method</p>
          <p className="setup__group-hint">
            {RUN_ROUNDS} rounds · 30 buyers · 1 competitor · 0 other variables
          </p>
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
              random_seed: 0,
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
