"""PageRank: three solvers agree, the contraction bound holds, and the
grammar-constrained surfer reduces to PageRank for the universal language."""
import random
import unittest

from cgtsdk import DFA, compile_regex
from cgtsdk.algorithms import (constrained_pagerank, pagerank_exact, pagerank_gauss_seidel,
                               pagerank_power)
from cgtsdk.lab import random_digraph, random_labelled_graph


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


class TestPageRank(unittest.TestCase):
    def test_solvers_agree(self):
        for seed in range(15):
            adj = random_digraph(30, random.Random(seed).choice([0.5, 1.5, 3]), seed)
            for alpha in (0.0, 0.5, 0.85, 0.99):
                exact = pagerank_exact(adj, alpha)
                self.assertAlmostEqual(sum(exact), 1.0, places=9)
                pw = pagerank_power(adj, alpha, tol=1e-12)
                gs = pagerank_gauss_seidel(adj, alpha, tol=1e-13)
                self.assertTrue(pw.converged and gs.converged)
                self.assertLess(l1(pw.scores, exact), 1e-9)
                self.assertLess(l1(gs.scores, exact), 1e-8)
                self.assertLessEqual(l1(pw.scores, exact), pw.error_bound + 1e-12)

    def test_contraction_each_step(self):
        """‖x_k − π‖₁ ≤ α‖x_{k−1} − π‖₁ for every k (CGT-THM-008)."""
        adj = random_digraph(40, 1.2, 9)
        alpha = 0.9
        pi = pagerank_exact(adj, alpha)
        prev = None
        for k in range(1, 40):
            x = pagerank_power(adj, alpha, tol=0, max_iter=k).scores
            if prev is not None:
                self.assertLessEqual(l1(x, pi), alpha * l1(prev, pi) + 1e-12)
            prev = x

    def test_personalization_and_dangling(self):
        adj = [[1], [2], []]           # vertex 2 is dangling
        v = [1.0, 0.0, 0.0]
        x = pagerank_power(adj, 0.85, v, tol=1e-13).scores
        self.assertLess(l1(x, pagerank_exact(adj, 0.85, v)), 1e-10)
        with self.assertRaises(ValueError):
            pagerank_power(adj, 1.0)
        with self.assertRaises(ValueError):
            pagerank_power(adj, 0.85, [0.5, 0.5, 0.5])

    def test_warm_start_saves_iterations(self):
        adj = random_digraph(200, 2.0, 4)
        base = pagerank_power(adj, 0.85, tol=1e-10)
        adj[0].append(5)
        cold = pagerank_power(adj, 0.85, tol=1e-10)
        warm = pagerank_power(adj, 0.85, tol=1e-10, x0=base.scores)
        self.assertLess(l1(cold.scores, warm.scores), 1e-9)
        self.assertLess(warm.iterations, cold.iterations)

    def test_constrained_universal_equals_pagerank(self):
        for seed in range(10):
            n = 25
            E = random_labelled_graph(n, 2.0, "abc", seed)
            adj = [[] for _ in range(n)]
            for u, _, v in E:
                adj[u].append(v)
            scores, pr, N = constrained_pagerank(n, E, DFA.universal("abc"), tol=1e-12)
            self.assertEqual(N, n)
            self.assertLess(l1(scores, pagerank_exact(adj)), 1e-9)

    def test_constrained_bounded_states(self):
        n = 40
        E = random_labelled_graph(n, 3.0, "ab", 1)
        d = compile_regex("(a b)* (a | ε)")  # prefix-closed alternation
        scores, pr, N = constrained_pagerank(n, E, d)
        self.assertLessEqual(N, d.size * n)
        self.assertAlmostEqual(sum(scores), 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
