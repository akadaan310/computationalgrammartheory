---
title: What Computational Grammar Theory Has Established
status: mixed
statusnote: A summary of the evidence of this edition, with every claim traced to the ledger. It will change as the research does.
description: The confirmed contributions, the negative results, the open questions and the research agenda — without inflating any of them.
---

::: objectives
- Summarize, for each of the four founding questions, what this edition has established and how firmly.
- Separate candidate contributions from restatements of known results.
- List the negative results that bound the theory.
- Identify the research that most deserves independent review, collaboration and publication.
:::

## The four questions {#sec:four}

The research program set itself four questions. Here are the answers this edition can defend.

**1. What is the object?** An *operational grammar* $G = (\Sigma, \Str, \sem{\cdot}, \Lang)$: moves with relational semantics on a computational structure, constrained by an admissibility language over the projection of move words, executed by representations whose adequacy is checkable and whose costs are reported as profiles in an explicit machine model (\ledger{CGT-DEF-003}, \ledger{CGT-DEF-005}). Alongside it, *structural grammars* generate the structure itself (\ledger{CGT-DEF-004}). The components are standard — labelled transition systems, relational semantics, formal languages, abstract data types — and the book says so (Chapter 7). The definition's value is that it covers every structure of Part I in one format while keeping syntax, semantics and execution apart.

**2. What can it do?** Its semantics is compositional, so paths, navigations, plans and histories really are grammatical objects (\ledger{CGT-PROP-001}). Grammars drive computation through product constructions for constrained search (\ledger{CGT-THM-001}), fixpoint evaluation of path grammars (\ledger{CGT-THM-004}), arithmetic evaluation of addresses (\ledger{CGT-THM-003}), compilation of move words (\ledger{CGT-THM-006}), sharing (\ledger{CGT-THM-005}), and validation of plans before execution (Chapter 17). They also define new models — the grammar-constrained random surfer — with costs derived from the general constructions (\ledger{CGT-PROP-010}).

**3. What does it cost?** Every capability above has a cost profile and a failure family:

| Capability | Best case | Failure family | Ledger |
|---|---|---|---|
| arithmetic addressing | $\Oh(1)$ navigation, no index | deep or sparse shapes; rotations relabel subtrees | THM-003, NEG-001–003 |
| compiled move words | $\Oh(\lvert w \rvert)$ once, then $\Oh(1)$ per application | arbitrary shapes need $\lfloor n/2 \rfloor$ bits per move | THM-006, THM-007 |
| precomputed answers | $\Oh(1)$ retrieval | $\lfloor n/2\rfloor\lceil n/2\rceil$ bits for reachability; break-even $Q^*$; updates | THM-002, PROP-005 |
| sharing | exponential compression | $\Theta(k \log n)$ inflation after $k$ updates; wrong kind of repetition | THM-005 |
| admissibility constraints | prune to one state | multiply work by exactly $\lvert Q \rvert$ | THM-001 |
| path grammars | correct by construction | evaluation *is* closure computation; shape changes cost | THM-004 |

**4. What has actually been discovered?** Separated honestly:

- *Candidate contributions, novelty not yet verified.* The constant-size normal form for move words in heap-shaped trees with its interval domain, together with the matching impossibility result for arbitrary shapes (\ledger{CGT-THM-006}, \ledger{CGT-THM-007}). The grammar-constrained random surfer as a ranking model (\ledger{CGT-PROP-010}). The unified discipline — operational grammars, three layers, cost profiles, and the five-mechanism account of where grammatical advantage comes from — together with the *mechanism thesis* that these five account for all of it (\ledger{CGT-CONJ-001}, a conjecture).
- *Elementary results proved here that are probably folklore.* The tight factor-$\lvert Q\rvert$ cost of constraints, the exact information bound for retrieval-only reachability, the exact work count of right-linear path-grammar evaluation, update inflation of shared trees, break-even under invalidating updates, the exact cost of doubling arrays under this book's cost model.
- *Known results restated in CGT terms.* Compositional semantics, product constructions, heap numbering and LCA, PageRank's convergence theory, the comparison lower bound, the P/NP boundary for grammar-based claims.
- *Empirical findings.* Eighteen reproducible observations, among them the break-even range from 4 to 27,000 queries, four different winning strategies across nine dynamic workloads, Gauss–Seidel's dependence on vertex order, and solution-grammar growth for SAT that the data cannot classify.

## What did not survive {#sec:negative}

The research began with an ambitious conjecture: that sufficiently expressive grammars might make problems dramatically easier, approaching constant-time resolution. In its strong form, this is rejected (\ledger{CGT-NEG-009}). Within standard models a grammar helps decide a hard problem only as an ordinary algorithm, as advice, as an exponential table or through a restriction of the problem (\ledger{CGT-PROP-006}). Several weaker hypotheses also failed and are kept in the ledger: address-word LCA as a competitive method, Gauss–Seidel as a generally faster PageRank solver, and constraints as a generally pruning device. Each failure sharpened a boundary that now appears as a theorem or a counterexample.

## Where grammar becomes advantage {#sec:concl-where}

Gathering the positive results, one pattern recurs across arrays, ring buffers, heaps, Fenwick trees, grids, hypercubes, de Bruijn graphs and compiled words: **grammatical structure becomes computational advantage when the meaning of a move is determined by a small number of parameters of the structure, so that sentences of the grammar can be evaluated — or compiled — by arithmetic instead of by traversal.** When the structure itself carries the information, as in arbitrary shapes, the advantage must instead be bought with stored information, and the counting lemma prices it. This is the most precise answer this edition can give to the question with which the program began. Turning it into a theorem is open problem \ledger{CGT-OPEN-012}.

## Research agenda {#sec:agenda}

In order of priority:

1. **Independent review** of the proofs marked "proved here", starting with \ledger{CGT-THM-006} and \ledger{CGT-THM-007}.
2. **Literature review for novelty** of the compiled-word normal form (implicit tree navigation, transition monoids, automatic structures) and of the constrained surfer (probabilistic model checking, meta-path ranking) (\ledger{CGT-OPEN-010}, \ledger{CGT-OPEN-011}).
3. **Characterize compilable classes** (\ledger{CGT-OPEN-012}): Cayley graphs of groups with efficient word problems are the natural next family.
4. **Context-free admissibility**: the cost-of-constraint theory for CFL-reachability (\ledger{CGT-OPEN-008}).
5. **Formalize the mechanism thesis** (\ledger{CGT-OPEN-001}) so that it becomes a theorem or is refuted.
6. **Evaluate constrained rankings** on corpora with relevance judgments, which requires collaboration and data this program does not have.

Results that pass review would be candidates for publication: the compilation theorems as a short note on implicit navigation, and the constrained surfer, if novel and useful, as an applied paper. Until then, the book's status remains what its front page says: an unreviewed research manuscript, with every claim labelled by the evidence behind it.

::: exercise {#exr:20-1}
Pick one result marked "proved here" and review its proof as an independent referee would: check every step, look for missing hypotheses, and search for prior work. Write a short referee report.
:::

::: exercise {#exr:20-2}
Propose a sixth mechanism of advantage not covered by \ref{def:mechanisms}, or argue that a candidate (caching, partial evaluation, parallelism, incremental maintenance) reduces to the five. What would count as a counterexample to the mechanism thesis?
:::

::: summary
- The object is the operational grammar with three separated layers and explicit cost profiles; its components are standard and its discipline is the contribution.
- Capabilities — addressing, compilation, precomputation, sharing, constraints, path grammars — each come with a cost profile and a proven failure family.
- Candidate contributions: compiled move words with a matching impossibility result, the grammar-constrained surfer, and the mechanism account; novelty awaits review.
- The strong founding conjecture is rejected; the surviving answer is that grammar becomes advantage when move semantics is fixed by few parameters, so sentences can be evaluated by arithmetic.
- The agenda: review, novelty search, characterization of compilable classes, context-free constraints, the mechanism thesis, and real-data evaluation.
:::
