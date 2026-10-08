---
title: Graph Algorithms Reconstructed
status: mixed
statusnote: Classical algorithms with cited sources; the exact work count of the right-linear path grammar is proved here.
description: Traversal, ordering, components, shortest paths, spanning trees and closure — and the theorem that evaluating a path grammar is computing a closure, with cost depending on the grammar's shape.
---

::: objectives
- Implement and justify BFS, DFS, topological sorting, strongly connected components, Dijkstra, Bellman–Ford, Kruskal, Prim, union–find and Floyd–Warshall, with counted costs.
- Read each algorithm as the evaluation of a path grammar in a particular algebra.
- Prove the exact rule-application count of semi-naive evaluation of the right-linear path grammar, and compare it with the doubling grammar.
- Explain why two grammars with the same meaning can have asymptotically different costs, trading total work against parallel depth.
:::

## Traversal, order and components {#sec:traversal}

**Breadth-first search** from $s$ visits vertices in order of hop distance and computes $\mathrm{dist}(s, \cdot)$ in $\Theta(n + m)$; **depth-first search** visits each vertex and edge once and classifies edges by discovery and finishing times. Both are textbook algorithms \cite{clrs2022}. Three classical consequences:

- **Topological sorting.** A DAG's vertices can be ordered so that every edge goes forward; Kahn's algorithm repeatedly removes a vertex of in-degree zero, in $\Theta(n + m)$, and reports a cycle if it gets stuck \cite{kahn1962}.
- **Strongly connected components.** Tarjan's algorithm \cite{tarjan1972} finds them in one DFS using low-link values, and numbers them in reverse topological order of the condensation (the SDK's `tarjan_scc` returns that numbering, so component $0$ is a sink).
- **Reachability and closure.** The reflexive–transitive closure — the semantics $\sem{E^*}$ of Chapter 6 — can be computed by condensing SCCs and OR-ing bitset rows in reverse topological order: each OR of $n$-bit rows costs $\lceil n / w \rceil$ word operations.

```python run
from cgtsdk import Cost
from cgtsdk.algorithms import bfs, tarjan_scc, topological_sort, transitive_closure
from cgtsdk.lab import random_digraph

for name, adj in (("random DAG", random_digraph(2000, 2.0, seed=1, dag=True)),
                  ("random digraph", random_digraph(2000, 2.0, seed=1))):
    c1, c2, c3 = Cost(), Cost(), Cost()
    d = bfs(adj, 0, c1)
    comp, k = tarjan_scc(adj, c2)
    order = topological_sort(adj)
    rows = transitive_closure(adj, c3)
    pairs = sum(bin(r).count("1") for r in rows)
    print(f"{name:15s} m={sum(map(len, adj))}  BFS edges={c1.counts['edge']}  SCCs={k}  "
          f"topological order: {'yes' if order else 'no (cycle)'}  closure pairs={pairs}  closure cost={c3.total}")
```

```output
random DAG      m=4000  BFS edges=20  SCCs=2000  topological order: yes  closure pairs=26226  closure cost=136000
random digraph  m=4000  BFS edges=3240  SCCs=718  topological order: no (cycle)  closure pairs=2575275  closure cost=39584
```

On the random digraph a giant strongly connected component absorbs 1,283 of the 2,000 vertices; condensing it shares one closure row among all its members, which is why the closure of a graph with *more* reachable pairs costs *fewer* steps. This is the sharing mechanism (M-SHARE) at work inside a classical algorithm.

## Shortest paths and spanning trees {#sec:sssp}

| Algorithm | Problem | Requirement | Cost | Source |
|---|---|---|---|---|
| Dijkstra | single-source shortest paths | weights $\ge 0$ | $\Oh((n + m) \log n)$ with a binary heap | \cite{dijkstra1959} |
| Bellman–Ford | single-source shortest paths, negative-cycle detection | none | $\Oh(nm)$ | \cite{bellman1958,ford1956} |
| Floyd–Warshall | all-pairs shortest paths | no negative cycles | $\Theta(n^3)$ | \cite{clrs2022} |
| Kruskal | minimum spanning forest | undirected | $\Oh(m \log m)$ with union–find | \cite{kruskal1956,tarjan1975} |
| Prim | minimum spanning forest | undirected | $\Oh(m \log n)$ with a binary heap | \cite{prim1957} |

All are implemented in `cgtsdk.algorithms` and tested against one another and against brute force: Dijkstra and Bellman–Ford against Floyd–Warshall on random weighted digraphs, Kruskal against Prim and against exhaustive search over edge subsets on small graphs.

In the path-algebra view of Chapter 6 all three shortest-path algorithms evaluate the *same* path grammar $E E^*$ in the tropical semiring $(\min, +)$; they differ in evaluation *strategy*. Dijkstra exploits a property of the algebra on non-negative weights — once a vertex is settled its distance never improves — to evaluate each vertex once in increasing order of distance. Bellman–Ford makes no such assumption and relaxes every edge up to $n - 1$ times. Floyd–Warshall is Kleene's algorithm for the closure of a matrix: it allows intermediate vertices $0, 1, \dots, k$ in turn. The grammar is common; the costs come from the semantics' algebraic properties and the evaluation order. A grammatical description, by itself, does not choose the order.

## Evaluating a path grammar {#sec:path-grammar}

We now make that last sentence precise. The closure $P^+ = \sem{E E^*}$ (paths of length at least one) is the least relation $P$ satisfying either of two grammars:

$$\text{right-linear:}\quad P \to E \mid E\,P \qquad\qquad \text{doubling:}\quad P \to E \mid P\,P . \label{eq:two-grammars}$$

Both have the same meaning (Chapter 6). Evaluate each **bottom-up**: start from the facts $E(u,v)$, and repeatedly apply the productions to newly derived facts until nothing new appears (*semi-naive evaluation*, standard in Datalog).

::: theorem {#thm:grammar-shape title="Same meaning, different grammar, different cost" status="proved-here" ledger="CGT-THM-004"}
Let $G$ have $n$ vertices and $m$ edges, and let $\ell$ be the largest length of a shortest positive-length path between a pair in $P^+$ (pairs $(u, u)$ on cycles included).

1. Semi-naive evaluation of the right-linear grammar makes exactly $m + \sum_{(w, v) \in P^+} \indeg(w)$ rule applications, which is at most $m + nm$.
2. Semi-naive evaluation of the doubling grammar makes $\Oh(n \cdot |P^+|) = \Oh(n^3)$ rule applications.
3. With synchronous rounds, the right-linear grammar needs $\ell - 1$ productive rounds and the doubling grammar $\lceil \log_2 \ell \rceil$.
:::

::: proof
(1) Initialization attempts each edge once: $m$. A fact $(w, v)$ enters the work list only when first derived, so each fact of $P^+$ is processed exactly once; processing it applies $E(u, w) \wedge P(w, v) \Rightarrow P(u, v)$ once per in-edge $(u, w)$, i.e. $\indeg(w)$ times. Soundness and completeness of semi-naive evaluation follow by induction on path length.

(2) Each fact is processed once, and processing $(w, v)$ joins it with the current $\{u : P(u, w)\}$ and $\{z : P(v, z)\}$, at most $2n$ attempts.

(3) By induction, after $i$ synchronous rounds the right-linear iterate contains exactly the pairs at distance in $[1, i+1]$ and the doubling iterate those at distance in $[1, 2^i]$.
:::

Part 1 says something exact and somewhat deflating: **evaluating the path grammar is computing the closure**, with the work of one reverse search per target. The recursive description of paths, however elegant, does no less work than the classical algorithm. Parts 2 and 3 show that the *shape* of a grammar is a real cost parameter: the doubling grammar does asymptotically more work on long paths but needs exponentially fewer rounds — the trade between total work and parallel depth behind computing transitive closure by repeated squaring. This is well known in Datalog practice (linear versus non-linear recursion); the exact count in part 1 is, as far as this research has found, a convenient statement rather than a new result.

The SDK checks part 1 exactly on every test graph. The experiment of the ledger measured the doubling grammar on directed paths (\ledger{CGT-EXP-007}): its rule applications grew by a factor of about $8$ each time $n$ doubled (cubic), while the right-linear grammar's grew by $4$ (quadratic).

```python run
from cgtsdk import Cost
from cgtsdk.algorithms import path_grammar_closure

for n in (32, 64, 128):
    path = [[i + 1] if i + 1 < n else [] for i in range(n)]
    lin, dbl = Cost(), Cost()
    P1 = path_grammar_closure(path, "linear", lin)
    P2 = path_grammar_closure(path, "doubling", dbl)
    assert P1 == P2
    pairs = sum(map(len, P1))
    formula = (n - 1) + sum(len(P1[w]) * (1 if w > 0 else 0) for w in range(n))
    print(f"n={n:4d} |P+|={pairs:5d}  right-linear rules={lin.counts['rule']:6d} (formula {formula})  doubling rules={dbl.counts['rule']:8d}")
```

```output
n=  32 |P+|=  496  right-linear rules=   496 (formula 496)  doubling rules=    9516
n=  64 |P+|= 2016  right-linear rules=  2016 (formula 2016)  doubling rules=   81500
n= 128 |P+|= 8128  right-linear rules=  8128 (formula 8128)  doubling rules=  675004
```

(On a directed path every vertex except the first has in-degree $1$, so the formula reduces to $m + \sum_{w > 0} |P(w)| = |P^+|$.)

## The mapping, algorithm by algorithm {#sec:mapping}

| Algorithm | Grammar it evaluates | Algebra | Evaluation strategy | Mechanism visible |
|---|---|---|---|---|
| BFS | $E E^*$ from one source | Boolean / hop count | frontier by frontier | — (it *is* the search) |
| SCC condensation + bitsets | $E E^*$, all sources | Boolean | reverse topological, sharing rows | M-SHARE |
| Dijkstra | $E E^*$ | $(\min, +)$, non-negative | settle in distance order | algebraic monotonicity |
| Bellman–Ford | $E E^*$ | $(\min, +)$ | $n - 1$ global rounds | — |
| Floyd–Warshall | $E \mid P\,P$ restricted by intermediate vertex | $(\min, +)$ | Kleene elimination | — |
| semi-naive right-linear | $P \to E \mid E P$ | Boolean | worklist | — (exact work count, THM-004) |
| semi-naive doubling | $P \to E \mid P P$ | Boolean | worklist / squaring | depth for work |
| Kruskal / union–find | — (not a path problem) | — | greedy by weight | path compression is precomputation (M-PRE, amortized) |

The verdict for graph algorithms is again **equivalence**: each classical algorithm is an evaluation strategy for a path grammar in some algebra, and the grammar alone does not supply the strategy. The grammatical view earns its keep by making the shared structure explicit — which is what made the product construction of Chapter 8 and the constrained random surfer of Chapter 16 straightforward to derive.

::: exercise {#exr:10-1}
Verify part 1 of \ref{thm:grammar-shape} by hand on the graph with edges $0 \to 1$, $1 \to 2$, $0 \to 2$, $2 \to 0$.
:::

::: solution {of="exr:10-1"}
In-degrees: $\indeg(0) = 1$, $\indeg(1) = 1$, $\indeg(2) = 2$. All $9$ pairs are in $P^+$ (the graph is strongly connected), so each $w$ appears as first component in $3$ facts. Rule applications: $m + 3 \cdot (1 + 1 + 2) = 4 + 12 = 16$.
:::

::: exercise {#exr:10-2}
Show that Dijkstra's algorithm can return wrong distances with one negative edge and no negative cycle. Which algebraic property used by its evaluation strategy fails?
:::

::: exercise {#exr:10-3}
Design a third grammar for $P^+$ — for example $P \to E \mid P\,E$ (left-linear) — and derive its exact rule count under semi-naive evaluation. When is it cheaper than the right-linear grammar?
:::

::: solution {of="exr:10-3"}
Symmetrically to part 1, processing a new fact $(u, w)$ applies $P(u, w) \wedge E(w, v) \Rightarrow P(u, v)$ once per out-edge of $w$, so the count is $m + \sum_{(u, w) \in P^+} \outdeg(w)$. It is cheaper when vertices that are frequently *reached* have small out-degree relative to the in-degree of vertices that frequently *reach*; on the reverse graph the two grammars exchange costs.
:::

::: exercise {#exr:10-4}
Using the SDK, compare `transitive_closure` (bitsets) with `path_grammar_closure` on random digraphs of increasing density. Explain the result in terms of the word-RAM's word parallelism.
:::

::: summary
- Classical graph algorithms — traversal, components, shortest paths, spanning trees, closure — are implemented with counted costs and cross-checked against each other and brute force.
- Each path algorithm evaluates the grammar $E E^*$ in an algebra; the strategy, not the grammar, determines the cost.
- Evaluating the right-linear path grammar costs exactly $m + \sum_{(w,v) \in P^+} \indeg(w)$ rule applications: it *is* closure computation (\ledger{CGT-THM-004}).
- Two grammars with the same meaning can differ asymptotically: doubling trades $\Theta(n^3)$ work on paths for $\Oh(\log \ell)$ rounds.
- The verdict is equivalence; the benefit of the grammatical view is a shared vocabulary that makes new constructions easy to derive.
:::
