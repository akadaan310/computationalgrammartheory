---
title: Hash Tables, Sets, Maps, and Tries
status: mixed
statusnote: Standard structures; framed as arithmetic addressing with collisions, with measured and adversarial costs.
description: When names are not dense numbers — hashing computes an address anyway, at the price of collisions; tries turn keys into words read by an automaton.
---

::: objectives
- Explain hashing as an attempt to recover the array's address formula for keys that are not dense integers.
- Separate the *expected* cost of hashing (under an explicit randomness assumption) from its *worst-case* cost, and exhibit inputs that realize the worst case.
- Measure probe counts in a linear-probing table and relate them to the load factor.
- Describe a trie as the deterministic automaton of a key set, and say what sharing a minimal automaton would add.
:::

## Recovering an address formula {#sec:hashing}

A **map** (dictionary) associates values with keys drawn from a large universe $U$ — strings, 64-bit identifiers, tuples. A **set** is a map whose values are ignored. Chapter 2 showed what makes arrays fast: names that are dense numbers and an arithmetic map from names to locations. Keys have neither property. A table of capacity $C$ with $n \ll |U|$ keys can only use an array if keys are first turned into slot numbers.

A **hash function** $h : U \to \{0, \dots, C-1\}$ does exactly that. The address of key $k$ is "computed" as $h(k)$ — but $h$ cannot be injective when $|U| > C$, so two keys may *collide*. A collision-resolution strategy decides where the second key goes. In **linear probing** (the strategy of the SDK's `HashTableStructure`), the slots $h(k), h(k)+1, h(k)+2, \dots$ (modulo $C$) are tried in turn until the key or an empty slot is found. Each slot inspection is a **probe**.

The grammar of a map is simple and its semantics is the abstract finite function:

| Move | Admissible when | Denotation | Cost (linear probing) |
|---|---|---|---|
| `put(k, v)` | always | $f[k \mapsto v]$ | 1 hash, probes until $k$ or empty, writes; occasional resize |
| `get(k)` | $k \in \dom f$ | $f(k)$ | 1 hash, probes |
| `contains(k)` | always | $[k \in \dom f]$ | 1 hash, probes |
| `delete(k)` | $k \in \dom f$ | $f$ without $k$ | 1 hash, probes, a tombstone write |

As always, the first three columns are shared by every representation of maps — sorted arrays with binary search, balanced trees, tries — and only the cost column changes.

## Expected versus worst-case cost {#sec:expected}

The appeal of hashing is the claim that lookups take "$\Oh(1)$ time". That claim has a hidden hypothesis, and it is false without it.

::: proposition {#prop:hash-worst title="Worst case of any fixed hash function" status="standard"}
For any fixed function $h : U \to \{0, \dots, C-1\}$ with $|U| \ge (n - 1) C + 1$ there are $n$ keys with the same hash value. Inserting them into a linear-probing table and then looking up the last one inserted costs $n$ probes; inserting all of them costs $\Theta(n^2)$ probes in total.
:::

::: proof
By the pigeonhole principle some slot value is the image of at least $n$ keys. Inserting those keys one by one, the $j$-th inserted key probes the $j-1$ occupied slots of its predecessors and then an empty one: $j$ probes, $\sum_j j = \Theta(n^2)$ in total. A later lookup of the $n$-th key repeats its $n$ probes.
:::

The "$\Oh(1)$" therefore requires *randomness*: either the keys are assumed to behave as if random, or $h$ is drawn at random from a suitable family after the keys are fixed (universal hashing). Under such assumptions classical analyses bound the expected number of probes by a function of the **load factor** $\alpha = n/C$ alone \cite{clrs2022}. The SDK uses a fixed, deterministic hash (FNV-1a over a canonical encoding) so that every count in this book is reproducible — which means its guarantees are *empirical* for the inputs we test, not worst-case. Both behaviours are easy to exhibit:

```python run
import random
from cgtsdk import Cost
from cgtsdk.structures import HashTableStructure

rng = random.Random(4)
keys = rng.sample(range(10**12), 2000)
for label, hash_fn in (("FNV-1a (fixed)", None), ("adversarial: h(k)=0", lambda k: 0)):
    t = HashTableStructure(capacity=4096, **({} if hash_fn is None else {"hash_fn": hash_fn}))
    g = t.grammar()
    for k in keys[:500]:
        g.execute(f"put({k}, 1)", check_adequacy=False)
    c = Cost()
    for k in keys[:500]:
        c.merge(g.execute(f"get({k})", check_adequacy=False).cost)
    print(f"{label:22s} n=500 load={500/t.cap:.3f}  probes per successful get = {c.counts['probe']/500:.2f}")
```

```output
FNV-1a (fixed)         n=500 load=0.122  probes per successful get = 1.10
adversarial: h(k)=0    n=500 load=0.122  probes per successful get = 250.50
```

The same table, the same keys, the same load factor: the only difference is whether the hash function scatters the keys. With every key colliding, the average successful lookup probes $(n+1)/2 = 250.5$ slots, exactly as \ref{prop:hash-worst} predicts.

::: boundary
An $\Oh(1)$ claim for hashing is a claim about an *expectation*, under a stated randomness assumption, with the load factor bounded. It is not a worst-case bound, and inputs chosen with knowledge of a fixed hash function defeat it. Treat any "constant-time lookup" claim for a hashing-based index — including any built from a grammar — with this checklist.
:::

## Load factor and resizing {#sec:load}

Probing cost grows with the load factor, so tables **resize**: the SDK doubles capacity and rehashes every key whenever more than half the slots are used (live keys plus tombstones). The amortized analysis is the dynamic-array argument of Chapter 2 with "copy" replaced by "rehash". Measured on random keys, probe counts behave as the theory leads one to expect — a little above one probe per successful lookup at low load, rising as $\alpha \to 1/2$:

```python run
import random
from cgtsdk import Cost
from cgtsdk.structures import HashTableStructure

rng = random.Random(7)
for n in (100, 300, 500, 700, 1000, 2000):
    t = HashTableStructure(capacity=2048)
    g = t.grammar()
    keys = rng.sample(range(10**9), n)
    for k in keys:
        g.execute(f"put({k}, 0)", check_adequacy=False)
    hit, miss = Cost(), Cost()
    for k in keys:
        hit.merge(g.execute(f"get({k})", check_adequacy=False).cost)
    for k in rng.sample(range(10**9, 2 * 10**9), 500):
        miss.merge(g.execute(f"contains({k})", check_adequacy=False).cost)
    print(f"n={n:5d} capacity={t.cap:5d} load={n/t.cap:.3f}  hit={hit.counts['probe']/n:.2f}  miss={miss.counts['probe']/500:.2f}")
```

```output
n=  100 capacity= 2048 load=0.049  hit=1.00  miss=1.06
n=  300 capacity= 2048 load=0.146  hit=1.11  miss=1.23
n=  500 capacity= 2048 load=0.244  hit=1.18  miss=1.33
n=  700 capacity= 2048 load=0.342  hit=1.24  miss=1.55
n= 1000 capacity= 2048 load=0.488  hit=1.56  miss=2.47
n= 2000 capacity= 4096 load=0.488  hit=1.44  miss=2.31
```

Unsuccessful searches (`contains` on absent keys) must run to an empty slot, so they cost more and grow faster with load; at the same load factor, doubling the table leaves probe counts roughly unchanged (the small differences are between two different random key sets) — the empirical signature of a cost that depends on $\alpha$ and not on $n$.

## Hashing as a grammar mechanism {#sec:hash-mechanism}

In the vocabulary of this book, hashing is **arithmetic addressing with collisions**: the name $k$ is turned into a number by computation, and the number into a location by the array formula. The density problem of Chapter 2 is solved by choosing $C = \Theta(n)$, and the price is that the address is only a *first guess*, corrected by probing. Two consequences are worth stating:

- **The grammar does not change.** A map's operations and their meanings are the same for every representation. What hashing changes is the execution layer, and its guarantees are probabilistic.
- **Perfect hashing is precomputation.** For a *static* key set one can build, in expected linear time, a hash function without collisions on that set — a construction outside this book's scope. In the classification of Chapter 12 this is mechanism M-PRE: work done once on the key set so that later queries need no probing. It inherits all the trade-offs of preprocessing: it must be rebuilt when the set changes.

## Tries: keys as words {#sec:tries}

A **trie** stores a set of strings by sharing their prefixes: each node is a prefix, and the edge from prefix $p$ to $p\,c$ is labelled by the character $c$. Looking up a key of length $\ell$ follows $\ell$ edges, independently of how many keys are stored, and `count_prefix(p)` — the number of keys beginning with $p$ — is a single walk if each node stores the size of its subtree.

::: proposition {#prop:trie-dfa title="A trie is a deterministic automaton" status="standard"}
The trie of a finite set $K$ of strings, with each node marked accepting iff it is a key, is a deterministic finite automaton recognizing exactly $K$; its states are the prefixes of keys. The *minimal* DFA of $K$ is obtained by merging states with identical futures, which shares common **suffixes** as well as prefixes.
:::

::: proof
Reading $w$ from the root follows the unique path labelled $w$ if $w$ is a prefix of some key and falls off otherwise; it ends in an accepting state iff $w \in K$. Two prefixes $p, p'$ have the same future iff $\{x : px \in K\} = \{x : p'x \in K\}$; merging such states (Myhill–Nerode) yields the minimal automaton, in which identical suffix sets are represented once.
:::

The trie thus makes literal the idea that a key is a *sentence* read by a machine. The minimal automaton — known in the string-processing literature as a directed acyclic word graph for dictionaries — is the first appearance of the third mechanism of this book, **sharing** (M-SHARE): repeated structure represented once. Chapter 12 measures what sharing buys for trees and what updates cost it.

```python run
from cgtsdk.structures import TrieStructure

g = TrieStructure(["car", "cart", "carton", "cat", "dog", "dot"]).grammar()
r = g.execute("contains('car'); contains('ca'); count_prefix('ca'); count_prefix('do')")
print(r.values, r.cost.snapshot())
```

```output
[True, False, 4, 2] {'pointer': 9, 'read': 4}
```

Each query cost one pointer step per character plus one read: $3 + 2 + 2 + 2 = 9$ pointer steps for the four keys and prefixes of total length $9$, whatever the size of the stored set.

::: exercise {#exr:4-1}
Prove that with linear probing and no deletions, the set of occupied slots after inserting a set of keys does not depend on the order of insertion (although the slot of each key may).
:::

::: exercise {#exr:4-2}
Using the SDK, construct 30 distinct integer keys that all receive the same FNV-1a slot in a table of capacity 64 (search by brute force). What does this exercise show about the guarantees of any fixed, publicly known hash function?
:::

::: solution {of="exr:4-2"}
Enumerate integers $k = 0, 1, 2, \dots$, compute `stable_hash(k) % 64`, and keep those equal to, say, $0$; about one in 64 qualifies, so a few thousand candidates suffice. Since the function is fixed and public, an adversary can always do this: worst-case guarantees require randomizing the hash function after the keys are chosen, or a deterministic structure with worst-case bounds (balanced trees).
:::

::: exercise {#exr:4-3}
Build the minimal DFA of $K = \{\mathrm{tap}, \mathrm{top}, \mathrm{tip}, \mathrm{taps}, \mathrm{tops}\}$ over the alphabet of letters. How many states does the trie have, and how many does the minimal DFA have?
:::

::: exercise {#exr:4-4}
A sorted array with binary search, a balanced search tree, a hash table and a trie all implement the same map grammar. For each, give the worst-case cost of `get` and of `put` and say which ones support `count_prefix` efficiently.
:::

::: summary
- Hashing recovers an address formula for keys that are not dense integers, at the price of collisions resolved by probing.
- "$\Oh(1)$ hashing" is an expectation under a randomness assumption with bounded load; any fixed hash function has inputs costing $\Theta(n)$ per lookup, and the SDK demonstrates them.
- Probe counts depend on the load factor, not on $n$; resizing keeps the load bounded at amortized constant cost.
- A trie is the deterministic automaton of its key set; the minimal automaton additionally shares suffixes — the first instance of the sharing mechanism.
:::
