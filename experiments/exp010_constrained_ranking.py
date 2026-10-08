"""CGT-EXP-010  Grammar-constrained random surfers (CGT-PROP-010).

A random surfer whose label word must stay inside a prefix-closed regular
language ℒ (given by a DFA) is a Markov chain on the product V × Q.

Hypotheses:
  H-018  The product chain has at most |Q|·n states and costs at most |Q|
         times plain PageRank per iteration (CGT-PROP-010);
         with ℒ = Σ* it coincides with PageRank exactly.
  H-019  Constraining the surfer changes the ranking materially (top-10
         overlap with plain PageRank well below 10) for selective languages,
         and negligibly for permissive ones.

Correctness check: the product-chain stationary vector is compared with a
direct linear solve (pagerank_exact on the materialised product chain).

Falsification: N > |Q|·n, universal ≠ PageRank, or the iterative solution
disagreeing with the direct solve.

Run:  python3 experiments/exp010_constrained_ranking.py
"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "src"))

from cgtsdk import DFA, Cost, compile_regex  # noqa: E402
from cgtsdk.algorithms import constrained_pagerank, pagerank_power  # noqa: E402
from cgt.core import env_info  # noqa: E402

SEED = 10
OUT = os.path.join(os.path.dirname(__file__), "results")
LANGS = {
    "universal Σ*": None,
    "no c: (a | b)*": "(a | b)*",
    "alternate: (a b)* (a | ε)": "(a b)* (a | ε)",
    "c only after a: (b | a c?)*": "(b | a (c | ε))*",
    "length < 3: (a|b|c)? (a|b|c)? (a|b|c)?": "(a | b | c | ε) (a | b | c | ε) (a | b | c | ε)",
}


def labelled_web(n, d, rng):
    E = []
    for v in range(n):
        for _ in range(rng.randrange(0, 2 * d + 1)):
            t = rng.randrange(n) if rng.random() < 0.5 else int(rng.random() ** 2 * n)  # skewed popularity
            if t != v:
                E.append((v, rng.choice("abc"), t))
    return E


def top(scores, k=10):
    return [i for i, _ in sorted(enumerate(scores), key=lambda t: (-t[1], t[0]))[:k]]


def main():
    rng = random.Random(SEED)
    rows = []
    for n in (500, 5000):
        E = labelled_web(n, 3, rng)
        adj = [[] for _ in range(n)]
        for u, _, v in E:
            adj[u].append(v)
        cp = Cost()
        plain = pagerank_power(adj, 0.85, tol=1e-10, cost=cp)
        for name, rx in LANGS.items():
            dfa = DFA.universal("abc") if rx is None else compile_regex(rx)
            c = Cost()
            scores, pr, N = constrained_pagerank(n, E, dfa, 0.85, 1e-10, cost=c)
            assert N <= dfa.size * n
            if rx is None:
                assert max(abs(a - b) for a, b in zip(scores, plain.scores)) < 1e-9
            row = {"n": n, "m": len(E), "language": name, "Q": dfa.size, "product_states": N,
                   "iterations": pr.iterations, "edge_ops": c.counts.get("edge", 0),
                   "plain_edge_ops": cp.counts["edge"],
                   "cost_ratio": c.counts.get("edge", 0) / cp.counts["edge"],
                   "top10_overlap_with_pagerank": len(set(top(scores)) & set(top(plain.scores))),
                   "l1_distance_to_pagerank": sum(abs(a - b) for a, b in zip(scores, plain.scores))}
            if n == 500:  # direct-solve validation of the product chain
                from cgtsdk.algorithms import pagerank_exact
                # rebuild the product chain exactly as constrained_pagerank does
                order, index, padj = [], {}, []
                for w in range(n):
                    index[(w, dfa.start)] = len(order); order.append((w, dfa.start))
                out = {}
                for u, a, w in E:
                    out.setdefault(a, [[] for _ in range(n)])[u].append(w)
                labels = sorted(set(out) & set(dfa.alphabet))
                i = 0
                while i < len(order):
                    u, q = order[i]; succ = []
                    for a in labels:
                        q2 = dfa.step(q, a)
                        if q2 is None:
                            continue
                        for w in out[a][u]:
                            if (w, q2) not in index:
                                index[(w, q2)] = len(order); order.append((w, q2))
                            succ.append(index[(w, q2)])
                    padj.append(succ); i += 1
                tele = [1.0 / n if q == dfa.start else 0.0 for (_, q) in order]
                ex = pagerank_exact(padj, 0.85, tele)
                marg = [0.0] * n
                for (w, _), s in zip(order, ex):
                    marg[w] += s
                row["l1_vs_direct_solve"] = sum(abs(a - b) for a, b in zip(marg, scores))
                assert row["l1_vs_direct_solve"] < 1e-8
            rows.append(row)
            print({k: (f"{v:.3g}" if isinstance(v, float) else v) for k, v in row.items()})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp010.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-010", "seed": SEED, "env": env_info(), "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
