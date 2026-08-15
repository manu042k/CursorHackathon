#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const preview = fs.readFileSync(path.join(root, "src/components/RosterPreview.tsx"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/paper.css"), "utf8");
const checks = [
  [preview.includes("agent_roles"), "from paper roster"],
  [preview.includes("count"), "count"],
  [preview.includes("WTP"), "WTP range"],
  [css.includes("border-bottom: 1px solid var(--color-hairline)"), "rule-separated rows"],
];
if (checks.some(([ok]) => !ok)) process.exit(1);
console.log("US-C5 checks passed");
