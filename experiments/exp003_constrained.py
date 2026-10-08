"""CGT-EXP-003  Grammar-induced constraints on search (mandate Experiments C/F).

Setting: an edge-labelled digraph over Sigma = {a, b, c} is an operational
grammar (CGT-DEF-003) whose moves are the label relations; an admissibility
language L (a DFA) says which move sequences are valid.  Query: the set of
vertices reachable from s by a walk whose label word is in L.

Hypothesis H-005: grammar constraints reduce explored states only when L is
restrictive relative to the graph; for permissive L the product search
explores up to |Q| times *more* states than unconstrained BFS.  Constraint
pruning is a property of (L, graph) jointly, not of having a grammar.
Hypothesis H-006: "search unconstrained, then filter" is not a correct
substitute; correct answers need the product (or equivalent) construction.

Falsification: H-005 fails if product exploration is never larger than
unconstrained BFS; H-006 fails if unconstrained reachability equals
constrained reachability on all sampled instances.

Run:  python3 experiments/exp003_constrained.py
"""
from __future__ import annotations

import json
import os
import random
from collections import deque

from cgt.core import DFA, OperationalGrammar, Ops, env_info

SEED = 3
SIGMA = ["a", "b", "c"]
OUT = os.path.join(os.path.dirname(__file__), "results")


def dfa(name: str) -> DFA:
    if name == "a*":
        return DFA({0}, 0, {0}, {(0, "a"): 0})
    if name == "(ab)*c":
        return DFA({0, 1, 2}, 0, {2}, {(0, "a"): 1, (1, "b"): 0, (0, "c"): 2})
    if name == "S*cS*":  # at least one c
        d = {(0, "a"): 0, (0, "b"): 0, (0, "c"): 1}
        d.update({(1, x): 1 for x in SIGMA})
        return DFA({0, 1}, 0, {1}, d)
    if name == "even_a":  # parity of a's -- permissive, doubles state space
        d = {(q, x): (q ^ 1 if x == "a" else q) for q in (0, 1) for x in SIGMA}
        return DFA({0, 1}, 0, {0}, d)
    if name == "mod5_len":  # walk length divisible by 5 -- permissive
        d = {(q, x): (q + 1) % 5 for q in range(5) for x in SIGMA}
        return DFA(set(range(5)), 0, {0}, d)
    raise KeyError(name)


LANGS = ["a*", "(ab)*c", "S*cS*", "even_a", "mod5_len"]


def labelled_gnp(n, avg_deg, rng):
    adj = {x: [[] for _ in range(n)] for x in SIGMA}
    for _ in range(int(avg_deg * n)):
        u, v = rng.randrange(n), rng.randrange(n)
        adj[rng.choice(SIGMA)][u].append(v)
    return adj


def grammar(adj, L) -> OperationalGrammar:
    moves = {x: (lambda y, x=x: adj[x][y]) for x in SIGMA}
    return OperationalGrammar(SIGMA, moves, dfa(L), Ops())


def unconstrained(adj, n, s, ops):
    seen = {s}; dq = deque([s])
    while dq:
        u = dq.popleft(); ops.add()
        for x in SIGMA:
            for v in adj[x][u]:
                ops.add()
                if v not in seen:
                    seen.add(v); dq.append(v)
    return seen


def naive_walks(adj, D: DFA, s, max_len, cap=2_000_000):
    """Enumerate walks (not product states) up to max_len, keep those in L."""
    out, explored = set(), 0
    st = [(s, D.start, 0)]
    while st:
        u, q, k = st.pop(); explored += 1
        if explored > cap:
            return None, explored
        if q in D.accept:
            out.add(u)
        if k == max_len:
            continue
        for x in SIGMA:
            q2 = D.step(q, x)
            if q2 is None:
                continue
            for v in adj[x][u]:
                st.append((v, q2, k + 1))
    return out, explored


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for n, deg in ((200, 1.5), (2000, 1.5), (2000, 4.0), (20000, 4.0)):
        adj = labelled_gnp(n, deg, rng)
        sources = [rng.randrange(n) for _ in range(20)]
        for L in LANGS:
            Dq = len(dfa(L).states)
            ex_p = ex_u = wrong = ops_p = ops_u = 0
            for s in sources:
                G = grammar(adj, L)
                ans = G.constrained_reach(s)
                ex_p += G.explored; ops_p += G.ops.reset()
                o = Ops()
                un = unconstrained(adj, n, s, o)
                ex_u += len(un); ops_u += o.reset()
                wrong += len(un ^ ans)  # vertices a filter-free search misreports
            k = len(sources)
            r = {"n": n, "avg_deg": deg, "L": L, "Q": Dq,
                 "product_states_mean": ex_p / k, "unconstrained_states_mean": ex_u / k,
                 "ratio_product_over_unconstrained": ex_p / max(1, ex_u),
                 "product_ops_mean": ops_p / k, "unconstrained_ops_mean": ops_u / k,
                 "misreported_vertices_mean": wrong / k}
            rows.append(r)
            print(f"n={n:6d} deg={deg} L={L:9s} |Q|={Dq} product={r['product_states_mean']:9.1f} "
                  f"unconstr={r['unconstrained_states_mean']:9.1f} "
                  f"ratio={r['ratio_product_over_unconstrained']:.3f} "
                  f"misreported={r['misreported_vertices_mean']:.1f}")

    # walk enumeration vs product construction (tiny graph, exact comparison)
    tiny = []
    adj = labelled_gnp(12, 2.5, rng)
    for L in LANGS:
        D = dfa(L)
        G = grammar(adj, L)
        ans = G.constrained_reach(0)
        bound = 12 * len(D.states)  # any accepted walk can be shortened to this
        for ml in (4, 8, 12, bound):
            got, explored = naive_walks(adj, D, 0, ml)
            status = "aborted(cap)" if got is None else ("exact" if got == ans else "INCOMPLETE")
            tiny.append({"L": L, "max_len": ml, "walks_explored": explored,
                         "status": status, "product_states": G.explored})
            print(f"tiny L={L:9s} max_len={ml:3d} walks={explored:9d} "
                  f"{status:12s} product_states={G.explored}")
            if got is None:
                break
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp003.json"), "w") as f:
        json.dump({"experiment": "CGT-EXP-003", "seed": SEED, "env": env_info(),
                   "rows": rows, "tiny": tiny}, f, indent=1)


if __name__ == "__main__":
    main()
