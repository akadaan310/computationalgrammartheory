// Scholarly export: render dist/print.html (generated from the same sources
// as the website) to dist/computational-grammar-theory.pdf with headless
// Chromium.  Run after `npm run build`.
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { serve } from "./serve.mjs";

const out = path.resolve("dist", "computational-grammar-theory.pdf");
const srv = await serve(0);
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const page = await browser.newPage();
await page.goto(`http://127.0.0.1:${srv.address().port}/print.html`, { waitUntil: "networkidle" });
await page.emulateMedia({ media: "print" });
await page.pdf({ path: out, format: "A4", printBackground: false, displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666">Computational Grammar Theory — Abed Kadaan — working edition 0.1 — <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
  margin: { top: "18mm", bottom: "20mm", left: "18mm", right: "18mm" } });
await browser.close(); srv.close();
const bytes = fs.statSync(out).size;
const head = fs.readFileSync(out).subarray(0, 5).toString();
if (head !== "%PDF-" || bytes < 100000) { console.error("PDF export failed or suspiciously small"); process.exit(1); }
console.log(`wrote ${out} (${(bytes / 1e6).toFixed(1)} MB)`);
