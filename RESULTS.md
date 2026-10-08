# Results Ledger

Every entry has a category from the ladder of claims, a status and a review state. **Proof-review status** is "self-checked" for everything in session 1: each proof was written and re-read by the same agent, and where possible checked against exhaustive or experimental computation (`experiments/check_theorems.py`). No result has been externally reviewed yet. **Novelty** is stated relative to `LITERATURE_REVIEW.md`. Most results here are *elementary*, and several are almost certainly folklore. Their value to the program is that they fix precise boundaries.

Notation: `DEFINITIONS.md`, `FORMAL_MODELS.md`. n = |A|, m = number of move/edge tuples, w = word size.

---

## A. Propositions and theorems

### CGT-PROP-001 Compositional semantics *(Proposition; standard)*

For an operational grammar G, the map ⟦·⟧ : Σ* → Rel(A) is a monoid homomorphism from (Σ*, ·, ε) to (Rel(A), ;, id_A). For languages, ⟦ℒ₁ℒ₂⟧ = ⟦ℒ₁⟧;⟦ℒ₂⟧, ⟦ℒ₁ ∪ ℒ₂⟧ = ⟦ℒ₁⟧ ∪ ⟦ℒ₂⟧ and ⟦ℒ*⟧ = ⋃_{k≥0} ⟦ℒ⟧^k, which is the reflexive-transitive closure.

*Proof.* ⟦·⟧ is defined on letters and extended by composition. Associativity of relational composition gives the homomorphism property. The language identities follow because composition distributes over arbitrary unions. ∎

*Meaning for CGT.* "A path from u to v is an edge from u to w followed by a path from w to v" is exactly ⟦E·E*⟧ = ⟦E⟧;⟦E*⟧. Treating paths as grammatical objects is therefore *sound by construction*. That is a statement about semantics only, and it says nothing about cost (THM-004). This is the relational (Kleene-algebra) view of paths that underlies Tarjan's path expressions (Tarjan 1981).

### CGT-PROP-002 Independence of syntax, semantics and execution *(Proposition; elementary)*

Each of the following combinations occurs:

1. *Syntactically admissible, semantically empty.* In a binary tree, the word `LL` ∈ {L,R}* is admissible, but ⟦LL⟧(root) = ∅ if the root's left child is a leaf.
2. *Semantically non-empty, expensive to resolve.* For a fixed regular language ℒ over an edge-labelled graph, deciding whether some *simple* path from s to t has its label in ℒ is NP-complete for some fixed ℒ (Mendelzon & Wood 1995). Under walk semantics the same question is polynomial (THM-001). The semantics has changed (simple paths vs walks), not the syntax.
3. *Cheap to retrieve, expensive to store or build.* Reachability is answered by one bit lookup from a transitive closure. The closure needs ⌊n/2⌋⌈n/2⌉ bits on some graphs (THM-002).
4. *Expensive to construct from scratch, cheap after preprocessing.* LCA queries in an arbitrary binary tree take Θ(h) by pointer walking and O(1) after O(n) preprocessing (Bender & Farach-Colton 2000). EXP-001 measures the variant with O(n log n) preprocessing.

*Proof.* By the cited examples (1 is immediate). ∎

### CGT-THM-001 Product resolution, pruning and its tight cost *(Theorem; (a) known, (b)–(c) elementary, proved here)*

Let G = (Σ, 𝔄, ⟦·⟧, ℒ) with ℒ given by a DFA D = (Q, Σ, δ, q₀, F) (δ partial), and let m = Σ_a |⟦a⟧|.

**(a) Upper bound.** For x ∈ A, the set ⟦ℒ⟧(x) can be computed in O(|Q|·(|Σ|·n + m)) time and O(|Q|·n) space, by searching the product graph on A × Q. (The |Σ|·n term pays for consulting δ once per product vertex and letter; it is absorbed into m when every element has an out-move of every label. Corrected in audit E-002.)

**(b) Tightness: a constraint can cost a factor |Q|.** For every k ≥ 1 and every n with gcd(n, k) = 1, there are a structure with n elements, m = n, and a k-state DFA such that: unconstrained search from x visits n states; product search visits exactly n·k states; and ⟦ℒ⟧(x) equals the unconstrained answer. So the constraint costs a factor k = |Q| and prunes nothing.

**(c) Pruning: a constraint can save an unbounded factor.** For every n there are a structure with n elements and a 1-state DFA such that product search visits 1 state, unconstrained search visits n, and the two answers differ.

*Proof.* (a) Product vertices are (y, q). There is an edge (y,q) → (z, δ(q,a)) for each (y,z) ∈ ⟦a⟧ with δ(q,a) defined. By induction on |w|: y ∈ ⟦w⟧(x) and δ*(q₀, w) = q iff (y, q) is reachable from (x, q₀) by a product walk spelling w. So ⟦ℒ⟧(x) = {y : (y, q) reachable from (x, q₀), q ∈ F}. The product has ≤ |Q|·n vertices and ≤ |Q|·m edges, and BFS is linear in that size. (This construction is standard; see Mendelzon & Wood 1995 and Barrett, Jacob & Marathe 2000.)

(b) Take the directed n-cycle with one label a, ⟦a⟧ = {(i, i+1 mod n)}, and ℒ = {a^t : t ≡ 0 mod k}, whose DFA is the k-cycle on Q = ℤ_k. The product move is (i, j) ↦ (i+1 mod n, j+1 mod k). The orbit of (0,0) is {(t mod n, t mod k) : t ≥ 0}, which has size lcm(n, k) = nk because gcd(n,k) = 1 (Chinese remainder theorem). So all nk product states are visited. Unconstrained search visits the n cycle vertices. For any target i there is t with t ≡ i (mod n) and t ≡ 0 (mod k), again by the CRT, so ⟦ℒ⟧(0) = A, which is the unconstrained answer.

(c) Take the star with centre x and n−1 leaves, edges x → leaf labelled b, and ℒ = a*. Product search visits only (x, q₀) and answers {x}. Unconstrained search visits n vertices and answers A. ∎

*Experimental match (EXP-003, OBS-006).* The measured product/unconstrained ratio ranges from 0.003 (ℒ = a*, sparse) to **exactly 5.000** for ℒ = (length ≡ 0 mod 5) on random graphs. The upper bound in (a) is attained in practice, not only on the constructed cycle.

### CGT-THM-002 Information lower bound for retrieval-only reachability grammars *(Theorem; elementary counting, independently proved here; likely folklore)*

**Lemma (counting).** Let a scheme map each 𝔄 ∈ 𝒦 to a bit string E(𝔄) from which every query in 𝒬 can be answered *without access to 𝔄*. If N = |{f_𝔄 : 𝔄 ∈ 𝒦}| (DEF-008), then max_𝔄 |E(𝔄)| ≥ ⌈log₂(N+1)⌉ − 1. Moreover, for every c ≥ 0, fewer than N·2^{−c} answer functions can have encodings shorter than log₂N − c bits.

*Proof.* Structures with different answer functions must have different encodings, since otherwise some query would get the same answer for both. There are 2^{L+1} − 1 strings of length ≤ L. So 2^{L+1} − 1 ≥ N, which gives L ≥ log₂(N+1) − 1. There are fewer than 2^{log₂N − c} = N·2^{−c} strings shorter than log₂N − c bits, and each encodes at most one answer function. ∎

**Theorem.** Let 𝒦 be the digraphs on vertex set [n] and 𝒬 the reachability queries "s ⇝ t?". Any retrieval-only scheme needs at least ⌊n/2⌋·⌈n/2⌉ bits on some n-vertex digraph. Moreover, for every c ≥ 0, all but a fraction smaller than 2^{−c} of the graphs in the bipartite family below need at least ⌊n/2⌋⌈n/2⌉ − c bits.

*Proof.* Let a = ⌊n/2⌋, b = ⌈n/2⌉, X = {1..a}, Y = {a+1..n}. For every S ⊆ X × Y, let G_S have edge set S. In G_S every path has length ≤ 1, so s ⇝ t (s ≠ t) iff (s,t) ∈ S. The answer functions of the G_S are therefore pairwise distinct, so N ≥ 2^{ab}. Apply the lemma. ∎

**Corollary CGT-COR-002a.** No representation of size o(n²) bits, whether grammar, index or label set, supports reachability on *all* digraphs without consulting the graph. The full transitive closure (n² bits) is optimal for this task up to a factor of 4. Any sub-quadratic scheme has to exploit a restricted class (M-RESTRICT) or read the input at query time, which is search.

**Corollary CGT-COR-002b (restricted class).** For rooted forests, the interval labels of Agrawal, Borgida & Jagadish (1989) use O(n log n) bits, which matches the class's information content of Θ(n log n) bits up to a constant factor. The number of labelled rooted forests on [n] is (n+1)^{n−1}, by Cayley's formula applied to trees on n+1 vertices. Distinct forests have distinct answer functions, because the reachability (ancestor) relation determines each node's parent as its deepest proper ancestor; so I = log₂ (n+1)^{n−1} = Θ(n log n). *(Justification added in audit E-003.)* Here the structural grammar of the class (nesting) *is* an optimal index.

*Scope.* The theorem limits *retrieval*. It says nothing about schemes that keep the graph and search it, for which 0 extra bits suffice at the cost of Θ(n+m) per query. This is exactly the line between "the grammar encodes the answer" and "the grammar organizes the search" that mandate §11 asks for. The same asymptotics for DAG closures (partial orders) follow from Kleitman & Rothschild (1975), where log₂(#posets) ~ n²/4. The family above is the simple, exact, non-asymptotic version.

*Experimental match (EXP-002, OBS-005).* At n = 1024, zlib compresses the bipartite closures to 281,960 bits, against the bound n²/4 = 262,144. Forest closures compress about 55-fold, in line with COR-002b.

### CGT-THM-003 Arithmetic addressing in binary trees: characterization of its scope *(Theorem; components classical, packaging and scope statement here)*

Let T be a binary tree of height h with n nodes, with addresses in {0,1}* (DEF-006) and heap numeration ν(w) = int("1"·w, 2). Assume a word-RAM with a most-significant-bit instruction. (Without it, add an O(log w) factor.)

**(a) Operations.** From the labels ν alone, with no other stored data: parent (⌊ν/2⌋), children (2ν, 2ν+1), depth (msb(ν)), the ancestor test (ν_v >> (d_v − d_u) = ν_u) and LCA each take O(⌈(h+1)/w⌉) word operations.

**(b) Address space.** Any table indexed directly by ν has 2^{h+1} − 1 cells. The density is δ = n/(2^{h+1} − 1). It is > 1/2 for complete (heap-shaped) trees and 2^{−Θ(n)} for path-shaped trees.

**(c) Scope.** Since h ≥ ⌊log₂ n⌋, labels need ≥ ⌊log₂ n⌋ + 1 bits. The label-only operations in (a) are O(1) iff h = O(w); with w = Θ(log n), iff h = O(log n). On path-shaped trees (h = n − 1) they cost Θ(n/w). That is a factor w better than pointer walking but not constant.

**(d) Instability under rotation.** A single rotation at node v changes the address, and hence the heap label, of *every* node in the subtree of v.

*Proof.* (a) The child and parent formulas follow from ν("1"·w·b) = 2ν + b. The ancestor test holds because u is an ancestor of v iff addr(u) is a prefix of addr(v), iff ν_v shifted right by d_v − d_u equals ν_u. For LCA, the LCA's address is the longest common prefix of the two addresses. First replace the deeper node by its ancestor at the same depth (one shift). This does not change the LCA, because the LCA's depth is ≤ the smaller depth. Two numerals of equal length share exactly the bits above the most significant set bit of their XOR, so LCA = ν >> (msb(ν_u ⊕ ν_v) + 1), with the convention msb(0) = −1 (equal numerals: the nodes coincide after alignment, and the shift is 0). Each step is a constant number of operations on (h+1)-bit integers. (b) The labels range over [1, 2^{h+1} − 1]. A complete tree has n ≥ 2^h. A path has h = n − 1. (c) Follows from (a) and (b). (d) Right rotation at v with left child ℓ. Let p be the address of v. Afterwards: ℓ has address p (before: p0). v has address p1 (before: p). A node of ℓ's left subtree with address p00x gets p0x. A node of ℓ's right subtree with address p01x gets p10x. A node of v's right subtree with address p1x gets p11x. All these maps change the word, so every node in the subtree changes address. ∎

*Contrast.* Euler tour + RMQ gives O(1) LCA for **every** shape after O(n) preprocessing (Bender & Farach-Colton 2000; EXP-001 uses the simpler O(n log n) sparse-table variant). So the arithmetic grammar (M-ARITH) wins only where it needs no preprocessing at all, which means only on dense (near-complete) shapes. Elsewhere precomputation (M-PRE) dominates. *Novelty:* heap numbering and XOR-based LCA in complete binary trees are classical. Precise attribution is still to be verified (CGT-OPEN-010). The contribution here is only the exact scope statement (c)–(d) in CGT terms.

### CGT-THM-004 Same semantics, different grammar shape, different cost *(Theorem; (a) exact count proved here, (b)–(c) standard)*

Consider the two path grammars over a digraph with m edges:

- right-linear  P → E | E P
- doubling      P → E | P P

Both denote the transitive closure P⁺ (PROP-001).

**(a)** Semi-naive bottom-up evaluation of the right-linear grammar, with duplicate elimination, makes exactly

  **m + Σ_{(w,v) ∈ P⁺} indeg(w)**

rule applications. This is ≤ m + n·m = O(nm), the cost of a search from every vertex.

**(b)** Semi-naive evaluation of the doubling grammar makes O(n·|P⁺|) = O(n³) applications.

**(c)** With synchronous (Jacobi) rounds, starting from P₀ = E, the number of *productive* rounds is ℓ − 1 for the right-linear grammar and ⌈log₂ ℓ⌉ for the doubling grammar, where ℓ ≥ 1 is the largest shortest *positive-length* distance over pairs of P⁺ (pairs (u,u) on cycles included); a fixpoint detector adds one confirming round. *(Corrected in audit E-001; see Errata.)*

*Proof.* (a) Initialization attempts each edge once (m). A fact (w,v) is appended to the work list only when it is first inserted, so each fact of P⁺ is processed exactly once. Processing (w,v) attempts E(u,w) ∧ P(w,v) ⇒ P(u,v) once for each in-edge (u,w), that is, indeg(w) times. Completeness and soundness of semi-naive evaluation for this rule are standard: induct on path length. (b) Each fact is processed once and costs |Pin(w)| + |P(v)| ≤ 2n at that moment. (c) By induction, after i synchronous rounds the linear iterate contains exactly the pairs at distance ∈ [1, i+1], and the doubling iterate exactly those at distance ∈ [1, 2^i]. The linear iterate is complete when i + 1 ≥ ℓ, i.e. after ℓ − 1 rounds; the doubling iterate when 2^i ≥ ℓ, i.e. after ⌈log₂ ℓ⌉ rounds. ∎

*Experimental match (EXP-007).* Formula (a) holds **exactly** on all 12 instances. On the directed path, the doubling-grammar firings grow 81,500 → 675,004 → 5,495,164 → 44,348,156 as n doubles: ratios ≈ 8.3, 8.1, 8.1, i.e., cubic (OBS-012, empirical). Right-linear firings are n(n−1)/2. Depths: 63 vs 7 at n = 64, and 511 vs 10 at n = 512.

*Meaning.* (i) Evaluating a path grammar *is* computing the closure, with the same work as repeated search. The grammar formulation does not reduce work (H-002, supported). (ii) The **shape** of a grammar for a fixed language is a real cost parameter: it trades total work against parallel depth. This is known in Datalog practice (linear vs non-linear recursion) and in parallel algorithms (transitive closure by repeated squaring). The exact count (a) appears to be a convenient, self-contained statement; novelty is not claimed.

### CGT-PROP-005 Break-even under invalidating updates *(Proposition; elementary)*

Let a stream be split by index-invalidating updates into epochs with Q₁, …, Q_k queries. A rebuild-on-demand index with build cost B and query cost q₁ beats a no-preprocessing baseline with query cost q₀ > q₁ iff

  B · |{j : Q_j > 0}| < (q₀ − q₁) · Σ_j Q_j.

A sufficient condition is Q_j > B/(q₀ − q₁) for every non-empty epoch.

*Proof.* Sum the costs epoch by epoch. ∎

*Experimental match (EXP-005).* With 10% insertions, epochs average ~10 queries, while B/(q₀ − q₁) ≈ 1,400. The lazily rebuilt closure costs 28× more than BFS (6.78M vs 0.24M steps), as predicted.

### CGT-THM-005 Update inflation of minimal-DAG tree grammars *(Theorem; elementary, proved here)*

Let T_h be the full binary tree of height h with all labels equal (n = 2^{h+1} − 1). Its minimal DAG has g = h + 1 nodes.

**(a)** Relabelling one node at depth d ≥ 0 with a fresh label creates exactly d + 1 new rules. The live minimal DAG then has h + d + 1 nodes.

**(b)** For every k ≤ 2^h there are k leaves such that relabelling them with pairwise distinct fresh labels yields a minimal DAG with at least k·(h + 1 − ⌈log₂ k⌉) nodes. Each update does O(h) work and adds at most h + 1 nodes, so g ≤ (h+1)(k+1).

**(c)** For the unary path with n nodes and a single label, the minimal DAG has n nodes, so there is no compression. A relabel at depth d creates d + 1 new rules under path copying (≈ n/2 on average for a uniformly random node). Yet the label string aⁿ has a straight-line program of size O(log n).

*Proof.* (a) The relabelled node and its d ancestors are the only nodes whose subtrees contain the fresh label, so their subtrees are new and pairwise distinct (they have different heights). Every other node's subtree is a full tree of some height < h. All heights 0..h−1 still occur (as the siblings along the path and their subtrees, or, for d = 0, inside the root's children). The old root class (full tree of height h) disappears. Total: h + (d + 1). (b) Choose the leaves so that at every depth j ≥ ⌈log₂ k⌉ their root paths pass through k distinct nodes. Let U be the union of the root paths. Each node in U has a non-empty set of fresh labels below it. Two nodes of U at the same depth have disjoint non-empty sets. Two nodes at different depths have subtrees of different heights. So all |U| ≥ k(h + 1 − ⌈log₂ k⌉) subtrees are distinct. The upper bound is (a) applied k times. (c) Subtrees of a unary path have pairwise distinct sizes. The SLP X₀ → a, X_{i+1} → X_i X_i, plus a binary decomposition of n, has O(log n) rules. ∎

*Meaning.* Sharing (M-SHARE) is *fragile*. Adversarial updates destroy it at Θ(log n) new rules per update. Minimal DAGs also miss repetition that is not a repeated *complete subtree*. Tree straight-line programs cover such repetition and can be exponentially more succinct than DAGs (Lohrey 2015 survey). *Experimental match (EXP-004):* the full binary tree with h = 15 goes from g = 16 to 1,521 after 200 random relabels. The unary path has g = n = 65,536 and creates ~32k rules per relabel.

### CGT-PROP-006 Grammars cannot move problems across the P/NP boundary within standard models *(Proposition; standard complexity theory restated)*

Let Π ⊆ {0,1}* and let a "grammar" Γ be attached to inputs.

1. **Uniform, polynomial.** If Γ(x) is computable in time poly(|x|) and Π(x) is decidable from (x, Γ(x)) in time poly(|x|), then Π ∈ P. If in addition Π is NP-complete, then P = NP.
2. **Advice.** If Γ depends only on |x|, has size poly(|x|), and Π is decidable from (x, Γ_{|x|}) in polynomial time, then Π ∈ P/poly. For NP-complete Π this would imply that the polynomial hierarchy collapses to its second level (Karp & Lipton 1980; the collapse to the *second* level is commonly credited to an improvement by Sipser, the original argument giving the third level, per the secondary sources consulted; see audit E-004). That consequence is widely believed false.
3. **Unbounded size.** For every decidable Π, taking Γ_n to be the truth table of Π on length-n inputs (2ⁿ bits) gives O(n)-time retrieval. Building Γ_n costs ≥ 2ⁿ decisions. This says nothing about P vs NP.
4. **Restriction.** Restricting Π to a class C (for example 2-CNF; Aspvall, Plass & Tarjan 1979) can make it polynomial while Π stays NP-complete. The tractability belongs to C, not to any grammar.

*Proof.* 1 is composition of polynomial-time computations. 2 is the definition of P/poly plus Karp–Lipton. 3 holds by construction. 4 is an example. ∎

*Consequence for the mandate's conjecture (§14).* "Constant or near-constant resolution through expressive grammars" is possible exactly in cases 3 and 4, and in case 2 only if a widely believed conjecture fails. In case 1 it is equivalent to an ordinary polynomial-time algorithm. The conjecture is therefore **rejected as a route to complexity-class separations or collapses** (CGT-NEG-009). It survives as the study of *which restricted classes and which preprocessing regimes* allow fast resolution, which is what the rest of this ledger does.

---

## B. Empirical observations

All numbers come from `experiments/results/*.json` (summary in `experiments/results/SUMMARY.md`).

| ID | Experiment | Observation |
|---|---|---|
| CGT-OBS-001 | EXP-001 | *(Audit E-005: the word-op count for R2 is assigned by the cost model, not measured, so its constancy is true by construction; the independent evidence is the wall-clock column.)* Heap-arithmetic LCA costs 4 word-ops/query for every complete and random-BST tree up to n = 65,536 (h ≤ 37 < 64), and 4⌈(h+1)/64⌉ on paths (1,024 at n = 16,384). Wall time per query on paths rises from 0.47 µs to 3.3 µs, consistent with the cost model. |
| CGT-OBS-002 | EXP-001 | LCA by longest common prefix of stored address words costs ≈2–3 character comparisons on *random* pairs, because random pairs diverge near the root. On deep ancestor pairs it costs ≈ depth (3,403 at n = 4,096 on paths). Address storage is Σ depth: Θ(n log n) on balanced trees, Θ(n²) on paths (infeasible at n = 16,384: 1.3·10⁸ chars). The workload decides the measured "advantage". |
| CGT-OBS-003 | EXP-001 | Euler tour + sparse table answers LCA in 3 ops/query for every shape and size, after 2.2·10⁶ build ops at n = 65,536. |
| CGT-OBS-004 | EXP-002 | Break-even query volumes for a precomputed closure against BFS range from **Q\* ≈ 4–12** (dense random digraphs: a giant SCC lets condensation share rows) to **Q\* ≈ 22,000–27,000** (sparse random graphs and DAGs, n = 4,096, where random queries are mostly negative and BFS stops early). |
| CGT-OBS-005 | EXP-002 | zlib never compresses bipartite-family closures below n²/4 bits (THM-002), but compresses forest closures ~55× (COR-002b). |
| CGT-OBS-006 | EXP-003 | Constrained/unconstrained explored-state ratio ranges from 0.003 to 5.000. Restrictive languages prune (a*, (ab)*c). Permissive ones (parity, length mod 5) cost exactly \|Q\|× more and return almost the same vertex set. |
| CGT-OBS-007 | EXP-003 | "Search, then filter" is *incorrect*: unconstrained search misreports up to ~15,600 of 20,000 vertices on restrictive languages. Enumerating walks instead of product states reaches the 2·10⁶ cap while the product has ≤ 55 states. |
| CGT-OBS-008 | EXP-004 | Minimal-DAG size/explicit size: 0.0042 (forest of copies of 8 templates), 0.44 (random labelled forest), 0.0004 (full binary tree), 1.0 (unary path). Rank access costs 16–22 steps against 1 for explicit arrays, and 32,710 steps on the unary path. |
| CGT-OBS-009 | EXP-005 | Across 9 query/update workloads, 4 different strategies are cheapest (BFS, lazy rebuild, incremental closure, memoized BFS), with cost ratios up to ~660×. No strategy dominates (H-008 supported). |
| CGT-OBS-010 | all | In every case where a grammar-based scheme won on some cost component, the win traces to one of M-ARITH, M-PRE, M-SHARE, M-RESTRICT or M-PRUNE. In no case did the grammatical formulation itself reduce work (cf. THM-004a). |
| CGT-OBS-011 | EXP-006 | Solution automata for random CNF (natural variable order, residual deduplication) grow from ~50 to ~44,000 nodes for 3-CNF at m/k = 4.26 over k = 8..28. Both exponential (b ≈ 0.49 bits/variable, R² = 0.987) and polynomial (degree ≈ 5.5, R² = 0.975) fits are acceptable. **The data cannot decide the asymptotics**, and no asymptotic claim is made. 2-CNF also grows (b ≈ 0.29), so 2-SAT's tractability does not come from small solution grammars. |
| CGT-OBS-012 | EXP-007 | On the directed path, doubling-grammar firings scale by ≈8× per doubling of n (cubic). Right-linear firings equal n(n−1)/2. |

## C. Conjecture

### CGT-CONJ-001 Mechanism thesis *(Conjecture / methodological thesis; informal)*

Every asymptotic advantage of a grammatical resolution scheme over the best conventional scheme, for the same query class, machine model and cost component, can be attributed to a combination of M-ARITH, M-PRE, M-SHARE, M-RESTRICT and M-PRUNE (DEF-009).

*Status.* Supported by OBS-010. Not yet a mathematical statement, because "conventional scheme" and "attributed to" are undefined. Making it precise is CGT-OPEN-001. *Falsifier:* a grammar-based scheme with an asymptotic advantage that none of the five mechanisms explains.

---

## A2. Session 2 results (2026-10-08)

### CGT-DEF-011 Arithmetically compilable structure *(Definition; CGT, provisional)*

A deterministic operational grammar is **arithmetically compilable** (for a class 𝒦 of structures) if there is a numeration ν of elements and a class 𝓕 of partial maps on numerals such that:

- (i) every move acts as some f ∈ 𝓕;
- (ii) 𝓕 is closed under composition, where composition includes the conjunction of domains;
- (iii) every f ∈ 𝓕 is stored in O(1) machine words, and composition, application and the domain test each cost O(1) word operations.

Then any move word w **compiles** in O(|w|) word operations into one element of 𝓕, and each later application costs O(1), independent of |w|. This is the sense in which a grammar becomes "operational" without preprocessing the structure itself.

### CGT-THM-006 Word compilation in heap-shaped binary trees *(Theorem; proved here; exhaustively checked; novelty unverified)*

Let T_n be the binary tree with node set {1, …, n}, with L : x ↦ 2x, R : x ↦ 2x + 1, U : x ↦ ⌊x/2⌋. A word w ∈ {L, R, U}* is *defined at x* iff every numeral visited after each step lies in [1, n].

Then there are integers k, j ≥ 0, c ∈ [0, 2^j) and lo, hi, computable from (w, n) in O(|w|) arithmetic operations, such that for every x ∈ [1, n]:

  ⟦w⟧(x) is defined ⇔ lo ≤ x ≤ hi, and then ⟦w⟧(x) = ⌊x / 2^k⌋ · 2^j + c.

With early termination (stop as soon as the domain is empty), all intermediate integers have O(log n) bits. So for n < 2^w, compilation costs O(|w|) word operations and each application costs O(1).

*Proof.*

1. **Normal form.** By induction on prefixes, each prefix w_i of w induces a total map p_i(x) = ⌊x/2^{k_i}⌋·2^{j_i} + c_i with 0 ≤ c_i < 2^{j_i}. The empty word gives (0, 0, 0). Appending L or R gives (k, j+1, 2c + b). Appending U with j > 0 gives (k, j−1, ⌊c/2⌋), because ⌊(2y + b)/2⌋ = y. Appending U with j = 0 gives (k+1, 0, 0).
2. **Monotonicity.** Each p_i is non-decreasing in x, since it is a composition of non-decreasing maps.
3. **Lower end of the domain.** The word is defined at x iff 1 ≤ p_i(x) ≤ n for every prefix i ≥ 1. The lower bound can fail only at a U-step with j = 0, where it requires ⌊x/2^{k}⌋ ≥ 1, i.e. x ≥ 2^k. Since k never decreases, all such conditions together say x ≥ 2^{k_max} =: lo (with lo ≥ 1).
4. **Upper end of the domain.** If c_i > n, the prefix value already exceeds n for every x, so the domain is empty. Otherwise, p_i(x) ≤ n ⇔ ⌊x/2^{k_i}⌋ ≤ ⌊(n − c_i)/2^{j_i}⌋ ⇔ x ≤ (⌊(n − c_i)/2^{j_i}⌋ + 1)·2^{k_i} − 1 =: T_i. Take hi = min(n, min_i T_i).
5. **Cost.** Each step updates (k, j, c, lo, hi) with O(1) operations. Once j > ⌊log₂ n⌋ or c > n, hi < lo, and compilation can stop.

∎

*Checks.* `sdk/tests/test_addressing.py` compares the compiled map with step-by-step evaluation for all words of length ≤ 7, all n ≤ 40 and all x: more than 2·10⁶ cases, all equal. It also checks 300 random long words on n < 5,000.

*Relationship to prior work.*
- Heap numbering is classical (Williams 1964).
- The moves of T_n are synchronous rational relations, so T_n is an automatic structure (Blumensath & Grädel 2000).
- The compiled object is an element of the structure's transition monoid (DEF-007).
- What THM-006 adds is a *constant-size normal form with an interval domain* for that monoid. No source stating it was found in the reviewed literature. Novelty is **unverified** (OPEN-010).

### CGT-THM-007 No constant-size compilation on arbitrary tree shapes *(Theorem; elementary counting, proved here)*

Let a scheme encode each binary tree T with n nodes (nodes named by their addresses) as a bit string E(T), so that for every node it can be decided from E(T) alone whether the move L is defined there. Then max_T |E(T)| ≥ ⌊n/2⌋ bits.

*Proof.* Consider the caterpillar trees: a right spine 1^0, …, 1^{s−1}, plus left leaves at a set S ⊆ {0, …, ⌊n/2⌋ − 1} of spine positions, with s = n − |S| (so s ≥ ⌈n/2⌉ > max S). Then dom⟦L⟧ = {1^i : i ∈ S}. These 2^{⌊n/2⌋} trees have pairwise distinct answer functions, and the counting lemma of THM-002 applies. ∎

*Meaning.* THM-006 and THM-007 together bound mechanism M-ARITH:
- constant-size compiled operations exist when the move semantics is fixed by O(1) parameters of the structure (here, n alone);
- for arbitrary shapes, even one move's *domain* carries Ω(n) bits, so the best possible is an n-entry table, built by simulation in Θ(n·|w|).

`check_theorems.thm007` verifies the counting for all binary trees with n ≤ 11 nodes. EXP-008 measures both sides (OBS-013, OBS-014).

### Further compilable classes *(Proposition CGT-PROP-008; elementary)*

The following are arithmetically compilable with density 1. Each is checked exhaustively on small instances in `sdk/tests/test_addressing.py`.

| Structure | Moves | Compiled class | Why it is closed |
|---|---|---|---|
| de Bruijn graph B(k, m) | x ↦ (kx + a) mod k^m | affine maps mod N | (a₂, b₂)∘(a₁, b₁) = (a₂a₁, a₂b₁ + b₂) mod N |
| hypercube Q_d | x ↦ x ⊕ 2^i | XOR masks | x ⊕ c₁ ⊕ c₂ = x ⊕ (c₁ ⊕ c₂) |
| d-dimensional grid | x ↦ x ± e_i, defined only inside the box | translation t plus per-axis prefix minimum/maximum (lo, hi) | composition adds t and takes min/max of shifted prefixes; the domain is a box |

### CGT-THM-008 Contraction of PageRank power iteration *(Theorem; standard; e.g. Langville & Meyer 2004; Haveliwala & Kamvar 2003 for the related eigenvalue bound)*

Let M be the column-stochastic matrix of the surfer's link step, with dangling columns replaced by v. Let T(x) = αMx + (1 − α)v. Then:

- for probability vectors x, y: ‖T(x) − T(y)‖₁ ≤ α‖x − y‖₁;
- T has a unique fixed point π, the PageRank vector;
- ‖x_k − π‖₁ ≤ α^k ‖x₀ − π‖₁ ≤ 2α^k;
- ‖x_k − π‖₁ ≤ α/(1 − α) · ‖x_k − x_{k−1}‖₁.

*Proof.* ‖Mz‖₁ ≤ ‖z‖₁ for column-stochastic M, by the triangle inequality, so T is an α-contraction on the simplex. Banach's fixed-point theorem gives existence, uniqueness and the a-priori rate. For the a-posteriori bound: ‖x_{k−1} − π‖ ≤ ‖x_{k−1} − x_k‖ + ‖x_k − π‖ ≤ r_k + α‖x_{k−1} − π‖, so ‖x_{k−1} − π‖ ≤ r_k/(1 − α). Then ‖x_k − π‖ ≤ α‖x_{k−1} − π‖ ≤ α r_k/(1 − α). ∎

`sdk/tests/test_pagerank.py` checks the per-step contraction against an exact linear solve.

### CGT-PROP-009 A-priori iteration bound *(Proposition; standard consequence)*

Power iteration from x₀ = v with stopping rule α/(1 − α)·r_k ≤ tol stops after at most k\* = ⌈log(tol·(1 − α)/2) / log α⌉ iterations.

*Proof.* r_k ≤ α^{k−1} r₁ ≤ 2α^{k−1}, so α r_k/(1 − α) ≤ 2α^k/(1 − α) ≤ tol once α^k ≤ tol(1 − α)/2. ∎

*EXP-009.* All 10 (graph, α) instances stop within k\*. On the copying-model graph (a DAG plus teleportation) power iteration stopped after 17–37 iterations even at α = 0.99, where k\* = 2,819. The bound is a worst case, and acyclic link structure converges far faster (OBS-015).

### CGT-PROP-010 Grammar-constrained random surfer *(Proposition; elementary; proposed model, novelty unverified)*

Given an edge-labelled graph, a DFA D over labels, damping α and uniform teleportation to V × {q₀}, define the Markov chain on V × Q:
- from (u, q), with probability α move uniformly along an edge (u, a, w) with δ(q, a) defined, to (w, δ(q, a));
- with probability 1 − α, or when no such edge exists, jump to (w, q₀) with w uniform.

The *constrained rank* of w is Σ_q π(w, q). Then:
- (a) only states reachable from V × {q₀} matter, and there are at most |Q|·n of them;
- (b) one iteration costs at most |Q|·m edge operations;
- (c) π is unique and power iteration obeys THM-008 on the product chain;
- (d) for the one-state universal DFA, the constrained rank equals PageRank of the underlying multigraph.

*Proof.* (a) and (b) hold by the product construction, as in THM-001. (c) is THM-008 with teleport vector (1/n)·1_{V×{q₀}}. (d) With one state the chain is the surfer chain itself. ∎

*Checks.* In EXP-010, iterative constrained ranks match a direct linear solve of the materialized product chain to within 9·10⁻¹¹ (L1). The universal case equals PageRank to 10⁻⁹.

*Relationship.* This is the product of a Markov chain with an automaton, a standard construction in probabilistic model checking (e.g. Baier & Katoen 2008, metadata verified, section not located). It is close in spirit to meta-path-constrained measures in heterogeneous networks (PathSim; Sun et al. 2011) and to personalized PageRank (Haveliwala 2002). Whether this exact ranking model has been published is **unknown** (OPEN-011).

### Session 2 empirical observations

| ID | Experiment | Observation |
|---|---|---|
| CGT-OBS-013 | EXP-008 | Heap-shaped tree, n = 10⁶, words generated as walks (≈ 90% of starts defined). The compiled word costs 5 operations per application against 16, 118, 933 and 7,420 step-by-step operations for L = 8, 64, 512, 4,096. Break-even comes after ≈ 2.2–2.9 applications. With *random* words most starts fall off the tree within a few steps (early exit), and break-even rises to 12–131 applications. The workload again decides the measured advantage. |
| CGT-OBS-014 | EXP-008 | Random pointer tree, n = 20,000. Tabulating ⟦w⟧ by simulation costs 1.4·10⁵–3.2·10⁵ pointer steps and n words of space. Walk-generated words are defined at 75% (L = 8), 4.5% (L = 64) and 0.1% (L = 512) of nodes. On arbitrary shapes, move semantics is non-uniform, which is the phenomenon THM-007 lower-bounds. |
| CGT-OBS-015 | EXP-009 | Power iteration respected k\* and the certified bound on all instances; the true error was 1.1–200× below the bound. Copying (acyclic) graph: 17–37 iterations for α ∈ [0.5, 0.99]. Block graph with cycles: 27 → 485 iterations as α goes 0.5 → 0.99, growing roughly like 1/(1 − α). |
| CGT-OBS-016 | EXP-009 | Gauss–Seidel used fewer sweeps than power iteration on the cyclic block graph for α ≤ 0.95 (e.g. 56 vs 104 at α = 0.85), but *more* on the acyclic copying graph (98 vs 28 at α = 0.85; 1,561 vs 37 at α = 0.99). On a 2,000-vertex DAG, reversing the vertex order cut GS sweeps from 110 to 34. Power iteration is order-invariant (80 iterations under both orderings, identical edge operations). |
| CGT-OBS-017 | EXP-009 | Warm start after k random insertions on n = 3,000: 27 vs 38 iterations at k = 1, 31 vs 35 at k = 1,000, and no saving at k = 10,000 (ranking L1 shift 0.51). |
| CGT-OBS-018 | EXP-010 | Constrained ranks: product states 500–18,872, always ≤ \|Q\|·n. Every non-universal language moved the ranking: L1 distance to PageRank 0.14–0.40, and top-10 overlap 5–9 of 10 (5 at n = 500 for both 'no c' and 'alternate'). The universal language gives overlap 10 and distance 0, as PROP-010(d) requires. Edge-operation cost relative to PageRank ranges from 0.46× (selective languages prune edges) to 6.4× (a 4-state length-bounded language). |

---

## D. Errata (audit of 2026-10-08, session 2)

The original session-1 text is preserved in git history (commit `1221dec`). Each correction below was made in place and is listed here with its reason.

| ID | Location | Original | Correction | Kind |
|---|---|---|---|---|
| E-001 | THM-004(c) | "depth is ℓ … and ⌈log₂ ℓ⌉ (each plus one confirming round)" | ℓ − 1 productive rounds (linear) vs ⌈log₂ ℓ⌉ (doubling), plus one confirming round. The measured 63 vs 7 at n = 64 (ℓ = 63) matches the corrected statement, not the original. | off-by-one in a statement; proof unaffected |
| E-002 | THM-001(a) | O(\|Q\|·(n + m)) | O(\|Q\|·(\|Σ\|·n + m)) | missing term in the bound |
| E-003 | COR-002b | information content asserted without showing that distinct forests have distinct answers | justification added | incomplete proof |
| E-004 | PROP-006(2) | collapse to the second level attributed to Karp & Lipton alone | attribution qualified (Sipser's improvement) | attribution |
| E-005 | OBS-001 | presented as a measured constant | marked as a cost-model assignment; wall-clock is the independent evidence | evidence status |
| E-006 | session-1 code comments (`experiments/cgt/core.py`, `experiments/exp004_forest_dag.py`) | cite `CGT-PROP-003` (bound on product states) and `CGT-PROP-007` (update growth of shared forests); neither ID was ever defined in the ledger | the results meant are THM-001(a) and THM-005 respectively. The session-1 code is kept unchanged as historical evidence (D-013), and the numbers PROP-003, PROP-004 and PROP-007 stay unassigned so that no ID is reused with a different meaning. Found by a release consistency scan, end of session 2 | dangling identifier |
