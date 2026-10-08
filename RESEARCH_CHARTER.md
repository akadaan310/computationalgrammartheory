# Research Charter: Computational Grammar Theory (CGT)

**Researcher and originator of the research program:** Abed Kadaan
**Research collaborator for this phase:** Claude (AI research assistant), working in a fresh, self-contained environment
**Charter date:** 2026-10-08 (session 1)
**Status of the program:** discovery phase. Nothing here is a finished theory.

---

## 1. The question

Abed Kadaan formulated the program and its motivating conjecture (see `PROVENANCE.md`):

> Computational structures may have formal grammars through which they expose, constrain, compose and resolve their possible operations, transitions, paths and outcomes. Can such a grammar become part of the machinery that operates on the structure, and not only a description of it?

This charter turns that conjecture into four questions that can be checked:

1. **Object.** What is a computational grammar, mathematically, and how does it relate to a computational structure?
2. **Capability.** Which operations, derivations, transformations and queries does it support?
3. **Cost.** What are the time, space, preprocessing, update and output costs of those operations, under an explicit machine model?
4. **Novelty.** Which results are new? Which are established, which are only experimental, which are conjectures, and which are open?

## 2. Rules of the work

The rules follow the researcher's mandate:

- **Order.** Discovery comes first, then formalization, then experiment, then proof and falsification. A book comes last.
- **Grammar is not an algorithm.** A grammar can describe valid computations without making them cheaper. Every claimed advantage must name the *mechanism* that produces it.
- **Explicit cost model.** Results use the word RAM with word size *w* = Θ(log *n*) unless stated otherwise. Every bound names what grows and what is held constant. Build cost, storage cost, query cost, update cost and output size are reported separately.
- **Ladder of claims.** Every claim gets exactly one category: Definition, Conjecture, Proposition, Theorem, Corollary, Empirical observation, Engineering result, Open problem or Rejected hypothesis. Experiments never promote a conjecture to a theorem.
- **Counterexamples are first-class results.** Each claimed advantage is paired with the instances where it fails (`COUNTEREXAMPLES.md`).
- **No priority claims without literature review.** Results that are standard or folklore are labelled that way, even when this program restates them (`LITERATURE_REVIEW.md`, `PROVENANCE.md`).
- **No P vs NP claims.** The program makes no claim about P vs NP unless it has a complete, independently checkable proof. Part VI of the mandate is answered by a boundary result (`RESULTS.md`, CGT-PROP-006), not by speculation.
- **Self-containment.** No external repositories, websites or implementations are used. All experiments generate their own inputs, use only the Python standard library, and are deterministic given their seeds.
- **History is preserved.** Rejected hypotheses and negative results stay in the ledger. Revisions go in `DECISION_LOG.md`.

## 3. Workspace

| File | Purpose |
|---|---|
| `RESEARCH_CHARTER.md` | this document |
| `DEFINITIONS.md` | provisional definitions (CGT-DEF-xxx) |
| `FORMAL_MODELS.md` | machine and cost models, the three-layer separation, notation for grammar-parameterized cost |
| `HYPOTHESES.md` | hypothesis ledger (CGT-H-xxx), with status |
| `LITERATURE_REVIEW.md` | related fields, verified references, what CGT adopts, changes or adds |
| `EXPERIMENTS.md` | experiment protocols (CGT-EXP-xxx) and interpretations |
| `RESULTS.md` | propositions and theorems with proofs, empirical observations (CGT-PROP/THM/OBS-xxx) |
| `COUNTEREXAMPLES.md` | failure cases (CGT-NEG-xxx) |
| `OPEN_PROBLEMS.md` | open questions (CGT-OPEN-xxx) |
| `PROVENANCE.md` | who contributed what, and the status of each result relative to prior work |
| `BOOK_OUTLINE.md` | provisional book outline, revised from the evidence |
| `DECISION_LOG.md` | dated methodological decisions |
| `experiments/` | reproducible code (`run_all.sh`), raw JSON results, `results/SUMMARY.md` |

## 4. Identifier convention

Identifiers are an organizational convention, not a mathematical requirement:
`CGT-DEF-nnn` (definition), `CGT-H-nnn` (hypothesis), `CGT-CONJ-nnn` (conjecture), `CGT-PROP-nnn` (proposition), `CGT-THM-nnn` (theorem), `CGT-COR-nnn` (corollary), `CGT-OBS-nnn` (empirical observation), `CGT-EXP-nnn` (experiment), `CGT-NEG-nnn` (negative result or counterexample), `CGT-OPEN-nnn` (open problem), `CGT-D-nnn` (decision).

## 5. Exit criteria for the discovery phase

The book (`BOOK_OUTLINE.md`) is written in full only when all of the following hold:

1. The definitions are stable across at least two further rounds of experiment.
2. At least one result is non-trivial and correct, and its relationship to prior work is established by a literature check stronger than the one done in session 1.
3. Each claimed advantage has a stated mechanism, a cost profile and a counterexample family.
4. The open problems are stated precisely enough that a reader could attack them.
