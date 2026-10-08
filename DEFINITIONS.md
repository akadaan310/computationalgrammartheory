# Definitions (provisional)

Every definition here is **provisional** (session 1). Each is marked as one of:

- *[standard]*: an established notion, restated in CGT notation;
- *[CGT, provisional]*: introduced by this investigation;
- *[CGT naming of standard notion]*: an existing idea under a CGT name, kept only when the name helps unify.

Rule followed throughout: existing terms are not redefined when an existing term already does the job.

---

## CGT-DEF-001 Computational structure *[standard]*

A *computational structure* is a finite relational structure 𝔄 = (A; R₁, …, R_k), possibly with labels and distinguished elements (roots, sources), together with a *representation* ρ(𝔄) ∈ {0,1}*: a concrete encoding such as adjacency lists, pointer records or an array. Its size n = |A|. The representation size |ρ(𝔄)| is counted in bits or in machine words.

*Remark.* The same structure has many representations. CGT keeps a structure (the mathematical object) separate from its representations (inputs to machines). Many apparent "grammar advantages" turn out to be changes of representation (`RESULTS.md`, CGT-OBS-010).

## CGT-DEF-002 Move signature and relational semantics *[standard: labelled transition system]*

A *move signature* is a finite alphabet Σ. An *interpretation* assigns each move a ∈ Σ a relation ⟦a⟧ ⊆ A × A. The pair (𝔄, ⟦·⟧) is a labelled transition system. The interpretation is *deterministic* if every ⟦a⟧ is a partial function.

*Examples.* Binary tree: Σ = {L, R, U} for left child, right child and parent. Edge-labelled graph: Σ is the set of edge labels. Linked list: Σ = {next, prev}. Array of length n: Σ = {+1, −1} (or the "jump" family +k).

## CGT-DEF-003 Operational grammar *[CGT, provisional]*

An *operational grammar* over a structure 𝔄 is a tuple

  **G = (Σ, 𝔄, ⟦·⟧, ℒ)**

where (Σ, ⟦·⟧) is a move signature with its interpretation (DEF-002) and ℒ ⊆ Σ* is the *admissibility language*. ℒ is given by a finite description, such as a DFA, an NFA or a context-free grammar. Its *class* (regular, context-free, …) is the class of the operational grammar.

- A word w ∈ Σ* is an **operation expression**.
- w is **syntactically admissible** iff w ∈ ℒ.
- The **semantics** of w is the relational composition ⟦w⟧ = ⟦a₁⟧ ; ⟦a₂⟧ ; … ; ⟦a_m⟧, with ⟦ε⟧ = id_A. For a language, ⟦ℒ⟧ = ⋃_{w∈ℒ} ⟦w⟧.
- w is **semantically realizable at x** iff ⟦w⟧(x) ≠ ∅.

*Why this is the right first object.* It covers paths (graphs), navigation (trees, lists), state transitions (automata as structures), admissible operation sequences (protocols, typestate) and addresses (DEF-006). It reduces cleanly to known theory: for regular ℒ it is a labelled transition system with a regular constraint, studied as regular path queries and formal-language-constrained path problems (`LITERATURE_REVIEW.md` §2). A conventional formal grammar G = (Σ, N, P, S) appears as the finite description of ℒ. What is added is the structure-dependent semantics ⟦·⟧ and the cost model (DEF-005).

## CGT-DEF-004 Structural grammar *[CGT naming of standard notion]*

A *structural grammar* for 𝔄 is a grammar H whose derivation, or unique generated object, *is* 𝔄 (or its representation). Examples: a minimal DAG of a tree (one nonterminal per distinct subtree), a straight-line program (SLP) for a string, a tree SLP, or a hyperedge-replacement graph grammar. Its size |H| is the total length of its productions.

*Distinction from DEF-003.* A structural grammar generates the **structure**. An operational grammar generates the **operations over** the structure. The two can be combined: navigation moves on a grammar-compressed tree form an operational grammar whose carrier is given by a structural grammar (CGT-EXP-004).

## CGT-DEF-005 Resolution scheme and cost profile *[standard notion, CGT packaging]*

Fix a query class 𝒬 over a class 𝒦 of structures. A *resolution scheme* is a triple of algorithms (Build, Query, Update) on a fixed machine model (default: word RAM, w = Θ(log n)). Its *cost profile* is

  **𝒞 = ( T_build, S, T_query, T_update, |out| )**

where each entry is a function of the parameters in `FORMAL_MODELS.md` §3: n (structure size), g (grammar size), q (query size), u (update parameters) and o (output size). A **grammatical index** is a resolution scheme whose Build takes the operational or structural grammar as input. A **grammar-based algorithm** is one whose control flow follows derivations: product constructions, fixpoint evaluation of productions, or descent through a structural grammar.

## CGT-DEF-006 Grammatical address, numeration, density *[CGT, provisional; related: automatic structures]*

Let G be deterministic and rooted at r ∈ A. The **address** of x ∈ A is the shortlex-least word addr(x) ∈ Σ* with ⟦addr(x)⟧(r) = x, when such a word exists. A **numeration** is an injective map ν from addresses to ℕ. The addressing is **arithmetic** if each move a acts on numerals by a function computable in O(⌈b/w⌉) word operations on b-bit numerals. Its **density** is

  δ = n / |{0, …, max ν}|.

*Example.* The heap numeration of binary trees, ν(w) = int("1"·w, 2), is arithmetic: left child is x ↦ 2x, right child is x ↦ 2x+1, parent is x ↦ ⌊x/2⌋. Its density is n/(2^{h+1}−1), where h is the height (CGT-THM-003).

*Motivation.* This is the formal counterpart of the researcher's original observation that an address can carry operational meaning (`PROVENANCE.md`). Closely related existing theory: automatic structures and automatic groups (`LITERATURE_REVIEW.md` §7).

## CGT-DEF-007 Transition monoid *[standard]*

T(G) = { ⟦w⟧ : w ∈ Σ* }, ordered by relational composition. When ⟦·⟧ is deterministic, T(G) is a monoid of partial functions on A. This is the standard transition monoid of an automaton, applied to structures. It is used in CGT-OPEN-002 to state when words can be "compiled" into constant-size operations.

## CGT-DEF-008 Information content of a query family *[standard idea, CGT notation]*

For a class 𝒦 of structures and a query family 𝒬, each 𝔄 ∈ 𝒦 induces an answer function f_𝔄 : 𝒬 → Ans. The **information content** is

  I(𝒦, 𝒬) = log₂ |{ f_𝔄 : 𝔄 ∈ 𝒦 }|.

## CGT-DEF-009 Mechanisms of advantage *[CGT, provisional]*

A *mechanism* is a reason why one resolution scheme beats another on a stated cost component. Session 1 identified five; this classification is a working hypothesis (CGT-CONJ-001):

| Code | Mechanism | Example in this work |
|---|---|---|
| **M-ARITH** | an arithmetic numeration of a dense address space replaces stored structure with computation | heap indexing (THM-003) |
| **M-PRE** | precomputation: answers are stored and later *retrieved* | transitive closure, LCA tables (THM-002) |
| **M-SHARE** | repeated substructure is represented once | minimal DAG, SLP (THM-005) |
| **M-RESTRICT** | a restriction on the instance class makes structure exploitable | interval labels on forests; 2-SAT |
| **M-PRUNE** | the admissibility language excludes moves before they are executed | product construction (THM-001) |

## CGT-DEF-010 Distinctions required by the mandate

| Term | Meaning in CGT | Status |
|---|---|---|
| conventional formal grammar | (Σ, N, P, S), generating a language ⊆ Σ* | standard |
| structural grammar | grammar generating the structure itself (DEF-004) | standard objects, CGT naming |
| operational grammar | moves + semantics + admissibility language (DEF-003) | CGT, provisional |
| computational semantics | ⟦·⟧ : Σ* → Rel(A), extended to languages | standard (relational semantics) |
| grammatical indexing | resolution scheme built from a grammar (DEF-005), including addresses (DEF-006) | CGT packaging |
| grammar-based algorithm | algorithm driven by derivations (DEF-005) | CGT packaging of standard techniques |
| grammar-parameterized complexity | cost profiles as functions of (n, g, q, u, o) and grammar parameters (`FORMAL_MODELS.md` §3) | CGT notation; relation to parameterized complexity in `LITERATURE_REVIEW.md` §9 |
