"""Finite automata over *move symbols* (CGT-DEF-003 admissibility languages).

Symbols are identifiers such as ``L``, ``get`` or ``a`` -- not single
characters -- so a regular expression is written with whitespace between
symbols::

    (L | R)* U          # any downward path, then one step up
    get* set            # reads followed by exactly one write

Operators: ``|`` union, juxtaposition = concatenation, postfix ``*``, ``+``,
``?``, parentheses, and ``ε`` (or ``eps``) for the empty word.  The pipeline is
the classical one: Thompson construction -> subset construction -> Moore
partition-refinement minimisation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, FrozenSet, Hashable, Iterable, List, Optional, Sequence, Set, Tuple

from .cost import Cost, null_cost


@dataclass
class DFA:
    """Deterministic automaton with a *partial* transition function."""

    states: Set[Hashable]
    start: Hashable
    accept: Set[Hashable]
    delta: Dict[Tuple[Hashable, str], Hashable]
    alphabet: FrozenSet[str] = frozenset()

    def __post_init__(self):
        if not self.alphabet:
            self.alphabet = frozenset(a for (_, a) in self.delta)

    def step(self, q, a: str):
        return self.delta.get((q, a))

    def run(self, word: Sequence[str], cost: Optional[Cost] = None):
        """Return the state reached, or None if a transition is undefined."""
        cost = cost or null_cost()
        q = self.start
        for a in word:
            cost.add("rule")
            q = self.step(q, a)
            if q is None:
                return None
        return q

    def accepts(self, word: Sequence[str], cost: Optional[Cost] = None) -> bool:
        q = self.run(word, cost)
        return q is not None and q in self.accept

    @property
    def size(self) -> int:
        return len(self.states)

    @staticmethod
    def universal(alphabet: Iterable[str]) -> "DFA":
        alphabet = frozenset(alphabet)
        return DFA({0}, 0, {0}, {(0, a): 0 for a in alphabet}, alphabet)

    def minimize(self) -> "DFA":
        """Moore partition refinement on the reachable, completed automaton."""
        alphabet = sorted(self.alphabet)
        # reachable part
        reach, todo = {self.start}, [self.start]
        while todo:
            q = todo.pop()
            for a in alphabet:
                r = self.step(q, a)
                if r is not None and r not in reach:
                    reach.add(r); todo.append(r)
        SINK = ("__sink__",)
        states = list(reach) + [SINK]

        def nxt(q, a):
            if q == SINK:
                return SINK
            r = self.step(q, a)
            return SINK if r is None else r

        block = {q: (q in self.accept) for q in states}
        while True:
            sig = {q: (block[q],) + tuple(block[nxt(q, a)] for a in alphabet) for q in states}
            ids: Dict[tuple, int] = {}
            new = {q: ids.setdefault(sig[q], len(ids)) for q in states}
            if len(set(new.values())) == len(set(block.values())):
                block = new
                break
            block = new
        sink_block = block[SINK]
        # a block is dead if it cannot reach acceptance; drop dead blocks
        trans = {}
        for q in states:
            for a in alphabet:
                trans[(block[q], a)] = block[nxt(q, a)]
        acc = {block[q] for q in states if q in self.accept}
        live = set(acc)
        changed = True
        while changed:
            changed = False
            for (b, a), c in trans.items():
                if c in live and b not in live:
                    live.add(b); changed = True
        start = block[self.start]
        if start not in live:
            return DFA({0}, 0, set(), {}, frozenset(alphabet))
        renum = {b: i for i, b in enumerate(sorted(live, key=lambda b: (b != start, b)))}
        delta = {(renum[b], a): renum[c] for (b, a), c in trans.items() if b in live and c in live}
        return DFA(set(renum.values()), renum[start], {renum[b] for b in acc if b in live},
                   delta, frozenset(alphabet))


# ---------------------------------------------------------------- regex
_TOKEN = re.compile(r"\s*(?:(\()|(\))|(\|)|(\*)|(\+)|(\?)|([A-Za-z_ε][A-Za-z0-9_]*))")


def _tokens(src: str) -> List[str]:
    out, pos = [], 0
    src = src.strip()
    while pos < len(src):
        m = _TOKEN.match(src, pos)
        if not m or m.end() == pos:
            raise SyntaxError(f"bad regular expression near {src[pos:pos + 10]!r}")
        out.append(next(g for g in m.groups() if g is not None))
        pos = m.end()
    return out


class _NFA:
    def __init__(self):
        self.eps: Dict[int, Set[int]] = {}
        self.sym: Dict[int, List[Tuple[str, int]]] = {}
        self.n = 0

    def new(self) -> int:
        self.n += 1
        return self.n - 1


def _parse(tokens: List[str], nfa: _NFA):
    """Recursive-descent parser producing Thompson fragments (start, end)."""
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def eat(t):
        nonlocal pos
        if peek() != t:
            raise SyntaxError(f"expected {t!r} at token {pos}, found {peek()!r}")
        pos += 1

    def union():
        frags = [concat()]
        while peek() == "|":
            eat("|"); frags.append(concat())
        if len(frags) == 1:
            return frags[0]
        s, e = nfa.new(), nfa.new()
        for a, b in frags:
            nfa.eps.setdefault(s, set()).add(a); nfa.eps.setdefault(b, set()).add(e)
        return s, e

    def concat():
        frags = []
        while peek() not in (None, "|", ")"):
            frags.append(postfix())
        if not frags:  # empty word
            s = nfa.new()
            return s, s
        for (a, b), (c, d) in zip(frags, frags[1:]):
            nfa.eps.setdefault(b, set()).add(c)
        return frags[0][0], frags[-1][1]

    def postfix():
        a, b = atom()
        while peek() in ("*", "+", "?"):
            op = peek(); eat(op)
            s, e = nfa.new(), nfa.new()
            nfa.eps.setdefault(s, set()).add(a)
            nfa.eps.setdefault(b, set()).add(e)
            if op in ("*", "?"):
                nfa.eps[s].add(e)
            if op in ("*", "+"):
                nfa.eps[b].add(a)
            a, b = s, e
        return a, b

    def atom():
        nonlocal pos
        t = peek()
        if t == "(":
            eat("("); f = union(); eat(")")
            return f
        if t is None or t in ("|", ")", "*", "+", "?"):
            raise SyntaxError(f"unexpected {t!r} at token {pos}")
        pos += 1
        s = nfa.new()
        if t in ("ε", "eps"):
            return s, s
        e = nfa.new()
        nfa.sym.setdefault(s, []).append((t, e))
        return s, e

    frag = union()
    if pos != len(tokens):
        raise SyntaxError(f"trailing tokens from {pos}: {tokens[pos:]}")
    return frag


def compile_regex(src: str, alphabet: Optional[Iterable[str]] = None, minimal: bool = True) -> DFA:
    """Compile a symbol-level regular expression to a DFA."""
    nfa = _NFA()
    s, e = _parse(_tokens(src), nfa)
    letters = set(alphabet or ()) | {a for lst in nfa.sym.values() for a, _ in lst}

    def closure(S):
        st, out = list(S), set(S)
        while st:
            q = st.pop()
            for r in nfa.eps.get(q, ()):
                if r not in out:
                    out.add(r); st.append(r)
        return frozenset(out)

    start = closure({s})
    states, todo, delta = {start}, [start], {}
    while todo:
        S = todo.pop()
        for a in letters:
            T = closure({r for q in S for (b, r) in nfa.sym.get(q, ()) if b == a})
            if not T:
                continue
            delta[(S, a)] = T
            if T not in states:
                states.add(T); todo.append(T)
    d = DFA(states, start, {S for S in states if e in S}, delta, frozenset(letters))
    return d.minimize() if minimal else d
