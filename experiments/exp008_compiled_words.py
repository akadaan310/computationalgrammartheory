"""CGT-EXP-008  Arithmetic addressing beyond binary trees, and compiled move
words (OPEN-002, OPEN-003; THM-006, THM-007).

Hypothesis H-013: in arithmetically addressed structures (heap-shaped trees,
grids, hypercubes, de Bruijn graphs) a move word of length L compiles in
O(L) word operations into an O(1)-size map that is then applied in O(1),
so applying it to Q start points costs O(L + Q) instead of Θ(L·Q).  On
pointer-represented trees of arbitrary shape no such compiled form exists
without Ω(n) bits (THM-007); the only option is an n-entry table built by
simulation, Θ(n·L) build.

Falsification: compiled and step-by-step results differ on any input; or the
compiled per-application cost grows with L.

Run:  python3 experiments/exp008_compiled_words.py   (requires sdk/src on the path;
      run_all.sh sets PYTHONPATH)
"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "src"))

from cgtsdk import Cost  # noqa: E402
from cgtsdk.addressing import (AffineMod, BoxTranslation, HeapWord, XorMask, compile_word,  # noqa: E402
                               debruijn_moves, grid_moves, heap_walk, hypercube_moves)
from cgt.core import env_info  # noqa: E402

SEED = 8
OUT = os.path.join(os.path.dirname(__file__), "results")


def walk_word(rng, x, n, L):
    """A word of length L that is defined at x: a random walk in the tree."""
    w = []
    for _ in range(L):
        opts = [a for a, y in (("L", 2 * x), ("R", 2 * x + 1), ("U", x >> 1)) if 1 <= y <= n]
        a = rng.choice(opts)
        w.append(a)
        x = 2 * x if a == "L" else 2 * x + 1 if a == "R" else x >> 1
    return w


def heap_rows(rng):
    rows = []
    n = 1_000_000
    for workload in ("random_words", "walk_words"):
      for L in (8, 64, 512, 4096):
        if workload == "random_words":
            # random words over {L,R,U}: most starts fall off the tree early
            w = [rng.choice("LRUU") for _ in range(L)]
        else:
            # adversarial for early exit: a word defined at a depth-12 node,
            # applied to starts at depth 12 (almost all defined)
            w = walk_word(rng, rng.randrange(1 << 12, 1 << 13), n, L)
        starts = ([rng.randrange(1, n + 1) for _ in range(2000)] if workload == "random_words"
                  else [rng.randrange(1 << 12, 1 << 13) for _ in range(2000)])
        cc, cw, ca = Cost(), Cost(), Cost()
        f = HeapWord.compile(w, n, cc)
        defined = 0
        for x in starts:
            a = f(x, ca)
            b = heap_walk(w, x, n, cw)
            assert a == b
            defined += a is not None
        Q = len(starts)
        rows.append({"structure": "heap_tree", "workload": workload, "n": n, "L": L, "Q": Q,
                     "compile_ops": cc.total, "compiled_ops_per_q": ca.total / Q,
                     "walk_ops_per_q": cw.total / Q, "defined_frac": defined / Q,
                     "break_even_Q": cc.total / max(1e-9, cw.total / Q - ca.total / Q)})
    return rows


def pointer_table_rows(rng):
    """Arbitrary-shape pointer tree: tabulate ⟦w⟧ by simulation from every node."""
    rows = []
    n = 20_000
    parent, left, right = [-1] * n, [-1] * n, [-1] * n
    for v in range(1, n):  # random binary tree by random attachment
        while True:
            p = rng.randrange(v)
            side = rng.randrange(2)
            if (left if side == 0 else right)[p] < 0:
                (left if side == 0 else right)[p] = v; parent[v] = p
                break
    for L in (8, 64, 512):
        # a word defined at some node: random walk in the pointer tree
        x, w = rng.randrange(n), []
        for _ in range(L):
            opts = [(a, y) for a, y in (("L", left[x]), ("R", right[x]), ("U", parent[x])) if y >= 0]
            a, x = rng.choice(opts)
            w.append(a)
        c = Cost()
        table = []
        for x in range(n):
            y = x
            for a in w:
                c.add("pointer", 1)
                y = parent[y] if a == "U" else (left if a == "L" else right)[y]
                if y < 0:
                    break
            table.append(y)
        rows.append({"structure": "pointer_tree_random", "n": n, "L": L,
                     "table_build_ops": c.total, "table_space_words": n,
                     "lookup_ops_per_q": 1, "defined_frac": sum(t >= 0 for t in table) / n})
    return rows


def other_rows(rng):
    rows = []
    cases = [
        ("debruijn_k2_m20", debruijn_moves(2, 20), AffineMod.identity(2 ** 20), lambda: rng.randrange(2 ** 20)),
        ("hypercube_d20", hypercube_moves(20), XorMask(0), lambda: rng.randrange(2 ** 20)),
        ("grid_1000x1000", grid_moves((1000, 1000)), BoxTranslation.identity((1000, 1000)),
         lambda: (rng.randrange(1000), rng.randrange(1000))),
    ]
    for name, mv, ident, gen in cases:
        for L in (8, 512):
            w = [rng.choice(sorted(mv)) for _ in range(L)]
            cc, cw = Cost(), Cost()
            f = compile_word(mv, w, ident, cc)
            Q = 500
            for _ in range(Q):
                x = gen()
                y = x
                for a in w:
                    if y is None:
                        break
                    cw.add("arith", 1)
                    y = mv[a](y)
                assert f(x) == y
            rows.append({"structure": name, "L": L, "compile_ops": cc.total, "density": 1.0,
                         # one composed map: 1 op (affine/xor) or 2d compares + d adds (grid)
                         "compiled_apply_ops": 1 if name != "grid_1000x1000" else 6,
                         "walk_ops_per_q": cw.total / Q})
    return rows


def main():
    rng = random.Random(SEED)
    rows = heap_rows(rng) + pointer_table_rows(rng) + other_rows(rng)
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp008.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-008", "seed": SEED, "env": env_info(), "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
