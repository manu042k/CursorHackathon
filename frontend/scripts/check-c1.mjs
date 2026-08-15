#!/usr/bin/env node
/**
 * US-C1 acceptance: tokens, announcement, nav, pill CTA, no SaaS chrome.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

function walk(dir, acc = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === ".next") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else if (/\.(css|tsx|jsx|html)$/.test(entry.name)) acc.push(full);
  }
  return acc;
}

const tokens = fs.readFileSync(path.join(root, "src/styles/tokens.css"), "utf8");
const checks = [
  [tokens.includes("--color-canvas: #ffffff"), "tokens encode canvas white"],
  [tokens.includes("--color-primary: #17171c"), "tokens encode near-black CTA"],
  [tokens.includes("--radius-pill: 32px"), "tokens encode pill radius 32px"],
  [tokens.includes("--color-coral: #ff7759"), "tokens encode coral (taxonomy only)"],
];

const announcement = fs.readFileSync(
  path.join(root, "src/components/AnnouncementBar.tsx"),
  "utf8"
);
checks.push([
  announcement.includes("Controlled experiment — not a forecast"),
  "AnnouncementBar copy",
]);

const nav = fs.readFileSync(path.join(root, "src/components/AppNav.tsx"), "utf8");
checks.push([nav.includes("Replay"), "nav logo left"]);
checks.push([nav.includes("Counterfactual"), "nav title center"]);
checks.push([!/account|avatar|sign in/i.test(nav), "no fake account menu"]);

const button = fs.readFileSync(path.join(root, "src/app/shell.css"), "utf8");
checks.push([button.includes("border-radius: var(--radius-pill)"), "primary button pill"]);
checks.push([button.includes("background: var(--color-primary)"), "primary button #17171c"]);

const files = walk(path.join(root, "src"));
for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  checks.push([!/box-shadow/.test(text), `no box-shadow in ${path.relative(root, file)}`]);
  checks.push([!/blue-600/.test(text), `no blue-600 in ${path.relative(root, file)}`]);
}

const buttonTsx = fs.readFileSync(
  path.join(root, "src/components/ButtonPrimary.tsx"),
  "utf8"
);
checks.push([!/#ff7759/.test(buttonTsx), "primary button is not coral"]);

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log(`US-C1 checks passed (${checks.length})`);
