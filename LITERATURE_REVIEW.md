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

---

## Session 2 update (2026-10-08): the book bibliography

The canonical bibliography is now `book/content/bibliography.json`. Every entry there carries a verification status and a note on what was consulted, and the book build fails on any citation key that is not in it. This section mirrors that file, so the ledger and the book cannot disagree about what was checked.

Legend:
- **[V]** bibliographic metadata (authors, title, venue, year) checked by web search against publisher, DBLP or institutional records;
- **[S]** known only through secondary sources (textbooks, surveys, citing papers);
- **[U]** not verified.

**No full text was read for any entry.** Statements that the book attributes to these works are standard textbook content, cited for orientation; they are not claims to have checked the original proofs.

| Key | Year | Authors | Title | Venue | Status |
|---|---|---|---|---|---|
| `ford1956` | 1956 | L. R. Ford Jr. | Network flow theory | RAND Corporation Paper P-923 | [S] |
| `kruskal1956` | 1956 | J. B. Kruskal | On the shortest spanning subtree of a graph and the traveling salesman problem | Proceedings of the AMS 7:48–50 | [V] |
| `prim1957` | 1957 | R. C. Prim | Shortest connection networks and some generalizations | Bell System Technical Journal 36(6):1389–1401 | [V] |
| `bellman1958` | 1958 | R. Bellman | On a routing problem | Quarterly of Applied Mathematics 16(1):87–90 | [V] |
| `dijkstra1959` | 1959 | E. W. Dijkstra | A note on two problems in connexion with graphs | Numerische Mathematik 1:269–271 | [V] |
| `avl1962` | 1962 | G. M. Adelson-Velsky, E. M. Landis | An algorithm for the organization of information | Doklady Akademii Nauk SSSR (English translation in Soviet Mathematics Doklady) | [S] |
| `hoare1962` | 1962 | C. A. R. Hoare | Quicksort | The Computer Journal 5(1):10–16 | [V] |
| `kahn1962` | 1962 | A. B. Kahn | Topological sorting of large networks | Communications of the ACM 5(11):558–562 | [S] |
| `williams1964` | 1964 | J. W. J. Williams | Algorithm 232: Heapsort | Communications of the ACM 7(6):347–348 | [V] |
| `knuth1968` | 1968 | D. E. Knuth | Semantics of context-free languages | Mathematical Systems Theory 2(2):127–145 | [V] |
| `tarjan1972` | 1972 | R. E. Tarjan | Depth-first search and linear graph algorithms | SIAM Journal on Computing 1(2):146–160 | [V] |
| `kleitman1975` | 1975 | D. J. Kleitman, B. L. Rothschild | Asymptotic enumeration of partial orders on a finite set | Transactions of the AMS 205:205–220 | [V] |
| `tarjan1975` | 1975 | R. E. Tarjan | Efficiency of a good but not linear set union algorithm | Journal of the ACM 22(2):215–225 | [V] |
| `kmp1977` | 1977 | D. E. Knuth, J. H. Morris Jr., V. R. Pratt | Fast pattern matching in strings | SIAM Journal on Computing 6(2):323–350 | [V] |
| `aspvall1979` | 1979 | B. Aspvall, M. F. Plass, R. E. Tarjan | A linear-time algorithm for testing the truth of certain quantified Boolean formulas | Information Processing Letters 8(3):121–123 | [V] |
| `downey1980` | 1980 | P. J. Downey, R. Sethi, R. E. Tarjan | Variations on the common subexpression problem | Journal of the ACM 27(4):758–771 | [V] |
| `karp1980` | 1980 | R. M. Karp, R. J. Lipton | Some connections between nonuniform and uniform complexity classes | Proc. 12th ACM STOC, pp. 302–309 | [S] |
| `tarjan1981fast` | 1981 | R. E. Tarjan | Fast algorithms for solving path problems | Journal of the ACM 28(3):594–614 | [V] |
| `tarjan1981unified` | 1981 | R. E. Tarjan | A unified approach to path problems | Journal of the ACM 28(3):577–593 | [V] |
| `harel1984` | 1984 | D. Harel, R. E. Tarjan | Fast algorithms for finding nearest common ancestors | SIAM Journal on Computing 13(2):338–355 | [V] |
| `italiano1986` | 1986 | G. F. Italiano | Amortized efficiency of a path retrieval data structure | Theoretical Computer Science 48:273–281 | [V] |
| `schieber1988` | 1988 | B. Schieber, U. Vishkin | On finding lowest common ancestors: simplification and parallelization | SIAM Journal on Computing 17(6):1253–1262 | [V] |
| `agrawal1989` | 1989 | R. Agrawal, A. Borgida, H. V. Jagadish | Efficient management of transitive relationships in large data and knowledge bases | Proc. ACM SIGMOD 1989, pp. 253–262 | [V] |
| `jacobson1989` | 1989 | G. Jacobson | Space-efficient static trees and graphs | Proc. 30th IEEE FOCS, pp. 549–554 | [V] |
| `yannakakis1990` | 1990 | M. Yannakakis | Graph-theoretic methods in database theory | Proc. 9th ACM PODS, pp. 230–242 | [V] |
| `epstein1992` | 1992 | D. B. A. Epstein, J. W. Cannon, D. F. Holt, S. V. F. Levy, M. S. Paterson, W. P. Thurston | Word Processing in Groups | Jones and Bartlett (later A K Peters) | [V] |
| `fenwick1994` | 1994 | P. M. Fenwick | A new data structure for cumulative frequency tables | Software: Practice and Experience 24(3):327–336 | [V] |
| `khoussainov1995` | 1995 | B. Khoussainov, A. Nerode | Automatic presentations of structures | Logic and Computational Complexity, LNCS 960 | [U] |
| `mendelzon1995` | 1995 | A. O. Mendelzon, P. T. Wood | Finding regular simple paths in graph databases | SIAM Journal on Computing 24(6):1235–1258 | [V] |
| `kozen1997` | 1997 | D. Kozen | Kleene algebra with tests | ACM Transactions on Programming Languages and Systems 19(3):427–443 | [V] |
| `brin1998` | 1998 | S. Brin, L. Page | The anatomy of a large-scale hypertextual Web search engine | Computer Networks and ISDN Systems 30:107–117 | [V] |
| `reps1998` | 1998 | T. Reps | Program analysis via graph reachability | Information and Software Technology 40(11–12):701–726 | [V] |
| `page1999` | 1999 | L. Page, S. Brin, R. Motwani, T. Winograd | The PageRank citation ranking: Bringing order to the Web | Technical Report 1999-66, Stanford InfoLab | [S] |
| `barrett2000` | 2000 | C. Barrett, R. Jacob, M. Marathe | Formal-language-constrained path problems | SIAM Journal on Computing 30(3):809–837 | [V] |
| `bender2000` | 2000 | M. A. Bender, M. Farach-Colton | The LCA problem revisited | Proc. LATIN 2000, LNCS 1776, pp. 88–94 | [V] |
| `blumensath2000` | 2000 | A. Blumensath, E. Grädel | Automatic structures | Proc. 15th IEEE LICS, pp. 51–62 | [V] |
| `darwiche2002` | 2002 | A. Darwiche, P. Marquis | A knowledge compilation map | Journal of Artificial Intelligence Research 17:229–264 | [V] |
| `haveliwala2002` | 2002 | T. H. Haveliwala | Topic-sensitive PageRank | Proc. 11th International World Wide Web Conference (WWW 2002) | [V] |
| `buneman2003` | 2003 | P. Buneman, M. Grohe, C. Koch | Path queries on compressed XML | Proc. 29th VLDB, pp. 141–152 | [V] |
| `cohen2003` | 2003 | E. Cohen, E. Halperin, H. Kaplan, U. Zwick | Reachability and distance queries via 2-hop labels | SIAM Journal on Computing 32(5):1338–1355 | [V] |
| `haveliwala2003` | 2003 | T. Haveliwala, S. Kamvar | The second eigenvalue of the Google matrix | Technical report, Stanford University | [S] |
| `kamvar2003` | 2003 | S. Kamvar, T. Haveliwala, C. Manning, G. Golub | Exploiting the block structure of the Web for computing PageRank | Technical Report 2003-17, Stanford University | [S] |
| `langville2004` | 2004 | A. N. Langville, C. D. Meyer | Deeper inside PageRank | Internet Mathematics 1(3):335–380 | [V] |
| `bianchini2005` | 2005 | M. Bianchini, M. Gori, F. Scarselli | Inside PageRank | ACM Transactions on Internet Technology 5(1):92–128 | [V] |
| `charikar2005` | 2005 | M. Charikar, E. Lehman, D. Liu, R. Panigrahy, M. Prabhakaran, A. Sahai, A. Shelat | The smallest grammar problem | IEEE Transactions on Information Theory 51(7):2554–2576 | [V] |
| `langville2006` | 2006 | A. N. Langville, C. D. Meyer | Google's PageRank and Beyond: The Science of Search Engine Rankings | Princeton University Press (ISBN 978-0-691-12202-1) | [V] |
| `baier2008` | 2008 | C. Baier, J.-P. Katoen | Principles of Model Checking | MIT Press (ISBN 978-0-262-02649-9) | [V] |
| `bille2011` | 2011 | P. Bille, G. M. Landau, R. Raman, K. Sadakane, S. R. Satti, O. Weimann | Random access to grammar-compressed strings | Proc. 22nd ACM-SIAM SODA, pp. 373–389 | [V] |
| `sun2011` | 2011 | Y. Sun, J. Han, X. Yan, P. S. Yu, T. Wu | PathSim: Meta path-based top-k similarity search in heterogeneous information networks | Proceedings of the VLDB Endowment 4(11):992–1003 | [V] |
| `verbin2013` | 2013 | E. Verbin, W. Yu | Data structure lower bounds on random access to grammar-compressed strings | Proc. CPM 2013 (LNCS) | [V] |
| `lohrey2015` | 2015 | M. Lohrey | Grammar-based tree compression | Proc. DLT 2015 (LNCS) | [V] |
| `vaswani2017` | 2017 | A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, I. Polosukhin | Attention is all you need | Advances in Neural Information Processing Systems 30, pp. 5998–6008 | [V] |
| `lewis2020` | 2020 | P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, D. Kiela | Retrieval-augmented generation for knowledge-intensive NLP tasks | Advances in Neural Information Processing Systems 33 | [V] |
| `malkov2020` | 2020 | Yu. A. Malkov, D. A. Yashunin | Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs | IEEE Transactions on Pattern Analysis and Machine Intelligence | [S] |
| `clrs2022` | 2022 | T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein | Introduction to Algorithms, 4th edition | MIT Press (ISBN 978-0-262-04630-5) | [V] |

Totals: 55 entries; 46 [V], 8 [S], 1 [U].

### Areas reviewed in session 2 (metadata level) and what they changed
- **PageRank and Markov chains** (Brin–Page; Page et al.; Langville–Meyer; Bianchini–Gori–Scarselli; Haveliwala; Kamvar et al.). These sources supply the convergence theory that Chapter 15 restates, with its own proofs (THM-008, PROP-009). They are also why the constrained surfer (PROP-010) is labelled *proposed*, not new: topic-sensitive and personalized PageRank are close relatives. Nothing in the book claims to improve any production search system.
- **Model checking and probabilistic systems** (Baier–Katoen). The product of a Markov chain with an automaton is the standard construction for probabilistic model checking. PROP-010 is therefore an application of known machinery to ranking, and OPEN-011 asks whether even that application is already published.
- **Heterogeneous-network ranking** (Sun et al. 2011, meta-paths). This is the closest found prior work to language-constrained ranking.
- **Automatic structures** (Khoussainov–Nerode **[U]**; Blumensath–Grädel **[V]**). This is the closest known framework to compiled move words (THM-006). OPEN-010 records the novelty check that is still owed.
- **Succinct and implicit trees** (Jacobson 1989), **LCA** (Harel–Tarjan; Schieber–Vishkin; Bender–Farach-Colton) and **range structures** (Fenwick). These are the baselines of Chapters 5, 11 and 13.
- **AI systems** (Vaswani et al. 2017; Lewis et al. 2020; Malkov–Yashunin **[S]**). These are cited only for the architectures described in Chapter 17. The chapter makes no empirical claim about them.
- **Classical algorithms** (Dijkstra, Bellman, Ford, Kruskal, Prim, Kahn, Tarjan, KMP, Hoare, Williams, AVL, Aspvall–Plass–Tarjan). These are the baselines of Part III.

### Debts still open
1. Full-text reading of the primary sources behind the candidate contributions: automatic structures and transition monoids for THM-006; probabilistic model checking and meta-path ranking for PROP-010.
2. Attribute grammars, graph grammars and Kleene algebra with tests were cited, but not reviewed in depth (§11 above). Publication blocker B-3 stays open.
3. The [S] and [U] entries should be checked against the originals before any external publication.
