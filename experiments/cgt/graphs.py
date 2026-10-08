"""Directed-graph generators and reachability representations (CGT-EXP-002/005).

Representations
  M1  BFS per query (no preprocessing)
  M2  transitive closure as bitsets over the SCC condensation
  M3  path-grammar fixpoint:  P(u,v) <- E(u,v) | E(u,w) P(w,v)   (right-linear)
                              P(u,v) <- E(u,v) | P(u,w) P(w,v)   (non-linear)
  M4  interval labels (only for forests: the tree grammar itself is the index)
Costs are counted in elementary steps; a bitset OR over n bits costs
ceil(n/64) word operations.
"""
from __future__ import annotations

import random
from collections import deque
from typing import List

W = 64


def wcost(nbits: int) -> int:
    return max(1, -(-nbits // W))


class DiGraph:
    def __init__(self, n: int):
        self.n = n
        self.adj: List[List[int]] = [[] for _ in range(n)]
        self.m = 0

    def add(self, u: int, v: int) -> None:
        self.adj[u].append(v)
        self.m += 1

    def edges(self):
        for u in range(self.n):
            for v in self.adj[u]:
                yield u, v


# ------------------------------------------------------------- generators
def gnp(n: int, avg_deg: float, rng: random.Random) -> DiGraph:
    g = DiGraph(n)
    m = int(avg_deg * n)
    seen = set()
    while len(seen) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v and (u, v) not in seen:
            seen.add((u, v)); g.add(u, v)
    return g


def random_dag(n: int, avg_deg: float, rng: random.Random) -> DiGraph:
    g = DiGraph(n)
    m = int(avg_deg * n)
    seen = set()
    while len(seen) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u < v and (u, v) not in seen:
            seen.add((u, v)); g.add(u, v)
    return g


def random_forest(n: int, roots: int, rng: random.Random) -> DiGraph:
    g = DiGraph(n)
    for v in range(roots, n):
        g.add(rng.randrange(v), v)
    return g


def bipartite_layers(n: int, p: float, rng: random.Random) -> DiGraph:
    """The lower-bound family of CGT-THM-002: A = [0,n/2), B = [n/2,n),
    arbitrary edges A->B.  Reachability = the edge relation itself."""
    g = DiGraph(n)
    a = n // 2
    for u in range(a):
        for v in range(a, n):
            if rng.random() < p:
                g.add(u, v)
    return g


# ------------------------------------------------------------- M1: BFS
def bfs_reach(g: DiGraph, s: int, t: int, ops) -> bool:
    if s == t:
        ops.add(); return True
    seen = bytearray(g.n); seen[s] = 1
    dq = deque([s])
    while dq:
        u = dq.popleft(); ops.add()
        for v in g.adj[u]:
            ops.add()
            if not seen[v]:
                if v == t:
                    return True
                seen[v] = 1; dq.append(v)
    return False


# ------------------------------------------------------------- M2: TC bitsets
def scc(g: DiGraph):
    """Iterative Tarjan. Returns comp[v] numbered in reverse topological order
    (comp 0 is a sink component)."""
    n = g.n
    index, low = [-1] * n, [0] * n
    onst = bytearray(n); st = []
    comp = [-1] * n; c = 0; idx = 0
    for r in range(n):
        if index[r] >= 0:
            continue
        work = [(r, 0)]
        while work:
            v, i = work.pop()
            if i == 0:
                index[v] = low[v] = idx; idx += 1
                st.append(v); onst[v] = 1
            recurse = False
            adj = g.adj[v]
            while i < len(adj):
                w = adj[i]; i += 1
                if index[w] < 0:
                    work.append((v, i)); work.append((w, 0)); recurse = True
                    break
                elif onst[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    w = st.pop(); onst[w] = 0; comp[w] = c
                    if w == v:
                        break
                c += 1
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
    return comp, c


class TCBitsets:
    name = "M2-TC-bitsets"

    def __init__(self, g: DiGraph):
        comp, k = scc(g)
        members = [0] * k
        for v in range(g.n):
            members[comp[v]] |= 1 << v
        cadj = [set() for _ in range(k)]
        for u, v in g.edges():
            if comp[u] != comp[v]:
                cadj[comp[u]].add(comp[v])
        reach = [0] * k
        ops = g.n + g.m
        for c in range(k):  # reverse topological: successors already done
            r = members[c]
            for d in cadj[c]:
                r |= reach[d]; ops += wcost(g.n)
            reach[c] = r
        self.comp, self.reach = comp, reach
        self.build_ops = ops
        self.space_bits = k * g.n

    def query(self, s: int, t: int, ops) -> bool:
        ops.add()
        return (self.reach[self.comp[s]] >> t) & 1 == 1


# ------------------------------------------------------------- M3: path grammar
def path_grammar_fixpoint(g: DiGraph, nonlinear: bool, ops):
    """Semi-naive bottom-up evaluation of the path grammar.  Returns the set of
    derived nonterminal instances P(u,v) (= pairs with a path of length >= 1).
    ops counts attempted rule applications (derivation steps)."""
    n = g.n
    radj = [[] for _ in range(n)]
    for u, v in g.edges():
        radj[v].append(u)
    P = [set() for _ in range(n)]          # P[u] = {v : P(u,v) derived}
    Pin = [set() for _ in range(n)]        # Pin[v] = {u : P(u,v) derived}
    delta = []
    for u, v in g.edges():
        ops.add()
        if v not in P[u]:
            P[u].add(v); Pin[v].add(u); delta.append((u, v))
    while delta:
        new = []
        for (w, v) in delta:
            if not nonlinear:
                # E(u,w) P(w,v) => P(u,v)
                for u in radj[w]:
                    ops.add()
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
            else:
                # P(u,w) P(w,v) => P(u,v)   (new fact used on either side)
                for u in list(Pin[w]):
                    ops.add()
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
                for x in list(P[v]):
                    ops.add()
                    if x not in P[w]:
                        P[w].add(x); Pin[x].add(w); new.append((w, x))
        delta = new
    return P


# ------------------------------------------------------------- M4: intervals
class IntervalLabels:
    """For a forest given as parent->child edges: u reaches v iff
    tin[u] <= tin[v] and tout[v] <= tout[u]  (Agrawal-Borgida-Jagadish 1989)."""

    name = "M4-interval"

    def __init__(self, g: DiGraph):
        n = g.n
        indeg = [0] * n
        for _, v in g.edges():
            indeg[v] += 1
        assert max(indeg) <= 1, "not a forest"
        tin, tout = [0] * n, [0] * n
        clock = 0
        for r in range(n):
            if indeg[r]:
                continue
            st = [(r, 0)]
            while st:
                v, s = st.pop()
                if s == 0:
                    tin[v] = clock; clock += 1
                    st.append((v, 1))
                    for c in g.adj[v]:
                        st.append((c, 0))
                else:
                    tout[v] = clock; clock += 1
        self.tin, self.tout = tin, tout
        self.build_ops = 2 * n + g.m
        self.space_bits = 2 * n * max(1, (2 * n).bit_length())

    def query(self, s: int, t: int, ops) -> bool:
        ops.add()
        return self.tin[s] <= self.tin[t] and self.tout[t] <= self.tout[s]


def tc_greedy_path(g: DiGraph, tc: TCBitsets, s: int, t: int, ops):
    """Path *retrieval* given only the closure, for DAGs: walk to any
    successor that still reaches t.  Cost = sum of out-degrees along the path.
    (On cyclic graphs a greedy walk can dead-end; not used there.)"""
    if not tc.query(s, t, ops):
        return None
    path, u, seen = [s], s, {s}
    while u != t:
        for v in g.adj[u]:
            ops.add()
            if v not in seen and (v == t or tc.query(v, t, ops)):
                u = v; path.append(v); seen.add(v)
                break
        else:  # pragma: no cover - impossible if tc is correct
            raise AssertionError
    return path
