# Counterexamples and Negative Results

Each entry is a constructed or observed case in which a proposed grammatical advantage fails. These cases define the scope of the theory.

| ID | Proposed advantage | Counterexample | Failure mode | Source |
|---|---|---|---|---|
| CGT-NEG-001 | Address arithmetic gives O(1) navigation | Path-shaped binary tree: labels have n bits, every operation costs Θ(n/w), and a directly indexed array needs 2ⁿ cells | Grammar (address space) much larger than the structure | THM-003(b,c); EXP-001 |
| CGT-NEG-002 | Stored address words give cheap LCA | Deep ancestor pairs cost ≈ depth. Storage is Σ depth = Θ(n²) on paths (1.3·10⁸ chars at n = 16,384) | Low cost only on random pairs (workload artifact); quadratic memory | OBS-002 |
| CGT-NEG-003 | Address-based indexes are stable | One rotation relabels the whole subtree (all n nodes at the root) | Updates invalidate many rules | THM-003(d) |
| CGT-NEG-004 | A small reachability grammar answers queries in O(1) | Bipartite family: any retrieval-only scheme needs ⌊n/2⌋⌈n/2⌉ bits, and zlib cannot do better | The answer is information-theoretically incompressible | THM-002; OBS-005 |
| CGT-NEG-005 | Grammatical path composition reduces work | The right-linear path grammar does exactly m + Σ indeg work (closure computation). The doubling grammar does Θ(n³) on paths | Grammar *is* the algorithm; a worse shape costs more | THM-004; EXP-007 |
| CGT-NEG-006 | Grammatical constraints reduce search | Cycle C_n with ℒ = (length ≡ 0 mod k), gcd(n,k) = 1: k times more states explored, same answer | Constraint enlarges the state space with no pruning | THM-001(b); OBS-006 |
| CGT-NEG-007 | Repeated structure gives compact grammars | Unary path: minimal DAG = n, no compression. Random labelled forests: ratio 0.44 | Repetition not in complete-subtree form; no repetition | THM-005(c); OBS-008 |
| CGT-NEG-008 | Compression survives updates | Full binary tree: 200 fresh-label relabels grow g from 16 to 1,521. Unary path: ~n/2 new rules per relabel | Sharing destroyed by adversarial updates | THM-005(a,b); OBS-008 |
| CGT-NEG-009 | Sufficiently expressive grammars make hard problems near-constant time | Within standard models, a grammar built in polynomial time and resolved in polynomial time *is* a polynomial-time algorithm. Exponential grammars are lookup tables. Polynomial advice for NP-complete problems collapses PH | Answer encoded in the grammar; exponential construction; nonuniformity | PROP-006 |
| CGT-NEG-010 | Preprocessing pays off | Sparse random graphs with random queries: break-even after ~22,000–27,000 queries at n = 4,096. With 10% insertions, the lazily rebuilt closure costs 28× BFS | Construction dominates query savings | OBS-004; PROP-005; EXP-005 |
| CGT-NEG-011 | Closure gives the path, not just the answer | The closure answers "is there a path" in O(1), but *retrieving* a path still costs Σ out-degrees along it (EXP-002), and on cyclic graphs a greedy walk can dead-end | Answer retrieval ≠ witness construction; output costs | EXP-002 (`tc_greedy_path`) |
| CGT-NEG-012 | A solution grammar makes SAT easy | The solution automata of random 3-CNF grow from 49 to 43,895 nodes for k = 8 → 28. 2-CNF automata grow too, although 2-SAT is linear time by a different mechanism | Construction cost; tractability belongs to the class | OBS-011 |

## Rejected hypotheses

- **CGT-REJ-001** (from H-000, strong form): *"Expressive grammars can make algorithmic problems dramatically easier, approaching constant-time resolution, in general."* Rejected by PROP-006 and NEG-004/009. The surviving form is the restricted version: specific classes and specific preprocessing regimes, with each mechanism named.
- **CGT-REJ-002** (initial working assumption of this session): *"Address-word LCA (R3) is a competitive grammatical navigation method."* It looked competitive on random pairs (2–3 ops). Rejected after the deep-pair workload and the storage analysis (NEG-002). Kept as an instance of the methodological lesson that the workload must be adversarial as well as random.
