# Publication Status

**Edition:** working edition 0.1 (2026-10-08, end of session 2).
**Verdict:** a complete, internally verified **research manuscript and software release candidate**. It is **not** a peer-reviewed publication, and it is not ready for submission to a journal or press until blockers B-3 and B-4 are cleared.

This file is updated by hand at the end of each session from verified command output (`REPRODUCIBILITY_REPORT.md`). The website's status page summarizes it.

## 1. What exists and has been verified

| Deliverable | State | Evidence |
|---|---|---|
| Book as a website | 20 chapters + 2 appendices in 8 parts; about 41,000 words; 48 numbered formal items; 74 exercises; 39 executed examples; theorem index; glossary (34 terms); bibliography (55 entries, all cited); full-text search; ledger pages; laboratory; SDK and GaaS pages; researcher and status pages | `npm run build`: 0 integrity errors; link check: 1,838 links, 0 broken |
| Print edition (PDF) | 152 A4 pages, generated from the same sources | `npm run pdf`: page-width check passed; sample pages inspected visually |
| Mathematical rendering | KaTeX at build time, HTML + MathML; any error fails the build | deliberate-error test (MATHEMATICAL_RENDERING.md §1) |
| Interactive laboratory | 9 widgets computing live: array vs list, dynamic array, tree addresses, compiled words, regex → DFA, product construction, PageRank with certificates, sorting, break-even | `npm test`: 7/7 suites against SDK fixtures |
| SDK `cgtsdk` 0.1.0 | standard library only; 12 structures; classical algorithms; addressing; sharing; PageRank; SAT baselines; lab; GaaS | 56 tests OK |
| GaaS contract `cgt-gaas/0.1` | specification + local reference server | `test_service.py`; GRAMMAR_AS_A_SERVICE.md |
| Research results | THM-001 … THM-008; PROP-001, -002, -005, -006, -008, -009, -010 (003, 004 and 007 are unassigned; session-1 code comments cite 003 and 007 without a ledger definition, erratum E-006); EXP-001 … EXP-010; OBS-001 … OBS-018; negative results NEG-001 … NEG-016 | theorem checks and `verify_reproduction.py`: counted fields identical in all 10 result files |
| PageRank case study | Chapters 15–16 (first principles; grammatical view, including what it does *not* improve) | executed examples; EXP-009, EXP-010 |
| AI-systems chapter | Chapter 17 (computation graphs, attention masks, retrieval, vector search, agent plans) | executed examples; no empirical claims about production systems |
| Deployment | Vercel-ready from the repository root (`vercel.json`), with security headers and a strict CSP; PDF published under `/downloads/` | clean-copy build without Python matches the local build; no CSP violations under production headers |
| Reader feedback (optional) | Supabase project with insert-only errata and independent-check tables and RLS; feedback page, a link in every chapter, and a reviewed-checks list on the status page | access rules tested against the live API; security advisor clean; end-to-end browser submission |
| Responsive, light/dark | desktop 1440px and mobile 390px, light and dark, all pages | screenshot check: no console errors, failed requests or horizontal overflow |

## 2. Publication blockers

| ID | Blocker | Status |
|---|---|---|
| B-1 | No book, site, SDK or rendering pipeline | **cleared** (§1) |
| B-2 | References not in a maintained bibliography with verification status | **cleared**: 55 entries, 46 metadata-verified, 8 secondary-only, 1 unverified (Khoussainov–Nerode 1995); none read in full text |
| B-3 | Novelty of the framing and of the candidate contributions unreviewed against the closest prior art | **open**: automatic structures and transition monoids (THM-006); probabilistic model checking and meta-path ranking (PROP-010); attribute grammars and Kleene algebra with tests (framing). OPEN-010, OPEN-011 |
| B-4 | No external review of any proof | **open**: every "proved here" result is self-checked, and the small-case ones exhaustively by computation |
| B-5 | PageRank, AI and GaaS content missing | **cleared** |

## 3. Honest limits of this edition

- The research and its formalization were carried out with AI assistance, under the researcher's mandates. The provenance record states the origin of every item.
- Most proved results are elementary, and several are probably folklore; the book says so wherever it applies.
- Experiments are at modest sizes (n ≤ 65,536; SAT k ≤ 28). Wall-clock times come from Python and are secondary data.
- The constrained surfer (PROP-010) is a proposed model with no evaluation on real relevance data.
- Accessibility: there is MathML, landmarks, a skip link and focus styles. **No** screen-reader testing or formal WCAG audit has been done.
- The GaaS server is a local reference implementation with no authentication. No hosted service exists.
- Nothing claims to improve any search engine's production system, and no university appointment, affiliation, endorsement or peer review is claimed.

## 4. Next steps

See `PUBLICATION_ROADMAP.md`.
