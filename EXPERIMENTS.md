# Experiments

**Code version:** this repository, `experiments/` (git history is the version record).
**Environment of the recorded runs:** CPython 3.13.16, Linux x86_64 (4 vCPU, 15 GB RAM), standard library only.
**Reproduce everything:** `sh experiments/run_all.sh` (about 1.5 minutes). This writes `experiments/results/exp00N.json` and `experiments/results/SUMMARY.md`.
**Determinism:** every experiment uses a fixed seed. Counted steps are reproducible bit for bit. Wall-clock fields will vary by machine.
**Cost methodology:** primary dependent variables are *counted elementary steps* under the cost model in each file's docstring. Wall-clock time (median or mean via `time.perf_counter`) is secondary. Bitset operations cost ⌈n/64⌉ word operations, and big-integer arithmetic costs ⌈bits/64⌉.
**Theorem checks:** `experiments/check_theorems.py` exhaustively checks the exact formulas of THM-001(b), THM-002, THM-003 (all 625 binary trees with ≤ 7 nodes), and THM-005(a, b) on small cases. These checks guard against mis-stated formulas. They are not proofs.
**Correctness:** every experiment asserts agreement between all methods and a baseline (BFS, pointer LCA, brute-force model counting for k ≤ 16, explicit preorder) on every query it times.

---

## CGT-EXP-001 Binary tree navigation (`exp001_binary_tree.py`)

- **Hypothesis.** H-001.
- **Independent variables.** Shape (complete, random BST, random-turn path); n ∈ {2⁸, …, 2¹⁶} (paths up to 2¹⁴); workload (random pairs, or deep ancestor pairs (x, parent x) with depth ≥ 2/3 of the height).
- **Representations.**
  - R1: pointers + depth array.
  - R2: heap-numeration labels, arithmetic only.
  - R3: stored address words, with LCA by longest common prefix.
  - R4: Euler tour + sparse table.
- **Dependent variables.** Build ops, space, LCA ops per query, wall time per query, path-output size, and relabel cost of a root rotation.
- **Controls.** The same trees and queries for all representations. 2,000 queries per workload.
- **Falsification criterion.** H-001 fails if R2 grows with n on complete trees, or is constant on paths.
- **Result.** OBS-001–003, THM-003. R2 is constant (4 ops) whenever h < 64 and costs 4⌈(h+1)/64⌉ otherwise. R4 is constant for every shape, but needs 2.2M build ops at n = 65,536. R3 looks best on random pairs, which is a workload artifact, and is worst on deep pairs. Its storage is Θ(n²) on paths. A rotation at the root relabels all n nodes for R2 and R3 and forces an R4 rebuild, against 3 pointer writes for R1.
- **Interpretation.** Only for dense shapes does the arithmetic address grammar give O(1) navigation with no index. Everywhere else, precomputation wins on queries and pointers win on updates.
- **Limitations.** The O(n log n) sparse table, not the O(n) ±1-RMQ method. No succinct tree encodings (balanced parentheses, LOUDS) tested. Python constants.

## CGT-EXP-002 Graph reachability with full accounting (`exp002_reachability.py`)

- **Hypotheses.** H-002, H-003, H-004.
- **Independent variables.** Family:
  - G(n, m) digraphs with average out-degree 0.8 or 3;
  - random DAG with degree 2;
  - random forest;
  - complete-random bipartite A→B, p = 1/2, the THM-002 family.

  n ∈ {256, 1024, 4096}; bipartite only up to n = 1,024.
- **Methods.**
  - M1: BFS per query, with early exit.
  - M2: SCC condensation + bitset closure.
  - M3: path-grammar fixpoint, right-linear (n ≤ 1,024) and doubling (n ≤ 512).
  - M4: interval labels (forests only).
- **Dependent variables.** Ops per query, build ops, break-even Q\* (ops and wall), closure bits, zlib-compressed closure bits, grammar firings, closure size, and path-retrieval cost from the closure.
- **Falsification criteria.** See the docstring. All three hypotheses survived.
- **Result.** OBS-004, OBS-005, THM-002, THM-004.

## CGT-EXP-003 Language-constrained reachability (`exp003_constrained.py`)

- **Hypotheses.** H-005, H-006.
- **Independent variables.** Graph size and degree: (200, 1.5), (2,000, 1.5), (2,000, 4), (20,000, 4); edge labels uniform over {a, b, c}. Constraint language:
  - a*
  - (ab)*c
  - Σ*cΣ*
  - an even number of a's
  - length ≡ 0 mod 5
- **Dependent variables.** Explored product states, explored unconstrained states, and misreported vertices, averaged over 20 sources. On a 12-vertex graph, walk-enumeration counts against product size.
- **Result.** OBS-006, OBS-007, THM-001.

## CGT-EXP-004 Forest composition and minimal-DAG grammars (`exp004_forest_dag.py`)

- **Hypothesis.** H-007.
- **Families** (n ≈ 64,000):
  - 1,000 copies drawn from 8 random 64-node templates;
  - 1,000 random 64-node trees over 4 labels;
  - full binary tree with h = 15;
  - unary path.
- **Dependent variables.** DAG nodes and edges, compression ratio, rank-access ops (explicit arrays = 1), new rules per relabel, and live DAG size after 1, 10, 50 and 200 relabels with fresh labels.
- **Result.** OBS-008, THM-005.
- **Limitations.** Minimal DAGs only. Tree SLPs and top-tree compression are not implemented. There is no garbage collection of dead rules beyond counting the live size.

## CGT-EXP-005 Dynamic workloads (`exp005_dynamic.py`)

- **Hypothesis.** H-008.
- **Setup.** G(1024, 0.9n). Streams of 4,000 operations. Nine workloads vary the query fraction, the insertion/deletion mix and the query distribution:
  - uniform;
  - repetitive (a pool of 10 pairs);
  - adversarial (source with the largest reach set, target unreachable).
- **Strategies.**
  - S1: BFS.
  - S2: lazy closure rebuild.
  - S3: incremental closure on insertions.
  - S4: memoized BFS.
- **Result.** OBS-009, PROP-005.

## CGT-EXP-006 Solution grammars for CNF-SAT (`exp006_solution_grammar.py`)

- **Hypothesis.** H-009.
- **Setup.** Random 3-CNF at clause/variable ratios 4.26 and 2.0, and random 2-CNF at ratio 1.0. k ∈ {8, …, 28}, 5 instances each. The layered solution automaton is built by residual deduplication. Model counts are verified by brute force for k ≤ 16.
- **Result.** OBS-011. Inconclusive on asymptotics, and recorded as such.
- **Limitations.** Natural variable order only. Residual deduplication is an upper bound on the minimal width. k is small.

## CGT-EXP-007 Grammar shape (`exp007_grammar_shape.py`)

- **Hypothesis.** H-010; also checks THM-004(a) exactly.
- **Setup.** Directed paths, G(n, 1.5n) and random DAGs, n ∈ {64, …, 512}. Right-linear vs doubling path grammars. Firings use semi-naive (Gauss–Seidel) evaluation, and parallel depth uses synchronous bitset iteration.
- **Result.** THM-004 formula exact on all 12 instances. OBS-012.

---

## Next experiments, selected from the evidence (session 2 candidates)

1. **EXP-008: Arithmetic addressing beyond trees.** Test dense numerations for grids, k-ary tries over fixed alphabets and de Bruijn graphs. Measure the density/cost trade-off. Motivation: THM-003 is the only mechanism found so far that needs zero preprocessing. Its exact scope is the most direct test of the researcher's address intuition.
2. **EXP-009: Tree SLPs vs DAGs under updates.** Test whether richer structural grammars keep compression under the THM-005 adversary.
3. **EXP-010: CFL-constrained reachability (Dyck languages).** The first case where the operational grammar is context-free. Compare the cubic CFL-reachability algorithm with specialized Dyck algorithms.
4. **EXP-011: Workload-adaptive scheme selection.** Use PROP-005 to switch among S1–S4 online. Measure regret against the hindsight-best strategy.
