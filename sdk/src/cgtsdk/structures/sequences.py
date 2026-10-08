"""Sequential structures: arrays, linked lists, stacks, queues, deques.

Representation layouts (for ``size_words``) are documented per class.  The
cost conventions are those of Chapter 2 of the book:

* array ``get(i)``: one address computation (``arith``), one bounds check
  (``compare``), one memory read -- independent of ``i``;
* list ``get(i)``: ``i`` pointer hops plus one read -- linear in ``i``.

That difference is the first example of CGT mechanism M-ARITH: the array's
index *is* an arithmetic address, the list's index is a word ``next^i`` that
must be walked.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

from ..cost import Cost
from ..grammar import Call, Inadmissible, Move, Structure


def _index(i: Any, n: int, what: str = "index") -> int:
    if not isinstance(i, int) or isinstance(i, bool):
        raise Inadmissible(f"{what} must be an integer, got {i!r}")
    if not 0 <= i < n:
        raise Inadmissible(f"{what} {i} out of range [0, {n})")
    return i


# =====================================================================
class ArrayStructure(Structure):
    """Dynamic array: contiguous block of ``capacity`` cells holding ``n``
    elements.  ``append`` doubles the capacity when full (amortised O(1)).

    Layout: ``capacity`` element words + 3 header words (base, n, capacity).
    """

    name = "array"
    SIGNATURE = (
        Move("get", ("i",), "read element i: address base+i"),
        Move("set", ("i", "x"), "write x at index i", True),
        Move("len", (), "number of elements"),
        Move("append", ("x",), "add x at the end (may reallocate)", True),
        Move("pop", (), "remove and return the last element", True),
        Move("insert", ("i", "x"), "insert x before index i, shifting the tail", True),
        Move("delete", ("i",), "remove index i, shifting the tail left", True),
    )

    def __init__(self, values=(), capacity: Optional[int] = None):
        values = list(values)
        self.n = len(values)
        self.capacity = max(capacity or 0, self.n, 1)
        self.mem: List[Any] = values + [None] * (self.capacity - self.n)
        self.reallocations = 0

    def abstract(self) -> List[Any]:
        return list(self.mem[: self.n])

    def size_words(self) -> int:
        return self.capacity + 3

    # -- reference semantics (pure) -------------------------------------
    @classmethod
    def denote(cls, s: List[Any], c: Call) -> Tuple[List[Any], Any]:
        n = len(s)
        if c.name == "get":
            return s, s[_index(c.args[0], n)]
        if c.name == "set":
            s = list(s); s[_index(c.args[0], n)] = c.args[1]
            return s, None
        if c.name == "len":
            return s, n
        if c.name == "append":
            return s + [c.args[0]], None
        if c.name == "pop":
            if not s:
                raise Inadmissible("pop from empty array")
            return s[:-1], s[-1]
        if c.name == "insert":
            i = _index(c.args[0], n + 1, "insert position")
            return s[:i] + [c.args[1]] + s[i:], None
        if c.name == "delete":
            i = _index(c.args[0], n)
            return s[:i] + s[i + 1:], s[i]
        raise Inadmissible(f"unknown move {c.name}")

    # -- representation -------------------------------------------------
    def _grow(self, cost: Cost) -> None:
        new_cap = 2 * self.capacity
        cost.add("alloc", new_cap, f"reallocate {self.capacity} -> {new_cap}")
        cost.add("read", self.n); cost.add("write", self.n)
        self.mem = self.mem[: self.n] + [None] * (new_cap - self.n)
        self.capacity = new_cap
        self.reallocations += 1

    def apply(self, c: Call, cost: Cost) -> Any:
        if c.name in ("get", "set", "delete"):
            cost.add("compare", 1, "bounds check")
            i = _index(c.args[0], self.n)
            cost.add("arith", 1, f"address = base + {i}")
            if c.name == "get":
                cost.add("read", 1, f"read cell {i}")
                return self.mem[i]
            if c.name == "set":
                cost.add("write", 1, f"write cell {i}")
                self.mem[i] = c.args[1]
                return None
            v = self.mem[i]
            k = self.n - i - 1
            cost.add("read", k + 1); cost.add("write", k, f"shift {k} cells left")
            self.mem[i:self.n - 1] = self.mem[i + 1:self.n]
            self.n -= 1
            self.mem[self.n] = None
            return v
        if c.name == "len":
            cost.add("read", 1, "read header n")
            return self.n
        if c.name == "append":
            if self.n == self.capacity:
                self._grow(cost)
            cost.add("write", 1, f"write cell {self.n}")
            self.mem[self.n] = c.args[0]
            self.n += 1
            return None
        if c.name == "pop":
            cost.add("compare", 1)
            if self.n == 0:
                raise Inadmissible("pop from empty array")
            self.n -= 1
            cost.add("read", 1)
            v, self.mem[self.n] = self.mem[self.n], None
            return v
        if c.name == "insert":
            cost.add("compare", 1, "bounds check")
            i = _index(c.args[0], self.n + 1, "insert position")
            if self.n == self.capacity:
                self._grow(cost)
            k = self.n - i
            cost.add("read", k); cost.add("write", k + 1, f"shift {k} cells right")
            self.mem[i + 1:self.n + 1] = self.mem[i:self.n]
            self.mem[i] = c.args[1]
            self.n += 1
            return None
        raise Inadmissible(f"unknown move {c.name}")


# =====================================================================
class _Node:
    __slots__ = ("val", "next")

    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


class LinkedListStructure(Structure):
    """Singly linked list with a head pointer and a stored length.

    Layout: 2 words per node (value, next) + 2 header words (head, n).
    The same signature as :class:`ArrayStructure` minus ``append``/``pop``
    (replaced by ``push_front``/``pop_front``), so the two can be compared
    on identical workloads.
    """

    name = "linked_list"
    SIGNATURE = (
        Move("get", ("i",), "read element i by walking i next-pointers"),
        Move("set", ("i", "x"), "walk to i and overwrite", True),
        Move("len", (), "stored length"),
        Move("push_front", ("x",), "new head node", True),
        Move("pop_front", (), "remove the head", True),
        Move("insert", ("i", "x"), "walk to i-1 and splice", True),
        Move("delete", ("i",), "walk to i-1 and unlink", True),
    )

    def __init__(self, values=()):
        self.head: Optional[_Node] = None
        self.n = 0
        for v in reversed(list(values)):
            self.head = _Node(v, self.head)
            self.n += 1

    def abstract(self) -> List[Any]:
        out, p = [], self.head
        while p is not None:
            out.append(p.val); p = p.next
        return out

    def size_words(self) -> int:
        return 2 * self.n + 2

    @classmethod
    def denote(cls, s: List[Any], c: Call) -> Tuple[List[Any], Any]:
        if c.name in ("get", "set", "len", "insert", "delete"):
            return ArrayStructure.denote(s, c)
        if c.name == "push_front":
            return [c.args[0]] + s, None
        if c.name == "pop_front":
            if not s:
                raise Inadmissible("pop_front from empty list")
            return s[1:], s[0]
        raise Inadmissible(f"unknown move {c.name}")

    def _walk(self, i: int, cost: Cost) -> _Node:
        p = self.head
        cost.add("read", 1, "read head")
        for _ in range(i):
            cost.add("pointer", 1)
            p = p.next
        if i:
            cost.note(f"followed next {i} times")
        return p

    def apply(self, c: Call, cost: Cost) -> Any:
        if c.name == "len":
            cost.add("read", 1)
            return self.n
        if c.name in ("get", "set"):
            cost.add("compare", 1, "bounds check")
            i = _index(c.args[0], self.n)
            p = self._walk(i, cost)
            if c.name == "get":
                cost.add("read", 1)
                return p.val
            cost.add("write", 1)
            p.val = c.args[1]
            return None
        if c.name == "push_front":
            cost.add("alloc", 1); cost.add("write", 3)
            self.head = _Node(c.args[0], self.head)
            self.n += 1
            return None
        if c.name == "pop_front":
            cost.add("compare", 1)
            if self.head is None:
                raise Inadmissible("pop_front from empty list")
            cost.add("read", 2); cost.add("write", 2)
            v = self.head.val
            self.head = self.head.next
            self.n -= 1
            return v
        if c.name == "insert":
            cost.add("compare", 1)
            i = _index(c.args[0], self.n + 1, "insert position")
            cost.add("alloc", 1); cost.add("write", 3)
            if i == 0:
                self.head = _Node(c.args[1], self.head)
            else:
                p = self._walk(i - 1, cost)
                p.next = _Node(c.args[1], p.next)
            self.n += 1
            return None
        if c.name == "delete":
            cost.add("compare", 1)
            i = _index(c.args[0], self.n)
            cost.add("write", 2)
            if i == 0:
                v = self.head.val
                self.head = self.head.next
            else:
                p = self._walk(i - 1, cost)
                v = p.next.val
                p.next = p.next.next
            self.n -= 1
            return v
        raise Inadmissible(f"unknown move {c.name}")


# =====================================================================
class StackStructure(Structure):
    """Array-backed stack.  The set of move words that are *defined* when
    started on an empty stack is { w : every prefix has #push ≥ #pop } --
    a context-free, non-regular language (book Chapter 3)."""

    name = "stack"
    SIGNATURE = (Move("push", ("x",), "", True), Move("pop", (), "", True),
                 Move("top", (), ""), Move("empty", (), ""))

    def __init__(self, values=()):
        self.arr = ArrayStructure(values)

    def abstract(self) -> List[Any]:
        return self.arr.abstract()

    def size_words(self) -> int:
        return self.arr.size_words()

    @classmethod
    def denote(cls, s, c):
        if c.name == "push":
            return s + [c.args[0]], None
        if c.name in ("pop", "top"):
            if not s:
                raise Inadmissible(f"{c.name} on empty stack")
            return (s[:-1], s[-1]) if c.name == "pop" else (s, s[-1])
        if c.name == "empty":
            return s, not s
        raise Inadmissible(c.name)

    def apply(self, c, cost):
        if c.name == "push":
            return self.arr.apply(Call("append", c.args), cost)
        if c.name == "pop":
            if self.arr.n == 0:
                cost.add("compare", 1)
                raise Inadmissible("pop on empty stack")
            return self.arr.apply(Call("pop"), cost)
        if c.name == "top":
            cost.add("compare", 1)
            if self.arr.n == 0:
                raise Inadmissible("top on empty stack")
            return self.arr.apply(Call("get", (self.arr.n - 1,)), cost)
        if c.name == "empty":
            cost.add("read", 1); cost.add("compare", 1)
            return self.arr.n == 0
        raise Inadmissible(c.name)


class QueueStructure(Structure):
    """Circular-buffer FIFO queue (doubling when full).  Layout: capacity
    words + 3 header words (head, n, capacity)."""

    name = "queue"
    SIGNATURE = (Move("enqueue", ("x",), "", True), Move("dequeue", (), "", True),
                 Move("front", (), ""), Move("len", (), ""))

    def __init__(self, values=(), capacity: int = 4):
        values = list(values)
        self.cap = max(capacity, len(values), 1)
        self.buf = values + [None] * (self.cap - len(values))
        self.head, self.n = 0, len(values)

    def abstract(self):
        return [self.buf[(self.head + i) % self.cap] for i in range(self.n)]

    def size_words(self):
        return self.cap + 3

    @classmethod
    def denote(cls, s, c):
        if c.name == "enqueue":
            return s + [c.args[0]], None
        if c.name in ("dequeue", "front"):
            if not s:
                raise Inadmissible(f"{c.name} on empty queue")
            return (s[1:], s[0]) if c.name == "dequeue" else (s, s[0])
        if c.name == "len":
            return s, len(s)
        raise Inadmissible(c.name)

    def _grow(self, cost):
        new = [self.buf[(self.head + i) % self.cap] for i in range(self.n)]
        cost.add("alloc", 2 * self.cap, f"reallocate {self.cap} -> {2 * self.cap}")
        cost.add("read", self.n); cost.add("write", self.n)
        self.buf = new + [None] * (2 * self.cap - self.n)
        self.cap *= 2
        self.head = 0

    def apply(self, c, cost):
        if c.name == "enqueue":
            if self.n == self.cap:
                self._grow(cost)
            cost.add("arith", 2, "tail = (head + n) mod cap"); cost.add("write", 1)
            self.buf[(self.head + self.n) % self.cap] = c.args[0]
            self.n += 1
            return None
        if c.name in ("dequeue", "front"):
            cost.add("compare", 1)
            if self.n == 0:
                raise Inadmissible(f"{c.name} on empty queue")
            cost.add("read", 1)
            v = self.buf[self.head]
            if c.name == "dequeue":
                cost.add("arith", 2); cost.add("write", 1)
                self.buf[self.head] = None
                self.head = (self.head + 1) % self.cap
                self.n -= 1
            return v
        if c.name == "len":
            cost.add("read", 1)
            return self.n
        raise Inadmissible(c.name)


class DequeStructure(QueueStructure):
    """Circular-buffer double-ended queue."""

    name = "deque"
    SIGNATURE = (Move("push_back", ("x",), "", True), Move("push_front", ("x",), "", True),
                 Move("pop_back", (), "", True), Move("pop_front", (), "", True),
                 Move("len", (), ""))

    @classmethod
    def denote(cls, s, c):
        if c.name == "push_back":
            return s + [c.args[0]], None
        if c.name == "push_front":
            return [c.args[0]] + s, None
        if c.name in ("pop_back", "pop_front"):
            if not s:
                raise Inadmissible(f"{c.name} on empty deque")
            return (s[:-1], s[-1]) if c.name == "pop_back" else (s[1:], s[0])
        if c.name == "len":
            return s, len(s)
        raise Inadmissible(c.name)

    def apply(self, c, cost):
        if c.name == "push_back":
            return super().apply(Call("enqueue", c.args), cost)
        if c.name == "pop_front":
            return super().apply(Call("dequeue"), cost)
        if c.name == "len":
            return super().apply(c, cost)
        if c.name == "push_front":
            if self.n == self.cap:
                self._grow(cost)
            cost.add("arith", 2); cost.add("write", 1)
            self.head = (self.head - 1) % self.cap
            self.buf[self.head] = c.args[0]
            self.n += 1
            return None
        if c.name == "pop_back":
            cost.add("compare", 1)
            if self.n == 0:
                raise Inadmissible("pop_back on empty deque")
            cost.add("arith", 2); cost.add("read", 1); cost.add("write", 1)
            j = (self.head + self.n - 1) % self.cap
            v, self.buf[j] = self.buf[j], None
            self.n -= 1
            return v
        raise Inadmissible(c.name)
