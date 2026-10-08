"""Ordered labelled forests, minimal-DAG (hash-consed) grammars, navigation and
path-copying updates (CGT-EXP-004).

A minimal DAG is the simplest *structural grammar* of a tree: one nonterminal
per distinct subtree, production  X -> label(X1 ... Xk)  (Downey, Sethi &
Tarjan 1980; Buneman, Grohe & Koch 2003).
"""
from __future__ import annotations

import bisect
import random
from typing import Dict, List, Tuple


class Explicit:
    """Explicit forest in preorder arrays: label[i], parent[i], children[i]."""

    def __init__(self):
        self.label: List[str] = []
        self.children: List[List[int]] = []
        self.roots: List[int] = []

    def new(self, lab: str) -> int:
        self.label.append(lab); self.children.append([])
        return len(self.label) - 1

    @property
    def n(self) -> int:
        return len(self.label)


def random_tree(F: Explicit, size: int, labels: str, rng, maxdeg: int = 3) -> int:
    root = F.new(rng.choice(labels))
    nodes = [root]
    for _ in range(size - 1):
        while True:
            p = rng.choice(nodes)
            if len(F.children[p]) < maxdeg:
                break
        c = F.new(rng.choice(labels)); F.children[p].append(c); nodes.append(c)
    return root


def copy_tree(F: Explicit, G: Explicit, r: int) -> int:
    x = G.new(F.label[r])
    for c in F.children[r]:
        G.children[x].append(copy_tree(F, G, c))
    return x


def full_binary(F: Explicit, h: int, lab: str = "a") -> int:
    x = F.new(lab)
    if h > 0:
        F.children[x] = [full_binary(F, h - 1, lab), full_binary(F, h - 1, lab)]
    return x


def monadic_path(F: Explicit, n: int, lab: str = "a") -> int:
    root = prev = F.new(lab)
    for _ in range(n - 1):
        c = F.new(lab); F.children[prev].append(c); prev = c
    return root


class DagGrammar:
    """Hash-consed DAG.  node id -> (label, child ids).  size[id] = expanded
    size, so preorder-rank access works without decompression."""

    def __init__(self):
        self.table: Dict[Tuple, int] = {}
        self.node: List[Tuple[str, Tuple[int, ...]]] = []
        self.size: List[int] = []
        self.build_ops = 0

    def make(self, lab: str, kids: Tuple[int, ...]) -> int:
        key = (lab, kids)
        self.build_ops += 1 + len(kids)
        x = self.table.get(key)
        if x is None:
            x = len(self.node)
            self.table[key] = x; self.node.append(key)
            self.size.append(1 + sum(self.size[k] for k in kids))
        return x

    @classmethod
    def from_explicit(cls, F: Explicit):
        D = cls()
        ids = [0] * F.n
        order = []
        st = list(F.roots)
        while st:
            v = st.pop(); order.append(v); st.extend(F.children[v])
        for v in reversed(order):  # children before parents
            ids[v] = D.make(F.label[v], tuple(ids[c] for c in F.children[v]))
        D.roots = [ids[r] for r in F.roots]
        return D

    def live_size(self) -> int:
        seen, st = set(), list(self.roots)
        while st:
            x = st.pop()
            if x in seen:
                continue
            seen.add(x); st.extend(self.node[x][1])
        return len(seen)

    def edges_live(self) -> int:
        seen, st, e = set(), list(self.roots), 0
        while st:
            x = st.pop()
            if x in seen:
                continue
            seen.add(x); e += len(self.node[x][1]); st.extend(self.node[x][1])
        return e

    # ---------------------------------------------------- navigation
    def access(self, i: int, ops) -> Tuple[List[Tuple[int, int]], str]:
        """Preorder rank i (over the whole forest) -> label.  Returns the
        derivation path [(dag node, child index)] as a by-product: the
        grammatical *address* of the node.  Cost: sum of degrees on the path."""
        # forest level: binary search over root prefix sums (an index over the
        # sequence of components; relabels never change sizes, so it stays valid)
        if getattr(self, "_prefix", None) is None or len(self._prefix) != len(self.roots) + 1:
            pre = [0]
            for r in self.roots:
                pre.append(pre[-1] + self.size[r])
            self._prefix = pre
        ri = bisect.bisect_right(self._prefix, i) - 1
        ops.add(max(1, len(self.roots).bit_length()))
        if not 0 <= ri < len(self.roots):
            raise IndexError
        i -= self._prefix[ri]
        x = self.roots[ri]
        path = [(-1, ri)]
        while i > 0:
            i -= 1
            for ci, c in enumerate(self.node[x][1]):
                ops.add()
                if i < self.size[c]:
                    path.append((x, ci)); x = c; break
                i -= self.size[c]
        return path, self.node[x][0]

    # ---------------------------------------------------- update
    def relabel(self, i: int, lab: str, ops) -> int:
        """Persistent update by path copying.  Returns number of DAG nodes
        created (new grammar rules)."""
        path, _ = self.access(i, ops)
        before = len(self.node)
        # walk back up: rebuild target, then each ancestor with new child id
        # recover node ids along the path
        ri = path[0][1]
        xs = [self.roots[ri]]
        for (p, ci) in path[1:]:
            xs.append(self.node[p][1][ci])
        tgt = xs[-1]
        new = self.make(lab, self.node[tgt][1]); ops.add()
        for k in range(len(xs) - 2, -1, -1):
            lab_k, kids = self.node[xs[k]]
            ci = path[k + 1][1]
            kids = kids[:ci] + (new,) + kids[ci + 1:]
            new = self.make(lab_k, kids); ops.add(len(kids))
        self.roots = self.roots[:ri] + [new] + self.roots[ri + 1:]
        return len(self.node) - before
