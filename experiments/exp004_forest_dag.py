"""CGT-EXP-004  Forest composition: does a structural grammar (minimal DAG)
compress repeated structure, and does the advantage survive access and
update costs?

Hypothesis H-007: the DAG grammar size g is small exactly when the forest has
many repeated *complete* subtrees; access by preorder rank costs O(depth x
degree) instead of O(1); every relabel creates up to depth+1 new rules, so k
updates can grow g by Theta(k * depth) (CGT-PROP-007).

Falsification: H-007 fails if (i) g is small on random forests, (ii) access
cost does not grow with depth, or (iii) updates on a highly shared tree do
not inflate g.

Run:  python3 experiments/exp004_forest_dag.py
"""
from __future__ import annotations

import json
import os
import random

from cgt.core import Ops, env_info
from cgt.forests import (DagGrammar, Explicit, copy_tree, full_binary,
                         monadic_path, random_tree)

SEED = 4
OUT = os.path.join(os.path.dirname(__file__), "results")


def build(fam: str, rng) -> Explicit:
    F = Explicit()
    if fam == "repetitive_forest":
        P = Explicit()
        pool = [random_tree(P, 64, "ab", rng) for _ in range(8)]
        for _ in range(1000):
            F.roots.append(copy_tree(P, F, rng.choice(pool)))
    elif fam == "random_forest":
        for _ in range(1000):
            F.roots.append(random_tree(F, 64, "abcd", rng))
    elif fam == "full_binary_h15":
        F.roots.append(full_binary(F, 15))
    elif fam == "monadic_path":
        F.roots.append(monadic_path(F, 65536))
    return F


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for fam in ("repetitive_forest", "random_forest", "full_binary_h15", "monadic_path"):
        F = build(fam, rng)
        D = DagGrammar.from_explicit(F)
        n = F.n
        row = {"family": fam, "n": n, "dag_nodes": D.live_size(),
               "dag_edges": D.edges_live(), "build_ops": D.build_ops}
        row["compression_ratio"] = (row["dag_nodes"] + row["dag_edges"]) / (2 * n - len(F.roots))
        # correctness of rank access against explicit preorder
        pre = []
        st = list(reversed(F.roots))
        while st:
            v = st.pop(); pre.append(v); st.extend(reversed(F.children[v]))
        ops = Ops()
        qs = [rng.randrange(n) for _ in range(1000)]
        for i in qs:
            path, lab = D.access(i, ops)
            assert lab == F.label[pre[i]]
        row["access_ops_per_q"] = ops.reset() / len(qs)
        row["access_explicit_ops_per_q"] = 1
        # updates: relabel random nodes with fresh labels (adversarial: destroys sharing)
        created, upd_ops = [], 0
        sizes = []
        for k in range(1, 201):
            i = rng.randrange(n)
            created.append(D.relabel(i, f"z{k}", ops))
            if k in (1, 10, 50, 200):
                sizes.append((k, D.live_size()))
        upd_ops = ops.reset()
        row["update_new_rules_mean"] = sum(created) / len(created)
        row["update_ops_mean"] = upd_ops / len(created)
        row["live_dag_after_updates"] = sizes
        # verify a sample after updates
        for i in qs[:200]:
            D.access(i, ops)
        rows.append(row)
        print(f"{fam:18s} n={n:6d} g={row['dag_nodes']:6d} edges={row['dag_edges']:6d} "
              f"ratio={row['compression_ratio']:.4f} access ops/q={row['access_ops_per_q']:8.1f} "
              f"upd new rules={row['update_new_rules_mean']:6.1f} live g after k upd={sizes}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp004.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-004", "seed": SEED, "env": env_info(),
                   "rows": rows}, f, indent=1)


if __name__ == "__main__":
    main()
