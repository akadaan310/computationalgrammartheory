"""CGT-EXP-002  Graph reachability: search vs closure vs path grammar vs
structural (interval) grammar, with full cost accounting.

Hypotheses (HYPOTHESES.md):
  H-002  Evaluating the path grammar P -> E | E P to fixpoint performs the same
         work as computing the transitive closure; it does not reduce work, it
         *is* the closure computation (rule firings ~ sum over sources of BFS).
  H-003  A precomputed reachability "grammar" pays off only after
         Q* = T_build / (T_search - T_lookup) queries, and its space cannot be
         compressed below ~n^2/4 bits on the bipartite family (CGT-THM-002).
  H-004  On forests the structural grammar itself (nesting = intervals) gives
         O(1) queries with O(n) preprocessing and O(n log n) bits: the
         advantage comes from the restricted class.

Falsification: H-002 fails if grammar fixpoint firings are asymptotically
below the closure size; H-003 fails if zlib compresses bipartite closures
far below n^2/4 * H(p) bits; H-004 fails if interval labels disagree with BFS.

Run:  python3 experiments/exp002_reachability.py
"""
from __future__ import annotations

import json
import os
import random
import time
import zlib

from cgt.core import Ops, env_info
from cgt.graphs import (IntervalLabels, TCBitsets, bfs_reach, bipartite_layers,
                        gnp, path_grammar_fixpoint, random_dag, random_forest,
                        tc_greedy_path)

SEED = 2
Q = 400
OUT = os.path.join(os.path.dirname(__file__), "results")


def families(n, rng):
    return {
        "gnp_d0.8": lambda: gnp(n, 0.8, rng),
        "gnp_d3": lambda: gnp(n, 3.0, rng),
        "dag_d2": lambda: random_dag(n, 2.0, rng),
        "forest": lambda: random_forest(n, max(1, n // 100), rng),
        "bipartite_p0.5": lambda: bipartite_layers(n, 0.5, rng),
    }


def closure_compressed_bits(tc: TCBitsets, n: int) -> int:
    rows = b"".join(tc.reach[tc.comp[v]].to_bytes((n + 7) // 8, "little")
                    for v in range(n))
    return 8 * len(zlib.compress(rows, 9))


def run(fam: str, n: int, rng: random.Random) -> dict:
    g = families(n, rng)[fam]()
    qs = [(rng.randrange(n), rng.randrange(n)) for _ in range(Q)]
    row = {"family": fam, "n": n, "m": g.m}
    ops = Ops()

    t0 = time.perf_counter()
    truth = [bfs_reach(g, s, t, ops) for s, t in qs]
    row["M1.s_per_q"] = (time.perf_counter() - t0) / Q
    row["M1.ops_per_q"] = ops.reset() / Q
    row["positive_frac"] = sum(truth) / Q

    t0 = time.perf_counter()
    tc = TCBitsets(g)
    row["M2.build_s"] = time.perf_counter() - t0
    row["M2.build_ops"] = tc.build_ops
    row["M2.space_bits"] = tc.space_bits
    row["M2.closure_pairs"] = sum(bin(tc.reach[tc.comp[v]]).count("1") for v in range(n))
    t0 = time.perf_counter()
    res = [tc.query(s, t, ops) for s, t in qs]
    row["M2.s_per_q"] = (time.perf_counter() - t0) / Q
    row["M2.ops_per_q"] = ops.reset() / Q
    assert res == truth, "TC disagrees with BFS"
    row["M2.compressed_bits_zlib"] = closure_compressed_bits(tc, n)

    # break-even query volume (counted ops, and wall clock)
    d_ops = row["M1.ops_per_q"] - row["M2.ops_per_q"]
    d_s = row["M1.s_per_q"] - row["M2.s_per_q"]
    row["breakeven_Q_ops"] = tc.build_ops / d_ops if d_ops > 0 else float("inf")
    row["breakeven_Q_wall"] = row["M2.build_s"] / d_s if d_s > 0 else float("inf")

    # path grammar fixpoint (small n only: it materialises the closure)
    if n <= 1024:
        for nl, tag in ((False, "M3lin"), (True, "M3nonlin")):
            if nl and n > 512:
                continue
            t0 = time.perf_counter()
            P = path_grammar_fixpoint(g, nl, ops)
            row[f"{tag}.build_s"] = time.perf_counter() - t0
            row[f"{tag}.firings"] = ops.reset()
            row[f"{tag}.facts"] = sum(len(x) for x in P)
            # P(u,v) means a path of length >= 1; reflexive pairs aside, equal to TC
            for s, t in qs:
                assert (s == t) or ((t in P[s]) == tc.query(s, t, ops))
            ops.reset()

    if fam == "forest":
        il = IntervalLabels(g)
        row["M4.build_ops"] = il.build_ops
        row["M4.space_bits"] = il.space_bits
        res = [il.query(s, t, ops) for s, t in qs]
        assert res == truth, "interval labels disagree"
        row["M4.ops_per_q"] = ops.reset() / Q
        row["breakeven_Q_ops_M4"] = il.build_ops / max(1e-9, row["M1.ops_per_q"] - 1)

    if fam in ("dag_d2", "forest"):
        pos = [(s, t) for (s, t), r in zip(qs, truth) if r][:100]
        if pos:
            L = 0
            for s, t in pos:
                L += len(tc_greedy_path(g, tc, s, t, ops)) - 1
            row["path_retrieval_ops_per_q"] = ops.reset() / len(pos)
            row["path_len_mean"] = L / len(pos)
    return row


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for n in (256, 1024, 4096):
        for fam in ("gnp_d0.8", "gnp_d3", "dag_d2", "forest", "bipartite_p0.5"):
            if fam == "bipartite_p0.5" and n > 1024:
                continue
            r = run(fam, n, rng)
            rows.append(r)
            print(f"{fam:15s} n={n:5d} m={r['m']:7d} pos={r['positive_frac']:.2f} "
                  f"BFS ops/q={r['M1.ops_per_q']:8.1f}  TC build={r['M2.build_ops']:9d} "
                  f"Q*={r['breakeven_Q_ops']:8.1f} (wall {r['breakeven_Q_wall']:7.1f}) "
                  f"TCbits={r['M2.space_bits']:9d} zlib={r['M2.compressed_bits_zlib']:9d} "
                  + (f"lin={r['M3lin.firings']} " if 'M3lin.firings' in r else "")
                  + (f"nonlin={r['M3nonlin.firings']} " if 'M3nonlin.firings' in r else "")
                  + (f"pairs={r['M2.closure_pairs']}"))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp002.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-002", "seed": SEED, "queries": Q,
                   "env": env_info(), "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
