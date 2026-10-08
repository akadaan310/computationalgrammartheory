// Scholarly export: render dist/print.html (generated from the same sources
// as the website) to dist/computational-grammar-theory.pdf with headless
// Chromium.  Run after `npm run build`.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { chromium } from "playwright-core";
import { serve } from "./serve.mjs";

const out = path.resolve("dist", "computational-grammar-theory.pdf");
const srv = await serve(0);
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const page = await browser.newPage();
await page.goto(`http://127.0.0.1:${srv.address().port}/print.html`, { waitUntil: "networkidle" });
await page.emulateMedia({ media: "print" });
// Nothing may be wider than the A4 text block (210 mm − 2×18 mm = 174 mm ≈ 658 CSS px):
// in print there is no scrolling, so wider content would be clipped.
await page.setViewportSize({ width: 658, height: 900 });
const wide = await page.evaluate(() => [...document.querySelectorAll(".katex-display > .katex, table, pre, img, svg")]
  .filter((e) => e.scrollWidth > (e.closest(".equation, .table-wrap, figure, .env, article, main") || document.body).clientWidth + 1)
  .map((e) => `${e.tagName}: ${(e.textContent || "").replace(/\s+/g, " ").slice(0, 70)}`));
if (wide.length) { console.error(`${wide.length} element(s) wider than the print text block:\n  ${wide.join("\n  ")}`); await browser.close(); srv.close(); process.exit(1); }
await page.pdf({ path: out, format: "A4", printBackground: false, displayHeaderFooter: true,
  headerTemplate: "<span></span>",
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666">Computational Grammar Theory — Abed Kadaan — working edition 0.1 — <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
  margin: { top: "18mm", bottom: "20mm", left: "18mm", right: "18mm" } });
await browser.close(); srv.close();
const bytes = fs.statSync(out).size;
const head = fs.readFileSync(out).subarray(0, 5).toString();
if (head !== "%PDF-" || bytes < 100000) { console.error("PDF export failed or suspiciously small"); process.exit(1); }
// Publish a committed copy for static hosts that cannot run Chromium (e.g. Vercel),
// with a manifest the site build uses to detect a stale PDF.
const pub = path.resolve("site", "downloads");
fs.mkdirSync(pub, { recursive: true });
fs.copyFileSync(out, path.join(pub, "computational-grammar-theory.pdf"));
const pages = (fs.readFileSync(out, "latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
const printSha = crypto.createHash("sha256").update(fs.readFileSync(path.resolve("dist", "print.html"))).digest("hex");
fs.writeFileSync(path.join(pub, "pdf.json"), JSON.stringify({ file: "computational-grammar-theory.pdf", pages, bytes, print_html_sha256: printSha, generated: new Date().toISOString().slice(0, 10) }, null, 1) + "\n");
console.log(`wrote ${out} (${(bytes / 1e6).toFixed(1)} MB, ${pages} pages) and site/downloads/`);
