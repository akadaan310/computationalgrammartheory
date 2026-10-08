---
title: "The Limits: Advice, Restriction, and P versus NP"
status: mixed
statusnote: The boundary proposition restates standard complexity theory; the solution-grammar measurements are empirical and do not decide their own question.
description: What a grammar can and cannot do to complexity classes — stated as precise challenges with their proof obligations, and answered.
---

::: objectives
- State, for each classical boundary of complexity theory touched by this program, the exact theorem or model being questioned, the CGT alternative proposed, and the proof obligation it would have to meet.
- Prove that, within standard models, attaching a grammar to inputs cannot move a problem across the P/NP boundary — and identify exactly the four ways in which claims to the contrary go wrong.
- Distinguish tractability that comes from a restricted class (2-SAT) from tractability that a grammar would have to supply.
- Read the solution-grammar experiment for SAT, and why it does not settle anything asymptotically.
:::

## The challenge, made explicit {#sec:challenge}

The research program began with an ambitious conjecture: if computational structures have sufficiently expressive grammars, certain problems might become dramatically easier — perhaps resolvable in constant or near-constant time. A conjecture of that kind is only worth stating if it is stated against something precise. The table lists each classical boundary this book has touched, what CGT proposed against it, and what a proof would have to show.

| Established result or model | CGT proposal | Required assumptions | Proof obligation | Outcome in this book |
|---|---|---|---|---|
| Comparison sorting needs $\log_2 n!$ comparisons | grammars of sorted orders | comparison model | a sort with fewer comparisons | impossible in the model; escape only by addressing (counting sort), which is a change of model (Ch. 9) |
| Reachability needs search or stored answers | a reachability grammar answering in $\Oh(1)$ | retrieval-only, all digraphs | encoding of $o(n^2)$ bits | **impossible**: $\lfloor n/2\rfloor\lceil n/2 \rceil$ bits needed (\ledger{CGT-THM-002}) |
| Preprocessing–query trade-offs | grammatical indexes | static data | break-even and space bounds | indexes pay only after $Q^*$ queries per epoch (\ledger{CGT-PROP-005}) |
| Constant-time navigation needs dense addressing | compiled move words | uniform move semantics | constant-size compiled form | **established** for heap-shaped trees, grids, hypercubes, de Bruijn graphs; **impossible** for arbitrary shapes (\ledger{CGT-THM-006}, \ledger{CGT-THM-007}) |
| Work–depth trade-offs in parallel evaluation | grammar shape as a cost parameter | semi-naive evaluation | exact counts | established for one pair of grammars (\ledger{CGT-THM-004}) |
| Constraints prune search | admissibility languages | regular languages | a speedup guarantee | **false** in general: a factor $\lvert Q\rvert$ slowdown is attained (\ledger{CGT-THM-001}) |
| P versus NP | expressive grammars resolve NP-hard problems quickly | standard Turing/RAM models | a polynomial algorithm for an NP-complete problem, or a separation proof | **no route** within standard models (\ref{prop:pnp}) |
| Parameterized complexity | grammar-parameterized costs $T(n, g, q, u, o)$ | — | a distinction not captured by existing parameterizations | **open** (\ledger{CGT-OPEN-005}) |

Several rows are negative. That is the point of making the challenge explicit: a precise "no" is a scientific result, and it sharpens what the positive rows mean.

## Grammars and the P/NP boundary {#sec:pnp}

Let $\Pi \subseteq \{0,1\}^*$ be a decision problem, and suppose a "grammar" $\Gamma$ is attached to inputs to help decide $\Pi$. What $\Gamma$ can do depends entirely on where it comes from and how large it is.

::: proposition {#prop:pnp title="Four ways a grammar can help, and what each implies" status="standard" ledger="CGT-PROP-006"}
1. **Uniform and polynomial.** If $\Gamma(x)$ is computable in time $\poly(|x|)$ and $\Pi(x)$ is decidable from $(x, \Gamma(x))$ in time $\poly(|x|)$, then $\Pi \in \P$. If $\Pi$ is NP-complete, this means $\P = \NP$.
2. **Advice.** If $\Gamma$ depends only on $|x|$, has size $\poly(|x|)$, and $\Pi$ is decidable from $(x, \Gamma_{|x|})$ in polynomial time, then $\Pi \in \Ppoly$. For NP-complete $\Pi$, this would collapse the polynomial hierarchy to its second level \cite{karp1980} — widely believed false.
3. **Unbounded size.** For every decidable $\Pi$, letting $\Gamma_n$ be the truth table of $\Pi$ on inputs of length $n$ ($2^n$ bits) answers every query by a single lookup; building $\Gamma_n$ costs at least $2^n$ decisions. Nothing follows about P versus NP.
4. **Restriction.** Restricting $\Pi$ to a class $C$ of inputs may make it polynomial while $\Pi$ remains NP-complete (2-CNF versus 3-CNF \cite{aspvall1979}). The tractability belongs to $C$.
:::

::: proof
(1) is composition of polynomial-time computations. (2) is the definition of $\Ppoly$ together with the Karp–Lipton theorem. (3) holds by construction. (4) is an example.
:::

Read against the founding conjecture, the proposition says: within the standard models, a grammar that makes an NP-complete problem fast is either an ordinary polynomial-time algorithm in disguise (case 1 — a proof of $\P = \NP$, to be judged as such), or polynomial advice (case 2 — believed impossible), or an exponential lookup table (case 3 — retrieval, not discovery), or a restriction of the problem (case 4). There is no fifth door. The ledger records the strong form of the conjecture as **rejected** (\ledger{CGT-NEG-009}); what survives is the study of which restricted classes and which preprocessing regimes allow fast resolution — the subject of the rest of the book.

::: boundary
Nothing in this book proves or disproves $\P = \NP$, and no claim is made that Computational Grammar Theory bears on the question beyond \ref{prop:pnp}. A fast benchmark on chosen instances, a new notation, or an algorithm that is fast on a restricted class is not evidence about the unrestricted problem.
:::

## Restriction: 2-SAT {#sec:2sat}

Satisfiability of CNF formulas with at most two literals per clause is solvable in linear time \cite{aspvall1979}: each clause $(a \vee b)$ is the pair of implications $\neg a \Rightarrow b$ and $\neg b \Rightarrow a$, and the formula is satisfiable iff no variable shares a strongly connected component of this **implication graph** with its negation. The implication graph is a structural grammar of the formula, and the decision procedure is the SCC algorithm of Chapter 10. With three literals per clause the problem is NP-complete, and no comparable structure is known. The tractability comes from the restriction, not from having a grammar. (The large random instance below has clause-to-variable ratio $1.5$, above the satisfiability threshold of random 2-CNF, and is unsatisfiable; deciding that also takes linear time.)

```python run
import random
from cgtsdk import Cost
from cgtsdk.algorithms import brute_force_count, satisfies, two_sat

rng = random.Random(11)
agree = 0
for trial in range(300):
    n = rng.randrange(2, 13)
    clauses = [tuple(rng.choice([v, -v]) for v in rng.sample(range(1, n + 1), 2)) for _ in range(rng.randrange(1, 2 * n))]
    a = two_sat(n, clauses)
    agree += (a is not None) == (brute_force_count(n, clauses) > 0) and (a is None or satisfies(a, clauses))
print(f"2-SAT via implication-graph SCCs agrees with brute force on {agree}/300 random formulas")
c = Cost()
big = [tuple(rng.choice([v, -v]) for v in rng.sample(range(1, 100_001), 2)) for _ in range(150_000)]
print("100,000 variables, 150,000 clauses:", "satisfiable" if two_sat(100_000, big, c) else "unsatisfiable",
      f"- {c.counts['edge']} edge inspections (linear in the formula)")
```

```output
2-SAT via implication-graph SCCs agrees with brute force on 300/300 random formulas
100,000 variables, 150,000 clauses: unsatisfiable - 600000 edge inspections (linear in the formula)
```

## Solution grammars for 3-SAT {#sec:solution-grammar}

The most expressive grammar one can attach to a satisfiability instance is a grammar generating exactly its satisfying assignments — in its canonical form, a layered deterministic automaton over $\{0,1\}$, essentially an ordered binary decision diagram. Once it exists, satisfiability, model counting and many other queries are linear in its size: retrieval. This is **knowledge compilation**, a field that maps exactly this trade-off between the succinctness of a target representation and the queries it supports in polynomial time \cite{darwiche2002}. The question for CGT is what building it costs.

The ledger's experiment (\ledger{CGT-EXP-006}) built the automaton by deduplicating residual clause sets, under the natural variable order, for random 3-CNF near the satisfiability threshold and random 2-CNF:

```python run
import random, math
from cgtsdk.algorithms import solution_automaton

rng = random.Random(6)
for label, width, ratio in (("3-CNF, m/k=4.26", 3, 4.26), ("2-CNF, m/k=1.0", 2, 1.0)):
    row = []
    for k in (8, 12, 16, 20, 24):
        sizes = []
        for _ in range(5):
            cls = [tuple((v + 1) * rng.choice([1, -1]) for v in rng.sample(range(k), width)) for _ in range(round(ratio * k))]
            sizes.append(solution_automaton(k, cls)[2])
        row.append(sorted(sizes)[2])
    print(f"{label:16s} median automaton nodes for k=8..24: {row}")
```

```output
3-CNF, m/k=4.26  median automaton nodes for k=8..24: [47, 212, 875, 2835, 10855]
2-CNF, m/k=1.0   median automaton nodes for k=8..24: [36, 73, 174, 340, 1260]
```

The sizes grow quickly, but over this range an exponential fit and a polynomial fit of high degree describe the medians about equally well ($R^2 \approx 0.99$ and $0.98$ in the ledger's larger run, \ledger{CGT-OBS-011}). The data **cannot** decide the asymptotics, and the book makes no asymptotic claim from them. Two things can be said. First, 2-CNF automata grow too, more slowly: 2-SAT's linear-time algorithm does not come from a small solution grammar. Second, if a polynomial-size solution grammar could always be *built* in polynomial time, satisfiability would be in P (case 1 of \ref{prop:pnp}); whatever the asymptotics of these particular automata, the construction cost is where any claim must be checked. Known exponential lower bounds for decision-diagram representations of some formulas are part of the knowledge-compilation literature; connecting them precisely to this experiment is open (\ledger{CGT-OPEN-006}).

## Grammars whose size depends on numbers {#sec:pseudo}

Chapter 11's knapsack dynamic program is a grammar of subproblems with $\Theta(nW)$ productions, where $W$ is a *number* in the input. It is polynomial in the value $W$ and exponential in its length $\log_2 W$. Any claim that a grammar resolves a numerical NP-hard problem "in polynomial time" must say polynomial in *what*: an input of length $\ell$ can encode numbers as large as $2^\ell$.

## What survives {#sec:survives}

Within standard models, grammars do not change complexity classes. What this book has established instead is a set of **precise local results**: where a grammar's structure *is* a cheap algorithm (dense addressing, compiled words, restricted classes), where it is a disguised precomputation bounded by information content, and where it is a constraint whose cost can go either way. These are the results that a "challenge to the foundations" can honestly claim at present: not a new complexity class, but a sharper map of where grammatical structure becomes computational advantage and where it provably cannot.

::: exercise {#exr:14-1}
A colleague claims a "grammar-indexed SAT solver" answers every query in $\Oh(1)$ after loading a precomputed grammar. Which case of \ref{prop:pnp} applies? List the questions you would ask to decide.
:::

::: solution {of="exr:14-1"}
Ask: how large is the grammar as a function of the formula size (case 3 if exponential)? Is it computed from the formula, and how long does that take (case 1 if polynomial — then it is a P = NP claim)? Does it depend only on the formula's length (case 2, advice)? Is the solver restricted to a class of formulas (case 4)? And is "$\Oh(1)$" measured over growing inputs or on a fixed benchmark?
:::

::: exercise {#exr:14-2}
Prove the correctness of the 2-SAT criterion: the formula is unsatisfiable iff some variable $x$ lies in the same strongly connected component as $\neg x$ in the implication graph.
:::

::: exercise {#exr:14-3}
For the formula $(x_1 \vee x_2) \wedge (\neg x_1 \vee x_3) \wedge (\neg x_2 \vee \neg x_3)$, build the solution automaton by residual deduplication under the order $x_1, x_2, x_3$ and count its models.
:::

::: summary
- Each classical boundary touched by the program has been stated with its proof obligation; several outcomes are negative.
- Within standard models a grammar helps decide an NP-complete problem only as a polynomial algorithm (a P = NP claim), as polynomial advice (believed impossible), as an exponential table (retrieval), or through a restriction of the problem (\ledger{CGT-PROP-006}).
- 2-SAT is tractable by restriction; 3-SAT solution grammars grow quickly, and the data cannot decide how quickly.
- Grammar sizes that depend on numbers rather than lengths yield pseudo-polynomial, not polynomial, bounds.
- What survives are precise local results about mechanisms, not changes of complexity class.
:::
