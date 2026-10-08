# Provenance Record

## Originator

**Abed Kadaan** formulated the Computational Grammar Theory research program, posed its foundational question, and supplied its motivating conceptual hypothesis.

The hypothesis grew out of Kadaan's work with grammatical representations of programmable URLs, computational transitions, persistent addresses and compositional computational experiences. In that work an address identified a state, described an operation, selected a transformation and preserved a history of transitions.

That work is treated here as the **historical and conceptual origin** of the question, not as evidence. None of its implementations were accessed or used. All models in this repository were defined independently.

## Contributors in this phase

- **Abed Kadaan**: research program, originating conjecture (H-000), research mandate, governance rules.
- **Claude (AI research assistant, session 1, 2026-10-08)**: provisional definitions, hypotheses H-001 to H-012, experiment design and code, proofs of the propositions and theorems below, and the literature baseline. All of it is subject to review.

## Classification of every result

| ID | Category | Origin | Relationship to prior work |
|---|---|---|---|
| H-000 | conjecture | **Kadaan** (original) | motivating; reformulated, see HYPOTHESES |
| DEF-001, 002, 007 | definition | standard | restated |
| DEF-003 operational grammar | definition | this investigation | packages labelled transition systems + admissibility language + cost model; no prior single source found (review incomplete) |
| DEF-004 structural grammar | definition | naming of standard objects | DAGs, SLPs, graph grammars |
| DEF-005 cost profile | definition | standard idea, CGT packaging | preprocessing/query trade-offs |
| DEF-006 address/numeration/density | definition | this investigation, inspired by **Kadaan's** address insight | special case of automatic presentations, plus cost and density |
| DEF-008 information content | definition | standard idea | counting arguments |
| DEF-009 mechanisms | definition (taxonomy) | this investigation | classification proposal |
| PROP-001 | proposition | standard | Kleene algebra; Tarjan 1981 |
| PROP-002 | proposition | examples from literature + trivial | Mendelzon–Wood; Bender–Farach-Colton |
| THM-001 (a) | theorem | **known** | Mendelzon–Wood 1995; Barrett–Jacob–Marathe 2000 |
| THM-001 (b), (c) | theorem | proved here | elementary; likely folklore |
| THM-002 | theorem | proved here | elementary counting; asymptotic version from Kleitman–Rothschild 1975; likely folklore |
| COR-002b | corollary | proved here, using Cayley's formula and Agrawal et al. 1989 | known index, new optimality remark (elementary) |
| THM-003 | theorem | components **classical** (attribution unverified), scope statement here | heap numbering; XOR-LCA |
| THM-004 (a) | theorem | exact count proved here | semi-naive evaluation is standard |
| THM-004 (b), (c) | theorem | standard | repeated squaring; Datalog folklore |
| PROP-005 | proposition | elementary | break-even accounting |
| THM-005 | theorem | proved here | elementary; DAG/TSLP context from Lohrey 2015 |
| PROP-006 | proposition | **standard** complexity theory restated | Karp–Lipton 1980; Aspvall–Plass–Tarjan 1979 |
| CONJ-001 mechanism thesis | conjecture | this investigation | none found |
| OBS-001 … OBS-012 | empirical | experiments here | n/a |
| NEG-001 … NEG-012 | negative results | this investigation | several instantiate known limitations |
| REJ-001 | rejected hypothesis | strong form of **Kadaan's** H-000 | rejected by PROP-006 |
| REJ-002 | rejected hypothesis | session-1 working assumption | rejected by EXP-001 deep workload |

## Session 2 additions (2026-10-08)

| ID | Category | Origin | Relationship to prior work |
|---|---|---|---|
| DEF-011 arithmetically compilable | definition | this investigation | cost-oriented specialization of transition monoids / automatic structures |
| THM-006 word compilation in heap-shaped trees | theorem | proved here; exhaustively checked | heap numbering classical (Williams 1964); normal form not found in the reviewed literature; **novelty unverified** |
| THM-007 no compact compilation on arbitrary trees | theorem | proved here | elementary counting |
| PROP-008 compilable de Bruijn / hypercube / grid moves | proposition | elementary | standard algebra |
| THM-008, PROP-009 PageRank contraction and iteration bound | theorem / proposition | **standard** | Page et al. 1999; Langville & Meyer 2004 |
| PROP-010 grammar-constrained surfer | proposition (model) | proposed here | Markov chain × automaton product is standard (model checking); close to meta-path measures (Sun et al. 2011); **novelty unknown** |
| SDK `cgtsdk` 0.1.0 | engineering result | implemented here | reference implementations of classical algorithms, each cited to its original source |
| GaaS contract `cgt-gaas/0.1` | engineering design | this investigation | — |
| OBS-013 … OBS-018, NEG-013 … NEG-016, REJ-003 | empirical / negative | experiments here | — |

## Priority statement

No claim of historical priority is made for any result in this repository. Most proved statements are elementary and some are probably folklore. The candidate contribution of the program so far is a **framing**: a unified operational-grammar notation, a cost-profile discipline that separates syntax, semantics and execution, and a five-mechanism account of where grammatical advantage comes from. Each piece is supported by precise boundary results and counterexamples. Whether this framing is new and useful has to be settled by a deeper literature review (`OPEN_PROBLEMS.md` OPEN-005, OPEN-010).
