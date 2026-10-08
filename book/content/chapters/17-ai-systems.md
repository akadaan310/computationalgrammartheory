---
title: Computation Graphs, Retrieval, and Agent Systems
status: mixed
statusnote: Explicit models of modern systems with careful limits; one worked application (validating agent plans against admissibility languages) runs on the SDK. No claim is made about neural-network semantics or inference speed.
description: Where computational grammars apply to modern AI systems — computation graphs, attention masks, retrieval pipelines, vector search and agent workflows — and where they do not.
---

::: objectives
- Model a computation graph as a structural grammar and identify the mechanisms used by common compiler optimizations.
- Read attention masks as admissibility relations, and separate cost reductions from changes of the computed function.
- Model retrieval pipelines and agent workflows as transition systems with admissibility languages, and validate plans in the syntax layer before execution.
- Explain why approximate vector search is navigation without the guarantees of the earlier chapters.
- State precisely what a symbolic grammar does not capture about a learned model.
:::

## Ground rules {#sec:ground}

Modern AI systems invite loose analogies with grammars, and loose analogies invite exaggerated claims. This chapter therefore begins each section with an **explicit computational model** — what the elements, moves, semantics and costs are — and keeps three distinctions throughout:

1. **Exact versus approximate.** A method that computes the same function as the original is exact; one that computes a different function, however close, is approximate, and its error must be measured, not assumed.
2. **Symbolic structure versus learned semantics.** A grammar can describe *which* operations a system performs and in *what order*. It does not describe what a trained network's weights compute; nothing here claims that it does.
3. **Model results versus system results.** Word-RAM costs do not account for accelerators, memory bandwidth or batching; no claim about real inference speed is made.

## Computation graphs {#sec:compgraphs}

*Model.* A numerical program (a neural network's forward pass, say) is a DAG whose nodes are operations — matrix products, additions, nonlinearities — and whose edges carry tensors. Executing it means evaluating nodes in a topological order (Chapter 10).

In this book's terms a computation graph is a **structural grammar** of the computation: a straight-line program in which each node is a production combining earlier results. Familiar compiler optimizations then fall into the mechanism taxonomy:

| Optimization | What it does | Mechanism | Exact? |
|---|---|---|---|
| common-subexpression elimination | merges identical subgraphs | M-SHARE (minimal DAG \cite{downey1980}) | yes |
| constant folding | evaluates subgraphs with constant inputs at compile time | M-PRE | yes |
| operator fusion | merges adjacent nodes to avoid materializing intermediates | representation change (memory traffic) | yes |
| memory planning | reuses buffers whose lifetimes do not overlap | interval scheduling on the topological order | yes |
| quantization, pruning | changes the numerical operations | — | **no**: approximate |

The table's last row is the important one: some "optimizations" change the function computed. They are legitimate engineering, but they are approximations, and their effect on outputs must be evaluated, never assumed from the structure of the graph.

## Attention as a relation {#sec:attention}

*Model.* In self-attention \cite{vaswani2017}, each of $n$ token positions computes a weighted combination of values at other positions, with weights derived from query–key similarities. Structurally, attention evaluates a relation $R \subseteq [n] \times [n]$ — "position $i$ may attend to position $j$" — and costs $\Theta(|R|)$ similarity computations (times the head dimension). Full attention uses $R = [n] \times [n]$: $n^2$ pairs.

An **attention mask** is an admissibility relation. A causal mask admits $j \le i$, halving the pairs; a local window of width $k$ admits $|i - j| < k$, about $2kn$ pairs:

```python run
n, k = 4096, 128
full = n * n
causal = n * (n + 1) // 2
window = sum(min(n, i + k) - max(0, i - k + 1) for i in range(n))
causal_window = sum(min(i + 1, k) for i in range(n))
for name, pairs in [("full", full), ("causal", causal), ("window |i-j|<128", window), ("causal window", causal_window)]:
    print(f"{name:18s} {pairs:10d} pairs  ({pairs / full:6.2%} of full)")
```

```output
full                 16777216 pairs  (100.00% of full)
causal                8390656 pairs  (50.01% of full)
window |i-j|<128      1028224 pairs  ( 6.13% of full)
causal window          516160 pairs  ( 3.08% of full)
```

The cost reduction is real and exactly proportional to $|R|$ — this is pruning (M-PRUNE) or restriction (M-RESTRICT) in its simplest form. But the boundary is sharp: **restricting the relation changes the function**. A causal mask is part of the model's definition (it is how autoregressive models are specified and trained); a sparse mask imposed on a model trained with full attention computes something else, and how much the outputs change is an empirical question about the model, not a property of the mask.

## Retrieval pipelines and vector search {#sec:ai-retrieval}

*Model.* Retrieval-augmented generation \cite{lewis2020} composes a retriever (which returns documents relevant to a query) with a generator conditioned on them. As a transition system its states are the pipeline stages and its moves are calls — embed, retrieve, rerank, generate — with a cost per call.

Retrieval is often **approximate nearest-neighbour search** over vector embeddings. Hierarchical navigable small-world graphs \cite{malkov2020} answer queries by greedy routing: starting from an entry point, repeatedly move to the neighbour closest to the query, descending through layers of a hierarchy. In this book's vocabulary a search is a *navigation word* on a proximity graph. But unlike every navigation in Part I, its result is **not guaranteed**: greedy routing can stop at a local minimum, and the quality of the answer (recall) is measured empirically. The grammatical reading describes the procedure; it supplies no correctness guarantee, and none should be claimed for it.

## Agent workflows and admissible plans {#sec:agents}

*Model.* An agent that uses tools — search, read a file, write a file, run a command, send a message — is a transition system over a workspace state. A **plan** is a word over tool calls. Some plans are dangerous or meaningless: deleting before confirming, writing a file never read, sending a message before the draft is reviewed. Such policies are naturally **admissibility languages**, and they can be checked in the *syntax* layer — before any tool runs. This is the one place in this chapter where the book's machinery applies directly and exactly, and it can be run:

```python run
from cgtsdk import Inadmissible, Move, Structure

class Workspace(Structure):
    """Files as a set of names; tools as moves. Abstract value: (files, opened)."""
    name = "workspace"
    SIGNATURE = (Move("search", ("q",)), Move("open", ("f",)), Move("edit", ("f",)),
                 Move("confirm", ()), Move("delete", ("f",)))

    def __init__(self, files):
        self.files, self.opened = set(files), set()

    def abstract(self):
        return (frozenset(self.files), frozenset(self.opened))

    @classmethod
    def denote(cls, s, c):
        files, opened = s
        if c.name in ("open", "edit", "delete") and c.args[0] not in files:
            raise Inadmissible(f"no file {c.args[0]!r}")
        if c.name == "open":
            return (files, opened | {c.args[0]}), None
        if c.name == "edit" and c.args[0] not in opened:
            raise Inadmissible(f"{c.args[0]!r} edited before being opened")
        if c.name == "delete":
            return (files - {c.args[0]}, opened - {c.args[0]}), None
        return s, None

    def apply(self, c, cost):
        cost.add("rule", 1)
        state, v = self.denote(self.abstract(), c)
        self.files, self.opened = set(state[0]), set(state[1])
        return v

# Policy (syntax layer): every delete must be immediately preceded by confirm.
policy = "(search | open | edit | confirm)* ((confirm delete) (search | open | edit | confirm)*)*"
plans = ["search('x'); open('a'); edit('a')",
         "open('a'); delete('a')",
         "open('a'); confirm; delete('a')",
         "edit('a')",
         "confirm; delete('zzz')"]
for p in plans:
    r = Workspace(["a", "b"]).grammar(policy).execute(p)
    verdict = ("REJECTED before execution (policy)" if not r.syntax.ok else
               f"admissible, but fails at step {r.undefined_at}: {r.reason}" if not r.defined else "admissible and executes")
    print(f"{p:36s} -> {verdict}")
```

```output
search('x'); open('a'); edit('a')    -> admissible and executes
open('a'); delete('a')               -> REJECTED before execution (policy)
open('a'); confirm; delete('a')      -> admissible and executes
edit('a')                            -> admissible, but fails at step 0: 'a' edited before being opened
confirm; delete('zzz')               -> admissible, but fails at step 1: no file 'zzz'
```

The three layers separate cleanly. The policy (syntax) rejects a plan before any tool runs, at the cost of running a DFA over the plan — linear in its length. The workspace semantics rejects plans that are admissible but impossible in the current state, at the step where they fail. And the costs of the tools themselves are a separate matter entirely. Two cautions apply. Policies that depend on counts or nesting (for example, "every acquired lock is released") are not regular: they need the context-free machinery of Chapter 3 or a counter. And a policy checks the *plan*, not the model that produced it: it constrains what is executed, not what the model "intends".

## Persistent histories {#sec:histories}

The motivating work behind this research program concerned persistent addresses and state histories: a system whose state is reached by a recorded sequence of transitions. In operational-grammar terms, a history is a move word; **replaying** it re-executes the word from a recorded initial state; **provenance** is the word itself. Chapter 13 says exactly when such a history can be *compiled* into a constant-size summary: when the moves act through a composition-closed class of constant-size maps (counters, translations, affine maps, bounded tree navigation). For general state — files, documents, model contexts — the semantics of a move depends on the state in ways that carry unbounded information, and the counting argument of \ref{thm:no-compile} applies in spirit: no constant-size summary can stand in for the history. Snapshots plus logs (precomputation plus replay) remain the general answer, with the break-even trade-offs of Chapter 12.

## What a grammar does not capture {#sec:notcapture}

A trained network computes a function determined by its weights. A grammar over its computation graph describes the order and kinds of operations, not that function. Claims that a symbolic grammar "explains", "compresses" or "accelerates" a learned model must be backed by the same evidence as any other claim in this book: an exact equivalence proof, or a measured approximation error under a stated workload. This book offers neither for any learned model, and claims nothing further.

::: exercise {#exr:17-1}
Write a regular admissibility language for a deployment agent with moves `build`, `test`, `deploy` and `rollback`, in which every `deploy` must be preceded by a `test` after the most recent `build`. Check it with the SDK on five plans of your choice.
:::

::: exercise {#exr:17-2}
Show that the policy "every `lock(x)` is eventually followed by `unlock(x)`, with locks properly nested" is not regular when the number of locks is unbounded, and regular when at most $K$ locks may be held at once.
:::

::: exercise {#exr:17-3}
For an attention mask $R$, the cost is $\Theta(|R|)$. Give a mask with $\Theta(n \log n)$ pairs in which every position can influence every other within $\Oh(\log n)$ layers. Which earlier construction in this book does it resemble?
:::

::: solution {of="exr:17-3"}
Let position $i$ attend to $i - 2^t$ for $t = 0, \dots, \lfloor \log_2 n \rfloor$ (and itself): $\Oh(n \log n)$ pairs. After $\ell$ layers information has propagated along sums of $\ell$ powers of two, so every earlier position is reachable within $\lceil \log_2 n \rceil$ layers. This is the doubling grammar of Chapter 10 (and repeated squaring): exponentially fewer rounds at the price of more pairs per round than a single-step mask.
:::

::: summary
- Computation graphs are structural grammars; CSE, constant folding and fusion are sharing, precomputation and representation changes — and quantization or pruning are approximations.
- Attention masks are admissibility relations: cost is proportional to the mask, and imposing a mask changes the function unless the model is defined with it.
- Retrieval and vector search are pipelines and navigations whose quality is empirical; the grammatical reading adds no guarantee.
- Agent plans can be validated against admissibility languages in the syntax layer before execution, exactly and cheaply; non-regular policies need more than a DFA.
- Histories compile to constant size only for uniform move semantics; otherwise snapshots and replay remain necessary.
:::
