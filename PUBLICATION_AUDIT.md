# Publication Audit

This file holds the audit record for the CGT repository. §1 is the **initial audit** made at the start of session 2 (2026-10-08), before anything new was built. §2 records the state at the end of session 2. Later audits are appended; earlier ones are never rewritten.

---

## 1. Initial audit (session 2 start)

### 1.1 Repository inventory

| Item | State at audit |
|---|---|
| Branch | `ccr-04ad16b1-q42wck`, 1 commit (`1221dec`), clean working tree, in sync with `origin` |
| Tracked files | 36: 13 ledger documents, 4 library modules (`experiments/cgt/`), 7 experiments, `check_theorems.py`, `analyze.py`, `run_all.sh`, 7 result JSON files, `SUMMARY.md`, `.gitignore` |
| Dependencies | Python ≥ 3.10, standard library only. No lockfile needed. |
| Tests | None as a test suite. `check_theorems.py` performs exhaustive small-case checks. Every experiment asserts cross-method agreement. |
| Book, site, SDK | Not present. Only `BOOK_OUTLINE.md` existed. |

### 1.2 Reproduction status

Command: `sh experiments/run_all.sh`. Environment: CPython 3.13.16, Linux 6.18 x86_64, 4 vCPU. Exit code **0**, wall time 85 s. All theorem checks passed.

To check determinism, `experiments/verify_reproduction.py` (new; it compares counted fields with the committed JSON and ignores wall-clock fields) reported **identical counted fields in all 7 result files**. The first version of the verifier wrongly flagged `exp002.json`: its suffix filter missed keys of the form `M1.s_per_q`. That was a defect in the new tool, which is now fixed, not in the experiments. Full detail: `REPRODUCIBILITY_REPORT.md`.

### 1.3 Mathematical review

Every proof in `RESULTS.md` was re-read against its statement. Findings:

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| E-001 | **medium** | THM-004(c) stated parallel depth "ℓ (+1)" for the right-linear grammar. The measured data (63 rounds at ℓ = 63) contradict it. The correct count is ℓ − 1 productive rounds + 1 confirming round. ℓ also needed to be defined as the largest shortest *positive-length* distance, so that cycles count. | Statement corrected. `check_theorems.thm004c` now verifies the corrected statement *exactly* on 45 graphs. |
| E-002 | low | THM-001(a) omitted the \|Σ\|·n term that comes from consulting δ for every letter. | Bound corrected. |
| E-003 | low | COR-002b asserted the information content of forests without showing that the answer function is injective. | One-line justification added: the ancestor relation determines the parents. |
| E-004 | low | PROP-006(2) attributed the second-level collapse to Karp–Lipton alone. | Attribution qualified (Sipser's improvement). |
| E-005 | **medium** (evidence status) | OBS-001 reported a constant "measured" word-op count for heap-arithmetic LCA. That count is *assigned by the cost model*, so it is constant by construction. | Re-labelled. Wall-clock time is the independent evidence. |
| — | note | THM-003(a): msb(0) was undefined in the LCA formula. | Convention msb(0) = −1 added. |

No proof was found to be wrong in a way that invalidates its theorem. All corrections are listed in `RESULTS.md` §D, and the original text is preserved in git history.

### 1.4 Experimental limitations (carried forward)
- Python constants dominate wall-clock time, so only counted steps support asymptotic claims.
- Sizes are modest: n ≤ 65,536, and k ≤ 28 for SAT.
- EXP-006 does not decide its own question (OBS-011).
- EXP-001 uses the O(n log n) sparse table, not the linear-time LCA structure.
- EXP-004 implements minimal DAGs only, not tree SLPs.
- Random-query workloads favour early-exit search. Adversarial workloads exist only in EXP-001 and EXP-005.

### 1.5 Literature debts at audit time
- 14 references marked [U].
- No primary paper had been read in full; verification was metadata-level only.
- Attribute grammars, graph grammars, term rewriting, model checking, PageRank and AI systems were not reviewed at all.

Session 2 verified bibliographic metadata for 30 further references (see `book/content/bibliography.json`, where each entry records how it was verified). Full-text reading of primary sources remains a debt.

### 1.6 Novelty uncertainties
Every proved result is elementary, and several are probably folklore: THM-001(b,c), THM-002, THM-004(a), THM-005. The candidate contribution, the unified framing plus the mechanism thesis CONJ-001, has **not** been compared against the literatures most likely to contain it:
- attribute grammars;
- Kleene algebra with tests;
- automatic structures;
- the knowledge-compilation map;
- cost semantics.

This is publication blocker B-3.

### 1.7 Required corrections
E-001 to E-005 (done).

### 1.8 Recommended research priorities (from the evidence)
1. OPEN-002, arithmetic addressing beyond trees. It is the only zero-preprocessing mechanism, and it is the closest test of the founding insight.
2. A PageRank study as the applied case. It is required by the mandate, and THM-001's product construction extends naturally to *language-constrained random walks*.
3. Literature review of the closest prior art for the framing (B-3).
4. OPEN-005, whether grammar-parameterized notation carries content.

### 1.9 Publication blockers identified at audit
| ID | Blocker |
|---|---|
| B-1 | No book, site, SDK or rendering pipeline exists. |
| B-2 | References are not in a maintained bibliography with verification status. |
| B-3 | Novelty of the framing is unreviewed against the closest prior art. |
| B-4 | No external review of any proof. Every result is "self-checked". |
| B-5 | PageRank, AI and GaaS content does not exist. |

---

## 2. End-of-session-2 status

See `PUBLICATION_STATUS.md` for the current state of each blocker and each completion criterion of the mandate. That file is regenerated by hand at the end of each session from verified build and test output.
