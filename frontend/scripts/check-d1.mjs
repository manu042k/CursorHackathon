#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const header = fs.readFileSync(path.join(root, "src/components/PaperHeader.tsx"), "utf8");
const finding = fs.readFileSync(path.join(root, "src/components/FindingPaper.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/paper.css"), "utf8");

const checks = [
  [header.includes("experiment.current_price"), "header from experiment prices"],
  [header.includes("fell"), "share verb fell"],
  [header.includes("rose"), "MRR verb rose"],
  [header.includes("left"), "buyers left"],
  [css.includes("--color-error"), "danger tone"],
  [css.includes("--color-deep-green"), "success tone"],
  [finding.includes("summary_narrative.text"), "narrative above numbers"],
  [finding.includes("<Receipt"), "embeds Receipt"],
  [finding.includes("finding__narrative"), "narrative block"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-D1 checks passed (${checks.length})`);
