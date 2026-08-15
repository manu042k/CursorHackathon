#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const finding = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
const checks = [
  [finding.includes("summary_narrative.text"), "renders narrative text"],
  [finding.includes("citation.agent_id} · R{citation.round} · {citation.run_id"), "citations as buyer_3 · R4 · B"],
];
const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log("US-D5 checks passed");
