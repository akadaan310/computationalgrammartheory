# Book Outline (provisional, revised from the evidence)

**Working title:** *Computational Grammar Theory: Structure, Operation, and the Cost of Resolution*
**Author of the research program:** Abed Kadaan

> **Superseded (session 2).** The book now exists: its structure is `book/content/book.json` (8 parts, 20 chapters, 2 appendices), described in `BOOK_CONTENT_ARCHITECTURE.md`. This file is kept unchanged below as the session-1 planning record.

**Status (session 1):** outline only. The book is not written until the exit criteria in `RESEARCH_CHARTER.md` §5 hold. Sections marked ◻ have no supporting results yet. Sections marked ◐ have partial results. Sections marked ● have results in the ledger.

The session-1 evidence changes the mandate's provisional outline in one main way. The book's spine is now **the mechanism account** (DEF-009): grammar as the explicit vehicle through which five mechanisms of computational advantage act, each with a cost profile and a failure family.

## Part I: The Problem of Structure
1. ● Structures, representations and operations (DEF-001/002); why the representation is not the structure (OBS-010).
2. ● Three questions kept separate: validity, meaning, cost (FORMAL_MODELS §2, PROP-002).
3. ● The originating question and its history (PROVENANCE).

## Part II: Grammar as a Computational Object
4. ● Operational grammars (DEF-003); compositional semantics (PROP-001).
5. ● Structural grammars (DEF-004): DAGs, SLPs, graph grammars.
6. ◐ Addresses and numerations (DEF-006); relation to automatic structures (LIT §7).
7. ◐ Transition monoids and compiled operations (DEF-007, OPEN-003).

## Part III: A Taxonomy of Structural Grammars
Provisional table, to be filled in by session 2+ experiments.

| Family | Natural moves Σ | Admissibility ℒ | Arithmetic address? | Sharing grammar | Main mechanism observed | Evidence |
|---|---|---|---|---|---|---|
| Arrays | ±1, jump +k | Σ* within bounds | yes, dense (δ = 1) | n/a | M-ARITH (the array index *is* the address) | standard |
| Linked lists | next, prev | Σ* | no (pointer chasing); order-maintenance labels exist [U] | SLP over values | M-PRE (rank index) | ◻ |
| Stacks/queues/deques | push/pop/… | well-bracketed (Dyck) for stacks | — | — | ℒ context-free | ◻ (OPEN-008) |
| Binary/complete trees, heaps | L, R, U | Σ* | **yes iff h = O(w)** | minimal DAG | M-ARITH / M-PRE | ● THM-003, EXP-001 |
| BSTs (balanced) | L, R, U, rotations | invariant-preserving | dense only if near-complete | — | M-PRE; rotations break addresses | ● THM-003(d) |
| Tries | one move per symbol | the key language | yes when the alphabet is fixed and the trie is complete | DAWG / minimal automaton [U] | M-SHARE | ◻ |
| Forests | root-select + tree moves | Σ* | via interval labels | minimal DAG, TSLP | M-RESTRICT, M-SHARE | ● COR-002b, THM-005, EXP-004 |
| Digraphs | edge labels | regular / CF | no in general | — | M-PRE (bounded by THM-002), M-PRUNE | ● THM-001/002/004 |
| Hypergraphs, temporal, dynamic graphs | — | — | — | — | — | ◻ |
| Finite-state machines | input symbols | Σ* | states are addresses (transition monoid) | minimization | M-SHARE (minimization), compiled words | ◻ (OPEN-003) |
| Pushdown, Petri nets | — | CF / Petri languages | — | — | — | ◻ |
| Hash tables, B-trees, Fenwick/segment trees | probe, descend | — | Fenwick trees use arithmetic addressing [U] | — | M-ARITH (Fenwick), M-PRE | ◻ (EXP-008 candidate) |
| Strings, rewriting systems | rewrite rules | — | — | SLPs | M-SHARE | ◐ (literature only) |

## Part IV: Operational Semantics and Path Composition
8. ● Paths as grammatical objects (PROP-001, Tarjan's path expressions).
9. ● Constrained resolution and the product construction (THM-001).
10. ● Same semantics, different grammar, different cost (THM-004).
11. ◐ Witnesses and output-sensitive retrieval (NEG-011, OPEN-009).

## Part V: Complexity and Computational Cost
12. ● Cost profiles and grammar-parameterized notation (FORMAL_MODELS §3); its limits (OPEN-005).
13. ● Retrieval vs discovery: the information lower bound (THM-002).
14. ● Preprocessing, repeated queries, break-even (PROP-005, OBS-004).
15. ● Dynamic grammars and update inflation (THM-003d, THM-005, EXP-005).
16. ● The P/NP boundary: what grammars cannot do (PROP-006, REJ-001).

## Part VI: Experimental Investigation
17. ● Methodology: counted steps, adversarial workloads, falsification criteria (EXPERIMENTS).
18. ● Results of EXP-001 … EXP-007, including negative findings (COUNTEREXAMPLES).

## Part VII: Formal Results
19. ● Collected definitions, theorems, proofs and counterexamples. Open problems.

## Part VIII: Applications and Research Directions
Each item is admitted only when a demonstrated result supports it:
- ◐ Graph databases and program analysis: constrained reachability (THM-001; Reps 1998).
- ◐ Compressed tree stores (THM-005 limits them).
- ◻ Compilers (attribute grammars: review pending), formal verification (typestate as admissibility languages).

## Part IX: The Interactive Presentation (design deferred)
Requirements derived from the science so far (not to be built yet):
- each theorem page links its proof, its experiment JSON and its counterexample family;
- structure explorer showing the three layers side by side for one expression (valid? denotes what? costs what?);
- break-even calculator driven by PROP-005 with the measured constants;
- product-construction visualizer for THM-001(b) (the CRT orbit).
