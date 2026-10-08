---
title: Lists, Stacks, Queues, and Deques
status: mixed
statusnote: Standard structures; the admissibility languages of their operation sequences are classical formal-language facts made explicit here.
description: Pointer-based sequences, and the first structure whose language of defined operation sequences is not regular.
---

::: objectives
- Describe singly and doubly linked lists, and explain why reaching position $i$ costs $i$ pointer hops in a pointer machine.
- Express list navigation as a grammar of cursor moves (`next`, `prev`).
- Prove that the operation sequences a stack can execute from empty form a non-regular language, and count them.
- Explain the circular buffer as arithmetic addressing on the ring $\Z_C$.
:::

## Linked lists {#sec:lists}

A **singly linked list** stores each element in a record holding the value and the address of the next record; a *head* cell holds the address of the first record. Records can live anywhere in memory. Nothing about record $i$'s address can be computed from $i$: it is known only once record $i-1$ has been read.

::: proposition {#prop:list-walk title="Walking is necessary" status="standard"}
Consider a machine that can obtain the address of a record only by reading it from the head cell or from a previously read record. Then reading the element at position $i$ of a singly linked list requires at least $i$ pointer dereferences after reading the head, and $i$ suffice.
:::

::: proof
By induction on $i$: the address of record $i$ is stored only in record $i-1$ (or in the head when $i = 0$), so record $i-1$ must be read first. Following the chain from the head reads records $0, 1, \dots, i$: $i$ dereferences after the head.
:::

The hypothesis is the crux. On a word RAM nothing *forbids* computing an address, but for a list nothing makes the computed address *correct*: the representation offers no arithmetic relation between position and location. That is precisely the property the array has and the list lacks.

The list's operations have the same denotations as the array's (`get`, `set`, `insert`, `delete` on an abstract sequence) and different costs. Inserting after a node one already holds is three pointer writes, independent of $n$; finding that node is the walk. The SDK's `LinkedListStructure` charges `pointer` for each hop, which is how the comparison at the end of Chapter 2 was counted.

### Cursors and the grammar of navigation {#sec:cursor}

A more grammatical view of a list replaces "position $i$" by a **cursor** and two moves, `next` and `prev` (the latter requires a *doubly* linked list, whose records also store the previous address). A navigation is then a word over $\{\mathit{next}, \mathit{prev}\}$, and its denotation is a partial function on positions:

$$\sem{\mathit{next}}(i) = i + 1 \text{ if } i + 1 < n, \qquad \sem{\mathit{prev}}(i) = i - 1 \text{ if } i \ge 1 .$$

A word $w$ moves the cursor by its *net displacement* $\#_{\mathit{next}}(w) - \#_{\mathit{prev}}(w)$, provided every prefix stays within $[0, n)$. Executing $w$ on the list costs $|w|$ pointer hops. But the denotation of $w$ is determined by just three numbers: the net displacement and the minimum and maximum prefix displacements. A word of a million moves could be "compiled" into those three numbers once and then applied in constant time — *if* the representation let us jump by a computed displacement. A doubly linked list does not; an array does. This simple observation reappears in Chapter 13 as a theorem about which structures admit compiled operations.

## Stacks {#sec:stacks}

A **stack** supports `push(x)`, `pop`, `top` and `empty`, with last-in-first-out semantics. Array-backed, every operation is amortized $\Oh(1)$ (pushes inherit the doubling analysis of Chapter 2). The interesting feature of the stack is not its cost but its **language**.

Ignore the pushed values and record only the sequence of move names. Starting from an empty stack, which words over $\{\mathit{push}, \mathit{pop}\}$ are *defined* — never pop an empty stack?

::: proposition {#prop:stack-language title="The defined stack words are not regular" status="standard"}
Let $D = \{ w \in \{\mathit{push}, \mathit{pop}\}^* : \text{every prefix of } w \text{ has at least as many } \mathit{push} \text{ as } \mathit{pop}\}$. Then $D$ is exactly the set of words defined on the empty stack, $D$ is context-free, and $D$ is not regular. The number of words of length $L$ in $D$ is $\binom{L}{\lfloor L/2 \rfloor}$.
:::

::: proof
*Definedness.* A pop is defined iff the stack is non-empty, i.e. iff the number of pushes so far exceeds the number of pops so far; every pop in $w$ is defined iff the prefix condition holds.

*Non-regularity.* Suppose a DFA with $q$ states accepted $D$. Among the words $\mathit{push}^0, \dots, \mathit{push}^{q}$ two, $\mathit{push}^a$ and $\mathit{push}^b$ with $a < b$, lead to the same state. Then $\mathit{push}^a \mathit{pop}^b$ and $\mathit{push}^b \mathit{pop}^b$ are both accepted or both rejected; but the first is not in $D$ and the second is. Contradiction.

*Context-freeness.* $D$ is generated by $S \to \varepsilon \mid \mathit{push}\, S \mid \mathit{push}\, S\, \mathit{pop}\, S$ (prefixes of Dyck words), or recognized by a one-counter automaton.

*Counting.* Words in $D$ are lattice paths of $L$ steps $\pm 1$ that never go below $0$; by the reflection principle their number is $\binom{L}{\lfloor L/2 \rfloor}$, the classical ballot-type count.
:::

The proposition is old mathematics, but its lesson for this book is new emphasis: **the admissibility language of a structure's operations can be more complex than any finite automaton can check**. A system that wants to validate stack-operation sequences *before* running them — as a Grammar-as-a-Service front end might (Chapter 19) — needs a counter, not a regular expression. The SDK sidesteps the issue by checking definedness in the semantic layer, call by call. We can let it count the defined words by brute force and compare with the formula:

```python run
from itertools import product
from math import comb
from cgtsdk.structures import StackStructure

for L in range(9):
    defined = 0
    for w in product(["push(0)", "pop"], repeat=L):
        r = StackStructure().grammar().execute(" ".join(w), check_adequacy=False)
        defined += bool(r.defined)
    print(L, defined, comb(L, L // 2))
```

```output
0 1 1
1 1 1
2 2 2
3 3 3
4 6 6
5 10 10
6 20 20
7 35 35
8 70 70
```

## Queues and the ring $\Z_C$ {#sec:queues}

A FIFO **queue** supports `enqueue`, `dequeue`, `front` and `len`. The standard array representation is a **circular buffer**: a block of capacity $C$, a *head* index $h$, and a count $n$. The element at queue position $i$ is stored at index $(h + i) \bmod C$, and

$$\mathit{enqueue}: \text{write at } (h + n) \bmod C,\; n \leftarrow n+1; \qquad \mathit{dequeue}: \text{read at } h,\; h \leftarrow (h+1) \bmod C,\; n \leftarrow n - 1 .$$

The positions of the queue are numbered in the ring $\Z_C$, and both moves are arithmetic on that ring — addition modulo $C$ — so both cost $\Oh(1)$ (amortized, with doubling when full). The circular buffer is arithmetic addressing (\ledger{CGT-DEF-009}) with the integers replaced by a cyclic group: the same pattern, and the first hint that *group structure* is what makes some numerations work (Chapter 13 develops this for de Bruijn graphs and hypercubes). A **deque** adds `push_front` and `pop_back` — subtraction modulo $C$ — at the same cost.

The admissibility language of the queue, like that of the stack, is the set of words in which each `dequeue` is preceded by more `enqueue`s than `dequeue`s; ignoring values, it is the *same* language $D$, because emptiness depends only on the count. What distinguishes the two structures is the semantics — which value comes out — not the syntax. This is a small but genuine instance of the book's three layers: identical admissibility, different denotations, similar costs.

::: example {title="Same language, different meaning"}
On `push(1) push(2) pop` the stack returns $2$; on `enqueue(1) enqueue(2) dequeue` the queue returns $1$. Both words are admissible from empty, and both cost a constant number of steps per call.
:::

## When lists still win {#sec:lists-win}

Linked structures lose to arrays on indexed access, but they have advantages that the cost columns of this chapter do not show: stable addresses (a record never moves, so external pointers to it stay valid), $\Oh(1)$ splicing of whole sublists, and no reallocation spikes. These are representation properties, not grammar properties — and they are a reminder that "which representation is best" depends on the workload, a theme made quantitative in Chapter 12.

::: exercise {#exr:3-1}
Compile the cursor word $w = \mathit{next}^3\, \mathit{prev}^5\, \mathit{next}^4$ into (net displacement, minimum prefix displacement, maximum prefix displacement). For which starting positions $i$ in a list of length $n = 10$ is $\sem{w}(i)$ defined?
:::

::: solution {of="exr:3-1"}
Prefix displacements run $1,2,3,2,1,0,-1,-2,-1,0,1,2$: net $+2$, minimum $-2$, maximum $+3$. Defined iff $i - 2 \ge 0$ and $i + 3 \le 9$, i.e. $2 \le i \le 6$; then $\sem{w}(i) = i + 2$.
:::

::: exercise {#exr:3-2}
Give a context-free grammar for $D$ different from the one in the proof of \ref{prop:stack-language}, and prove that it generates exactly $D$.
:::

::: exercise {#exr:3-3}
Show that the set of words over $\{\mathit{push}, \mathit{pop}\}$ that are defined on a stack of *bounded* capacity $K$ (where `push` on a full stack is undefined) is regular, and give its minimal DFA. How many states does it have?
:::

::: solution {of="exr:3-3"}
Track the height $0, \dots, K$: states $0..K$, `push` from $h < K$ to $h+1$, `pop` from $h > 0$ to $h-1$, all states accepting. All $K+1$ states are distinguishable (from height $h$, the word $\mathit{pop}^{h+1}$ is rejected but $\mathit{pop}^{h}$ accepted), so the minimal DFA has $K+1$ states.
:::

::: exercise {#exr:3-4}
A queue implemented with two stacks (an "inbox" and an "outbox") gives amortized $\Oh(1)$ operations. Write its operations as words over the stacks' moves, and prove the amortized bound with a potential function.
:::

::: summary
- In a linked list the location of element $i$ is not a function of $i$; reaching it takes $i$ dereferences. Cursor navigation is a grammar of `next`/`prev` words whose denotation is determined by three numbers, but the list cannot exploit that.
- The operation words a stack can execute from empty form the non-regular, context-free language $D$ of Dyck prefixes, with $\binom{L}{\lfloor L/2\rfloor}$ words of length $L$: admissibility can exceed finite-automaton power.
- The circular buffer is arithmetic addressing on the ring $\Z_C$; queues and deques cost amortized $\Oh(1)$.
- Stacks and queues share an admissibility language and differ in semantics — the three layers in miniature.
:::
