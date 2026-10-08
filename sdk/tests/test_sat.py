import random
import unittest

from cgtsdk.algorithms import brute_force_count, satisfies, solution_automaton, two_sat


class TestSat(unittest.TestCase):
    def test_two_sat_vs_brute_force(self):
        rng = random.Random(8)
        for _ in range(400):
            n = rng.randrange(1, 8)
            cls = [tuple(rng.choice([v, -v]) for v in rng.sample(range(1, n + 1), min(2, n)) * (1 if n > 1 else 2))[:2]
                   for _ in range(rng.randrange(1, 3 * n + 2))]
            a = two_sat(n, cls)
            sat = brute_force_count(n, cls) > 0
            self.assertEqual(a is not None, sat)
            if a is not None:
                self.assertTrue(satisfies(a, cls))

    def test_solution_automaton_counts_models(self):
        rng = random.Random(9)
        for _ in range(60):
            n = rng.randrange(1, 11)
            cls = [tuple(rng.choice([v, -v]) for v in rng.sample(range(1, n + 1), min(3, n))) for _ in range(rng.randrange(1, 4 * n))]
            w, models, nodes = solution_automaton(n, cls)
            self.assertEqual(models, brute_force_count(n, cls))
            self.assertEqual(nodes, sum(w))


if __name__ == "__main__":
    unittest.main()
