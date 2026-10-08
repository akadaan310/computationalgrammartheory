// cgt-core.js — browser port of the parts of the CGT SDK used by the
// laboratory.  Same semantics and the same cost conventions as the Python
// package `cgtsdk`; `npm test` checks every function here against fixtures
// exported from the SDK (book/data/lab_fixtures.json).  If they ever
// disagree, the SDK is authoritative and the build's tests fail.

export class Cost {
  constructor(wordBits = 64) { this.counts = {}; this.trace = []; this.wordBits = wordBits; }
  add(cat, k = 1, note) { this.counts[cat] = (this.counts[cat] || 0) + k; if (note) this.trace.push([cat, note]); }
  wordArith(bits, k = 1, note) { this.add("arith", k * Math.max(1, Math.ceil(bits / this.wordBits)), note); }
  get total() { return Object.values(this.counts).reduce((a, b) => a + b, 0); }
  snapshot() { return Object.fromEntries(Object.entries(this.counts).filter(([, v]) => v !== 0).sort()); }
}

export class Undefined extends Error {}

// ------------------------------------------------------------------ regex -> minimal DFA
function tokens(src) {
  const re = /\s*(?:(\()|(\))|(\|)|(\*)|(\+)|(\?)|([A-Za-z_ε][A-Za-z0-9_]*))/y;
  const out = []; src = src.trim(); let pos = 0;
  while (pos < src.length) {
    re.lastIndex = pos; const m = re.exec(src);
    if (!m || re.lastIndex === pos) throw new SyntaxError(`bad regular expression near '${src.slice(pos, pos + 10)}'`);
    out.push(m.slice(1).find((g) => g !== undefined)); pos = re.lastIndex;
  }
  return out;
}

export function compileRegex(src) {
  const toks = tokens(src); let pos = 0, n = 0;
  const eps = new Map(), sym = new Map();
  const newState = () => n++;
  const addEps = (a, b) => { if (!eps.has(a)) eps.set(a, new Set()); eps.get(a).add(b); };
  const peek = () => toks[pos];
  const eat = (t) => { if (peek() !== t) throw new SyntaxError(`expected '${t}' at token ${pos}`); pos++; };
  function union() {
    const frags = [concat()];
    while (peek() === "|") { eat("|"); frags.push(concat()); }
    if (frags.length === 1) return frags[0];
    const s = newState(), e = newState();
    for (const [a, b] of frags) { addEps(s, a); addEps(b, e); }
    return [s, e];
  }
  function concat() {
    const frags = [];
    while (peek() !== undefined && peek() !== "|" && peek() !== ")") frags.push(postfix());
    if (!frags.length) { const s = newState(); return [s, s]; }
    for (let i = 0; i + 1 < frags.length; i++) addEps(frags[i][1], frags[i + 1][0]);
    return [frags[0][0], frags[frags.length - 1][1]];
  }
  function postfix() {
    let [a, b] = atom();
    while (["*", "+", "?"].includes(peek())) {
      const op = peek(); eat(op);
      const s = newState(), e = newState();
      addEps(s, a); addEps(b, e);
      if (op !== "+") addEps(s, e);
      if (op !== "?") addEps(b, a);
      a = s; b = e;
    }
    return [a, b];
  }
  function atom() {
    const t = peek();
    if (t === "(") { eat("("); const f = union(); eat(")"); return f; }
    if (t === undefined || ["|", ")", "*", "+", "?"].includes(t)) throw new SyntaxError(`unexpected '${t}' at token ${pos}`);
    pos++;
    const s = newState();
    if (t === "ε" || t === "eps") return [s, s];
    const e = newState();
    if (!sym.has(s)) sym.set(s, []); sym.get(s).push([t, e]);
    return [s, e];
  }
  const [s0, f0] = union();
  if (pos !== toks.length) throw new SyntaxError(`trailing tokens from ${pos}`);
  const letters = [...new Set([...sym.values()].flat().map(([a]) => a))].sort();
  const closure = (S) => { const st = [...S], out = new Set(S); while (st.length) { const q = st.pop(); for (const r of eps.get(q) || []) if (!out.has(r)) { out.add(r); st.push(r); } } return out; };
  const key = (S) => [...S].sort((a, b) => a - b).join(",");
  const start = closure([s0]);
  const states = new Map([[key(start), start]]); const todo = [start]; const delta = new Map();
  while (todo.length) {
    const S = todo.pop();
    for (const a of letters) {
      const T0 = []; for (const q of S) for (const [b, r] of sym.get(q) || []) if (b === a) T0.push(r);
      if (!T0.length) continue;
      const T = closure(T0), kT = key(T);
      delta.set(`${key(S)}|${a}`, kT);
      if (!states.has(kT)) { states.set(kT, T); todo.push(T); }
    }
  }
  const accept = new Set([...states.keys()].filter((k) => states.get(k).has(f0)));
  return minimize({ states: [...states.keys()], start: key(start), accept, delta, alphabet: letters });
}

function minimize(d) {
  const A = d.alphabet, SINK = "__sink__";
  const reach = new Set([d.start]), todo = [d.start];
  while (todo.length) { const q = todo.pop(); for (const a of A) { const r = d.delta.get(`${q}|${a}`); if (r !== undefined && !reach.has(r)) { reach.add(r); todo.push(r); } } }
  const states = [...reach, SINK];
  const nxt = (q, a) => (q === SINK ? SINK : d.delta.get(`${q}|${a}`) ?? SINK);
  let block = new Map(states.map((q) => [q, d.accept.has(q) ? 1 : 0]));
  for (;;) {
    const ids = new Map(); const nb = new Map();
    for (const q of states) { const sig = [block.get(q), ...A.map((a) => block.get(nxt(q, a)))].join(","); if (!ids.has(sig)) ids.set(sig, ids.size); nb.set(q, ids.get(sig)); }
    const done = new Set(nb.values()).size === new Set(block.values()).size;
    block = nb; if (done) break;
  }
  const trans = new Map();
  for (const q of states) for (const a of A) trans.set(`${block.get(q)}|${a}`, block.get(nxt(q, a)));
  const acc = new Set(states.filter((q) => d.accept.has(q)).map((q) => block.get(q)));
  const live = new Set(acc); let changed = true;
  while (changed) { changed = false; for (const [k, c] of trans) { const b = Number(k.split("|")[0]); if (live.has(c) && !live.has(b)) { live.add(b); changed = true; } } }
  const st = block.get(d.start);
  if (!live.has(st)) return new DFA([0], 0, [], new Map(), A);
  const order = [...live].sort((x, y) => (x !== st) - (y !== st) || x - y);
  const ren = new Map(order.map((b, i) => [b, i]));
  const delta = new Map();
  for (const [k, c] of trans) { const [b, a] = k.split("|"); if (live.has(Number(b)) && live.has(c)) delta.set(`${ren.get(Number(b))}|${a}`, ren.get(c)); }
  return new DFA([...ren.values()], ren.get(st), [...acc].filter((b) => live.has(b)).map((b) => ren.get(b)), delta, A);
}

export class DFA {
  constructor(states, start, accept, delta, alphabet) { this.states = states; this.start = start; this.accept = new Set(accept); this.delta = delta; this.alphabet = alphabet; }
  get size() { return this.states.length; }
  step(q, a) { return this.delta.get(`${q}|${a}`); }
  accepts(word) { let q = this.start; for (const a of word) { q = this.step(q, a); if (q === undefined) return false; } return this.accept.has(q); }
  static universal(alphabet) { return new DFA([0], 0, [0], new Map(alphabet.map((a) => [`0|${a}`, 0])), alphabet); }
}

// ------------------------------------------------------------------ sequences (array / linked list)
function idx(i, n, what = "index") {
  if (!Number.isInteger(i)) throw new Undefined(`${what} must be an integer`);
  if (i < 0 || i >= n) throw new Undefined(`${what} ${i} out of range [0, ${n})`);
  return i;
}

export class ArrayStructure {
  constructor(values) { this.n = values.length; this.capacity = Math.max(this.n, 1); this.mem = [...values, ...Array(this.capacity - this.n).fill(null)]; }
  grow(c) { const nc = 2 * this.capacity; c.add("alloc", nc, `reallocate ${this.capacity} → ${nc}`); c.add("read", this.n); c.add("write", this.n); this.mem = [...this.mem.slice(0, this.n), ...Array(nc - this.n).fill(null)]; this.capacity = nc; }
  apply(op, args, c) {
    if (["get", "set", "delete"].includes(op)) {
      c.add("compare", 1, "bounds check"); const i = idx(args[0], this.n);
      c.add("arith", 1, `address = base + ${i}`);
      if (op === "get") { c.add("read", 1, `read cell ${i}`); return this.mem[i]; }
      if (op === "set") { c.add("write", 1, `write cell ${i}`); this.mem[i] = args[1]; return null; }
      const v = this.mem[i], k = this.n - i - 1;
      c.add("read", k + 1); c.add("write", k, `shift ${k} cells left`);
      this.mem.splice(i, 1); this.mem.push(null); this.n--; return v;
    }
    if (op === "len") { c.add("read", 1, "read header n"); return this.n; }
    if (op === "append") { if (this.n === this.capacity) this.grow(c); c.add("write", 1, `write cell ${this.n}`); this.mem[this.n++] = args[0]; return null; }
    if (op === "insert") {
      c.add("compare", 1, "bounds check"); const i = idx(args[0], this.n + 1, "insert position");
      if (this.n === this.capacity) this.grow(c);
      const k = this.n - i; c.add("read", k); c.add("write", k + 1, `shift ${k} cells right`);
      this.mem.splice(i, 0, args[1]); this.mem.length = this.capacity; this.n++; return null;
    }
    throw new Undefined(`unknown move ${op}`);
  }
  values() { return this.mem.slice(0, this.n); }
}

export class LinkedListStructure {
  constructor(values) { this.vals = [...values]; }
  walk(i, c) { c.add("read", 1, "read head"); if (i) { c.add("pointer", i); c.trace.push(["note", `followed next ${i} times`]); } }
  apply(op, args, c) {
    const n = this.vals.length;
    if (op === "len") { c.add("read", 1); return n; }
    if (op === "get" || op === "set") {
      c.add("compare", 1, "bounds check"); const i = idx(args[0], n); this.walk(i, c);
      if (op === "get") { c.add("read", 1); return this.vals[i]; }
      c.add("write", 1); this.vals[i] = args[1]; return null;
    }
    if (op === "push_front") { c.add("alloc", 1); c.add("write", 3); this.vals.unshift(args[0]); return null; }
    if (op === "insert") {
      c.add("compare", 1); const i = idx(args[0], n + 1, "insert position");
      c.add("alloc", 1); c.add("write", 3); if (i > 0) this.walk(i - 1, c);
      this.vals.splice(i, 0, args[1]); return null;
    }
    if (op === "delete") {
      c.add("compare", 1); const i = idx(args[0], n); c.add("write", 2); if (i > 0) this.walk(i - 1, c);
      return this.vals.splice(i, 1)[0];
    }
    throw new Undefined(`unknown move ${op}`);
  }
  values() { return [...this.vals]; }
}

export function parseCall(s) {
  const m = s.trim().match(/^([A-Za-z_]\w*)\s*(?:\(([^()]*)\))?$/);
  if (!m) throw new SyntaxError(`cannot parse '${s}'`);
  const args = m[2] && m[2].trim() ? m[2].split(",").map((x) => { x = x.trim(); if (/^-?\d+$/.test(x)) return Number(x); if (/^'.*'$|^".*"$/.test(x)) return x.slice(1, -1); throw new SyntaxError(`bad argument ${x}`); }) : [];
  return [m[1], args];
}
export function splitExpr(src) { return src.split(/[;\n]/).map((s) => s.trim()).filter(Boolean); }

// ------------------------------------------------------------------ complete binary tree (pointer vs heap)
export class CompleteTree {
  constructor(n, rep) { this.n = n; this.rep = rep; this.height = Math.floor(Math.log2(n)); this.cursor = ""; }
  has(a) { return a === "" || (/^[01]+$/.test(a) && parseInt("1" + a, 2) <= this.n); }
  label(a) { return parseInt("1" + a, 2); }
  goto(a, c) {
    if (this.rep === "pointer") {
      c.add("read", 1); let cur = "";
      for (const b of a) { c.add("pointer", 1); if (!this.has(cur + b)) throw new Undefined(`no node at address '${a}'`); cur += b; }
      this.cursor = cur; return cur;
    }
    c.wordArith(a.length + 1, 1, "ν = int('1'+addr, 2)"); c.add("probe", 1);
    if (!this.has(a)) throw new Undefined(`no node at address '${a}'`);
    this.cursor = a; return a;
  }
  read(c) { if (this.rep === "pointer") c.add("read", 1); else c.add("probe", 1); return this.label(this.cursor); }
}

// ------------------------------------------------------------------ compiled heap words (CGT-THM-006)
export function compileHeapWord(word, n, c) {
  let k = 0, j = 0, cc = 0n, lo = 1n, hi = BigInt(n);
  const N = BigInt(n);
  for (const a of word) {
    c?.add("arith", 4);
    if (a === "U") { if (j > 0) { j--; cc >>= 1n; } else { k++; const p = 1n << BigInt(k); if (p > lo) lo = p; } }
    else if (a === "L" || a === "R") { j++; cc = (cc << 1n) | (a === "R" ? 1n : 0n); }
    else throw new SyntaxError(`unknown move ${a}`);
    if (cc > N) hi = 0n;
    else { const t = ((((N - cc) >> BigInt(j)) + 1n) << BigInt(k)) - 1n; if (t < hi) hi = t; }
  }
  return { k, j, c: cc, lo, hi, apply(x) { const X = BigInt(x); if (X < lo || X > hi) return null; return Number(((X >> BigInt(k)) << BigInt(j)) | cc); } };
}
export function heapWalk(word, x, n) {
  for (const a of word) { x = a === "U" ? Math.floor(x / 2) : 2 * x + (a === "R" ? 1 : 0); if (x < 1 || x > n) return null; }
  return x;
}

// ------------------------------------------------------------------ product reachability (CGT-THM-001)
export function productReach(n, edges, dfa, source, c) {
  const out = new Map();
  for (const [u, a, v] of edges) { if (!out.has(a)) out.set(a, Array.from({ length: n }, () => [])); out.get(a)[u].push(v); }
  const labels = [...out.keys()].filter((a) => dfa.alphabet.includes(a)).sort();
  const seen = new Set([`${source}|${dfa.start}`]); const queue = [[source, dfa.start]]; const reach = new Set(); const order = [];
  for (let h = 0; h < queue.length; h++) {
    const [y, q] = queue[h]; c?.add("read", 1); order.push([y, q]);
    if (dfa.accept.has(q)) reach.add(y);
    for (const a of labels) {
      c?.add("rule", 1); const q2 = dfa.step(q, a);
      if (q2 === undefined) continue;
      for (const z of out.get(a)[y]) { c?.add("edge", 1); const k = `${z}|${q2}`; if (!seen.has(k)) { seen.add(k); queue.push([z, q2]); } }
    }
  }
  return { reach: [...reach].sort((a, b) => a - b), explored: seen.size, order };
}

// ------------------------------------------------------------------ PageRank (CGT-THM-008)
export function pagerankPower(adj, alpha = 0.85, tol = 1e-10, maxIter = 10000, onIter) {
  const n = adj.length, out = adj.map((a) => a.length), v = Array(n).fill(1 / n);
  let x = [...v]; const residuals = [];
  for (let k = 1; k <= maxIter; k++) {
    let dangling = 0; for (let u = 0; u < n; u++) if (out[u] === 0) dangling += x[u];
    const y = v.map((vi) => (1 - alpha + alpha * dangling) * vi);
    for (let u = 0; u < n; u++) if (out[u]) { const share = alpha * x[u] / out[u]; for (const w of adj[u]) y[w] += share; }
    let r = 0; for (let i = 0; i < n; i++) r += Math.abs(x[i] - y[i]);
    x = y; residuals.push(r);
    const bound = alpha > 0 ? alpha / (1 - alpha) * r : r;
    onIter?.(k, x, r, bound);
    if (bound <= tol) return { scores: x, iterations: k, residuals, bound, converged: true };
  }
  return { scores: x, iterations: maxIter, residuals, bound: alpha / (1 - alpha) * residuals.at(-1), converged: false };
}

// ------------------------------------------------------------------ sorting with compare counts (same conventions as cgtsdk.algorithms.basic)
export function insertionSort(a0, c) {
  const a = [...a0];
  for (let i = 1; i < a.length; i++) {
    const x = a[i]; let j = i - 1; c.add("read", 1);
    while (j >= 0) { c.add("compare", 1); if (a[j] <= x) break; a[j + 1] = a[j]; c.add("write", 1); j--; }
    a[j + 1] = x; c.add("write", 1);
  }
  return a;
}
export function mergeSort(a0, c) {
  const a = [...a0];
  if (a.length <= 1) return a;
  const mid = Math.floor(a.length / 2);
  const left = mergeSort(a.slice(0, mid), c), right = mergeSort(a.slice(mid), c);
  const out = []; let i = 0, j = 0;
  while (i < left.length && j < right.length) { c.add("compare", 1); if (left[i] <= right[j]) out.push(left[i++]); else out.push(right[j++]); c.add("write", 1); }
  const rest = [...left.slice(i), ...right.slice(j)]; c.add("write", rest.length);
  return [...out, ...rest];
}
export function heapSort(a0, c) {
  const a = [...a0], n = a.length;
  const sift = (i, end) => {
    for (;;) {
      const l = 2 * i + 1, r = 2 * i + 2; let m = i; c.add("arith", 2);
      if (l < end) { c.add("compare", 1); if (a[l] > a[m]) m = l; }
      if (r < end) { c.add("compare", 1); if (a[r] > a[m]) m = r; }
      if (m === i) return;
      [a[i], a[m]] = [a[m], a[i]]; c.add("write", 2); i = m;
    }
  };
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) sift(i, n);
  for (let end = n - 1; end > 0; end--) { [a[0], a[end]] = [a[end], a[0]]; c.add("write", 2); sift(0, end); }
  return a;
}
