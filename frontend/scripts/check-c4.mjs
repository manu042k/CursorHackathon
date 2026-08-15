#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const sse = fs.readFileSync(path.join(root, "src/lib/sse.ts"), "utf8");
const progress = fs.readFileSync(path.join(root, "src/components/RunProgress.tsx"), "utf8");

const checks = [
  [sse.includes("EventSource"), "subscribes to events"],
  [sse.includes("/events"), "/events path"],
  [progress.includes("round {latest.round} / 8") || progress.includes("round {latest.round} / 8"), "round index"],
  [progress.includes("Run A") && progress.includes("Run B"), "two columns"],
  [form.includes("router.push") && form.includes("/experiments/"), "navigate on complete"],
  [progress.includes("failed") && !form.includes("router.push(`/experiments/${failed"), "failed stays"],
  [!form.includes("setInterval") && !sse.includes("setInterval") && !progress.includes("setInterval"), "no setInterval"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-C4 checks passed (${checks.length})`);
