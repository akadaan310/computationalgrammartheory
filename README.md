# Computational Grammar Theory

*Structure, Operation, and the Cost of Resolution*: an open research program and textbook by **Abed Kadaan**, Computational Substrate Scientist and Principal Researcher.

> Can the grammar of a computational structure (its admissible operations, transitions, paths and resolutions) become part of the machinery that computes over it? And exactly when does that change what computation costs?

This repository contains:

| Part | Where | What |
|---|---|---|
| **The book (website)** | `book/` | 20 chapters + 2 appendices, theorem index, glossary, bibliography, interactive laboratory, SDK and GaaS reference, research ledger; KaTeX math rendered at build time; light and dark themes; responsive |
| **Print edition** | `book/site/downloads/computational-grammar-theory.pdf` | 152-page A4 PDF built from the same sources |
| **SDK** | `sdk/` | `cgtsdk`, Python ≥ 3.10, standard library only: operational grammars, cost accounting, structures, algorithms, PageRank, a GaaS reference server |
| **Research ledger** | repository root (`RESULTS.md`, `DEFINITIONS.md`, …) | the canonical scientific record: definitions, theorems, experiments, counterexamples, open problems, provenance, decisions |
| **Experiments** | `experiments/` | EXP-001 … EXP-010, deterministic and reproducible |
| **Reader-feedback backend** (optional) | `supabase/` | insert-only errata and independent-check submissions, with row-level security |

**Status:** a working research manuscript (edition 0.1). It is **not peer reviewed**: results marked "proved here" are self-checked and await independent review. No university appointment, affiliation or endorsement is claimed. See `PUBLICATION_STATUS.md`.

## Deploy the book on Vercel

The repository deploys as-is. The website (the academic book) is the default output.

1. In Vercel: **Add New… → Project → Import** this GitHub repository.
2. Leave **Root Directory** empty (the repository root). `vercel.json` sets everything else:
   - install: `cd book && npm ci`;
   - build: `cd book && npm run build:site`;
   - output: `book/dist`;
   - no framework preset.
3. Click **Deploy**. No environment variables are required.

Optional environment variables:

| Variable | Effect |
|---|---|
| `CGT_SUPABASE_URL`, `CGT_SUPABASE_PUBLISHABLE_KEY` | point the feedback forms at a different Supabase project (the default project is configured in `book/content/backend.json`) |
| `CGT_BACKEND=off` | build without the feedback backend; the forms then point to GitHub issues |

The deployment sends security headers, including a strict Content-Security-Policy that allows connections only to the site itself and `*.supabase.co`. Every build runs the full integrity gate: any LaTeX error, broken cross-reference, unknown citation or ledger ID fails the deployment instead of publishing a broken page.

**Updating the PDF.** Vercel cannot run Chromium, so the PDF is generated locally and committed:

```sh
cd book && npm run build && npm run pdf   # writes book/site/downloads/
git add book/site/downloads && git commit -m "Update print edition"
```

The build warns when the committed PDF is older than the sources.

## Build and verify locally

```sh
# book (Node ≥ 18; Python 3 for data export and example checks)
cd book && npm ci
npm run build        # export SDK data, build dist/ with integrity checks
npm run verify       # build + laboratory tests + executed examples + link check
node tools/serve.mjs  # serves dist/ at http://127.0.0.1:8080/

# SDK
cd sdk && python3 -m unittest discover -s tests

# research reproduction
sh experiments/run_all.sh && python3 experiments/verify_reproduction.py
```

See `REPRODUCIBILITY_REPORT.md` for the environment of record and the outcome of every command.

## Supabase (optional reader feedback)

- **Project:** `computational-grammar-theory` (ref `viyuzjhvjivhdvbrcnwh`).
- **Schema:** `supabase/migrations/`.
- **Workflow:** `supabase/README.md`; triage errata and publish reviewed checks from the Supabase dashboard.
- **New schema changes:** add a migration file and apply it with `supabase db push` or the Supabase MCP connector.

## Documents

| Topic | File |
|---|---|
| Publication | `PUBLICATION_STATUS.md` · `PUBLICATION_ROADMAP.md` · `PUBLICATION_AUDIT.md` · `RELEASE_CHECKLIST.md` |
| Book engineering | `BOOK_CONTENT_ARCHITECTURE.md` · `DESIGN_SYSTEM.md` · `MATHEMATICAL_RENDERING.md` |
| Software | `CGT_SDK_SPEC.md` · `GRAMMAR_AS_A_SERVICE.md` · `REPRODUCIBILITY_REPORT.md` |
| Research ledger | `RESEARCH_CHARTER.md` · `DEFINITIONS.md` · `FORMAL_MODELS.md` · `HYPOTHESES.md` · `RESULTS.md` · `COUNTEREXAMPLES.md` · `EXPERIMENTS.md` · `LITERATURE_REVIEW.md` · `OPEN_PROBLEMS.md` · `PROVENANCE.md` · `DECISION_LOG.md` · `BOOK_OUTLINE.md` |
