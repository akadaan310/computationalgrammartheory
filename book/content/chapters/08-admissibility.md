---
title: Admissibility Languages and the Product Construction
status: mixed
statusnote: The automata constructions are classical; the tight cost of constraints (factor |Q| attained; unbounded pruning) is proved here.
description: How an admissibility language is compiled into an automaton, how a structure is searched under it, and exactly how much a constraint can help or hurt.
---

::: objectives
- Compile a regular expression over move symbols into a minimal deterministic automaton, and know the cost of each step.
- Resolve a language-constrained query on a structure by searching the product of the structure with the automaton.
- Prove that a constraint can multiply the cost of search by exactly $|Q|$ and can also prune it to almost nothing.
- Explain why "search first, filter afterwards" is incorrect, and why enumerating walks is exponential.
- Describe what changes when the admissibility language is context-free.
:::

## From expression to automaton {#sec:compile}

An admissibility language is written as a regular expression over move symbols, such as `(a b)* (a | ε)` or `(L | R)* U`. The SDK compiles it by the classical three-stage pipeline:

1. **Thompson's construction** turns the expression into a nondeterministic automaton with $\varepsilon$-moves, with $\Oh(r)$ states for an expression of length $r$.
2. **The subset construction** turns it into a deterministic automaton whose states are sets of NFA states; in the worst case this is exponential in $r$.
3. **Moore's partition refinement** merges states with the same future, giving the **minimal** DFA — unique up to renaming (Myhill–Nerode).

::: proposition {#prop:minimal-size title="Determinization can be exponential" status="standard"}
The language "the $k$-th letter from the end is $a$", $(a \mid b)^*\, a\, (a \mid b)^{k-1}$, has an expression of length $\Oh(k)$ and a minimal DFA with $2^k$ states.
:::

::: proof
A DFA must remember the last $k$ letters: two different suffixes of length $k$ differ at some position $j$, and appending $j - 1$ further letters separates them (one is accepted, the other not). So at least $2^k$ states are needed, and the automaton tracking the last $k$ letters achieves it.
:::

The SDK's tests check the size $8$ for $k = 3$ and check acceptance of every word up to length six against Python's own regular-expression engine for a set of expressions:

```python run
from cgtsdk import compile_regex

for rx in ["a*", "(a b)* (a | ε)", "(L | R)* U", "(a | b)* a (a | b) (a | b)", "(a | b)* a (a | b) (a | b) (a | b) (a | b)"]:
    d = compile_regex(rx)
    print(f"{rx:44s} minimal DFA states = {d.size:3d}   accepts 'a b a': {d.accepts('a b a'.split())}")
```

```output
a*                                           minimal DFA states =   1   accepts 'a b a': False
(a b)* (a | ε)                               minimal DFA states =   2   accepts 'a b a': True
(L | R)* U                                   minimal DFA states =   2   accepts 'a b a': False
(a | b)* a (a | b) (a | b)                   minimal DFA states =   8   accepts 'a b a': True
(a | b)* a (a | b) (a | b) (a | b) (a | b)   minimal DFA states =  32   accepts 'a b a': False
```

(The automata are *partial*: a missing transition means the word can no longer be accepted, so no "dead" state is counted.) The size $|Q|$ of the minimal DFA is the grammar parameter that governs everything below.

::: demo regex-dfa
Text alternative: type a regular expression over move symbols and a word; the widget compiles the minimal DFA with the same pipeline as the SDK, prints its transition table, and reports whether the word is admissible.
:::

## Searching under a constraint {#sec:product}

Let $G = (\Sigma, \Str, \sem{\cdot}, \Lang)$ with $\Lang$ given by a DFA $D = (Q, \Sigma, \delta, q_0, F)$ with partial $\delta$. The **constrained resolution** problem is: given $x$, compute $\sem{\Lang}(x)$, the set of elements reachable from $x$ by some admissible word. For a labelled graph this is the regular path query of Chapter 6.

The answer is found by searching the **product** $A \times Q$: there is a product edge $(y, q) \to (z, \delta(q, a))$ for each move $(y, z) \in \sem{a}$ with $\delta(q, a)$ defined. Then $y \in \sem{\Lang}(x)$ iff some $(y, q)$ with $q \in F$ is reachable from $(x, q_0)$.

::: theorem {#thm:product title="Product resolution, and the exact cost of a constraint" status="proved-here" ledger="CGT-THM-001"}
Let $m = \sum_a |\sem{a}|$.

1. *(Upper bound; standard.)* $\sem{\Lang}(x)$ is computable in $\Oh(|Q| \cdot (|\Sigma| n + m))$ time and $\Oh(|Q| \cdot n)$ space.
2. *(A constraint can cost a factor $|Q|$ and prune nothing.)* For all $k \ge 1$ and all $n$ coprime to $k$ there are a structure with $n$ elements and $m = n$ and a $k$-state DFA such that unconstrained search from $x$ visits $n$ states, product search visits exactly $nk$, and $\sem{\Lang}(x)$ equals the unconstrained answer.
3. *(A constraint can prune almost everything.)* For every $n$ there are a structure with $n$ elements and a one-state DFA such that product search visits $1$ state, unconstrained search visits $n$, and the answers differ.
:::

::: proof
(1) By induction on $|w|$: $y \in \sem{w}(x)$ and $\delta^*(q_0, w) = q$ iff $(y, q)$ is reachable from $(x, q_0)$ along a product walk spelling $w$. The product has at most $|Q| n$ vertices; each is expanded once, consulting $\delta$ for each letter ($|Q||\Sigma| n$ in total) and inspecting each move of its first component once per state ($|Q| m$ in total). This is the classical construction \cite{mendelzon1995,barrett2000}.

(2) Take the directed cycle on $\Z_n$ with one label $a$, $\sem{a} = \{(i, i+1 \bmod n)\}$, and $\Lang = \{a^t : t \equiv 0 \pmod k\}$, whose DFA is the $k$-cycle on $\Z_k$. The product move is $(i, j) \mapsto (i + 1 \bmod n, j + 1 \bmod k)$, and the orbit of $(0, 0)$ is $\{(t \bmod n, t \bmod k) : t \ge 0\}$, of size $\operatorname{lcm}(n, k) = nk$ by the Chinese remainder theorem. Unconstrained search visits the $n$ vertices. For every target $i$ some $t$ satisfies $t \equiv i \pmod n$ and $t \equiv 0 \pmod k$, so $\sem{\Lang}(0) = \Z_n$, the unconstrained answer.

(3) Take a star with centre $x$ and $n-1$ edges labelled $b$ to leaves, and $\Lang = a^*$. The product visits only $(x, q_0)$ and answers $\{x\}$; unconstrained search visits all $n$ vertices.
:::

Part 1 is textbook material; parts 2 and 3 are elementary and quite possibly folklore, but together they state something that is rarely made explicit: **a grammatical constraint is not a speedup**. It changes the search space, in either direction, by up to the size of the automaton. Whether it helps depends jointly on the language and on the structure — exactly the claim of hypothesis H-005, which the experiments supported (\ledger{CGT-H-005}).

```python run
from cgtsdk import Cost, compile_regex
from cgtsdk.algorithms import product_reach
from cgtsdk.structures import GraphStructure

n = 101
cycle = GraphStructure(n, [(i, "a", (i + 1) % n) for i in range(n)])
for k in (1, 2, 5, 10):
    rx = " ".join(["a"] * k)                     # words of length divisible by k: (a^k)*
    reach, explored = product_reach(cycle, 0, compile_regex(f"({rx})*"), return_explored=True)
    print(f"k={k:2d}: product states explored = {explored:4d} = n*k = {n*k:4d};  |answer| = {len(reach)}")
```

```output
k= 1: product states explored =  101 = n*k =  101;  |answer| = 101
k= 2: product states explored =  202 = n*k =  202;  |answer| = 101
k= 5: product states explored =  505 = n*k =  505;  |answer| = 101
k=10: product states explored = 1010 = n*k = 1010;  |answer| = 101
```

On random labelled graphs (\ledger{CGT-EXP-003}) the measured ratio of explored product states to unconstrained states ranged from $0.003$ (language $a^*$ on a sparse graph) to exactly $5.000$ (walk length divisible by $5$): both extremes of the theorem occur in practice, not only on constructed inputs.

::: demo product
Text alternative: on an eight-vertex labelled graph, type a regular expression; the widget compiles its DFA, runs breadth-first search over (vertex, state) pairs, highlights the vertices of $\sem{\Lang}(\text{source})$, and compares the number of explored product states with plain reachability — which explores up to $|Q|$ times fewer states and gives a different answer whenever the constraint matters.
:::

## Two incorrect shortcuts {#sec:shortcuts}

Two tempting alternatives to the product construction fail.

**Search, then filter.** Plain reachability forgets *which* label words lead to a vertex, so no filtering of its answer can recover $\sem{\Lang}(x)$. On the random graphs of the experiment, unconstrained search misreported up to about 15,600 of 20,000 vertices for restrictive languages (\ledger{CGT-OBS-007}). The constraint must be carried *during* the search.

**Enumerate walks, then check the word.** This is correct if walks up to length $|Q| \cdot n$ are enumerated — any longer accepted walk revisits a product state and can be shortened — but the number of walks grows exponentially. On a 12-vertex graph the experiment's walk enumeration hit its cap of two million walks while the product had at most $55$ states. The product construction is, in effect, the **sharing** mechanism applied to walks: all walks reaching the same (vertex, state) pair are represented once.

## Context-free admissibility {#sec:cfl}

When $\Lang$ is context-free — balanced parentheses for matched calls and returns, the Dyck language of Chapter 3 — the product is no longer a finite graph, and constrained reachability becomes **CFL-reachability**, the formulation behind interprocedural program analysis \cite{reps1998,yannakakis1990}. It is solved by a dynamic program over pairs of vertices and nonterminals in time cubic in $n$ (with factors depending on the grammar) \cite{barrett2000}. Whether the factor-$|Q|$ phenomenon of \ref{thm:product} has a precise context-free analogue — how the size of the grammar enters, and whether the bound is attained — is open (\ledger{CGT-OPEN-008}).

::: exercise {#exr:8-1}
Compile `(L | R)* U` by hand: give the Thompson NFA, the subset DFA, and the minimal DFA. Explain in one sentence what language of tree navigations it describes.
:::

::: solution {of="exr:8-1"}
The minimal DFA has two states: a start state $q_0$ looping on $L$ and $R$, and an accepting state $q_1$ reached by $U$ from $q_0$, with no transitions out of $q_1$. It describes any downward walk followed by exactly one step up — for example, "go to a node, then report its parent".
:::

::: exercise {#exr:8-2}
In part 2 of \ref{thm:product}, what happens when $\gcd(n, k) = g > 1$? Compute the number of explored product states and the answer set.
:::

::: solution {of="exr:8-2"}
The orbit of $(0,0)$ has size $\operatorname{lcm}(n,k) = nk/g$, and $t \equiv i \pmod n$, $t \equiv 0 \pmod k$ is solvable iff $g \mid i$. So $nk/g$ states are explored and the answer is the $n/g$ vertices divisible by $g$.
:::

::: exercise {#exr:8-3}
Prove the shortening argument: if some walk from $x$ to $y$ has its label in $\Lang$, then some such walk has length less than $|Q| \cdot n$.
:::

::: exercise {#exr:8-4}
Using the SDK, generate a random labelled graph with $n = 2000$ and average degree $1.5$, and compare product-search sizes for `a*`, `(a b)* c` and "length divisible by 5". Reproduce the qualitative pattern of \ledger{CGT-EXP-003}.
:::

::: summary
- Admissibility languages compile to minimal DFAs (Thompson, subset, Moore); determinization can cost $2^k$ states.
- Constrained resolution is search on the product $A \times Q$, in $\Oh(|Q|(|\Sigma| n + m))$ time.
- A constraint can multiply the search space by exactly $|Q|$ without changing the answer, or prune it to a single state (\ledger{CGT-THM-001}); measured ratios on random graphs span both extremes.
- Filtering an unconstrained search is incorrect; enumerating walks is exponential; the product shares all walks that reach the same (vertex, state) pair.
- Context-free admissibility leads to CFL-reachability, cubic in general; its cost-of-constraint theory is open.
:::
