---
title: Trees, Heaps, Search Trees, and Forests
status: mixed
statusnote: Standard structures; the scope theorem for arithmetic tree addressing and the update-inflation theorem for shared trees are proved here.
description: Tree addresses as words, the heap numeration and exactly when it gives constant-time navigation, search trees, and forests compressed by sharing.
---

::: objectives
- Name every node of a binary tree by its address, a word over $\{0, 1\}$, and evaluate addresses by pointer walks or by arithmetic.
- State and prove the exact scope of arithmetic tree addressing: when the heap numeration gives constant-time navigation and when it does not.
- Compare arithmetic addressing with the preprocessing approach to lowest common ancestors.
- Explain why rotations in balanced search trees invalidate addresses.
- Compress forests by sharing identical subtrees, and prove how adversarial updates destroy that sharing.
:::

## Addresses are words {#sec:tree-addresses}

A **rooted binary tree** is a structure whose elements are nodes, with partial functions $\mathit{left}$, $\mathit{right}$ and $\mathit{parent}$ and a distinguished root. Write $0$ for a step to the left child and $1$ for a step to the right child. Every node $x$ is reached from the root by exactly one word over $\{0,1\}$, its **address** $\addr(x)$; the root's address is the empty word $\varepsilon$.

::: definition {#def:address title="Grammatical address and numeration" ledger="CGT-DEF-006"}
Let a structure have a root $r$ and deterministic moves $\Sigma$. The **address** of an element $x$ is the shortlex-least word $w \in \Sigma^*$ with $\sem{w}(r) = x$. A **numeration** is an injective map $\nu$ from addresses to $\N$; it is **arithmetic** if each move acts on numerals by a map computable in $\Oh(\lceil b/w \rceil)$ word operations on $b$-bit numerals. Its **density** is the number of elements divided by $1 + \max \nu$.
:::

For trees the moves are $L$, $R$, $U$ (left, right, up), and the address of a node is its unique root-to-node word over $\{L, R\}$ — written over $\{0, 1\}$. The set of addresses of a tree is **prefix-closed**: if $w$ is an address so is every prefix of $w$. Conversely, every finite prefix-closed set of binary words is the address set of exactly one binary tree. A tree *is* its language of addresses.

This is the formal counterpart of the observation from which the research program began: an address that identifies a state and determines how to reach it is a word in a small language, and *evaluating* the word is computation.

## The heap numeration {#sec:heap}

How cheaply can an address be evaluated? In a pointer representation, evaluating $w$ costs $|w|$ pointer hops. The **heap numeration** does better on some trees:

$$\nu(w) = \operatorname{int}(1w), \qquad \text{i.e.}\quad \nu(\varepsilon) = 1,\;\; \nu(w0) = 2\nu(w),\;\; \nu(w1) = 2\nu(w) + 1,\;\; \nu(\text{parent}) = \lfloor \nu / 2 \rfloor . \label{eq:heapnum}$$

The moves become arithmetic: left child is doubling, right child is doubling plus one, parent is halving. This is the indexing of the binary heap introduced by Williams \cite{williams1964}, in which a complete binary tree with $n$ nodes occupies exactly the array slots $1, \dots, n$. The SDK represents a tree either way; the costs differ:

```python run
from cgtsdk.structures import BinaryTreeStructure

for shape, make in (("complete, n=1023", lambda rep: BinaryTreeStructure.complete(1023, rep)),
                    ("path,     n=1000", lambda rep: BinaryTreeStructure.path(1000, "01", rep))):
    for rep in ("pointer", "heap"):
        t = make(rep)
        deepest = max(t.labels, key=len)
        r = t.grammar().execute(f"goto('{deepest}') read")
        print(f"{shape} {rep:7s} depth={len(deepest):4d} cost={r.cost.total:5d} {r.cost.snapshot()}  density={t.density:.3g}")
```

```output
complete, n=1023 pointer depth=   9 cost=   11 {'pointer': 9, 'read': 2}  density=1
complete, n=1023 heap    depth=   9 cost=    3 {'arith': 1, 'probe': 2}  density=1
path,     n=1000 pointer depth= 999 cost= 1001 {'pointer': 999, 'read': 2}  density=9.33e-299
path,     n=1000 heap    depth= 999 cost=   18 {'arith': 16, 'probe': 2}  density=9.33e-299
```

On the complete tree the heap numeration reaches the deepest node in three steps and has density $1$: an array of exactly $n$ slots suffices. On the path-shaped tree the numerals have $1000$ bits; each arithmetic operation costs $\lceil 1000/64 \rceil = 16$ word steps, still much better than $999$ pointer hops. But the density is $9 \times 10^{-299}$: an array indexed by numerals would need $2^{1000}$ slots, and the SDK has to fall back to a hash table keyed by numerals (the `probe` steps). Arithmetic navigation has not become free; it has moved the cost into the *size of the address space*.

## The scope of arithmetic tree addressing {#sec:thm003}

The following theorem states exactly when the heap numeration gives constant-time navigation. Its components are classical; the statement of scope is this book's.

::: theorem {#thm:heap-scope title="Scope of arithmetic tree addressing" status="adapted" ledger="CGT-THM-003"}
Let $T$ be a binary tree of height $h$ with $n$ nodes, labelled by heap numerals. On a word RAM with a most-significant-bit instruction:

1. *(Operations.)* Parent, children, depth, the ancestor test and the lowest common ancestor are computable from the numerals alone in $\Oh(\lceil (h+1)/w \rceil)$ word operations.
2. *(Address space.)* Any table indexed directly by numerals has $2^{h+1} - 1$ slots; the density is $n / (2^{h+1} - 1)$, which exceeds $1/2$ for complete trees and is $2^{-\Theta(n)}$ for path-shaped trees.
3. *(Scope.)* Since $h \ge \lfloor \log_2 n \rfloor$, the label-only operations are $\Oh(1)$ if and only if $h = \Oh(w)$; with $w = \Theta(\log n)$, if and only if $h = \Oh(\log n)$.
4. *(Instability.)* A single rotation at a node $v$ changes the address, hence the numeral, of every node in the subtree of $v$.
:::

::: proof
(1) The child and parent formulas are \eqref{eq:heapnum}. Node $u$ is an ancestor of $v$ iff $\addr(u)$ is a prefix of $\addr(v)$, iff shifting $\nu(v)$ right by $\operatorname{depth}(v) - \operatorname{depth}(u)$ yields $\nu(u)$, where $\operatorname{depth}(x) = \msb(\nu(x))$. For the LCA, first shift the deeper numeral right until both have the same length; this replaces the deeper node by its ancestor at the other's depth and does not change the LCA. Two numerals of equal length agree exactly on the bits above the most significant bit of their exclusive-or, so the LCA is the common numeral shifted right by $\msb(\nu_u \oplus \nu_v) + 1$ (with $\msb(0) = -1$). Each step is a constant number of operations on $(h+1)$-bit integers.

(2) Numerals range over $[1, 2^{h+1} - 1]$. A complete tree has $n \ge 2^h$; a path has $h = n - 1$.

(3) follows from (1) and (2).

(4) Let $v$ have address $p$ and left child $\ell$; a right rotation makes $\ell$ the root of the subtree. Afterwards $\ell$ has address $p$ (before $p0$); $v$ has $p1$ (before $p$); a node of $\ell$'s left subtree with address $p00x$ gets $p0x$; a node of $\ell$'s right subtree with address $p01x$ gets $p10x$; a node of $v$'s right subtree with address $p1x$ gets $p11x$. Every word changes.
:::

The theorem draws a clean line. Arithmetic addressing wins only where it needs *no* preprocessing and *no* large tables — on dense, shallow shapes such as heaps. Everywhere else, the competitor is **precomputation**: an Euler tour of the tree with a range-minimum structure answers LCA queries in $\Oh(1)$ for *every* shape after $\Oh(n)$ preprocessing \cite{bender2000,harel1984,schieber1988}. The book's first experiment measured all three approaches (\ledger{CGT-EXP-001}): pointer walking costs grow with depth, heap arithmetic is constant (4 word operations) as long as $h < 64$ and grows as $\lceil (h+1)/64 \rceil$ beyond, and the Euler-tour index answers in 3 operations for every shape after $\Theta(n \log n)$ build steps in the simple sparse-table variant.

```python run
from cgtsdk import Cost
from cgtsdk.algorithms import EulerLCA, NaiveLCA, heap_lca
from cgtsdk.lab import random_parent_array
import random

rng = random.Random(3)
for shape in ("complete", "random", "path"):
    par = random_parent_array(4096, 5, shape)
    b1, b2 = Cost(), Cost()
    naive, euler = NaiveLCA(par, b1), EulerLCA(par, b2)
    q1, q2, q3 = Cost(), Cost(), Cost()
    pairs = [(rng.randrange(4096), rng.randrange(4096)) for _ in range(500)]
    for u, v in pairs:
        a = naive.query(u, v, q1); b = euler.query(u, v, q2)
        assert a == b
        if shape == "complete":
            assert heap_lca(u + 1, v + 1, q3) - 1 == a
    heap = f"{q3.total/500:6.1f}" if shape == "complete" else "   n/a"
    print(f"{shape:8s} per query: walk {q1.total/500:7.1f}  euler {q2.total/500:4.1f} (build {b2.total})  heap-arith {heap}")
```

```output
complete per query: walk    19.0  euler  6.0 (build 188419)  heap-arith    4.0
random   per query: walk    14.5  euler  6.0 (build 188419)  heap-arith    n/a
path     per query: walk  1329.2  euler  6.0 (build 188419)  heap-arith    n/a
```

(The Euler query is charged 6 steps here — three arithmetic operations, two reads, one comparison — under the SDK's finer cost model.) On the complete tree, heap arithmetic needs no build at all; the Euler index needs about $188{,}000$ counted build steps (tour plus sparse table) before its first query. On the other two shapes heap labels would need $h + 1$ bits, which for the path is 4,096 bits per label — and the experiment does not even try.

::: demo tree-address
Text alternative: choose a tree size and an address; the widget draws the complete tree, highlights the root-to-node path, and reports the cost of `goto(address); read` in the pointer representation ($|w|$ hops) and in the heap representation (one numeral computation and a table probe), together with the density $n/(2^{h+1}-1)$.
:::

## Search trees and rotations {#sec:bst}

A **binary search tree** stores keys so that every key in a node's left subtree is smaller and every key in its right subtree larger. Search, insertion and deletion follow one root-to-leaf path, so they cost $\Theta(h)$. Insertion order determines $h$: sorted insertions build a path ($h = n - 1$). **AVL trees** \cite{avl1962} restore balance after each update by *rotations*, guaranteeing $h = \Oh(\log n)$:

```python run
from cgtsdk.structures import BSTStructure

keys = list(range(1, 1024))
for balance in ("none", "avl"):
    t = BSTStructure(keys, balance)
    r = t.grammar().execute("contains(1023); contains(512); contains(2000)")
    print(f"{balance:4s} height={t.tree_height():5d}  three searches cost {r.cost.total:5d} {r.cost.snapshot()}")
```

```output
none height= 1023  three searches cost  7670 {'compare': 5114, 'pointer': 2556}
avl  height=   10  three searches cost    59 {'compare': 40, 'pointer': 19}
```

The rotations that make this possible are exactly the operations that part (4) of \ref{thm:heap-scope} shows to be fatal for addresses: every node in a rotated subtree changes its address. Balanced search trees and address-based indexes are therefore in tension. A search tree navigates by *comparison* — its grammar is "go left if smaller" — and does not need stable addresses; an address-based scheme needs stable addresses and cannot afford rotations. The research ledger records this as a counterexample to "address-based indexes are stable" (\ledger{CGT-NEG-003}).

## Forests and shared structure {#sec:forests}

A **forest** is a sequence of trees. Forests of syntax trees, XML documents and file systems are often highly repetitive: the same subtree occurs many times. The simplest *structural grammar* of a tree represents each distinct subtree once.

::: definition {#def:dag title="Minimal DAG of a tree" ledger="CGT-DEF-004"}
The **minimal DAG** of a labelled ordered tree has one node per distinct subtree; the node for a subtree with root label $a$ and children subtrees $t_1, \dots, t_k$ points to the nodes of $t_1, \dots, t_k$. Equivalently, it is a grammar with one nonterminal $X_t$ per distinct subtree and the production $X_t \to a(X_{t_1}, \dots, X_{t_k})$.
:::

The minimal DAG is computed by *hash-consing*, bottom-up, in expected linear time; its use for common subexpressions goes back at least to Downey, Sethi and Tarjan \cite{downey1980}, and for compressing XML structure to Buneman, Grohe and Koch \cite{buneman2003}. A full binary tree of height $h$ with identical labels has $2^{h+1} - 1$ nodes but a minimal DAG of $h + 1$ nodes: exponential compression. Navigation by preorder rank still works without decompression, by storing each DAG node's expanded size and descending, at a cost of $\Oh(\text{depth} \times \text{degree})$ instead of $\Oh(1)$ in an explicit array (\ledger{CGT-EXP-004}).

Sharing, however, is fragile.

::: theorem {#thm:dag-inflation title="Update inflation of shared trees" status="proved-here" ledger="CGT-THM-005"}
Let $T_h$ be the full binary tree of height $h$ with identical labels, $n = 2^{h+1}-1$; its minimal DAG has $h+1$ nodes.

1. Relabelling one node at depth $d$ with a fresh label creates exactly $d + 1$ new DAG nodes, and the minimal DAG of the result has $h + d + 1$ nodes.
2. For every $k \le 2^h$ there are $k$ leaves whose relabelling with pairwise distinct fresh labels yields a minimal DAG with at least $k\,(h + 1 - \lceil \log_2 k \rceil)$ nodes; since each relabelling adds at most $h+1$ nodes, the size is $\Theta(k \log n)$ for $k \le \sqrt{n}$.
3. The unary path of $n$ nodes with one label has a minimal DAG of $n$ nodes, though its label string $a^n$ has a straight-line program with $\Oh(\log n)$ rules.
:::

::: proof
(1) The relabelled node and its $d$ ancestors are the only nodes whose subtrees contain the fresh label, so their $d+1$ subtrees are new and pairwise distinct (they have different heights). Every other subtree is a full tree of some height below $h$, and all heights $0, \dots, h-1$ still occur; the full tree of height $h$ no longer does. Total: $h + d + 1$.

(2) Choose leaves whose root paths pass through $k$ distinct nodes at every depth $j \ge \lceil \log_2 k \rceil$. Every node on the union $U$ of these paths has a non-empty set of fresh labels below it; nodes of $U$ at the same depth have disjoint such sets, and nodes at different depths have subtrees of different heights, so all $|U| \ge k(h + 1 - \lceil \log_2 k \rceil)$ subtrees are distinct.

(3) Subtrees of the unary path have pairwise distinct sizes. For $a^n$, the rules $X_0 \to a$, $X_{i+1} \to X_i X_i$ together with the binary expansion of $n$ give $\Oh(\log n)$ rules.
:::

Part (3) shows that minimal DAGs are not the most succinct structural grammars: tree straight-line programs can compress repetition that is not a repeated *complete subtree*, and can be exponentially more succinct than DAGs \cite{lohrey2015}. The experiment of the ledger (\ledger{CGT-EXP-004}) saw both effects: a full binary tree with $65{,}535$ nodes went from a 16-node DAG to $1{,}521$ live nodes after 200 random relabels, and a unary path of $65{,}536$ nodes did not compress at all.

```python run
from cgtsdk import Cost
from cgtsdk.sharing import DagGrammar, Explicit, full_binary

F = Explicit(); F.roots.append(full_binary(F, 10))
D = DagGrammar.from_explicit(F)
print("n =", F.n, " minimal DAG nodes =", D.live_size())
c = Cost()
for depth_rank in (0, 1, 1000, 2046):            # preorder ranks of a few nodes
    created = D.relabel(depth_rank, f"fresh{depth_rank}", c)
    print(f"relabel rank {depth_rank:4d}: new rules {created:2d}, live DAG nodes {D.live_size()}")
```

```output
n = 2047  minimal DAG nodes = 11
relabel rank    0: new rules  1, live DAG nodes 11
relabel rank    1: new rules  2, live DAG nodes 12
relabel rank 1000: new rules 11, live DAG nodes 21
relabel rank 2046: new rules 11, live DAG nodes 30
```

Relabelling the root (depth $0$) creates one rule and leaves the DAG size at $h + 0 + 1 = 11$; relabelling rank $1$ (depth $1$) creates two rules. The later relabels act on a tree that already contains fresh labels, so part (1) no longer applies exactly, but each still adds at most $h + 1 = 11$ rules, and the DAG grows towards the $\Theta(k \log n)$ of part (2).

::: exercise {#exr:5-1}
Compute the heap numerals of the nodes with addresses $\varepsilon$, $0$, $011$ and $1101$, and use the XOR method of \ref{thm:heap-scope} to find the LCA of $011$ and $0101$.
:::

::: solution {of="exr:5-1"}
$\nu = 1, 2, 11, 29$. For $011$ ($\nu = 1011_2 = 11$) and $0101$ ($\nu = 10101_2 = 21$): shift $21$ right by one to get $1010_2 = 10$ (depth equal). $11 \oplus 10 = 0001_2$, whose msb is bit $0$; shift by $0 + 1$: $11 \gg 1 = 101_2 = 5$, the node with address $01$. Indeed $01$ is the longest common prefix of $011$ and $0101$.
:::

::: exercise {#exr:5-2}
Prove that every finite prefix-closed set of binary words is the address set of exactly one binary tree.
:::

::: exercise {#exr:5-3}
A *k-ary heap* numbers the children of node $x$ as $kx - (k-2), \dots, kx + 1$ (1-based). Derive the parent formula and the analogue of part (2) of \ref{thm:heap-scope}.
:::

::: exercise {#exr:5-4}
Using the SDK's `BSTStructure`, insert the keys $1, \dots, n$ in sorted order and in random order for $n = 2^{10}$, and compare the total comparison counts of all insertions with and without AVL balancing. Relate the numbers to the height bounds.
:::

::: exercise {#exr:5-5}
Give a forest of $n$ nodes whose minimal DAG has $\Theta(n)$ nodes even though every tree in it is isomorphic, as an unlabelled tree, to every other. What property of the labels causes this?
:::

::: summary
- A tree is its prefix-closed language of addresses; evaluating an address is computation, by pointer walk or by arithmetic.
- The heap numeration makes navigation $\Oh(1)$ exactly when the height is $\Oh(w)$ (dense, shallow shapes); otherwise numerals are long and tables astronomically sparse (\ledger{CGT-THM-003}).
- Precomputation (Euler tour + RMQ) gives $\Oh(1)$ LCA on every shape after linear preprocessing; arithmetic wins only where it needs no preprocessing.
- Rotations, the tool of balanced search trees, change every address in the rotated subtree.
- Minimal DAGs compress repeated subtrees exponentially, but $k$ adversarial relabels inflate them to $\Theta(k\log n)$ nodes, and they miss repetition that tree straight-line programs capture (\ledger{CGT-THM-005}).
:::
