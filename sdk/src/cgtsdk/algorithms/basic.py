"""Searching, sorting, union-find, dynamic programming and string matching.

Every function takes an optional :class:`~cgtsdk.cost.Cost` and counts the
operations named in its docstring.  These are the *classical baselines* of
Part III of the book; each is tested against an independent oracle
(Python's built-ins or brute force) in ``sdk/tests``.
"""
from __future__ import annotations

import random
from typing import Any, Callable, List, Optional, Sequence, Tuple

from ..cost import Cost, null_cost


# ----------------------------------------------------------------- search
def linear_search(a: Sequence[Any], x: Any, cost: Optional[Cost] = None) -> int:
    """Index of the first occurrence of x, or -1.  Θ(n) compares worst case."""
    cost = cost or null_cost()
    for i, v in enumerate(a):
        cost.add("read", 1); cost.add("compare", 1)
        if v == x:
            return i
    return -1


def binary_search(a: Sequence[Any], x: Any, cost: Optional[Cost] = None) -> int:
    """Leftmost index i with a[i] == x in a sorted sequence, or -1.
    Invariant: a[lo-1] < x <= a[hi] (with sentinels).  ⌈log₂(n+1)⌉ + 1
    three-way compares at most."""
    cost = cost or null_cost()
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        cost.add("arith", 2); cost.add("read", 1); cost.add("compare", 1)
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    cost.add("compare", 1)
    return lo if lo < len(a) and a[lo] == x else -1


# ----------------------------------------------------------------- sorting
def insertion_sort(a: Sequence[Any], cost: Optional[Cost] = None) -> List[Any]:
    """Stable; Θ(n²) compares worst case, n-1 on sorted input."""
    cost = cost or null_cost()
    a = list(a)
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        cost.add("read", 1)
        while j >= 0:
            cost.add("compare", 1)
            if a[j] <= x:
                break
            a[j + 1] = a[j]; cost.add("write", 1)
            j -= 1
        a[j + 1] = x; cost.add("write", 1)
    return a


def merge_sort(a: Sequence[Any], cost: Optional[Cost] = None) -> List[Any]:
    """Stable; at most n⌈log₂ n⌉ compares."""
    cost = cost or null_cost()
    a = list(a)
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid], cost), merge_sort(a[mid:], cost)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        cost.add("compare", 1)
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
        cost.add("write", 1)
    rest = left[i:] + right[j:]
    cost.add("write", len(rest))
    return out + rest


def heapsort(a: Sequence[Any], cost: Optional[Cost] = None) -> List[Any]:
    """In-place heapsort (Williams 1964 / Floyd's bottom-up heap
    construction); O(n log n) compares, not stable."""
    cost = cost or null_cost()
    a = list(a)
    n = len(a)

    def sift(i, end):
        while True:
            l, r, m = 2 * i + 1, 2 * i + 2, i
            cost.add("arith", 2)
            if l < end:
                cost.add("compare", 1)
                if a[l] > a[m]:
                    m = l
            if r < end:
                cost.add("compare", 1)
                if a[r] > a[m]:
                    m = r
            if m == i:
                return
            a[i], a[m] = a[m], a[i]; cost.add("write", 2)
            i = m

    for i in range(n // 2 - 1, -1, -1):
        sift(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]; cost.add("write", 2)
        sift(0, end)
    return a


def quicksort(a: Sequence[Any], cost: Optional[Cost] = None, seed: int = 0) -> List[Any]:
    """Randomised quicksort with 3-way partition (Hoare 1962 idea; seeded
    pivot choice for reproducibility).  Expected O(n log n) compares;
    worst case Θ(n²)."""
    cost = cost or null_cost()
    rng = random.Random(seed)
    a = list(a)

    def qs(lo, hi):
        while lo < hi:
            p = a[rng.randint(lo, hi)]
            lt, i, gt = lo, lo, hi
            while i <= gt:
                cost.add("compare", 1)
                if a[i] < p:
                    a[lt], a[i] = a[i], a[lt]; cost.add("write", 2); lt += 1; i += 1
                elif a[i] > p:
                    cost.add("compare", 1)
                    a[i], a[gt] = a[gt], a[i]; cost.add("write", 2); gt -= 1
                else:
                    cost.add("compare", 1)
                    i += 1
            # recurse on the smaller side, loop on the larger: O(log n) stack
            if lt - lo < hi - gt:
                qs(lo, lt - 1); lo = gt + 1
            else:
                qs(gt + 1, hi); hi = lt - 1

    qs(0, len(a) - 1)
    return a


# ----------------------------------------------------------------- union-find
class UnionFind:
    """Disjoint sets with union by rank and path compression (Tarjan 1975):
    amortised O(α(n)) per operation."""

    def __init__(self, n: int, cost: Optional[Cost] = None):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.cost = cost or null_cost()
        self.components = n

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            self.cost.add("pointer", 1)
            root = self.parent[root]
        while self.parent[x] != root:  # compression
            self.parent[x], x = root, self.parent[x]
            self.cost.add("write", 1)
        return root

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        self.cost.add("compare", 1)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx; self.cost.add("write", 1)
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True


# ----------------------------------------------------------------- dynamic programming
def lcs_length(x: Sequence[Any], y: Sequence[Any], cost: Optional[Cost] = None) -> int:
    """Longest common subsequence length; Θ(|x||y|) table cells."""
    cost = cost or null_cost()
    prev = [0] * (len(y) + 1)
    for i in range(1, len(x) + 1):
        cur = [0] * (len(y) + 1)
        for j in range(1, len(y) + 1):
            cost.add("compare", 1); cost.add("write", 1)
            cur[j] = prev[j - 1] + 1 if x[i - 1] == y[j - 1] else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def edit_distance(x: Sequence[Any], y: Sequence[Any], cost: Optional[Cost] = None) -> int:
    """Levenshtein distance (unit insert/delete/substitute); Θ(|x||y|)."""
    cost = cost or null_cost()
    prev = list(range(len(y) + 1))
    for i in range(1, len(x) + 1):
        cur = [i] + [0] * len(y)
        for j in range(1, len(y) + 1):
            cost.add("compare", 3); cost.add("write", 1)
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x[i - 1] != y[j - 1]))
        prev = cur
    return prev[-1]


def knapsack_01(weights: Sequence[int], values: Sequence[int], capacity: int,
                cost: Optional[Cost] = None) -> int:
    """Maximum value of a subset with total weight ≤ capacity; Θ(nW) cells
    (pseudo-polynomial: W is a number, not an input length)."""
    cost = cost or null_cost()
    best = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            cost.add("compare", 1); cost.add("write", 1)
            if best[c - w] + v > best[c]:
                best[c] = best[c - w] + v
    return best[capacity]


# ----------------------------------------------------------------- strings
def naive_find_all(text: str, pat: str, cost: Optional[Cost] = None) -> List[int]:
    """All occurrences by direct comparison; Θ(nm) compares worst case."""
    cost = cost or null_cost()
    out = []
    for i in range(len(text) - len(pat) + 1):
        j = 0
        while j < len(pat):
            cost.add("compare", 1)
            if text[i + j] != pat[j]:
                break
            j += 1
        if j == len(pat):
            out.append(i)
    return out


def kmp_failure(pat: str, cost: Optional[Cost] = None) -> List[int]:
    cost = cost or null_cost()
    f = [0] * len(pat)
    k = 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]:
            cost.add("compare", 1); k = f[k - 1]
        cost.add("compare", 1)
        if pat[i] == pat[k]:
            k += 1
        f[i] = k
    return f


def kmp_find_all(text: str, pat: str, cost: Optional[Cost] = None) -> List[int]:
    """Knuth–Morris–Pratt (1977): at most 2n compares after O(m)
    preprocessing.  The failure function is the transition structure of the
    pattern's string-matching automaton."""
    cost = cost or null_cost()
    if not pat:
        return list(range(len(text) + 1))
    f = kmp_failure(pat, cost)
    out, k = [], 0
    for i, ch in enumerate(text):
        while k and ch != pat[k]:
            cost.add("compare", 1); k = f[k - 1]
        cost.add("compare", 1)
        if ch == pat[k]:
            k += 1
        if k == len(pat):
            out.append(i - k + 1)
            k = f[k - 1]
    return out
