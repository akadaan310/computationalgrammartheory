# Hypothesis Ledger

Status values: **open**, **supported** (evidence agrees and no counterevidence; not proved), **established** (proved; see the theorem), **partly supported**, **rejected**, **reformulated** (superseded by a sharper statement, kept for history).

---

### CGT-H-000 The originating conjecture *(A. Kadaan; Conjecture)*
- **Statement.** Computational structures possess grammars through which their valid operations, paths and outcomes can be expressed and systematically derived, and these grammars can become operational components of computation.
- **Status.** **Reformulated** into H-001 … H-010. Its *descriptive* half is established as a definition plus PROP-001: every structure with a move signature has an operational grammar, and its semantics is compositional. Its *operational* half ("becomes part of the machinery") is supported conditionally: the grammar drives computation through products (THM-001), addresses (THM-003), fixpoints (THM-004) and sharing (THM-005). Its strongest form ("dramatically easier, near-constant resolution") is **rejected** as a general claim (PROP-006, NEG-009).

### CGT-H-001 Arithmetic address grammars
- **Statement.** An address grammar with an arithmetic numeration answers ancestor and LCA queries in O(1) word operations without auxiliary preprocessing, but only for shape classes with h = O(w). The advantage is a property of density, not of grammar per se.
- **Motivation.** The researcher's observation that addresses can carry operations.
- **Assumptions.** Word RAM, msb instruction.
- **Test.** EXP-001. Falsified if heap LCA cost grows with n on complete trees, or stays O(1) on paths.
- **Evidence.** OBS-001: constant 4 ops up to n = 65,536 on complete and random BSTs; grows linearly in h on paths.
- **Counterevidence.** None.
- **Status.** **Established** as THM-003.
- **Next question.** Which other structures (grids, de Bruijn graphs, Cayley graphs) admit dense arithmetic addressing? See OPEN-002.

### CGT-H-002 Grammar evaluation is closure computation
- **Statement.** Evaluating the path grammar P → E | E P to fixpoint does the work of computing the transitive closure. It does not reduce work.
- **Test.** EXP-002, EXP-007. Falsified if firings are asymptotically below the closure size.
- **Evidence.** The exact firing formula (THM-004a) holds on all 12 instances. Firings ≥ |P⁺| always.
- **Status.** **Established** (THM-004).

### CGT-H-003 Precomputed path grammars: break-even and incompressibility
- **Statement.** A closure-type index pays off only after Q\* = B/(q₀ − q₁) queries, and its space cannot be compressed below ~n²/4 bits on general digraphs.
- **Test.** EXP-002. Falsified if zlib compresses bipartite closures well below n²/4.
- **Evidence.** OBS-004 (Q\* from 4 to 27,000), OBS-005.
- **Status.** **Established** for the space half (THM-002). The break-even half is a definition plus measurement (PROP-005).

### CGT-H-004 Restricted classes: the structural grammar is the index
- **Statement.** On forests, the nesting structure (interval labels) gives O(1) reachability with O(n) build and O(n log n) bits.
- **Test.** EXP-002, with correctness checked against BFS.
- **Status.** **Supported**, and known (Agrawal, Borgida & Jagadish 1989). COR-002b shows it matches the class's information content.

### CGT-H-005 Constraint pruning depends on (ℒ, structure) jointly
- **Statement.** Grammatical constraints reduce explored states only when ℒ is restrictive relative to the structure. For permissive ℒ they cost up to a factor |Q|.
- **Test.** EXP-003. Falsified if product search is never larger than unconstrained search.
- **Evidence.** OBS-006: ratio 0.003 … 5.000.
- **Status.** **Established** (THM-001 b, c).

### CGT-H-006 Constraints cannot be applied after the search
- **Statement.** "Search unconstrained, then filter" is not a correct substitute for constrained search.
- **Evidence.** OBS-007.
- **Status.** **Supported.** Trivially true in principle, since reachability forgets which label words were used. Quantified in EXP-003.

### CGT-H-007 Sharing is real but fragile
- **Statement.** A minimal-DAG grammar is small exactly when there are many repeated complete subtrees. Access costs O(depth × degree). Updates inflate it by up to depth + 1 rules each.
- **Test.** EXP-004.
- **Status.** **Established** for the inflation part (THM-005). **Supported** for the rest (OBS-008).
- **Next question.** Are there dynamic grammar-compressed tree representations with bounded inflation? See OPEN-004.

### CGT-H-008 No universally best resolution strategy under updates
- **Statement.** The cheapest strategy depends on the query/update ratio, the deletion share and query repetitiveness.
- **Test.** EXP-005. Falsified if one strategy wins every workload.
- **Evidence.** OBS-009: 4 winners in 9 workloads.
- **Status.** **Supported.**

### CGT-H-009 Solution grammars for hard problems are large
- **Statement.** For random 3-CNF near the threshold, the grammar of satisfying assignments grows exponentially in k. For 2-CNF, tractability comes from the restriction, not from a small solution grammar.
- **Test.** EXP-006.
- **Evidence.** OBS-011: growth is fast, but exponential and polynomial fits cannot be told apart for k ≤ 28. 2-CNF solution automata also grow.
- **Status.** **Open** for the first half: empirically undecided, and no proof attempted. **Supported** for the second half.

### CGT-H-010 Grammar shape is a cost parameter
- **Statement.** Two grammars with the same semantics can have asymptotically different resolution costs.
- **Evidence.** THM-004: Θ(n²) vs Θ(n³) work and Θ(n) vs Θ(log n) depth on paths.
- **Status.** **Established** (one instance). Known in Datalog and parallel-algorithms practice.

### CGT-H-011 Unifying specification across structures
- **Statement.** One formalism (operational grammars, DEF-003) can specify valid operations for sequential, hierarchical, relational and state structures.
- **Evidence.** The Python core (`experiments/cgt/core.py`) expresses trees ({L,R,U}), labelled graphs (label relations + DFA) and the forest/DAG navigation as instances. The taxonomy in `BOOK_OUTLINE.md` Part III maps every mandated family.
- **Status.** **Supported** as a *specification* claim. Unification of *specification* is not unification of *efficient execution* (OBS-010).

### CGT-H-012 Full accounting removes most apparent advantages
- **Statement.** Once preprocessing, memory, updates and output are counted, most apparent grammatical advantages either vanish or reduce to known mechanisms.
- **Evidence.** OBS-002 (workload artifact), OBS-004 (break-even up to 27,000 queries), OBS-008 (access 16–32,710× costlier than explicit arrays), OBS-009.
- **Status.** **Supported.**
