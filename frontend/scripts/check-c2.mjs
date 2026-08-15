#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const price = fs.readFileSync(path.join(root, "src/lib/price.ts"), "utf8");
const api = fs.readFileSync(path.join(root, "src/lib/api.ts"), "utf8");

const checks = [
  [form.includes('product_name: "Acme Analytics"'), "Acme prefill"],
  [form.includes("current_price: 49"), "$49 prefill"],
  [form.includes('variable_delta: "+20%"'), "+20% prefill"],
  [form.includes("random_seed: 42"), "seed 42"],
  [form.includes("Product"), "Product group"],
  [form.includes("The one change"), "The one change group"],
  [form.includes("Method"), "Method strip"],
  [form.includes("price_change"), "only price_change"],
  [!form.includes("marketing_spend"), "no unfinished interventions"],
  [form.includes("Run this experiment"), "primary CTA"],
  [form.includes("Open the prepared Acme paper"), "fixture door"],
  [form.includes("/experiments/acme-seed-42"), "golden paper href"],
  [form.includes("createExperiment"), "POST create"],
  [form.includes("ApiDownError"), "API-down path"],
  [!form.includes("setInterval"), "no fake round ticks"],
  [price.includes("Raise ${product} from $${price} to $${forked} starting round"), "live sentence"],
  [api.includes("/experiments"), "POST /experiments"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-C2 checks passed (${checks.length})`);
