# Reproducibility Report

This report records what was rerun, in which environment, and with what outcome. A claim in the book or the ledger is called *reproducible* only if a command listed here regenerates it. Earlier runs are kept below; they are never rewritten.

## 1. Environment of record (session 2, 2026-10-08)

| Component | Version |
|---|---|
| OS / CPU | Linux 6.18 x86_64, 4 vCPU (cloud container) |
| Python | CPython 3.13.16. The SDK and experiments use only the standard library and require Python ≥ 3.10. |
| Node.js / npm | v22.22.0 / 10.9.4 (the book build requires Node ≥ 18) |
| Book packages | pinned exactly in `book/package.json`: katex 0.16.22, markdown-it 14.1.0, markdown-it-container 4.0.0, @fontsource 5.3.0 (Source Serif 4, IBM Plex Sans, JetBrains Mono); playwright-core 1.56.1 (dev) |
| Browser for PDF and screenshots | Chromium 141.0.7390.37 (headless), path set by the `CHROMIUM` environment variable |

## 2. Commands and outcomes

| # | Command (from the repository root unless stated) | What it checks | Outcome |
|---|---|---|---|
| R1 | `python3 experiments/check_theorems.py` | exhaustive small-case checks of THM-001(b), THM-002, THM-003, THM-004(c) (45 graphs), THM-005, THM-007 (all binary trees, n ≤ 11) | all pass |
| R2 | `sh experiments/run_all.sh` | R1, then EXP-001 … EXP-010, then `analyze.py` | exit 0, 2 min 15 s |
| R3 | `python3 experiments/verify_reproduction.py` | counted fields of every `experiments/results/exp0NN.json` against the committed files | **identical counted fields in all 10 files** |
| R4 | `cd sdk && python3 -m unittest discover -s tests` | SDK: adequacy of every structure against its reference semantics (random calls, including undefined ones), algorithm oracles, PageRank certificates, addressing, sharing, SAT, the GaaS contract and HTTP server | 56 tests, OK (22 s) |
| R5 | `python3 book/tools/check_examples.py` | every `python run` block in the book is executed, and its output must equal the printed output exactly | 39/39 reproduce |
| R6 | `cd book && npm test` | the browser laboratory's JavaScript port (`cgt-core.js`) against fixtures exported from the SDK | 7/7 suites pass |
| R7 | `cd book && npm run build` | site build with integrity checks (LaTeX, labels, references, citations, ledger IDs, glossary, status badges, placeholders, demos) | 22 chapters, 48 formal items, 251 labels, 55/55 references cited, 0 errors |
| R8 | `node book/tools/linkcheck.mjs` | every internal link and anchor in `dist/` | 1,838 links, 0 broken |
| R9 | `cd book && npm run pdf` | print edition generated from the same sources; fails if any equation, table, code block or figure is wider than the A4 text block | 152-page A4 PDF, about 1.9 MB, no over-wide element |
| R10 | `node book/tools/screenshot.mjs <out> <pages…>` | desktop and mobile, light and dark: console errors, failed requests, horizontal overflow | no errors on any page (after the fixes in §4) |

| R11 | clean copy of the tracked files; `cd book && npm ci && npm run build:site` with **no Python on the PATH** (the commands in `vercel.json`) | the Vercel build | exit 0; `dist/` byte-identical to the local build |
| R12 | pages served with the headers of `vercel.json` (CSP included) in Chromium | no CSP violations; lab widgets mount; search; feedback | no console errors or violations |
| R13 | REST calls with the publishable key against the Supabase project | the access rules of `supabase/migrations/` | insert 201; reading errata, privileged inserts and deletes denied; constraint violations rejected; only reviewed checks visible |

`cd book && npm run verify` runs R7, R6, R5 and R8 in sequence.

## 3. What is and is not reproducible

- **Bit-for-bit:** every counted cost, every theorem check, every example output and every SDK test. All random inputs come from fixed seeds. Hashing uses a fixed FNV hash, not Python's salted `hash`, so hash-table probe counts are stable across processes.
- **Not bit-for-bit:** wall-clock fields (`*_s`, `s_per_q`, `breakeven_Q_wall` and similar). They depend on the machine, are reported as secondary data only, and are excluded by `verify_reproduction.py`. Rerunning R2 rewrites these fields in `experiments/results/`. The committed files keep the wall-clock values of the run of record.
- **Built HTML** is deterministic for fixed sources and package versions. The PDF embeds a creation date, so its bytes differ between runs; its content does not.

## 4. Defects found by the reproduction tooling (all fixed and logged)

| Found by | Defect | Fix | Ledger |
|---|---|---|---|
| R3 (first version) | the verifier's suffix filter missed keys such as `M1.s_per_q` and wrongly flagged `exp002.json` | filter corrected | PUBLICATION_AUDIT §1.2 |
| R5 | the recursive BST overflowed the recursion limit on 1,023 sorted keys | iterative insertion and deletion, plus a regression test with 5,000 sorted keys | D-018 |
| R5 | several hand-predicted example outputs in the draft chapters were wrong | outputs regenerated by execution; prose corrected where it had drawn conclusions from the wrong numbers | D-019 |
| R7 | duplicate section labels, a ledger anchor regex that missed headings with inline tags, two uncited references | labels renamed, regex fixed, references cited where used | D-020 |
| R8 | 215 broken links: `../` prefixes in the print edition; DEF-011 anchored in the results ledger, not the definitions ledger | links resolve to the page where an ID is actually anchored; prefixes rewritten | D-020 |
| R9 | the first PDF clipped 36 code blocks and one equation at the right margin | code wraps in print, display math is set at 95 %, and the export now checks widths | D-022 |
| R10 | horizontal overflow on mobile: chapter tables without a scroll wrapper, KaTeX MathML escaping scroll containers, non-wrapping citation groups | tables wrapped, scroll containers made `position:relative`, citations allowed to wrap | D-021 |

## 5. Earlier runs

- **Session 2, initial audit:** R2 (session-1 version, 7 experiments) took 85 s and exited 0, and R3 reported identical counted fields in all 7 result files. See `PUBLICATION_AUDIT.md` §1.2.
- **Session 1:** R2 was introduced (see `EXPERIMENTS.md`).
