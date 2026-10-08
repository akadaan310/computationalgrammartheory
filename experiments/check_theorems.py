"""Exhaustive small-case checks of the exact statements in RESULTS.md.
These checks are not proofs. They guard against mis-stated formulas.

  THM-001(b)  product orbit on C_n x Z_k has size n*k when gcd(n,k)=1
  THM-002     bipartite family has 2^(ab) distinct reachability relations
  THM-003     heap-label LCA / ancestor agree with pointer definitions
  THM-005(a)  relabel at depth d in full binary tree T_h: d+1 new rules,
              live minimal DAG h+d+1
  THM-005(b)  k spread leaves relabelled: minimal DAG >= k(h+1-ceil(log2 k))

Run:  python3 experiments/check_theorems.py
"""
from __future__ import annotations

import itertools
import os
import math

from cgt.core import DFA, OperationalGrammar, Ops
from cgt.forests import DagGrammar, Explicit, full_binary
from cgt.graphs import DiGraph, bfs_reach


def thm001b():
    for n in range(1, 25):
        for k in range(1, 8):
            moves = {"a": lambda i, n=n: [(i + 1) % n]}
            D = DFA(set(range(k)), 0, {0}, {(q, "a"): (q + 1) % k for q in range(k)})
            G = OperationalGrammar(["a"], moves, D, Ops())
            ans = G.constrained_reach(0)
            if math.gcd(n, k) == 1:
                assert G.explored == n * k and ans == set(range(n)), (n, k)
            else:
                assert G.explored == n * k // math.gcd(n, k)
    print("THM-001(b) ok")


def thm002():
    for a, b in ((1, 1), (1, 2), (2, 2), (2, 3)):
        X, Y = range(a), range(a, a + b)
        pairs = [(x, y) for x in X for y in Y]
        rels = set()
        for mask in range(1 << len(pairs)):
            S = {pairs[i] for i in range(len(pairs)) if mask >> i & 1}
            g = DiGraph(a + b)
            for u, v in S:
                g.add(u, v)
            R = frozenset((s, t) for s in range(a + b) for t in range(a + b)
                          if s != t and bfs_reach(g, s, t, Ops()))
            assert R == S  # reachability relation of G_S is exactly S
            rels.add(R)
        assert len(rels) == 2 ** (a * b)
    print("THM-002 ok")


def thm003():
    # all binary trees with up to 7 nodes, given as sets of addresses closed under prefix
    def trees(n):
        def grow(nodes):
            if len(nodes) == n:
                yield nodes; return
            for v in sorted(nodes):
                for b in "01":
                    if v + b not in nodes and v + b > max(nodes):
                        yield from grow(nodes | {v + b})
        # canonical generation can repeat; dedupe
        seen = set()
        for t in grow(frozenset({""})):
            if t not in seen:
                seen.add(t); yield t
    count = 0
    for n in range(1, 8):
        for t in trees(n):
            count += 1
            nu = {w: int("1" + w, 2) for w in t}
            for u, v in itertools.product(t, t):
                lcp = os.path.commonprefix([u, v])
                a, b = nu[u], nu[v]
                da, db = a.bit_length(), b.bit_length()
                if da > db: a >>= da - db
                elif db > da: b >>= db - da
                assert a >> (a ^ b).bit_length() == nu[lcp]
                anc = v.startswith(u)
                db_, da_ = nu[v].bit_length(), nu[u].bit_length()
                assert anc == (db_ >= da_ and nu[v] >> (db_ - da_) == nu[u])
    print(f"THM-003 ok ({count} trees)")


def thm005():
    for h in range(1, 7):
        F = Explicit(); F.roots.append(full_binary(F, h))
        n = F.n
        for i in range(n):  # every node, every depth
            D = DagGrammar.from_explicit(F)
            assert D.live_size() == h + 1
            ops = Ops()
            path, _ = D.access(i, ops)
            d = len(path) - 1
            created = D.relabel(i, "fresh", ops)
            assert created == d + 1, (h, i, created, d)
            assert D.live_size() == h + d + 1, (h, i, D.live_size(), d)
        # (b) spread leaves: leaves are the last 2^h nodes in heap order; preorder
        for k in (1, 2, 3, 4, 5, 8):
            if k > 2 ** h:
                continue
            D = DagGrammar.from_explicit(F)
            # preorder ranks of leaves, spread across the subtrees at depth ceil(log2 k)
            leaves = []
            st, pre = list(F.roots), []
            while st:
                v = st.pop(); pre.append(v); st.extend(reversed(F.children[v]))
            leaf_ranks = [r for r, v in enumerate(pre) if not F.children[v]]
            step = len(leaf_ranks) // (2 ** math.ceil(math.log2(k))) if k > 1 else 1
            chosen = [leaf_ranks[j * step] for j in range(k)]
            for j, r in enumerate(chosen):
                D.relabel(r, f"f{j}", Ops())
            assert D.live_size() >= k * (h + 1 - math.ceil(math.log2(k))), (h, k)
    print("THM-005 ok")


def thm004c():
    """Corrected statement (audit E-001): Jacobi productive rounds are l-1
    (right-linear) and ceil(log2 l) (doubling), +1 confirming round."""
    import random
    from collections import deque
    from exp007_grammar_shape import jacobi_depth, path_graph
    from cgt.graphs import gnp, random_dag
    rng = random.Random(41)
    graphs = [path_graph(n) for n in (2, 3, 5, 17, 64)]
    graphs += [gnp(40, 1.5, rng) for _ in range(20)] + [random_dag(40, 2.0, rng) for _ in range(20)]
    for g in graphs:
        # l = max over (u,v) in P+ of the shortest *positive-length* u->v path
        ell = 0
        for s in range(g.n):
            dist = {}
            dq = deque()
            for v in g.adj[s]:
                if v not in dist:
                    dist[v] = 1; dq.append(v)
            while dq:
                u = dq.popleft()
                for v in g.adj[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1; dq.append(v)
            ell = max([ell] + list(dist.values()))
        if ell == 0:
            continue
        lin, dbl = jacobi_depth(g, False), jacobi_depth(g, True)
        assert lin == (ell - 1) + 1, (lin, ell)
        assert dbl == math.ceil(math.log2(ell)) + 1, (dbl, ell)
    print(f"THM-004(c) ok ({len(graphs)} graphs)")


def thm007():
    """THM-007 (lower bound for compiled moves on arbitrary trees): the
    domains dom⟦L⟧ over binary trees with n nodes take at least 2^floor(n/2)
    distinct values (caterpillar family), checked exactly for n <= 11 by
    enumerating all binary trees (as prefix-closed address sets)."""
    def trees(n):
        # all binary trees with n nodes as frozensets of addresses
        if n == 0:
            yield frozenset(); return
        for k in range(n):
            for lt in trees(k):
                for rt in trees(n - 1 - k):
                    yield frozenset({""} | {"0" + a for a in lt} | {"1" + a for a in rt})
    for n in range(1, 12):
        doms = set()
        for t in trees(n):
            doms.add(frozenset(a for a in t if a + "0" in t))
        assert len(doms) >= 2 ** (n // 2), (n, len(doms))
        # caterpillar family alone attains 2^floor(n/2)
        cat = set()
        half = n // 2
        for mask in range(1 << half):
            leaves = [i for i in range(half) if mask >> i & 1]
            spine = n - len(leaves)
            t = {"1" * i for i in range(spine)} | {"1" * i + "0" for i in leaves}
            assert len(t) == n
            cat.add(frozenset(a for a in t if a + "0" in t))
        assert len(cat) == 2 ** half, (n, len(cat))
    print("THM-007 ok (n <= 11, all binary trees enumerated)")


if __name__ == "__main__":
    thm007()
    thm004c()
    thm001b(); thm002(); thm003(); thm005()
