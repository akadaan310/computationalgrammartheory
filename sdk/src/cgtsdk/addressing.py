"""Arithmetic addressing and compiled move words (CGT-DEF-011, THM-006/007).

A structure is *arithmetically addressed* when its elements are numerals and
every move acts on numerals by a map from a class that is closed under
composition, with O(1)-word elements and O(1)-time apply and domain test.
Then any move word compiles once into a single such map and is afterwards
applied in O(1) time -- regardless of its length.

Implemented classes (each with an exhaustive small-case test):

* :class:`AffineMod`     -- x ↦ (a·x + b) mod N.  De Bruijn shifts, cyclic
                            rotations, rings.
* :class:`XorMask`       -- x ↦ x ⊕ c.  Hypercube moves.
* :class:`BoxTranslation`-- x ↦ x + t on a d-dimensional box, partial: the
                            word is defined iff every prefix stays in the box.
* :class:`HeapWord`      -- words over {L, R, U} on the heap-shaped binary
                            tree with nodes 1..n (THM-006): compiled to
                            x ↦ ((x >> k) << j) | c with domain [lo, hi].
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

from .cost import Cost, null_cost


# ----------------------------------------------------------------- affine mod N
@dataclass(frozen=True)
class AffineMod:
    a: int
    b: int
    N: int

    def __call__(self, x: int) -> int:
        return (self.a * x + self.b) % self.N

    def then(self, g: "AffineMod") -> "AffineMod":
        """self first, then g:  g(self(x)) = g.a(a x + b) + g.b."""
        assert self.N == g.N
        return AffineMod((g.a * self.a) % self.N, (g.a * self.b + g.b) % self.N, self.N)

    @staticmethod
    def identity(N: int) -> "AffineMod":
        return AffineMod(1, 0, N)


def debruijn_moves(k: int, m: int):
    """Vertices = words of length m over [k] read as base-k numerals; move
    ``s{a}`` shifts in letter a: x ↦ (k x + a) mod k^m."""
    N = k ** m
    return {f"s{a}": AffineMod(k, a, N) for a in range(k)}


# ----------------------------------------------------------------- hypercube
@dataclass(frozen=True)
class XorMask:
    c: int

    def __call__(self, x: int) -> int:
        return x ^ self.c

    def then(self, g: "XorMask") -> "XorMask":
        return XorMask(self.c ^ g.c)


def hypercube_moves(d: int):
    return {f"f{i}": XorMask(1 << i) for i in range(d)}


# ----------------------------------------------------------------- grids
@dataclass(frozen=True)
class BoxTranslation:
    """Translation by t (a d-vector) on the box Π[0, dims_i), defined at x iff
    every prefix of the compiled word stays inside: x_i + lo_i ≥ 0 and
    x_i + hi_i < dims_i, where lo/hi are the min/max prefix displacements."""

    dims: Tuple[int, ...]
    t: Tuple[int, ...]
    lo: Tuple[int, ...]
    hi: Tuple[int, ...]

    @staticmethod
    def step(dims, axis: int, sign: int) -> "BoxTranslation":
        z = tuple(0 for _ in dims)
        t = tuple(sign if i == axis else 0 for i in range(len(dims)))
        return BoxTranslation(tuple(dims), t, tuple(min(0, v) for v in t), tuple(max(0, v) for v in t))

    @staticmethod
    def identity(dims) -> "BoxTranslation":
        z = tuple(0 for _ in dims)
        return BoxTranslation(tuple(dims), z, z, z)

    def then(self, g: "BoxTranslation") -> "BoxTranslation":
        t = tuple(a + b for a, b in zip(self.t, g.t))
        lo = tuple(min(a, s + b) for a, s, b in zip(self.lo, self.t, g.lo))
        hi = tuple(max(a, s + b) for a, s, b in zip(self.hi, self.t, g.hi))
        return BoxTranslation(self.dims, t, lo, hi)

    def defined(self, x: Sequence[int]) -> bool:
        return all(xi + l >= 0 and xi + h < d for xi, l, h, d in zip(x, self.lo, self.hi, self.dims))

    def __call__(self, x: Sequence[int]) -> Optional[Tuple[int, ...]]:
        return tuple(xi + ti for xi, ti in zip(x, self.t)) if self.defined(x) else None


def grid_moves(dims: Sequence[int]):
    out = {}
    for i in range(len(dims)):
        out[f"+{i}"] = BoxTranslation.step(dims, i, 1)
        out[f"-{i}"] = BoxTranslation.step(dims, i, -1)
    return out


def row_major(x: Sequence[int], dims: Sequence[int]) -> int:
    """The dense numeration of a grid point: density exactly 1."""
    v = 0
    for xi, d in zip(x, dims):
        v = v * d + xi
    return v


def compile_word(moves: dict, word: Iterable[str], identity, cost: Optional[Cost] = None):
    cost = cost or null_cost()
    f = identity
    for a in word:
        f = f.then(moves[a]); cost.add("arith", 1)
    return f


# ----------------------------------------------------------------- heap-shaped trees
@dataclass(frozen=True)
class HeapWord:
    """Compiled form of a word over {L, R, U} on the heap-shaped binary tree
    whose nodes are exactly the numerals 1..n (CGT-THM-006).

    Semantics of the original word at x: follow the moves one by one; the
    word is defined iff every visited numeral lies in [1, n].  Compiled form:
    f(x) = ((x >> k) << j) | c, defined iff lo ≤ x ≤ hi.
    """

    n: int
    k: int
    j: int
    c: int
    lo: int
    hi: int

    @staticmethod
    def compile(word: Iterable[str], n: int, cost: Optional[Cost] = None) -> "HeapWord":
        cost = cost or null_cost()
        k = j = c = 0           # current prefix map  x ↦ ((x >> k) << j) | c
        lo, hi = 1, n           # domain of the empty word
        for a in word:
            cost.add("arith", 4)
            if a == "U":
                if j > 0:       # cancel the last downward step: (y·2+b)>>1 = y
                    j -= 1; c >>= 1
                else:
                    k += 1
                    lo = max(lo, 1 << k)            # need x >> k ≥ 1
            elif a in ("L", "R"):
                j += 1; c = (c << 1) | (a == "R")
            else:
                raise ValueError(f"unknown move {a!r}")
            # every prefix value ((x>>k)<<j)|c must be ≤ n  ⇔  x>>k ≤ (n-c)>>j
            if c > n:
                hi = 0
            else:
                hi = min(hi, ((((n - c) >> j) + 1) << k) - 1)
        return HeapWord(n, k, j, c, lo, hi)

    def defined(self, x: int) -> bool:
        return self.lo <= x <= self.hi

    def __call__(self, x: int, cost: Optional[Cost] = None) -> Optional[int]:
        cost = cost or null_cost()
        cost.add("compare", 2); cost.add("arith", 3)
        if not self.defined(x):
            return None
        return ((x >> self.k) << self.j) | self.c


def heap_walk(word: Iterable[str], x: int, n: int, cost: Optional[Cost] = None) -> Optional[int]:
    """Reference semantics: step-by-step evaluation, Θ(|word|)."""
    cost = cost or null_cost()
    for a in word:
        cost.add("arith", 1); cost.add("compare", 1)
        x = x >> 1 if a == "U" else 2 * x + (a == "R")
        if not 1 <= x <= n:
            return None
    return x
