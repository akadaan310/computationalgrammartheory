"""Range-query structures and lowest common ancestors.

Fenwick trees are a second instance of *arithmetic addressing* (M-ARITH):
the responsibility range of slot i is (i - lowbit(i), i], so navigation is
bit arithmetic on indices rather than pointer chasing (Fenwick 1994).
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ..cost import Cost, null_cost


class Fenwick:
    """Prefix sums with point updates, both O(log n); 1-based internally."""

    def __init__(self, values: Sequence[float], cost: Optional[Cost] = None):
        self.n = len(values)
        self.t = [0] * (self.n + 1)
        c = cost or null_cost()
        for i, v in enumerate(values, 1):   # O(n) build
            self.t[i] += v; c.add("write", 1)
            j = i + (i & -i)
            c.add("arith", 2)
            if j <= self.n:
                self.t[j] += self.t[i]; c.add("write", 1)

    def add(self, i: int, delta: float, cost: Optional[Cost] = None) -> None:
        """a[i] += delta (0-based)."""
        c = cost or null_cost()
        i += 1
        while i <= self.n:
            self.t[i] += delta; c.add("write", 1)
            i += i & -i; c.add("arith", 2)

    def prefix(self, i: int, cost: Optional[Cost] = None) -> float:
        """Sum of a[0..i) ."""
        c = cost or null_cost()
        s = 0
        while i > 0:
            s += self.t[i]; c.add("read", 1)
            i -= i & -i; c.add("arith", 2)
        return s

    def range_sum(self, l: int, r: int, cost: Optional[Cost] = None) -> float:
        """Sum of a[l..r)."""
        return self.prefix(r, cost) - self.prefix(l, cost)


class SegmentTree:
    """Iterative segment tree for an associative operation (default: sum)
    with point assignment.  Leaves at n..2n-1: again a heap numeration."""

    def __init__(self, values: Sequence[float], op: Callable = lambda a, b: a + b,
                 identity: float = 0, cost: Optional[Cost] = None):
        c = cost or null_cost()
        self.n, self.op, self.e = len(values), op, identity
        self.t = [identity] * self.n + list(values)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = op(self.t[2 * i], self.t[2 * i + 1]); c.add("write", 1); c.add("arith", 1)
        if self.n:
            self.t[0] = identity

    def assign(self, i: int, v: float, cost: Optional[Cost] = None) -> None:
        c = cost or null_cost()
        i += self.n
        self.t[i] = v; c.add("write", 1)
        while i > 1:
            i //= 2
            self.t[i] = self.op(self.t[2 * i], self.t[2 * i + 1]); c.add("write", 1); c.add("arith", 2)

    def query(self, l: int, r: int, cost: Optional[Cost] = None) -> float:
        """op over a[l..r)."""
        c = cost or null_cost()
        resl, resr = self.e, self.e
        l += self.n; r += self.n
        while l < r:
            c.add("arith", 2)
            if l & 1:
                resl = self.op(resl, self.t[l]); l += 1; c.add("read", 1)
            if r & 1:
                r -= 1; resr = self.op(self.t[r], resr); c.add("read", 1)
            l //= 2; r //= 2
        return self.op(resl, resr)


class SparseTable:
    """Idempotent range queries (min) in O(1) after O(n log n) build."""

    def __init__(self, values: Sequence, key: Callable = lambda x: x, cost: Optional[Cost] = None):
        c = cost or null_cost()
        self.key = key
        self.rows = [list(values)]
        j = 1
        while (1 << j) <= len(values):
            prev, half = self.rows[-1], 1 << (j - 1)
            row = [min(prev[i], prev[i + half], key=key) for i in range(len(values) - (1 << j) + 1)]
            c.add("compare", len(row)); c.add("write", len(row))
            self.rows.append(row)
            j += 1

    def query(self, l: int, r: int, cost: Optional[Cost] = None):
        """min over values[l..r] (inclusive)."""
        c = cost or null_cost()
        j = (r - l + 1).bit_length() - 1
        c.add("arith", 3); c.add("read", 2); c.add("compare", 1)
        return min(self.rows[j][l], self.rows[j][r - (1 << j) + 1], key=self.key)

    @property
    def size_words(self) -> int:
        return sum(len(r) for r in self.rows)


# =====================================================================
# Lowest common ancestors on a rooted tree given by a parent array
# (parent[root] = -1).  Three schemes, the three of CGT-EXP-001.
# =====================================================================
def _depths(parent: Sequence[int]) -> List[int]:
    n = len(parent)
    depth = [-1] * n
    for v in range(n):
        path = []
        u = v
        while u >= 0 and depth[u] < 0:
            path.append(u); u = parent[u]
        d = -1 if u < 0 else depth[u]
        for x in reversed(path):
            d += 1; depth[x] = d
    return depth


class NaiveLCA:
    """Walk up with parent pointers: O(n) build (depths), O(h) query."""

    def __init__(self, parent: Sequence[int], cost: Optional[Cost] = None):
        self.parent = list(parent)
        self.depth = _depths(parent)
        (cost or null_cost()).add("write", len(parent))

    def query(self, u: int, v: int, cost: Optional[Cost] = None) -> int:
        c = cost or null_cost()
        d, p = self.depth, self.parent
        while d[u] > d[v]:
            u = p[u]; c.add("pointer", 1)
        while d[v] > d[u]:
            v = p[v]; c.add("pointer", 1)
        while u != v:
            u, v = p[u], p[v]; c.add("pointer", 2)
        c.add("compare", 1)
        return u


class EulerLCA:
    """Euler tour + sparse table: O(n log n) build, O(1) query (the simple
    variant of Bender & Farach-Colton 2000)."""

    def __init__(self, parent: Sequence[int], cost: Optional[Cost] = None):
        c = cost or null_cost()
        n = len(parent)
        kids: List[List[int]] = [[] for _ in range(n)]
        roots = []
        for v, p in enumerate(parent):
            (kids[p] if p >= 0 else roots).append(v)
        self.depth = _depths(parent)
        euler, self.first = [], [0] * n
        for r in roots:
            st = [(r, 0)]
            while st:
                v, i = st.pop()
                if i == 0:
                    self.first[v] = len(euler)
                euler.append(v)
                if i < len(kids[v]):
                    st.append((v, i + 1)); st.append((kids[v][i], 0))
        c.add("write", len(euler))
        self.roots = set(roots)
        self.st = SparseTable(euler, key=lambda x: self.depth[x], cost=c)

    def query(self, u: int, v: int, cost: Optional[Cost] = None) -> int:
        l, r = sorted((self.first[u], self.first[v]))
        return self.st.query(l, r, cost)


def heap_lca(a: int, b: int, cost: Optional[Cost] = None, word_bits: int = 64) -> int:
    """LCA of heap numerals a, b ≥ 1 (CGT-THM-003): align depths, XOR,
    shift.  Charged ⌈bits/w⌉ per arithmetic operation."""
    c = cost or null_cost()
    bits = max(a.bit_length(), b.bit_length())
    da, db = a.bit_length(), b.bit_length()
    if da > db:
        a >>= da - db
    elif db > da:
        b >>= db - da
    c.word_arith(bits, 4)
    return a >> (a ^ b).bit_length()
