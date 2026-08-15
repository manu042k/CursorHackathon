#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const receipt = fs.readFileSync(path.join(root, "src/components/Receipt.tsx"), "utf8");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const finding = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/shell.css"), "utf8");

const checks = [
  [receipt.includes("seed"), "seed"],
  [receipt.includes("adapter"), "adapter"],
  [receipt.includes("runtime"), "runtime"],
  [receipt.includes("model"), "model"],
  [receipt.includes("prompt_hash"), "prompt_hash"],
  [receipt.includes("roster_hash"), "roster_hash"],
  [receipt.includes("other_variables_changed"), "other_variables_changed"],
  [receipt.includes("—"), "em-dash pending hashes"],
  [receipt.includes("slice(0, 8)"), "short hashes"],
  [form.includes("<Receipt"), "used on setup"],
  [finding.includes("<Receipt"), "used on results"],
  [css.includes("font-family: var(--font-mono)"), "mono labels"],
  [!receipt.includes("chip") && !receipt.includes("#ff7759"), "not rainbow chips"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-C3 checks passed (${checks.length})`);
