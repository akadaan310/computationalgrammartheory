---
title: Structures, Representations, and Operations
status: mixed
statusnote: Definitions and standard material; the three-layer separation is this program's organizing principle.
description: Elements, relations, state, operations and machine models — and the three questions this book never lets collapse into one.
epigraph: A data structure is not only a place where values are kept. It is a promise about which operations are possible, what they mean, and what they cost.
---

::: objectives
After this chapter you should be able to:

- describe a data structure as a set of elements with relations, distinguished from any particular **representation** of it in memory;
- explain what it means for an operation to be *partial*, and why "undefined" is a legitimate answer;
- state the word-RAM cost model and say precisely what a claim such as "this takes $\Oh(1)$ time" asserts and does not assert;
- separate, for any computational claim, the questions of **syntax** (is the request well formed?), **semantics** (what does it denote?) and **execution** (what does it cost?).
:::

## The question this book asks {#sec:question}

Every programmer learns early that an array lets you read element $i$ "in constant time", while a linked list makes you walk to it. The usual explanation is mechanical: the array's elements sit side by side in memory, so the machine can *compute* where element $i$ lives; the list's elements are scattered, so the machine must *follow* pointers. Both explanations are true. But notice what they are really about. They are about the relationship between a **description of an operation** — "element $i$" — and the **machinery** that carries it out.

This book is about that relationship, taken seriously and made precise. Its research program was formulated by Abed Kadaan, who arrived at it from work on programmable addresses: addresses that do more than locate a resource, because they also identify a state, select a transformation, and record a history of transitions. In such a system an address behaves less like a label and more like a *sentence* in a small language, and the language has a grammar. The question that follows is general:

> Can the grammar of a computational structure — the formal rules saying which operations are admissible, how they compose, and what they mean — become part of the machinery by which the structure is operated on, and not merely a description of it?

The motivation is not evidence, and this book does not treat it as such. The question has to be answered the way any question in computer science is answered: by precise definitions, by algorithms and their analysis, by proofs, by reproducible experiments, and — just as importantly — by **counterexamples** that mark where an idea stops working. Some of the answers turn out to be positive and new; many turn out to be known results seen from a new angle; several turn out to be negative. All three kinds of answer appear in this book, labelled as such.

## Elements, relations, and states {#sec:elements}

We begin with the most ordinary vocabulary.

::: definition {#def:structure title="Computational structure" ledger="CGT-DEF-001"}
A **computational structure** $\Str = (A;\, R_1, \dots, R_k)$ consists of a finite set $A$ of **elements** and finitely many **relations** $R_i \subseteq A^{r_i}$ over them, possibly together with labels on elements and distinguished elements (a root, a source, a current position). Its **size** $n$ is $|A|$ (plus the number of related tuples when that is larger).
:::

The definition is deliberately bland. It is the standard notion of a finite relational structure from logic, and nothing in it is new. Its value is that it lets us talk about very different data structures in the same words.

::: example {title="Three structures in one vocabulary"}
1. A **playlist** of five songs is the set $A = \{s_0, \dots, s_4\}$ with the successor relation $\mathit{next} = \{(s_0,s_1), (s_1,s_2), (s_2,s_3), (s_3,s_4)\}$ and the distinguished element $s_0$ (the first song).
2. A **family tree** is a set of people with the relation $\mathit{parent}$ and a distinguished root.
3. A **road map** is a set of junctions with a labelled relation $\mathit{road}_\ell(u, v)$ meaning "a road of kind $\ell$ leads from $u$ to $v$".
:::

The *state* of a structure is everything an operation can inspect or change: which tuples are present, the labels, the distinguished elements. A program that manipulates a structure moves it from state to state.

## Operations are partial {#sec:partial}

An **operation** inspects the current state, possibly changes it, and possibly returns a value. Reading the third song of the playlist returns a value and leaves the state alone; inserting a song changes the state. Crucially, many operations are **partial**: reading the seventh song of a five-song playlist is not an operation that "returns an error value"; it is an operation that is *not defined* in this state.

This distinction matters throughout the book, so we fix it now. When an operation is undefined in a state we will say that its **denotation is empty**. In the formal treatment of \chapref{07-operational-grammars}, each operation $a$ denotes a relation $\sem{a} \subseteq A \times A$ between states (or elements), and "undefined at $x$" means $\sem{a}(x) = \varnothing$. Programming languages report this with exceptions, sentinel values or crashes; the mathematics simply records that there is no successor state.

## Representations {#sec:representations}

A structure is a mathematical object. A **representation** is a concrete layout of that object in a machine's memory: a bit string, an arrangement of memory cells and pointers. The same structure has many representations, and *the representation, not the structure, determines what operations cost*.

::: example {#ex:two-layouts title="One sequence, two layouts"}
The sequence $(10, 20, 30, 40)$ can be laid out

- **contiguously**, as four consecutive memory cells starting at some base address $b$: the value $30$ sits at address $b + 2$;
- **as a linked list**, as four two-word records $(\text{value}, \text{next})$ placed anywhere in memory, each holding the address of the following record, with a separate *head* cell holding the address of the first.

Both represent the same abstract sequence. In the first, the position of element $i$ is *computable* from $i$ by one addition. In the second, the position of element $i$ is known only after following $i$ pointers.
:::

The same pattern recurs for every structure in Part I. A graph can be stored as an $n \times n$ adjacency matrix or as adjacency lists; a binary tree as linked records or as an array in "heap order"; a set as a sorted array, a hash table or a balanced tree. In each case one representation makes some operations cheap and others expensive, and a second representation reverses the trade. The comparison is only meaningful once we say *how cost is counted*.

## Cost needs a machine model {#sec:model}

Throughout the book costs are stated in an explicit machine model.

::: definition {#def:wordram title="Word RAM"}
The **word RAM** has an unbounded array of memory cells, each holding a $w$-bit word with $w \ge \log_2 n$. In one step it can read or write a cell at a computed address, or perform an arithmetic, comparison or bitwise operation on one or two words. An operation on a $b$-bit integer costs $\lceil b / w \rceil$ word steps.
:::

Three conventions follow, and the book holds itself to them strictly.

1. **"$\Oh(1)$" is a claim about a model.** It means: a number of word-RAM steps bounded by a constant *independent of the parameters that grow*, and those parameters must be named. An array access is $\Oh(1)$ as $n$ grows because one address computation suffices; it is *not* $\Oh(1)$ if the index itself has $n$ bits.
2. **Build, storage, query, update and output are separate costs.** A query that takes $\Oh(1)$ time after $\Theta(n^2)$ preprocessing is not "an $\Oh(1)$ algorithm". Chapter 12 develops this into a full accounting discipline (the *cost profile*).
3. **We count, we do not time.** The book's software counts elementary steps — reads, writes, comparisons, pointer hops, hash probes — under a stated cost model. Wall-clock time measured in an interpreted language mostly measures the interpreter; a flat curve of timings over a small range is not evidence of constant time.

::: remark
The word RAM idealizes real machines: it ignores caches, memory hierarchies and parallelism. Where these matter (PageRank on large graphs, in Part V) we say so explicitly and do not let a word-RAM bound stand in for a claim about real hardware.
:::

## Syntax, semantics, execution {#sec:three-layers}

We can now state the organizing principle of the book. Any request made of a structure raises three different questions, and conflating them is the most common source of exaggerated claims about "fast" representations.

::: definition {#def:three-layers title="The three layers" ledger="CGT-DEF-003"}
For a request (an *operation expression*) addressed to a structure:

1. **Syntax** asks whether the expression is well formed and admissible — whether it uses known operations, with the right number of arguments, in an allowed order.
2. **Semantics** asks what the expression *denotes* in the current state: which values it returns and which state it leads to, or that it is undefined.
3. **Execution** asks what it costs to compute that denotation in a given representation and machine model.
:::

The three questions are independent: every combination of answers occurs (\ledger{CGT-PROP-002}).

::: example {title="The layers come apart"}
- *Well formed but undefined.* `get(7)` on a five-element array is a perfectly good expression; it denotes nothing.
- *Defined but expensive.* `get(4999)` on a linked list of 5,000 elements is defined, and costs about 5,000 pointer hops.
- *Cheap to retrieve, expensive to obtain.* "Is there a path from $u$ to $v$?" is answered by one bit lookup if a reachability table has been precomputed — but that table may need $n^2/4$ bits for some graphs, whatever encoding is used (Chapter 12).
:::

The SDK that accompanies this book makes the three layers concrete. Executing an expression returns a result that reports each layer separately, and checks that the representation's answer agrees with a reference semantics:

```python run
from cgtsdk.structures import ArrayStructure, LinkedListStructure

for S in (ArrayStructure, LinkedListStructure):
    g = S([10, 20, 30, 40, 50]).grammar()
    for expr in ["get(3)", "get(7)", "fly(1)"]:
        r = g.execute(expr)
        layer = ("syntax error" if not r.syntax.ok else
                 "undefined" if not r.defined else f"value {r.value}")
        print(f"{S.name:12s} {expr:7s} -> {layer:13s} cost {r.cost.snapshot()}")
```

```output
array        get(3)  -> value 40      cost {'arith': 1, 'compare': 1, 'read': 1}
array        get(7)  -> undefined     cost {'compare': 1}
array        fly(1)  -> syntax error  cost {}
linked_list  get(3)  -> value 40      cost {'compare': 1, 'pointer': 3, 'read': 2}
linked_list  get(7)  -> undefined     cost {'compare': 1}
linked_list  fly(1)  -> syntax error  cost {}
```

Read the output carefully. The *same* expression `get(3)` has the same meaning (the value $40$) on both structures; what differs is the execution layer — one address computation versus three pointer hops. The expression `get(7)` passes the syntax layer and is rejected by the semantic layer after a single bounds check. The expression `fly(1)` never reaches semantics: there is no such operation.

## A grammar, informally {#sec:informal-grammar}

A sequence of operations such as `get(2); set(0, 9); get(0)` is a sentence in a small language. Its alphabet is the structure's set of operations; its grammar says which sentences are admissible; its meaning is the composition of the meanings of the individual operations. For an array that grammar is almost trivial: every sequence of `get`, `set`, `len` and the rest is admissible, and indices out of range make a sentence undefined. For other structures the grammar has real content:

- for a **stack**, a sentence that pops more than it has pushed is undefined — and the set of *defined* sentences is not even a regular language (Chapter 3);
- for a **binary tree**, the sentences over the moves $\{L, R, U\}$ ("left child", "right child", "up") are exactly the addresses and walks of the tree (Chapter 5);
- for a **graph with labelled edges**, a regular expression over labels describes which *paths* are admissible, and resolving it costs at most a factor $|Q|$ more than ordinary search, where $|Q|$ is the size of the expression's automaton — a factor that is tight (Chapter 8).

Part II turns this informal picture into definitions. Before that, Part I examines the ordinary structures one at a time, because the definitions must fit them, not the other way round.

## How evidence is labelled in this book {#sec:evidence}

Every formal statement carries a badge saying what kind of claim it is:

- <span class="status status-definition">Definition</span> introduces an object; it is not a discovery.
- <span class="status status-standard">Established</span> marks a known result from the literature, with a citation.
- <span class="status status-adapted">Adapted</span> marks known ideas restated or packaged in this book's terms.
- <span class="status status-proved-here">Proved here</span> marks a result whose proof appears in this book. Such proofs have been checked by their authors and, where possible, by exhaustive computation on small cases, but **they have not been independently reviewed**.
- <span class="status status-empirical">Empirical</span> marks a reproducible measurement — evidence, never proof.
- <span class="status status-conjecture">Conjecture</span> and <span class="status status-rejected">Rejected</span> mark open and failed hypotheses. Rejected hypotheses are kept: knowing where an idea fails is part of knowing the idea.
- <span class="status status-proposed">Proposed</span> marks a model or design introduced here whose novelty has not been established.

Identifiers such as \ledger{CGT-THM-006} link each statement to the research ledger, the repository's permanent record of definitions, hypotheses, experiments, results, counterexamples and decisions.

::: exercise {#exr:1-1}
Write the road map of \ref{sec:elements} for three junctions $u, v, x$ with a *motorway* from $u$ to $v$ and a *lane* from $v$ to $x$ and from $x$ to $u$ as a structure $(A; \mathit{road}_{\mathrm{motorway}}, \mathit{road}_{\mathrm{lane}})$. Which pairs are in the composition $\mathit{road}_{\mathrm{motorway}} \then \mathit{road}_{\mathrm{lane}}$ ("a motorway, then a lane")?
:::

::: solution {of="exr:1-1"}
$A = \{u, v, x\}$, $\mathit{road}_{\mathrm{motorway}} = \{(u,v)\}$, $\mathit{road}_{\mathrm{lane}} = \{(v,x), (x,u)\}$. The composition contains $(u, x)$ only: from $u$ the motorway reaches $v$, and from $v$ a lane reaches $x$.
:::

::: exercise {#exr:1-2}
For each statement, say which layer — syntax, semantics or execution — it is about. (a) "`pop` on an empty stack is undefined." (b) "Binary search needs at most $\lceil \log_2(n+1) \rceil$ comparisons." (c) "`insert(2)` is rejected because `insert` takes two arguments." (d) "There is a path from $u$ to $v$ whose labels spell `abab`."
:::

::: solution {of="exr:1-2"}
(a) semantics; (b) execution; (c) syntax; (d) semantics — the existence of such a path is a fact about the structure, independent of how long it takes to find.
:::

::: exercise {#exr:1-3}
A colleague reports that reading a value from their "grammar-indexed store" takes the same 40 nanoseconds for stores of 1,000, 10,000 and 100,000 entries, and concludes that reads are $\Oh(1)$. List three things you would need to know before accepting the conclusion.
:::

::: exercise {#exr:1-4}
Give an example of an operation on a familiar structure that is cheap in one representation and expensive in another, other than indexed access. State both costs in the word-RAM model.
:::

::: summary
- A **structure** is a set of elements with relations; a **representation** is a layout in memory; costs belong to representations.
- Operations are **partial**: "undefined" is a semantic answer, not an execution failure.
- Costs are stated in the **word-RAM** model, counted rather than timed, and split into build, storage, query, update and output.
- Every request raises three independent questions — **syntax, semantics, execution** — and this book files every claim under exactly one of them.
- Formal statements carry evidence badges; "proved here" means self-checked, not independently reviewed.
:::
