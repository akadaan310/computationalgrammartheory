"""Grammar layers and the adequacy property for every reference structure:
on random workloads, the representation's executed values equal the
reference semantics, including *where* an expression becomes undefined."""
import random
import unittest

from cgtsdk import Call, Inadmissible, compile_regex, parse_expression
from cgtsdk.structures import (ArrayStructure, AutomatonStructure, BinaryTreeStructure,
                               BSTStructure, DequeStructure, GraphStructure, HashTableStructure,
                               HeapStructure, LinkedListStructure, QueueStructure, StackStructure,
                               TrieStructure)


class TestParsing(unittest.TestCase):
    def test_parse(self):
        calls = parse_expression("get(2); set(0, 'x') L  R; goto('01')")
        self.assertEqual([c.name for c in calls], ["get", "set", "L", "R", "goto"])
        self.assertEqual(calls[1].args, (0, "x"))
        self.assertEqual(calls[4].args, ("01",))

    def test_parse_errors(self):
        for bad in ("get(", "get(1))", "1abc", "get(import os)"):
            with self.assertRaises(SyntaxError):
                parse_expression(bad)

    def test_three_layers_are_distinct(self):
        g = ArrayStructure([1, 2, 3]).grammar()
        r = g.execute("nope")
        self.assertFalse(r.syntax.ok)            # syntax layer
        r = g.execute("get(1, 2)")
        self.assertFalse(r.syntax.ok)            # arity is syntax
        r = g.execute("get(7)")
        self.assertTrue(r.syntax.ok)
        self.assertFalse(r.defined)              # semantics: ⟦w⟧ = ∅
        self.assertEqual(r.undefined_at, 0)
        self.assertTrue(r.adequate)
        r = g.execute("get(1)")
        self.assertTrue(r.defined)
        self.assertEqual(r.value, 2)
        self.assertGreater(r.cost.total, 0)      # execution layer

    def test_admissibility_projection(self):
        g = GraphStructure(3, [(0, "a", 1), (1, "b", 2), (2, "a", 0)])
        gr = g.grammar("(a b)*")
        self.assertTrue(gr.check_syntax("a here b here").ok)  # observers are free
        self.assertFalse(gr.check_syntax("a here").ok)
        with self.assertRaises(ValueError):
            g.grammar("a z")

    def test_resolve_raises(self):
        g = StackStructure().grammar()
        with self.assertRaises(Inadmissible):
            g.resolve("push(1) pop pop")
        self.assertEqual(g.resolve("push(5) top"), 5)


def _random_calls(kind, rng, n_calls, universe):
    out = []
    for _ in range(n_calls):
        x = rng.randrange(-2, universe + 2)
        if kind in ("array", "list"):
            ops = ["get", "set", "len", "insert", "delete"] + (["append", "pop"] if kind == "array"
                                                             else ["push_front", "pop_front"])
            op = rng.choice(ops)
            args = {"get": (x,), "set": (x, rng.randrange(100)), "len": (), "insert": (x, rng.randrange(100)),
                    "delete": (x,), "append": (rng.randrange(100),), "pop": (),
                    "push_front": (rng.randrange(100),), "pop_front": ()}[op]
        elif kind == "stack":
            op = rng.choice(["push", "pop", "top", "empty"])
            args = (x,) if op == "push" else ()
        elif kind == "queue":
            op = rng.choice(["enqueue", "dequeue", "front", "len"])
            args = (x,) if op == "enqueue" else ()
        elif kind == "deque":
            op = rng.choice(["push_back", "push_front", "pop_back", "pop_front", "len"])
            args = (x,) if op.startswith("push") else ()
        elif kind == "hash":
            op = rng.choice(["put", "get", "contains", "delete", "len"])
            args = {"put": (x, rng.randrange(9)), "get": (x,), "contains": (x,), "delete": (x,), "len": ()}[op]
        elif kind == "heap":
            op = rng.choice(["push", "pop_min", "peek", "len"])
            args = (x,) if op == "push" else ()
        elif kind == "bst":
            op = rng.choice(["insert", "contains", "delete", "min"])
            args = () if op == "min" else (x,)
        elif kind == "trie":
            op = rng.choice(["insert", "contains", "count_prefix"])
            args = ("".join(rng.choice("ab") for _ in range(rng.randrange(4))),)
        out.append(Call(op, args))
    return out


class TestAdequacy(unittest.TestCase):
    """Randomised adequacy: executed values == denoted values (CGT-DEF-003)."""

    CASES = [
        ("array", lambda: ArrayStructure([1, 2, 3])),
        ("list", lambda: LinkedListStructure([1, 2, 3])),
        ("stack", lambda: StackStructure([1])),
        ("queue", lambda: QueueStructure([1, 2], capacity=2)),
        ("deque", lambda: DequeStructure([1, 2], capacity=2)),
        ("hash", lambda: HashTableStructure({1: 1, 2: 4})),
        ("heap", lambda: HeapStructure([3, 1])),
        ("bst", lambda: BSTStructure([5, 2, 8])),
        ("bst", lambda: BSTStructure([5, 2, 8], balance="avl")),
        ("trie", lambda: TrieStructure(["a", "ab"])),
    ]

    def test_random_workloads(self):
        rng = random.Random(2026)
        for kind, make in self.CASES:
            for trial in range(60):
                s = make()
                g = s.grammar()
                # execute call by call so that undefined calls do not end the trial
                for c in _random_calls(kind, rng, 25, 8):
                    r = g.execute([c])
                    self.assertTrue(r.syntax.ok, (kind, c, r.syntax.error))
                    self.assertTrue(r.adequate, (kind, trial, c, r.summary(), r.denoted))

    def test_hash_adversarial_collisions(self):
        """All keys collide: still correct, but probes grow linearly."""
        good = HashTableStructure(capacity=64).grammar()
        bad = HashTableStructure(capacity=64, hash_fn=lambda k: 0).grammar()
        for i in range(24):
            good.execute(f"put({i}, {i})"); bad.execute(f"put({i}, {i})")
        rg, rb = good.execute("get(23)"), bad.execute("get(23)")
        self.assertEqual(rg.value, rb.value)
        self.assertEqual(rb.cost.counts["probe"], 24)   # 23 colliding keys precede it
        self.assertLess(rg.cost.counts["probe"], 6)


class TestTreeRepresentations(unittest.TestCase):
    def test_pointer_and_heap_agree(self):
        rng = random.Random(7)
        for shape in ("complete", "path"):
            make = (lambda rep: BinaryTreeStructure.complete(31, rep)) if shape == "complete" else \
                   (lambda rep: BinaryTreeStructure.path(20, "01", rep))
            p, h = make("pointer").grammar(), make("heap").grammar()
            for _ in range(300):
                op = rng.choice(["L", "R", "U", "read", "here", "root", "goto"])
                if op == "goto":
                    a = "".join(rng.choice("01") for _ in range(rng.randrange(6)))
                    e = f"goto('{a}')"
                else:
                    e = op
                rp, rh = p.execute(e), h.execute(e)
                self.assertEqual((rp.defined, rp.values), (rh.defined, rh.values), e)
                self.assertTrue(rp.adequate and rh.adequate)

    def test_density(self):
        self.assertGreater(BinaryTreeStructure.complete(31).density, 0.5)
        self.assertLess(BinaryTreeStructure.path(40).density, 1e-9)

    def test_goto_cost_shapes(self):
        """THM-003: pointer goto costs |addr|; heap goto costs ⌈bits/64⌉+1."""
        deep = "0" * 200
        tp = BinaryTreeStructure.path(201, "0", "pointer").grammar()
        th = BinaryTreeStructure.path(201, "0", "heap").grammar()
        cp = tp.execute(f"goto('{deep}')").cost.total
        ch = th.execute(f"goto('{deep}')").cost.total
        self.assertEqual(cp, 201)          # 1 read + 200 pointer hops
        self.assertEqual(ch, 4 + 1)        # ⌈201/64⌉ = 4 word ops + 1 probe


class TestGraphAndAutomaton(unittest.TestCase):
    def test_relational_semantics(self):
        g = GraphStructure(4, [(0, "a", 1), (0, "a", 2), (1, "b", 3), (2, "b", 3)]).grammar()
        r = g.execute("at(0) a here b here")
        self.assertEqual(r.values, [None, None, [1, 2], None, [3]])
        r = g.execute("at(3) a")
        self.assertFalse(r.defined)

    def test_automaton_structure(self):
        d = compile_regex("(a b)*")
        g = AutomatonStructure(d).grammar()
        self.assertEqual(g.execute("a b accepting a accepting").values, [None, None, True, None, False])
        self.assertFalse(g.execute("reset b").defined)


if __name__ == "__main__":
    unittest.main()
