# Computational Grammar Theory: research workspace

A research program formulated by **Abed Kadaan**. The question: can the grammar of a computational structure, meaning its valid operations, transitions, paths and resolutions, become part of the machinery that computes over it, and under what precise conditions does that give a computational advantage?

This repository is the **discovery-phase ledger**. It is not a product and not yet a book.

## Session 1 findings in brief
- **Object.** An *operational grammar* G = (Σ, 𝔄, ⟦·⟧, ℒ): moves, relational semantics on a structure, and an admissibility language. A *structural grammar* generates the structure itself. See `DEFINITIONS.md`.
- **What it can do.** Its semantics is compositional, so paths really are grammatical objects (PROP-001). In practice it drives computation through five mechanisms: arithmetic addressing, precomputation, sharing, class restriction and pruning (DEF-009).
- **What it costs.** Tight bounds and counterexamples for each mechanism:
  - arithmetic addressing is O(1) only when tree height is O(w) (THM-003);
  - retrieval-only reachability needs n²/4 bits (THM-002);
  - constraints can cost a factor |Q| or save an unbounded factor (THM-001);
  - grammar shape trades work against parallel depth (THM-004);
  - sharing is destroyed by updates (THM-005);
  - grammars cannot move problems across the P/NP boundary within standard models (PROP-006).
- **What is new.** Most results are elementary or known. The candidate contribution is the unified framing plus the mechanism thesis (CONJ-001), and that is pending deeper review. See `PROVENANCE.md`.

## Navigate
`RESEARCH_CHARTER.md` · `DEFINITIONS.md` · `FORMAL_MODELS.md` · `HYPOTHESES.md` · `RESULTS.md` · `COUNTEREXAMPLES.md` · `EXPERIMENTS.md` · `LITERATURE_REVIEW.md` · `OPEN_PROBLEMS.md` · `PROVENANCE.md` · `BOOK_OUTLINE.md` · `DECISION_LOG.md`

## Reproduce
```sh
sh experiments/run_all.sh     # Python ≥ 3.10, stdlib only, ~1.5 min, deterministic
cat experiments/results/SUMMARY.md
```
