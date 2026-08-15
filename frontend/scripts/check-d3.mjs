#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const bar = fs.readFileSync(path.join(root, "src/components/AttributionBar.tsx"), "utf8");

const checks = [
  [bar.includes("of this round's new gap is"), "caption"],
  [bar.includes("contribution_pct"), "values from payload"],
  [bar.includes("divergence_by_round"), "from divergence_by_round"],
  [bar.includes("price-sensitive"), "price-sensitive band"],
  [bar.includes("competitor"), "competitor band"],
  [bar.includes("loyal"), "loyal band"],
  [bar.includes("attribution__empty"), "empty not fake thirds"],
  [!bar.includes("33"), "no fake 33/33/33"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-D3 checks passed (${checks.length})`);
