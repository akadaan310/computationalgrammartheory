---
title: Range Queries, Dynamic Programming, and Strings
status: mixed
statusnote: Classical algorithms; the grammatical reading identifies which mechanism each uses.
description: Fenwick and segment trees as arithmetic addressing, sparse tables as precomputation, dynamic programming as shared derivations, and string matching as automata.
---

::: objectives
- Explain Fenwick trees and segment trees as implicit trees addressed by bit arithmetic, and state their costs.
- Contrast them with sparse tables, which trade preprocessing for constant-time queries.
- Read dynamic programming as the evaluation of a grammar of subproblems with sharing, and connect it to parsing.
- Explain the Knuth–Morris–Pratt algorithm as a deterministic automaton for its pattern, with linear preprocessing.
:::

## Prefix sums by bit arithmetic {#sec:fenwick}

**Problem.** Maintain an array $a_0, \dots, a_{n-1}$ under point updates $a_i \mathrel{+}= \delta$ and answer prefix sums $\sum_{j < i} a_j$.

A plain array answers updates in $\Oh(1)$ and sums in $\Theta(n)$; a prefix-sum array does the reverse. The **Fenwick tree** \cite{fenwick1994} answers both in $\Oh(\log n)$ with a single array $t[1..n]$, where slot $i$ stores the sum of the range $(i - \lowbit(i),\, i]$ and $\lowbit(i) = i \mathbin{\&} (-i)$ is the lowest set bit of $i$. A prefix sum walks $i \to i - \lowbit(i)$, an update walks $i \to i + \lowbit(i)$:

$$\sum_{j < i} a_j = t[i] + t[i - \lowbit(i)] + \cdots, \qquad \text{update at } i:\; t[i] \mathrel{+}= \delta,\; t[i + \lowbit(i)] \mathrel{+}= \delta,\; \dots \label{eq:fenwick}$$

Each walk visits at most $\lceil \log_2 (n+1) \rceil$ slots, because each step clears (or carries past) one bit. The Fenwick tree is an implicit tree whose parent pointers are **computed** from the index by bit arithmetic — the same mechanism as the heap numeration (M-ARITH), with density exactly $1$: it uses $n$ slots for $n$ elements. The **segment tree** is the heap-numbered binary tree over the array's leaves (leaves at $n, \dots, 2n-1$, node $i$ with children $2i$, $2i + 1$), supporting any associative operation in $\Oh(\log n)$.

```python run
from cgtsdk import Cost
from cgtsdk.algorithms import Fenwick, SegmentTree, SparseTable

n = 1 << 16
a = [(7 * i) % 101 for i in range(n)]
fw, sg = Fenwick(a), SegmentTree(a)
st_cost = Cost(); st = SparseTable(a, cost=st_cost)
c1, c2, c3 = Cost(), Cost(), Cost()
l, r = 12345, 54321
assert fw.range_sum(l, r, c1) == sg.query(l, r, c2) == sum(a[l:r])
assert st.query(l, r - 1, c3) == min(a[l:r])
print(f"Fenwick range sum: {c1.total} steps   segment tree: {c2.total} steps   (log2 n = 16)")
print(f"sparse-table range min: {c3.total} steps after a build of {st_cost.total} steps and {st.size_words} words")
```

```output
Fenwick range sum: 39 steps   segment tree: 46 steps   (log2 n = 16)
sparse-table range min: 6 steps after a build of 1835044 steps and 983058 words
```

The sparse table is the opposite mechanism: **precomputation** (M-PRE). It stores the minimum of every range of length $2^j$, after which any range minimum is the minimum of two overlapping stored ranges — $\Oh(1)$ per query — at the price of $\Theta(n \log n)$ build steps and words, and of total invalidation on any update. This is the LCA index of Chapter 5 in its general form. For idempotent operations (min, max, gcd), both mechanisms are available; which one wins depends on the ratio of queries to updates, exactly as in the break-even analysis of Chapter 12.

## Dynamic programming as shared derivations {#sec:dp}

A dynamic program defines a quantity by a **recurrence** — a grammar of subproblems — and evaluates each subproblem once. For the longest common subsequence of strings $x$ and $y$:

$$L(i, j) = \begin{cases} 0 & i = 0 \text{ or } j = 0,\\ L(i-1, j-1) + 1 & x_i = y_j,\\ \max\big(L(i-1, j),\, L(i, j-1)\big) & \text{otherwise.}\end{cases} \label{eq:lcs}$$

Read as a grammar, each production rewrites $L(i,j)$ into smaller instances; a naive evaluation expands a derivation *tree* with exponentially many nodes, while the table evaluates the derivation *DAG*, in which identical subproblems are shared. Dynamic programming is therefore the sharing mechanism (M-SHARE) applied to derivations — the same idea as the minimal DAG of a tree (Chapter 5) and the product construction's sharing of walks (Chapter 8). Its cost is the number of distinct subproblems times the work per production: $\Theta(|x||y|)$ for LCS and edit distance, $\Theta(nW)$ for 0/1 knapsack with capacity $W$.

The last bound is a warning about what "polynomial" means. $\Theta(nW)$ is polynomial in the *value* $W$ but exponential in its *length* $\log_2 W$: knapsack is NP-hard, and dynamic programming does not contradict that. It is the first instance in this book of a phenomenon Chapter 14 makes systematic — a grammar (here, of subproblems) whose size depends on numbers in the input rather than on the input's length.

```python run
import itertools, random
from cgtsdk import Cost
from cgtsdk.algorithms import edit_distance, knapsack_01, lcs_length

c = Cost()
print("edit distance(kitten, sitting) =", edit_distance("kitten", "sitting", c), " table cells:", c.counts["write"])
rng = random.Random(5)
w = [rng.randrange(1, 20) for _ in range(12)]; v = [rng.randrange(1, 30) for _ in range(12)]
for W in (10, 100, 1000):
    c = Cost()
    best = knapsack_01(w, v, W, c)
    brute = max(sum(v[i] for i in S) for k in range(13) for S in itertools.combinations(range(12), k) if sum(w[i] for i in S) <= W)
    print(f"knapsack W={W:5d}: best={best} (brute force {brute})  DP cells={c.counts.get('write', 0)}")
```

```output
edit distance(kitten, sitting) = 3  table cells: 42
knapsack W=   10: best=57 (brute force 57)  DP cells=39
knapsack W=  100: best=147 (brute force 147)  DP cells=1102
knapsack W= 1000: best=151 (brute force 151)  DP cells=11902
```

The number of table cells grows linearly with $W$ — ten times larger $W$, about ten times more work — even though the input grew by only one decimal digit per item.

Parsing is the original instance. The CYK algorithm decides membership of a string of length $\ell$ in a context-free language by a dynamic program over substrings and nonterminals in $\Oh(\ell^3)$ time — the same table-over-pairs pattern as CFL-reachability in Chapter 8 \cite{yannakakis1990}.

## String matching as an automaton {#sec:kmp}

**Problem.** Find all occurrences of a pattern $p$ of length $k$ in a text of length $n$.

The naive algorithm compares $p$ at every shift: $\Theta(nk)$ comparisons in the worst case. The Knuth–Morris–Pratt algorithm \cite{kmp1977} precomputes the **failure function** of $p$ in $\Oh(k)$ — for each prefix, the longest proper border — which is a compact encoding of the deterministic automaton recognizing $\Sigma^* p$. Running that automaton over the text never moves backwards in the text, and makes at most $2n$ comparisons.

```python run
from cgtsdk import Cost
from cgtsdk.algorithms import kmp_find_all, naive_find_all

text, pat = "a" * 5000, "a" * 60 + "b"
c1, c2 = Cost(), Cost()
assert kmp_find_all(text, pat, c1) == naive_find_all(text, pat, c2) == []
print(f"naive: {c2.counts['compare']} comparisons   KMP (including preprocessing): {c1.counts['compare']} comparisons   2n = {2 * len(text)}")
```

```output
naive: 301340 comparisons   KMP (including preprocessing): 10059 comparisons   2n = 10000
```

KMP is M-PRE: a small amount of preprocessing *of the query* (the pattern), producing an automaton — a grammar — that is then executed over the data. The trie of Chapter 4 does the same for a set of keys, and the Aho–Corasick automaton for a set of patterns. String matching is one domain where "compile the query into an automaton, then run it" is the classical algorithm, not a reinterpretation.

::: exercise {#exr:11-1}
Prove that $i - \lowbit(i)$ clears the lowest set bit of $i$, and hence that a Fenwick prefix sum visits at most $\lceil \log_2(n+1) \rceil$ slots.
:::

::: exercise {#exr:11-2}
Write the recurrence for edit distance as a grammar of subproblems and draw the derivation DAG for $x = \mathrm{ab}$, $y = \mathrm{ba}$. How many nodes would the derivation *tree* have?
:::

::: exercise {#exr:11-3}
Compute the KMP failure function of $p = \mathrm{abacabab}$ and draw the corresponding automaton for $\Sigma^* p$ over $\{a, b, c\}$.
:::

::: solution {of="exr:11-3"}
Borders of the prefixes $a, ab, aba, abac, abaca, abacab, abacaba, abacabab$ have lengths $0, 0, 1, 0, 1, 2, 3, 2$. The automaton has states $0..8$ (matched prefix length); from state $j$ on the letter $p_{j+1}$ go to $j+1$, otherwise follow failure links until a state with that transition (or $0$).
:::

::: exercise {#exr:11-4}
For range-minimum queries under updates, compare a segment tree with a sparse table rebuilt after each update. Using the counted costs of the SDK, find the number of queries per update at which the sparse table becomes cheaper for $n = 2^{12}$.
:::

::: summary
- Fenwick and segment trees are implicit trees addressed by bit arithmetic (M-ARITH): $\Oh(\log n)$ updates and queries with density-one storage.
- Sparse tables trade $\Theta(n \log n)$ preprocessing for $\Oh(1)$ queries (M-PRE) and break on updates.
- Dynamic programming evaluates a grammar of subproblems on its derivation DAG — sharing (M-SHARE); pseudo-polynomial bounds are polynomial in numbers, not in input length.
- KMP compiles the pattern into an automaton in $\Oh(k)$ and matches in at most $2n$ comparisons — preprocessing the query into a grammar.
:::
