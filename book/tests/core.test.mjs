// The browser laboratory must reproduce the SDK exactly (fixtures exported
// from cgtsdk by tools/export_data.py).
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import * as core from "../site/assets/js/cgt-core.js";

const fx = JSON.parse(fs.readFileSync(new URL("../data/lab_fixtures.json", import.meta.url)));
const norm = (o) => Object.fromEntries(Object.entries(o).filter(([, v]) => v !== 0).sort());

test("regex compiles to the same minimal DFA size and language", () => {
  for (const r of fx.regex) {
    const d = core.compileRegex(r.regex);
    assert.equal(d.size, r.size, r.regex);
    r.words.forEach((w, i) => assert.equal(d.accepts(w ? w.split(" ") : []), r.accept[i], `${r.regex} on '${w}'`));
  }
});

test("array and linked list: identical values and cost counts", () => {
  for (const s of fx.sequences) {
    const st = s.structure === "array" ? new core.ArrayStructure(s.init) : new core.LinkedListStructure(s.init);
    for (const row of s.rows) {
      const c = new core.Cost();
      const [op, args] = core.parseCall(row.expr);
      const v = st.apply(op, args, c);
      assert.deepEqual([v ?? null], row.values.map((x) => x ?? null), row.expr);
      assert.deepEqual(norm(c.counts), norm(row.counts), `${s.structure} ${row.expr}`);
    }
  }
});

test("tree goto: pointer vs heap costs", () => {
  for (const t of fx.tree_goto) {
    for (const row of t.rows) {
      const tr = new core.CompleteTree(t.n, t.representation); const c = new core.Cost();
      let defined = true, vals = [];
      try { vals.push(tr.goto(row.addr, c)); vals.push(tr.read(c)); } catch (e) { defined = false; }
      assert.equal(defined, row.defined, row.addr);
      if (defined) assert.deepEqual(vals, row.values);
      assert.deepEqual(norm(c.counts), norm(row.counts), `${t.representation} ${row.addr}`);
    }
  }
});

test("compiled heap words (THM-006)", () => {
  for (const h of fx.heapword) {
    const f = core.compileHeapWord(h.word, h.n);
    assert.deepEqual([f.k, f.j, Number(f.c), Number(f.lo), Number(f.hi)], h.compiled, h.word);
    for (let x = 1; x <= h.n; x++) {
      assert.equal(f.apply(x), h.results[x - 1]);
      assert.equal(core.heapWalk(h.word, x, h.n), h.results[x - 1]);
    }
  }
});

test("product reachability (THM-001)", () => {
  for (const p of fx.product) {
    const r = core.productReach(p.n, p.edges, core.compileRegex(p.regex), p.source);
    assert.deepEqual(r.reach, p.reach, p.regex);
    assert.equal(r.explored, p.explored, p.regex);
  }
});

test("PageRank power iteration", () => {
  for (const p of fx.pagerank) {
    const r = core.pagerankPower(p.adj, p.alpha, p.tol);
    assert.equal(r.iterations, p.iterations);
    r.scores.forEach((s, i) => assert.ok(Math.abs(s - p.scores[i]) < 1e-14));
    r.scores.forEach((s, i) => assert.ok(Math.abs(s - p.exact[i]) < 1e-10));
  }
});

test("sorting: outputs and operation counts", () => {
  for (const s of fx.sorting) {
    for (const [name, f] of [["insertion_sort", core.insertionSort], ["merge_sort", core.mergeSort], ["heapsort", core.heapSort]]) {
      const c = new core.Cost();
      assert.deepEqual(f(s.input, c), s[name].output);
      assert.deepEqual(norm(c.counts), norm(s[name].counts), name);
    }
  }
});
