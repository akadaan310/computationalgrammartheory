"""Binary-tree generators and five navigation representations (CGT-EXP-001).

Node ids are 0..n-1, root = 0.  A node's *grammatical address* is the word
w in {0,1}* (0 = left move, 1 = right move) such that [[w]](root) = node
(CGT-DEF-006).  The *heap numeration* of an address w is int('1'+w, 2).
"""
from __future__ import annotations

import random
import sys
from typing import List, Optional, Tuple

sys.setrecursionlimit(1 << 20)
W = 64  # machine word size assumed by the word-RAM cost model


def words(bits: int) -> int:
    """Word-RAM cost of one arithmetic op on a `bits`-bit integer."""
    return max(1, -(-bits // W))


class BinTree:
    def __init__(self, n: int):
        self.n = n
        self.left: List[int] = [-1] * n
        self.right: List[int] = [-1] * n
        self.parent: List[int] = [-1] * n

    # ---------------------------------------------------------------- shape
    def attach(self, p: int, c: int, side: int) -> None:
        if side == 0:
            self.left[p] = c
        else:
            self.right[p] = c
        self.parent[c] = p

    def depth_array(self) -> List[int]:
        d = [0] * self.n
        order = self.preorder()
        for v in order[1:]:
            d[v] = d[self.parent[v]] + 1
        return d

    def preorder(self) -> List[int]:
        out, st = [], [0]
        while st:
            v = st.pop()
            out.append(v)
            if self.right[v] >= 0:
                st.append(self.right[v])
            if self.left[v] >= 0:
                st.append(self.left[v])
        return out

    def height(self) -> int:
        return max(self.depth_array())


def complete_tree(n: int) -> BinTree:
    t = BinTree(n)
    for k in range(2, n + 1):  # heap index k -> node k-1
        t.attach(k // 2 - 1, k - 1, k & 1)
    return t


def random_bst(n: int, rng: random.Random) -> BinTree:
    keys = list(range(n))
    rng.shuffle(keys)
    t = BinTree(n)
    key = [0] * n
    key[0] = keys[0]
    for i in range(1, n):
        k = keys[i]
        key[i] = k
        v = 0
        while True:
            side = 0 if k < key[v] else 1
            c = t.left[v] if side == 0 else t.right[v]
            if c < 0:
                t.attach(v, i, side)
                break
            v = c
    return t


def path_tree(n: int, rng: Optional[random.Random] = None) -> BinTree:
    """Adversarial: a path of length n-1 (random left/right turns if rng)."""
    t = BinTree(n)
    for i in range(1, n):
        t.attach(i - 1, i, rng.randrange(2) if rng else 0)
    return t


# ======================================================================
# Representation R1: pointer navigation (baseline)
# ======================================================================
class PointerNav:
    name = "R1-pointer"

    def __init__(self, t: BinTree):
        self.t = t
        self.depth = t.depth_array()
        self.build_ops = t.n
        self.space_words = 4 * t.n  # left, right, parent, depth

    def lca(self, u: int, v: int, ops) -> int:
        d, p = self.depth, self.t.parent
        while d[u] > d[v]:
            u = p[u]; ops.add()
        while d[v] > d[u]:
            v = p[v]; ops.add()
        while u != v:
            u, v = p[u], p[v]; ops.add()
        ops.add()
        return u

    def is_ancestor(self, u: int, v: int, ops) -> bool:
        d, p = self.depth, self.t.parent
        while d[v] > d[u]:
            v = p[v]; ops.add()
        ops.add()
        return u == v


# ======================================================================
# Representation R2: heap numeration ("address arithmetic")
# ======================================================================
class HeapNav:
    """The grammar {x -> 2x (left), x -> 2x+1 (right), x -> x>>1 (up)} acting
    on the heap numeration.  Moves are word-RAM arithmetic; the cost of an
    arithmetic op on a b-bit number is ceil(b/64) (multi-precision)."""

    name = "R2-heap-arith"

    def __init__(self, t: BinTree):
        self.t = t
        idx = [0] * t.n
        idx[0] = 1
        for v in t.preorder()[1:]:
            p = t.parent[v]
            idx[v] = 2 * idx[p] + (0 if t.left[p] == v else 1)
        self.idx = idx
        self.h = t.height()
        self.build_ops = t.n * words(self.h + 1)
        # An array/bitmap indexed by heap number needs 2^(h+1) slots.
        self.address_space = 2 ** (self.h + 1) - 1
        self.space_words = t.n * words(self.h + 1)  # labels only (no array)

    def lca_idx(self, a: int, b: int, ops) -> int:
        c = words(self.h + 1)
        da, db = a.bit_length(), b.bit_length()
        if da > db:
            a >>= da - db
        elif db > da:
            b >>= db - da
        x = a ^ b
        ops.add(4 * c)  # bit_length x2, shift, xor (constant number of ops)
        return a >> x.bit_length()

    def lca(self, u: int, v: int, ops) -> int:
        return self.lca_idx(self.idx[u], self.idx[v], ops)

    def is_ancestor(self, u: int, v: int, ops) -> bool:
        a, b = self.idx[u], self.idx[v]
        da, db = a.bit_length(), b.bit_length()
        ops.add(3 * words(self.h + 1))
        return db >= da and (b >> (db - da)) == a


# ======================================================================
# Representation R3: stored address words; LCA = longest common prefix
# ======================================================================
class AddressNav:
    name = "R3-address-words"

    def __init__(self, t: BinTree, max_chars: int = 30_000_000):
        depth = t.depth_array()
        total = sum(depth)
        self.feasible = total <= max_chars
        self.space_chars = total
        self.build_ops = total + t.n
        if not self.feasible:
            return
        addr = [""] * t.n
        for v in t.preorder()[1:]:
            p = t.parent[v]
            addr[v] = addr[p] + ("0" if t.left[p] == v else "1")
        self.addr = addr

    def lca_addr(self, u: int, v: int, ops) -> str:
        a, b = self.addr[u], self.addr[v]
        k = 0
        m = min(len(a), len(b))
        while k < m and a[k] == b[k]:
            k += 1
        ops.add(k + 1)
        return a[:k]


# ======================================================================
# Representation R4: grammar + precomputed index (Euler tour + sparse table)
# ======================================================================
class IndexNav:
    """Euler tour + sparse-table RMQ (Bender & Farach-Colton style, without
    the +-1 block trick): O(n log n) preprocessing, O(1) query."""

    name = "R4-euler-sparse"

    def __init__(self, t: BinTree, ops_counter=None):
        n = t.n
        depth = t.depth_array()
        euler, first = [], [0] * n
        tin, tout = [0] * n, [0] * n
        clock = 0
        st = [(0, 0)]
        while st:
            v, state = st.pop()
            if state == 0:
                first[v] = len(euler)
                tin[v] = clock; clock += 1
                euler.append(v)
                st.append((v, 1))
                for c in (t.right[v], t.left[v]):
                    if c >= 0:
                        st.append((v, 2))
                        st.append((c, 0))
            elif state == 2:
                euler.append(v)
            else:
                tout[v] = clock; clock += 1
        m = len(euler)
        sp = [euler[:]]
        j, ops = 1, m
        while (1 << j) <= m:
            prev, half = sp[-1], 1 << (j - 1)
            row = []
            for i in range(m - (1 << j) + 1):
                a, b = prev[i], prev[i + half]
                row.append(a if depth[a] <= depth[b] else b)
            ops += len(row)
            sp.append(row)
            j += 1
        self.sp, self.first, self.depth = sp, first, depth
        self.tin, self.tout = tin, tout
        self.build_ops = ops + 2 * n
        self.space_words = sum(len(r) for r in sp) + 4 * n

    def lca(self, u: int, v: int, ops) -> int:
        l, r = self.first[u], self.first[v]
        if l > r:
            l, r = r, l
        j = (r - l + 1).bit_length() - 1
        a, b = self.sp[j][l], self.sp[j][r - (1 << j) + 1]
        ops.add(3)
        return a if self.depth[a] <= self.depth[b] else b

    def is_ancestor(self, u: int, v: int, ops) -> bool:
        ops.add(2)
        return self.tin[u] <= self.tin[v] and self.tout[v] <= self.tout[u]


# ======================================================================
# Updates
# ======================================================================
def rotate_right_cost(t: BinTree, v: int) -> dict:
    """Right rotation at v.  Pointer cost is O(1).  Every node in the rotated
    subtree changes its address (and heap number), so R2/R3 must relabel the
    whole subtree; R4 must rebuild (no local repair in this simple index)."""
    # subtree size of v
    size, st = 0, [v]
    while st:
        x = st.pop(); size += 1
        for c in (t.left[x], t.right[x]):
            if c >= 0:
                st.append(c)
    return {"pointer": 3, "heap_relabel": size, "address_relabel": size,
            "index_rebuild": t.n}
