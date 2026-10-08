"""CGT-EXP-001  Binary tree navigation under four representations.

Hypothesis H-001 (see HYPOTHESES.md): an address grammar whose words have an
arithmetic numeration (heap numbering) answers ancestor/LCA queries in O(1)
word-RAM time *without preprocessing*, but only while the tree height is
O(word size); the advantage is a property of the shape class (density
n / 2^(h+1)), not of grammar per se.

Falsification criterion: if heap-arithmetic LCA cost per query grows with n on
complete trees, or if it stays O(1) on path-shaped trees, H-001 is rejected.

Run:  python3 experiments/exp001_binary_tree.py   (deterministic, seed 1)
"""
from __future__ import annotations

import json
import os
import random
import time

from cgt.core import Ops, env_info
from cgt.trees import (AddressNav, HeapNav, IndexNav, PointerNav, complete_tree,
                       path_tree, random_bst, rotate_right_cost)

SEED = 1
SIZES = [2 ** 8, 2 ** 10, 2 ** 12, 2 ** 14, 2 ** 16]
Q = 2000
OUT = os.path.join(os.path.dirname(__file__), "results")


def run_one(shape: str, n: int, rng: random.Random) -> dict:
    t = {"complete": lambda: complete_tree(n),
         "random_bst": lambda: random_bst(n, rng),
         "path": lambda: path_tree(n, rng)}[shape]()
    queries = [(rng.randrange(n), rng.randrange(n)) for _ in range(Q)]
    row = {"shape": shape, "n": n, "height": t.height()}

    reps = {}
    for cls in (PointerNav, HeapNav, IndexNav):
        t0 = time.perf_counter()
        r = cls(t)
        row[f"{r.name}.build_s"] = time.perf_counter() - t0
        row[f"{r.name}.build_ops"] = r.build_ops
        row[f"{r.name}.space_words"] = r.space_words
        reps[r.name] = r
    heap = reps["R2-heap-arith"]
    row["R2.address_space"] = heap.address_space if heap.h < 60 else f"2^{heap.h + 1}"
    row["R2.density"] = n / (2 ** (heap.h + 1) - 1)

    addr = AddressNav(t)
    row["R3.space_chars"] = addr.space_chars
    row["R3.feasible"] = addr.feasible

    # --- LCA queries: correctness + cost, two workloads ------------------
    d0 = reps["R1-pointer"].depth
    hmax = max(d0)
    deep_nodes = [x for x in range(n) if d0[x] >= max(1, (2 * hmax) // 3)]
    workloads = {
        "rand": queries,
        # adversarial for prefix-walking: ancestor pairs deep in the tree,
        # whose LCA (the parent) has a long address
        "deep": [(x, t.parent[x]) for x in
                 (deep_nodes[rng.randrange(len(deep_nodes))] for _ in range(Q))],
    }
    ops = Ops()
    for wl, qs in workloads.items():
        truth = []
        t0 = time.perf_counter()
        for u, v in qs:
            truth.append(reps["R1-pointer"].lca(u, v, ops))
        row[f"{wl}.R1.lca_s_per_q"] = (time.perf_counter() - t0) / Q
        row[f"{wl}.R1.lca_ops_per_q"] = ops.reset() / Q

        t0 = time.perf_counter()
        res = [heap.lca(u, v, ops) for u, v in qs]
        row[f"{wl}.R2.lca_s_per_q"] = (time.perf_counter() - t0) / Q
        row[f"{wl}.R2.lca_ops_per_q"] = ops.reset() / Q
        assert res == [heap.idx[x] for x in truth], "heap LCA mismatch"

        idx = reps["R4-euler-sparse"]
        t0 = time.perf_counter()
        res = [idx.lca(u, v, ops) for u, v in qs]
        row[f"{wl}.R4.lca_s_per_q"] = (time.perf_counter() - t0) / Q
        row[f"{wl}.R4.lca_ops_per_q"] = ops.reset() / Q
        assert res == truth, "index LCA mismatch"

        if addr.feasible:
            t0 = time.perf_counter()
            res = [addr.lca_addr(u, v, ops) for u, v in qs]
            row[f"{wl}.R3.lca_s_per_q"] = (time.perf_counter() - t0) / Q
            row[f"{wl}.R3.lca_ops_per_q"] = ops.reset() / Q
            assert res == [addr.addr[x] for x in truth], "address LCA mismatch"
        if wl == "rand":
            rand_truth = truth
    truth = rand_truth

    # --- ancestor queries agree ------------------------------------------
    for u, v in queries[:500]:
        a = reps["R1-pointer"].is_ancestor(u, v, ops)
        assert a == heap.is_ancestor(u, v, ops) == idx.is_ancestor(u, v, ops)
    ops.reset()

    # --- path retrieval: output size dominates all representations -------
    d = reps["R1-pointer"].depth
    row["path_output_mean"] = sum(d[u] + d[v] - 2 * d[w]
                                  for (u, v), w in zip(queries, truth)) / Q

    # --- update: rotation at the root ------------------------------------
    if t.left[0] >= 0:
        row.update({f"rot.{k}": v for k, v in rotate_right_cost(t, 0).items()})
    return row


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for shape in ("complete", "random_bst", "path"):
        for n in SIZES:
            if shape == "path" and n > 2 ** 14:
                continue  # heap numbers of 2^16 bits are fine, but R1 is O(n) per query
            r = run_one(shape, n, rng)
            rows.append(r)
            for wl in ("rand", "deep"):
                print(f"{shape:10s} {wl} n={n:6d} h={r['height']:6d} "
                      f"ops/q R1={r[wl + '.R1.lca_ops_per_q']:8.1f} "
                      f"R2={r[wl + '.R2.lca_ops_per_q']:7.1f} "
                      f"R3={r.get(wl + '.R3.lca_ops_per_q', float('nan')):8.1f} "
                      f"R4={r[wl + '.R4.lca_ops_per_q']:4.1f} | "
                      f"us/q R1={1e6 * r[wl + '.R1.lca_s_per_q']:7.2f} "
                      f"R2={1e6 * r[wl + '.R2.lca_s_per_q']:5.2f} "
                      f"R4={1e6 * r[wl + '.R4.lca_s_per_q']:5.2f} | "
                      f"build R4={r['R4-euler-sparse.build_ops']:9d} "
                      f"density={r['R2.density']:.3g}")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp001.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-001", "seed": SEED, "queries": Q,
                   "env": env_info(), "rows": rows}, f, indent=1, default=str)


if __name__ == "__main__":
    main()
