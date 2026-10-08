# Publication Roadmap

The order of work from the current working edition (0.1) to an externally reviewable publication. Each stage has an exit criterion that someone other than the author can check. Dates are not promised; the order is.

## Stage 0: working edition 0.1 (done, session 2)

The book as a website, with its PDF, the SDK, the laboratory, the GaaS contract, a reproducible build and the ledger. State and evidence: `PUBLICATION_STATUS.md`.

## Stage 1: novelty review (clears blocker B-3)

1. Read in full text the closest prior art to each candidate contribution:
   - **Compiled move words (THM-006, THM-007).**
     - automatic structures: Khoussainov–Nerode 1995, which is still [U], and Blumensath–Grädel 2000;
     - transition monoids of tree automata;
     - implicit and succinct tree navigation: Jacobson 1989 and its successors;
     - folklore on heap index arithmetic.
   - **Constrained surfer (PROP-010).**
     - probabilistic model checking (Baier–Katoen, Chapter 10);
     - meta-path ranking (Sun et al. 2011);
     - topic-sensitive and personalized PageRank;
     - random walks constrained by regular languages.
   - **Framing (CONJ-001, DEF-003, DEF-009).**
     - attribute grammars (Knuth 1968);
     - Kleene algebra with tests (Kozen 1997);
     - the knowledge-compilation map (Darwiche–Marquis 2002);
     - cost semantics.
2. For each candidate, record one of four outcomes in `PROVENANCE.md` and the book: *known (with citation)*, *known in a different form*, *apparently new*, or *undetermined*. Downgrade the claim wherever the outcome is "known".
3. Resolve the [S] and [U] bibliography entries against the originals.

**Exit:** OPEN-010 and OPEN-011 are closed with written conclusions, and every bibliography entry cited for a substantive claim is [V].

## Stage 2: independent proof review (clears blocker B-4)

1. Ask at least one qualified reviewer, someone not involved in the work, to check THM-006, THM-007 and THM-008, plus the counting and break-even results THM-002 and PROP-005. Book Exercise 20.1 is the reviewer's template.
2. Record each review in the ledger: reviewer (with their permission), date, scope, and the issues found and their resolution. Change a badge from "proved here" to "proved here, independently checked" only for the results actually reviewed.
3. Optional: formalize THM-006 in a proof assistant (Lean or Coq). The statement is finite-state arithmetic and well suited to it.

**Exit:** every result the book presents as a contribution has at least one recorded independent check.

## Stage 3: research completion for a first paper

1. Write a short paper on **compiled move words**: the normal form, interval domains, the matching lower bound via caterpillars, and the compilable classes of PROP-008. Do this only if Stage 1 finds it new; otherwise rewrite it as an expository note with correct attribution.
2. Evaluate the **constrained surfer** on a public corpus with relevance judgments, with predefined metrics and baselines, *if* Stage 1 leaves it worth pursuing.
3. Turn OPEN-012 (characterizing the compilable classes; Cayley graphs with efficient word problems) into either a theorem or a precise conjecture backed by evidence.

**Exit:** a manuscript that passes internal checks (`npm run verify`, `run_all.sh`, `verify_reproduction.py`) and states its novelty with citations.

## Stage 4: edition 1.0 of the book

1. Fold the outcomes of Stages 1–3 into the chapters. Every statement that changes is logged as an erratum, never rewritten silently.
2. Accessibility:
   - a formal WCAG 2.2 AA audit, including contrast measurements for both themes;
   - keyboard-only and screen-reader testing of the laboratory;
   - fixes for everything found.
3. External readers: students for Parts I–III, and practitioners for Parts V–VII. Revise from their exercise attempts.
4. Release with a fixed version number, a tagged commit, the PDF attached, and a permanent archive copy (for example, a DOI-issuing repository).

**Exit:** every item in `RELEASE_CHECKLIST.md` is checked for the tagged commit.

## Stage 5: services and agency work (optional, after 1.0)

- **Hosted GaaS** only with preemptive resource limits, authentication, per-client quotas and audit logging (GRAMMAR_AS_A_SERVICE.md §8), and with a privacy and data-retention statement.
- **Consulting** on representation and cost analysis, positioned only on demonstrated results, as described on the researcher page.

## What will not be on the roadmap

- Claims about P vs NP beyond the boundary results of Chapter 14.
- Claims about any company's production search or AI systems.
- Benchmarks without code and data in the repository.
