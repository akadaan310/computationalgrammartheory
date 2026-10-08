"""Classical algorithms against independent oracles (built-ins / brute force)."""
import itertools
import random
import re
import unittest
from collections import deque

from cgtsdk import Cost, compile_regex
from cgtsdk.algorithms import (EulerLCA, Fenwick, NaiveLCA, SegmentTree, SparseTable, UnionFind,
                               bellman_ford, bfs, bfs_path, binary_search, dfs_order, dijkstra,
                               edit_distance, floyd_warshall, heap_lca, heapsort, insertion_sort,
                               kmp_find_all, knapsack_01, kruskal, lcs_length, linear_search,
                               merge_sort, naive_find_all, path_grammar_closure, prim, product_reach,
                               quicksort, tarjan_scc, topological_sort, transitive_closure)
from cgtsdk.lab import random_digraph, random_labelled_graph, random_parent_array, random_weighted
from cgtsdk.structures import GraphStructure

R = random.Random(12345)


def reach_bfs(adj, s):
    seen, dq = {s}, deque([s])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); dq.append(v)
    return seen


class TestSearchSort(unittest.TestCase):
    def test_search(self):
        for _ in range(200):
            a = sorted(R.randrange(30) for _ in range(R.randrange(20)))
            x = R.randrange(-2, 32)
            self.assertEqual(binary_search(a, x), a.index(x) if x in a else -1)
            self.assertEqual(linear_search(a, x), a.index(x) if x in a else -1)

    def test_binary_search_compare_bound(self):
        a = list(range(1000))
        c = Cost()
        binary_search(a, 777, c)
        self.assertLessEqual(c.counts["compare"], 10 + 1 + 1)  # ⌈log₂ 1001⌉ + final check

    def test_sorts(self):
        for _ in range(150):
            a = [R.randrange(20) for _ in range(R.randrange(40))]
            for f in (insertion_sort, merge_sort, heapsort, quicksort):
                self.assertEqual(f(a), sorted(a), f.__name__)

    def test_counting_sort(self):
        from cgtsdk.algorithms import counting_sort
        for _ in range(100):
            a = [R.randrange(10) for _ in range(R.randrange(30))]
            c = Cost()
            self.assertEqual(counting_sort(a, 10, c), sorted(a))
            self.assertNotIn("compare", c.counts)

    def test_sort_compare_counts(self):
        a = list(range(256))
        c = Cost(); insertion_sort(a, c)
        self.assertEqual(c.counts["compare"], 255)  # sorted input: n-1
        c = Cost(); insertion_sort(a[::-1], c)
        self.assertEqual(c.counts["compare"], 256 * 255 // 2)
        c = Cost(); merge_sort(R.sample(range(1000), 1000), c)
        self.assertLessEqual(c.counts["compare"], 1000 * 10)


class TestUnionFindDP(unittest.TestCase):
    def test_union_find(self):
        for _ in range(50):
            n = 30
            uf = UnionFind(n)
            comp = list(range(n))
            for _ in range(40):
                a, b = R.randrange(n), R.randrange(n)
                uf.union(a, b)
                ca, cb = comp[a], comp[b]
                comp = [ca if c == cb else c for c in comp]
            for a in range(n):
                for b in range(n):
                    self.assertEqual(uf.find(a) == uf.find(b), comp[a] == comp[b])

    def test_dp_vs_bruteforce(self):
        for _ in range(60):
            x = "".join(R.choice("ab") for _ in range(R.randrange(7)))
            y = "".join(R.choice("ab") for _ in range(R.randrange(7)))
            best = 0
            for k in range(len(x) + 1):
                for idx in itertools.combinations(range(len(x)), k):
                    sub = "".join(x[i] for i in idx)
                    it = iter(y)
                    if all(ch in it for ch in sub):
                        best = max(best, k)
            self.assertEqual(lcs_length(x, y), best)
            self.assertLessEqual(edit_distance(x, y), max(len(x), len(y)))
            self.assertEqual(edit_distance(x, x), 0)
        for _ in range(60):
            w = [R.randrange(1, 8) for _ in range(6)]
            v = [R.randrange(10) for _ in range(6)]
            cap = R.randrange(15)
            brute = max(sum(v[i] for i in S) for k in range(7) for S in itertools.combinations(range(6), k)
                        if sum(w[i] for i in S) <= cap)
            self.assertEqual(knapsack_01(w, v, cap), brute)

    def test_edit_distance_known(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)


class TestStrings(unittest.TestCase):
    def test_kmp(self):
        for _ in range(300):
            t = "".join(R.choice("ab") for _ in range(R.randrange(30)))
            p = "".join(R.choice("ab") for _ in range(R.randrange(1, 5)))
            expect = [m.start() for m in re.finditer(f"(?={p})", t)]
            self.assertEqual(kmp_find_all(t, p), expect)
            self.assertEqual(naive_find_all(t, p), expect)

    def test_kmp_linear_compares(self):
        t, p = "a" * 2000, "a" * 50 + "b"
        c1, c2 = Cost(), Cost()
        kmp_find_all(t, p, c1); naive_find_all(t, p, c2)
        self.assertLessEqual(c1.counts["compare"], 2 * len(t) + 2 * len(p))
        self.assertGreater(c2.counts["compare"], 20 * len(t))


class TestRegex(unittest.TestCase):
    def test_against_python_re(self):
        exprs = ["a*", "(a b)* c", "(a | b)* c (a | b)*", "a+ b?", "(a | ε) b", "((a b) | c)* a"]
        for e in exprs:
            d = compile_regex(e)
            pat = re.compile(e.replace(" ", "").replace("ε", ""))
            for k in range(7):
                for w in itertools.product("abc", repeat=k):
                    self.assertEqual(d.accepts(list(w)), bool(pat.fullmatch("".join(w))), (e, w))

    def test_minimal_sizes(self):
        self.assertEqual(compile_regex("a*").size, 1)
        self.assertEqual(compile_regex("(a b)*").size, 2)
        # (a|b)* a (a|b)(a|b): the 3rd-from-last letter is a -> 2^3 states minimal (+ none dead)
        self.assertEqual(compile_regex("(a | b)* a (a | b) (a | b)").size, 8)


class TestGraphs(unittest.TestCase):
    def test_bfs_scc_closure_topo(self):
        for seed in range(30):
            n = R.randrange(1, 25)
            adj = random_digraph(n, R.choice([0.5, 1.5, 3]), seed)
            tc = transitive_closure(adj)
            comp, k = tarjan_scc(adj)
            for s in range(n):
                rs = reach_bfs(adj, s)
                self.assertEqual({t for t in range(n) if tc[s] >> t & 1}, rs)
                d = bfs(adj, s)
                self.assertEqual({t for t in range(n) if d[t] != float("inf")}, rs)
                for t in range(n):
                    same = s in reach_bfs(adj, t) and t in rs
                    self.assertEqual(comp[s] == comp[t], same)
                    if t in rs:
                        p = bfs_path(adj, s, t)
                        self.assertEqual(len(p) - 1, d[t])
                        self.assertTrue(all(b in adj[a] for a, b in zip(p, p[1:])))
            # comp numbering is reverse topological: edges go to <= comp
            for u in range(n):
                for v in adj[u]:
                    self.assertGreaterEqual(comp[u], comp[v])
            order = topological_sort(adj)
            if k == n and all(u not in adj[u] for u in range(n)):
                pos = {v: i for i, v in enumerate(order)}
                self.assertTrue(all(pos[u] < pos[v] for u in range(n) for v in adj[u]))
            else:
                self.assertIsNone(order)
            disc, fin = dfs_order(adj)
            self.assertEqual(sorted(disc), list(range(n)))
            self.assertEqual(sorted(fin), list(range(n)))

    def test_shortest_paths(self):
        for seed in range(25):
            n = R.randrange(2, 20)
            adj = random_digraph(n, 2.5, seed)
            w = random_weighted(adj, seed)
            fw = floyd_warshall(n, [(u, v, c) for u in range(n) for v, c in w[u]])
            for s in range(n):
                self.assertEqual(dijkstra(w, s), fw[s])
                self.assertEqual(bellman_ford(w, s), fw[s])

    def test_negative_cycle(self):
        w = [[(1, 1)], [(2, -3)], [(0, 1)]]
        self.assertIsNone(bellman_ford(w, 0))

    def test_mst(self):
        for seed in range(25):
            rng = random.Random(seed)
            n = rng.randrange(1, 12)
            edges = [(rng.randrange(1, 9), u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.5]
            k, _ = kruskal(n, edges)
            p, _ = prim(n, edges)
            self.assertEqual(k, p)
            if len(edges) <= 12:  # brute force: minimum-weight maximal spanning forest
                uf0 = UnionFind(n)
                for _, u, v in edges:
                    uf0.union(u, v)
                need = n - uf0.components
                best = float("inf")
                for S in itertools.combinations(edges, need):
                    uf = UnionFind(n)
                    if all(uf.union(u, v) for _, u, v in S):
                        best = min(best, sum(w for w, _, _ in S))
                self.assertEqual(k, best if need else 0)

    def test_path_grammar_formula(self):
        """THM-004(a) exactly, for the SDK implementation."""
        for seed in range(20):
            adj = random_digraph(R.randrange(2, 30), 1.5, seed)
            n = len(adj)
            c = Cost()
            P = path_grammar_closure(adj, "linear", c)
            indeg = [0] * n
            for u in range(n):
                for v in adj[u]:
                    indeg[v] += 1
            m = sum(map(len, adj))
            self.assertEqual(c.counts.get("rule", 0), m + sum(indeg[w] * len(P[w]) for w in range(n)))
            P2 = path_grammar_closure(adj, "doubling")
            self.assertEqual(P, P2)
            tc = transitive_closure(adj)
            for s in range(n):  # P⁺ vs reflexive closure
                plus = {t for t in range(n) if any(tc[x] >> t & 1 for x in adj[s])}
                self.assertEqual(P[s], plus)

    def test_product_reach_vs_walk_enumeration(self):
        langs = ["a*", "(a b)* c", "(a | b | c)* c (a | b | c)*", "(a a)*"]
        for seed in range(15):
            n = 6
            E = random_labelled_graph(n, 1.6, "abc", seed)
            g = GraphStructure(n, E)
            for L in langs:
                d = compile_regex(L)
                got = product_reach(g, 0, d)
                # walks of length ≤ n·|Q| suffice (pumping argument)
                expect, frontier = set(), {(0, d.start)}
                if d.start in d.accept:
                    expect.add(0)
                seen = set(frontier)
                for _ in range(n * d.size + 1):
                    nxt = set()
                    for (y, q) in frontier:
                        for (u, a, v) in E:
                            if u == y and d.step(q, a) is not None:
                                nxt.add((v, d.step(q, a)))
                    for (v, q) in nxt:
                        if q in d.accept:
                            expect.add(v)
                    frontier = nxt - seen
                    seen |= nxt
                self.assertEqual(got, expect, (seed, L))


class TestRanges(unittest.TestCase):
    def test_fenwick_segment_sparse(self):
        for _ in range(40):
            n = R.randrange(1, 40)
            a = [R.randrange(-5, 10) for _ in range(n)]
            fw, sg = Fenwick(a), SegmentTree(a)
            for _ in range(30):
                i, x = R.randrange(n), R.randrange(-5, 10)
                fw.add(i, x - a[i]); sg.assign(i, x); a[i] = x
                l = R.randrange(n); r = R.randrange(l, n + 1)
                self.assertEqual(fw.range_sum(l, r), sum(a[l:r]))
                self.assertEqual(sg.query(l, r), sum(a[l:r]))
            st = SparseTable(a)
            for l in range(n):
                for r in range(l, n):
                    self.assertEqual(st.query(l, r), min(a[l:r + 1]))

    def test_fenwick_log_cost(self):
        fw = Fenwick([1] * 1024)
        c = Cost()
        fw.prefix(1023, c)
        self.assertLessEqual(c.counts["read"], 10)

    def test_lca_three_ways(self):
        for shape in ("random", "path", "star", "complete"):
            par = random_parent_array(200, 3, shape)
            nv, eu = NaiveLCA(par), EulerLCA(par)
            for _ in range(300):
                u, v = R.randrange(200), R.randrange(200)
                self.assertEqual(nv.query(u, v), eu.query(u, v))
            if shape == "complete":   # heap numbering: node i ↔ numeral i+1
                for _ in range(300):
                    u, v = R.randrange(200), R.randrange(200)
                    self.assertEqual(heap_lca(u + 1, v + 1) - 1, nv.query(u, v))


if __name__ == "__main__":
    unittest.main()
