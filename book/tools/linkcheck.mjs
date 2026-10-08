// Check every internal link and fragment in dist/: each href to a local page
// must exist, and each #fragment must match an id on the target page.
import fs from "node:fs";
import path from "node:path";
const DIST = path.resolve("dist");
const pages = [];
(function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) walk(p); else if (p.endsWith(".html")) pages.push(p); } })(DIST);
const ids = new Map();
for (const p of pages) ids.set(p, new Set([...fs.readFileSync(p, "utf8").matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
let bad = 0, checked = 0;
for (const p of pages) {
  const html = fs.readFileSync(p, "utf8");
  for (const m of html.matchAll(/href="([^"]+)"/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|data:)/.test(href)) continue;
    const [file, frag] = href.split("#");
    const target = file ? path.resolve(path.dirname(p), file.split("?")[0]) : p;
    checked++;
    if (!fs.existsSync(target)) { bad++; console.error(`${path.relative(DIST, p)}: missing target ${href}`); continue; }
    if (frag && target.endsWith(".html") && !ids.get(target)?.has(decodeURIComponent(frag))) { bad++; console.error(`${path.relative(DIST, p)}: missing fragment ${href}`); }
  }
}
console.log(`${checked} internal links checked, ${bad} broken`);
process.exit(bad ? 1 : 0);
