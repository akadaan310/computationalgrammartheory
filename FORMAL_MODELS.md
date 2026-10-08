# Formal Models

## 1. Machine model

Unless stated otherwise, the model is the **word RAM**: words of w bits with w ≥ log₂ n, unit-cost arithmetic, bitwise operations, shifts and comparisons on single words, and random access to memory cells. An operation on a b-bit integer costs ⌈b/w⌉ word operations (multi-precision). Every "O(1)" claim in this repository means O(1) word operations *under this model*, with the parameters that are allowed to grow stated explicitly.

The experiments run in CPython. Wall-clock time there is dominated by interpreter constants, so every experiment reports **counted elementary steps** under an explicitly stated cost model. Wall-clock time is recorded in the raw JSON only as a secondary check. Flat timings over a small range are never taken as evidence of O(1) (charter §2).

## 2. The three layers

For an operational grammar G = (Σ, 𝔄, ⟦·⟧, ℒ), three different claims are kept apart:

| Layer | Question | Formal object | Example where it is true but the next layer fails |
|---|---|---|---|
| **Syntax** | Is the expression valid? | w ∈ ℒ | `LLR` is a valid address word, but the node may not exist |
| **Semantics** | What does it denote in this structure? | ⟦w⟧ ⊆ A × A; ⟦ℒ⟧(x) | a path matching a regular constraint exists, but finding one *simple* such path is NP-hard (Mendelzon & Wood 1995) |
| **Execution** | What does it cost to evaluate, derive or resolve? | cost profile 𝒞 (DEF-005) | reachability is O(1) to *retrieve* from a closure, which costs Θ(n²) bits to store (THM-002) |

CGT-PROP-002 (`RESULTS.md`) shows that all three layers are independent: each combination of truth values is realized.

## 3. Grammar-parameterized cost notation (candidate framework)

A cost profile is written

  T_X(n, g, q, u, o)

for X ∈ {build, query, update}, together with S(n, g) for space, where:

| Symbol | Meaning |
|---|---|
| n | size of the underlying structure (\|A\| plus number of tuples) |
| g | size of the grammar: total length of productions, or DFA states × \|Σ\| |
| q | size of the query description (word length, size of a constraint automaton) |
| u | update parameters: number of updates, and *update distance* (number of grammar rules invalidated) |
| o | output size |

Grammar-specific parameters used so far:

| Parameter | Symbol | Where it matters |
|---|---|---|
| automaton states of ℒ | \|Q\| | product search is Θ(\|Q\|·(n + m)) in the worst case (THM-001) |
| derivation depth | d | access in structural grammars is O(d·Δ), where Δ is the maximum degree (EXP-004) |
| address bit length | h + 1 | heap-arithmetic cost is ⌈(h+1)/w⌉ (THM-003) |
| sharing ratio | g/n | compression from a minimal DAG (EXP-004) |
| update inflation | Δg per update | ≤ d + 1 for minimal DAGs, with matching lower bounds (THM-005) |
| parallel derivation depth | rounds | right-linear vs doubling path grammars (THM-004) |

*Status.* This is notation, not a theory. Whether it gives distinctions that parameterized complexity, succinct data structures and cell-probe complexity do not already give is open (CGT-OPEN-005). Session 1 found **no** case where it does; every result so far is expressible in existing frameworks.

## 4. Total cost accounting for repeated queries

For a workload with Q queries and U updates:

  T_total = T_build + Σ_{i=1..Q} T_query,i + Σ_{j=1..U} T_update,j (+ output costs)

The **break-even query volume** of a scheme with build cost B and per-query cost q₁, against a baseline with no preprocessing and per-query cost q₀ > q₁, is

  Q* = B / (q₀ − q₁).

Under updates that invalidate the index, the condition applies **per epoch** (CGT-PROP-005).

## 5. The status of the grammar in complexity statements

When a grammar Γ(x) is attached to a problem instance x, a statement about cost is meaningful only after the following are fixed:

1. Is Γ part of the input, computed from the input, or supplied as advice that depends only on |x|?
2. What size bound applies to it: polynomial, exponential or unbounded?
3. Can Γ encode the answer?
4. Is Build counted?

CGT-PROP-006 uses this checklist to settle the mandate's P/NP questions within the standard models.
