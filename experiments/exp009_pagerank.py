"""CGT-EXP-009  PageRank: convergence, certification, updates, representation.

Hypotheses:
  H-014  Power iteration meets the a-priori iteration bound
         k* = ⌈log(tol·(1−α)/2) / log α⌉ (CGT-PROP-009) on every instance, and
         the a-posteriori bound α/(1−α)·‖x_k − x_{k−1}‖₁ dominates the true
         error (CGT-THM-008).  Observed iterations are typically well below k*.
  H-015  Gauss–Seidel needs fewer sweeps than power iteration (no guarantee
         claimed; measured).
  H-016  After k edge insertions, a warm start saves iterations, and the
         saving shrinks as k grows (incremental reuse = M-PRE with
         invalidation).
  H-017  Exploiting block (host) structure is a *representation/ordering*
         effect: it does not change the per-iteration cost Θ(n + m).

Falsification: any instance violating k* or the a-posteriori bound falsifies
our implementation or the theorem; H-015/H-016 are falsified by measurements
showing the opposite.

Run:  python3 experiments/exp009_pagerank.py
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "src"))

from cgtsdk import Cost  # noqa: E402
from cgtsdk.algorithms import pagerank_exact, pagerank_gauss_seidel, pagerank_power  # noqa: E402
from cgt.core import env_info  # noqa: E402

SEED = 9
OUT = os.path.join(os.path.dirname(__file__), "results")


def copying_graph(n, d, p_copy, dangling_frac, rng):
    """Directed copying model: each new vertex links to d targets; each target
    is copied from a random earlier vertex's out-links with prob p_copy, else
    uniform.  A fraction of vertices is made dangling (no out-links)."""
    adj = [[] for _ in range(n)]
    for v in range(1, n):
        for _ in range(d):
            u = rng.randrange(v)
            if adj[u] and rng.random() < p_copy:
                t = rng.choice(adj[u])
            else:
                t = rng.randrange(v)
            if t != v and t not in adj[v]:
                adj[v].append(t)
    for v in rng.sample(range(n), int(dangling_frac * n)):
        adj[v] = []
    return adj


def block_graph(n, hosts, d, p_in, rng):
    adj = [[] for _ in range(n)]
    size = n // hosts
    for v in range(n):
        h = v // size
        for _ in range(d):
            if rng.random() < p_in:
                t = h * size + rng.randrange(size)
            else:
                t = rng.randrange(n)
            if t != v and t < n:
                adj[v].append(t)
    return adj


def kstar(alpha, tol):
    return math.ceil(math.log(tol * (1 - alpha) / 2) / math.log(alpha)) if alpha > 0 else 1


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def convergence(rng):
    rows = []
    for gname, make, n in (("copying_n300", lambda: copying_graph(300, 4, 0.6, 0.1, rng), 300),
                           ("block_n300", lambda: block_graph(300, 10, 4, 0.9, rng), 300)):
        adj = make()
        for alpha in (0.5, 0.85, 0.9, 0.95, 0.99):
            tol = 1e-10
            exact = pagerank_exact(adj, alpha)
            cp, cg = Cost(), Cost()
            pw = pagerank_power(adj, alpha, tol=tol, cost=cp)
            gs = pagerank_gauss_seidel(adj, alpha, tol=tol * (1 - alpha), cost=cg)
            err_pw, err_gs = l1(pw.scores, exact), l1(gs.scores, exact)
            assert pw.iterations <= kstar(alpha, tol), "a-priori bound violated"
            assert err_pw <= pw.error_bound + 1e-15, "a-posteriori bound violated"
            rows.append({"graph": gname, "n": n, "m": sum(map(len, adj)), "alpha": alpha,
                         "kstar": kstar(alpha, tol), "power_iters": pw.iterations,
                         "power_err": err_pw, "power_bound": pw.error_bound,
                         "gs_sweeps": gs.iterations, "gs_err": err_gs,
                         "power_edge_ops": cp.counts.get("edge", 0),
                         "gs_edge_ops": cg.counts.get("edge", 0)})
    return rows


def updates(rng):
    rows = []
    n = 3000
    base_adj = copying_graph(n, 5, 0.6, 0.05, rng)
    base = pagerank_power(base_adj, 0.85, tol=1e-9)
    for k in (1, 10, 100, 1000, 10000):
        adj = [list(a) for a in base_adj]
        for _ in range(k):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                adj[u].append(v)
        cc, cw = Cost(), Cost()
        cold = pagerank_power(adj, 0.85, tol=1e-9, cost=cc)
        warm = pagerank_power(adj, 0.85, tol=1e-9, x0=base.scores, cost=cw)
        assert l1(cold.scores, warm.scores) < 1e-8
        rows.append({"n": n, "insertions": k, "cold_iters": cold.iterations,
                     "warm_iters": warm.iterations, "cold_edge_ops": cc.counts["edge"],
                     "warm_edge_ops": cw.counts["edge"], "l1_shift_from_base": l1(base.scores, cold.scores)})
    return rows


def ordering(rng):
    """Same graph, two vertex orderings: iteration count and per-iteration
    edge operations of power iteration are invariant (it is a permutation of
    the same linear map); only memory locality could differ (not modelled)."""
    n = 2000
    adj = block_graph(n, 20, 5, 0.9, rng)
    perm = list(range(n)); rng.shuffle(perm)
    inv = [0] * n
    for i, p in enumerate(perm):
        inv[p] = i
    padj = [[] for _ in range(n)]
    for u in range(n):
        padj[perm[u]] = [perm[v] for v in adj[u]]
    c1, c2 = Cost(), Cost()
    a = pagerank_power(adj, 0.85, tol=1e-10, cost=c1)
    b = pagerank_power(padj, 0.85, tol=1e-10, cost=c2)
    diff = max(abs(a.scores[u] - b.scores[perm[u]]) for u in range(n))
    g1, g2 = Cost(), Cost()
    ga = pagerank_gauss_seidel(adj, 0.85, tol=1e-11, cost=g1)
    gb = pagerank_gauss_seidel(padj, 0.85, tol=1e-11, cost=g2)
    # Gauss–Seidel on a DAG (the copying graph links only to earlier
    # vertices): sweeping in reverse topological order of the *link* direction
    # (sources of in-links first) vs the natural order.
    dag = copying_graph(n, 5, 0.6, 0.05, rng)
    rev = [[n - 1 - v for v in dag[n - 1 - u]] for u in range(n)]  # relabel u -> n-1-u
    d1, d2 = Cost(), Cost()
    nat = pagerank_gauss_seidel(dag, 0.85, tol=1e-11, cost=d1)
    rvs = pagerank_gauss_seidel(rev, 0.85, tol=1e-11, cost=d2)
    pdag = pagerank_power(dag, 0.85, tol=1e-10)
    dag_rows = [{"n": n, "ordering": "DAG natural (in-links from later vertices)", "gs_sweeps": nat.iterations,
                 "power_iters": pdag.iterations},
                {"n": n, "ordering": "DAG reversed (in-links from earlier vertices)", "gs_sweeps": rvs.iterations,
                 "max_score_diff": max(abs(nat.scores[u] - rvs.scores[n - 1 - u]) for u in range(n))}]
    return dag_rows + [{"n": n, "ordering": "block-contiguous", "power_iters": a.iterations,
             "power_edge_ops": c1.counts["edge"], "gs_sweeps": ga.iterations},
            {"n": n, "ordering": "random-permuted", "power_iters": b.iterations,
             "power_edge_ops": c2.counts["edge"], "gs_sweeps": gb.iterations,
             "max_score_diff": diff}]


def main():
    rng = random.Random(SEED)
    conv, upd, order = convergence(rng), updates(rng), ordering(rng)
    for r in conv + upd + order:
        print({k: (f"{v:.3g}" if isinstance(v, float) else v) for k, v in r.items()})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp009.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-009", "seed": SEED, "env": env_info(),
                   "convergence": conv, "updates": upd, "ordering": order}, f, indent=1)


if __name__ == "__main__":
    main()
