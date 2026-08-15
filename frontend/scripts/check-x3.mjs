#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const receipt = fs.readFileSync(path.join(root, "src/components/Receipt.tsx"), "utf8");
const trace = fs.readFileSync(path.join(root, "src/components/ReasonTrace.tsx"), "utf8");

const checks = [
  [form.includes('adapter: "fixture"'), "adapter=fixture"],
  [receipt.includes("adapter"), "receipt adapter"],
  [trace.includes("onClick") && trace.includes("scrollTo"), "trace click"],
];
if (checks.some(([ok]) => !ok)) process.exit(1);
console.log("US-X3 frontend checks passed");
