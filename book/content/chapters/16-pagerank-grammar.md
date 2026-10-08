---
title: PageRank Through the Lens of Grammar
status: mixed
statusnote: One proposed model (the grammar-constrained surfer) with proved basic properties and measured costs; its novelty and usefulness are open. Everything else is a re-reading of established results.
description: The random surfer as a probabilistic operational grammar, rankings constrained by admissibility languages, block structure as a structural grammar — and an honest list of what the grammatical view does not improve.
---

::: objectives
- Read the random surfer as an operational grammar with probabilistic semantics.
- Define the grammar-constrained surfer, prove its basic properties, and state its cost.
- Interpret its measured effect on rankings, and say what would be needed to show that it is useful.
- Place host/block structure, ordering and incremental updates in the mechanism taxonomy.
- List what the grammatical view does not provide for PageRank.
:::

## The surfer as a grammar {#sec:surfer-grammar}

The random surfer of Chapter 15 has two moves, *follow* and *teleport*, applied at random. As an operational grammar its states are pages, its moves are relations — follow maps $u$ to its out-neighbours, teleport maps $u$ to every page — and its semantics is **probabilistic**: each move carries a probability distribution over successors instead of a set. The PageRank vector is the long-run frequency with which the moves' composition visits each page. Nothing is gained by renaming the model; the reason to read it this way is that the operational-grammar toolkit of Part II — and in particular admissibility languages and the product construction — applies to it directly.

## Constraining the surfer {#sec:constrained}

On a graph whose links carry labels (a citation that *supports* or *refutes*, a link between people that is *colleague* or *family*, a hyperlink in *navigation* or *content*), one may want a ranking driven only by certain *patterns* of links. Admissibility languages express such patterns, and the product construction of Chapter 8 turns them into a Markov chain.

::: definition {#def:constrained-surfer title="Grammar-constrained random surfer" ledger="CGT-PROP-010"}
Let $G$ be an edge-labelled graph on $n$ vertices, $D = (Q, \Sigma, \delta, q_0, F)$ a DFA over labels (all states treated as live; the language is effectively prefix-closed), and $\alpha \in [0,1)$. The constrained surfer lives on $V \times Q$. From $(u, q)$:

- with probability $\alpha$ it follows a uniformly random edge $(u, a, w)$ among those with $\delta(q, a)$ defined, moving to $(w, \delta(q, a))$; if there is no such edge, it jumps as in the next case;
- with probability $1 - \alpha$ it jumps to $(w, q_0)$ with $w$ uniform.

The **constrained rank** of $w$ is $\sum_q \pi(w, q)$, where $\pi$ is the stationary distribution.
:::

::: proposition {#prop:constrained title="Basic properties of the constrained surfer" status="proposed" ledger="CGT-PROP-010"}
1. Only states reachable from $V \times \{q_0\}$ carry probability; there are at most $|Q| \cdot n$ of them.
2. One power iteration costs at most $|Q| \cdot m$ edge operations plus $\Oh(|Q| n)$.
3. The stationary distribution exists and is unique, and power iteration converges with rate $\alpha$ with the certified error bound of \ref{thm:contraction}.
4. For the one-state universal DFA, constrained rank equals PageRank of the underlying multigraph.
:::

::: proof
(1) and (2) hold by the product construction (\ref{thm:product}): each product state is expanded once per iteration, inspecting the edges of its vertex whose label the DFA admits. (3) is \ref{thm:contraction} applied to the product chain with teleportation vector $\frac{1}{n}\mathbf{1}_{V \times \{q_0\}}$, a probability distribution. (4) With one state that admits every label, the product chain is the surfer chain itself.
:::

The status badge reads *proposed*: the model is defined here, its properties are elementary, and **its novelty is unknown**. Products of Markov chains with automata are standard in probabilistic model checking \cite{baier2008}, and similarity measures driven by label patterns ("meta-paths") are established for heterogeneous information networks \cite{sun2011}; whether this exact ranking model has been published is an open literature question (\ledger{CGT-OPEN-011}).

```python run
import random
from cgtsdk import DFA, Cost, compile_regex
from cgtsdk.algorithms import constrained_pagerank, pagerank_power

rng = random.Random(10)
n = 2000
E = [(u, rng.choice("abc"), int(rng.random() ** 2 * n)) for u in range(n) for _ in range(rng.randrange(0, 7))]
E = [(u, a, w) for (u, a, w) in E if u != w]
adj = [[] for _ in range(n)]
for u, _, w in E:
    adj[u].append(w)
plain_cost = Cost()
plain = pagerank_power(adj, 0.85, tol=1e-10, cost=plain_cost)
top = lambda s: [i for i, _ in sorted(enumerate(s), key=lambda t: (-t[1], t[0]))[:10]]
for name, dfa in [("universal", DFA.universal("abc")), ("no c: (a | b)*", compile_regex("(a | b)*")),
                  ("alternate: (a b)* (a | ε)", compile_regex("(a b)* (a | ε)"))]:
    c = Cost()
    scores, res, N = constrained_pagerank(n, E, dfa, 0.85, 1e-10, cost=c)
    l1 = sum(abs(x - y) for x, y in zip(scores, plain.scores))
    print(f"{name:26s} |Q|={dfa.size}  product states={N:5d}  cost ratio={c.counts['edge'] / plain_cost.counts['edge']:.2f}"
          f"  top-10 overlap={len(set(top(scores)) & set(top(plain.scores)))}  L1 distance={l1:.3f}")
```

```output
universal                  |Q|=1  product states= 2000  cost ratio=1.03  top-10 overlap=10  L1 distance=0.000
no c: (a | b)*             |Q|=1  product states= 2000  cost ratio=0.80  top-10 overlap=7  L1 distance=0.338
alternate: (a b)* (a | ε)  |Q|=2  product states= 3118  cost ratio=0.67  top-10 overlap=8  L1 distance=0.411
```

The universal language reproduces PageRank exactly, at a small overhead for building the product. A one-state language that forbids `c` links is *cheaper* than PageRank (fewer admissible edges), is at $L_1$ distance $0.34$ from it — so about $17\%$ of the probability mass moves, since $L_1$ distance is twice the total-variation distance — and changes three of the top ten pages; the alternating language uses about $1.6 n$ product states, moves about $21\%$ of the mass and changes two of the top ten. The ledger's experiment (\ledger{CGT-EXP-010}) found the same pattern on other graphs and languages, with costs from $0.46\times$ to $6.4\times$ PageRank, and validated each constrained ranking against a direct linear solve of the materialized product chain (\ledger{CGT-OBS-018}).

::: boundary
These experiments show that constrained rankings *differ* from PageRank and what they *cost*. They do not show that the differences are *improvements* for any retrieval task. That requires labelled corpora and relevance judgments, which this research does not have. The proposal is a model with known costs, not a demonstrated improvement.
:::

## Block structure as a structural grammar {#sec:blocks}

Web graphs are not random: most links stay within a host. BlockRank exploits this by computing local rankings inside hosts, combining them by host importance, and using the result to start a global power iteration, reporting a speed-up by a small factor \cite{kamvar2003}. In this book's taxonomy the host partition is a **structural grammar** of the graph (a two-level grammar: hosts, then pages), and the method combines M-SHARE (local computations reused as a starting vector), ordering, and M-PRE (warm starts). The general lesson of Chapter 15 applies: power iteration's cost per iteration is invariant under reordering, and what structure buys is a *better starting point* or a *better sweep order* for Gauss–Seidel-like methods — and fewer cut edges when the graph is distributed.

## What the grammatical view does not provide {#sec:not}

It is important to be explicit:

- **No faster PageRank.** Every iteration still reads every admissible edge. The constrained surfer can be cheaper than PageRank only because it ranks a different, smaller chain.
- **No change to convergence theory.** Rates, bounds and solver behaviour are those of Chapter 15.
- **No evidence about ranking quality.** See the boundary above.
- **No claim about production search.** Modern search engines rank with many signals beyond link analysis; nothing here addresses them.

What it does provide is a uniform way to *state* constrained and structured link analyses — as languages over link labels and grammars over graph structure — together with cost bounds that follow from the product construction rather than having to be derived afresh for each variant. Related ranking problems — personalized and topic-sensitive rankings \cite{haveliwala2002}, hub-and-authority methods, ranking in heterogeneous networks \cite{sun2011} — fit the same pattern, and are directions rather than results of this book.

::: exercise {#exr:16-1}
Show that the constrained surfer with a DFA that admits a label only from state $q_0$ and then has no further transitions (the language "at most one link") produces a ranking computable without iteration. What is it?
:::

::: solution {of="exr:16-1"}
From $(u, q_0)$ the surfer follows one admissible link to $(w, q_1)$, from which every move is a jump back to $V \times \{q_0\}$. The chain has depth one, and $\pi$ can be written in closed form: mass on $(w, q_1)$ is $\alpha$ times the uniform mass flowing over in-links of $w$, normalized. The ranking is essentially a weighted in-degree (one-step citation count).
:::

::: exercise {#exr:16-2}
Prove part 2 of \ref{prop:constrained} precisely, and give a family of graphs and languages on which the bound $|Q| \cdot m$ per iteration is attained.
:::

::: exercise {#exr:16-3}
Design an evaluation that could show whether a constrained ranking is better than PageRank for a concrete task. What data, metric and baseline would you need, and what would count as a negative result?
:::

::: summary
- The random surfer is an operational grammar with probabilistic semantics; admissibility languages constrain it through the product construction.
- The grammar-constrained surfer has at most $|Q| n$ states, costs at most $|Q| m$ edge operations per iteration, converges at rate $\alpha$ with certified error, and reduces to PageRank for the universal language (\ledger{CGT-PROP-010}).
- Measured: constrained rankings differ materially from PageRank at costs between about half and six times PageRank's; their usefulness is untested and their novelty unverified.
- Host structure is a structural grammar of the graph; what it buys is starting points, sweep orders and fewer cut edges, not cheaper iterations.
- The grammatical view gives a uniform statement of constrained link analysis with derived costs, not a faster PageRank.
:::
