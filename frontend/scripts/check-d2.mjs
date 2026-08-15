#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const chart = fs.readFileSync(path.join(root, "src/components/TwinChart.tsx"), "utf8");
const rounds = fs.readFileSync(path.join(root, "src/lib/rounds.ts"), "utf8");
const finding = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/paper.css"), "utf8");

const checks = [
  [chart.includes('metric="share"'), "share figure"],
  [chart.includes('metric="mrr"'), "mrr figure"],
  [chart.includes("Run A · $"), "series name A"],
  [chart.includes("Run B · $"), "series name B"],
  [chart.includes("applies_from_round"), "intervention marker"],
  [chart.includes("R{round}"), "round pills"],
  [chart.includes("ArrowLeft"), "left key"],
  [chart.includes("ArrowRight"), "right key"],
  [!css.includes("box-shadow"), "no drop shadows"],
  [css.includes("stroke: var(--color-hairline)"), "hairline axes"],
  [finding.includes("firstMajorRound"), "default major round"],
  [rounds.includes(">= 8"), "golden R4 threshold"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-D2 checks passed (${checks.length})`);
