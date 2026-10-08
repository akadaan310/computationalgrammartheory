---
title: Cost Profiles, Preprocessing, and Information
status: mixed
statusnote: The information lower bound and break-even analysis are elementary results proved here; the experiments are reproducible measurements.
description: When does precomputing pay? What is the least information a "grammar of all answers" must contain? And what happens when the structure changes?
---

::: objectives
- Account for the total cost of a workload: build, queries, updates and output, in a single formula.
- Compute break-even query volumes, including under invalidating updates.
- Prove that any representation answering reachability on all digraphs without consulting the graph needs at least $\lfloor n/2 \rfloor \lceil n/2 \rceil$ bits.
- Distinguish retrieving an answer from discovering it, and both from producing a witness.
- Read the experimental evidence that no strategy dominates under updates.
:::

## Total cost {#sec:total}

A resolution scheme (\ref{def:costprofile}) has a cost profile $(T_{\mathrm{build}}, S, T_{\mathrm{query}}, T_{\mathrm{update}}, |\mathrm{out}|)$. For a workload of $Q$ queries and $U$ updates the cost that matters is

$$T_{\mathrm{total}} = T_{\mathrm{build}} + \sum_{i=1}^{Q} T_{\mathrm{query},i} + \sum_{j=1}^{U} T_{\mathrm{update},j}, \label{eq:total}$$

plus the cost of writing the outputs, and subject to the space $S$ fitting in memory. Every "fast query" claim must be read against \eqref{eq:total}. A query answered in $\Oh(1)$ after $\Theta(n^2)$ preprocessing is a statement about the second term only.

::: proposition {#prop:breakeven title="Break-even under invalidating updates" status="proved-here" ledger="CGT-PROP-005"}
Suppose updates invalidate a precomputed index, splitting the query stream into epochs with $Q_1, \dots, Q_k$ queries, and the index is rebuilt (cost $B$) at the first query of each non-empty epoch. Against a baseline without preprocessing (query cost $q_0$) and with indexed query cost $q_1 < q_0$, the index is cheaper iff

$$B \cdot \big|\{j : Q_j > 0\}\big| \;<\; (q_0 - q_1) \sum_j Q_j ;$$

a sufficient condition is $Q_j > Q^* = B / (q_0 - q_1)$ for every non-empty epoch.
:::

::: proof
Sum the costs epoch by epoch: the index pays $B + Q_j q_1$ in each non-empty epoch and the baseline $Q_j q_0$.
:::

The formula is trivial; its consequences are not. In the experiments on random graphs with $n = 4096$ (\ledger{CGT-OBS-004}), the break-even query volume for a precomputed transitive closure against breadth-first search ranged from about $4$ queries on dense graphs (where a giant strongly connected component lets the closure share rows) to about $27{,}000$ on sparse ones (where random queries are mostly negative and search stops early). The same index is an obvious win or an obvious loss depending on a structural property of the input and on the query distribution.

```python run
from cgtsdk import Cost, break_even
from cgtsdk.algorithms import bfs, transitive_closure
from cgtsdk.lab import random_digraph
import random

rng = random.Random(1)
for deg in (0.8, 3.0):
    adj = random_digraph(1024, deg, seed=2)
    build = Cost(); rows = transitive_closure(adj, build)
    q0 = Cost()
    for _ in range(300):
        bfs(adj, rng.randrange(1024), q0)   # search without an index (full BFS from a random source)
    q1 = 1                                   # one bit test per indexed query
    Qstar = break_even(build.total, q1, q0.total / 300)
    print(f"avg out-degree {deg}: closure build {build.total} steps, BFS {q0.total/300:.1f} steps/query -> break-even after {Qstar:.0f} queries")
```

```output
avg out-degree 0.8: closure build 14742 steps, BFS 10.0 steps/query -> break-even after 1637 queries
avg out-degree 3.0: closure build 8208 steps, BFS 4565.1 steps/query -> break-even after 2 queries
```

(Here each BFS runs to completion rather than stopping at the target, so the dense case is even more favourable to the index than in the ledger's experiment.)

::: demo break-even
Text alternative: enter a build cost, per-query costs with and without the index, and the number of queries between invalidating updates; the widget computes $Q^* = B/(q_0 - q_1)$ and says whether the index pays within an epoch. Its defaults are the counted values of the ledger's dynamic-workload experiment.
:::

## The information a grammar must contain {#sec:info}

The strongest form of the founding conjecture would be a small "grammar" from which every reachability question about a graph can be *read off*, without searching the graph. Information theory forbids it.

::: lemma {#lem:counting title="Counting lemma" status="proved-here" ledger="CGT-THM-002"}
Let a scheme map each structure $\Str$ in a class $\mathcal{K}$ to a bit string $E(\Str)$ from which every query of a family $\mathcal{Q}$ can be answered without access to $\Str$. If the structures of $\mathcal{K}$ induce $N$ distinct answer functions, then some encoding has length at least $\lceil \log_2(N+1) \rceil - 1$, and fewer than $N \cdot 2^{-c}$ answer functions have encodings shorter than $\log_2 N - c$ bits.
:::

::: proof
Structures with different answer functions need different encodings. There are $2^{L+1} - 1$ strings of length at most $L$, so $2^{L+1} - 1 \ge N$; and there are fewer than $2^{\log_2 N - c} = N 2^{-c}$ strings shorter than $\log_2 N - c$.
:::

::: theorem {#thm:info title="Information lower bound for retrieval-only reachability" status="proved-here" ledger="CGT-THM-002"}
Any scheme that answers all reachability queries "does $s$ reach $t$?" on all digraphs with vertex set $[n]$, without consulting the graph, uses at least $\lfloor n/2 \rfloor \lceil n/2 \rceil$ bits on some digraph; and on all but a fraction smaller than $2^{-c}$ of the bipartite graphs below it uses at least $\lfloor n/2 \rfloor \lceil n/2 \rceil - c$ bits.
:::

::: proof
Split $[n]$ into $X$ of size $a = \lfloor n/2 \rfloor$ and $Y$ of size $b = \lceil n/2 \rceil$. For each $S \subseteq X \times Y$ let $G_S$ have edge set $S$. Every path in $G_S$ has length at most one, so $s$ reaches $t \neq s$ iff $(s, t) \in S$. The $2^{ab}$ graphs have pairwise different answer functions; apply \ref{lem:counting} with $N = 2^{ab}$.
:::

::: corollary {#cor:closure-optimal status="proved-here"}
No grammar, index or labeling of $o(n^2)$ bits answers reachability on all digraphs without reading the graph; the transitive closure ($n^2$ bits) is optimal for this task up to a factor of $4$. Sub-quadratic schemes must either restrict the class of graphs or read the graph at query time — that is, search.
:::

The asymptotic version for acyclic graphs follows from the enumeration of partial orders by Kleitman and Rothschild \cite{kleitman1975} ($\log_2$ of their number is $\sim n^2/4$); the bipartite family above gives the exact, non-asymptotic bound in one line. The result is elementary and almost certainly folklore. Its role here is to rule out precisely the reading of the founding conjecture that says a sufficiently expressive grammar could make reachability a constant-time lookup *in general*. The experiments agree: a general-purpose compressor could not shrink bipartite-family closures below $n^2/4$ bits (281,960 bits against the bound 262,144 at $n = 1024$, \ledger{CGT-OBS-005}).

### Restricted classes can be cheap {#sec:forest-labels}

The lower bound applies to *all* digraphs. Restricted classes have less information, and for them the grammar of the class can be the optimal index.

::: proposition {#prop:forest-labels status="proved-here" ledger="CGT-THM-002"}
For rooted forests on $[n]$, assigning each vertex its DFS entry and exit times $(\mathrm{in}(v), \mathrm{out}(v))$ answers "$u$ is an ancestor of $v$" by $\mathrm{in}(u) \le \mathrm{in}(v) \wedge \mathrm{out}(v) \le \mathrm{out}(u)$, in $\Oh(1)$, with $\Oh(n \log n)$ bits after $\Oh(n)$ preprocessing \cite{agrawal1989}. This is optimal up to a constant factor: there are $(n+1)^{n-1}$ labelled rooted forests, each with a distinct ancestor relation.
:::

::: proof
The nesting property of DFS intervals gives correctness. Cayley's formula counts rooted forests on $[n]$ as trees on $n + 1$ vertices. The ancestor relation determines each vertex's parent as its deepest proper ancestor, so distinct forests have distinct answer functions; the counting lemma gives $\log_2 (n+1)^{n-1} = \Theta(n \log n)$ bits.
:::

This is mechanism M-RESTRICT in its clearest form: the nesting structure that *defines* forests is itself a compact index, and the advantage comes from the restriction of the class, not from having a grammar. 2-hop labelings extend the idea to graphs whose reachability has small covers \cite{cohen2003}.

## Retrieval, discovery, witnesses {#sec:retrieval}

Three different things are often all called "answering a query":

1. **Retrieval:** reading an answer that was computed earlier (one bit of a closure).
2. **Discovery:** computing the answer from the structure (a search).
3. **Witness production:** exhibiting *why* — the actual path, of length $\ell$.

Retrieval can be $\Oh(1)$; discovery cannot be cheaper than reading enough of the structure to decide; witness production costs at least the output size. A closure answers "is there a path?" by retrieval but still needs search-like work to produce the path: walking from $s$ along successors that still reach $t$ costs the sum of their out-degrees (\ledger{CGT-NEG-011}). Storing next-hop pointers for all pairs makes witness production output-linear, at $\Theta(n^2 \log n)$ bits — whether that is optimal is an open question (\ledger{CGT-OPEN-009}).

## When the structure changes {#sec:cost-dynamic}

Precomputation assumes the structure holds still. The ledger's dynamic-workload experiment (\ledger{CGT-EXP-005}) ran nine streams of 4,000 operations on a digraph with $n = 1024$, comparing BFS per query, a lazily rebuilt closure, an incrementally maintained closure (insertions handled by OR-ing rows, deletions forcing a rebuild \cite{italiano1986}), and memoized BFS. Four different strategies won:

| Workload | BFS | lazy rebuild | incremental | memoized BFS | cheapest |
|---|---|---|---|---|---|
| queries only, uniform | 62,223 | 21,641 | 21,641 | 66,121 | rebuild / incremental |
| queries only, repetitive | 30,216 | 21,641 | 21,641 | 4,077 | memo |
| 90% queries, 10% insertions, uniform | 242,024 | 6,775,863 | 602,748 | 245,653 | BFS |
| 90% queries, 10% insertions, adversarial | 1,780,567 | 7,546,028 | 661,186 | 1,770,413 | incremental |
| 50% queries, mixed updates, uniform | 26,624 | 17,535,647 | 12,550,168 | 28,608 | BFS |

(Counted steps; full table in the ledger.) With 10% insertions, epochs contain about ten queries while $Q^* \approx 1{,}400$, so the lazily rebuilt index costs 28 times as much as plain search — the break-even proposition at work. No strategy dominates; the winner is decided by the query–update ratio, the share of deletions, and the repetitiveness of queries (\ledger{CGT-OBS-009}).

Sharing suffers from updates in the same way: $k$ adversarial relabellings inflate a minimal DAG of a full binary tree to $\Theta(k \log n)$ nodes (Chapter 5, \ledger{CGT-THM-005}).

## An accounting of the mechanisms {#sec:accounting}

| Mechanism | What it reduces | What it costs | What defeats it |
|---|---|---|---|
| M-ARITH | query time, space for addresses | requires dense numerations | sparse or deep shapes (Ch. 5); non-uniform shapes (Ch. 13) |
| M-PRE | query time | build time, space $\ge$ information content | updates; the counting lemma |
| M-SHARE | space | navigation overhead | updates; repetition of the wrong kind |
| M-RESTRICT | everything, on the class | applicability | inputs outside the class |
| M-PRUNE | search space | up to a factor $\lvert Q \rvert$ more work | permissive languages (Ch. 8) |

::: exercise {#exr:12-1}
Derive a version of \ref{prop:breakeven} for an index that supports *incremental* updates at cost $u$ each instead of rebuilds. When is incremental maintenance better than lazy rebuilding?
:::

::: solution {of="exr:12-1"}
With $U$ updates, incremental maintenance costs $B + Uu + Qq_1$; lazy rebuilding costs $B \cdot (\text{number of non-empty epochs}) + Q q_1$. Incremental wins when $Uu < B \cdot (\#\text{non-empty epochs} - 1)$ — roughly when an update costs less than a rebuild times the fraction of updates followed by a query. Deletions that force rebuilds make $u$ effectively $B$.
:::

::: exercise {#exr:12-2}
Use the counting lemma to give a lower bound on the space of any scheme answering "is $u$ adjacent to $v$?" on all undirected graphs with $n$ vertices without consulting the graph. Compare it with the adjacency matrix.
:::

::: exercise {#exr:12-3}
The counting lemma says nothing about schemes that read the graph at query time. Give a scheme with $\Oh(n)$ extra bits that answers reachability on DAGs faster than BFS for some queries, and say which mechanism it uses.
:::

::: summary
- Total cost $= T_{\mathrm{build}} + \sum T_{\mathrm{query}} + \sum T_{\mathrm{update}}$ plus output; an index pays only after $Q^* = B/(q_0 - q_1)$ queries per epoch (\ledger{CGT-PROP-005}).
- Retrieval-only reachability on all digraphs needs $\lfloor n/2\rfloor\lceil n/2\rceil$ bits (\ledger{CGT-THM-002}); no grammar evades the counting lemma. Restricted classes such as forests have compact optimal indexes.
- Retrieval, discovery and witness production are different costs.
- Under updates no strategy dominates; the measured winners vary with the workload.
- Each mechanism has a cost and a class of inputs that defeats it.
:::
