# Release Checklist

Work through this list for every tagged release. An item is checked only if its command was run on the release commit and passed; write the outcome next to it. Status for **edition 0.1 (2026-10-08)**: ✅ verified in this session · ⬜ not done · ➖ not applicable yet.

## A. Science

- ✅ `python3 experiments/check_theorems.py`: all small-case theorem checks pass.
- ✅ `sh experiments/run_all.sh` exits 0, and `python3 experiments/verify_reproduction.py` reports identical counted fields in every result file.
- ✅ Every correction since the last release is in the errata table (`RESULTS.md` §D) and in `DECISION_LOG.md`, with nothing rewritten silently (E-001 … E-006, D-012 … D-025).
- ✅ Every result in the book carries an evidence status, and every ledger ID cited in the book is anchored in the ledger (enforced by the build).
- ✅ Negative results are present and linked: COUNTEREXAMPLES and Chapter 20 §"What did not survive".
- ⬜ Independent review of the "proved here" results (blocker B-4).
- ⬜ Novelty review of the candidate contributions (blocker B-3).

## B. Citations

- ✅ Every bibliography entry has a verification status and is cited, and every citation key resolves (enforced by the build).
- ✅ `LITERATURE_REVIEW.md` mirrors the bibliography's statuses.
- ⬜ [S] and [U] entries checked against the originals.

## C. Book build

- ✅ `cd book && npm ci && npm run build`: 0 integrity errors (LaTeX, labels, references, citations, ledger, glossary, statuses, objectives, exercises, summaries, placeholders, demos).
- ✅ `npm run examples`: every executed example reproduces its printed output (39/39).
- ✅ `npm test`: laboratory port agrees with the SDK fixtures (7/7).
- ✅ `node tools/linkcheck.mjs`: 0 broken internal links or anchors.
- ✅ `npm run pdf`: PDF exported with no element wider than the text block, and the committed copy in `book/site/downloads/` matches the sources (the build issues no staleness warning).
- ✅ Screenshot check (`tools/screenshot.mjs`) of every page at 1440px and 390px, light and dark: no console errors, failed requests or horizontal overflow. This ran before the feedback page was added; the feedback page was checked separately at desktop and mobile widths. A full pass on the release commit is still to be done.

## D. Software

- ✅ `cd sdk && python3 -m unittest discover -s tests`: all tests pass.
- ✅ The GaaS contract document matches the code (field names, error codes, limits).
- ✅ `book/data/` was regenerated from the current SDK (`npm run build` runs the export) and committed.

## E. Deployment

- ✅ Clean-copy build with exactly the commands in `vercel.json`, without Python on the PATH, gives the same `dist/` as the local build.
- ✅ Pages load under the production headers from `vercel.json` with no CSP violations: lab widgets mount, search works, feedback calls reach Supabase.
- ⬜ First Vercel deployment made by the owner, with the deployed URL spot-checked (home, a chapter, lab, PDF download, feedback form).
- ✅ Only the publishable Supabase key is in the repository (the build refuses secret and service-role keys).

## F. Backend (Supabase)

- ✅ Migrations in `supabase/migrations/` are applied to the hosted project.
- ✅ Security advisor: no findings.
- ✅ Access rules verified against the live API (insert allowed; reads of errata, privileged columns, updates and deletes denied; unreviewed checks hidden).
- ⬜ Setup test rows deleted from the dashboard (listed in `supabase/README.md`).

## G. Identity and claims

- ✅ Researcher identified as "Abed Kadaan, Computational Substrate Scientist and Principal Researcher"; no university appointment, affiliation, endorsement, peer review or independent verification is claimed.
- ✅ No claim to improve any search engine's or AI company's production system.
- ✅ No model identifiers in repository artifacts.

## H. Accessibility

- ✅ `lang`, landmarks, skip link, visible focus styles, MathML for every formula, and text alternatives for every laboratory widget.
- ⬜ Keyboard-only walkthrough of the laboratory and the feedback forms.
- ⬜ Screen-reader test, and a formal WCAG 2.2 AA audit with measured contrast in both themes.

## I. Release

- ⬜ Version number and edition updated in `book/content/book.json`, `book/package.json` and `sdk/pyproject.toml`.
- ⬜ Tagged commit; PDF attached to the release; archived copy (DOI) for 1.0.
- ✅ `PUBLICATION_STATUS.md` and `REPRODUCIBILITY_REPORT.md` updated from this session's output.
