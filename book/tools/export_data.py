"""Export machine-generated data consumed by the book build (book/data/):

* sdk_reference.json      -- API reference generated from cgtsdk docstrings
* gaas_capabilities.json  -- the GaaS contract's capabilities + an example
* ledger_ids.json         -- every CGT-* identifier present in the ledger files
* lab_fixtures.json       -- reference outputs computed by the SDK, which the
                             browser laboratory (cgt-core.js) must reproduce
                             exactly (checked by `npm test`)
* experiments.json        -- compact experiment numbers for in-book figures

Run from anywhere:  python3 book/tools/export_data.py
"""
from __future__ import annotations

import importlib
import inspect
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
REPO = os.path.dirname(BOOK)
sys.path.insert(0, os.path.join(REPO, "sdk", "src"))

import cgtsdk  # noqa: E402
from cgtsdk import Cost, compile_regex  # noqa: E402
from cgtsdk.addressing import HeapWord, heap_walk  # noqa: E402
from cgtsdk.algorithms import (heapsort, insertion_sort, merge_sort, pagerank_exact,  # noqa: E402
                               pagerank_power, product_reach)
from cgtsdk.service import capabilities, handle  # noqa: E402
from cgtsdk.structures import (ArrayStructure, BinaryTreeStructure, GraphStructure,  # noqa: E402
                               LinkedListStructure)

OUT = os.path.join(BOOK, "data")

MODULES = ["cgtsdk", "cgtsdk.grammar", "cgtsdk.cost", "cgtsdk.automata", "cgtsdk.structures",
           "cgtsdk.algorithms", "cgtsdk.addressing", "cgtsdk.lab", "cgtsdk.service"]


def sdk_reference():
    mods = []
    seen = set()
    for name in MODULES:
        m = importlib.import_module(name)
        members = []
        names = getattr(m, "__all__", None) or [n for n in dir(m) if not n.startswith("_")]
        for n in sorted(names):
            obj = getattr(m, n, None)
            if obj is None or not (inspect.isclass(obj) or inspect.isfunction(obj)):
                continue
            if getattr(obj, "__module__", "").split(".")[0] != "cgtsdk":
                continue
            key = (obj.__module__, obj.__qualname__)
            if key in seen and name not in ("cgtsdk.structures", "cgtsdk.algorithms"):
                continue
            seen.add(key)
            try:
                sig = str(inspect.signature(obj))
            except (TypeError, ValueError):
                sig = ""
            entry = {"name": n, "kind": "class" if inspect.isclass(obj) else "function",
                     "signature": sig, "doc": inspect.getdoc(obj) or "", "defined_in": obj.__module__}
            if inspect.isclass(obj) and getattr(obj, "SIGNATURE", None):
                entry["moves"] = [str(mv) for mv in obj.SIGNATURE]
            members.append(entry)
        mods.append({"name": name, "doc": inspect.getdoc(m) or "", "members": members})
    loader = unittest.TestLoader()
    tests = loader.discover(os.path.join(REPO, "sdk", "tests"), top_level_dir=os.path.join(REPO, "sdk", "tests"))
    return {"version": cgtsdk.__version__, "tests": tests.countTestCases(), "modules": mods}


def gaas():
    caps = capabilities()
    ex = {"contract": caps["contract"], "grammar": {"structure": "array", "version": "1"},
          "init": {"values": [5, 3, 8]}, "expression": "get(2); set(0, 9); get(0)"}
    r = handle(ex)
    r["provenance"].pop("wall_ms", None)
    caps["example_response"] = r
    return caps


LEDGER_FILES = ["RESULTS.md", "DEFINITIONS.md", "HYPOTHESES.md", "COUNTEREXAMPLES.md", "OPEN_PROBLEMS.md",
                "EXPERIMENTS.md", "PROVENANCE.md", "DECISION_LOG.md", "LITERATURE_REVIEW.md", "RESEARCH_CHARTER.md"]


def ledger_ids():
    ids = set()
    for f in LEDGER_FILES:
        ids |= set(re.findall(r"CGT-[A-Z]+-\d+[a-z]?", open(os.path.join(REPO, f), encoding="utf8").read()))
    return sorted(ids)


def fixtures():
    fx = {}
    # regex -> minimal DFA: sizes and acceptance on all short words
    import itertools
    regexes = ["a*", "(a b)* c", "(a | b)* c (a | b)*", "a+ b?", "(a | ε) b", "(a | b)* a (a | b) (a | b)",
               "(L | R)* U", "(a b)* (a | ε)"]
    fx["regex"] = []
    for rx in regexes:
        d = compile_regex(rx)
        alpha = sorted(d.alphabet)
        words = [list(w) for k in range(5) for w in itertools.product(alpha, repeat=k)]
        fx["regex"].append({"regex": rx, "size": d.size, "alphabet": alpha,
                            "words": [" ".join(w) for w in words],
                            "accept": [d.accepts(w) for w in words]})
    # array vs linked list: exact cost counts for expressions
    fx["sequences"] = []
    for exprs in (["get(0)", "get(5)", "get(9)", "set(3, 7)", "len"], ["insert(0, 1)", "delete(4)", "append(2)"]):
        for cls in (ArrayStructure, LinkedListStructure):
            if cls is LinkedListStructure and "append(2)" in exprs:
                continue
            g = cls(list(range(10))).grammar()
            rows = []
            for e in exprs:
                r = g.execute(e)
                rows.append({"expr": e, "values": r.values, "counts": r.cost.snapshot()})
            fx["sequences"].append({"structure": cls.name, "init": list(range(10)), "rows": rows})
    # binary tree goto: pointer vs heap costs
    fx["tree_goto"] = []
    for rep in ("pointer", "heap"):
        t = BinaryTreeStructure.complete(1000, rep).grammar()
        rows = []
        for a in ["", "0", "011", "0101010", "111111111", "000000000"]:
            r = t.execute(f"goto('{a}') read")
            rows.append({"addr": a, "defined": r.defined, "values": r.values, "counts": r.cost.snapshot()})
        fx["tree_goto"].append({"representation": rep, "n": 1000, "rows": rows})
    # compiled heap words
    fx["heapword"] = []
    for w, n in [("LRU", 20), ("UUL", 50), ("LLRRUUU", 100), ("RUL", 7), ("LLLLLLLLLL", 30)]:
        f = HeapWord.compile(w, n)
        fx["heapword"].append({"word": w, "n": n, "compiled": [f.k, f.j, f.c, f.lo, f.hi],
                               "results": [heap_walk(w, x, n) for x in range(1, n + 1)]})
    # product reachability
    fx["product"] = []
    edges = [(0, "a", 1), (1, "b", 2), (2, "a", 3), (3, "b", 0), (0, "c", 4), (4, "a", 1), (2, "c", 4), (1, "a", 1)]
    g = GraphStructure(5, edges)
    for rx in ["(a b)*", "a* c", "(a | b | c)* c", "a (b a)* b"]:
        out, ex = product_reach(g, 0, compile_regex(rx), return_explored=True)
        fx["product"].append({"n": 5, "edges": edges, "regex": rx, "source": 0, "reach": sorted(out), "explored": ex})
    # PageRank
    fx["pagerank"] = []
    for adj in ([[1, 2], [2], [0], []], [[1], [2], [0, 3], [3]], [[1, 2, 3], [0], [0], [0, 1, 2]]):
        for alpha in (0.5, 0.85):
            pw = pagerank_power(adj, alpha, tol=1e-12)
            fx["pagerank"].append({"adj": adj, "alpha": alpha, "tol": 1e-12, "iterations": pw.iterations,
                                   "scores": pw.scores, "exact": pagerank_exact(adj, alpha)})
    # sorting compare counts on explicit arrays
    fx["sorting"] = []
    for arr in ([5, 2, 9, 1, 5, 6], list(range(10)), list(range(10, 0, -1)), [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]):
        row = {"input": arr}
        for f in (insertion_sort, merge_sort, heapsort):
            c = Cost()
            out = f(arr, c)
            row[f.__name__] = {"output": out, "counts": c.snapshot()}
        fx["sorting"].append(row)
    return fx


def experiments():
    R = os.path.join(REPO, "experiments", "results")
    out = {}
    for f in sorted(os.listdir(R)):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(R, f)))
            d.pop("env", None)
            out[f[:-5]] = d
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("sdk_reference", sdk_reference), ("gaas_capabilities", gaas), ("ledger_ids", ledger_ids),
                     ("lab_fixtures", fixtures), ("experiments", experiments)):
        with open(os.path.join(OUT, f"{name}.json"), "w") as fh:
            json.dump(fn(), fh, indent=None, separators=(",", ":"), default=str)
    print("exported book/data/*.json")


if __name__ == "__main__":
    main()
