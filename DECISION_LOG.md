# Decision Log

| ID | Date | Decision | Reason |
|---|---|---|---|
| CGT-D-001 | 2026-10-08 | The workspace was empty. Initialized the full ledger structure required by the mandate. | Mandate Step 1. No other directories were inspected. |
| CGT-D-002 | 2026-10-08 | The first formal object is the *operational grammar* (moves + relational semantics + admissibility language). Structural grammars are a separate, second object. | It covers paths, navigation, state transitions and addresses with one definition. It reduces to well-studied theory (LTS, regular path queries), so novelty claims can be checked. |
| CGT-D-003 | 2026-10-08 | Primary experimental metric: counted elementary steps under a stated cost model. Wall-clock time is secondary. | CPython constants would hide asymptotic behaviour. The mandate forbids inferring O(1) from flat timings. |
| CGT-D-004 | 2026-10-08 | Python standard library only. No numpy or matplotlib. Tables instead of plots. | Self-containment and reproducibility. matplotlib was not installed. Plots are deferred to the website phase. |
| CGT-D-005 | 2026-10-08 | Web search used to verify bibliographic metadata of the key references. Unverified references are marked [U]. | Mandate §27: do not invent citations. Verify before publication. |
| CGT-D-006 | 2026-10-08 | Added a *deep-pair* adversarial workload to EXP-001 after the first run. | The first run showed address-word LCA at 2 ops/query, an artifact of random pairs diverging near the root. Kept as REJ-002. |
| CGT-D-007 | 2026-10-08 | Added a root-level prefix-sum index to forest rank access in EXP-004 after the first run. | The first run's 512 ops/query came from linearly scanning 1,000 roots, not from the grammar. The fair comparison needs the forest-level index. |
| CGT-D-008 | 2026-10-08 | EXP-007 reports two depth notions: semi-naive (Gauss–Seidel) rounds were replaced by synchronous (Jacobi) parallel depth for THM-004(c). | The first implementation made facts visible within a round, which understated parallel depth (2 rounds for any n). |
| CGT-D-009 | 2026-10-08 | Part VI of the mandate (P vs NP) is answered by a boundary proposition (PROP-006) plus one exploratory experiment (EXP-006), not by attempting a separation. | Mandate §15: rigorous boundaries are results. No claim about P vs NP is made. |
| CGT-D-010 | 2026-10-08 | Removed a drafted counterexample row claiming that grammar-based methods were always slower in wall-clock time. | Not checked against the raw data. Unverified claims are not recorded. |
| CGT-D-011 | 2026-10-08 | Next session's priority: OPEN-002 (dense arithmetic addressing, via automatic structures) and the literature debts (OPEN-010). | THM-003 is the only mechanism found that needs zero preprocessing, and it is the closest formal counterpart of the originating address insight. |
