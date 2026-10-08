"""Core objects of the provisional CGT formalism (see DEFINITIONS.md).

Everything here is deliberately small and dependency-free (Python stdlib only)
so that each definition in DEFINITIONS.md has an executable counterpart.

CGT-DEF-003  Operational grammar  G = (Sigma, A, [[.]], L)
    Sigma : finite set of move symbols
    A     : carrier (states / positions of a structure)
    [[a]] : A -> set(A) for each a in Sigma  (relational semantics)
    L     : admissibility language over Sigma, given by a DFA (None = Sigma*)

Words w in Sigma* are *operation expressions*; their semantics is the
relational composition [[w]] = [[a1]] ; ... ; [[ak]]  (CGT-PROP-001).
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Hashable, Iterable, List, Optional, Set, Tuple


class Ops:
    """Elementary-step counter.  Experiments report counted steps (model-level
    cost) in addition to wall-clock time, because CPython wall-clock time is
    dominated by interpreter constants that say little about asymptotics."""

    def __init__(self) -> None:
        self.n = 0

    def add(self, k: int = 1) -> None:
        self.n += k

    def reset(self) -> int:
        v, self.n = self.n, 0
        return v


@dataclass
class DFA:
    """Deterministic finite automaton over move symbols (partial transitions)."""

    states: Set[Hashable]
    start: Hashable
    accept: Set[Hashable]
    delta: Dict[Tuple[Hashable, str], Hashable]

    def step(self, q, a):
        return self.delta.get((q, a))

    def accepts(self, word: Iterable[str]) -> bool:
        q = self.start
        for a in word:
            q = self.step(q, a)
            if q is None:
                return False
        return q in self.accept

    def is_live_prefix(self, q) -> bool:  # used for admissibility pruning
        return q is not None


@dataclass
class OperationalGrammar:
    sigma: List[str]
    moves: Dict[str, Callable[[Hashable], Iterable[Hashable]]]
    admissible: Optional[DFA] = None
    ops: Ops = field(default_factory=Ops)

    # --- syntax -----------------------------------------------------------
    def is_admissible(self, word: List[str]) -> bool:
        if any(a not in self.moves for a in word):
            return False
        return True if self.admissible is None else self.admissible.accepts(word)

    # --- semantics --------------------------------------------------------
    def apply(self, word: List[str], x) -> Set:
        """[[w]](x): relational image of x under the word (no admissibility)."""
        cur = {x}
        for a in word:
            nxt = set()
            for y in cur:
                for z in self.moves[a](y):
                    self.ops.add()
                    nxt.add(z)
            cur = nxt
            if not cur:
                break
        return cur

    # --- execution: language-constrained reachability ---------------------
    def constrained_reach(self, x) -> Set:
        """{ y : exists w in L with y in [[w]](x) }  via the product of the
        structure's transition relation with the admissibility DFA.
        Explores at most |A| * |Q| product states (CGT-PROP-003)."""
        if self.admissible is None:
            raise ValueError("no admissibility language")
        D = self.admissible
        seen = {(x, D.start)}
        dq = deque(seen)
        out = set()
        while dq:
            y, q = dq.popleft()
            self.ops.add()
            if q in D.accept:
                out.add(y)
            for a in self.sigma:
                q2 = D.step(q, a)
                if q2 is None:  # grammar prunes the move before it is executed
                    continue
                for z in self.moves[a](y):
                    self.ops.add()
                    if (z, q2) not in seen:
                        seen.add((z, q2))
                        dq.append((z, q2))
        self.explored = len(seen)
        return out


def timeit(fn, *args, repeat: int = 5):
    """Median wall-clock seconds of fn(*args) over `repeat` runs, plus result."""
    ts, res = [], None
    for _ in range(repeat):
        t0 = time.perf_counter()
        res = fn(*args)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2], res


def env_info() -> dict:
    import platform
    import sys

    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
