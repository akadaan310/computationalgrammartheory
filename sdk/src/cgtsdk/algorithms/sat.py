"""SAT-related baselines for Chapter 14 (CGT-PROP-006, CGT-EXP-006).

* two_sat: Aspvall, Plass & Tarjan (1979) -- satisfiability of 2-CNF in
  linear time via strongly connected components of the implication graph
  (a tractable *restricted class*, mechanism M-RESTRICT).
* solution_automaton: the layered deterministic automaton of satisfying
  assignments of a CNF under the natural variable order, built by
  deduplicating residual clause sets.  Its size is an upper bound on the
  minimal width; it can grow exponentially, which is the point.
* brute_force_count: exhaustive oracle for tests.

Literals are non-zero integers: +i means x_i, -i means not x_i (1-based).
"""
from __future__ import annotations

import itertools
from typing import FrozenSet, List, Optional, Sequence, Tuple

from ..cost import Cost, null_cost
from .graph import tarjan_scc


def two_sat(nvars: int, clauses: Sequence[Tuple[int, int]], cost: Optional[Cost] = None):
    """Return a satisfying assignment (list of bools, index i-1 for x_i) or None."""
    cost = cost or null_cost()
    node = lambda lit: 2 * (abs(lit) - 1) + (lit < 0)   # x_i -> 2(i-1), not x_i -> 2(i-1)+1
    adj: List[List[int]] = [[] for _ in range(2 * nvars)]
    for a, b in clauses:                                 # (a or b) == (not a -> b) and (not b -> a)
        adj[node(-a)].append(node(b)); adj[node(-b)].append(node(a))
        cost.add("edge", 2)
    comp, _ = tarjan_scc(adj, cost)
    out = []
    for i in range(nvars):
        if comp[2 * i] == comp[2 * i + 1]:
            return None
        # comps are numbered in reverse topological order: x_i true iff comp(x_i) < comp(not x_i)
        out.append(comp[2 * i] < comp[2 * i + 1])
    return out


def satisfies(assign: Sequence[bool], clauses) -> bool:
    return all(any((l > 0) == assign[abs(l) - 1] for l in c) for c in clauses)


def brute_force_count(nvars: int, clauses) -> int:
    return sum(satisfies(bits, clauses) for bits in itertools.product((False, True), repeat=nvars))


def _assign(state: FrozenSet[FrozenSet[int]], lit: int):
    out = []
    for c in state:
        if lit in c:
            continue
        if -lit in c:
            c = c - {-lit}
            if not c:
                return None
        out.append(c)
    return frozenset(out)


def solution_automaton(nvars: int, clauses, cap: int = 2_000_000, cost: Optional[Cost] = None):
    """Layer widths, number of models (None if the cap was hit) and total nodes."""
    cost = cost or null_cost()
    layer = {frozenset(frozenset(c) for c in clauses): 1}
    widths, nodes = [1], 1
    for i in range(1, nvars + 1):
        nxt = {}
        for st, cnt in layer.items():
            for lit in (i, -i):
                cost.add("rule", 1)
                r = _assign(st, lit)
                if r is not None:
                    nxt[r] = nxt.get(r, 0) + cnt
        layer = nxt
        widths.append(len(layer)); nodes += len(layer)
        if nodes > cap:
            return widths, None, nodes
    return widths, layer.get(frozenset(), 0), nodes
