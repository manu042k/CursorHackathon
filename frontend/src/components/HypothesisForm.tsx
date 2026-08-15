"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { ButtonPrimary } from "@/components/ButtonPrimary";
import { Receipt } from "@/components/Receipt";
import { RunProgress } from "@/components/RunProgress";
import { ApiDownError, createExperiment } from "@/lib/api";
import { hypothesisSentence } from "@/lib/price";
import { subscribeExperimentEvents } from "@/lib/sse";
import type { CreateExperimentRequest, RoundCompleteEvent } from "@/types/contracts";

const ACME: CreateExperimentRequest = {
  product_name: "Acme Analytics",
  product_description: "B2B analytics dashboard for e-commerce teams",
  current_price: 49,
  market_size: 30,
  competitor_count: 1,
  competitor_price: 45,
  buyer_price_sensitivity: "medium",
  rounds: 8,
  random_seed: 42,
  variable_type: "price_change",
  variable_delta: "+20%",
  applies_from_round: 1,
  adapter: "fixture",
};

export function HypothesisForm() {
  const [productName, setProductName] = useState(ACME.product_name);
  const [productDescription, setProductDescription] = useState(ACME.product_description);
  const [currentPrice, setCurrentPrice] = useState(String(ACME.current_price));
  const [competitorPrice, setCompetitorPrice] = useState(String(ACME.competitor_price));
  const [delta, setDelta] = useState(ACME.variable_delta);
  const [fromRound, setFromRound] = useState(String(ACME.applies_from_round));
  const seed = ACME.random_seed;
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [startedId, setStartedId] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [ticks, setTicks] = useState<RoundCompleteEvent[]>([]);
  const [failed, setFailed] = useState<string | null>(null);

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
      ...ACME,
      product_name: productName,
      product_description: productDescription,
      current_price: price,
      competitor_price: Number.parseFloat(competitorPrice) || 0,
      variable_type: "price_change",
      variable_delta: delta,
      applies_from_round: roundN,
      random_seed: seed,
      adapter: "fixture",
    };
    try {
      const created = await createExperiment(body);
      setStartedId(created.id);
    } catch (err) {
      const message =
        err instanceof ApiDownError
          ? err.message
          : "API is not running.";
      setError(`${message} Open the prepared Acme paper.`);
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
        <ButtonPrimary type="submit" disabled={pending}>
          Run this experiment
        </ButtonPrimary>
        <p>
          <Link href="/experiments/acme-seed-42" className="button-secondary">
            Open the prepared Acme paper
          </Link>
        </p>
        {error ? (
          <p className="setup__error" role="alert">
            {error}{" "}
            <Link href="/experiments/acme-seed-42" className="button-secondary">
              Open the prepared Acme paper
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
          <Receipt
            receipt={{
              random_seed: seed,
              prompt_hash: "—",
              roster_hash: "—",
              other_variables_changed: 0,
              adapter: "fixture",
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
