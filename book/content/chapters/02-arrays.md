---
title: "Arrays: Addresses You Can Compute"
status: mixed
statusnote: Standard material, reorganized around the array's grammar; the exact doubling cost is computed here for the book's cost model.
description: The array as the first and purest example of a grammar whose words are arithmetic — and what that costs when the array must grow, shift or become multidimensional.
epigraph: An array index is a sentence of one word, and the machine can evaluate it by arithmetic.
---

::: objectives
- State the address formula of an array and explain why it makes indexed access independent of the index.
- Write the array's operation grammar: its moves, their admissibility conditions, their denotations and their costs.
- Generalize the address formula to multidimensional arrays (row-major numeration) and explain density.
- Prove the exact amortized cost of a doubling dynamic array under an explicit cost model.
- Compare arrays and linked lists on identical workloads, and say which costs are intrinsic to the request and which to the representation.
:::

## Contiguous memory and the address formula {#sec:address-formula}

An **array** of $n$ elements, each occupying $s$ memory cells, is stored in $n s$ consecutive cells starting at a **base address** $b$. Element $i$ (counting from $0$) begins at

$$\addr(i) = b + i \cdot s \label{eq:address}$$

and nowhere else. Equation \eqref{eq:address} is the whole secret of the array. To reach element $i$ the machine does not search, and it does not follow anything: it *computes* where the element is, with one multiplication and one addition — or, when $s$ is a power of two, a shift and an addition. On the word RAM of \chapref{01-structures} this is a constant number of steps for every $i < n$, because $i$, $b$ and $s$ each fit in a machine word.

It is worth pausing on what makes this possible. Three properties hold at once:

1. **Every element has a name that is a number.** The index $i$ identifies element $i$ uniquely.
2. **The names are dense.** The indices $0, 1, \dots, n-1$ are used with no gaps, so a block of exactly $n$ cells suffices.
3. **The map from names to locations is arithmetic.** It is a single affine function, computable in $\Oh(1)$ word operations.

Each property can fail separately, and much of this book is about what happens when it does. If names are not numbers (strings, say), we need hashing (Chapter 4). If names are numbers but sparse — a few thousand keys drawn from $\{0, \dots, 2^{64}-1\}$ — a block indexed by them would be astronomically large. If locations are not an arithmetic function of names, we must store and follow pointers (Chapter 3). The array is the case where all three hold, and that is why it is the right place to begin.

::: definition {#def:array title="Array structure" ledger="CGT-DEF-001"}
An **array** of length $n$ is the structure whose elements are the positions $\{0, \dots, n-1\}$, each carrying a value, with the successor relation $i \mapsto i+1$. Its **contiguous representation** stores the value at position $i$ in the $s$ cells starting at $\addr(i) = b + i s$.
:::

## The array's grammar {#sec:array-grammar}

An operation on an array is written as a *call*: a name and arguments. Here is the move signature of the dynamic array used throughout the book (it is exactly the signature of `ArrayStructure` in the SDK):

| Move | Admissible when | Denotation (on the abstract sequence $s$) | Cost in the contiguous representation |
|---|---|---|---|
| `get(i)` | $0 \le i < n$ | returns $s_i$ | 1 comparison, 1 address computation, 1 read |
| `set(i, x)` | $0 \le i < n$ | replaces $s_i$ by $x$ | 1 comparison, 1 address computation, 1 write |
| `len` | always | returns $n$ | 1 read of the header |
| `append(x)` | always | $s \cdot x$ | 1 write, plus a reallocation when full (§\ref{sec:dynamic}) |
| `pop` | $n > 0$ | removes and returns $s_{n-1}$ | $\Oh(1)$ |
| `insert(i, x)` | $0 \le i \le n$ | inserts $x$ before position $i$ | shifts $n - i$ elements |
| `delete(i)` | $0 \le i < n$ | removes and returns $s_i$ | shifts $n - i - 1$ elements |

Three columns, three layers. The *admissibility* column is part of the semantics: `get(9)` on a five-element array is well formed but denotes nothing. The *denotation* column says what each move means on the **abstract** sequence, independently of any memory layout. The *cost* column belongs to one particular representation; the linked list of Chapter 3 has the same first two columns and a different third.

A sequence of calls is an operation expression, and its meaning is the composition of the meanings of its calls: `set(0, 9); get(0)` returns $9$ whatever the array held before, provided it was non-empty. This compositional reading is formalized in Chapter 7. For now it is enough to see it executed, with the cost of each call counted:

```python run
from cgtsdk.structures import ArrayStructure

g = ArrayStructure([5, 3, 8, 1]).grammar()
r = g.execute("set(0, 9); get(0); insert(1, 7); get(4); delete(0)", trace=True)
print("values:", r.values)
print("final :", g.structure.abstract())
print("cost  :", r.cost.snapshot(), "total", r.cost.total)
print("adequate (representation agrees with semantics):", r.adequate)
```

```output
values: [None, 9, None, 1, 9]
final : [7, 3, 8, 1]
cost  : {'alloc': 8, 'arith': 4, 'compare': 5, 'read': 14, 'write': 13} total 44
adequate (representation agrees with semantics): True
```

The `insert` filled the array to capacity and forced a reallocation (`alloc 8`), and both `insert` and `delete` shifted elements: the reads and writes beyond those of `get` and `set` are the shifts. The last line is a check the SDK performs on every execution: the values computed by the memory representation are compared with the values computed by a separate, purely mathematical reference semantics on the abstract sequence. Agreement is called **adequacy**, and every structure in the SDK is tested for it on thousands of random operation sequences.

::: remark
Out-of-range indices are where the semantic layer earns its keep. A language such as C would let `get(9)` read whatever memory follows the array — the representation has *a* behaviour even where the abstract operation has *no* meaning. Keeping a reference semantics separate from the representation is what lets us say precisely that such a behaviour is not a value of the operation.
:::

## Multidimensional arrays and dense numerations {#sec:multidim}

A $d_1 \times d_2$ grid of values is stored by choosing a *numeration* of its positions: a bijection from coordinate pairs to $\{0, \dots, d_1 d_2 - 1\}$, followed by the address formula. The usual choice is **row-major** order:

$$\nu(x_1, x_2) = x_1 d_2 + x_2, \qquad\text{and in general}\qquad \nu(x_1, \dots, x_k) = \sum_{i=1}^{k} x_i \prod_{j > i} d_j . \label{eq:rowmajor}$$

::: proposition {#prop:rowmajor title="Row-major numeration is a dense arithmetic addressing" status="standard"}
For dimensions $d_1, \dots, d_k \ge 1$, the map $\nu$ of \eqref{eq:rowmajor} is a bijection from $\prod_i [0, d_i)$ onto $[0, N)$, $N = \prod_i d_i$. Moving one step along axis $i$ adds or subtracts the **stride** $\sigma_i = \prod_{j>i} d_j$, so each move costs $\Oh(1)$ word operations, and the step is defined exactly when the coordinate stays in $[0, d_i)$.
:::

::: proof
$\nu$ is the mixed-radix representation of integers with digits $x_i \in [0, d_i)$ and radices $d_1, \dots, d_k$; every integer in $[0, N)$ has exactly one such representation. Changing $x_i$ by $\pm 1$ changes $\nu$ by $\pm \sigma_i$. Definedness is the coordinate condition, which is checked by comparing $x_i$ with $0$ and $d_i - 1$ — or, if only $\nu$ is stored, by computing $x_i = \lfloor \nu / \sigma_i \rfloor \bmod d_i$, still $\Oh(1)$ word operations for fixed $k$.
:::

The **density** of a numeration — the number of elements divided by the size of the range of numerals — is exactly $1$ here. That is the property that lets a block of exactly $N$ cells hold the grid. In Chapter 5 the same idea applied to binary trees gives density $1$ for complete trees and density $2^{-\Theta(n)}$ for path-shaped ones, which is the whole difference between a heap and an unusable array. In Chapter 13 we go one step further: a long *sequence* of grid moves can be **compiled** into one translation together with a bounding box, after which it is applied to any start point in constant time, however long the sequence was (\ledger{CGT-PROP-008}).

## Growing an array: amortized doubling {#sec:dynamic}

A contiguous block cannot grow in place: the cells after it may be in use. A **dynamic array** keeps a *capacity* $C \ge n$ and, when `append` finds $n = C$, allocates a new block of $2C$ cells, copies the $n$ elements, and frees the old block. A single append can therefore cost $\Theta(n)$. The classical observation is that the *average* over any sequence of appends is constant \cite{clrs2022}. With an explicit cost model we can say exactly which constant.

::: proposition {#prop:doubling title="Exact cost of doubling" status="proved-here"}
Count one step per allocated cell, per element read and per element written, and start from an empty array of capacity $1$. Then $m \ge 1$ consecutive appends cost exactly

$$T(m) \;=\; m \;+\; 4\left(2^{\lceil \log_2 m \rceil} - 1\right) \;<\; 9m .$$

The ratio $T(m)/m$ does not converge: it is $5 - 4/m$ when $m$ is a power of two and tends to $9$ along $m = 2^k + 1$.
:::

::: proof
Each append writes one element: $m$ steps. A reallocation happens when an append finds the array full, i.e. when $n = C$ for $C = 1, 2, 4, \dots$; the reallocation at capacity $C$ allocates $2C$ cells and reads and writes $C$ elements, costing $4C$. During $m$ appends the array is found full at sizes $C = 2^0, 2^1, \dots, 2^{t-1}$ where $2^{t-1} < m \le 2^t$, i.e. $t = \lceil \log_2 m \rceil$. Hence $T(m) = m + 4 \sum_{i=0}^{t-1} 2^i = m + 4(2^t - 1)$. Since $2^t < 2m$, $T(m) < m + 8m = 9m$. For $m = 2^k$, $t = k$ and $T/m = 1 + 4(m-1)/m = 5 - 4/m$; for $m = 2^k + 1$, $t = k + 1$ and $T/m = 1 + 4(2m - 3)/m \to 9$.
:::

The constant $9$ is an artefact of charging one step per allocated cell; charging allocation as a single step gives the familiar bound of about $3$ per append. That sensitivity is exactly why the book insists on stating the cost model. The proposition is easy to check against the SDK, which counts the same steps:

```python run
from cgtsdk.structures import ArrayStructure
import math

for m in (1, 16, 17, 1000, 1025, 4096, 4097):
    g = ArrayStructure([]).grammar()
    total = sum(g.execute(f"append({k})", check_adequacy=False).cost.total for k in range(m))
    formula = m + 4 * (2 ** math.ceil(math.log2(m)) - 1)
    print(f"m={m:5d}  counted={total:6d}  formula={formula:6d}  per append={total/m:.3f}")
```

```output
m=    1  counted=     1  formula=     1  per append=1.000
m=   16  counted=    76  formula=    76  per append=4.750
m=   17  counted=   141  formula=   141  per append=8.294
m= 1000  counted=  5092  formula=  5092  per append=5.092
m= 1025  counted=  9213  formula=  9213  per append=8.988
m= 4096  counted= 20476  formula= 20476  per append=4.999
m= 4097  counted= 36861  formula= 36861  per append=8.997
```

::: demo dynamic-array
Text alternative: the widget appends $m$ elements and reports the total counted cost and the number of reallocations; the total always equals $m + 4(2^{\lceil \log_2 m\rceil} - 1)$, and the appends that trigger a reallocation are shown with their individual (linear) cost.
:::

::: boundary
"Amortized $\Oh(1)$ append" is a statement about *sequences* of operations. It does not bound any single append, which can cost $\Theta(n)$ — a real concern in latency-sensitive systems — and it assumes the sequence starts from an empty or freshly allocated array.
:::

## Insertion and deletion shift the tail {#sec:shift}

Inserting at position $i$ must move the $n - i$ elements at positions $i, \dots, n-1$ one cell to the right, because positions are *defined* by the address formula: the element that ends up at position $i+1$ has to be at address $b + (i+1)s$. The same rigidity that makes `get` cheap makes `insert` expensive.

::: proposition {#prop:insert-cost status="standard"}
In the contiguous representation, `insert(i, x)` and `delete(i)` cost $\Theta(n - i)$ reads and writes (plus a reallocation for `insert` at full capacity), and this is optimal for any representation in which element $j$ is stored at address $b + js$ before and after the operation.
:::

::: proof
The upper bound is the shift. For the lower bound: after inserting at $i$, each of the $n - i$ elements formerly at positions $j \ge i$ is at position $j+1$, so the cell $b + (j+1)s$ must now hold it; at least one write per moved element is necessary.
:::

A linked list makes the opposite trade: insertion after a known node is $\Oh(1)$ pointer surgery, but finding position $i$ costs $i$ pointer hops. Neither representation dominates the other.

## Arrays and lists on the same workload {#sec:compare}

Because the SDK gives both structures the same `get`/`set`/`insert`/`delete` moves with the same reference semantics, they can be run on identical workloads with correctness checked automatically:

```python run
from cgtsdk.lab import compare_structures, format_table, random_index_workload
from cgtsdk.structures import ArrayStructure, LinkedListStructure

n = 1000
for op in ("get", "delete"):
    work = random_index_workload(n, queries=200, seed=1, op=op)
    rows = compare_structures([ArrayStructure, LinkedListStructure], range(n), work)
    print(f"workload: 200 random {op}(i), n = {n}")
    print(format_table(rows))
    print()
```

```output
workload: 200 random get(i), n = 1000
implementation                    build    per query   space(w) correct
-----------------------------------------------------------------------
ArrayStructure                     1000         3.00       1003 True
LinkedListStructure                1000       551.05       2002 True

workload: 200 random delete(i), n = 1000
implementation                    build    per query   space(w) correct
-----------------------------------------------------------------------
ArrayStructure                     1000       742.06       1003 True
LinkedListStructure                1000       418.66       1658 True
```

For random `get`, the array costs exactly $3$ steps per query and the list about $n/2$ (here $551$ — the 200 random indices happen to average a little above $500$). For random `delete` the comparison reverses: the array shifts on average about half of the remaining elements with a read *and* a write each, while the list walks about half of them and splices in constant time — still linear, but cheaper by a factor of about $1.8$ under this cost model. The "build" column charges one write per initial element; the space column counts words and shows the list's two words per node (it shrinks as elements are deleted, while the array keeps its capacity). Some deletions in the random workload hit indices beyond the shrinking end and are undefined; both structures agree on exactly which ones, which is part of what `correct` certifies.

::: demo array-vs-list
Text alternative: choose $n$, an operation and an index; the widget executes the operation on both representations, shows which cells are touched (the array touches one; the list walks the prefix), prints the step-by-step trace, and plots the cost of `get(i)` for every $i$ — constant for the array, linear for the list.
:::

## What the array teaches {#sec:lesson}

The array is the cleanest instance of the first mechanism catalogued in this book (\ledger{CGT-DEF-009}): **arithmetic addressing**. Its operation `get(i)` is a one-word sentence whose evaluation is arithmetic, and the conditions under which this works — names are numbers, names are dense, locations are an affine function of names — are exactly the conditions we will look for in trees, grids, hypercubes and graphs. Where they hold, the grammar of the structure *is* executable machinery; where they fail, we pay for pointers, tables or search. The array also teaches the first counter-lesson: the rigidity of the address formula is what makes insertion linear. A representation is a bargain, not a free lunch.

::: exercise {#exr:2-1}
A $3 \times 4 \times 5$ array is stored in row-major order. Compute $\nu(2, 1, 3)$ and the three strides. Which single arithmetic operation moves from position $(2,1,3)$ to $(2,2,3)$?
:::

::: solution {of="exr:2-1"}
Strides: $\sigma_1 = 4 \cdot 5 = 20$, $\sigma_2 = 5$, $\sigma_3 = 1$. $\nu(2,1,3) = 2 \cdot 20 + 1 \cdot 5 + 3 = 48$. Moving along the second axis adds $\sigma_2 = 5$, giving $53 = \nu(2,2,3)$.
:::

::: exercise {#exr:2-2}
Redo \ref{prop:doubling} for a growth factor of $3$ instead of $2$ (the capacity triples). Find the exact total cost and the $\limsup$ of the per-append cost. Which factor minimizes the $\limsup$ under this cost model?
:::

::: exercise {#exr:2-3}
Suppose `pop` *shrinks* the array to half its capacity whenever $n$ falls to $C/2$. Exhibit a sequence of $m$ operations costing $\Theta(m^2)$. What shrinking rule avoids this?
:::

::: solution {of="exr:2-3"}
At $n = C/2 + 1$ (just after a growth), alternate `pop` and `append`. Each `pop` brings $n$ to $C/2$ and halves the capacity, copying $\Theta(n)$ elements; each `append` finds the array full and doubles it again, copying $\Theta(n)$. Shrinking only when $n$ falls to $C/4$ leaves room for $\Theta(C)$ operations between resizes, restoring an amortized constant cost.
:::

::: exercise {#exr:2-4}
Run the comparison of \ref{sec:compare} with `insert(i, x)` workloads, using the SDK. Predict, before running, which representation wins and by roughly what factor; then explain any discrepancy from the counted costs.
:::

::: exercise {#exr:2-5}
"An array lookup is $\Oh(1)$." Rewrite this statement so that it names the machine model, the parameter that grows, and the assumption about the size of indices under which it is true. Give a setting in which it is false.
:::

::: summary
- The address formula $\addr(i) = b + is$ makes indexed access a constant number of word operations: the index is a one-word sentence evaluated by arithmetic.
- It requires names that are numbers, dense, and mapped to locations by an arithmetic function; each requirement can fail, and later chapters study what replaces it.
- Row-major numeration extends dense arithmetic addressing to grids; moves are stride additions.
- Doubling dynamic arrays cost exactly $m + 4(2^{\lceil\log_2 m\rceil}-1) < 9m$ steps for $m$ appends in this book's cost model; amortized bounds say nothing about single operations.
- The rigidity that makes `get` cheap makes `insert` linear; lists make the opposite trade. The SDK runs both on identical workloads and checks them against one semantics.
:::
