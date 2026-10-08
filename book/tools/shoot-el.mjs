// Screenshot individual elements: node tools/shoot-el.mjs out.png page.html "selector" [nth] [width] [scheme]
import { chromium } from "playwright-core";
import { serve } from "./serve.mjs";
const [out, pg, sel, nth = "0", width = "1280", scheme = "light"] = process.argv.slice(2);
const srv = await serve(0);
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const p = await (await b.newContext({ viewport: { width: +width, height: 900 }, colorScheme: scheme })).newPage();
p.on("pageerror", (e) => console.log("pageerror:", e.message));
p.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text()); });
await p.goto(`http://127.0.0.1:${srv.address().port}/${pg}`, { waitUntil: "networkidle" });
await p.waitForTimeout(300);
const el = p.locator(sel).nth(+nth);
await el.screenshot({ path: out });
await b.close(); srv.close();
