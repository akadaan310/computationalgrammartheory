---
title: Operational Grammars
status: mixed
statusnote: The central definitions of the program (provisional); their components are standard, and the chapter says precisely which.
description: The formal object of Computational Grammar Theory — moves, relational semantics, admissibility languages, adequate representations, cost profiles — and the five mechanisms through which grammar can affect cost.
---

::: objectives
- Define an operational grammar and its three layers precisely.
- Define what it means for a representation to be *adequate* for a grammar, and why the SDK tests adequacy.
- Distinguish operational grammars (which generate operations over a structure) from structural grammars (which generate the structure).
- Write the grammar of each structure of Part I in one common format.
- State the five mechanisms of advantage and the mechanism thesis, and say why the thesis is a conjecture.
- Locate the definitions with respect to labelled transition systems, Kleene algebra with tests, attribute grammars and automatic structures.
:::

## The object {#sec:object}

Part I described structures one at a time. Each had a set of operations ("moves"), a meaning for each move, a notion of which sequences of moves are allowed, and a representation with costs. The following definition collects these components.

::: definition {#def:opgrammar title="Operational grammar" ledger="CGT-DEF-003"}
An **operational grammar** is a tuple

$$G = (\Sigma, \Str, \sem{\cdot}, \Lang)$$

where $\Str$ is a computational structure with set of states $A$; $\Sigma$ is a finite **move signature**, each move with an arity; $\sem{a} \subseteq A \times A$ is the **relational semantics** of move $a$ (for moves with arguments, one relation per argument tuple); and $\Lang \subseteq \Gamma^*$, for a subset $\Gamma \subseteq \Sigma$, is the **admissibility language**, given by a finite description (a regular expression, an automaton, a context-free grammar). The class of $G$ is the class of $\Lang$ (regular, context-free, …).

A word $w \in \Sigma^*$ (with arguments) is an **operation expression**. It is

- **syntactically admissible** if its moves are in $\Sigma$ with correct arities and its projection $\pi_\Gamma(w)$ onto $\Gamma$ lies in $\Lang$;
- **semantically defined at** $x$ if $\sem{w}(x) \neq \varnothing$, where $\sem{w}$ is the composition of Definition \ref{def:relsem};
- **executed** by a representation at a cost given by a cost profile (\ref{def:costprofile}).
:::

Three remarks fix the reading.

1. **Admissibility is a projection.** The language constrains only the moves it mentions; observer moves such as `here` or `read` are free unless named. This is a definitional choice (\ledger{CGT-D-015}); without it, every constraint would have to enumerate every observer.
2. **Admissibility and definedness are different.** `pop` on an empty stack is admissible under the universal language and undefined; `(a b)* a` may reject `a b` although $\sem{ab}(x)$ is non-empty. Syntax is decided by $\Lang$ without looking at the state; semantics depends on the state.
3. **The finite description of $\Lang$ is a conventional formal grammar** $(\Sigma, N, P, S)$ or an automaton. What the definition adds is the structure-dependent semantics $\sem{\cdot}$ and, in \ref{def:costprofile}, a cost model.

## Adequate representations {#sec:adequacy}

A representation implements the moves on concrete memory. It is correct when it computes what the semantics says.

::: definition {#def:adequacy title="Adequacy"}
A representation $\rho$ of a structure with grammar $G$ is **adequate** if for every state $x$ and every expression $w$: $\rho$ executes $w$ to completion iff $\sem{w}(x) \neq \varnothing$, the values it returns at each call are those of the semantics, and when $w$ is undefined, $\rho$ reports undefinedness at the first call $i$ at which the prefix $w_{\le i}$ becomes undefined.
:::

Adequacy is the standard notion of a correct implementation of an abstract data type (an abstraction function relating concrete and abstract states). The SDK makes it executable: every structure has a pure reference semantics `denote` on its abstract value and an instrumented `apply` on its representation, and `execute` compares them call by call. The test suite checks adequacy for every structure on thousands of random expressions, including undefined ones (\ledger{CGT-D-014}).

Here is the whole interface, used to define a new structure from scratch: a counter that can be incremented and decremented within bounds, with an admissibility language forbidding two decrements in a row.

```python run
from cgtsdk import Cost, Inadmissible, Move, Structure

class BoundedCounter(Structure):
    """A counter in [0, K]. Abstract value: the integer."""
    name = "counter"
    SIGNATURE = (Move("inc", (), "add one"), Move("dec", (), "subtract one"), Move("value", (), "read"))

    def __init__(self, K, start=0):
        self.K, self.v = K, start

    def abstract(self):
        return (self.K, self.v)

    @classmethod
    def denote(cls, state, call):
        K, v = state
        if call.name == "inc":
            if v == K: raise Inadmissible("counter at its maximum")
            return (K, v + 1), None
        if call.name == "dec":
            if v == 0: raise Inadmissible("counter at zero")
            return (K, v - 1), None
        return state, v

    def apply(self, call, cost):
        cost.add("compare", 1)
        if call.name == "value":
            cost.add("read", 1); return self.v
        step = 1 if call.name == "inc" else -1
        if not 0 <= self.v + step <= self.K:
            raise Inadmissible("counter at its maximum" if step > 0 else "counter at zero")
        cost.add("write", 1); self.v += step

for expr in ["inc inc dec value", "inc dec dec", "dec", "inc inc inc inc", "inc value inc dec value"]:
    g = BoundedCounter(K=3).grammar(admissible="(inc | dec inc)* (dec | ε)")   # fresh state each time
    r = g.execute(expr)
    status = (f"syntax: {r.syntax.error}" if not r.syntax.ok else
              f"undefined at call {r.undefined_at}: {r.reason}" if not r.defined else f"values {r.values}")
    print(f"{expr:24s} -> {status}  [adequate={r.adequate}]")
```

```output
inc inc dec value        -> values [None, None, None, 1]  [adequate=True]
inc dec dec              -> syntax: move word inc dec dec is not in the admissibility language  [adequate=None]
dec                      -> undefined at call 0: counter at zero  [adequate=True]
inc inc inc inc          -> undefined at call 3: counter at its maximum  [adequate=True]
inc value inc dec value  -> values [None, 1, None, None, 1]  [adequate=True]
```

Execution mutates the representation, so each expression starts from a fresh counter at zero. The second expression is rejected *before* execution because `dec dec` is not admissible; the third is admissible and undefined (the counter starts at zero); the fourth runs off the top. The last shows projection at work: `value` is not mentioned by the language, so it does not interfere with it.

## The grammar of each structure {#sec:grammar-table}

With the definition in hand, the structures of Part I can be written in one format. The table is a summary of Chapters 2–6; the SDK implements each row.

| Structure | States | Moves $\Sigma$ | Defined when | Admissibility class (from empty) | Typical representation and move cost |
|---|---|---|---|---|---|
| array | sequences | `get(i)`, `set(i,x)`, `insert`, `delete`, `append`, `pop`, `len` | index in range | universal | contiguous: $\Oh(1)$ access, $\Theta(n-i)$ shifts |
| linked list | sequences + cursor | `get(i)`… or `next`, `prev` | index in range / neighbour exists | universal | records: $\Theta(i)$ access |
| stack | sequences | `push(x)`, `pop`, `top`, `empty` | non-empty for `pop`, `top` | context-free, not regular (Dyck prefixes) | array: amortized $\Oh(1)$ |
| queue / deque | sequences | `enqueue`, `dequeue`, … | non-empty | same language as the stack | ring buffer on $\Z_C$: amortized $\Oh(1)$ |
| map / set | finite functions | `put`, `get`, `contains`, `delete` | key present for `get`, `delete` | universal | hashing: $\Oh(1)$ *expected*; trie: $\Oh(\lvert k \rvert)$ |
| heap | multisets | `push`, `pop_min`, `peek` | non-empty | Dyck-type, as for stacks | array with heap numeration: $\Oh(\log n)$ |
| binary tree | trees + cursor | `L`, `R`, `U`, `goto(w)`, `read` | target node exists | universal; addresses form a prefix-closed language | pointers: $\Theta(\lvert w \rvert)$; heap numerals: $\Oh(\lceil h/w \rceil)$ |
| search tree | sorted sets | `insert`, `delete`, `contains`, `min` | key present for `delete` | universal | $\Theta(h)$; AVL: $\Oh(\log n)$ |
| labelled graph | vertex sets | one move per label, `at(v)`, `here` | image non-empty | any regular / context-free $\Lang$ by choice | adjacency lists: $\Theta(\text{edges inspected})$ |
| automaton | states | one move per letter | transition defined | — | table: $\Oh(1)$ per letter |

The table makes visible what is common — every structure is a set of states with partial moves — and what is not: the admissibility class (universal, regular, context-free), the dependence of definedness on state, and above all the cost column.

## Structural grammars {#sec:structural}

An operational grammar generates *operations over* a structure. A second kind of grammar generates *the structure itself*.

::: definition {#def:structural title="Structural grammar" ledger="CGT-DEF-004"}
A **structural grammar** for a structure $\Str$ is a grammar whose unique derivation (or unique generated object) is $\Str$ or its representation: a minimal DAG of a tree, a straight-line program for a string, a tree straight-line program, a hyperedge-replacement grammar for a graph. Its size is the total length of its productions.
:::

The two kinds combine: navigating a grammar-compressed tree is an operational grammar whose states are given by a structural grammar (Chapter 5, \ledger{CGT-THM-005}). Grammar-based compression is an established field \cite{charikar2005,lohrey2015,bille2011}; random access into a grammar-compressed string of length $N$ takes $\Oh(\log N)$ time \cite{bille2011}, and lower bounds show that for polynomial-space structures this cannot in general be improved to constant time \cite{verbin2013}. This book uses these objects and does not claim new compression results.

## Cost profiles {#sec:costprofile}

::: definition {#def:costprofile title="Resolution scheme and cost profile" ledger="CGT-DEF-005"}
For a class of structures and a family of queries, a **resolution scheme** is a triple of algorithms (Build, Query, Update) on a fixed machine model. Its **cost profile** is the tuple

$$\mathcal{C} = \big(T_{\mathrm{build}},\; S,\; T_{\mathrm{query}},\; T_{\mathrm{update}},\; |\mathrm{out}|\big),$$

each a function of the structure size $n$, the grammar size $g$, the query size $q$, update parameters $u$ and output size $o$. A **grammatical index** is a resolution scheme whose Build takes a grammar as input; a **grammar-based algorithm** is one whose control flow follows derivations (product constructions, fixpoint evaluation of productions, descent through a structural grammar).
:::

The notation $T(n, g, q, u, o)$ is a reporting discipline, not yet a theory: whether grammar parameters yield distinctions not already captured by parameterized complexity or by preprocessing–query trade-offs is an open problem (\ledger{CGT-OPEN-005}).

## Five mechanisms {#sec:mechanisms}

Every advantage observed so far in this research — in the chapters of Part I and in the ten experiments of the ledger — traces to one of five mechanisms.

::: definition {#def:mechanisms title="Mechanisms of advantage" ledger="CGT-DEF-009"}
| Code | Mechanism | Where it appears |
|---|---|---|
| **M-ARITH** | an arithmetic numeration of a dense address space replaces stored structure by computation | arrays; ring buffers; heaps (\ledger{CGT-THM-003}); compiled words (\ledger{CGT-THM-006}) |
| **M-PRE** | precomputation: answers are stored and later retrieved | closures, LCA tables, perfect hashing — bounded below by information content (\ledger{CGT-THM-002}) |
| **M-SHARE** | repeated substructure is represented once | minimal DAGs, minimal automata — fragile under updates (\ledger{CGT-THM-005}) |
| **M-RESTRICT** | a restriction of the instance class makes structure exploitable | interval labels on forests; 2-SAT |
| **M-PRUNE** | the admissibility language excludes moves before they are executed | product construction — and it can also *multiply* work (\ledger{CGT-THM-001}) |
:::

::: conjecture {#conj:mechanism title="Mechanism thesis" status="conjecture" ledger="CGT-CONJ-001"}
Every asymptotic advantage of a grammatical resolution scheme over the best conventional scheme for the same queries, machine model and cost component is attributable to a combination of M-ARITH, M-PRE, M-SHARE, M-RESTRICT and M-PRUNE.
:::

The thesis is not yet a mathematical statement: "conventional scheme" and "attributable" are undefined, and making them precise is an open problem (\ledger{CGT-OPEN-001}). It is nevertheless falsifiable in practice — by a grammar-based scheme with an advantage none of the five explains — and it organizes the rest of the book. Chapters 8–14 examine each mechanism with its cost profile and its failure cases.

## Relationship to established theory {#sec:related}

The components of an operational grammar are not new, and it is important to say which existing theories each comes from.

- **Labelled transition systems and relational semantics.** $(\Sigma, \Str, \sem{\cdot})$ is a labelled transition system; the extension to words is the relational model of Kleene algebra. \emph{Kleene algebra with tests} \cite{kozen1997} adds Boolean guards and is a natural home for admissibility conditions that depend on state.
- **Formal-language-constrained paths.** With regular or context-free $\Lang$ over a labelled graph, the grammar is exactly the setting of regular path queries and CFL-reachability \cite{mendelzon1995,barrett2000,yannakakis1990,reps1998}.
- **Attribute grammars.** Knuth's attribute grammars \cite{knuth1968} attach semantic functions to the productions of a context-free grammar and evaluate them over derivation trees. They are the classical way of making a grammar *compute*. CGT differs in where the grammar lives: attribute grammars describe strings and their parse trees; operational grammars describe operations over an arbitrary structure. A systematic comparison is a literature debt of this program (\ledger{CGT-OPEN-010}).
- **Automatic structures and groups.** Structures whose elements are words of a regular language and whose relations are recognized by synchronous automata \cite{blumensath2000,khoussainov1995}, and groups whose multiplication by generators is so recognized \cite{epstein1992}, are the closest existing theory to the address-as-sentence idea. Chapter 13's compiled words are a cost-oriented special case.
- **Abstract data types.** Adequacy is the standard notion of a correct implementation of an abstract type.

What the program adds is not a new object but a *discipline*: every claim filed under one layer, every cost stated as a profile in an explicit model, every advantage attributed to a mechanism and paired with the inputs that defeat it.

::: exercise {#exr:7-1}
Extend `BoundedCounter` with a move `reset` and an admissibility language in which `reset` may only occur after at least two `inc`. Write the language as a regular expression and check your answer with the SDK.
:::

::: exercise {#exr:7-2}
Prove that adequacy is preserved under sequential composition: if a representation is adequate for every single-call expression from every reachable state, it is adequate for all expressions.
:::

::: solution {of="exr:7-2"}
Induction on the length of $w = w' c$. By hypothesis the representation agrees with the semantics on $w'$, including the point of first undefinedness; if $w'$ is defined, the representation reaches a state whose abstraction is the semantic state $y$ reached by $w'$, and the single-call hypothesis at $y$ gives agreement on $c$. The point of first undefinedness of $w$ is that of $w'$ if $w'$ is undefined, and otherwise is the last call iff $\sem{c}(y) = \varnothing$.
:::

::: exercise {#exr:7-3}
Give an operational grammar (states, moves, semantics, admissibility) for a traffic light with moves `next` and `emergency`, in which `emergency` is admissible only from green. Which component of the definition carries the "only from green" condition — syntax or semantics? Argue for both choices.
:::

::: exercise {#exr:7-4}
For each mechanism in \ref{def:mechanisms}, give one example from outside this book (a database index, a compiler optimization, a cache) and say which cost component of the profile it improves and which it worsens.
:::

::: summary
- An operational grammar $G = (\Sigma, \Str, \sem{\cdot}, \Lang)$ consists of moves, relational semantics on a structure, and an admissibility language constraining the projection of move words.
- Syntax (admissibility), semantics (definedness and values) and execution (cost) are separate layers; a representation is adequate when its execution agrees with the semantics, and the SDK tests this.
- Structural grammars generate the structure; operational grammars generate operations over it.
- Costs are reported as profiles $(T_{\mathrm{build}}, S, T_{\mathrm{query}}, T_{\mathrm{update}}, |\mathrm{out}|)$.
- Five mechanisms — arithmetic addressing, precomputation, sharing, restriction, pruning — account for every advantage observed so far; that they account for *all* advantages is a conjecture.
- The components are standard; the program's contribution is the discipline that keeps them apart.
:::
