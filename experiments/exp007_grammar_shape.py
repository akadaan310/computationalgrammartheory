"""CGT-EXP-007  Same language, different grammar: does the *shape* of a path
grammar change the cost of resolving it?

  right-linear   P -> E | E P      (one edge at a time)
  doubling       P -> E | P P      (compose two derived paths)

Both define the same relation (the transitive closure).  CGT-THM-004 predicts
exact firing counts for the right-linear grammar:
    firings = |E| + sum_{(w,v) in P} indeg(w)
and Theta(n^3) firings for the doubling grammar on a directed path, against
Theta(n^2) for right-linear -- but O(log n) vs Theta(n) semi-naive rounds.

Falsification: THM-004's formula fails on any instance; or the doubling grammar
is not asymptotically costlier on paths; or its round count is not O(log n).

Run:  python3 experiments/exp007_grammar_shape.py
"""
from __future__ import annotations

import json
import math
import os
import random

from cgt.core import Ops, env_info
from cgt.graphs import DiGraph, gnp, random_dag


def fixpoint_rounds(g, nonlinear):
    """Same semi-naive evaluation as cgt.graphs.path_grammar_fixpoint, but
    also returns the number of semi-naive rounds.  Facts derived within a
    round are visible immediately (Gauss-Seidel), so these rounds are NOT the
    parallel depth; see jacobi_depth for that."""
    n = g.n
    radj = [[] for _ in range(n)]
    for u, v in g.edges():
        radj[v].append(u)
    P = [set() for _ in range(n)]; Pin = [set() for _ in range(n)]
    ops, delta, rounds = len(list(g.edges())), [], 0
    for u, v in g.edges():
        if v not in P[u]:
            P[u].add(v); Pin[v].add(u); delta.append((u, v))
    while delta:
        rounds += 1
        new = []
        for (w, v) in delta:
            if not nonlinear:
                for u in radj[w]:
                    ops += 1
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
            else:
                for u in list(Pin[w]):
                    ops += 1
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
                for x in list(P[v]):
                    ops += 1
                    if x not in P[w]:
                        P[w].add(x); Pin[x].add(w); new.append((w, x))
        delta = new
    return P, ops, rounds


def jacobi_depth(g, nonlinear):
    """Number of synchronous (Jacobi) rounds until fixpoint, i.e. the parallel
    derivation depth: P_{i+1} = E u E.P_i (linear) or E u P_i.P_i (doubling).
    Bitset rows; counts rounds only."""
    n = g.n
    E = [0] * n
    for u, v in g.edges():
        E[u] |= 1 << v
    P, rounds = E[:], 0
    while True:
        rounds += 1
        base = E if not nonlinear else P
        Q = []
        for u in range(n):
            r, b = E[u] | (P[u] if nonlinear else 0), base[u]
            while b:
                low = b & -b
                r |= P[low.bit_length() - 1]
                b ^= low
            Q.append(r)
        if Q == P:
            return rounds
        P = Q


def path_graph(n):
    g = DiGraph(n)
    for i in range(n - 1):
        g.add(i, i + 1)
    return g


def main():
    rng = random.Random(7)
    rows = []
    for fam, mk in (("path", path_graph),
                    ("gnp_d1.5", lambda n: gnp(n, 1.5, rng)),
                    ("dag_d2", lambda n: random_dag(n, 2.0, rng))):
        for n in (64, 128, 256, 512):
            g = mk(n)
            indeg = [0] * n
            for _, v in g.edges():
                indeg[v] += 1
            P1, f1, r1 = fixpoint_rounds(g, False)
            P2, f2, r2 = fixpoint_rounds(g, True)
            assert P1 == P2
            pairs = sum(len(s) for s in P1)
            predicted = g.m + sum(indeg[w] for w in range(n) for _ in P1[w])
            assert f1 == predicted, (f1, predicted)
            j1, j2 = jacobi_depth(g, False), jacobi_depth(g, True)
            rows.append({"family": fam, "n": n, "m": g.m, "closure_pairs": pairs,
                         "linear_firings": f1, "linear_predicted": predicted,
                         "linear_gs_rounds": r1, "doubling_firings": f2,
                         "doubling_gs_rounds": r2, "linear_parallel_depth": j1,
                         "doubling_parallel_depth": j2})
            print(f"{fam:9s} n={n:4d} pairs={pairs:7d} linear firings={f1:8d} (=formula) "
                  f"depth={j1:4d} | doubling firings={f2:10d} depth={j2:3d} "
                  f"(log2 n={math.log2(n):.0f})")
    out = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "exp007.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-007", "env": env_info(), "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
