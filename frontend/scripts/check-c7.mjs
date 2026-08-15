#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const confirm = fs.readFileSync(path.join(root, "src/components/RosterConfirm.tsx"), "utf8");
if (!confirm.includes("Confirm and run analysis")) {
  console.error("missing confirm CTA");
  process.exit(1);
}
if (!form.includes("RosterConfirm")) {
  console.error("HypothesisForm must render RosterConfirm");
  process.exit(1);
}
console.log("US-C7 checks passed");
