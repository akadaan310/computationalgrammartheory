// lab.js — interactive laboratory widgets.  Every number displayed here is
// computed live by cgt-core.js, whose functions are checked against the
// Python SDK by `npm test`.  Nothing is pre-recorded except where a widget
// says it shows stored experiment results (and then it names the file).
import * as core from "./cgt-core.js";

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (x, d = 4) => (Math.abs(x) < 1e-3 && x !== 0 ? x.toExponential(2) : Number(x).toFixed(d));
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const costLine = (c) => Object.entries(c.snapshot()).map(([k, v]) => `${k} ${v}`).join(" · ") || "—";
function bars(rows, max) {
  const m = max ?? Math.max(1, ...rows.map((r) => r[1]));
  return rows.map(([label, v, cls = ""], i) => `<div class="bar-row"><span>${esc(label)}</span><span class="bar ${cls}" style="width:${Math.max(0.3, 100 * v / m)}%"></span><span>${typeof v === "number" ? (Number.isInteger(v) ? v : fmt(v)) : v}</span></div>`).join("");
}

const WIDGETS = {};
export function mount(el) {
  const name = el.dataset.demo;
  const w = WIDGETS[name];
  if (!w) { el.insertAdjacentHTML("beforeend", `<p class="lab-note">Unknown demo “${esc(name)}”.</p>`); return; }
  const host = document.createElement("div");
  host.className = "lab-panel";
  el.appendChild(host);
  w(host);
  el.classList.add("ready");
}

// ===================================================================== arrays vs lists
WIDGETS["array-vs-list"] = (host) => {
  host.innerHTML = `
  <div class="lab-row"><label>n <input type="number" min="1" max="64" value="16" data-k="n" style="width:5rem"></label>
  <label>operation <select data-k="op"><option>get</option><option>set</option><option>insert</option><option>delete</option></select></label>
  <label>index i <input type="number" min="0" value="11" data-k="i" style="width:5rem"></label>
  <button data-k="run">Execute on both</button></div>
  <div class="lab-cmp">
    <div class="lab-card"><h4>Array — address arithmetic</h4><div class="cells" data-k="a"></div><div class="big-number" data-k="ac"></div><div class="lab-note" data-k="acl"></div></div>
    <div class="lab-card"><h4>Linked list — pointer walk</h4><div class="cells" data-k="l"></div><div class="big-number" data-k="lc"></div><div class="lab-note" data-k="lcl"></div></div>
  </div>
  <div><p class="lab-note">Cost of <code>get(i)</code> for every i (counted steps):</p><div data-k="sweep"></div></div>
  <div class="lab-out" aria-live="polite" data-k="trace"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const n = Math.max(1, Math.min(64, +$("n").value)), i = +$("i").value, op = $("op").value;
    const vals = Array.from({ length: n }, (_, k) => 10 * k);
    const A = new core.ArrayStructure(vals), L = new core.LinkedListStructure(vals);
    const args = op === "set" || op === "insert" ? [i, 99] : [i];
    const ca = new core.Cost(), cl = new core.Cost();
    let out = [];
    for (const [S, c, name] of [[A, ca, "array"], [L, cl, "linked list"]]) {
      try { const v = S.apply(op, args, c); out.push(`${name}: ${op}(${args.join(", ")}) = ${v ?? "—"}   [${costLine(c)}]`); }
      catch (e) { out.push(`${name}: ${op}(${args.join(", ")}) is UNDEFINED (semantic layer): ${e.message}   [${costLine(c)}]`); }
      out.push(...c.trace.map(([cat, note]) => `   ${cat}: ${note}`));
    }
    const cells = (k, walk) => vals.map((v, j) => `<span class="cell ${j === k ? "hit" : walk && j < k ? "walk" : ""}"><small>${j}</small>${v}</span>`).join("");
    $("a").innerHTML = cells(i, false); $("l").innerHTML = cells(i, true);
    $("ac").textContent = ca.total; $("lc").textContent = cl.total;
    $("acl").textContent = costLine(ca); $("lcl").textContent = costLine(cl);
    $("trace").textContent = out.join("\n");
    const rows = [];
    for (let k = 0; k < n; k += Math.max(1, Math.floor(n / 16))) {
      const c1 = new core.Cost(), c2 = new core.Cost();
      new core.ArrayStructure(vals).apply("get", [k], c1); new core.LinkedListStructure(vals).apply("get", [k], c2);
      rows.push([`array get(${k})`, c1.total], [`list get(${k})`, c2.total, "b2"]);
    }
    $("sweep").innerHTML = bars(rows);
  }
  $("run").addEventListener("click", run);
  host.querySelectorAll("input,select").forEach((x) => x.addEventListener("change", run));
  run();
};

// ===================================================================== dynamic array doubling
WIDGETS["dynamic-array"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>append how many elements <input type="number" min="1" max="2000" value="100" data-k="m" style="width:6rem"></label><button data-k="run">Append</button></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Total counted cost</h4><div class="big-number" data-k="tot"></div><div class="lab-note" data-k="b"></div></div>
  <div class="lab-card"><h4>Reallocations</h4><div class="big-number" data-k="re"></div><div class="lab-note">capacities 1, 2, 4, …</div></div></div>
  <div data-k="hist"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const m = Math.max(1, Math.min(2000, +$("m").value));
    const A = new core.ArrayStructure([]); const c = new core.Cost(); let re = 0; const spikes = [];
    for (let k = 0; k < m; k++) { const before = c.total; const cap = A.capacity; A.apply("append", [k], c); if (A.capacity !== cap) re++; spikes.push(c.total - before); }
    $("tot").textContent = c.total; $("re").textContent = re;
    $("b").textContent = `${costLine(c)} — amortised ${fmt(c.total / m, 2)} per append (bound: < 9 per append under this cost model, proved in Chapter 2)`;
    const show = spikes.map((v, k) => [k, v]).filter(([k, v]) => v > 1 || k < 3).slice(-12);
    $("hist").innerHTML = `<p class="lab-note">Appends that triggered a reallocation (cost = copy + allocate):</p>` + bars(show.map(([k, v]) => [`append #${k + 1}`, v, v > 1 ? "b2" : ""]));
  }
  $("run").addEventListener("click", run); run();
};

// ===================================================================== tree addresses: pointer vs heap
function treeSVG(n, path, cur) {
  const h = Math.floor(Math.log2(n)); const W = 640, H = 46 * (h + 1) + 20;
  const pos = (v) => { const d = Math.floor(Math.log2(v)); const i = v - 2 ** d; const span = W / 2 ** d; return [span * (i + 0.5), 22 + 46 * d]; };
  let s = `<svg class="lab-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Complete binary tree with ${n} nodes; highlighted path to the target address">`;
  const on = new Set(path);
  for (let v = 2; v <= n; v++) { const [x1, y1] = pos(v >> 1), [x2, y2] = pos(v); s += `<line class="edge ${on.has(v) && on.has(v >> 1) ? "on" : ""}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`; }
  for (let v = 1; v <= n; v++) { const [x, y] = pos(v); s += `<circle class="node ${v === cur ? "cur" : on.has(v) ? "on" : ""}" cx="${x}" cy="${y}" r="${n > 63 ? 4 : 9}"/>`; if (n <= 63) s += `<text x="${x}" y="${y + 3.5}" text-anchor="middle" style="font-size:8px">${v}</text>`; }
  return s + "</svg>";
}
WIDGETS["tree-address"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>nodes n <input type="number" min="1" max="127" value="31" data-k="n" style="width:5rem"></label>
  <label>address (word over 0 = L, 1 = R) <input data-k="a" value="0110" style="width:9rem"></label><button data-k="run">goto + read</button></div>
  <div data-k="svg"></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Pointer representation</h4><div class="big-number" data-k="pc"></div><div class="lab-note" data-k="pl"></div></div>
  <div class="lab-card"><h4>Heap numeration</h4><p class="lab-note" style="margin:0">ν(w) = int("1"·w, 2)</p><div class="big-number" data-k="hc"></div><div class="lab-note" data-k="hl"></div></div></div>
  <div class="lab-out" aria-live="polite" data-k="out"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const n = Math.max(1, Math.min(127, +$("n").value)); const a = $("a").value.trim();
    const res = [];
    for (const rep of ["pointer", "heap"]) {
      const t = new core.CompleteTree(n, rep), c = new core.Cost();
      try { t.goto(a, c); const v = t.read(c); res.push([rep, c, `label ${v}`]); } catch (e) { res.push([rep, c, `undefined: ${e.message}`]); }
    }
    const nu = /^[01]*$/.test(a) ? parseInt("1" + a, 2) : NaN;
    const path = []; if (!isNaN(nu)) for (let v = nu; v >= 1; v = v >> 1) path.push(v);
    $("svg").innerHTML = treeSVG(n, path.filter((v) => v <= n), nu <= n ? nu : -1);
    $("pc").textContent = res[0][1].total; $("pl").textContent = `${costLine(res[0][1])} — ${res[0][2]}`;
    $("hc").textContent = res[1][1].total; $("hl").textContent = `${costLine(res[1][1])} — ${res[1][2]}`;
    const h = Math.floor(Math.log2(n));
    $("out").textContent = `ν("${a}") = ${isNaN(nu) ? "invalid" : nu}   (binary ${isNaN(nu) ? "" : nu.toString(2)})\nparent = ⌊ν/2⌋, children = 2ν, 2ν+1 — no pointers stored.\nheight h = ${h}; address space 2^(h+1) − 1 = ${2 ** (h + 1) - 1}; density n / (2^(h+1) − 1) = ${fmt(n / (2 ** (h + 1) - 1), 3)}  (CGT-THM-003)`;
  }
  $("run").addEventListener("click", run); host.querySelectorAll("input").forEach((x) => x.addEventListener("change", run)); run();
};

// ===================================================================== compiled words (THM-006)
WIDGETS["compiled-words"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>word over L, R, U <input data-k="w" value="LRLUURRUL" style="width:12rem"></label><label>n <input type="number" data-k="n" value="100" min="1" max="100000" style="width:6rem"></label><button data-k="run">Compile</button></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Compiled form</h4><div class="lab-out" data-k="cf"></div></div>
  <div class="lab-card"><h4>Cost per application</h4><div data-k="cost"></div></div></div>
  <p class="lab-note">Results for x = 1 … min(n, 40) (compiled map vs step-by-step walk; mismatches would be flagged in red — none are possible if CGT-THM-006 holds, and the build's tests check this):</p>
  <div class="lab-out" aria-live="polite" data-k="tab"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const w = $("w").value.replace(/[^LRU]/g, ""); const n = Math.max(1, Math.min(100000, +$("n").value));
    const cc = new core.Cost(); const f = core.compileHeapWord(w, n, cc);
    $("cf").textContent = `f(x) = ((x >> ${f.k}) << ${f.j}) | ${f.c}\ndefined iff ${f.lo} ≤ x ≤ ${f.hi}${f.hi < f.lo ? "   (nowhere defined)" : ""}\ncompile cost: ${cc.total} word operations (4 per letter)`;
    $("cost").innerHTML = bars([["compiled", 5], ["walk (≤)", 2 * w.length, "b2"]]) + `<p class="lab-note">Compiled: 2 comparisons + 3 arithmetic operations, independent of |w| = ${w.length}. Walk: one step and one bounds check per letter until it falls off the tree.</p>`;
    const rows = []; let bad = 0;
    for (let x = 1; x <= Math.min(n, 40); x++) { const a = f.apply(x), b = core.heapWalk(w, x, n); if (a !== b) bad++; rows.push(`x=${String(x).padStart(3)}  compiled ${String(a ?? "undef").padStart(6)}   walk ${String(b ?? "undef").padStart(6)}${a !== b ? "   MISMATCH" : ""}`); }
    $("tab").textContent = rows.join("\n") + (bad ? `\n${bad} mismatches!` : "\nall equal");
  }
  $("run").addEventListener("click", run); host.querySelectorAll("input").forEach((x) => x.addEventListener("change", run)); run();
};

// ===================================================================== regex -> DFA
WIDGETS["regex-dfa"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>regular expression over move symbols <input data-k="rx" value="(a b)* (a | ε)" style="width:16rem"></label><label>word <input data-k="w" value="a b a" style="width:8rem"></label><button data-k="run">Compile and test</button></div><div class="lab-out" aria-live="polite" data-k="out"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    try {
      const d = core.compileRegex($("rx").value);
      const rows = [`minimal DFA: ${d.size} state(s), alphabet {${d.alphabet.join(", ")}}, start ${d.start}, accepting {${[...d.accept].join(", ")}}`, "", "state | " + d.alphabet.map((a) => a.padEnd(4)).join(" ")];
      for (const q of d.states) rows.push(`${String(q).padEnd(5)} | ` + d.alphabet.map((a) => String(d.step(q, a) ?? "—").padEnd(4)).join(" ") + (d.accept.has(q) ? "   (accepting)" : ""));
      const w = $("w").value.trim() ? $("w").value.trim().split(/\s+/) : [];
      rows.push("", `word “${w.join(" ") || "ε"}” is ${d.accepts(w) ? "ADMISSIBLE (in ℒ)" : "NOT admissible"}`);
      $("out").textContent = rows.join("\n");
    } catch (e) { $("out").textContent = "syntax error: " + e.message; }
  }
  $("run").addEventListener("click", run); run();
};

// ===================================================================== product construction (THM-001)
const PRESET_EDGES = [[0, "a", 1], [1, "b", 2], [2, "a", 3], [3, "b", 0], [0, "c", 4], [4, "a", 1], [2, "c", 4], [1, "a", 1], [3, "a", 5], [5, "b", 6], [6, "c", 0], [5, "c", 7], [7, "a", 6]];
function graphSVG(n, edges, onV, cur) {
  const W = 520, H = 300, R = 115; const pos = (i) => [W / 2 + R * 1.6 * Math.cos(2 * Math.PI * i / n - Math.PI / 2), H / 2 + R * Math.sin(2 * Math.PI * i / n - Math.PI / 2)];
  let s = `<svg class="lab-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Edge-labelled graph; reachable vertices highlighted"><defs><marker id="arr" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>`;
  for (const [u, a, v] of edges) {
    const [x1, y1] = pos(u), [x2, y2] = pos(v);
    if (u === v) { s += `<circle class="edge" cx="${x1}" cy="${y1 - 18}" r="10"/><text class="lbl" x="${x1 + 12}" y="${y1 - 26}">${a}</text>`; continue; }
    const mx = (x1 + x2) / 2 + (y2 - y1) * 0.22, my = (y1 + y2) / 2 - (x2 - x1) * 0.22;
    s += `<path class="edge" d="M${x1},${y1} Q${mx},${my} ${x2},${y2}" marker-end="url(#arr)"/><text class="lbl" x="${mx}" y="${my}">${a}</text>`;
  }
  for (let i = 0; i < n; i++) { const [x, y] = pos(i); s += `<circle class="node ${i === cur ? "cur" : onV.has(i) ? "on" : ""}" cx="${x}" cy="${y}" r="13"/><text x="${x}" y="${y + 4}" text-anchor="middle">${i}</text>`; }
  return s + "</svg>";
}
WIDGETS["product"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>admissibility language ℒ <input data-k="rx" value="(a b)*" style="width:12rem"></label><label>source <input type="number" data-k="s" value="0" min="0" max="7" style="width:4rem"></label><button data-k="run">Resolve ⟦ℒ⟧(source)</button></div>
  <div data-k="svg"></div><div class="lab-cmp"><div class="lab-card"><h4>Constrained (product A × Q)</h4><div class="big-number" data-k="pe"></div><div class="lab-note" data-k="pr"></div></div><div class="lab-card"><h4>Unconstrained reachability</h4><div class="big-number" data-k="ue"></div><div class="lab-note" data-k="ur"></div></div></div>
  <div class="lab-out" aria-live="polite" data-k="out"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const n = 8, s = Math.max(0, Math.min(7, +$("s").value));
    try {
      const d = core.compileRegex($("rx").value); const c = new core.Cost();
      const r = core.productReach(n, PRESET_EDGES, d, s, c);
      const u = core.productReach(n, PRESET_EDGES, core.DFA.universal(["a", "b", "c"]), s);
      $("svg").innerHTML = graphSVG(n, PRESET_EDGES, new Set(r.reach), s);
      $("pe").textContent = r.explored; $("pr").textContent = `product states explored (≤ |Q|·n = ${d.size}·${n} = ${d.size * n}); answer {${r.reach.join(", ")}}`;
      $("ue").textContent = u.explored; $("ur").textContent = `vertices explored; answer {${u.reach.join(", ")}} — differs from ⟦ℒ⟧ wherever the constraint matters`;
      $("out").textContent = `minimal DFA for ℒ has |Q| = ${d.size}\nBFS order over (vertex, state): ${r.order.map(([y, q]) => `(${y},${q})`).join(" ")}\n${costLine(c)}`;
    } catch (e) { $("out").textContent = "syntax error: " + e.message; }
  }
  $("run").addEventListener("click", run); run();
};

// ===================================================================== PageRank
const PR_PRESETS = {
  "small web (with a dangling page)": [[1, 2], [2], [0, 3], [], [0, 3, 2]],
  "cycle of 6": [[1], [2], [3], [4], [5], [0]],
  "star into hub": [[0], [0], [0], [0], [0], [0]].map((a, i) => (i === 0 ? [1, 2, 3, 4, 5] : [0])),
  "two communities + bridge": [[1, 2], [0, 2], [0, 1, 3], [4, 5], [3, 5], [3, 4]],
};
WIDGETS["pagerank"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>graph <select data-k="g">${Object.keys(PR_PRESETS).map((k) => `<option>${esc(k)}</option>`).join("")}</select></label>
  <label>damping α <input type="range" min="0" max="0.99" step="0.01" value="0.85" data-k="a"></label><span data-k="av">0.85</span>
  <button data-k="step">One iteration</button><button class="secondary" data-k="solve">Iterate to tol 1e-10</button><button class="secondary" data-k="reset">Reset</button></div>
  <div class="lab-row"><label style="width:100%">edges (one line per vertex: out-neighbours) <textarea data-k="adj"></textarea></label></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Scores x<sub>k</sub></h4><div data-k="bars"></div></div><div class="lab-card"><h4>Certification (CGT-THM-008)</h4><div data-k="cert"></div></div></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  let adj, x, k, hist;
  const parse = () => $("adj").value.split("\n").map((l) => l.split(/[\s,]+/).filter(Boolean).map(Number));
  function load() { adj = PR_PRESETS[$("g").value]; $("adj").value = adj.map((a) => a.join(" ")).join("\n"); reset(); }
  function reset() { adj = parse(); const n = adj.length; if (adj.some((a) => a.some((v) => !(v >= 0 && v < n)))) { $("cert").textContent = "invalid edge list"; return; } x = Array(n).fill(1 / n); k = 0; hist = []; draw(); }
  function step() {
    const n = adj.length, alpha = +$("a").value, out = adj.map((a) => a.length);
    let dang = 0; for (let u = 0; u < n; u++) if (!out[u]) dang += x[u];
    const y = Array(n).fill((1 - alpha + alpha * dang) / n);
    for (let u = 0; u < n; u++) if (out[u]) for (const w of adj[u]) y[w] += alpha * x[u] / out[u];
    const r = y.reduce((s, yi, i) => s + Math.abs(yi - x[i]), 0); x = y; k++; hist.push(r); draw();
  }
  function draw() {
    const alpha = +$("a").value; $("av").textContent = alpha.toFixed(2);
    const r = hist.at(-1);
    $("bars").innerHTML = bars(x.map((v, i) => [`page ${i}${adj[i]?.length ? "" : " (dangling)"}`, v, i % 2 ? "b3" : ""]), Math.max(...x)) + `<p class="lab-note">Σ x = ${fmt(x.reduce((a, b) => a + b, 0), 12)}</p>`;
    const bound = r === undefined ? "—" : fmt(alpha / (1 - alpha) * r, 3);
    const kstar = alpha > 0 ? Math.ceil(Math.log(1e-10 * (1 - alpha) / 2) / Math.log(alpha)) : 1;
    $("cert").innerHTML = `<p>iteration k = <strong>${k}</strong></p><p>residual ‖x<sub>k</sub> − x<sub>k−1</sub>‖₁ = ${r === undefined ? "—" : fmt(r, 3)}</p><p>certified error ‖x<sub>k</sub> − π‖₁ ≤ α/(1−α)·residual = <strong>${bound}</strong></p><p>a-priori iterations for tol 1e-10: k* = ${kstar} (CGT-PROP-009)</p>`;
  }
  $("g").addEventListener("change", load); $("step").addEventListener("click", step);
  $("solve").addEventListener("click", () => { reset(); const alpha = +$("a").value; let guard = 0; do { step(); } while (alpha / (1 - alpha) * hist.at(-1) > 1e-10 && ++guard < 5000); });
  $("reset").addEventListener("click", reset); $("a").addEventListener("input", draw); $("adj").addEventListener("change", reset);
  load();
};

// ===================================================================== sorting
WIDGETS["sorting"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>n <input type="number" min="2" max="2000" value="200" data-k="n" style="width:6rem"></label><label>input <select data-k="kind"><option>random</option><option>sorted</option><option>reversed</option><option>few distinct</option></select></label><label>seed <input type="number" data-k="seed" value="1" style="width:4rem"></label><button data-k="run">Sort with all three</button></div><div data-k="out"></div>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const n = Math.max(2, Math.min(2000, +$("n").value)), r = rng(+$("seed").value);
    let a = Array.from({ length: n }, () => Math.floor(r() * 1e6));
    if ($("kind").value === "sorted") a.sort((p, q) => p - q);
    if ($("kind").value === "reversed") a.sort((p, q) => q - p);
    if ($("kind").value === "few distinct") a = a.map((v) => v % 4);
    const rows = [];
    for (const [name, f, cls] of [["insertion sort", core.insertionSort, "b2"], ["merge sort", core.mergeSort, ""], ["heapsort", core.heapSort, "b3"]]) { const c = new core.Cost(); f(a, c); rows.push([name, c.counts.compare || 0, cls]); }
    rows.push(["n(n−1)/2", n * (n - 1) / 2, "b4"], ["n·⌈log₂ n⌉", n * Math.ceil(Math.log2(n)), "b4"]);
    $("out").innerHTML = `<p class="lab-note">Comparisons counted (same conventions as <code>cgtsdk.algorithms</code>):</p>` + bars(rows);
  }
  $("run").addEventListener("click", run); host.querySelectorAll("input,select").forEach((x) => x.addEventListener("change", run)); run();
};

// ===================================================================== break-even (PROP-005)
WIDGETS["break-even"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>build cost B <input type="number" value="21641" data-k="B" style="width:7rem"></label><label>query cost without index q₀ <input type="number" value="15.6" step="0.1" data-k="q0" style="width:6rem"></label><label>with index q₁ <input type="number" value="1" step="0.1" data-k="q1" style="width:5rem"></label><label>queries per invalidating update <input type="number" value="10" data-k="e" style="width:6rem"></label></div><div class="lab-out" aria-live="polite" data-k="out"></div>
  <p class="lab-note">Defaults are the counted values of CGT-EXP-005 (n = 1024, uniform queries): closure build ≈ 21,641 steps, BFS ≈ 15.6 steps/query.</p>`;
  const $ = (k) => host.querySelector(`[data-k="${k}"]`);
  function run() {
    const B = +$("B").value, q0 = +$("q0").value, q1 = +$("q1").value, e = +$("e").value;
    const qs = q0 > q1 ? B / (q0 - q1) : Infinity;
    $("out").textContent = `break-even queries per epoch  Q* = B / (q₀ − q₁) = ${isFinite(qs) ? qs.toFixed(1) : "∞ (the index never pays)"}\nqueries per epoch in this workload: ${e}\nverdict: ${e > qs ? "the index pays for itself in every epoch" : "search without an index is cheaper"}\ncost per epoch: index ${(B + e * q1).toFixed(0)} vs search ${(e * q0).toFixed(0)}`;
  }
  host.querySelectorAll("input").forEach((x) => x.addEventListener("input", run)); run();
};
