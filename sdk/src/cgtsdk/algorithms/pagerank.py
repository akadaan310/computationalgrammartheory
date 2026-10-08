"""PageRank (Page, Brin, Motwani & Winograd 1999) and grammar-constrained
variants.

Model (book Chapter 13).  Let G = (V, E) with n vertices, out-degree o(u),
dangling set D = {u : o(u) = 0}, damping α ∈ [0, 1), and a teleportation
distribution v (default uniform).  The random surfer at u

* with probability α follows a uniformly random out-edge of u, or, if u is
  dangling, jumps according to v;
* with probability 1 − α jumps according to v.

The PageRank vector π is the unique stationary distribution:

    π = α (Pᵀ π + (Σ_{u∈D} π_u) v) + (1 − α) v .

Power iteration contracts the L1 error by a factor α per step (proved in the
book, CGT-THM-008), so ‖x_k − π‖₁ ≤ αᵏ ‖x_0 − π‖₁ ≤ 2αᵏ and, a posteriori,
‖x_k − π‖₁ ≤ α/(1−α) · ‖x_k − x_{k−1}‖₁.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Hashable, List, Optional, Sequence, Tuple

from ..automata import DFA
from ..cost import Cost, null_cost


@dataclass
class PageRankResult:
    scores: List[float]
    iterations: int
    residuals: List[float] = field(default_factory=list)   # ‖x_k − x_{k−1}‖₁
    converged: bool = True

    @property
    def error_bound(self) -> float:
        """A-posteriori bound on ‖x_k − π‖₁ (needs α): see pagerank_power."""
        return self._bound

    _bound: float = float("nan")

    def top(self, k: int = 10) -> List[Tuple[int, float]]:
        return sorted(enumerate(self.scores), key=lambda t: (-t[1], t[0]))[:k]


def _check(n: int, alpha: float, v: Optional[Sequence[float]]) -> List[float]:
    if not 0 <= alpha < 1:
        raise ValueError("damping α must lie in [0, 1)")
    if v is None:
        return [1.0 / n] * n
    if len(v) != n or any(x < 0 for x in v) or abs(sum(v) - 1) > 1e-9:
        raise ValueError("teleportation vector must be a probability distribution on V")
    return list(v)


def pagerank_power(adj: Sequence[Sequence[int]], alpha: float = 0.85,
                   v: Optional[Sequence[float]] = None, tol: float = 1e-10,
                   max_iter: int = 10_000, x0: Optional[Sequence[float]] = None,
                   cost: Optional[Cost] = None) -> PageRankResult:
    """Power iteration with dangling mass redistributed by v.  Stops when the
    a-posteriori bound α/(1−α)·‖x_k − x_{k−1}‖₁ ≤ tol.  Cost: one ``edge``
    per edge per iteration plus ``arith`` per vertex."""
    cost = cost or null_cost()
    n = len(adj)
    v = _check(n, alpha, v)
    out = [len(a) for a in adj]
    if x0 is not None:  # warm start: must be a distribution for the bound to hold
        if len(x0) != n or any(t < 0 for t in x0) or sum(x0) <= 0:
            raise ValueError("x0 must be a non-negative vector of length n")
        s0 = sum(x0)
        x = [t / s0 for t in x0]
    else:
        x = list(v)
    res = PageRankResult(x, 0)
    for k in range(1, max_iter + 1):
        dangling = sum(x[u] for u in range(n) if out[u] == 0)
        cost.add("arith", n)
        y = [(1 - alpha + alpha * dangling) * v[i] for i in range(n)]
        cost.add("arith", 2 * n)
        for u in range(n):
            if out[u]:
                share = alpha * x[u] / out[u]
                for w in adj[u]:
                    y[w] += share
                    cost.add("edge", 1)
        r = sum(abs(a - b) for a, b in zip(x, y)); cost.add("arith", n)
        x = y
        res.residuals.append(r)
        if alpha / (1 - alpha) * r <= tol if alpha > 0 else r <= tol:
            res.iterations, res.scores = k, x
            res._bound = alpha / (1 - alpha) * r if alpha < 1 else float("inf")
            return res
    res.iterations, res.scores, res.converged = max_iter, x, False
    res._bound = alpha / (1 - alpha) * res.residuals[-1]
    return res


def pagerank_gauss_seidel(adj: Sequence[Sequence[int]], alpha: float = 0.85,
                          v: Optional[Sequence[float]] = None, tol: float = 1e-10,
                          max_iter: int = 10_000, cost: Optional[Cost] = None) -> PageRankResult:
    """Gauss–Seidel sweeps on the linear system (I − αM) x = (1 − α) v,
    M = Pᵀ + v·1_Dᵀ.  Uses updated values within a sweep; typically fewer
    sweeps than power iteration.  Stops on ‖x_k − x_{k−1}‖₁ ≤ tol (no
    contraction-based guarantee is claimed for this stopping rule)."""
    cost = cost or null_cost()
    n = len(adj)
    v = _check(n, alpha, v)
    out = [len(a) for a in adj]
    inn: List[List[int]] = [[] for _ in range(n)]
    selfw = [0.0] * n
    for u in range(n):
        for w in adj[u]:
            if w == u:
                selfw[u] += 1.0 / out[u]
            else:
                inn[w].append(u)
    dang = [out[u] == 0 for u in range(n)]
    x = list(v)
    D = sum(x[u] for u in range(n) if dang[u])
    res = PageRankResult(x, 0)
    for k in range(1, max_iter + 1):
        r = 0.0
        for i in range(n):
            s = sum(x[u] / out[u] for u in inn[i]); cost.add("edge", len(inn[i]))
            d_other = D - (x[i] if dang[i] else 0.0)
            m_ii = selfw[i] + (v[i] if dang[i] else 0.0)
            new = ((1 - alpha) * v[i] + alpha * (s + v[i] * d_other)) / (1 - alpha * m_ii)
            cost.add("arith", 8)
            if dang[i]:
                D += new - x[i]
            r += abs(new - x[i])
            x[i] = new
        res.residuals.append(r)
        if r <= tol:
            total = sum(x)
            res.iterations, res.scores = k, [xi / total for xi in x]
            return res
    total = sum(x)
    res.iterations, res.scores, res.converged = max_iter, [xi / total for xi in x], False
    return res


def pagerank_exact(adj: Sequence[Sequence[int]], alpha: float = 0.85,
                   v: Optional[Sequence[float]] = None) -> List[float]:
    """Direct solve of (I − αM) x = (1 − α) v by Gaussian elimination with
    partial pivoting.  Θ(n³); a validation oracle for small n only."""
    n = len(adj)
    v = _check(n, alpha, v)
    out = [len(a) for a in adj]
    A = [[(1.0 if i == j else 0.0) for j in range(n)] + [(1 - alpha) * v[i]] for i in range(n)]
    for u in range(n):
        if out[u]:
            for w in adj[u]:
                A[w][u] -= alpha / out[u]
        else:
            for i in range(n):
                A[i][u] -= alpha * v[i]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        p = A[col][col]
        for r in range(col + 1, n):
            f = A[r][col] / p
            if f:
                for c in range(col, n + 1):
                    A[r][c] -= f * A[col][c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (A[r][n] - sum(A[r][c] * x[c] for c in range(r + 1, n))) / A[r][r]
    return x


# ---------------------------------------------------------------------
def constrained_pagerank(n: int, edges: Sequence[Tuple[int, str, int]], dfa: DFA,
                         alpha: float = 0.85, tol: float = 1e-10, max_iter: int = 10_000,
                         cost: Optional[Cost] = None) -> Tuple[List[float], PageRankResult, int]:
    """Grammar-constrained random surfer (CGT proposal; CGT-PROP-010).

    The surfer carries the state q of a DFA over edge labels.  From (u, q)
    it may follow only edges (u, a, w) with δ(q, a) defined, uniformly among
    those, moving to (w, δ(q, a)); if none exists, (u, q) is dangling.  Every
    teleport (and every dangling jump) lands in (w, q₀) with w uniform.
    The vertex score is the marginal Σ_q π(w, q).

    Returns (vertex scores, product-chain result, number of product states).
    With the 1-state universal DFA this is exactly ordinary PageRank on the
    unlabelled graph (tested).  Only product states reachable from V × {q₀}
    are materialised; their number is ≤ |Q|·n (cf. THM-001)."""
    cost = cost or null_cost()
    out: Dict[str, List[List[int]]] = {}
    for u, a, w in edges:
        out.setdefault(a, [[] for _ in range(n)])[u].append(w)
    labels = sorted(set(out) & set(dfa.alphabet))
    index: Dict[Tuple[int, Hashable], int] = {}
    order: List[Tuple[int, Hashable]] = []
    for w in range(n):
        index[(w, dfa.start)] = len(order); order.append((w, dfa.start))
    padj: List[List[int]] = []
    i = 0
    while i < len(order):
        u, q = order[i]
        succ = []
        for a in labels:
            cost.add("rule", 1)
            q2 = dfa.step(q, a)
            if q2 is None:
                continue
            for w in out[a][u]:
                cost.add("edge", 1)
                key = (w, q2)
                if key not in index:
                    index[key] = len(order); order.append(key)
                succ.append(index[key])
        padj.append(succ)
        i += 1
    N = len(order)
    tele = [1.0 / n if q == dfa.start else 0.0 for (_, q) in order]
    pr = pagerank_power(padj, alpha, tele, tol, max_iter, cost=cost)
    scores = [0.0] * n
    for (w, _), s in zip(order, pr.scores):
        scores[w] += s
    return scores, pr, N
