---
title: Graphs and Paths
status: mixed
statusnote: Standard material; the relational reading of paths is classical (Kleene algebra, Tarjan's path expressions) and is restated here as the semantic basis of the book.
description: Graph representations, walks versus simple paths, and the relational semantics that makes "a path is an edge followed by a path" a theorem rather than a slogan.
---

::: objectives
- Compare adjacency-matrix and adjacency-list representations by the cost of their basic operations.
- Read a labelled graph as a family of relations, and words of labels as compositions of relations.
- Prove that the meaning of a word of moves is the composition of the meanings of its letters, and that languages of words denote unions.
- Distinguish walks from simple paths, and explain why that semantic choice moves a problem from polynomial time to NP-hardness.
- Relate paths-as-grammar to Tarjan's path expressions and to semiring path problems.
:::

## Graphs and their representations {#sec:graph-repr}

A **directed graph** $G = (V, E)$ is a structure with one binary relation $E \subseteq V \times V$. A **labelled** graph has one relation $E_a$ per label $a$ in a finite alphabet $\Sigma$; a **weighted** graph attaches a number to each edge. Throughout, $n = |V|$ and $m = |E|$.

Two representations dominate:

| Operation | Adjacency matrix ($n^2$ bits) | Adjacency lists ($\Oh(n + m)$ words) |
|---|---|---|
| test whether $(u, v) \in E$ | $\Oh(1)$: one bit at address $un + v$ | $\Oh(\outdeg(u))$, or $\Oh(1)$ expected with hashing |
| list the out-neighbours of $u$ | $\Theta(n)$ | $\Theta(\outdeg(u))$ |
| breadth-first search from $s$ | $\Theta(n^2)$ | $\Theta(n + m)$ |
| space | $\Theta(n^2)$ bits | $\Theta(n + m)$ words |

The matrix applies the array's address formula to *pairs* of vertices (row-major numeration of $V \times V$, Chapter 2), so edge tests are arithmetic; but it pays $n^2$ bits whether or not the graph is sparse, and every traversal touches whole rows. Lists pay only for edges that exist. Neither is better in general — the familiar shape of every comparison in this book.

## Labelled graphs as relations {#sec:relations}

Read each label $a$ as a **move** whose meaning is the relation $E_a$: from vertex $u$, the move $a$ may lead to any $v$ with $(u, v) \in E_a$. A *word* of labels $a_1 a_2 \cdots a_k$ then means "follow an $a_1$ edge, then an $a_2$ edge, …", and its meaning is a composition of relations.

::: definition {#def:relsem title="Relational semantics of move words" ledger="CGT-DEF-002"}
Given relations $\sem{a} \subseteq V \times V$ for each $a \in \Sigma$, extend $\sem{\cdot}$ to words and languages by

$$\sem{\varepsilon} = \mathrm{id}_V, \qquad \sem{u w} = \sem{u} \then \sem{w}, \qquad \sem{\Lang} = \bigcup_{w \in \Lang} \sem{w},$$

where $R \then S = \{(x, z) : \exists y.\ (x, y) \in R \wedge (y, z) \in S\}$ is relational composition (first $R$, then $S$). For a vertex $x$, write $\sem{w}(x) = \{y : (x, y) \in \sem{w}\}$.
:::

::: proposition {#prop:homomorphism title="Compositional semantics" status="standard" ledger="CGT-PROP-001"}
$\sem{\cdot}$ is a monoid homomorphism from $(\Sigma^*, \cdot, \varepsilon)$ to $(\Rel(V), \then, \mathrm{id}_V)$. For languages, $\sem{\Lang_1 \Lang_2} = \sem{\Lang_1} \then \sem{\Lang_2}$, $\sem{\Lang_1 \cup \Lang_2} = \sem{\Lang_1} \cup \sem{\Lang_2}$, and $\sem{\Lang^*} = \bigcup_{k \ge 0} \sem{\Lang}^k$, the reflexive–transitive closure of $\sem{\Lang}$.
:::

::: proof
The extension to words is by composition, and relational composition is associative with identity $\mathrm{id}_V$, so $\sem{uw} = \sem{u} \then \sem{w}$ for all words by induction on $|u|$. Composition distributes over arbitrary unions on both sides, which gives the identities for concatenation and union of languages, and hence for $\Lang^* = \bigcup_k \Lang^k$.
:::

The proposition turns the recursive slogan "a path from $u$ to $v$ is an edge from $u$ to some $w$ followed by a path from $w$ to $v$" into an identity:

$$\sem{E E^*} = \sem{E} \then \sem{E^*} . \label{eq:path-recursion}$$

Paths really are grammatical objects: the set of walks is the language $E E^*$ (or $\Sigma^+$ for labelled graphs), and its meaning is the transitive closure. This is the relational reading underlying Kleene algebra, and Tarjan's **path expressions** make it algorithmic: a regular expression over the edges that represents *all* paths from a source to each vertex, from which shortest paths, path counts and dataflow facts can be computed by interpreting the expression in a suitable algebra \cite{tarjan1981unified,tarjan1981fast}. Tarjan showed that constructing path expressions is, in a precise sense, the most general path problem.

::: boundary
\ref{prop:homomorphism} is a statement about **semantics**. It says the recursive description of paths is *correct*; it says nothing about how *cheaply* a path can be found. Chapter 10 shows that evaluating the recursive description is exactly the work of computing a closure, and that two grammars with the same meaning can differ asymptotically in cost (\ledger{CGT-THM-004}).
:::

The SDK implements this relational semantics directly: the state of `GraphStructure` is a *set* of current vertices, and a label move maps the set to its image.

```python run
from cgtsdk.structures import GraphStructure

edges = [(0, "a", 1), (0, "a", 2), (1, "b", 3), (2, "b", 3), (3, "a", 0), (2, "c", 4)]
g = GraphStructure(5, edges).grammar()
r = g.execute("at(0) a here b here a here c")
print(r.values, "| defined:", r.defined, "| undefined at call", r.undefined_at, "-", r.reason)
```

```output
[None, None, [1, 2], None, [3], None, [0]] | defined: False | undefined at call 7 - ⟦c⟧ of the current set is empty
```

From $\{0\}$, the move $a$ reaches $\{1, 2\}$, then $b$ reaches $\{3\}$, then $a$ returns to $\{0\}$; the final $c$ has no edge from $0$, so the expression is undefined *at that call* — the semantic layer again, with its reason.

## Walks, simple paths, and a change of meaning {#sec:simple}

A **walk** may repeat vertices; a **simple path** may not. The distinction looks minor. It is not.

::: proposition {#prop:walk-vs-simple title="Walk semantics versus simple-path semantics" status="standard"}
Let $\Lang$ be a regular language over the labels, given by an automaton with $|Q|$ states. Deciding whether some *walk* from $s$ to $t$ has its label word in $\Lang$ takes $\Oh(|Q|(|\Sigma| n + m))$ time. Deciding whether some *simple path* from $s$ to $t$ has its label word in $\Lang$ is NP-complete for some fixed regular languages $\Lang$ \cite{mendelzon1995}, and remains NP-hard on very restricted graph classes \cite{barrett2000}.
:::

The first half is the product construction of Chapter 8 (\ledger{CGT-THM-001}); the second is a theorem of Mendelzon and Wood. Nothing about the *syntax* of the query changed — the same regular expression, the same graph. What changed is the **semantics**: which sequences of edges count as a path. That one change moves the problem across the boundary between polynomial time and NP-completeness (assuming P ≠ NP). It is the clearest example in this book of why the semantic layer must be stated precisely before any claim about cost is made.

## Path problems as algebra {#sec:semirings}

Many path problems differ only in *how* the paths in $\sem{E^*}$ are aggregated:

| Problem | Value of a path | Combine alternatives | Algebra |
|---|---|---|---|
| reachability | true | or | Boolean semiring $(\{0,1\}, \vee, \wedge)$ |
| shortest path | sum of weights | min | tropical semiring $(\R \cup \{\infty\}, \min, +)$ |
| widest path | min of capacities | max | $(\R, \max, \min)$ |
| number of paths (DAG) | 1 | + | $(\N, +, \times)$ |

Interpreting the path grammar in each algebra gives each problem; this is the unifying idea behind Tarjan's path algebra and the closed-semiring treatment of shortest paths in textbooks \cite{clrs2022}. For CGT the point is precise: the **grammar** of paths ($E E^*$) is common to all of them; the **semantics** is chosen by the algebra; the **execution** cost depends on the algebra's properties (Dijkstra's algorithm needs non-negative weights; Bellman–Ford does not). Chapter 10 implements each.

::: exercise {#exr:6-1}
For the graph of the SDK example above, compute $\sem{(a\,b)^*}(0)$ and $\sem{a\,(b\,a)^*}(0)$ by hand, using \ref{prop:homomorphism}.
:::

::: solution {of="exr:6-1"}
$\sem{ab}(0) = \sem{b}(\{1, 2\}) = \{3\}$ and $\sem{ab}(3) = \sem{b}(\sem{a}(3)) = \sem{b}(\{0\}) = \varnothing$, so $\sem{(ab)^*}(0) = \{0\} \cup \{3\} = \{0, 3\}$. For $a(ba)^*$: $\sem{a}(0) = \{1,2\}$; $\sem{ba}(\{1,2\}) = \sem{a}(\{3\}) = \{0\}$; $\sem{ba}(\{0\}) = \sem{a}(\sem{b}(0)) = \varnothing$. Hence $\sem{a(ba)^*}(0) = \{1, 2, 0\}$.
:::

::: exercise {#exr:6-2}
Show that relational composition does *not* distribute over intersection: give relations $R, S, T$ with $R \then (S \cap T) \neq (R \then S) \cap (R \then T)$. What does this imply for a "language" built with intersection?
:::

::: exercise {#exr:6-3}
Explain why the walk/simple-path dichotomy does not arise for the language $\Sigma^*$ (plain reachability): show that if a walk from $s$ to $t$ exists, a simple path exists.
:::

::: exercise {#exr:6-4}
In the counting semiring, $\sem{E^*}$ may be infinite on graphs with cycles. Which property of DAGs makes path counting well defined, and how is it computed in $\Oh(n + m)$ time?
:::

::: summary
- Adjacency matrices apply the address formula to vertex pairs; adjacency lists pay only for existing edges. Neither dominates.
- Labels are moves whose meanings are relations; words mean compositions and languages mean unions (\ledger{CGT-PROP-001}). "A path is an edge followed by a path" is the identity $\sem{EE^*} = \sem{E} \then \sem{E^*}$.
- This is a semantic fact, not a cost bound.
- Changing the semantics from walks to simple paths makes regular path queries NP-complete: the syntax is unchanged, the meaning is not.
- Path problems share a grammar and differ by the algebra in which it is interpreted.
:::
