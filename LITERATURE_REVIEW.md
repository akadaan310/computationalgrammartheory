# Literature Review (session 1, baseline)

**Method and limits.** This is a *baseline* review: enough to keep established knowledge apart from proposed contributions. It is not a systematic survey.

Each reference carries a verification mark:

- **[V]**: bibliographic details (authors, title, venue, year, pages where given) checked in session 1 by web search against publisher, DBLP, ACM/SIAM/AMS, or institutional records. Only abstracts and metadata were read, not full texts. Statements about content are limited to what those abstracts support, or are flagged.
- **[U]**: cited from general knowledge and *not yet verified*. Do not publish until checked.

No paper, author, theorem or quotation has been invented. Where a detail could not be confirmed, that is stated.

---

## 1. Formal language and automata theory
- **Existing.** Grammars (Σ, N, P, S), the Chomsky hierarchy, regular/context-free closure and decision properties, and the transition monoids of automata.
- **CGT adopts** these as the *finite descriptions* of admissibility languages ℒ (DEF-003) and the transition monoid T(G) (DEF-007).
- **CGT changes** the semantic target: words denote relations on a structure, not strings in a language.
- **New?** No. This is the relational semantics of labelled transition systems.

## 2. Language-constrained paths and graph query languages
- Mendelzon, A. O. & Wood, P. T. (1995). *Finding regular simple paths in graph databases.* SIAM J. Computing 24(6):1235–1258. Conference version VLDB 1989, pp. 185–193. **[V]**
  - Regular *simple* path queries are NP-complete in general.
  - They are polynomial under a "no conflicts" condition.
  - This is used in PROP-002 and THM-001.
- Barrett, C., Jacob, R. & Marathe, M. (2000). *Formal-language-constrained path problems.* SIAM J. Computing 30(3):809–837. Conference version SWAT 1998, LNCS 1432. **[V]**
  - Shortest paths constrained by a context-free language are polynomial.
  - Better bounds hold for regular languages.
  - Simple-path variants are NP-hard even for fixed simple regular languages.
- Yannakakis, M. (1990). *Graph-theoretic methods in database theory.* PODS 1990, pp. 230–242. **[V]** (bibliographic only). It is commonly credited with the CFL-reachability formulation **[U for this attribution]**.
- Reps, T. (1998). *Program analysis via graph reachability.* Information & Software Technology 40(11–12):701–726. **[V]** CFL-reachability unifies slicing, some dataflow problems, shape analysis and points-to analysis.
- **Relationship.** For regular ℒ, the CGT operational grammar is exactly the setting of regular path queries. For context-free ℒ it is CFL-reachability. THM-001(a) is standard. THM-001(b)–(c), which give the tight factor-|Q| cost and unbounded pruning, are elementary and probably folklore.
- **CGT contributes** only the explicit cost framing: the constraint as a pruning mechanism (M-PRUNE) with a tight worst case.

## 3. Algebraic path problems and path expressions
- Tarjan, R. E. (1981). *A unified approach to path problems.* J. ACM 28(3):577–593. **[V]**
- Tarjan, R. E. (1981). *Fast algorithms for solving path problems.* J. ACM 28(3):594–614. **[V]**
  - A *path expression* is a regular expression representing all paths from a source.
  - Constructing path expressions is "in some sense the most general path problem".
- **Relationship.** This is the most important prior art for the mandate's request (§9) to treat "paths as grammatical objects". Tarjan already treats path sets as regular expressions (grammars) and derives algorithms from them. CGT's PROP-001 restates the semantic basis. THM-004 adds an exact work count for one evaluation strategy.
- **New?** Treating paths grammatically is **not new**. Any CGT claim in this area must be measured against Tarjan's framework and the closed-semiring literature **[U: Aho, Hopcroft & Ullman 1974; Lehmann 1977]**.

## 4. Reachability indexing and labeling
- Agrawal, R., Borgida, A. & Jagadish, H. V. (1989). *Efficient management of transitive relationships in large data and knowledge bases.* SIGMOD 1989, pp. 253–262. **[V]** Interval labels on spanning trees, compressed closure, and incremental updates. Used in EXP-002 (M4) and COR-002b.
- Cohen, E., Halperin, E., Kaplan, H. & Zwick, U. (2003). *Reachability and distance queries via 2-hop labels.* SIAM J. Computing 32(5):1338–1355. Conference version SODA 2002. **[V]** Labels from 2-hop covers, with near-optimal cover construction.
- Italiano, G. F. (1986). *Amortized efficiency of a path retrieval data structure.* Theoretical Computer Science 48:273–281. **[V]** Incremental transitive closure with O(n) amortized cost per insertion, as reported by later work.
- **Relationship.** THM-002's counting bound explains *why* general-graph reachability labels cannot all be small. Labeling schemes are the established form of "grammatical indexing" for reachability.

## 5. Tree indexing: LCA and navigation
- Bender, M. A. & Farach-Colton, M. (2000). *The LCA problem revisited.* LATIN 2000, LNCS 1776, pp. 88–94. **[V]** O(n) preprocessing and O(1) LCA queries, via the reduction to ±1 RMQ.
- Harel & Tarjan (1984) and Schieber & Vishkin (1988) are the classical O(1)-query LCA results; the second includes the complete-binary-tree (XOR) technique. **[U]**
- The heap numbering of complete binary trees goes back at least to Williams' heapsort (1964). **[U]**
- **Relationship.** THM-003 packages these classical facts into an exact scope statement for arithmetic addressing.

## 6. Grammar-based compression of strings and trees
- Charikar, M., Lehman, E., Liu, D., Panigrahy, R., Prabhakaran, M., Sahai, A. & Shelat, A. (2005). *The smallest grammar problem.* IEEE Trans. Information Theory 51(7):2554–2576. **[V]** Hardness and approximation of the smallest SLP.
- Bille, P., Landau, G. M., Raman, R., Sadakane, K., Satti, S. R. & Weimann, O. *Random access to grammar-compressed strings (and trees).* SODA 2011, pp. 373–389; arXiv:1001.1565. **[V]**
  - O(log N) random access with O(n) space for a grammar of size n.
  - Extends to navigation in grammar-compressed ordered trees.
  - A SIAM J. Comput. journal version exists, but its volume and pages are **unverified**.
- Verbin, E. & Yu, W. (2013). *Data structure lower bounds on random access to grammar-compressed strings.* CPM 2013; arXiv:1203.1080. **[V via arXiv and citing papers]** Polynomial-space grammar-based structures need roughly (log N)^{1−ε}/log S query time, in a specific parameter regime (per Duyster & Kociumaka, ICALP 2026). **[V, metadata]**
- Downey, P. J., Sethi, R. & Tarjan, R. E. (1980). *Variations on the common subexpression problem.* J. ACM 27(4):758–771. **[V]** Congruence closure on DAGs. This is the foundation of DAG (hash-consing) representations.
- Buneman, P., Grohe, M. & Koch, C. (2003). *Path queries on compressed XML.* VLDB 2003, pp. 141–152. **[V]** Shares identical subtrees and evaluates XPath-like queries on the compressed skeleton.
- Lohrey, M. (2015). *Grammar-based tree compression.* DLT 2015, LNCS, doi:10.1007/978-3-319-21500-6_3. **[V]** Survey of tree SLPs, compression bounds and algorithms on compressed trees. It is the source for "TSLPs can be exponentially more succinct than DAGs" (THM-005c context). **[U: exact statement to be checked in the survey text]**
- **Relationship.** M-SHARE is the established field of grammar-based compression. THM-005 (update inflation) is an elementary adversary argument. Dynamic grammar-compressed structures are an existing research area that must be reviewed before claiming anything (OPEN-004).

## 7. Automatic structures and automatic groups (closest to the "address as grammar" intuition)
- Khoussainov, B. & Nerode, A. (1995). *Automatic presentations of structures.* LCC 1994, LNCS 960. **[U: details not confirmed]** Independently: Hodgson's 1976 thesis, per Grädel's later tutorial **[V, secondary]**.
- Blumensath, A. & Grädel, E. (2000). *Automatic structures.* LICS 2000, pp. 51–62. **[V]** Structures presented by regular sets of words and synchronous automata, with effective first-order query evaluation.
- Epstein, D., Cannon, J., Holt, D., Levy, S., Paterson, M. & Thurston, W. (1992). *Word Processing in Groups.* Jones & Bartlett (later A K Peters). **[V]** Automatic groups: group elements as words, with multiplication by generators recognized by finite automata.
- **Relationship.** DEF-006 (grammatical addresses) is a special, cost-oriented case of these ideas:
  - an automatic presentation encodes elements as words of a regular language, with relations recognized by automata;
  - CGT adds the *word-RAM cost* of acting on numerals and the *density* parameter.

  This literature is the natural home for the researcher's original insight and should be the main lens of session 2 (OPEN-002).

## 8. Knowledge compilation (grammars of solutions)
- Darwiche, A. & Marquis, P. (2002). *A knowledge compilation map.* JAIR 17:229–264. **[V]** Compares target languages (OBDD, DNNF, …) by succinctness and polytime queries and transformations.
- Aspvall, B., Plass, M. F. & Tarjan, R. E. (1979). *A linear-time algorithm for testing the truth of certain quantified Boolean formulas.* Information Processing Letters 8(3):121–123. **[V]** 2-SAT and 2-QBF in linear time via SCCs.
- **Relationship.** EXP-006 is a small knowledge-compilation experiment. The "grammar of solutions" in Part VI of the mandate *is* knowledge compilation, and its central trade-off (succinctness vs polytime queries) is already mapped by Darwiche & Marquis.

## 9. Complexity theory: nonuniformity, advice, parameterization
- Karp, R. M. & Lipton, R. J. (1980). *Some connections between nonuniform and uniform complexity classes.* STOC 1980, pp. 302–309. **[V, via course notes and reference lists]** The journal version is titled *Turing machines that take advice* **[U]**. Used in PROP-006.
- Parameterized complexity (Downey & Fellows; Courcelle's theorem for bounded treewidth) **[U]**. Grammar-parameterized cost (FORMAL_MODELS §3) has to be compared against this field. So far no distinction has been found that it does not already capture.
- Cell-probe and succinct data structure lower bounds **[U: Jacobson 1989; Pătraşcu]**: THM-002 is a crude, information-theoretic special case.

## 10. Order enumeration
- Kleitman, D. J. & Rothschild, B. L. (1975). *Asymptotic enumeration of partial orders on a finite set.* Trans. AMS 205:205–220. **[V]** log₂(#posets on n elements) ~ n²/4, giving the asymptotic version of THM-002 for DAG closures.

## 11. Fields named in the mandate, not yet reviewed
Attribute grammars (Knuth 1968 **[U]**), graph grammars (handbook ed. Rozenberg 1997 **[U]**), term rewriting, abstract interpretation, Kleene algebra with tests (Kozen 1997 **[U]**), incremental computation, database query optimization, proof systems and program synthesis.

**Expected relevance:**
- Attribute grammars are the closest existing notion of grammar-carried computation over a tree. Session 2 must review them before CGT claims anything about "operations attached to productions".
- Graph grammars are the structural-grammar analogue for graphs.

---

## Summary: established knowledge vs proposed contributions

| Item | Established (by whom) | CGT contribution |
|---|---|---|
| Relational semantics of move words, compositional paths | Kleene algebra; Tarjan 1981 | restated (PROP-001) |
| Regular/CFL-constrained reachability | Mendelzon–Wood; Barrett–Jacob–Marathe; Yannakakis; Reps | tight factor-\|Q\| cost and unbounded-pruning examples (THM-001 b, c), elementary |
| Reachability labels and closure size | Agrawal et al.; Cohen et al.; Kleitman–Rothschild (asymptotic) | exact, non-asymptotic counting bound for retrieval-only schemes (THM-002), elementary, likely folklore |
| Heap numbering and O(1) LCA | classical [U]; Bender–Farach-Colton | exact scope statement of arithmetic addressing (THM-003) |
| Grammar compression, DAGs, SLPs | Downey–Sethi–Tarjan; Charikar et al.; Bille et al.; Lohrey | update-inflation adversary (THM-005), elementary |
| Linear vs non-linear recursion | Datalog folklore; parallel TC by squaring | exact firing count (THM-004a) |
| Grammars and P vs NP | Karp–Lipton; standard | boundary statement for the CGT setting (PROP-006) |
| Unified operational-grammar notation + cost profile + mechanism taxonomy | (no single source found) | DEF-003, DEF-005, DEF-009, CONJ-001: **the candidate contribution of session 1**, pending a deeper review |
