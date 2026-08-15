#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const form = fs.readFileSync(path.join(root, "src/components/HypothesisForm.tsx"), "utf8");
if (!form.includes("inside this simulation")) process.exit(1);
console.log("US-C6 checks passed");
