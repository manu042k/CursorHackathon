#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const loader = fs.readFileSync(path.join(root, "src/components/PaperLoader.tsx"), "utf8");
const api = fs.readFileSync(path.join(root, "src/lib/api.ts"), "utf8");
const css = fs.readFileSync(path.join(root, "src/app/paper.css"), "utf8");

const checks = [
  [api.includes("/experiments/${id}"), "GET bind"],
  [loader.includes("skeleton"), "loading skeleton"],
  [loader.includes("failed"), "failed engine error"],
  [loader.includes("No paper for"), "unknown id empty"],
  [loader.includes("Grok Bot are not shown") || loader.includes("not shown"), "no fake Grok Bot numbers"],
  [css.includes("skeleton__rule"), "skeleton rules"],
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error(failed.map(([, msg]) => `FAIL ${msg}`).join("\n"));
  process.exit(1);
}
console.log("US-D6 checks passed");
