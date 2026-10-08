# The laboratory

<p class="lede">Every widget on this page executes real operations in your browser using <code>cgt-core.js</code>, a port of the relevant parts of the Python SDK. The book's test suite checks those functions against reference outputs exported from the SDK, so the numbers here are the SDK's numbers. Each widget also appears in the chapter that explains it.</p>

<div class="lab-section">

## Arrays and linked lists: the same request, two costs

::: demo array-vs-list
Text alternative: `get(i)` on an array costs one bounds check, one address computation and one read for every $i$. On a linked list it costs one bounds check, a read of the head, $i$ pointer hops and a read. The widget executes both and draws the costs for every index. See Chapter 2.
:::

## Dynamic arrays: amortized doubling

::: demo dynamic-array
Text alternative: appending $m$ elements one by one to an array that doubles its capacity when full costs exactly $m + 4(2^{\lceil \log_2 m \rceil} - 1) < 9m$ counted steps under the book's cost model. See Chapter 2.
:::

## Tree addresses: pointers versus heap numerals

::: demo tree-address
Text alternative: in a complete binary tree, the node at address $w \in \{0,1\}^*$ has heap numeral $\nu(w) = \mathrm{int}(1w)$. A pointer representation reaches it with $|w|$ pointer hops. The numeral reaches it with one arithmetic operation per $w$-bit word, but a table indexed by numerals needs $2^{h+1}-1$ slots. See Chapter 5 and CGT-THM-003.
:::

## Compiling a move word

::: demo compiled-words
Text alternative: any word over $\{L, R, U\}$ compiles, in a heap-shaped tree with nodes $1..n$, into a map $x \mapsto ((x \gg k) \ll j) \mid c$ that is defined exactly on an interval $[lo, hi]$. After compilation each application costs a constant number of word operations, independent of the word's length. See Chapter 13 and CGT-THM-006.
:::

## Admissibility languages

::: demo regex-dfa
Text alternative: a regular expression over move symbols compiles (Thompson construction, subset construction, Moore minimization) into the minimal deterministic automaton that decides admissibility. See Chapter 8.
:::

## Constrained reachability: the product construction

::: demo product
Text alternative: the vertices reachable from a source along walks whose label word belongs to a regular language $\mathcal{L}$ are found by breadth-first search over pairs (vertex, automaton state). At most $|Q| \cdot n$ pairs are explored, and the bound is attained on some inputs. See Chapter 8 and CGT-THM-001.
:::

## PageRank, one iteration at a time

::: demo pagerank
Text alternative: power iteration $x_{k+1} = \alpha M x_k + (1-\alpha) v$ contracts the $L_1$ distance to the PageRank vector by a factor $\alpha$ per step, so the residual certifies the error: $\|x_k - \pi\|_1 \le \frac{\alpha}{1-\alpha}\|x_k - x_{k-1}\|_1$. The widget iterates on small graphs, including one with a dangling page. See Chapter 15 and CGT-THM-008.
:::

## Sorting: counting comparisons

::: demo sorting
Text alternative: insertion sort makes between $n-1$ comparisons (sorted input) and $n(n-1)/2$ (reversed input); merge sort and heapsort make $O(n \log n)$ comparisons on every input. See Chapter 9.
:::

## When does preprocessing pay?

::: demo break-even
Text alternative: an index with build cost $B$ and query cost $q_1$ beats search with query cost $q_0$ within an epoch between invalidating updates only if the epoch has more than $B/(q_0-q_1)$ queries. See Chapter 12 and CGT-PROP-005.
:::

</div>
