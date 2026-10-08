"""Graph algorithms on simple adjacency-list digraphs.

A graph is ``adj: list[list[int]]`` (unweighted) or
``adj: list[list[tuple[int, float]]]`` (weighted).  All functions count
``edge`` inspections and other steps in an optional Cost.
"""
from __future__ import annotations

import heapq
from collections import deque
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ..cost import Cost, null_cost
from .basic import UnionFind

INF = float("inf")


def bfs(adj: Sequence[Sequence[int]], s: int, cost: Optional[Cost] = None) -> List[float]:
    """Hop distances from s (inf if unreachable).  Θ(n + m)."""
    cost = cost or null_cost()
    dist = [INF] * len(adj)
    dist[s] = 0
    dq = deque([s])
    while dq:
        u = dq.popleft(); cost.add("read", 1)
        for v in adj[u]:
            cost.add("edge", 1)
            if dist[v] == INF:
                dist[v] = dist[u] + 1; cost.add("write", 1)
                dq.append(v)
    return dist


def bfs_path(adj, s: int, t: int, cost: Optional[Cost] = None) -> Optional[List[int]]:
    """A shortest (fewest-edges) path s→t, or None.  Witness retrieval."""
    cost = cost or null_cost()
    parent = {s: None}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        if u == t:
            break
        for v in adj[u]:
            cost.add("edge", 1)
            if v not in parent:
                parent[v] = u; dq.append(v)
    if t not in parent:
        return None
    path = [t]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return path[::-1]


def dfs_order(adj, cost: Optional[Cost] = None) -> Tuple[List[int], List[int]]:
    """Iterative DFS over all vertices: (discovery order, finish order)."""
    cost = cost or null_cost()
    n = len(adj)
    seen = [False] * n
    disc, fin = [], []
    for r in range(n):
        if seen[r]:
            continue
        seen[r] = True; disc.append(r)
        st = [(r, 0)]
        while st:
            u, i = st.pop()
            if i < len(adj[u]):
                st.append((u, i + 1))
                v = adj[u][i]; cost.add("edge", 1)
                if not seen[v]:
                    seen[v] = True; disc.append(v)
                    st.append((v, 0))
            else:
                fin.append(u)
    return disc, fin


def topological_sort(adj, cost: Optional[Cost] = None) -> Optional[List[int]]:
    """Kahn (1962).  Returns an order, or None if the graph has a cycle."""
    cost = cost or null_cost()
    n = len(adj)
    indeg = [0] * n
    for u in range(n):
        for v in adj[u]:
            cost.add("edge", 1); indeg[v] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    out = []
    while q:
        u = q.popleft(); out.append(u)
        for v in adj[u]:
            cost.add("edge", 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return out if len(out) == n else None


def tarjan_scc(adj, cost: Optional[Cost] = None) -> Tuple[List[int], int]:
    """Tarjan (1972).  Returns (comp, k): comp[v] in 0..k-1, numbered in
    *reverse topological* order of the condensation (comp 0 is a sink)."""
    cost = cost or null_cost()
    n = len(adj)
    index, low = [-1] * n, [0] * n
    onst = [False] * n
    st: List[int] = []
    comp = [-1] * n
    c = idx = 0
    for r in range(n):
        if index[r] >= 0:
            continue
        work = [(r, 0)]
        while work:
            v, i = work.pop()
            if i == 0:
                index[v] = low[v] = idx; idx += 1
                st.append(v); onst[v] = True
            recurse = False
            while i < len(adj[v]):
                w = adj[v][i]; i += 1; cost.add("edge", 1)
                if index[w] < 0:
                    work.append((v, i)); work.append((w, 0)); recurse = True
                    break
                if onst[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    w = st.pop(); onst[w] = False; comp[w] = c
                    if w == v:
                        break
                c += 1
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
    return comp, c


def transitive_closure(adj, cost: Optional[Cost] = None, word_bits: int = 64) -> List[int]:
    """Reachability rows as Python-int bitsets (bit t of row s ⇔ s ⇝ t,
    reflexive).  SCC condensation + reverse-topological OR; each OR of
    n-bit rows is charged ⌈n/word_bits⌉ word operations."""
    cost = cost or null_cost()
    n = len(adj)
    comp, k = tarjan_scc(adj, cost)
    members = [0] * k
    for v in range(n):
        members[comp[v]] |= 1 << v
    cadj: List[Set[int]] = [set() for _ in range(k)]
    for u in range(n):
        for v in adj[u]:
            cost.add("edge", 1)
            if comp[u] != comp[v]:
                cadj[comp[u]].add(comp[v])
    reach = [0] * k
    for c in range(k):
        r = members[c]
        for d in cadj[c]:
            r |= reach[d]
            cost.word_arith(n)
        reach[c] = r
    return [reach[comp[v]] for v in range(n)]


def dijkstra(wadj, s: int, cost: Optional[Cost] = None) -> List[float]:
    """Dijkstra (1959) with a binary heap; non-negative weights required.
    O((n + m) log n)."""
    cost = cost or null_cost()
    dist = [INF] * len(wadj)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq); cost.add("compare", max(1, len(pq).bit_length()))
        if d > dist[u]:
            continue
        for v, w in wadj[u]:
            if w < 0:
                raise ValueError("Dijkstra requires non-negative weights")
            cost.add("edge", 1); cost.add("compare", 1)
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v)); cost.add("compare", max(1, len(pq).bit_length()))
    return dist


def bellman_ford(wadj, s: int, cost: Optional[Cost] = None) -> Optional[List[float]]:
    """Bellman (1958) / Ford (1956).  O(nm).  Returns None if a negative
    cycle is reachable from s."""
    cost = cost or null_cost()
    n = len(wadj)
    dist = [INF] * n
    dist[s] = 0
    for _ in range(n - 1):
        changed = False
        for u in range(n):
            if dist[u] == INF:
                continue
            for v, w in wadj[u]:
                cost.add("edge", 1); cost.add("compare", 1)
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w; changed = True
        if not changed:
            break
    for u in range(n):
        for v, w in wadj[u]:
            if dist[u] + w < dist[v]:
                return None
    return dist


def kruskal(n: int, edges: Sequence[Tuple[float, int, int]], cost: Optional[Cost] = None):
    """Kruskal (1956): minimum spanning forest of an undirected graph given
    as (w, u, v) triples.  Returns (total weight, chosen edges)."""
    cost = cost or null_cost()
    uf = UnionFind(n, cost)
    total, chosen = 0.0, []
    for w, u, v in sorted(edges):
        cost.add("edge", 1)
        if uf.union(u, v):
            total += w; chosen.append((w, u, v))
    cost.add("compare", int(len(edges) * max(1, len(edges).bit_length())))  # sort, charged m⌈log m⌉
    return total, chosen


def prim(n: int, edges: Sequence[Tuple[float, int, int]], cost: Optional[Cost] = None):
    """Prim (1957) / Jarník: minimum spanning forest with a binary heap."""
    cost = cost or null_cost()
    adj: List[List[Tuple[float, int]]] = [[] for _ in range(n)]
    for w, u, v in edges:
        adj[u].append((w, v)); adj[v].append((w, u))
    seen = [False] * n
    total, chosen = 0.0, []
    for r in range(n):
        if seen[r]:
            continue
        seen[r] = True
        pq = [(w, r, v) for w, v in adj[r]]
        heapq.heapify(pq)
        while pq:
            w, u, v = heapq.heappop(pq); cost.add("compare", max(1, len(pq).bit_length()))
            if seen[v]:
                continue
            seen[v] = True; total += w; chosen.append((w, min(u, v), max(u, v)))
            for w2, x in adj[v]:
                cost.add("edge", 1)
                if not seen[x]:
                    heapq.heappush(pq, (w2, v, x)); cost.add("compare", max(1, len(pq).bit_length()))
    return total, chosen


def floyd_warshall(n: int, wedges, cost: Optional[Cost] = None) -> List[List[float]]:
    """All-pairs shortest paths, Θ(n³): the closed-semiring instance of the
    path grammar P → E | P P evaluated by dynamic programming over the
    allowed intermediate vertices."""
    cost = cost or null_cost()
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in wedges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF:
                continue
            di = d[i]
            for j in range(n):
                cost.add("compare", 1)
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d
