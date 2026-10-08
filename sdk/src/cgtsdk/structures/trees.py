"""Hierarchical structures: navigable binary trees (two representations) and
binary search trees (plain or AVL-balanced).

Navigation grammar (CGT-DEF-006): moves ``L``, ``R``, ``U`` act on a cursor;
``goto(addr)`` jumps to the node whose address word over {0,1} is ``addr``.
Two representations of the *same* abstract tree are provided:

* ``"pointer"`` -- nodes with left/right/parent pointers.  ``goto`` walks
  ``|addr|`` pointers.
* ``"heap"``    -- nodes stored in a table keyed by the heap numeration
  ν(w) = int('1'+w, 2).  Moves are arithmetic (2ν, 2ν+1, ⌊ν/2⌋) charged at
  ⌈bits/w⌉ word operations; ``goto`` is one numeral computation plus one
  table probe.  If the address space 2^(h+1) is dense the table can be an
  array; otherwise a hash table is used and ``density`` reports n/2^(h+1)
  (CGT-THM-003).
"""
from __future__ import annotations

from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Tuple

from ..cost import Cost
from ..grammar import Call, Inadmissible, Move, Structure


class BinaryTreeStructure(Structure):
    name = "binary_tree"
    SIGNATURE = (
        Move("L", (), "cursor to left child"),
        Move("R", (), "cursor to right child"),
        Move("U", (), "cursor to parent"),
        Move("root", (), "cursor to the root"),
        Move("goto", ("addr",), "cursor to the node with address addr ∈ {0,1}*"),
        Move("read", (), "label at the cursor"),
        Move("here", (), "address of the cursor"),
    )

    def __init__(self, labels: Dict[str, Any], representation: str = "pointer"):
        """``labels`` maps address words to labels; it must be prefix-closed
        and contain the root address ''."""
        if "" not in labels:
            raise ValueError("a tree needs a root (address '')")
        for a in labels:
            if a and a[:-1] not in labels:
                raise ValueError(f"address {a!r} has no parent: not prefix-closed")
            if set(a) - {"0", "1"}:
                raise ValueError(f"address {a!r} is not a word over {{0,1}}")
        if representation not in ("pointer", "heap"):
            raise ValueError("representation is 'pointer' or 'heap'")
        self.rep = representation
        self.labels = dict(labels)
        self.height = max(len(a) for a in labels)
        self.cursor = ""                       # abstract cursor, kept in sync
        if self.rep == "pointer":
            self._nodes: Dict[str, Dict[str, Optional[str]]] = {
                a: {"0": a + "0" if a + "0" in labels else None,
                    "1": a + "1" if a + "1" in labels else None,
                    "U": a[:-1] if a else None} for a in labels}
        else:
            self._table = {int("1" + a, 2): v for a, v in labels.items()}
            self._nu = 1

    # -- constructors ------------------------------------------------------
    @classmethod
    def complete(cls, n: int, representation: str = "pointer") -> "BinaryTreeStructure":
        labels = {format(k, "b")[1:]: k for k in range(1, n + 1)}
        return cls(labels, representation)

    @classmethod
    def path(cls, n: int, turns: str = "0", representation: str = "pointer"):
        labels, a = {"": 0}, ""
        for i in range(1, n):
            a += turns[(i - 1) % len(turns)]
            labels[a] = i
        return cls(labels, representation)

    # -- semantics ---------------------------------------------------------
    def abstract(self) -> Tuple[FrozenSet[Tuple[str, Any]], str]:
        return (frozenset(self.labels.items()), self.cursor)

    @property
    def n(self) -> int:
        return len(self.labels)

    @property
    def density(self) -> float:
        return self.n / (2 ** (self.height + 1) - 1)

    def size_words(self) -> int:
        if self.rep == "pointer":
            return 4 * self.n  # label, left, right, parent
        # array if dense, else hash table of (numeral, label) at load ≤ 1/2
        words_per_label = max(1, -(-(self.height + 1) // 64))
        return min(2 ** (self.height + 1), 4 * self.n) * (1 + words_per_label)

    @classmethod
    def denote(cls, state, c: Call):
        items, cur = state
        nodes = dict(items)
        if c.name in ("L", "R"):
            nxt = cur + ("0" if c.name == "L" else "1")
            if nxt not in nodes:
                raise Inadmissible(f"node {cur or 'ε'} has no {'left' if c.name == 'L' else 'right'} child")
            return (items, nxt), nxt
        if c.name == "U":
            if cur == "":
                raise Inadmissible("the root has no parent")
            return (items, cur[:-1]), cur[:-1]
        if c.name == "root":
            return (items, ""), ""
        if c.name == "goto":
            a = c.args[0]
            if not isinstance(a, str) or a not in nodes:
                raise Inadmissible(f"no node at address {a!r}")
            return (items, a), a
        if c.name == "read":
            return state, nodes[cur]
        if c.name == "here":
            return state, cur
        raise Inadmissible(c.name)

    # -- execution ---------------------------------------------------------
    def apply(self, c: Call, cost: Cost) -> Any:
        if self.rep == "pointer":
            return self._apply_pointer(c, cost)
        return self._apply_heap(c, cost)

    def _apply_pointer(self, c, cost):
        node = self._nodes[self.cursor]
        if c.name in ("L", "R", "U"):
            key = {"L": "0", "R": "1", "U": "U"}[c.name]
            cost.add("pointer", 1)
            nxt = node[key]
            if nxt is None:
                raise Inadmissible(f"move {c.name} undefined at {self.cursor or 'ε'}")
            self.cursor = nxt
            return nxt
        if c.name == "root":
            cost.add("read", 1)
            self.cursor = ""
            return ""
        if c.name == "goto":
            a = c.args[0]
            if not isinstance(a, str):
                raise Inadmissible(f"no node at address {a!r}")
            cur = ""
            cost.add("read", 1)
            for i, b in enumerate(a):
                cost.add("pointer", 1)
                nxt = self._nodes[cur][b] if b in "01" else None
                if nxt is None:
                    raise Inadmissible(f"no node at address {a!r}")
                cur = nxt
            self.cursor = cur
            return cur
        if c.name == "read":
            cost.add("read", 1)
            return self.labels[self.cursor]
        if c.name == "here":
            # a pointer node does not store its address: recover it by walking up
            a, cur = [], self.cursor
            while cur:
                cost.add("pointer", 1)
                a.append(cur[-1]); cur = self._nodes[cur]["U"]
            return "".join(reversed(a))
        raise Inadmissible(c.name)

    def _apply_heap(self, c, cost):
        bits = self.height + 2
        if c.name in ("L", "R", "U"):
            if c.name == "U":
                if self._nu == 1:
                    raise Inadmissible("the root has no parent")
                cost.word_arith(bits, 1, "ν ← ⌊ν/2⌋")
                nu = self._nu >> 1
            else:
                cost.word_arith(bits, 2, f"ν ← 2ν{'+1' if c.name == 'R' else ''}")
                nu = 2 * self._nu + (c.name == "R")
            cost.add("probe", 1, "membership in node table")
            if nu not in self._table:
                raise Inadmissible(f"move {c.name} undefined at {self.cursor or 'ε'}")
            self._nu = nu
            self.cursor = format(nu, "b")[1:]
            return self.cursor
        if c.name == "root":
            self._nu, self.cursor = 1, ""
            cost.add("arith", 1)
            return ""
        if c.name == "goto":
            a = c.args[0]
            if not isinstance(a, str) or set(a) - {"0", "1"}:
                raise Inadmissible(f"no node at address {a!r}")
            cost.word_arith(len(a) + 1, 1, "ν = int('1'+addr, 2)")
            nu = int("1" + a, 2)
            cost.add("probe", 1)
            if nu not in self._table:
                raise Inadmissible(f"no node at address {a!r}")
            self._nu, self.cursor = nu, a
            return a
        if c.name == "read":
            cost.add("probe", 1)
            return self._table[self._nu]
        if c.name == "here":
            cost.word_arith(bits, 1, "strip leading 1 of ν")
            return format(self._nu, "b")[1:]
        raise Inadmissible(c.name)


# =====================================================================
class _BNode:
    __slots__ = ("key", "left", "right", "h")

    def __init__(self, key):
        self.key, self.left, self.right, self.h = key, None, None, 1


def _h(n):
    return n.h if n else 0


class BSTStructure(Structure):
    """Binary search tree over distinct comparable keys, optionally AVL
    balanced (Adelson-Velsky & Landis 1962).  Abstract value: the sorted
    tuple of keys.  Cost: one ``compare`` per key comparison, one ``pointer``
    per edge followed, ``write`` per pointer/height update."""

    name = "bst"
    SIGNATURE = (Move("insert", ("k",), "", True), Move("contains", ("k",), ""),
                 Move("delete", ("k",), "undefined if absent", True),
                 Move("min", (), "undefined if empty"))

    def __init__(self, keys=(), balance: str = "none"):
        if balance not in ("none", "avl"):
            raise ValueError("balance is 'none' or 'avl'")
        self.balance = balance
        self.root: Optional[_BNode] = None
        self.n = 0
        c = Cost()
        for k in keys:
            self.apply(Call("insert", (k,)), c)

    def abstract(self):
        out, st, t = [], [], self.root
        while st or t is not None:      # iterative in-order (no recursion limit)
            while t is not None:
                st.append(t); t = t.left
            t = st.pop()
            out.append(t.key)
            t = t.right
        return tuple(out)

    def size_words(self):
        return 4 * self.n

    @classmethod
    def denote(cls, s, c):
        if c.name == "insert":
            return tuple(sorted(set(s) | {c.args[0]})), None
        if c.name == "contains":
            return s, c.args[0] in s
        if c.name == "delete":
            if c.args[0] not in s:
                raise Inadmissible(f"key {c.args[0]!r} absent")
            return tuple(k for k in s if k != c.args[0]), None
        if c.name == "min":
            if not s:
                raise Inadmissible("min of empty tree")
            return s, s[0]
        raise Inadmissible(c.name)

    # -- AVL helpers ------------------------------------------------------
    def _fix(self, t, cost):
        t.h = 1 + max(_h(t.left), _h(t.right)); cost.add("write", 1)
        if self.balance != "avl":
            return t
        bf = _h(t.left) - _h(t.right)
        cost.add("compare", 2)
        if bf > 1:
            if _h(t.left.left) < _h(t.left.right):
                t.left = self._rot_left(t.left, cost)
            return self._rot_right(t, cost)
        if bf < -1:
            if _h(t.right.right) < _h(t.right.left):
                t.right = self._rot_right(t.right, cost)
            return self._rot_left(t, cost)
        return t

    def _rot_right(self, t, cost):
        l = t.left
        t.left, l.right = l.right, t
        cost.add("write", 2, "rotation")
        t.h = 1 + max(_h(t.left), _h(t.right))
        l.h = 1 + max(_h(l.left), _h(l.right))
        return l

    def _rot_left(self, t, cost):
        r = t.right
        t.right, r.left = r.left, t
        cost.add("write", 2, "rotation")
        t.h = 1 + max(_h(t.left), _h(t.right))
        r.h = 1 + max(_h(r.left), _h(r.right))
        return r

    def _rebuild_path(self, path, child, cost):
        """Reattach `child` below the last node of `path` and fix heights /
        rebalance bottom-up.  path: list of (node, went_left)."""
        for node, went_left in reversed(path):
            if went_left:
                node.left = child
            else:
                node.right = child
            cost.add("write", 1)
            child = self._fix(node, cost)
        return child

    def _insert(self, t, k, cost):
        """Iterative: no recursion depth limit on degenerate (path-shaped) trees."""
        path, cur = [], t
        while cur is not None:
            cost.add("compare", 1)
            if k == cur.key:
                return t
            cost.add("compare", 1); cost.add("pointer", 1)
            left = k < cur.key
            path.append((cur, left))
            cur = cur.left if left else cur.right
        cost.add("alloc", 1)
        self.n += 1
        return self._rebuild_path(path, _BNode(k), cost)

    def _delete(self, t, k, cost):
        path, cur = [], t
        while cur is not None:
            cost.add("compare", 1)
            if k == cur.key:
                break
            cost.add("compare", 1); cost.add("pointer", 1)
            left = k < cur.key
            path.append((cur, left))
            cur = cur.left if left else cur.right
        if cur is None:
            raise Inadmissible(f"key {k!r} absent")
        if cur.left is None or cur.right is None:
            replacement = cur.left or cur.right
        else:
            # replace by the successor: delete the minimum of the right subtree
            sub, m = [], cur.right
            while m.left is not None:
                cost.add("pointer", 1)
                sub.append((m, True)); m = m.left
            cur.key = m.key; cost.add("write", 1)
            right = self._rebuild_path(sub, m.right, cost) if sub else m.right
            cur.right = right; cost.add("write", 1)
            replacement = self._fix(cur, cost)
        self.n -= 1
        return self._rebuild_path(path, replacement, cost)

    def apply(self, c, cost):
        if c.name == "insert":
            self.root = self._insert(self.root, c.args[0], cost)
            return None
        if c.name == "delete":
            self.root = self._delete(self.root, c.args[0], cost)
            return None
        if c.name == "contains":
            t, k = self.root, c.args[0]
            while t is not None:
                cost.add("compare", 1)
                if k == t.key:
                    return True
                cost.add("compare", 1); cost.add("pointer", 1)
                t = t.left if k < t.key else t.right
            return False
        if c.name == "min":
            if self.root is None:
                raise Inadmissible("min of empty tree")
            t = self.root
            while t.left:
                cost.add("pointer", 1); t = t.left
            return t.key
        raise Inadmissible(c.name)

    def tree_height(self) -> int:
        return _h(self.root)

    def check_invariants(self) -> bool:
        """Search-tree order, stored heights, and (for AVL) balance factors."""
        st, ok = [(self.root, None, None)], True
        while st:
            t, lo, hi = st.pop()
            if t is None:
                continue
            ok &= (lo is None or lo < t.key) and (hi is None or t.key < hi)
            ok &= t.h == 1 + max(_h(t.left), _h(t.right))
            if self.balance == "avl":
                ok &= abs(_h(t.left) - _h(t.right)) <= 1
            st += [(t.left, lo, t.key), (t.right, t.key, hi)]
        return bool(ok)
