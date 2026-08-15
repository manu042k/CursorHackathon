#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const trace = fs.readFileSync(path.join(root, "src/components/ReasonTrace.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/paper.css"), "utf8");
const finding = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
const rounds = fs.readFileSync(path.join(root, "src/lib/rounds.ts"), "utf8");

const checks = [
  [trace.includes("decision") && trace.includes("!=="), "default differing decisions"],
  [trace.includes('runLabel("A")') && trace.includes('runLabel("B")'), "Current stacked over Changed"],
  [!css.includes("text-overflow") && !css.includes("ellipsis"), "no truncation"],
  [css.includes("agent-console-card") && css.includes("--color-primary"), "dark console card"],
  [finding.includes("firstMajorRound") && rounds.includes(">= 8"), "opens major round R4"],
  [trace.includes("Show everyone"), "Show everyone"],
  [trace.includes("scrollIntoView"), "citation click scrolls row"],
  [trace.includes("buyer_3") || trace.includes("citation.agent_id"), "citations select round"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-D4 checks passed (${checks.length})`);
