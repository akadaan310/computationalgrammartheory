// Screenshot pages at desktop and mobile widths, light and dark, and report
// console errors, failed requests and horizontal overflow.
//   node tools/screenshot.mjs out-dir page1.html page2.html ...
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { serve } from "./serve.mjs";

const [outDir, ...pages] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const srv = await serve(0);
const base = `http://127.0.0.1:${srv.address().port}/`;
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const problems = [];
for (const [vw, vh, tag] of [[1440, 900, "desktop"], [390, 844, "mobile"]]) {
  for (const scheme of ["light", "dark"]) {
    const ctx = await browser.newContext({ viewport: { width: vw, height: vh }, colorScheme: scheme, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    page.on("console", (m) => { if (m.type() === "error") problems.push(`${tag}/${scheme}: console: ${m.text()}`); });
    page.on("requestfailed", (r) => problems.push(`${tag}/${scheme}: failed request ${r.url()}`));
    page.on("response", (r) => { if (r.status() >= 400) problems.push(`${tag}/${scheme}: HTTP ${r.status()} ${r.url()}`); });
    for (const p of pages) {
      await page.goto(base + p, { waitUntil: "networkidle" });
      await page.waitForTimeout(250);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (overflow > 1) problems.push(`${tag}/${scheme}: ${p} overflows horizontally by ${overflow}px`);
      const name = `${p.replace(/[\/.]/g, "_")}-${tag}-${scheme}.png`;
      await page.screenshot({ path: path.join(outDir, name), fullPage: process.env.FULL === "1" });
    }
    await ctx.close();
  }
}
await browser.close();
srv.close();
console.log(problems.length ? problems.join("\n") : "no console errors, failed requests or horizontal overflow");
