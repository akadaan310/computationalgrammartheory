#!/usr/bin/env node
// Build the CGT book website from canonical sources in book/content.
//
//   node tools/build.mjs              -> dist/  (fails on any integrity error)
//   node tools/build.mjs --check-only -> run all checks, write nothing
//
// Authoring format (BOOK_CONTENT_ARCHITECTURE.md):
//   * Markdown with $inline$ and $$display$$ LaTeX (KaTeX, rendered at build
//     time to HTML + MathML; a parse error FAILS the build -- never shown raw).
//   * Environments:  ::: theorem {#thm:label title="..." status="proved-here" ledger="CGT-THM-006"}
//   * Inline commands outside math: \ref{label} \eqref{eq:label} \cite{key,key}
//     \ledger{CGT-THM-006} \gloss{term} \chapref{chapter-id}
//   * Equations: \label{eq:x} inside $$...$$ -> numbered (c.k) with \tag.
//   * ```python run  ... ```  followed by ```output ... ``` is executed and
//     compared by tools/check_examples.py.
//   * ::: demo name  ...accessible text alternative... :::  mounts a lab widget.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import katex from "katex";
import MarkdownIt from "markdown-it";
import container from "markdown-it-container";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const REPO = path.resolve(ROOT, "..");
const CONTENT = path.join(ROOT, "content");
const DIST = path.join(ROOT, "dist");
const CHECK_ONLY = process.argv.includes("--check-only");

const errors = [];
const warnings = [];
const err = (where, msg) => errors.push(`${where}: ${msg}`);
const warn = (where, msg) => warnings.push(`${where}: ${msg}`);

// ------------------------------------------------------------------ data
const readJSON = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const book = readJSON(path.join(CONTENT, "book.json"));
const bib = readJSON(path.join(CONTENT, "bibliography.json"));
const glossary = readJSON(path.join(CONTENT, "glossary.json"));
const macros = readJSON(path.join(CONTENT, "macros.json"));
const dataDir = path.join(ROOT, "data");
const loadData = (n) => (fs.existsSync(path.join(dataDir, n)) ? readJSON(path.join(dataDir, n)) : null);
const sdkRef = loadData("sdk_reference.json");
const gaasCaps = loadData("gaas_capabilities.json");
const ledgerIds = new Set(loadData("ledger_ids.json") || []);

const LEDGER = [["results", "RESULTS.md", "Results ledger"], ["definitions", "DEFINITIONS.md", "Definitions"], ["hypotheses", "HYPOTHESES.md", "Hypotheses"],
  ["counterexamples", "COUNTEREXAMPLES.md", "Counterexamples and rejected hypotheses"], ["open-problems", "OPEN_PROBLEMS.md", "Open problems"],
  ["experiments", "EXPERIMENTS.md", "Experiments"], ["provenance", "PROVENANCE.md", "Provenance"], ["literature", "LITERATURE_REVIEW.md", "Literature review"],
  ["decisions", "DECISION_LOG.md", "Decision log"], ["charter", "RESEARCH_CHARTER.md", "Research charter"], ["audit", "PUBLICATION_AUDIT.md", "Publication audit"],
  ["summary", "experiments/results/SUMMARY.md", "Experimental summary (generated)"]];

const ENV = {
  // name: [display name, counter, numbered]
  definition: ["Definition", "thm", true], theorem: ["Theorem", "thm", true],
  proposition: ["Proposition", "thm", true], lemma: ["Lemma", "thm", true],
  corollary: ["Corollary", "thm", true], conjecture: ["Conjecture", "thm", true],
  observation: ["Empirical observation", "thm", true], algorithm: ["Algorithm", "alg", true],
  example: ["Example", "ex", true], exercise: ["Exercise", "exr", true],
  remark: ["Remark", null, false], proof: ["Proof", null, false],
  solution: ["Solution", null, false], objectives: ["Learning objectives", null, false],
  summary: ["Summary", null, false], boundary: ["Claim boundary", null, false],
  demo: ["Interactive laboratory", null, false], history: ["Historical note", null, false],
};
const FORMAL = new Set(["theorem", "proposition", "lemma", "corollary", "conjecture", "observation"]);
const STATUS = {
  "proved-here": ["Proved here", "Proof in this book; self-checked, not externally reviewed."],
  "standard": ["Established", "Known result from the literature; cited."],
  "adapted": ["Adapted", "Known ideas restated or packaged in CGT terms."],
  "empirical": ["Empirical", "Reproducible measurement; not a proof."],
  "conjecture": ["Conjecture", "Not established."],
  "rejected": ["Rejected", "A hypothesis this research tested and rejected."],
  "definition": ["Definition", "A precise object, not a discovery."],
  "proposed": ["Proposed", "A model or design proposed here; novelty unverified."],
};

// ------------------------------------------------------------------ chapters
function parseFrontMatter(src, file) {
  const m = src.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) { err(file, "missing front matter"); return [{}, src]; }
  const meta = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2].trim();
  }
  return [meta, src.slice(m[0].length)];
}

const chapters = [];
let chapterNo = 0;
for (const part of book.parts) {
  for (const slug of part.chapters) {
    const file = path.join(CONTENT, "chapters", `${slug}.md`);
    if (!fs.existsSync(file)) {
      if (process.env.CGT_PARTIAL) { warn("book.json", `chapter file missing (partial build): ${slug}.md`); continue; }
      err("book.json", `chapter file missing: ${slug}.md`); continue;
    }
    const raw = fs.readFileSync(file, "utf8");
    const [meta, body] = parseFrontMatter(raw, slug);
    const appendix = part.appendix === true;
    const number = appendix ? String.fromCharCode(65 + chapters.filter((c) => c.appendix).length) : String(++chapterNo);
    chapters.push({ slug, file, meta, body, part, number, appendix, url: `chapters/${slug}.html` });
  }
}

// ------------------------------------------------------------------ helpers
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const slugify = (s) => s.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
function parseAttrs(s, where) {
  const out = {};
  const m = s.match(/\{([^}]*)\}/);
  if (!m) return out;
  const re = /#([\w:.-]+)|(\w+)="([^"]*)"/g;
  let x;
  while ((x = re.exec(m[1]))) {
    if (x[1]) out.id = x[1]; else out[x[2]] = x[3];
  }
  return out;
}

function renderMath(tex, display, where, tag) {
  try {
    return katex.renderToString(tag ? `${tex} \\tag{${tag}}` : tex, {
      displayMode: display, throwOnError: true, strict: "error", output: "htmlAndMathml",
      trust: false, macros: { ...macros },
    });
  } catch (e) {
    err(where, `LaTeX error in ${display ? "display" : "inline"} math «${tex.slice(0, 80)}»: ${e.message}`);
    return `<span class="math-error" role="alert">[equation failed to render: build error]</span>`;
  }
}

// ------------------------------------------------------------------ registry (pass 1 fills, pass 2 resolves)
let registry = new Map(); // label -> {kind, number, url, title, chapter}
const formalIndex = [];  // for theorem index page
const searchDocs = [];
const citedKeys = new Set();
const usedLedger = new Set();

function makeMd(ctx) {
  const md = new MarkdownIt({ html: true, linkify: false, typographer: true });

  // --- display math $$...$$ (block)
  md.block.ruler.before("fence", "math_block", (state, start, end, silent) => {
    const pos = state.bMarks[start] + state.tShift[start];
    if (state.src.slice(pos, pos + 2) !== "$$") return false;
    let line = start, content = state.src.slice(pos + 2, state.eMarks[start]);
    let closed = content.trimEnd().endsWith("$$") && content.trim().length > 2;
    if (closed) content = content.trimEnd().slice(0, -2);
    else {
      const lines = [content];
      while (++line < end) {
        const l = state.src.slice(state.bMarks[line] + state.tShift[line], state.eMarks[line]);
        if (l.trimEnd().endsWith("$$")) { lines.push(l.trimEnd().slice(0, -2)); closed = true; break; }
        lines.push(l);
      }
      content = lines.join("\n");
    }
    if (!closed) return false;
    if (silent) return true;
    const tok = state.push("math_block", "math", 0);
    tok.content = content; tok.map = [start, line + 1];
    state.line = line + 1;
    return true;
  });
  md.renderer.rules.math_block = (tokens, i) => {
    let tex = tokens[i].content.trim();
    const where = `${ctx.slug}:${(tokens[i].map?.[0] ?? 0) + ctx.offset + 1}`;
    let tag = null, id = "";
    const lab = tex.match(/\\label\{(eq:[\w:.-]+)\}/);
    if (lab) {
      tex = tex.replace(lab[0], "");
      ctx.counters.eq += 1;
      tag = `${ctx.number}.${ctx.counters.eq}`;
      id = lab[1];
      if (ctx.pass === 1) define(id, { kind: "eq", number: tag, url: `${ctx.url}#${id}`, title: `(${tag})`, chapter: ctx.slug }, where);
    }
    return `<div class="equation"${id ? ` id="${id}"` : ""}>${renderMath(tex, true, where, tag)}</div>\n`;
  };

  // --- inline math $...$ and inline commands
  md.inline.ruler.after("escape", "math_inline", (state, silent) => {
    if (state.src[state.pos] !== "$" || state.src[state.pos + 1] === "$") return false;
    let p = state.pos + 1;
    while (p < state.posMax) {
      if (state.src[p] === "\\") { p += 2; continue; }
      if (state.src[p] === "$") break;
      p++;
    }
    if (p >= state.posMax || p === state.pos + 1) return false;
    if (!silent) { const t = state.push("math_inline", "math", 0); t.content = state.src.slice(state.pos + 1, p); }
    state.pos = p + 1;
    return true;
  });
  md.renderer.rules.math_inline = (tokens, i) => renderMath(tokens[i].content, false, ctx.slug, null);

  md.inline.ruler.before("escape", "cgt_cmd", (state, silent) => {
    const m = state.src.slice(state.pos).match(/^\\(ref|eqref|cite|ledger|gloss|chapref)\{([^}]+)\}/);
    if (!m) return false;
    if (!silent) { const t = state.push("cgt_cmd", "", 0); t.meta = { cmd: m[1], arg: m[2] }; }
    state.pos += m[0].length;
    return true;
  });
  md.renderer.rules.cgt_cmd = (tokens, i) => renderCommand(tokens[i].meta, ctx);

  // --- headings with {#sec:id}
  md.core.ruler.push("cgt_headings", (state) => {
    const toks = state.tokens;
    for (let i = 0; i < toks.length; i++) {
      if (toks[i].type !== "heading_open") continue;
      const inline = toks[i + 1];
      let text = inline.content;
      const m = text.match(/\s*\{#(sec:[\w:.-]+)\}\s*$/);
      let id;
      if (m) {
        id = m[1];
        inline.content = text.slice(0, m.index);
        inline.children = inline.children.map((c) => (c.type === "text" ? Object.assign(c, { content: c.content.replace(m[0], "") }) : c));
      } else id = "s-" + slugify(text);
      toks[i].attrSet("id", id);
      const level = Number(toks[i].tag.slice(1));
      if (level === 2) { ctx.counters.sec += 1; ctx.counters.sub = 0; }
      if (level === 3) ctx.counters.sub += 1;
      const num = !ctx.number ? "" : level === 2 ? `${ctx.number}.${ctx.counters.sec}` : level === 3 ? `${ctx.number}.${ctx.counters.sec}.${ctx.counters.sub}` : "";
      if (num) inline.children.unshift(Object.assign(new state.Token("html_inline", "", 0), { content: `<span class="secno">${num}</span> ` }));
      const clean = inline.content.replace(/\$[^$]*\$/g, "").trim();
      if (level <= 3) ctx.toc.push({ id, level, num, text: inline.content });
      if (ctx.pass === 1 && m) define(id, { kind: "sec", number: num, url: `${ctx.url}#${id}`, title: `§${num}`, chapter: ctx.slug }, ctx.slug);
      if (ctx.pass === 2 && level <= 3) searchDocs.push({ t: `${num} ${clean}`, u: `${ctx.url}#${id}`, k: "section", c: ctx.title });
    }
  });

  // --- environments
  for (const name of Object.keys(ENV)) {
    md.use(container, name, {
      validate: (params) => params.trim().split(/\s/)[0] === name,
      render: (tokens, idx) => renderEnv(name, tokens, idx, ctx),
    });
  }

  // --- code fences: language, run marker, light highlighting
  md.renderer.rules.fence = (tokens, i) => {
    const info = tokens[i].info.trim().split(/\s+/);
    const lang = info[0] || "text";
    const run = info.includes("run");
    const code = tokens[i].content;
    const label = lang === "output" ? "Output (checked)" : run ? "Python · executed by the book's example checker" : lang;
    return `<figure class="code ${lang === "output" ? "code-output" : ""}"><figcaption>${esc(label)}</figcaption><pre><code class="lang-${esc(lang)}">${highlight(code, lang)}</code></pre></figure>\n`;
  };
  return md;
}

const PY_KW = "False|None|True|and|as|assert|break|class|continue|def|elif|else|except|for|from|if|import|in|is|lambda|not|or|pass|raise|return|try|while|with|yield";
const PY_RE = new RegExp(`(#[^\\n]*)|(&quot;(?:[^&]|&(?!quot;))*?&quot;|'[^'\\n]*')|\\b(\\d+(?:\\.\\d+)?)\\b|\\b(${PY_KW})\\b`, "g");
function highlight(code, lang) {
  const e = esc(code);
  if (lang !== "python") return e;
  return e.replace(PY_RE, (m, c, s, n, k) => c ? `<span class="tok-c">${c}</span>` : s ? `<span class="tok-s">${s}</span>`
    : n ? `<span class="tok-n">${n}</span>` : `<span class="tok-k">${k}</span>`);
}

function define(label, entry, where) {
  if (registry.has(label)) err(where, `duplicate label ${label}`);
  registry.set(label, entry);
}

function renderCommand({ cmd, arg }, ctx) {
  const where = ctx.slug;
  if (cmd === "cite") {
    const keys = arg.split(",").map((s) => s.trim());
    const parts = keys.map((k) => {
      const b = bib[k];
      if (!b) { if (ctx.pass === 2) err(where, `unknown citation key ${k}`); return `<span class="cite-missing">[${esc(k)}?]</span>`; }
      citedKeys.add(k); ctx.cites.add(k);
      return `<a class="cite" href="${ctx.rel}bibliography.html#${k}" title="${esc(b.short || b.title)}">${esc(b.label)}</a>`;
    });
    return `<span class="citation">[${parts.join("; ")}]</span>`;
  }
  if (cmd === "ledger") {
    usedLedger.add(arg);
    if (ctx.pass === 2 && ledgerIds.size && !ledgerIds.has(arg)) err(where, `unknown ledger id ${arg}`);
    return `<a class="ledger-id" href="${ctx.rel}${ledgerUrl(arg)}">${esc(arg)}</a>`;
  }
  if (cmd === "gloss") {
    const key = arg.toLowerCase();
    const g = glossary.find((x) => x.term.toLowerCase() === key || (x.aliases || []).map((a) => a.toLowerCase()).includes(key));
    if (!g && ctx.pass === 2) err(where, `unknown glossary term ${arg}`);
    return `<a class="gloss" href="${ctx.rel}glossary.html#${g ? slugify(g.term) : ""}" title="${esc(g ? g.short : "")}">${esc(arg)}</a>`;
  }
  if (cmd === "chapref") {
    const c = chapters.find((x) => x.slug === arg || x.meta.id === arg);
    if (!c) { if (ctx.pass === 2) (process.env.CGT_PARTIAL ? warn : err)(where, `unknown chapter ${arg}`); return esc(arg); }
    return `<a class="xref" href="${ctx.rel}${c.url}">${c.appendix ? "Appendix" : "Chapter"} ${c.number}</a>`;
  }
  // ref / eqref
  const r = registry.get(arg);
  if (!r) { if (ctx.pass === 2) err(where, `unresolved reference ${arg}`); return `<span class="xref-missing">??</span>`; }
  const text = cmd === "eqref" ? `(${r.number})` : r.kind === "sec" ? `§${r.number}` : `${r.title}`;
  return `<a class="xref" href="${ctx.rel}${r.url}">${esc(text)}</a>`;
}

function ledgerUrl(id) {
  const kind = id.split("-")[1];
  const preferred = { DEF: "definitions", H: "hypotheses", HYP: "hypotheses", NEG: "counterexamples", REJ: "counterexamples",
    OPEN: "open-problems", EXP: "experiments", D: "decisions" }[kind] || "results";
  const preferredHas = ledgerRendered?.find((L) => L.slug === preferred)?.ids.has(id);
  if (!preferredHas && anchorPage.has(id)) return `ledger/${anchorPage.get(id)}.html#${id}`;
  const page = { DEF: "definitions", H: "hypotheses", HYP: "hypotheses", NEG: "counterexamples", REJ: "counterexamples",
    OPEN: "open-problems", EXP: "experiments", D: "decisions" }[kind] || "results";
  return `ledger/${page}.html#${id}`;
}

function renderEnv(name, tokens, idx, ctx) {
  const [display, counter, numbered] = ENV[name];
  const tok = tokens[idx];
  if (tok.nesting === -1) {
    const close = ctx.envStack.pop();
    if (close === "proof") return `<span class="qed" aria-label="end of proof">∎</span></div></div>\n`;
    if (close === "solution") return `</div></details>\n`;
    if (close === "demo") return `</div></div></section>\n`;
    return `</div></div>\n`;
  }
  ctx.envStack.push(name);
  const where = `${ctx.slug}:${(tok.map?.[0] ?? 0) + ctx.offset + 1}`;
  const params = tok.info.trim().slice(name.length).trim();
  const attrs = parseAttrs(params, where);
  let number = "";
  if (numbered) {
    ctx.counters[counter] = (ctx.counters[counter] || 0) + 1;
    number = `${ctx.number}.${ctx.counters[counter]}`;
  }
  const id = attrs.id || (numbered ? `${name}-${number}` : `${name}-${ctx.slug}-${idx}`);
  const title = attrs.title ? attrs.title : "";
  if (FORMAL.has(name) && !attrs.status) err(where, `${display} ${number} has no status attribute`);
  if (attrs.status && !STATUS[attrs.status]) err(where, `unknown status ${attrs.status}`);
  if (attrs.ledger) {
    for (const L of attrs.ledger.split(",").map((s) => s.trim())) {
      usedLedger.add(L);
      if (ctx.pass === 2 && ledgerIds.size && !ledgerIds.has(L)) err(where, `unknown ledger id ${L}`);
    }
  }
  const label = `${display}${number ? " " + number : ""}`;
  if (ctx.pass === 1 && attrs.id) define(attrs.id, { kind: name, number, url: `${ctx.url}#${id}`, title: label, chapter: ctx.slug }, where);
  if (ctx.pass === 2 && numbered && ["definition", "theorem", "proposition", "lemma", "corollary", "conjecture", "observation", "algorithm"].includes(name)) {
    formalIndex.push({ kind: name, label, title, status: attrs.status || (name === "definition" ? "definition" : ""), ledger: attrs.ledger || "", url: `${ctx.url}#${id}`, chapter: ctx.number, chapterTitle: ctx.title });
    searchDocs.push({ t: `${label}${title ? " — " + title : ""}`, u: `${ctx.url}#${id}`, k: name, c: ctx.title });
  }
  const badge = attrs.status ? `<span class="status status-${attrs.status}" title="${esc(STATUS[attrs.status]?.[1] || "")}">${esc(STATUS[attrs.status]?.[0] || attrs.status)}</span>` : "";
  const ledger = attrs.ledger ? attrs.ledger.split(",").map((L) => `<a class="ledger-id" href="${ctx.rel}${ledgerUrl(L.trim())}">${esc(L.trim())}</a>`).join(" ") : "";
  const titleHtml = title ? ` <span class="env-title">(${md2inline(title, ctx)})</span>` : "";
  if (name === "proof") return `<div class="env env-proof" id="${id}"><div class="env-head"><em>Proof${titleHtml}.</em></div><div class="env-body">\n`;
  if (name === "solution") return `<details class="env env-solution"><summary>Solution${attrs.of ? " to " + renderCommand({ cmd: "ref", arg: attrs.of }, ctx) : ""}</summary><div class="env-body">\n`;
  if (name === "demo") {
    const demo = params.split(/\s+/)[0];
    if (!demo) err(where, "demo needs a name");
    ctx.demos.add(demo);
    return `<section class="env env-demo" aria-label="Interactive laboratory: ${esc(demo)}"><div class="env-head"><span class="env-name">${display}</span>${titleHtml}</div><div class="demo" data-demo="${esc(demo)}" data-rel="${ctx.rel}"><div class="demo-fallback">\n`;
  }
  return `<div class="env env-${name}" id="${id}"><div class="env-head"><span class="env-name">${esc(label)}</span>${titleHtml}${badge}${ledger ? `<span class="env-ledger">${ledger}</span>` : ""}</div><div class="env-body">\n`;
}

function md2inline(s, ctx) {
  return ctx.mdInline.renderInline(s);
}

// ------------------------------------------------------------------ chapter rendering
function renderChapter(ch, pass) {
  const ctx = {
    slug: ch.slug, number: ch.number, url: ch.url, rel: "../", title: ch.meta.title, pass,
    counters: { thm: 0, alg: 0, ex: 0, exr: 0, eq: 0, sec: 0, sub: 0 }, toc: [], envStack: [],
    cites: new Set(), demos: new Set(), offset: (ch.file && fs.readFileSync(ch.file, "utf8").split("\n").length - ch.body.split("\n").length) || 0,
  };
  const md = makeMd(ctx);
  ctx.mdInline = md;
  const html = md.render(ch.body);
  // placeholder / hygiene checks
  if (pass === 2) {
    for (const [i, line] of ch.body.split("\n").entries()) {
      if (/\b(TODO|TBD|FIXME|XXX|lorem ipsum)\b/i.test(line)) err(`${ch.slug}:${i + ctx.offset + 1}`, `placeholder text: ${line.trim().slice(0, 60)}`);
    }
    if (!ch.appendix && !ctx.counters.exr && !ch.meta.noexercises) err(ch.slug, "chapter has no exercises");
    if (!/::: objectives/.test(ch.body) && !ch.appendix && !ch.meta.noobjectives) err(ch.slug, "chapter has no learning objectives");
    if (!/::: summary/.test(ch.body) && !ch.appendix && !ch.meta.nosummary) err(ch.slug, "chapter has no summary");
    for (const req of ["title", "status"]) if (!ch.meta[req]) err(ch.slug, `front matter lacks ${req}`);
  }
  return { html, ctx };
}

// ledger pages first: every identifier links to the page where it is actually anchored
const ledgerRendered = LEDGER.map(([slug, file, title]) => ({ slug, file, title, ...ledgerPage(slug, file, title) }));
const anchorPage = new Map();
for (const L of ledgerRendered) for (const id of L.ids) if (!anchorPage.has(id)) anchorPage.set(id, L.slug);

// pass 1: numbering + labels
for (const ch of chapters) renderChapter(ch, 1);
// glossary/bib/ledger labels
// pass 2: final
const rendered = chapters.map((ch) => ({ ch, ...renderChapter(ch, 2) }));

// bibliography checks
for (const [k, b] of Object.entries(bib)) {
  for (const f of ["label", "authors", "title", "year", "venue", "verification"]) if (!b[f]) err("bibliography.json", `${k} lacks ${f}`);
  if (!["metadata-verified", "secondary-only", "unverified"].includes(b.verification)) err("bibliography.json", `${k}: bad verification ${b.verification}`);
  if (!citedKeys.has(k)) (process.env.CGT_PARTIAL ? () => {} : warn)("bibliography.json", `entry ${k} is never cited`);
}

// ------------------------------------------------------------------ templates
const NAV = [["index.html", "Home"], ["contents.html", "Contents"], ["lab.html", "Laboratory"], ["theorems.html", "Results"],
  ["ledger/index.html", "Research ledger"], ["sdk.html", "SDK"], ["gaas.html", "GaaS"], ["researcher.html", "Researcher"]];

function page({ title, rel, body, active, description = "", toc = "", bodyClass = "" }) {
  const nav = NAV.map(([u, t]) => `<a href="${rel}${u}"${active === u ? ' aria-current="page"' : ""}>${t}</a>`).join("");
  return `<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description || book.description)}">
<meta name="author" content="${esc(book.author)}">
<link rel="icon" href="${rel}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="${rel}assets/katex/katex.min.css">
<link rel="stylesheet" href="${rel}assets/css/cgt.css">
<script>try{const t=localStorage.getItem("cgt-theme");if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
</head>
<body class="${bodyClass}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="${rel}index.html"><span class="brand-mark" aria-hidden="true">⟦G⟧</span><span class="brand-text"><span class="brand-title">Computational Grammar Theory</span><span class="brand-sub">Abed Kadaan · research program</span></span></a>
  <nav class="site-nav" aria-label="Primary">${nav}</nav>
  <div class="tools">
    <form class="search" role="search" action="${rel}search.html"><label class="vh" for="q">Search the book</label><input id="q" name="q" type="search" placeholder="Search definitions, theorems, chapters…" autocomplete="off" data-rel="${rel}"><div class="search-pop" hidden></div></form>
    <button class="theme-toggle" type="button" aria-label="Toggle light or dark theme"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg></button>
  </div>
</header>
${toc}
<main id="main" class="main">
${body}
</main>
<footer class="site-footer">
  <p><strong>${esc(book.title)}</strong> — ${esc(book.edition)}. Research program formulated by <a href="${rel}researcher.html">${esc(book.author)}</a>, ${esc(book.role)}.</p>
  <p class="status-note">${esc(book.status)} <a href="${rel}status.html">Publication status and limitations</a>.</p>
</footer>
<script src="${rel}assets/js/site.js" defer></script>
</body>
</html>`;
}

function chapterPage({ ch, html, ctx }, i) {
  const prev = rendered[i - 1]?.ch, next = rendered[i + 1]?.ch;
  const kind = ch.appendix ? "Appendix" : "Chapter";
  const tocItems = ctx.toc.filter((t) => t.level >= 2).map((t) => `<li class="toc-l${t.level}"><a href="#${t.id}"><span class="secno">${t.num}</span> ${ctx.mdInline.renderInline(t.text)}</a></li>`).join("");
  const refs = [...ctx.cites].sort((a, b) => bib[a].label.localeCompare(bib[b].label));
  const refList = refs.length ? `<section class="chapter-refs" aria-labelledby="refs-h"><h2 id="refs-h">References cited in this chapter</h2><ol>${refs.map((k) => `<li><a href="../bibliography.html#${k}">${esc(bib[k].label)}</a> ${formatBib(bib[k])}</li>`).join("")}</ol></section>` : "";
  const status = ch.meta.status ? `<p class="chapter-status"><span class="status status-${esc(ch.meta.status)}">${esc(STATUS[ch.meta.status]?.[0] || ch.meta.status)}</span> ${esc(ch.meta.statusnote || "")}</p>` : "";
  if (ch.meta.status && !STATUS[ch.meta.status] && !["draft", "mixed"].includes(ch.meta.status)) err(ch.slug, `bad chapter status ${ch.meta.status}`);
  const body = `<article class="chapter" data-chapter="${ch.number}">
<header class="chapter-opener">
  <p class="chapter-kicker">Part ${esc(ch.part.id)} · ${esc(ch.part.title)}</p>
  <p class="chapter-number">${kind} ${ch.number}</p>
  <h1>${ctx.mdInline.renderInline(ch.meta.title)}</h1>
  ${ch.meta.epigraph ? `<p class="epigraph">${ctx.mdInline.renderInline(ch.meta.epigraph)}</p>` : ""}
  ${status}
</header>
${html}
${refList}
<nav class="pager" aria-label="Chapter navigation">${prev ? `<a class="prev" href="../${prev.url}">← ${prev.appendix ? "Appendix" : "Chapter"} ${prev.number}: ${esc(stripMd(prev.meta.title))}</a>` : "<span></span>"}${next ? `<a class="next" href="../${next.url}">${next.appendix ? "Appendix" : "Chapter"} ${next.number}: ${esc(stripMd(next.meta.title))} →</a>` : ""}</nav>
</article>`;
  const toc = `<aside class="chapter-toc" aria-label="On this page"><p class="toc-title">${kind} ${ch.number}</p><ol>${tocItems}</ol><p class="toc-src"><a href="https://github.com/akadaan310/computationalgrammartheory/blob/main/book/content/chapters/${ch.slug}.md">Source of this chapter</a></p></aside>`;
  return page({ title: `${kind} ${ch.number}. ${stripMd(ch.meta.title)} — Computational Grammar Theory`, rel: "../", body, toc, bodyClass: "has-toc", description: ch.meta.description || "" });
}

const stripMd = (s) => s.replace(/\$([^$]*)\$/g, "$1").replace(/[*_`]/g, "");

function formatBib(b) {
  const doi = b.doi ? ` doi:<a href="https://doi.org/${esc(b.doi)}">${esc(b.doi)}</a>.` : "";
  const url = !b.doi && b.url ? ` <a href="${esc(b.url)}">link</a>.` : "";
  return `${esc(b.authors)} (${esc(b.year)}). <cite>${esc(b.title)}</cite>. ${esc(b.venue)}.${doi}${url}`;
}

// ------------------------------------------------------------------ site pages
function contentsBody(rel) {
  return book.parts.map((p) => `<section class="part"><h2><span class="part-no">Part ${esc(p.id)}</span> ${esc(p.title)}</h2>${p.blurb ? `<p class="part-blurb">${esc(p.blurb)}</p>` : ""}<ol class="chapter-list">${
    rendered.filter((r) => r.ch.part === p).map(({ ch, ctx }) => `<li><a href="${rel}${ch.url}"><span class="cl-no">${ch.appendix ? "Appendix " : ""}${ch.number}</span><span class="cl-title">${ctx.mdInline.renderInline(ch.meta.title)}</span></a>${ch.meta.description ? `<p class="cl-desc">${esc(ch.meta.description)}</p>` : ""}<span class="status status-${esc(ch.meta.status)}">${esc(STATUS[ch.meta.status]?.[0] || ch.meta.status)}</span></li>`).join("")}</ol></section>`).join("\n");
}

function homeBody() {
  const first = rendered[0]?.ch;
  const stats = { chapters: rendered.length, results: formalIndex.filter((f) => ["theorem", "proposition", "lemma", "corollary"].includes(f.kind)).length,
    defs: formalIndex.filter((f) => f.kind === "definition").length, refs: Object.keys(bib).length };
  return `<section class="hero">
  <p class="hero-kicker">A research program and an open book</p>
  <h1 class="hero-title">Can the grammar of a computational structure become part of the machinery that computes over it?</h1>
  <p class="hero-lede">Computational Grammar Theory studies the formal grammars through which data structures expose, constrain, compose and resolve their operations — and asks, with proofs, experiments and counterexamples, <em>exactly when</em> such grammars change what computation costs.</p>
  <p class="hero-author"><span class="author-name">${esc(book.author)}</span><span class="author-role">${esc(book.role)}</span></p>
  <p class="hero-actions"><a class="btn btn-primary" href="${first ? first.url : "contents.html"}">Begin reading: Chapter 1</a><a class="btn" href="contents.html">Table of contents</a><a class="btn" href="lab.html">Open the laboratory</a></p>
</section>
<section class="home-grid">
  <div class="home-card"><h2>The three questions kept apart</h2>
  <ol class="three"><li><strong>Syntax</strong> — which expressions are admissible?</li><li><strong>Semantics</strong> — what do they denote in a structure?</li><li><strong>Execution</strong> — what does it cost to resolve them?</li></ol>
  <p>Every claim in this book is filed under exactly one of these questions, and every cost is stated with its machine model.</p></div>
  <div class="home-card"><h2>What has been established so far</h2>
  <p>${stats.defs} definitions and ${stats.results} proved or cited results across ${stats.chapters} chapters, each with an evidence badge: <span class="status status-proved-here">Proved here</span> <span class="status status-standard">Established</span> <span class="status status-empirical">Empirical</span> <span class="status status-conjecture">Conjecture</span> <span class="status status-rejected">Rejected</span>.</p>
  <p>Negative results are central, not hidden: see the <a href="ledger/counterexamples.html">counterexample ledger</a>.</p></div>
  <div class="home-card"><h2>Run it yourself</h2><p>The <a href="sdk.html">CGT SDK</a> (Python, standard library only) implements every structure and algorithm in the book with explicit cost accounting. The <a href="lab.html">laboratory</a> runs real operations in your browser, validated against the SDK.</p></div>
</section>
<section class="home-start"><h2>Contents at a glance</h2>${contentsBody("")}</section>`;
}

function theoremsBody() {
  const kinds = ["definition", "theorem", "proposition", "lemma", "corollary", "conjecture", "observation", "algorithm"];
  const rows = formalIndex.map((f) => `<tr data-kind="${f.kind}" data-status="${esc(f.status)}"><td><a href="${f.url}">${esc(f.label)}</a></td><td>${esc(f.title)}</td><td>${f.status ? `<span class="status status-${esc(f.status)}">${esc(STATUS[f.status]?.[0] || f.status)}</span>` : ""}</td><td>${f.ledger.split(",").filter(Boolean).map((L) => `<a class="ledger-id" href="${ledgerUrl(L.trim())}">${esc(L.trim())}</a>`).join(" ")}</td><td>${esc(f.chapterTitle)}</td></tr>`).join("");
  const counts = kinds.map((k) => `${formalIndex.filter((f) => f.kind === k).length} ${k}${formalIndex.filter((f) => f.kind === k).length === 1 ? "" : "s"}`).join(" · ");
  return `<h1>Index of definitions and results</h1><p class="lede">${counts}. Status badges distinguish results proved in this book (self-checked, not externally reviewed) from established results of the literature, empirical observations, conjectures and rejected hypotheses.</p>
<div class="filter" role="group" aria-label="Filter by kind"><button data-filter="all" aria-pressed="true">All</button>${kinds.map((k) => `<button data-filter="${k}" aria-pressed="false">${k[0].toUpperCase() + k.slice(1)}s</button>`).join("")}</div>
<div class="table-wrap"><table class="index-table"><thead><tr><th>Item</th><th>Title</th><th>Status</th><th>Ledger</th><th>Chapter</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function glossaryBody() {
  const items = [...glossary].sort((a, b) => a.term.localeCompare(b.term)).map((g) => {
    searchDocs.push({ t: g.term, u: `glossary.html#${slugify(g.term)}`, k: "glossary", c: "Glossary" });
    const see = g.see ? ` <a class="xref" href="${registry.get(g.see)?.url || "#"}">${esc(registry.get(g.see)?.title || "")}</a>` : "";
    if (g.see && !registry.get(g.see)) err("glossary.json", `${g.term}: unresolved see ${g.see}`);
    return `<dt id="${slugify(g.term)}">${esc(g.term)}${g.aliases ? ` <span class="aliases">(${esc(g.aliases.join(", "))})</span>` : ""}</dt><dd>${renderInlineStandalone(g.definition)}${see ? ` See${see}.` : ""}</dd>`;
  }).join("");
  return `<h1>Glossary</h1><p class="lede">Persistent definitions of the vocabulary used throughout the book. Terms link to the place where they are defined formally.</p><dl class="glossary">${items}</dl>`;
}

function renderInlineStandalone(s) {
  const ctx = { slug: "glossary", number: "G", url: "glossary.html", rel: "", title: "Glossary", pass: 2, counters: { eq: 0, sec: 0, sub: 0 }, toc: [], envStack: [], cites: new Set(), demos: new Set(), offset: 0 };
  const md = makeMd(ctx); ctx.mdInline = md;
  return md.renderInline(s);
}

function bibliographyBody() {
  const keys = Object.keys(bib).sort((a, b) => bib[a].label.localeCompare(bib[b].label));
  const V = { "metadata-verified": "Metadata verified", "secondary-only": "Secondary sources only", unverified: "Unverified" };
  const items = keys.map((k) => {
    const b = bib[k];
    searchDocs.push({ t: `${b.label} — ${b.title}`, u: `bibliography.html#${k}`, k: "reference", c: "Bibliography" });
    return `<li id="${k}"><span class="bib-label">${esc(b.label)}</span> ${formatBib(b)} <span class="verif verif-${b.verification}" title="${esc(b.verification_note || "")}">${V[b.verification]}</span>${b.consulted ? ` <span class="verif verif-consulted">${esc(b.consulted)}</span>` : ""}${b.note ? `<span class="bib-note">${esc(b.note)}</span>` : ""}</li>`;
  }).join("");
  const counts = Object.entries(V).map(([k, v]) => `${Object.values(bib).filter((b) => b.verification === k).length} ${v.toLowerCase()}`).join(", ");
  return `<h1>Bibliography</h1><p class="lede">${keys.length} entries: ${counts}. <strong>Metadata verified</strong> means authors, title, venue and year were checked against publisher, DBLP or institutional records; it does <em>not</em> mean the full text was read. Each entry states what was consulted.</p><ol class="bibliography">${items}</ol>`;
}

// ------------------------------------------------------------------ ledger pages (render the canonical ledger markdown)


function ledgerPage(slug, file, title) {
  const md = new MarkdownIt({ html: false, typographer: false });
  let html = md.render(fs.readFileSync(path.join(REPO, file), "utf8"));
  const seen = new Set();
  // anchor every ledger identifier at its first defining occurrence (heading or table row)
  html = html.replace(/<(h[2-4])>((?:(?!<\/h[2-4]>).)*?)(CGT-[A-Z]+-\d+[a-z]?)/g, (m, tag, pre, id) => {
    if (seen.has(id)) return m; seen.add(id); return `<${tag} id="${id}">${pre}${id}`;
  });
  html = html.replace(/<tr>\n<td>(?:<strong>)?(CGT-[A-Z]+-\d+[a-z]?|E-\d+|B-\d+)/g, (m, id) => {
    if (seen.has(id)) return m; seen.add(id); return m.replace("<tr>", `<tr id="${id}">`);
  });
  html = html.replace(/<p><strong>(CGT-[A-Z]+-\d+[a-z]?)/g, (m, id) => { if (seen.has(id)) return m; seen.add(id); return `<p id="${id}"><strong>${id}`; });
  html = html.replace(/<li><strong>(CGT-[A-Z]+-\d+[a-z]?)/g, (m, id) => { if (seen.has(id)) return m; seen.add(id); return `<li id="${id}"><strong>${id}`; });
  html = html.replace(/<table>/g, '<div class="table-wrap"><table>').replace(/<\/table>/g, "</table></div>");
  return { html: `<p class="ledger-crumb"><a href="index.html">Research ledger</a> / ${esc(title)} · canonical source: <code>${esc(file)}</code></p><div class="ledger-doc">${html}</div>`, ids: seen };
}

// ------------------------------------------------------------------ SDK / GaaS / researcher / status / search / lab / print
function sdkBody() {
  if (!sdkRef) { err("data", "sdk_reference.json missing: run tools/export_data.py"); return ""; }
  const mods = sdkRef.modules.map((m) => `<section class="api-module" id="${esc(m.name)}"><h2><code>${esc(m.name)}</code></h2>${m.doc ? `<div class="api-doc">${esc(m.doc).replace(/\n\n/g, "</p><p>").replace(/^/, "<p>")}</p></div>` : ""}${m.members.map((x) => `<div class="api-member" id="${esc(m.name + "." + x.name)}"><h3><code>${esc(x.name)}${esc(x.signature || "")}</code> <span class="api-kind">${esc(x.kind)}</span></h3>${x.doc ? `<pre class="api-docstring">${esc(x.doc)}</pre>` : ""}${(x.moves || []).length ? `<p class="api-moves">Move signature: ${x.moves.map((mv) => `<code>${esc(mv)}</code>`).join(" ")}</p>` : ""}</div>`).join("")}</section>`).join("");
  sdkRef.modules.forEach((m) => m.members.forEach((x) => searchDocs.push({ t: `${m.name}.${x.name}`, u: `sdk.html#${m.name}.${x.name}`, k: "api", c: "SDK reference" })));
  return `<h1>The CGT SDK — reference</h1><p class="lede"><code>cgtsdk</code> ${esc(sdkRef.version)} · Python ≥ 3.10 · standard library only · ${esc(String(sdkRef.tests))} tests. Generated from the package's docstrings by <code>tools/export_data.py</code>; the tutorial is  <a href="${rendered.find((r) => r.ch.slug.includes("sdk"))?.ch.url || "contents.html"}">the SDK chapter</a>.</p>
<pre class="install"><code>git clone https://github.com/akadaan310/computationalgrammartheory
cd computationalgrammartheory/sdk &amp;&amp; python3 -m pip install -e .   # or: export PYTHONPATH=sdk/src
python3 -m unittest discover -s tests</code></pre>${mods}`;
}

function gaasBody() {
  if (!gaasCaps) { err("data", "gaas_capabilities.json missing"); return ""; }
  const s = Object.entries(gaasCaps.structures).map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(v.version)}</td><td>${esc(v.description)}</td><td>${v.moves ? v.moves.map((m) => `<code>${esc(m)}</code>`).join(" ") : "edge labels + <code>at(v)</code>, <code>here</code>"}</td></tr>`).join("");
  const a = Object.entries(gaasCaps.algorithms).map(([k, v]) => `<tr><td><code>${esc(k)}</code></td><td>${v.exact ? "exact" : "approximate (certified bound)"}</td><td>${esc(v.complexity)}</td><td>${esc(v.description)}</td></tr>`).join("");
  const lim = Object.entries(gaasCaps.limits).map(([k, v]) => `<li><code>${esc(k)}</code> ≤ ${esc(v)}</li>`).join("");
  return `<h1>Grammar as a Service — contract <code>${esc(gaasCaps.contract)}</code></h1>
<p class="lede">A request names a versioned grammar (or an algorithm with declared capabilities), an operation expression, and limits; the response carries values, a layered rejection if any (syntax · semantics · execution), a cost report and provenance hashes. The reference implementation is a pure function you can call in-process — no account, key or network is needed for anything in the curriculum. Design rationale:  <a href="${rendered.find((r) => r.ch.slug.includes("gaas"))?.ch.url || "contents.html"}">the GaaS chapter</a>.</p>
<h2>Structures</h2><div class="table-wrap"><table><thead><tr><th>Name</th><th>Version</th><th>Description</th><th>Moves</th></tr></thead><tbody>${s}</tbody></table></div>
<h2>Algorithms</h2><div class="table-wrap"><table><thead><tr><th>Name</th><th>Exactness</th><th>Declared cost</th><th>Description</th></tr></thead><tbody>${a}</tbody></table></div>
<h2>Hard limits</h2><ul>${lim}</ul><p>A request may lower any limit and never raise one.</p>
<h2>Example</h2><pre><code>${esc(JSON.stringify({ contract: gaasCaps.contract, grammar: { structure: "array", version: "1" }, init: { values: [5, 3, 8] }, expression: "get(2); set(0, 9); get(0)" }, null, 1))}</code></pre>
<pre><code>${esc(JSON.stringify(gaasCaps.example_response, null, 1))}</code></pre>`;
}

function readPage(name) {
  const p = path.join(CONTENT, "pages", `${name}.md`);
  const ctx = { slug: name, number: "", url: `${name}.html`, rel: "", title: name, pass: 2, counters: { eq: 0, sec: 0, sub: 0, thm: 0, exr: 0, ex: 0, alg: 0 }, toc: [], envStack: [], cites: new Set(), demos: new Set(), offset: 0 };
  const md = makeMd(ctx); ctx.mdInline = md;
  return md.render(fs.readFileSync(p, "utf8"));
}

// ------------------------------------------------------------------ write
function write(rel, html) {
  if (CHECK_ONLY) return;
  const out = path.join(DIST, rel);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, html);
}
function copyDir(src, dst, filter = () => true) {
  if (CHECK_ONLY) return;
  fs.mkdirSync(dst, { recursive: true });
  for (const f of fs.readdirSync(src)) {
    const s = path.join(src, f), d = path.join(dst, f);
    if (fs.statSync(s).isDirectory()) copyDir(s, d, filter);
    else if (filter(f)) fs.copyFileSync(s, d);
  }
}

if (!CHECK_ONLY) fs.rmSync(DIST, { recursive: true, force: true });
rendered.forEach((r, i) => write(r.ch.url, chapterPage(r, i)));
write("index.html", page({ title: `${book.title} — ${book.subtitle}`, rel: "", body: homeBody(), active: "index.html", bodyClass: "home" }));
write("contents.html", page({ title: `Contents — ${book.title}`, rel: "", body: `<h1>Contents</h1><p class="lede">${esc(book.description)}</p>${contentsBody("")}`, active: "contents.html" }));
write("theorems.html", page({ title: `Results index — ${book.title}`, rel: "", body: theoremsBody(), active: "theorems.html" }));
write("glossary.html", page({ title: `Glossary — ${book.title}`, rel: "", body: glossaryBody() }));
write("bibliography.html", page({ title: `Bibliography — ${book.title}`, rel: "", body: bibliographyBody() }));
write("sdk.html", page({ title: `SDK reference — ${book.title}`, rel: "", body: sdkBody(), active: "sdk.html" }));
write("gaas.html", page({ title: `Grammar as a Service — ${book.title}`, rel: "", body: gaasBody(), active: "gaas.html" }));
for (const name of ["researcher", "status", "lab", "math-tests"]) {
  const active = { researcher: "researcher.html", lab: "lab.html" }[name];
  write(`${name}.html`, page({ title: `${{ researcher: "Abed Kadaan", status: "Publication status", lab: "Laboratory", "math-tests": "Mathematical typography tests" }[name]} — ${book.title}`, rel: "", body: readPage(name), active, bodyClass: name === "lab" ? "lab-page" : "" }));
}
write("search.html", page({ title: `Search — ${book.title}`, rel: "", body: `<h1>Search</h1><div id="search-results" aria-live="polite"><noscript>Search requires JavaScript. Use the <a href="contents.html">contents</a>, <a href="theorems.html">results index</a> or <a href="glossary.html">glossary</a>.</noscript></div>` }));

// ledger
const ledgerIndex = [];
const allLedgerAnchors = new Set();
for (const { slug, file, title, html, ids } of ledgerRendered) {
  ids.forEach((x) => allLedgerAnchors.add(`${slug}#${x}`));
  ids.forEach((x) => searchDocs.push({ t: x, u: `ledger/${slug}.html#${x}`, k: "ledger", c: title }));
  ledgerIndex.push([slug, title, file]);
  write(`ledger/${slug}.html`, page({ title: `${title} — Research ledger`, rel: "../", body: html, active: "ledger/index.html", bodyClass: "ledger" }));
}
write("ledger/index.html", page({ title: "Research ledger — Computational Grammar Theory", rel: "../", active: "ledger/index.html",
  body: `<h1>Research ledger</h1><p class="lede">The canonical scientific record behind the book, rendered directly from the repository's ledger files — the book cites it, it does not duplicate it. Every identifier (CGT-DEF, -THM, -PROP, -OBS, -NEG, -OPEN, …) has a stable anchor.</p><ul class="ledger-list">${ledgerIndex.map(([s, t, f]) => `<li><a href="${s}.html">${esc(t)}</a> <code>${esc(f)}</code></li>`).join("")}</ul>` }));
// every ledger id used in the book must be anchored somewhere
for (const L of usedLedger) {
  const page = ledgerUrl(L).split("/")[1].replace(".html", "");
  if (![...allLedgerAnchors].some((a) => a.endsWith(`#${L}`))) err("ledger", `ledger id ${L} is cited in the book but has no anchor in the ledger pages`);
}

// print edition (single page) for PDF export
const printBody = `<section class="print-title"><h1>${esc(book.title)}</h1><p class="subtitle">${esc(book.subtitle)}</p><p class="author">${esc(book.author)}<br>${esc(book.role)}</p><p>${esc(book.edition)}</p><p class="status-note">${esc(book.status)}</p></section>
<nav class="print-toc"><h2>Contents</h2>${contentsBody("#").replace(/href="#chapters\/([\w-]+)\.html"/g, 'href="#ch-$1"')}</nav>
${rendered.map(({ ch, html, ctx }) => `<article class="chapter print-chapter" id="ch-${ch.slug}"><header class="chapter-opener"><p class="chapter-number">${ch.appendix ? "Appendix" : "Chapter"} ${ch.number}</p><h1>${ctx.mdInline.renderInline(ch.meta.title)}</h1></header>${html.replace(/href="\.\.\/chapters\/([\w-]+)\.html#/g, 'href="#').replace(/href="\.\.\/chapters\/([\w-]+)\.html"/g, 'href="#ch-$1"').replace(/href="\.\.\//g, 'href="')}</article>`).join("\n")}
<section class="print-bib"><h1>Bibliography</h1>${bibliographyBody().replace(/^<h1>Bibliography<\/h1>/, "")}</section>`;
write("print.html", page({ title: `${book.title} — print edition`, rel: "", body: printBody, bodyClass: "print-edition" }));

// search index
write("assets/search-index.json", JSON.stringify(searchDocs));
// assets
copyDir(path.join(ROOT, "site", "assets"), path.join(DIST, "assets"));
copyDir(path.join(ROOT, "node_modules", "katex", "dist"), path.join(DIST, "assets", "katex"), (f) => f === "katex.min.css" || f.endsWith(".woff2"));
for (const [pkg, fam] of [["source-serif-4", "source-serif-4"], ["ibm-plex-sans", "ibm-plex-sans"], ["jetbrains-mono", "jetbrains-mono"]]) {
  copyDir(path.join(ROOT, "node_modules", "@fontsource", pkg, "files"), path.join(DIST, "assets", "fonts"),
    (f) => /-(latin|latin-ext)-(400|600|700)-(normal|italic)\.woff2$/.test(f));
}
if (!CHECK_ONLY) {
  for (const n of ["lab_fixtures.json", "experiments.json"]) {
    if (fs.existsSync(path.join(dataDir, n))) fs.copyFileSync(path.join(dataDir, n), path.join(DIST, "assets", n));
  }
  fs.writeFileSync(path.join(DIST, ".nojekyll"), "");
}

// demos used in chapters must exist in lab.js
const labSrc = fs.readFileSync(path.join(ROOT, "site", "assets", "js", "lab.js"), "utf8");
for (const r of rendered) for (const d of r.ctx.demos) if (!labSrc.includes(`"${d}"`)) err(r.ch.slug, `demo ${d} is not implemented in lab.js`);

// ------------------------------------------------------------------ report
for (const w of warnings) console.warn("warning:", w);
if (errors.length) {
  for (const e of errors) console.error("ERROR:", e);
  console.error(`\n${errors.length} integrity error(s); build ${CHECK_ONLY ? "check" : ""} FAILED.`);
  process.exit(1);
}
console.log(`ok: ${rendered.length} chapters, ${formalIndex.length} formal items, ${registry.size} labels, ${citedKeys.size}/${Object.keys(bib).length} references cited, ${searchDocs.length} search entries${CHECK_ONLY ? " (check only)" : " -> dist/"}`);
