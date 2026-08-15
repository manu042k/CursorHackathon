#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const twin = fs.readFileSync(path.join(root, "src/components/TwinChart.tsx"), "utf8");
const paper = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
if (twin.includes("setMetric") || twin.includes("Share (%)")) {
  console.error("US-D8: TwinChart must not toggle Share/MRR");
  process.exit(1);
}
if (!paper.includes("PersonaOutcomes") || !paper.includes("CompetitorPath")) {
  console.error("US-D8: FindingPaper must include persona and competitor figures");
  process.exit(1);
}
console.log("US-D8 checks passed");
