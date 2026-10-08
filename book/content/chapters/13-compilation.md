---
title: "Compiling Operations: When Grammar Becomes Arithmetic"
status: proved-here
statusnote: The main new result of the current edition — a constant-size normal form for move words in heap-shaped trees, with a matching impossibility result for arbitrary shapes. Novelty not yet verified against the literature.
description: A move word of any length can be compiled into a constant-size operation on some structures and provably not on others. This chapter finds the line.
---

::: objectives
- Define arithmetically compilable structures and explain what compilation buys: one-time cost proportional to the word, then constant cost per application.
- Prove that every move word over $\{L, R, U\}$ in a heap-shaped binary tree compiles to a map $x \mapsto ((x \gg k) \ll j) \mid c$ defined exactly on an interval.
- Prove that no constant-size compiled form exists for arbitrary tree shapes, by a counting argument.
- Recognize compilable structures beyond trees: de Bruijn graphs, hypercubes, grids.
- Read the experimental evidence, including the workload under which compilation barely helps.
:::

## The idea {#sec:idea}

Chapter 3 made an observation about lists: a navigation word such as $\mathit{next}^{3}\mathit{prev}^{5}\mathit{next}^{4}$ is determined by three numbers — its net displacement and its minimum and maximum prefix displacements — however long it is. If a representation could jump by a computed displacement, a word of a million moves could be *compiled* once into those three numbers and then applied in constant time. A linked list cannot jump; an array can.

This is the founding question of the book in its sharpest form. A move word is a sentence of the structure's operational grammar. Can the *sentence itself* be turned into machinery — a single cheap operation equivalent to the whole sentence — and on which structures?

::: definition {#def:compilable title="Arithmetically compilable structure" ledger="CGT-DEF-011"}
A deterministic operational grammar is **arithmetically compilable** on a class $\mathcal{K}$ of structures if there are a numeration $\nu$ of elements and a class $\mathcal{F}$ of partial maps on numerals such that

1. every move acts on numerals as some $f \in \mathcal{F}$;
2. $\mathcal{F}$ is closed under composition, including conjunction of domains;
3. every $f \in \mathcal{F}$ is stored in $\Oh(1)$ words, and composing, applying and testing the domain of members of $\mathcal{F}$ cost $\Oh(1)$ word operations.

Then every move word $w$ **compiles** in $\Oh(|w|)$ word operations into one element of $\mathcal{F}$, which is applied afterwards in $\Oh(1)$, independently of $|w|$.
:::

The definition is a cost-oriented specialization of an old idea: the meanings of all words form the **transition monoid** of the structure (\ledger{CGT-DEF-007}), and compilation asks for a representation of that monoid with constant-size elements and constant-time operations. Automatic structures \cite{blumensath2000,khoussainov1995} and automatic groups \cite{epstein1992} ask a related question — whether elements and moves are recognized by finite automata — but not this one: there, applying a move to a word-encoded element costs time linear in the element's encoding.

## The heap-shaped tree {#sec:heapword}

Let $T_n$ be the binary tree whose nodes are exactly the numerals $1, \dots, n$ (the shape of a binary heap with $n$ elements), with moves

$$L : x \mapsto 2x, \qquad R : x \mapsto 2x + 1, \qquad U : x \mapsto \lfloor x/2 \rfloor .$$

A word $w \in \{L, R, U\}^*$ is **defined at** $x$ if every numeral visited after each step lies in $[1, n]$. Evaluating $w$ step by step costs $\Theta(|w|)$ (or less, when it falls off the tree early).

::: theorem {#thm:heapword title="Word compilation in heap-shaped trees" status="proved-here" ledger="CGT-THM-006"}
For every word $w \in \{L, R, U\}^*$ and every $n \ge 1$ there are integers $k, j \ge 0$, $0 \le c < 2^j$ and $lo, hi$, computable from $(w, n)$ with $\Oh(|w|)$ arithmetic operations, such that for every $x \in [1, n]$:

$$\sem{w}(x) \text{ is defined} \iff lo \le x \le hi, \qquad \text{and then}\qquad \sem{w}(x) = \Big\lfloor \frac{x}{2^k} \Big\rfloor \cdot 2^j + c . \label{eq:normalform}$$

With early termination (stop as soon as the domain is empty), all intermediate integers have $\Oh(\log n)$ bits; for $n < 2^{\mathrm{w}}$ compilation costs $\Oh(|w|)$ word operations and each application costs $\Oh(1)$.
:::

::: proof
*Normal form of prefixes.* We show by induction on $i$ that the map $p_i$ computed by the first $i$ letters (ignoring definedness) is $p_i(x) = \lfloor x / 2^{k_i} \rfloor \cdot 2^{j_i} + c_i$ with $0 \le c_i < 2^{j_i}$. The empty word gives $(0, 0, 0)$. Appending $L$ or $R$ gives $(k, j+1, 2c + b)$ with $b \in \{0, 1\}$. Appending $U$ when $j > 0$ gives $(k, j-1, \lfloor c/2 \rfloor)$, because $\lfloor (2y + b)/2 \rfloor = y$: an up-move cancels the last down-move. Appending $U$ when $j = 0$ gives $(k+1, 0, 0)$.

*Monotonicity.* Each $p_i$ is non-decreasing in $x$, as a composition of non-decreasing maps.

*Domain, lower end.* $w$ is defined at $x$ iff $1 \le p_i(x) \le n$ for every prefix $i \ge 1$. A prefix value can drop below $1$ only at an up-move taken with $j = 0$, which requires $\lfloor x / 2^{k} \rfloor \ge 1$, i.e. $x \ge 2^k$ for the new $k$. Since $k$ never decreases, these conditions together say $x \ge 2^{k_{\max}} =: lo$ (and $lo \ge 1$).

*Domain, upper end.* If $c_i > n$, the prefix value exceeds $n$ for every $x$ and the domain is empty. Otherwise, because $c_i < 2^{j_i}$, $p_i(x) \le n$ iff $\lfloor x/2^{k_i} \rfloor \le \lfloor (n - c_i)/2^{j_i} \rfloor$, i.e.

$$x \le T_i := \Big(\Big\lfloor \frac{n - c_i}{2^{j_i}} \Big\rfloor + 1\Big)\, 2^{k_i} - 1 .$$

Take $hi = \min(n, \min_i T_i)$. Each $T_i$ is a threshold because $p_i$ is non-decreasing; the conjunction of all lower and upper conditions is therefore the interval $[lo, hi]$.

*Cost.* Each letter updates $(k, j, c, lo, hi)$ with a constant number of operations. Once $j > \lfloor \log_2 n \rfloor$ or $c > n$ the domain is empty and compilation may stop; until then all quantities have $\Oh(\log n)$ bits, and $k \le |w|$ with $2^k$ needed only while $2^k \le n$.
:::

The proof is short, but the statement was checked mechanically as well: for all words of length at most $7$, all $n \le 40$ and all $x$, the compiled map agrees with step-by-step evaluation — more than two million cases — and for $300$ random long words on trees with up to $5{,}000$ nodes (`sdk/tests/test_addressing.py`). The browser laboratory's implementation is checked against the SDK's.

```python run
import random
from cgtsdk import Cost
from cgtsdk.addressing import HeapWord, heap_walk

n = 10**6
rng = random.Random(1)
x, w = 6000, []
for _ in range(2000):                      # a 2000-letter walk that stays inside the tree
    opts = [(a, y) for a, y in (("L", 2*x), ("R", 2*x + 1), ("U", x // 2)) if 1 <= y <= n]
    a, x = rng.choice(opts); w.append(a)
compile_cost = Cost()
f = HeapWord.compile(w, n, compile_cost)
print(f"|w| = {len(w)}  ->  f(x) = ((x >> {f.k}) << {f.j}) | {f.c},  defined on [{f.lo}, {f.hi}]")
apply_cost, walk_cost = Cost(), Cost()
starts = [rng.randrange(4096, 8192) for _ in range(1000)]
assert all(f(s, apply_cost) == heap_walk(w, s, n, walk_cost) for s in starts)
print(f"compile once: {compile_cost.total} ops;  per application: compiled {apply_cost.total/1000:.0f}, step-by-step {walk_cost.total/1000:.0f}")
```

```output
|w| = 2000  ->  f(x) = ((x >> 3) << 9) | 486,  defined on [8, 7807]
compile once: 8000 ops;  per application: compiled 5, step-by-step 3640
```

A word of two thousand moves collapses to "shift right by $3$, shift left by $9$, set the low nine bits to $486$", defined on the interval $[8, 7807]$. After a one-time cost of $8{,}000$ operations, each application costs $5$ instead of about $3{,}600$.

::: demo compiled-words
Text alternative: type a word over L, R, U and a tree size; the widget compiles it with the algorithm of the proof, shows $(k, j, c, lo, hi)$, and lists the compiled result next to step-by-step evaluation for the first forty start nodes. They always agree; the widget would flag any disagreement.
:::

## The lower bound: arbitrary shapes {#sec:compile-lb}

Why does the heap-shaped tree compile and a linked list or an arbitrary tree not? Because in $T_n$ the semantics of every move is determined by a *single number*, $n$. In an arbitrary tree, even the domain of a single move carries a lot of information.

::: theorem {#thm:no-compile title="No constant-size compilation on arbitrary shapes" status="proved-here" ledger="CGT-THM-007"}
Let a scheme encode each binary tree $T$ with $n$ nodes (nodes named by their addresses) as a bit string $E(T)$ from which it can be decided, for every node, whether the move $L$ is defined there, without access to $T$. Then some tree needs $|E(T)| \ge \lfloor n/2 \rfloor$ bits.
:::

::: proof
Consider caterpillars: a right spine $1^0, 1^1, \dots, 1^{s-1}$ with left leaves attached at the spine positions in a set $S \subseteq \{0, \dots, \lfloor n/2 \rfloor - 1\}$, and $s = n - |S| \ge \lceil n/2 \rceil$ so that every position of $S$ is on the spine. Then $\dom \sem{L} = \{1^i : i \in S\}$. The $2^{\lfloor n/2 \rfloor}$ caterpillars have pairwise different answer functions, and the counting lemma (\ref{lem:counting}) applies.
:::

So for arbitrary shapes the best possible "compiled" form of a word is essentially a table of its values at all $n$ nodes, built by simulating the word from every node at cost $\Theta(n |w|)$. The theorem was also checked by enumerating all binary trees with up to $11$ nodes (`experiments/check_theorems.py`).

Together the two theorems locate the boundary of mechanism M-ARITH for trees precisely: **compilation to constant size is possible exactly when the move semantics is fixed by a constant number of parameters of the structure, and impossible when the shape itself carries the information.** The general form of this statement — a characterization of compilable classes — is open (\ledger{CGT-OPEN-012}).

## More compilable structures {#sec:more}

The pattern is not special to trees. Three further structures compile with density $1$, each with a different algebra:

::: proposition {#prop:compilable title="De Bruijn graphs, hypercubes and grids are compilable" status="proved-here" ledger="CGT-PROP-008"}
1. **De Bruijn graph** $B(k, m)$: vertices are base-$k$ numerals of $m$ digits; the move "shift in digit $a$" is $x \mapsto (kx + a) \bmod k^m$. Affine maps modulo $N$ are closed under composition: $(a_2, b_2) \circ (a_1, b_1) = (a_2 a_1,\, a_2 b_1 + b_2) \bmod N$.
2. **Hypercube** $Q_d$: the move "flip bit $i$" is $x \mapsto x \oplus 2^i$; compositions are XORs with the XOR of the masks.
3. **Grid** $\prod_i [0, d_i)$ with moves $\pm e_i$ defined inside the box: a word compiles to a translation $t$ together with the per-axis minimum and maximum prefix displacements $(lo, hi)$; it is defined at $x$ iff $x_i + lo_i \ge 0$ and $x_i + hi_i < d_i$ for all $i$; composition adds translations and takes the minimum and maximum of shifted prefixes.
:::

::: proof
Each item is a direct calculation of the closure property, as stated; the grid case is the multi-dimensional version of the cursor observation of Chapter 3. Each is checked exhaustively on small instances in the SDK's tests.
:::

```python run
from cgtsdk import Cost
from cgtsdk.addressing import (AffineMod, BoxTranslation, XorMask, compile_word,
                               debruijn_moves, grid_moves, hypercube_moves)
import random

rng = random.Random(3)
cases = [("de Bruijn B(2,20)", debruijn_moves(2, 20), AffineMod.identity(2**20)),
         ("hypercube Q_20", hypercube_moves(20), XorMask(0)),
         ("grid 1000 x 1000", grid_moves((1000, 1000)), BoxTranslation.identity((1000, 1000)))]
for name, moves, ident in cases:
    w = [rng.choice(sorted(moves)) for _ in range(10_000)]
    c = Cost(); f = compile_word(moves, w, ident, c)
    print(f"{name:18s} 10,000-move word compiled in {c.total} ops into {f}")
```

```output
de Bruijn B(2,20)  10,000-move word compiled in 10000 ops into AffineMod(a=0, b=782888, N=1048576)
hypercube Q_20     10,000-move word compiled in 10000 ops into XorMask(c=537303)
grid 1000 x 1000   10,000-move word compiled in 10000 ops into BoxTranslation(dims=(1000, 1000), t=(32, -78), lo=(-51, -81), hi=(39, 35))
```

The de Bruijn word compiled to a *constant* map ($a = 0$): after more than $20$ shifts the starting vertex is entirely forgotten, which the affine form exposes immediately. The grid word compiled to "move by $(32, -78)$", defined for start points with coordinates at least $(51, 81)$ and below $(1000 - 39,\, 1000 - 35)$.

## What the experiments show {#sec:experiment}

The ledger's experiment (\ledger{CGT-EXP-008}) measured compilation against step-by-step evaluation under two workloads, a lesson learned from earlier experiments (\ledger{CGT-D-017}).

| Workload on $T_{10^6}$ | $\lvert w \rvert$ | compiled ops / application | step-by-step ops / application | applications to break even |
|---|---|---|---|---|
| words generated as walks (≈90% of starts defined) | 8 | 5 | 16 | 2.9 |
| | 512 | 5 | 933 | 2.2 |
| | 4096 | 5 | 7,420 | 2.2 |
| random words (most starts fall off early) | 512 | 5 | 29 | 86 |
| | 4096 | 5 | 130 | 131 |

When words stay inside the tree, compilation pays after about two applications. When random words fall off the tree within a few steps, step-by-step evaluation stops early and compilation needs over a hundred applications to pay. On random pointer trees with $n = 20{,}000$, the same kind of walk-generated word was defined at only $0.1\%$ of nodes for $|w| = 512$ — the non-uniformity that \ref{thm:no-compile} lower-bounds (\ledger{CGT-OBS-014}).

::: boundary
Compilation is a statement about *repeated application of the same word*. It does not make a single evaluation cheaper (compiling costs as much as evaluating), and it applies only to structures whose move semantics is uniform. Its novelty as a normal form has not been verified against the literature on implicit tree navigation and on transition monoids; it is presented as proved here, not as new.
:::

::: exercise {#exr:13-1}
Compile $w = L\,R\,R\,U\,U\,L$ for $n = 100$ by hand, following the proof of \ref{thm:heapword}. Check your $(k, j, c, lo, hi)$ with the SDK or the laboratory.
:::

::: solution {of="exr:13-1"}
Prefixes: $L$: $(0,1,0)$; $LR$: $(0,2,1)$; $LRR$: $(0,3,3)$; $LRRU$: $(0,2,1)$; $LRRUU$: $(0,1,0)$; $LRRUUL$: $(0,2,0)$. No up-move with $j = 0$, so $lo = 1$. Thresholds $T_i = \lfloor (100 - c_i)/2^{j_i} \rfloor$ (with $k_i = 0$): $50, 24, 12, 24, 50, 25$; $hi = 12$. So $f(x) = 4x$ on $[1, 12]$: the walk visits $8x + 3 \le 100$, which forces $x \le 12$.
:::

::: exercise {#exr:13-2}
Generalize \ref{thm:heapword} to heap-shaped $k$-ary trees with moves "child $i$" and "parent". What replaces shifts?
:::

::: exercise {#exr:13-3}
Show that the grid compiled form of \ref{prop:compilable} is closed under composition by proving the composition formula, and give the compiled form of the reverse of a word in terms of the word's compiled form.
:::

::: exercise {#exr:13-4}
Prove that the moves $\mathit{next}$ and $\mathit{prev}$ on a *circular* doubly linked list of known length $n$ compile into translations modulo $n$ — and explain why this does not make a linked list as fast as an array.
:::

::: solution {of="exr:13-4"}
Each move is $x \mapsto x \pm 1 \bmod n$ on positions, so words compile to $x \mapsto x + t \bmod n$, defined everywhere. But *applying* the compiled form requires reaching position $x + t$, and a linked list offers no way to jump by a computed offset: the compiled *meaning* is constant-size, while its *execution* still walks $\min(t, n - t)$ pointers. Compilation helps only when the representation supports arithmetic addressing.
:::

::: summary
- A structure is arithmetically compilable when its moves act on numerals through a composition-closed class of constant-size maps; then any word compiles once and applies in constant time.
- In heap-shaped trees every word over $\{L, R, U\}$ compiles to $x \mapsto ((x \gg k) \ll j) \mid c$ on an interval domain (\ledger{CGT-THM-006}).
- For arbitrary shapes no constant-size compiled form exists: one move's domain can carry $\lfloor n/2 \rfloor$ bits (\ledger{CGT-THM-007}).
- De Bruijn graphs, hypercubes and grids compile too, via affine maps, XOR masks and bounded translations (\ledger{CGT-PROP-008}).
- Measured: compilation pays after about two applications when words stay defined, and after over a hundred when early exits make step-by-step evaluation cheap.
:::
