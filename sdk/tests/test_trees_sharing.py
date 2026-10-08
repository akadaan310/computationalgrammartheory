"""BST/AVL invariants under random and degenerate workloads; minimal-DAG
sharing and CGT-THM-005(a) on small cases."""
import random
import unittest

from cgtsdk import Cost
from cgtsdk.sharing import DagGrammar, Explicit, full_binary, monadic_path, random_tree
from cgtsdk.structures import BSTStructure


class TestBST(unittest.TestCase):
    def test_degenerate_insertions_do_not_recurse(self):
        for balance in ("none", "avl"):
            t = BSTStructure(range(5000), balance)
            self.assertTrue(t.check_invariants())
            self.assertEqual(t.tree_height(), 5000 if balance == "none" else t.tree_height())
            self.assertTrue(t.grammar().resolve("contains(4999)"))
            for k in range(0, 5000, 7):
                t.grammar().execute(f"delete({k})")
            self.assertTrue(t.check_invariants())
        self.assertLessEqual(BSTStructure(range(5000), "avl").tree_height(), 18)  # 1.44 log2 n

    def test_random_against_set(self):
        rng = random.Random(9)
        for balance in ("none", "avl"):
            t, ref = BSTStructure([], balance), set()
            g = t.grammar()
            for _ in range(3000):
                k = rng.randrange(300)
                if rng.random() < 0.55:
                    g.execute(f"insert({k})"); ref.add(k)
                elif k in ref:
                    g.execute(f"delete({k})"); ref.discard(k)
                else:
                    self.assertFalse(g.execute(f"delete({k})").defined)
            self.assertEqual(t.abstract(), tuple(sorted(ref)))
            self.assertTrue(t.check_invariants())


class TestSharing(unittest.TestCase):
    def test_thm005a(self):
        for h in range(1, 6):
            F = Explicit(); F.roots.append(full_binary(F, h))
            for i in range(F.n):
                D = DagGrammar.from_explicit(F)
                path, _ = D.access(i, Cost())
                d = len(path) - 1
                self.assertEqual(D.relabel(i, "fresh", Cost()), d + 1)
                self.assertEqual(D.live_size(), h + d + 1)

    def test_rank_access_and_no_compression_of_paths(self):
        rng = random.Random(1)
        F = Explicit()
        for _ in range(20):
            F.roots.append(random_tree(F, 15, "ab", rng))
        D = DagGrammar.from_explicit(F)
        pre, st = [], list(reversed(F.roots))
        while st:
            v = st.pop(); pre.append(v); st.extend(reversed(F.children[v]))
        for i in range(F.n):
            self.assertEqual(D.access(i, Cost())[1], F.label[pre[i]])
        P = Explicit(); P.roots.append(monadic_path(P, 300))
        self.assertEqual(DagGrammar.from_explicit(P).live_size(), 300)


if __name__ == "__main__":
    unittest.main()
