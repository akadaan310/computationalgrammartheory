---
title: Searching and Sorting Reconstructed
status: mixed
statusnote: Classical algorithms with standard proofs; each is mapped to its grammar, including where the grammar adds nothing.
description: Linear and binary search, four comparison sorts and counting sort — with invariants, counted costs, the comparison lower bound, and the one way around it.
---

::: objectives
- State, implement and prove correct linear search, binary search, insertion sort, merge sort, heapsort, quicksort and counting sort.
- Predict their comparison counts exactly or within stated bounds, and check the predictions with counted costs.
- Prove the $\Omega(n \log n)$ lower bound for comparison sorting, and explain it as a statement about the grammar of comparisons.
- Explain why counting sort escapes the bound — arithmetic addressing — and exactly when it stops helping.
:::

Each algorithm in Part III is presented as an **algorithm card**: the problem, the conventional algorithm with pseudocode and a correctness argument, its costs, a pointer to its SDK implementation, its CGT reading (which grammar it operates on, and how grammar operations map to implementation steps), and — always — where the grammatical view adds nothing. This chapter's verdict is mostly *equivalence*: sorting and searching are the home ground of classical algorithm design, and the grammatical view re-describes them without making them faster. That verdict is itself a result.

## Searching {#sec:search}

**Problem.** Given a sequence $a_0, \dots, a_{n-1}$ and a value $x$, find an index $i$ with $a_i = x$, or report that none exists.

::: algorithm {#alg:binary title="Binary search (leftmost occurrence)"}
```text
lo ← 0; hi ← n                      invariant: a[lo-1] < x ≤ a[hi]  (sentinels a[-1] = −∞, a[n] = +∞)
while lo < hi:
    mid ← ⌊(lo + hi)/2⌋
    if a[mid] < x: lo ← mid + 1 else: hi ← mid
return lo if lo < n and a[lo] = x else −1
```
:::

::: proposition {#prop:binary status="standard"}
On a sorted sequence, binary search returns the leftmost index of $x$ or $-1$, using at most $\lceil \log_2(n+1) \rceil$ loop comparisons plus one final equality test. Linear search uses at most $n$ comparisons and needs no order.
:::

::: proof
The invariant holds initially and is preserved by both branches because the sequence is sorted; the interval $[lo, hi)$ strictly shrinks and at least halves, so the loop runs at most $\lceil \log_2 (n+1) \rceil$ times. At exit $lo = hi$, and the invariant says every element before $lo$ is $< x$ and $a_{lo} \ge x$; hence $x$ occurs iff $a_{lo} = x$, and then $lo$ is its leftmost index.
:::

*SDK:* `cgtsdk.algorithms.binary_search`, `linear_search`. *Grammar:* binary search is navigation in the implicit balanced search tree whose root is the middle element: each comparison is a move $L$ or $R$, and the comparison outcomes spell the address of the answer. The sorted array *is* a perfectly balanced BST in disguise, with addresses computed by midpoint arithmetic — arithmetic addressing again (M-ARITH). *Where grammar adds nothing:* the algorithm is optimal among comparison-based searches (an adversary argument gives $\lceil \log_2(n+1) \rceil$), and no re-description changes that.

## Four comparison sorts {#sec:sorts}

**Problem.** Rearrange a sequence into non-decreasing order.

The four classical comparison sorts, in their SDK form:

| Algorithm | Comparisons (worst) | Comparisons (best) | Extra space | Stable | Reference |
|---|---|---|---|---|---|
| insertion sort | $n(n-1)/2$ | $n - 1$ (sorted input) | $\Oh(1)$ | yes | folklore |
| merge sort | $n \lceil \log_2 n \rceil$ | about $\tfrac12 n \log_2 n$ | $\Oh(n)$ | yes | \cite{clrs2022} |
| heapsort | $\Oh(n \log n)$ | $\Oh(n \log n)$ | $\Oh(1)$ | no | \cite{williams1964} |
| quicksort (random pivot) | $\Theta(n^2)$ | $\Oh(n \log n)$ expected | $\Oh(\log n)$ | no | \cite{hoare1962} |

::: algorithm {#alg:insertion title="Insertion sort"}
```text
for i ← 1 to n−1:                    invariant: a[0..i) is sorted
    x ← a[i]; j ← i − 1
    while j ≥ 0 and a[j] > x: a[j+1] ← a[j]; j ← j − 1
    a[j+1] ← x
```
:::

The invariant gives correctness at once. The comparison count is $n - 1$ plus the number of **inversions** (pairs $i < j$ with $a_i > a_j$), capped per element by its position — exactly $n - 1$ on sorted input and $n(n-1)/2$ on reversed input. The SDK counts confirm both exactly:

```python run
import random
from cgtsdk import Cost
from cgtsdk.algorithms import heapsort, insertion_sort, merge_sort, quicksort

n = 512
inputs = {"sorted": list(range(n)), "reversed": list(range(n, 0, -1)),
          "random": random.Random(1).sample(range(10**6), n)}
print(f"{'input':9s} {'insertion':>10s} {'merge':>7s} {'heap':>7s} {'quick':>7s}   n(n-1)/2={n*(n-1)//2}  n*log2(n)={n*9}")
for name, a in inputs.items():
    counts = []
    for f in (insertion_sort, merge_sort, heapsort, quicksort):
        c = Cost(); assert f(a, c) == sorted(a); counts.append(c.counts.get("compare", 0))
    print(f"{name:9s} {counts[0]:10d} {counts[1]:7d} {counts[2]:7d} {counts[3]:7d}")
```

```output
input      insertion   merge    heap   quick   n(n-1)/2=130816  n*log2(n)=4608
sorted           511    2304    7958    8642
reversed      130816    2304    7203    8217
random         69565    3970    7599    7796
```

(Quicksort here uses a three-way partition that charges up to two comparisons per element per partitioning step, which is why its counts sit above merge sort's.) Insertion sort is the best of the four on sorted input and by far the worst on reversed input; merge sort makes exactly $n \log_2 n / 2 = 2304$ comparisons when one half always wins, and fewer than $n \lceil \log_2 n \rceil = 4608$ in every case.

::: demo sorting
Text alternative: choose $n$, an input order and a seed; the widget sorts the same input with insertion sort, merge sort and heapsort, counting comparisons exactly as the SDK does, and compares them with $n(n-1)/2$ and $n \lceil \log_2 n \rceil$.
:::

## The comparison lower bound as a statement about grammar {#sec:lowerbound}

A comparison sort can learn about its input only by comparing elements. Its execution on all inputs of size $n$ is therefore described by a **decision tree**: a binary tree whose internal nodes are comparisons "$a_i < a_j$?" and whose leaves are output permutations. Each run follows one root-to-leaf path; the path's address — the word of comparison outcomes — determines the output.

::: theorem {#thm:sort-lb title="Comparison lower bound" status="standard"}
Every comparison-based sorting algorithm makes at least $\lceil \log_2 n! \rceil = n \log_2 n - \Oh(n)$ comparisons on some input of size $n$.
:::

::: proof
Distinct inputs that are permutations of $\{1, \dots, n\}$ require distinct outputs, so the decision tree has at least $n!$ leaves. A binary tree of height $h$ has at most $2^h$ leaves, so $h \ge \log_2 n!$, and $\log_2 n! = n \log_2 n - n \log_2 e + \Oh(\log n)$ by Stirling's formula.
:::

In the language of this book: the **grammar** available to a comparison sort is the binary alphabet of comparison outcomes, and the **information** it must produce is one of $n!$ answers. No grammar over a two-letter alphabet can address $n!$ answers with words shorter than $\log_2 n!$. This is the counting lemma that reappears in Chapter 12 as an information lower bound on *any* precomputed grammar (\ledger{CGT-THM-002}). Re-describing sorting grammatically cannot beat it — and claims to "sort in constant time with a grammar" should be read against it.

## Counting sort: escaping the bound by arithmetic addressing {#sec:counting}

The lower bound assumes that comparisons are the only way to learn about the input. If the keys are integers in a small range $[0, k)$, a key can be used as an **address**:

::: algorithm {#alg:counting title="Counting sort"}
```text
count[0..k] ← 0
for x in a: count[x+1] ← count[x+1] + 1          histogram, using x as an address
for i ← 0 to k−1: count[i+1] ← count[i+1] + count[i]   prefix sums: first slot of each key
for x in a (left to right): out[count[x]] ← x; count[x] ← count[x] + 1   stable placement
```
:::

::: proposition {#prop:counting status="standard"}
Counting sort sorts $n$ integers in $[0, k)$ stably with no comparisons, in $\Theta(n + k)$ time and space.
:::

This is mechanism M-ARITH in its purest form: the key's value *is* the location, exactly like an array index (Chapter 2). And it has exactly the array's limitation: the **density** $n / k$ must not be small. With $k = \Theta(n)$ it is linear; with 64-bit keys ($k = 2^{64}$) it is absurd. Radix sort refines the idea by addressing one digit at a time.

```python run
import random
from cgtsdk import Cost
from cgtsdk.algorithms import counting_sort, merge_sort

rng = random.Random(2)
for n, k in ((10_000, 100), (10_000, 10_000), (10_000, 1_000_000)):
    a = [rng.randrange(k) for _ in range(n)]
    c1, c2 = Cost(), Cost()
    assert counting_sort(a, k, c1) == merge_sort(a, c2) == sorted(a)
    print(f"n={n} k={k:9d}  counting sort: {c1.total:9d} steps, 0 comparisons   merge sort: {c2.total:7d} steps")
```

```output
n=10000 k=      100  counting sort:     50301 steps, 0 comparisons   merge sort:  253841 steps
n=10000 k=    10000  counting sort:     80001 steps, 0 comparisons   merge sort:  254082 steps
n=10000 k=  1000000  counting sort:   3050001 steps, 0 comparisons   merge sort:  254093 steps
```

At density $100$ keys per slot, counting sort is five times cheaper than merge sort in counted steps; at density $10^{-2}$ it is twelve times *more* expensive. The same algorithm wins or loses according to a single structural parameter — the density of the address space.

## Verdict {#sec:verdict}

For searching and sorting, the grammatical view gives *re-descriptions*: binary search as navigation in an implicit tree, a sorting algorithm as a grammar of comparison outcomes, counting sort as arithmetic addressing. It gives no speedup over the classical algorithms, and the comparison lower bound explains why none is possible within the comparison model. What it does give is a uniform vocabulary in which the one known way around the bound — using keys as addresses — is the same mechanism as array indexing and heap navigation, with the same failure condition.

::: exercise {#exr:9-1}
Prove that insertion sort makes exactly $(n - 1) + I - E$ comparisons, where $I$ is the number of inversions and $E$ is the number of elements that are smaller than every element before them (those for which the inner loop runs off the left end). Check the formula against the SDK on random inputs.
:::

::: exercise {#exr:9-2}
Give an input of size $8$ on which the SDK's quicksort with seed $0$ makes more comparisons than heapsort, or prove that none exists. (Use the SDK to search.)
:::

::: exercise {#exr:9-3}
Show that $\lceil \log_2 n! \rceil$ comparisons suffice to sort $n = 5$ elements (seven comparisons), or look up and verify a schedule that does.
:::

::: exercise {#exr:9-4}
Counting sort uses $\Theta(k)$ memory even when only a few distinct keys occur. Combine it with hashing (Chapter 4) to sort $n$ keys from a huge universe with $d$ distinct values in $\Oh(n + d \log d)$ time. Which mechanisms does your algorithm use?
:::

::: solution {of="exr:9-4"}
Count occurrences in a hash table keyed by value ($\Oh(n)$ expected, M-ARITH with collisions), sort the $d$ distinct keys by a comparison sort ($\Oh(d \log d)$), then emit each key its counted number of times ($\Oh(n)$). The bound is expected, under the hashing assumptions of Chapter 4.
:::

::: summary
- Binary search is navigation in an implicit balanced tree addressed by midpoint arithmetic; it is optimal among comparison searches.
- Insertion, merge, heap and quick sort are implemented with counted comparisons that match their analyses exactly where the analysis is exact.
- The $\log_2 n!$ lower bound is a counting statement: a binary grammar of comparison outcomes cannot address $n!$ answers with shorter words.
- Counting sort escapes it by using keys as addresses — arithmetic addressing — and is only as good as the density of the key range.
- For searching and sorting the grammatical view yields equivalence, not improvement; that is a finding, not a failure.
:::
