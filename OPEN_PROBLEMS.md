# Open Problems

Ordered roughly by how informative a solution would be for the program.

### CGT-OPEN-001 Formalize the mechanism thesis
Make CONJ-001 precise. Define "grammatical resolution scheme" and "attributable to mechanism M" so that the thesis becomes either a theorem or a refuted claim. One candidate route is to express each mechanism as a reduction to a known lower-bound framework, such as the cell-probe model for M-PRE and Kolmogorov or grammar complexity for M-SHARE.

### CGT-OPEN-002 Which structures admit dense arithmetic addressing?
THM-003 characterizes binary trees under the heap numeration. Generalize: for which deterministic rooted operational grammars is there a numeration ν with density Ω(1) and O(1) word-op moves? Candidates are complete k-ary trees, d-dimensional grids, de Bruijn graphs and Cayley graphs of groups with efficient word problems. Relate the answer to automatic structures and automatic groups (`LITERATURE_REVIEW.md` §7). This is the most direct formal test of the researcher's original address insight.

### CGT-OPEN-003 Compiling move words
For a fixed word w used many times, when can ⟦w⟧ be compiled into an O(1)-size operation? Examples: compositions of the affine maps x ↦ 2x + b compose to x ↦ 2^k x + c; the transition monoid of a DFA. Characterize this through the size of a representation of the transition monoid T(G) (DEF-007).

### CGT-OPEN-004 Dynamic structural grammars with bounded inflation
Is there a grammar-compressed tree representation with O(polylog n) update time whose size stays within a constant factor of the optimal grammar after every update? THM-005 shows that path copying on minimal DAGs does not achieve this. The existing literature on dynamic compressed structures must be reviewed first.

### CGT-OPEN-005 Does grammar-parameterized complexity distinguish anything new?
Find a problem whose complexity in (n, g, q, u, o) is not already captured by parameterized complexity, compressed-data algorithms or preprocessing-query trade-offs. If none exists, the notation is a reporting convention and not a theory, and the book should say so.

### CGT-OPEN-006 Solution-grammar growth for random 3-CNF
Is the minimal ordered solution automaton of random 3-CNF at constant clause density 2^{Θ(k)} with high probability, for natural or optimal orders? EXP-006 cannot decide this. The knowledge-compilation literature probably already answers it, so check there first.

### CGT-OPEN-007 Lower bounds for grammar shapes
THM-004 compares two grammars for the closure. Among all semi-naive-evaluable grammars for P⁺, is there a work/depth trade-off lower bound? For example, does every grammar with derivation depth O(log n) need ω(n·m) work on some family?

### CGT-OPEN-008 Context-free operational grammars
Extend THM-001 to context-free ℒ: CFL-reachability and Dyck reachability. Determine where grammar size |Q| or |N| enters the cost, and whether the tight-factor phenomenon persists.

### CGT-OPEN-009 Output-sensitive witnesses
A closure answers existence in O(1). What is the cheapest additional structure that retrieves a witness path in O(length) time? For DAGs, a next-hop matrix uses Θ(n² log n) bits. Is there an information lower bound for witness retrieval analogous to THM-002?

### CGT-OPEN-010 Literature debts
Verify all **[U]** references in `LITERATURE_REVIEW.md`. In particular: attribution of heap numbering and XOR-LCA, Khoussainov–Nerode details, Lohrey's TSLP-vs-DAG succinctness statement, Yannakakis's CFL-reachability attribution, and attribute-grammar literature.

---

## Session 2 updates

- **CGT-OPEN-002** (arithmetic addressing beyond trees): **partially resolved.** PROP-008 gives dense compilable numerations for de Bruijn graphs, hypercubes and grids. THM-006 does the same for heap-shaped trees. Still open: Cayley graphs of non-abelian groups with efficient word problems; tries over growing alphabets.
- **CGT-OPEN-003** (compiling move words): **partially resolved** by THM-006, THM-007 and DEF-011.

### CGT-OPEN-011 Is the grammar-constrained surfer (PROP-010) known, and is it useful?
Search the probabilistic-model-checking, meta-path and personalized-ranking literatures for this exact model. Evaluate it on a corpus with relevance judgments before claiming any retrieval benefit.

### CGT-OPEN-012 Characterize arithmetically compilable classes
For which classes 𝒦 does a numeration exist with an O(1)-word class 𝓕 closed under composition (DEF-011)? Conjecture: exactly when the move domains and actions are determined by O(1) words of parameters per structure, uniformly in 𝒦. A precise form might use the transition monoid's representation size together with the counting lemma of THM-002/THM-007.

### CGT-OPEN-013 Gauss–Seidel orderings for PageRank
OBS-016 suggests that sweeping in an order consistent with the link direction (in-neighbours first) helps. Is there a cheap ordering derived from the SCC condensation (a "structural grammar" of the graph) with a provable sweep bound? The literature on ordering for iterative PageRank solvers must be reviewed first; this is likely known.
