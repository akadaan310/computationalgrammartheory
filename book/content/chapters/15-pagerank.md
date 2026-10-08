---
title: PageRank from First Principles
status: mixed
statusnote: Established mathematics with complete proofs of the results used; experiments reproducible. Nothing here concerns any search engine's production systems.
description: The random surfer, stochastic matrices, dangling pages, damping, existence and uniqueness of the ranking, power iteration with certified error, solvers, sparse representations, updates and personalization.
---

::: objectives
- Build the PageRank model from a directed graph: transition matrix, dangling pages, damping, teleportation.
- Prove that the PageRank vector exists and is unique, and that power iteration converges geometrically with rate $\alpha$.
- Certify the error of an approximate PageRank vector from the last residual, and bound the number of iterations in advance.
- Compare power iteration and Gauss–Seidel, and explain why the vertex order matters for one and not the other.
- State the cost of one iteration in time, memory and communication, and the effect of graph updates and personalization.
:::

## The ranking problem {#sec:ranking}

A collection of hyperlinked pages forms a directed graph: an edge $u \to v$ means page $u$ links to page $v$. **PageRank** assigns each page a score meant to capture how much attention the link structure directs to it. It was introduced by Page, Brin, Motwani and Winograd \cite{page1999} and described as part of the prototype of the Google search engine by Brin and Page \cite{brin1998}. The mathematics is now standard \cite{langville2006,langville2004,bianchini2005}.

::: boundary
This chapter and the next treat PageRank as a published algorithm on mathematical graphs. They say nothing about any search engine's current ranking systems, which combine many signals and are not public. No result here should be read as an improvement to, or an endorsement by, any company's production search.
:::

## The random surfer {#sec:surfer}

Let $G = (V, E)$ have $n$ vertices, out-degrees $o(u)$, and **dangling** vertices $D = \{u : o(u) = 0\}$. Fix a **damping factor** $\alpha \in [0, 1)$ and a **teleportation distribution** $v$ on $V$ (uniform unless stated otherwise). A random surfer at $u$:

- with probability $\alpha$ follows one of $u$'s out-links uniformly at random — or, if $u$ is dangling, jumps to a page drawn from $v$;
- with probability $1 - \alpha$ jumps to a page drawn from $v$.

Write $M$ for the $n \times n$ **column-stochastic** matrix of the link step with the dangling fix: $M_{wu} = 1/o(u)$ if $u \to w$, $M_{wu} = v_w$ if $u \in D$, and $0$ otherwise. The surfer's distribution evolves by

$$x_{k+1} = T(x_k), \qquad T(x) = \alpha\, M x + (1 - \alpha)\, v . \label{eq:surfer}$$

::: definition {#def:pagerank title="PageRank vector"}
The **PageRank vector** $\pi$ is a probability vector with $T(\pi) = \pi$, i.e.

$$\pi = \alpha \Big( P^{\top} \pi + \big(\textstyle\sum_{u \in D} \pi_u\big)\, v \Big) + (1 - \alpha)\, v, \label{eq:pagerank}$$

where $P^\top$ distributes each non-dangling page's score equally over its out-links.
:::

Three modelling choices are hidden in \eqref{eq:pagerank} and each matters in practice. **Dangling pages** (no out-links: images, PDFs, pages not yet crawled) would otherwise leak probability; here their mass is redistributed by $v$, one of several conventions \cite{langville2004}. **Damping** $\alpha$ (classically $0.85$) controls how far the surfer follows links before teleporting. **Teleportation** $v$ makes the chain irreducible and is the lever for personalization (§\ref{sec:personal}).

## Existence, uniqueness, convergence {#sec:theory}

::: theorem {#thm:contraction title="Contraction of the PageRank map" status="standard" ledger="CGT-THM-008"}
For probability vectors $x, y$, $\|T(x) - T(y)\|_1 \le \alpha \|x - y\|_1$. Hence $T$ has a unique fixed point $\pi$ in the probability simplex; for every starting distribution $x_0$, the iterates satisfy $\|x_k - \pi\|_1 \le \alpha^k \|x_0 - \pi\|_1 \le 2\alpha^k$; and, with residual $r_k = \|x_k - x_{k-1}\|_1$,

$$\|x_k - \pi\|_1 \le \frac{\alpha}{1 - \alpha}\, r_k . \label{eq:aposteriori}$$
:::

::: proof
$T(x) - T(y) = \alpha M (x - y)$. A column-stochastic matrix has non-negative entries with columns summing to one, so for any vector $z$, $\|Mz\|_1 = \sum_w |\sum_u M_{wu} z_u| \le \sum_u |z_u| \sum_w M_{wu} = \|z\|_1$. Thus $T$ is an $\alpha$-contraction in $L_1$ on the simplex, which $T$ maps to itself; Banach's fixed-point theorem gives existence, uniqueness and $\|x_k - \pi\| \le \alpha^k \|x_0 - \pi\|$, and $\|x_0 - \pi\|_1 \le 2$ for probability vectors. For \eqref{eq:aposteriori}:

$$\begin{aligned}
\|x_{k-1} - \pi\|_1 &\le \|x_{k-1} - x_k\|_1 + \|x_k - \pi\|_1 \le r_k + \alpha\, \|x_{k-1} - \pi\|_1, \\
\text{so}\quad \|x_{k-1} - \pi\|_1 &\le \frac{r_k}{1-\alpha}, \qquad \|x_k - \pi\|_1 \le \alpha\,\|x_{k-1} - \pi\|_1 \le \frac{\alpha}{1 - \alpha}\, r_k . 
\end{aligned}$$
:::

In spectral terms, $\alpha M + (1 - \alpha) v \mathbf{1}^\top$ is a column-stochastic matrix with eigenvalue $1$, and its second eigenvalue has modulus at most $\alpha$ \cite{haveliwala2003}; the contraction argument gives the rate directly without eigenvalues.

::: proposition {#prop:kstar title="A-priori iteration bound" status="standard" ledger="CGT-PROP-009"}
Power iteration from $x_0 = v$, stopped as soon as $\frac{\alpha}{1-\alpha} r_k \le \tau$, stops after at most

$$k^* = \left\lceil \frac{\log\big(\tau (1 - \alpha)/2\big)}{\log \alpha} \right\rceil$$

iterations, and the returned vector is within $\tau$ of $\pi$ in $L_1$.
:::

::: proof
$r_k = \|T(x_{k-1}) - T(x_{k-2})\| \le \alpha^{k-1} r_1 \le 2\alpha^{k-1}$, so $\frac{\alpha}{1-\alpha} r_k \le \frac{2\alpha^k}{1-\alpha} \le \tau$ once $\alpha^k \le \tau(1-\alpha)/2$. The error claim is \eqref{eq:aposteriori}.
:::

For $\alpha = 0.85$ and $\tau = 10^{-10}$, $k^* = 158$; for $\alpha = 0.99$, $k^* = 2{,}819$. The bound is a worst case. The SDK's tests check the per-step contraction against an exact linear solve, and the experiments found it respected on every instance:

```python run
from cgtsdk.algorithms import pagerank_exact, pagerank_power

adj = [[1, 2], [2], [0, 3], [], [0, 3, 2]]          # page 3 is dangling
pi = pagerank_exact(adj, 0.85)                       # Gaussian elimination, the oracle
print("PageRank (exact):", [round(p, 6) for p in pi])
for k in (1, 2, 5, 10, 20, 40):
    x = pagerank_power(adj, 0.85, tol=0, max_iter=k)
    err = sum(abs(a - b) for a, b in zip(x.scores, pi))
    print(f"k={k:2d}  true error {err:.2e}   certified bound {x.error_bound:.2e}   2*alpha^k {2 * 0.85**k:.2e}")
```

```output
PageRank (exact): [0.223817, 0.163171, 0.321147, 0.223817, 0.068049]
k= 1  true error 1.09e-01   certified bound 2.12e+00   2*alpha^k 1.70e+00
k= 2  true error 7.58e-02   certified bound 8.90e-01   2*alpha^k 1.44e+00
k= 5  true error 8.59e-03   certified bound 1.15e-01   2*alpha^k 8.87e-01
k=10  true error 4.02e-04   certified bound 6.80e-03   2*alpha^k 3.94e-01
k=20  true error 7.14e-07   certified bound 8.54e-06   2*alpha^k 7.75e-02
k=40  true error 1.23e-12   certified bound 2.15e-11   2*alpha^k 3.00e-03
```

The certified bound stays within a factor of about $10$–$20$ of the true error and, after the first few iterations, is far tighter than the a-priori $2\alpha^k$ — this graph converges faster than the worst case, and the residual detects it.

::: demo pagerank
Text alternative: pick one of several small graphs (or edit the out-link lists) and a damping factor; step through power iteration one iteration at a time, watching the scores, the residual $\|x_k - x_{k-1}\|_1$, and the certified error bound $\frac{\alpha}{1-\alpha}\|x_k - x_{k-1}\|_1$; the a-priori bound $k^*$ for tolerance $10^{-10}$ is shown alongside.
:::

## Solvers {#sec:solvers}

Equation \eqref{eq:pagerank} is also a linear system: $(I - \alpha M)\pi = (1 - \alpha) v$. Power iteration is the Jacobi method for it. **Gauss–Seidel** updates $\pi_i$ using the newest values of the other entries within a sweep:

$$\pi_i \leftarrow \frac{(1-\alpha) v_i + \alpha \big( \sum_{u \to i,\, u \ne i} \pi_u / o(u) + v_i \sum_{u \in D,\, u \ne i} \pi_u \big)}{1 - \alpha M_{ii}} .$$

The SDK implements both, plus an exact solver by Gaussian elimination used as an oracle on small graphs. The experiments (\ledger{CGT-EXP-009}) show that neither iterative method dominates. On a graph with host-like blocks and many cycles, Gauss–Seidel needed fewer sweeps than power iteration needed iterations (56 versus 104 at $\alpha = 0.85$). On an acyclic "copying-model" graph whose links all point to *earlier* vertices, sweeping in the natural order works *against* the direction of information flow, and Gauss–Seidel was dramatically slower (1,561 sweeps versus 37 iterations at $\alpha = 0.99$). Reversing the vertex order cut its sweeps from 110 to 34. Power iteration, by contrast, is invariant under reordering: the same linear map, the same iteration count and the same number of edge operations in any order (\ledger{CGT-OBS-016}). The ledger records "Gauss–Seidel is faster" as a rejected general hypothesis (\ledger{CGT-REJ-003}).

The convergence data also contain a surprise that this book cannot yet explain. On the acyclic copying-model graph, power iteration stopped after 17–37 iterations for every $\alpha$ up to $0.99$, while $k^*$ grew to 2,819; on the cyclic block graph, iterations grew from 27 to 485 as $\alpha$ went from $0.5$ to $0.99$ (\ledger{CGT-OBS-015}). A tempting explanation — without cycles, probability cannot circulate, so the iteration settles after about the length of the longest path — is contradicted by the next example, in which the acyclic graph converges *more slowly* than the cyclic one: dangling pages send their mass back through teleportation, which re-creates circulation.

```python run
from cgtsdk.algorithms import pagerank_gauss_seidel, pagerank_power
import math, random

rng, n = random.Random(4), 400
cyclic = [[(u + 1) % n, rng.randrange(n)] for u in range(n)]           # a ring plus one random link each
acyclic = [[w for w in nbrs if w > u] for u, nbrs in enumerate(cyclic)]  # keep only forward links
print("alpha    k*   power: cyclic acyclic   Gauss-Seidel: cyclic acyclic")
for alpha in (0.5, 0.85, 0.99):
    kstar = math.ceil(math.log(1e-10 * (1 - alpha) / 2) / math.log(alpha))
    p = [pagerank_power(g, alpha, tol=1e-10).iterations for g in (cyclic, acyclic)]
    s = [pagerank_gauss_seidel(g, alpha, tol=1e-10 * (1 - alpha)).iterations for g in (cyclic, acyclic)]
    print(f"{alpha:5}  {kstar:5d}        {p[0]:5d}  {p[1]:6d}               {s[0]:5d}  {s[1]:6d}")
```

```output
alpha    k*   power: cyclic acyclic   Gauss-Seidel: cyclic acyclic
  0.5     36           22      29                  12       5
 0.85    158           48     104                  37      10
 0.99   2819           78     393                 523      78
```

Three observations, each consistent with the theory and none implied by $\alpha$ alone. First, every count is far below $k^*$: the bound is a worst case. Second, the acyclic graph needs *more* power iterations than the cyclic one here, the opposite of the copying graph. Third, on the acyclic graph every link points *forward*, so Gauss–Seidel's natural sweep order follows the flow of probability and it needs a small fraction of power iteration's work; on the cyclic graph at $\alpha = 0.99$ it needs several times more. Which structural parameters govern these counts is an open question for this program; that the *order* of evaluation relative to the link direction matters for Gauss–Seidel and not for power iteration is established (\ledger{CGT-OBS-016}).

## Cost of an iteration: memory and communication {#sec:cost}

One power iteration reads every edge once and every vertex a constant number of times: $\Theta(n + m)$ operations. In memory, the standard representation is **compressed sparse rows**: an array of $m$ target indices, an array of $n + 1$ offsets, and two vectors of $n$ floating-point scores — about $m$ words plus $3n$. This is the adjacency-list representation of Chapter 6 laid out contiguously, so that the edge array is read sequentially (arithmetic addressing of edges by offset).

At web scale the graph does not fit in one machine's memory. Partitioning the vertices across machines makes each iteration a local multiply plus an exchange of the scores flowing along *cut* edges; the communication per iteration is proportional to the number of cut edges, which is why host-based partitioning helps — most links stay within a host \cite{kamvar2003}. These are system-level costs that the word-RAM model does not capture; the book states them qualitatively and makes no measured claim about them.

## Updates and incremental ranking {#sec:updates}

When the graph changes, the old vector is a good starting point. Since \ref{thm:contraction} holds from any start, a **warm start** from the previous $\pi$ converges to the new fixed point in about $\log(\|\pi_{\text{old}} - \pi_{\text{new}}\|_1 / \tau) / \log(1/\alpha)$ iterations instead of $\log(2/\tau)/\log(1/\alpha)$. The saving therefore shrinks as the update moves the fixed point further. In the experiment (\ledger{CGT-OBS-017}), on a 3,000-page graph a single inserted link cut iterations from 38 to 27; after 10,000 random insertions, which moved the ranking by $0.51$ in $L_1$, there was no saving at all. Incremental ranking is precomputation with invalidation — the break-even logic of Chapter 12 in a numerical setting \cite{langville2004}.

## Personalization {#sec:personal}

Replacing the uniform $v$ by a distribution concentrated on pages of interest gives **personalized PageRank**; a set of $t$ topic-specific vectors precomputed and mixed at query time gives **topic-sensitive PageRank** \cite{haveliwala2002}. The mixing works because $\pi$ depends *linearly* on $v$: from \eqref{eq:surfer}, $\pi = (1 - \alpha)(I - \alpha M)^{-1} v$ when the dangling redistribution uses a fixed vector, so a convex combination of teleportation vectors yields the same combination of PageRank vectors. Precomputing $t$ vectors costs $t$ PageRank computations and $tn$ words of storage; each query-time mixture is $\Oh(tn)$. This is again M-PRE, and again the break-even depends on query volume. (With the convention used here — dangling mass redistributed by $v$ itself — $M$ depends on $v$ and exact linearity requires redistributing dangling mass by a fixed vector instead. The SDK computes each personalized vector directly.)

## Evaluating a ranking {#sec:evaluation}

Convergence and certified error say how accurately the PageRank *vector* has been computed. They say nothing about whether the ranking is *useful*. Usefulness is measured against relevance judgments on real queries with standard metrics, and requires real corpora and human or behavioural evidence. This book has no such data and makes no claim about ranking quality, here or in the next chapter.

::: exercise {#exr:15-1}
Show that if $G$ is $d$-regular (every vertex has in- and out-degree $d$) and $v$ is uniform, then $\pi$ is uniform for every $\alpha$, and power iteration from $v$ stops after one step. Why does this make regular graphs useless as benchmarks for PageRank solvers?
:::

::: solution {of="exr:15-1"}
With no dangling vertices, $(P^\top \mathbf{u})_w = \sum_{u \to w} \frac{1}{n}\cdot\frac{1}{d} = \frac{1}{n}$ for the uniform vector $\mathbf{u}$, because $w$ has $d$ in-neighbours. So $T(\mathbf{u}) = \alpha \mathbf{u} + (1-\alpha)\mathbf{u} = \mathbf{u}$: the uniform vector is the fixed point, the first residual is $0$, and the stopping rule fires at $k = 1$. Any solver started from the uniform vector "converges" immediately on such graphs, so they measure nothing about solvers. (An earlier draft of this chapter used a chorded cycle as its example and fell into exactly this trap; the example checker exposed it.)
:::

::: exercise {#exr:15-2}
Reverse every link of the acyclic graph in the example (so links point backward) and rerun Gauss–Seidel. Predict the result from the discussion of sweep order before running it, and compare with \ledger{CGT-OBS-016}.
:::

::: exercise {#exr:15-3}
Prove that the dangling-mass convention matters: give a three-vertex graph on which redistributing dangling mass uniformly and redistributing it by a personalized $v$ produce different rankings.
:::

::: exercise {#exr:15-4}
Derive the warm-start iteration estimate stated in §\ref{sec:updates} from \ref{thm:contraction}.
:::

::: summary
- PageRank is the stationary distribution of a damped random surfer with dangling pages and teleportation; it exists, is unique, and attracts every start (\ledger{CGT-THM-008}).
- Power iteration contracts the $L_1$ error by $\alpha$ per step; the residual certifies the error, and $k^* = \lceil \log(\tau(1-\alpha)/2)/\log\alpha \rceil$ iterations always suffice (\ledger{CGT-PROP-009}).
- Gauss–Seidel can be faster or much slower depending on vertex order relative to link direction; power iteration is order-invariant.
- One iteration costs $\Theta(n + m)$ operations and about $m + 3n$ words in compressed sparse rows; distribution costs communication on cut edges.
- Warm starts save iterations in proportion to how little the update moves the fixed point; personalization is linear in $v$ under a fixed dangling convention.
- Accuracy of the vector is not usefulness of the ranking; the latter needs relevance data this book does not have.
:::
