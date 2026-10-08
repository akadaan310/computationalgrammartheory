---
title: The CGT SDK
status: mixed
statusnote: An engineering artifact; every example in this chapter is executed and checked when the book is built.
description: A tutorial for the executable companion to this book — structures, grammars, the three layers, cost models, comparisons, experiment records and extension points.
---

::: objectives
- Install the SDK and run its test suite.
- Execute operation expressions and read each of the three layers of the result.
- Report the same execution under different cost models.
- Compare implementations on identical workloads against an independent oracle, separating build and query cost.
- Record an experiment with a deterministic fingerprint.
- Extend the SDK with a new structure and know which tests it must pass.
:::

## Installation and layout {#sec:install}

The SDK is a Python package, `cgtsdk`, with no dependencies outside the standard library (Python 3.10 or later). From a clone of the repository:

```text
cd sdk
python3 -m pip install -e .            # or simply: export PYTHONPATH=sdk/src
python3 -m unittest discover -s tests  # the full test suite
```

| Module | Contents |
|---|---|
| `cgtsdk.grammar` | `Move`, `Call`, `Structure`, `OperationalGrammar`, `ExecutionResult`, `Inadmissible`, `parse_expression` |
| `cgtsdk.cost` | `Cost` (counter with optional trace), `CostModel`, `Report`, `break_even` |
| `cgtsdk.automata` | `DFA`, `compile_regex` (Thompson → subset → Moore) |
| `cgtsdk.structures` | arrays, lists, stacks, queues, deques, hash tables, heaps, tries, binary trees (pointer/heap), BST/AVL, labelled graphs, automata |
| `cgtsdk.algorithms` | search, sorting, union–find, DP, string matching, graph algorithms, range queries, LCA, PageRank solvers, SAT baselines, product reachability, path-grammar closure |
| `cgtsdk.addressing` | compiled move words: `HeapWord`, `AffineMod`, `XorMask`, `BoxTranslation` |
| `cgtsdk.sharing` | minimal-DAG forests with rank access and path-copying updates |
| `cgtsdk.lab` | generators, `compare_structures`, `compare_functions`, `ExperimentRecord` |
| `cgtsdk.service` | the Grammar-as-a-Service contract, local server and client (Chapter 19) |

The complete, generated API reference is on the [SDK reference page](../sdk.html).

## Three layers in one call {#sec:layers}

Every structure exposes `grammar()`, and `execute` returns an `ExecutionResult` with one field per layer:

```python run
from cgtsdk.structures import QueueStructure

g = QueueStructure([1, 2]).grammar()
for expr in ["enqueue(3); dequeue; front", "dequeue; dequeue; dequeue", "enqueue()", "push(1)"]:
    r = g.execute(expr)
    print(f"{expr:28s} syntax_ok={r.syntax.ok!s:5s} defined={r.defined!s:5s} values={r.values} cost={r.cost.total}"
          + (f"  [{r.syntax.error or r.reason}]" if (not r.syntax.ok or not r.defined) else ""))
```

```output
enqueue(3); dequeue; front   syntax_ok=True  defined=True  values=[None, 1, 2] cost=10
dequeue; dequeue; dequeue    syntax_ok=True  defined=False values=[2, 3] cost=11  [dequeue on empty queue]
enqueue()                    syntax_ok=False defined=None  values=[] cost=0  [call 0: enqueue takes 1 argument(s) ('x',), got 0]
push(1)                      syntax_ok=False defined=None  values=[] cost=0  [call 0: unknown move 'push'; signature is ['dequeue', 'enqueue', 'front', 'len']]
```

Notice that the structure is *stateful*: the second expression continues from the state left by the first (the queue then held $2, 3$), which is why its third `dequeue` is undefined. The reason for each failure is reported — `r.reason` for the semantic layer, `r.syntax.error` for an arity error and an unknown move. (The first expression's ten steps are $3$ for `enqueue` — two arithmetic operations for the ring index and one write — $5$ for `dequeue` and $2$ for `front`.)

## Cost models {#sec:costmodels}

A `Cost` records counts by category (`read`, `write`, `compare`, `arith`, `pointer`, `hash`, `probe`, `alloc`, `edge`, `rule`). A `CostModel` weights categories, so one execution can be reported under several models without rerunning it. The SDK ships `UNIT` (every step costs one) and `MEMORY` (only memory traffic: reads, writes, pointer hops, probes):

```python run
from cgtsdk import MEMORY, UNIT, CostModel
from cgtsdk.structures import ArrayStructure, LinkedListStructure

CACHE_MISS = CostModel("pointer-heavy", 64, (("pointer", 100.0), ("read", 1.0), ("write", 1.0)))
for S in (ArrayStructure, LinkedListStructure):
    r = S(range(1000)).grammar().execute("get(600)")
    print(f"{S.name:12s} unit={r.cost.weighted(UNIT):6.0f}  memory={r.cost.weighted(MEMORY):6.0f}  pointer-heavy={r.cost.weighted(CACHE_MISS):8.0f}")
```

```output
array        unit=     3  memory=     1  pointer-heavy=       3
linked_list  unit=   603  memory=   602  pointer-heavy=   60003
```

The third model is a caricature in which a pointer hop costs a hundred times a sequential read — a crude stand-in for cache misses. Cost models are assumptions, and the SDK makes them explicit and swappable instead of hiding them in a single "time".

## Comparing implementations {#sec:sdk-compare}

`compare_functions` runs implementations on identical inputs, checks every output against an independent oracle, and reports build and query cost separately. Here are three ways to answer LCA queries on a random tree, with the Euler-tour index's preprocessing reported as build cost:

```python run
import random
from cgtsdk.algorithms import EulerLCA, NaiveLCA
from cgtsdk.lab import compare_functions, format_table, random_parent_array

par = random_parent_array(3000, seed=1, shape="random")
oracle = NaiveLCA(par)
rng = random.Random(2)
queries = [(rng.randrange(3000), rng.randrange(3000)) for _ in range(400)]
def scheme(cls):                     # build once (cost reported as build), then query
    return lambda c: (lambda u, v, cost, _i=cls(par, c): _i.query(u, v, cost))
rows = compare_functions({"walk up (depths only)": None, "Euler tour + sparse table": None},
                         queries, oracle=lambda u, v: oracle.query(u, v),
                         builds={"walk up (depths only)": scheme(NaiveLCA),
                                 "Euler tour + sparse table": scheme(EulerLCA)})
print(format_table(rows))
```

```output
implementation                    build    per query   space(w) correct
-----------------------------------------------------------------------
walk up (depths only)              3000        14.77          - True
Euler tour + sparse table        133619         6.00          - True
```

Both schemes preprocess: the walk-up scheme only computes depths (one write per vertex), the Euler scheme builds its tour and sparse table. The richer index pays for its extra build only after $(B_{\text{Euler}} - B_{\text{walk}}) / (q_{\text{walk}} - q_{\text{Euler}})$ queries — `cgtsdk.break_even` computes this kind of number (Chapter 12).

## Recording experiments {#sec:records}

An `ExperimentRecord` stores the hypothesis, the seed, the parameters and the results, together with the environment. Its **fingerprint** is a SHA-256 hash of everything deterministic — excluding the environment and any field whose name mentions wall-clock time — so two runs of the same experiment on different machines can be compared by a single string:

```python run
import random
from cgtsdk import Cost
from cgtsdk.algorithms import heapsort, merge_sort
from cgtsdk.lab import ExperimentRecord

def run(seed):
    rng = random.Random(seed)
    rec = ExperimentRecord("demo-sorting", "merge sort makes fewer comparisons than heapsort on random input",
                           seed, {"n": 1000}, falsification="heapsort makes fewer comparisons on some seed")
    a = rng.sample(range(10**6), 1000)
    for f in (merge_sort, heapsort):
        c = Cost(); f(a, c)
        rec.results.append({"algorithm": f.__name__, "compare": c.counts["compare"]})
    return rec

r1, r2 = run(7), run(7)
print(r1.results)
print("fingerprints equal:", r1.fingerprint() == r2.fingerprint(), r1.fingerprint()[:16])
```

```output
[{'algorithm': 'merge_sort', 'compare': 8697}, {'algorithm': 'heapsort', 'compare': 16846}]
fingerprints equal: True b1dc23626e0eb76a
```

## Extending the SDK {#sec:extending}

A new structure subclasses `Structure` and provides four things (the `BoundedCounter` of Chapter 7 and the `Workspace` of Chapter 17 are complete examples):

1. `SIGNATURE` — the moves, as `Move(name, params, doc, mutates)`;
2. `abstract()` — the abstract value the representation stands for;
3. `denote(state, call)` — the pure reference semantics, returning `(new_state, value)` or raising `Inadmissible`;
4. `apply(call, cost)` — the instrumented representation, counting every step it performs.

The contract a new structure must satisfy is the **adequacy property** of Chapter 7: on every expression, `apply` and `denote` agree on values and on the first undefined call. The SDK's tests check this for every built-in structure on thousands of random calls, including undefined ones (`tests/test_grammar_structures.py`); a new structure should be added to that test. New algorithms should be added with an independent oracle test — brute force on small inputs, or a second algorithm — as every algorithm in `tests/test_algorithms.py` is.

::: remark
The book's example checker found a real defect during writing: the binary search tree's recursive insertion overflowed Python's recursion limit on 1,023 sorted keys. Insertion and deletion are now iterative, and a regression test inserts 5,000 sorted keys (\ledger{CGT-D-018}). The checker exists precisely to catch this kind of error.
:::

::: exercise {#exr:18-1}
Define a cost model in which hash probes cost ten units and everything else one, and use it to compare a hash table with a sorted array plus binary search for 10,000 random lookups. At what load factor does the comparison change?
:::

::: exercise {#exr:18-2}
Implement a `DequeStructure` backed by a doubly linked list, add it to the adequacy test, and compare it with the ring-buffer deque using `compare_structures`.
:::

::: exercise {#exr:18-3}
Write an `ExperimentRecord` for the break-even analysis of the LCA comparison above, including a falsification criterion, and check that its fingerprint is stable across two runs.
:::

::: summary
- The SDK is a standard-library Python package mirroring the book: grammar, cost, automata, structures, algorithms, addressing, sharing, lab and service modules.
- `execute` reports syntax, semantics and execution separately; structures are stateful.
- Costs are counted by category and weighted by explicit, swappable cost models.
- `compare_functions` and `compare_structures` check every output against an oracle and separate build from query cost.
- Experiment records have deterministic fingerprints; new structures must satisfy adequacy, and new algorithms need oracle tests.
:::
