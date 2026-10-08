"""Grammar-driven algorithms: product reachability (CGT-THM-001) and path
grammar fixpoints (CGT-THM-004)."""
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from ..automata import DFA
from ..cost import Cost, null_cost

if TYPE_CHECKING:  # pragma: no cover
    from ..structures.graphs import GraphStructure


def product_reach(g: "GraphStructure", x: int, dfa: DFA, cost: Optional[Cost] = None,
                  return_explored: bool = False):
    """{ y : some walk x ⇝ y has its label word in ℒ(dfa) } by BFS on the
    product A × Q.  Explores ≤ |Q|·n states; THM-001(b) shows this bound is
    attained, THM-001(c) that it can also prune almost everything."""
    cost = cost or null_cost()
    start = (x, dfa.start)
    seen = {start}
    dq = deque([start])
    out: Set[int] = set()
    labels = sorted(set(g.labels) & set(dfa.alphabet))
    while dq:
        y, q = dq.popleft(); cost.add("read", 1)
        if q in dfa.accept:
            out.add(y)
        for a in labels:
            cost.add("rule", 1)
            q2 = dfa.step(q, a)
            if q2 is None:
                continue          # the grammar prunes the move before it is executed
            for z in g.out[a][y]:
                cost.add("edge", 1)
                if (z, q2) not in seen:
                    seen.add((z, q2)); dq.append((z, q2))
    return (out, len(seen)) if return_explored else out


def path_grammar_closure(adj, shape: str = "linear", cost: Optional[Cost] = None) -> List[Set[int]]:
    """Semi-naive bottom-up evaluation of a path grammar for P⁺.

    ``linear``:   P → E | E P     — rule attempts = m + Σ_{(w,v)∈P⁺} indeg(w)  (THM-004a)
    ``doubling``: P → E | P P     — O(n·|P⁺|) attempts, O(log ℓ) parallel depth
    """
    cost = cost or null_cost()
    if shape not in ("linear", "doubling"):
        raise ValueError("shape is 'linear' or 'doubling'")
    n = len(adj)
    radj: List[List[int]] = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            radj[v].append(u)
    P = [set() for _ in range(n)]
    Pin = [set() for _ in range(n)]
    delta = []
    for u in range(n):
        for v in adj[u]:
            cost.add("rule", 1)
            if v not in P[u]:
                P[u].add(v); Pin[v].add(u); delta.append((u, v))
    while delta:
        new = []
        for w, v in delta:
            if shape == "linear":
                for u in radj[w]:
                    cost.add("rule", 1)
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
            else:
                for u in list(Pin[w]):
                    cost.add("rule", 1)
                    if v not in P[u]:
                        P[u].add(v); Pin[v].add(u); new.append((u, v))
                for z in list(P[v]):
                    cost.add("rule", 1)
                    if z not in P[w]:
                        P[w].add(z); Pin[z].add(w); new.append((w, z))
        delta = new
    return P
