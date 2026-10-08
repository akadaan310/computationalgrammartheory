"""Relational and state structures: edge-labelled digraphs and automata.

:class:`GraphStructure` has *relational* semantics: the state is a set of
current vertices S, and a label move ``a`` maps S to ⟦a⟧(S) = {v : u ∈ S,
(u, a, v) ∈ E}.  An empty S is the semantic layer's "undefined"
(⟦w⟧(x) = ∅, CGT-DEF-003).  ``at(v)`` resets S to {v}.
"""
from __future__ import annotations

from typing import Any, Dict, FrozenSet, Hashable, Iterable, List, Optional, Sequence, Set, Tuple

from ..automata import DFA
from ..cost import Cost
from ..grammar import Call, Inadmissible, Move, Structure


class GraphStructure(Structure):
    name = "graph"

    def __init__(self, n: int, edges: Iterable[Tuple[int, str, int]] = ()):
        """Vertices 0..n-1; edges are (u, label, v)."""
        self.n = n
        self.out: Dict[str, List[List[int]]] = {}
        self.m = 0
        for u, a, v in edges:
            self.add_edge(u, a, v)
        self.current: FrozenSet[int] = frozenset({0}) if n else frozenset()

    def add_edge(self, u: int, a: str, v: int) -> None:
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError(f"edge ({u},{a},{v}) outside vertex range")
        if not a.isidentifier():
            raise ValueError(f"edge label {a!r} must be an identifier")
        self.out.setdefault(a, [[] for _ in range(self.n)])[u].append(v)
        self.m += 1

    @classmethod
    def from_unlabelled(cls, n: int, edges: Iterable[Tuple[int, int]], label: str = "e"):
        return cls(n, ((u, label, v) for u, v in edges))

    @property
    def labels(self) -> List[str]:
        return sorted(self.out)

    def signature(self) -> Dict[str, Move]:
        sig = {a: Move(a, (), f"follow all edges labelled {a}") for a in self.labels}
        sig["at"] = Move("at", ("v",), "set the current vertex set to {v}")
        sig["here"] = Move("here", (), "sorted list of current vertices")
        return sig

    def edges(self) -> List[Tuple[int, str, int]]:
        return [(u, a, v) for a in self.labels for u in range(self.n) for v in self.out[a][u]]

    def abstract(self):
        return (self.n, frozenset(self.edges()), self.current)

    def size_words(self) -> int:
        return self.n * max(1, len(self.out)) + 2 * self.m

    @classmethod
    def denote(cls, state, c):
        n, E, S = state
        if c.name == "at":
            v = c.args[0]
            if not isinstance(v, int) or not 0 <= v < n:
                raise Inadmissible(f"no vertex {v!r}")
            return (n, E, frozenset({v})), None
        if c.name == "here":
            return state, sorted(S)
        T = frozenset(v for (u, a, v) in E if a == c.name and u in S)
        if not T:
            raise Inadmissible(f"⟦{c.name}⟧ of the current set is empty")
        return (n, E, T), None

    def apply(self, c, cost):
        if c.name == "at":
            v = c.args[0]
            if not isinstance(v, int) or not 0 <= v < self.n:
                raise Inadmissible(f"no vertex {v!r}")
            cost.add("write", 1)
            self.current = frozenset({v})
            return None
        if c.name == "here":
            cost.add("read", len(self.current))
            return sorted(self.current)
        adj = self.out.get(c.name)
        if adj is None:
            raise Inadmissible(f"no edges labelled {c.name}")
        T = set()
        for u in self.current:
            cost.add("read", 1)
            for v in adj[u]:
                cost.add("edge", 1)
                T.add(v)
        if not T:
            raise Inadmissible(f"⟦{c.name}⟧ of the current set is empty")
        self.current = frozenset(T)
        return None

    # -- constrained resolution (CGT-THM-001) ------------------------------
    def constrained_reach(self, x: int, dfa: DFA, cost: Optional[Cost] = None) -> Set[int]:
        """⟦ℒ⟧(x) by BFS on the product with the DFA: O(|Q|(|Σ|n + m))."""
        from ..algorithms.automata import product_reach
        return product_reach(self, x, dfa, cost)


class AutomatonStructure(Structure):
    """A DFA viewed as a structure: elements are states, moves are letters,
    the cursor is the current state.  ``accepting()`` queries acceptance."""

    name = "automaton"

    def __init__(self, dfa: DFA):
        self.dfa = dfa
        self.state = dfa.start

    def signature(self):
        sig = {a: Move(a, (), f"read letter {a}") for a in sorted(self.dfa.alphabet)}
        sig["accepting"] = Move("accepting", (), "is the current state accepting?")
        sig["reset"] = Move("reset", (), "back to the start state")
        return sig

    def abstract(self):
        return (self.dfa, self.state)

    def size_words(self):
        return len(self.dfa.delta) * 3 + len(self.dfa.states)

    @classmethod
    def denote(cls, state, c):
        dfa, q = state
        if c.name == "accepting":
            return state, q in dfa.accept
        if c.name == "reset":
            return (dfa, dfa.start), None
        r = dfa.step(q, c.name)
        if r is None:
            raise Inadmissible(f"no transition on {c.name} from {q!r}")
        return (dfa, r), None

    def apply(self, c, cost):
        if c.name == "accepting":
            cost.add("read", 1)
            return self.state in self.dfa.accept
        if c.name == "reset":
            cost.add("write", 1)
            self.state = self.dfa.start
            return None
        cost.add("rule", 1)
        r = self.dfa.step(self.state, c.name)
        if r is None:
            raise Inadmissible(f"no transition on {c.name} from {self.state!r}")
        self.state = r
        return None
