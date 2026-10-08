"""Exhaustive small-case checks of the compiled-word classes (THM-006)."""
import itertools
import random
import unittest

from cgtsdk.addressing import (AffineMod, BoxTranslation, HeapWord, XorMask, compile_word,
                               debruijn_moves, grid_moves, heap_walk, hypercube_moves, row_major)


class TestHeapWord(unittest.TestCase):
    def test_exhaustive(self):
        """All words of length ≤ 7 over {L,R,U}, all n ≤ 40, all start nodes."""
        checked = 0
        for L in range(8):
            for w in itertools.product("LRU", repeat=L):
                for n in range(1, 41):
                    f = HeapWord.compile(w, n)
                    for x in range(1, n + 1):
                        self.assertEqual(f(x), heap_walk(w, x, n), (w, n, x))
                        checked += 1
        self.assertGreater(checked, 2_000_000)

    def test_long_random_words(self):
        rng = random.Random(3)
        for _ in range(300):
            n = rng.randrange(1, 5000)
            w = [rng.choice("LRUUU") for _ in range(rng.randrange(200))]  # U-heavy keeps words defined
            f = HeapWord.compile(w, n)
            for _ in range(40):
                x = rng.randrange(1, n + 1)
                self.assertEqual(f(x), heap_walk(w, x, n))


class TestOtherClasses(unittest.TestCase):
    def test_debruijn(self):
        mv = debruijn_moves(3, 4)
        for L in range(6):
            for w in itertools.product(sorted(mv), repeat=L):
                f = compile_word(mv, w, AffineMod.identity(81))
                for x in range(81):
                    y = x
                    for a in w:
                        y = mv[a](y)
                    self.assertEqual(f(x), y)

    def test_hypercube(self):
        mv = hypercube_moves(4)
        for w in itertools.product(sorted(mv), repeat=5):
            f = compile_word(mv, w, XorMask(0))
            for x in range(16):
                y = x
                for a in w:
                    y = mv[a](y)
                self.assertEqual(f(x), y)

    def test_grid_with_boundaries(self):
        dims = (3, 4)
        mv = grid_moves(dims)
        for L in range(6):
            for w in itertools.product(sorted(mv), repeat=L):
                f = compile_word(mv, w, BoxTranslation.identity(dims))
                for x in itertools.product(range(3), range(4)):
                    y = x
                    for a in w:
                        y = mv[a](y) if y is not None else None
                    self.assertEqual(f(x), y, (w, x))
        self.assertEqual(row_major((2, 3), dims), 11)


if __name__ == "__main__":
    unittest.main()
