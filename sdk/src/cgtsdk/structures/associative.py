"""Associative and priority structures: hash table, binary heap, trie.

Hash functions are fixed and deterministic (no per-process randomisation),
so probe counts are reproducible.  Expected O(1) lookup for hashing holds
under the usual uniform-hashing *assumption*; the SDK's tests include an
adversarial key set that collides on purpose (book Chapter 2, NEG example).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..cost import Cost
from ..grammar import Call, Inadmissible, Move, Structure

_FNV_OFFSET, _FNV_PRIME = 0xCBF29CE484222325, 0x100000001B3
_MASK64 = (1 << 64) - 1


def stable_hash(key: Any) -> int:
    """Deterministic 64-bit hash: FNV-1a over a canonical byte encoding."""
    if isinstance(key, bool) or key is None:
        data = repr(key).encode()
    elif isinstance(key, int):
        data = b"i" + str(key).encode()
    elif isinstance(key, str):
        data = b"s" + key.encode("utf-8")
    elif isinstance(key, tuple):
        data = b"t" + b"|".join(stable_hash(k).to_bytes(8, "little") for k in key)
    else:
        raise TypeError(f"unhashable key type for stable_hash: {type(key).__name__}")
    h = _FNV_OFFSET
    for byte in data:
        h ^= byte
        h = (h * _FNV_PRIME) & _MASK64
    return h


_TOMB = object()


class HashTableStructure(Structure):
    """Open addressing with linear probing; resize ×2 when load > 1/2.

    Layout: 2 words per slot (key, value) + 3 header words.  ``hash_fn`` may
    be replaced (e.g. by a constant function) to study adversarial inputs.
    """

    name = "hash_table"
    SIGNATURE = (
        Move("put", ("k", "v"), "insert or overwrite", True),
        Move("get", ("k",), "value for k (undefined if absent)"),
        Move("contains", ("k",), "membership test"),
        Move("delete", ("k",), "remove k (undefined if absent)", True),
        Move("len", (), "number of keys"),
    )

    def __init__(self, items=(), capacity: int = 8, hash_fn=stable_hash):
        self.cap = max(8, capacity)
        self.keys: List[Any] = [None] * self.cap
        self.vals: List[Any] = [None] * self.cap
        self.n = 0
        self.used = 0  # live + tombstones
        self.hash_fn = hash_fn
        for k, v in dict(items).items():
            self.apply(Call("put", (k, v)), Cost())

    def abstract(self) -> Dict[Any, Any]:
        return {k: v for k, v in zip(self.keys, self.vals) if k is not None and k is not _TOMB}

    def size_words(self) -> int:
        return 2 * self.cap + 3

    @classmethod
    def denote(cls, s, c):
        if c.name == "put":
            t = dict(s); t[c.args[0]] = c.args[1]
            return t, None
        if c.name in ("get", "delete"):
            if c.args[0] not in s:
                raise Inadmissible(f"key {c.args[0]!r} absent")
            if c.name == "get":
                return s, s[c.args[0]]
            t = dict(s); v = t.pop(c.args[0])
            return t, v
        if c.name == "contains":
            return s, c.args[0] in s
        if c.name == "len":
            return s, len(s)
        raise Inadmissible(c.name)

    def _find(self, k, cost: Cost) -> Tuple[int, Optional[int]]:
        """Return (slot of k or -1, first reusable slot)."""
        cost.add("hash", 1)
        i = self.hash_fn(k) % self.cap
        free = None
        for _ in range(self.cap):
            cost.add("probe", 1)
            key = self.keys[i]
            if key is None:
                return -1, (free if free is not None else i)
            if key is _TOMB:
                if free is None:
                    free = i
            else:
                cost.add("compare", 1)
                if key == k:
                    return i, free
            i = (i + 1) % self.cap
        return -1, free

    def _resize(self, cost: Cost) -> None:
        old = [(k, v) for k, v in zip(self.keys, self.vals) if k is not None and k is not _TOMB]
        self.cap *= 2
        cost.add("alloc", 2 * self.cap, f"rehash into {self.cap} slots")
        self.keys, self.vals = [None] * self.cap, [None] * self.cap
        self.n = self.used = 0
        for k, v in old:
            _, slot = self._find(k, cost)
            self.keys[slot], self.vals[slot] = k, v
            cost.add("write", 2)
            self.n += 1; self.used += 1

    def apply(self, c: Call, cost: Cost) -> Any:
        k = c.args[0] if c.args else None
        if c.name == "len":
            cost.add("read", 1)
            return self.n
        if c.name == "put":
            i, free = self._find(k, cost)
            if i >= 0:
                cost.add("write", 1); self.vals[i] = c.args[1]
                return None
            if self.keys[free] is None:
                self.used += 1
            self.keys[free], self.vals[free] = k, c.args[1]
            cost.add("write", 2)
            self.n += 1
            if 2 * self.used > self.cap:
                self._resize(cost)
            return None
        i, _ = self._find(k, cost)
        if c.name == "contains":
            return i >= 0
        if i < 0:
            raise Inadmissible(f"key {k!r} absent")
        cost.add("read", 1)
        if c.name == "get":
            return self.vals[i]
        if c.name == "delete":
            v = self.vals[i]
            self.keys[i], self.vals[i] = _TOMB, None
            cost.add("write", 2)
            self.n -= 1
            return v
        raise Inadmissible(c.name)


# =====================================================================
class HeapStructure(Structure):
    """Binary min-heap in an array (Williams 1964).  The parent of slot i is
    (i-1)//2 and its children are 2i+1, 2i+2: the heap numeration of
    CGT-THM-003, shifted to start at 0.  Abstract value: the sorted multiset."""

    name = "heap"
    SIGNATURE = (Move("push", ("x",), "", True), Move("pop_min", (), "", True),
                 Move("peek", (), ""), Move("len", (), ""))

    def __init__(self, values=()):
        self.a: List[Any] = []
        c = Cost()
        for v in values:
            self.apply(Call("push", (v,)), c)

    def abstract(self):
        return sorted(self.a)

    def size_words(self):
        return len(self.a) + 2

    @classmethod
    def denote(cls, s, c):
        if c.name == "push":
            return sorted(s + [c.args[0]]), None
        if c.name in ("pop_min", "peek"):
            if not s:
                raise Inadmissible(f"{c.name} on empty heap")
            return (s[1:], s[0]) if c.name == "pop_min" else (s, s[0])
        if c.name == "len":
            return s, len(s)
        raise Inadmissible(c.name)

    def apply(self, c, cost):
        a = self.a
        if c.name == "len":
            cost.add("read", 1)
            return len(a)
        if c.name == "push":
            a.append(c.args[0]); cost.add("write", 1)
            i = len(a) - 1
            while i > 0:
                p = (i - 1) // 2
                cost.add("arith", 2); cost.add("compare", 1)
                if a[p] <= a[i]:
                    break
                a[p], a[i] = a[i], a[p]; cost.add("write", 2)
                i = p
            return None
        cost.add("compare", 1)
        if not a:
            raise Inadmissible(f"{c.name} on empty heap")
        cost.add("read", 1)
        if c.name == "peek":
            return a[0]
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last; cost.add("write", 1)
            i, n = 0, len(a)
            while True:
                l, r, m = 2 * i + 1, 2 * i + 2, i
                cost.add("arith", 2)
                if l < n:
                    cost.add("compare", 1)
                    if a[l] < a[m]:
                        m = l
                if r < n:
                    cost.add("compare", 1)
                    if a[r] < a[m]:
                        m = r
                if m == i:
                    break
                a[m], a[i] = a[i], a[m]; cost.add("write", 2)
                i = m
        return top


# =====================================================================
class TrieStructure(Structure):
    """Character trie over strings.  Each step of a lookup is one move
    labelled by the next character: the trie *is* the minimal-prefix DFA of
    its key set (without suffix sharing; cf. DAWGs)."""

    name = "trie"
    SIGNATURE = (Move("insert", ("w",), "", True), Move("contains", ("w",), ""),
                 Move("count_prefix", ("p",), "number of keys starting with p"))

    def __init__(self, words=()):
        self.root: Dict = {}
        self.nodes = 1
        c = Cost()
        for w in words:
            self.apply(Call("insert", (w,)), c)

    def abstract(self):
        out = set()

        def walk(node, pre):
            if node.get("$"):
                out.add(pre)
            for ch, sub in node.items():
                if ch not in ("$", "#"):
                    walk(sub, pre + ch)
        walk(self.root, "")
        return out

    def size_words(self):
        return 3 * self.nodes

    @classmethod
    def denote(cls, s, c):
        w = c.args[0]
        if not isinstance(w, str):
            raise Inadmissible("keys are strings")
        if c.name == "insert":
            return s | {w}, None
        if c.name == "contains":
            return s, w in s
        if c.name == "count_prefix":
            return s, sum(1 for x in s if x.startswith(w))
        raise Inadmissible(c.name)

    def apply(self, c, cost):
        w = c.args[0]
        if not isinstance(w, str):
            raise Inadmissible("keys are strings")
        node = self.root
        if c.name == "insert":
            path = [node]
            for ch in w:
                cost.add("pointer", 1)
                if ch not in node:
                    node[ch] = {}; self.nodes += 1; cost.add("alloc", 1)
                node = node[ch]
                path.append(node)
            if not node.get("$"):
                node["$"] = True
                for p in path:  # maintain subtree key counts
                    p["#"] = p.get("#", 0) + 1; cost.add("write", 1)
            return None
        for ch in w:
            cost.add("pointer", 1)
            if ch not in node:
                return False if c.name == "contains" else 0
            node = node[ch]
        cost.add("read", 1)
        return bool(node.get("$")) if c.name == "contains" else node.get("#", 0)
