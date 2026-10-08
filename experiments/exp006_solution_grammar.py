"""CGT-EXP-006  The "grammar of solutions" for CNF-SAT (mandate Part VI).

The most expressive grammar one can attach to a SAT instance is a grammar
generating exactly its satisfying assignments.  Its canonical small form is a
layered deterministic automaton over {0,1}^k (a quasi-reduced ordered
decision diagram).  Once it exists, SAT, model counting and many queries are
linear in its size -- *retrieval*.  The question is what it costs to build.

We build the automaton by residual deduplication: the state after reading
x1..xi is the residual clause set (satisfied clauses dropped, falsified
literals removed).  Syntactically equal residuals are merged.  This gives an
UPPER bound on the minimal width; it is exact as a recogniser.

Hypothesis H-009: for random 3-CNF near the satisfiability threshold
(m/k ~ 4.26) the solution grammar grows exponentially in k (so construction is
not polynomial), while for 2-CNF and Horn-like restrictions tractability comes
from the restriction, not from the grammar.
Falsification: H-009 fails if total nodes for threshold 3-CNF grow
polynomially (e.g., fit k^c with small c better than 2^(ak)) over k <= 28.

Run:  python3 experiments/exp006_solution_grammar.py
"""
from __future__ import annotations

import itertools
import json
import math
import os
import random

from cgt.core import env_info

SEED = 6
CAP = 2_000_000
OUT = os.path.join(os.path.dirname(__file__), "results")


def random_kcnf(k, m, width, rng):
    cls = []
    for _ in range(m):
        vs = rng.sample(range(k), width)
        cls.append(frozenset(v + 1 if rng.random() < 0.5 else -(v + 1) for v in vs))
    return cls


def assign(state, lit):
    """Residual of a clause set after making `lit` true. None = falsified."""
    out = []
    for c in state:
        if lit in c:
            continue
        if -lit in c:
            c = c - {-lit}
            if not c:
                return None
        out.append(c)
    return frozenset(out)


def build(k, clauses):
    """Layered solution automaton.  Returns (layer widths, #models, nodes)."""
    layer = {frozenset(clauses): 1}  # state -> number of paths (models so far)
    widths, nodes = [1], 1
    for i in range(1, k + 1):
        nxt = {}
        for st, cnt in layer.items():
            for lit in (i, -i):
                r = assign(st, lit)
                if r is not None:
                    nxt[r] = nxt.get(r, 0) + cnt
        layer = nxt
        widths.append(len(layer)); nodes += len(layer)
        if nodes > CAP:
            return widths, None, nodes
    models = layer.get(frozenset(), 0)
    return widths, models, nodes


def brute_count(k, clauses):
    cnt = 0
    for bits in itertools.product((False, True), repeat=k):
        if all(any((l > 0) == bits[abs(l) - 1] for l in c) for c in clauses):
            cnt += 1
    return cnt


def main():
    rng = random.Random(SEED)
    rows = []
    for label, width, ratio in (("3cnf_r4.26", 3, 4.26), ("3cnf_r2.0", 3, 2.0),
                                ("2cnf_r1.0", 2, 1.0)):
        for k in (8, 12, 16, 20, 24, 28):
            trials = []
            for _ in range(5):
                cl = random_kcnf(k, round(ratio * k), width, rng)
                w, models, nodes = build(k, cl)
                if k <= 16 and models is not None:
                    assert models == brute_count(k, cl), "model count mismatch"
                trials.append({"nodes": nodes, "max_width": max(w), "models": models})
            med = sorted(t["nodes"] for t in trials)[2]
            rows.append({"family": label, "k": k, "median_nodes": med, "trials": trials})
            print(f"{label:11s} k={k:2d} median nodes={med:9d} "
                  f"max widths={[t['max_width'] for t in trials]} "
                  f"log2(nodes)/k={math.log2(med) / k:.3f}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp006.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-006", "seed": SEED, "cap": CAP,
                   "env": env_info(), "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
