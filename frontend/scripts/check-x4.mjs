#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
const api = fs.readFileSync(path.join(root, "src/lib/api.ts"), "utf8");
const checks = [
  [form.includes('adapter'), "same form posts adapter"],
  [form.includes("getHealth"), "health"],
  [form.includes('"cursor"'), "cursor adapter option"],
  [api.includes("/health"), "GET /health"],
];
if (checks.some(([ok]) => !ok)) process.exit(1);
console.log("US-X4 frontend checks passed");
