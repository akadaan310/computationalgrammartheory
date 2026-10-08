"""CGT-EXP-005  Repeated queries and dynamic updates (mandate Experiments D/E).

Strategies for an interleaved stream of reachability queries and edge
updates on a digraph (n = 1024 by default):
  S1  BFS per query, O(1) update                        (no grammar/index)
  S2  closure, rebuilt lazily before a query if dirty   (static index)
  S3  closure, incremental on insertion (bitset rows), lazy rebuild on deletion
  S4  memoised BFS: cache answers, flush cache on any update

Hypothesis H-008: no strategy dominates; the winner is determined by the
query/update ratio, the deletion share, and query repetitiveness.  A
precomputed closure (the "grammar of all paths") wins only for query-heavy,
insertion-only or low-churn streams; under deletions it can be worse than
search by orders of magnitude.
Falsification: H-008 fails if one strategy is cheapest on every workload.

Run:  python3 experiments/exp005_dynamic.py
"""
from __future__ import annotations

import json
import os
import random

from cgt.core import Ops, env_info
from cgt.graphs import DiGraph, TCBitsets, bfs_reach, gnp, wcost

SEED = 5
OUT = os.path.join(os.path.dirname(__file__), "results")


class Closure:
    def __init__(self, g: DiGraph, ops):
        tc = TCBitsets(g)
        ops.add(tc.build_ops)
        self.R = [tc.reach[tc.comp[v]] for v in range(g.n)]
        ops.add(g.n)

    def insert(self, u, v, n, ops):
        ops.add()
        if (self.R[u] >> v) & 1:
            return
        rv = self.R[v]
        for x in range(n):
            ops.add()
            if (self.R[x] >> u) & 1:
                self.R[x] |= rv; ops.add(wcost(n))

    def query(self, s, t, ops):
        ops.add()
        return (self.R[s] >> t) & 1 == 1


def make_stream(g: DiGraph, length, q_frac, del_frac, repetitive, adversarial, rng):
    pool = [(rng.randrange(g.n), rng.randrange(g.n)) for _ in range(10)]
    stream = []
    present = [(u, v) for u, v in g.edges()]
    for _ in range(length):
        if rng.random() < q_frac:
            if repetitive:
                stream.append(("q",) + rng.choice(pool))
            elif adversarial:
                stream.append(("q", adversarial[0], rng.choice(adversarial[1])))
            else:
                stream.append(("q", rng.randrange(g.n), rng.randrange(g.n)))
        elif rng.random() < del_frac and present:
            i = rng.randrange(len(present))
            present[i], present[-1] = present[-1], present[i]
            stream.append(("d",) + present.pop())
        else:
            u, v = rng.randrange(g.n), rng.randrange(g.n)
            present.append((u, v)); stream.append(("i", u, v))
    return stream


def copy_graph(g):
    h = DiGraph(g.n)
    for u, v in g.edges():
        h.add(u, v)
    return h


def remove_edge(g, u, v):
    g.adj[u].remove(v); g.m -= 1


def run_stream(g0, stream):
    n = g0.n
    costs, answers = {}, {}
    # S1
    g, ops, ans = copy_graph(g0), Ops(), []
    for op, u, v in stream:
        if op == "q":
            ans.append(bfs_reach(g, u, v, ops))
        elif op == "i":
            g.add(u, v); ops.add()
        else:
            remove_edge(g, u, v); ops.add()
    costs["S1_bfs"], answers["S1_bfs"] = ops.n, ans
    # S2 lazy rebuild
    g, ops, ans, C, dirty = copy_graph(g0), Ops(), [], None, True
    for op, u, v in stream:
        if op == "q":
            if dirty:
                C = Closure(g, ops); dirty = False
            ans.append(C.query(u, v, ops))
        else:
            (g.add(u, v) if op == "i" else remove_edge(g, u, v)); ops.add(); dirty = True
    costs["S2_rebuild"], answers["S2_rebuild"] = ops.n, ans
    # S3 incremental inserts, lazy rebuild after deletions
    g, ops, ans = copy_graph(g0), Ops(), []
    C, dirty = Closure(g, ops), False
    for op, u, v in stream:
        if op == "q":
            if dirty:
                C = Closure(g, ops); dirty = False
            ans.append(C.query(u, v, ops))
        elif op == "i":
            g.add(u, v); ops.add()
            if not dirty:
                C.insert(u, v, n, ops)
        else:
            remove_edge(g, u, v); ops.add(); dirty = True
    costs["S3_incremental"], answers["S3_incremental"] = ops.n, ans
    # S4 memo
    g, ops, ans, memo = copy_graph(g0), Ops(), [], {}
    for op, u, v in stream:
        if op == "q":
            ops.add()
            if (u, v) not in memo:
                memo[(u, v)] = bfs_reach(g, u, v, ops)
            ans.append(memo[(u, v)])
        else:
            (g.add(u, v) if op == "i" else remove_edge(g, u, v)); ops.add()
            if memo:
                memo.clear()
    costs["S4_memo"], answers["S4_memo"] = ops.n, ans
    ref = answers["S1_bfs"]
    for k, a in answers.items():
        assert a == ref, f"{k} gives wrong answers"
    return costs


def main():
    rng = random.Random(SEED)
    n = 1024
    g0 = gnp(n, 0.9, rng)  # just below the giant-SCC threshold: varied reach sets
    tc = TCBitsets(g0)
    reach_size = [bin(tc.reach[tc.comp[v]]).count("1") for v in range(n)]
    s_big = max(range(n), key=lambda v: reach_size[v])
    unreach = [t for t in range(n) if not (tc.reach[tc.comp[s_big]] >> t) & 1]
    rows = []
    L = 4000
    for name, qf, df, rep, adv in [
        ("query_only_uniform", 1.0, 0.0, False, None),
        ("query_only_repetitive", 1.0, 0.0, True, None),
        ("query_only_adversarial", 1.0, 0.0, False, (s_big, unreach)),
        ("99q_1ins_uniform", 0.99, 0.0, False, None),
        ("90q_10ins_uniform", 0.90, 0.0, False, None),
        ("90q_10ins_adversarial", 0.90, 0.0, False, (s_big, unreach)),
        ("90q_10mixed(50%del)_adversarial", 0.90, 0.5, False, (s_big, unreach)),
        ("50q_50mixed(50%del)_uniform", 0.50, 0.5, False, None),
        ("90q_10mixed(50%del)_repetitive", 0.90, 0.5, True, None),
    ]:
        stream = make_stream(g0, L, qf, df, rep, adv, rng)
        c = run_stream(g0, stream)
        best = min(c, key=c.get)
        rows.append({"workload": name, "ops": L, "costs": c, "best": best})
        print(f"{name:34s} " + " ".join(f"{k}={v:10d}" for k, v in c.items()) + f"  best={best}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp005.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-005", "seed": SEED, "n": n,
                   "reach_of_adversarial_source": reach_size[s_big],
                   "env": env_info(), "rows": rows}, f, indent=1)
    print("adversarial source reach size:", reach_size[s_big])


if __name__ == "__main__":
    main()
