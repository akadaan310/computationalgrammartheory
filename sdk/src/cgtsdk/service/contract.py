"""Grammar as a Service (GaaS) -- reference contract ``cgt-gaas/0.1``.

The contract is a pure function :func:`handle` from a JSON request to a JSON
response.  The HTTP server in :mod:`cgtsdk.service.server` is a thin
transport around it; the same function can be called in-process, so the
whole curriculum works offline.

Design rules (GRAMMAR_AS_A_SERVICE.md):

* every request names a *versioned* grammar (structure kind + version) or an
  algorithm with declared capabilities;
* rejection is layered: ``syntax`` (malformed / not admissible),
  ``semantics`` (⟦w⟧ undefined), ``execution`` (quota exceeded);
* every response carries a cost report and provenance (hashes of the
  canonical request and result, SDK version, determinism flag);
* quotas bound *counted cost*, number of calls, output size and wall time;
  expressing a computation grammatically never makes it free.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from .. import __version__
from ..algorithms import (bfs, constrained_pagerank, dijkstra, pagerank_power, product_reach,
                          tarjan_scc, transitive_closure)
from ..automata import compile_regex
from ..cost import Cost
from ..grammar import OperationalGrammar
from ..structures import (ArrayStructure, BinaryTreeStructure, BSTStructure, DequeStructure,
                          GraphStructure, HashTableStructure, HeapStructure, LinkedListStructure,
                          QueueStructure, StackStructure, TrieStructure)

CONTRACT = "cgt-gaas/0.1"

DEFAULT_LIMITS = {"max_calls": 10_000, "max_cost": 5_000_000, "max_output_items": 100_000,
                  "timeout_ms": 5_000, "max_n": 200_000}
HARD_LIMITS = dict(DEFAULT_LIMITS)  # a request may lower limits, never raise them


class Rejected(Exception):
    def __init__(self, layer: str, code: str, message: str):
        super().__init__(message)
        self.layer, self.code, self.message = layer, code, message


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode()).hexdigest()


# ---------------------------------------------------------------- registries
def _list_arg(init, key, max_n):
    v = init.get(key, [])
    if not isinstance(v, list):
        raise Rejected("syntax", "bad_init", f"init.{key} must be a list")
    if len(v) > max_n:
        raise Rejected("execution", "quota", f"init.{key} longer than max_n={max_n}")
    return v


def _build_graph(init, max_n):
    n = init.get("n")
    if not isinstance(n, int) or not 0 < n <= max_n:
        raise Rejected("syntax", "bad_init", f"init.n must be an integer in [1, {max_n}]")
    edges = _list_arg(init, "edges", 20 * max_n)
    try:
        return GraphStructure(n, [tuple(e) for e in edges])
    except (TypeError, ValueError) as e:
        raise Rejected("syntax", "bad_init", f"edges: {e}") from None


#: name -> (version, builder(init, max_n) -> Structure, description)
STRUCTURES: Dict[str, Tuple[str, Callable, str]] = {
    "array": ("1", lambda i, m: ArrayStructure(_list_arg(i, "values", m)), "dynamic array"),
    "linked_list": ("1", lambda i, m: LinkedListStructure(_list_arg(i, "values", m)), "singly linked list"),
    "stack": ("1", lambda i, m: StackStructure(_list_arg(i, "values", m)), "array-backed stack"),
    "queue": ("1", lambda i, m: QueueStructure(_list_arg(i, "values", m)), "circular queue"),
    "deque": ("1", lambda i, m: DequeStructure(_list_arg(i, "values", m)), "circular deque"),
    "hash_table": ("1", lambda i, m: HashTableStructure([tuple(p) for p in _list_arg(i, "items", m)]),
                   "open addressing, linear probing"),
    "heap": ("1", lambda i, m: HeapStructure(_list_arg(i, "values", m)), "binary min-heap"),
    "trie": ("1", lambda i, m: TrieStructure(_list_arg(i, "words", m)), "character trie"),
    "bst": ("1", lambda i, m: BSTStructure(_list_arg(i, "keys", m), i.get("balance", "none")), "BST / AVL"),
    "binary_tree": ("1", lambda i, m: BinaryTreeStructure.complete(min(int(i.get("n", 1)), m),
                                                                   i.get("representation", "pointer")),
                    "complete binary tree, pointer or heap representation"),
    "graph": ("1", _build_graph, "edge-labelled digraph, relational semantics"),
}


def _adj_from(init, max_n):
    g = _build_graph(init, max_n)
    adj = [[] for _ in range(g.n)]
    for u, _, v in g.edges():
        adj[u].append(v)
    return g, adj


def _alg_pagerank(init, params, cost, max_n):
    _, adj = _adj_from(init, max_n)
    alpha = float(params.get("alpha", 0.85))
    tol = float(params.get("tol", 1e-10))
    r = pagerank_power(adj, alpha, tol=tol, max_iter=int(params.get("max_iter", 1000)), cost=cost)
    return {"scores": r.scores, "iterations": r.iterations, "converged": r.converged,
            "l1_error_bound": r.error_bound}


def _alg_constrained_pagerank(init, params, cost, max_n):
    g = _build_graph(init, max_n)
    d = compile_regex(str(params.get("language", "")))
    scores, pr, N = constrained_pagerank(g.n, g.edges(), d, float(params.get("alpha", 0.85)),
                                         float(params.get("tol", 1e-10)), cost=cost)
    return {"scores": scores, "product_states": N, "iterations": pr.iterations,
            "l1_error_bound": pr.error_bound}


def _alg_reach(init, params, cost, max_n):
    g = _build_graph(init, max_n)
    x = params.get("source", 0)
    if not isinstance(x, int) or not 0 <= x < g.n:
        raise Rejected("syntax", "bad_params", "params.source must be a vertex")
    if "language" in params:
        d = compile_regex(str(params["language"]))
        out, explored = product_reach(g, x, d, cost, return_explored=True)
        return {"reachable": sorted(out), "product_states": explored}
    _, adj = _adj_from(init, max_n)
    dist = bfs(adj, x, cost)
    return {"reachable": [v for v, dv in enumerate(dist) if dv != float("inf")]}


def _alg_sssp(init, params, cost, max_n):
    n = init.get("n")
    if not isinstance(n, int) or not 0 < n <= max_n:
        raise Rejected("syntax", "bad_init", "init.n must be a positive integer")
    wadj = [[] for _ in range(n)]
    for e in _list_arg(init, "weighted_edges", 20 * max_n):
        u, v, w = e
        if not (0 <= u < n and 0 <= v < n) or w < 0:
            raise Rejected("syntax", "bad_init", f"bad weighted edge {e}")
        wadj[u].append((v, w))
    d = dijkstra(wadj, int(params.get("source", 0)), cost)
    return {"distances": [None if x == float("inf") else x for x in d]}


def _alg_scc(init, params, cost, max_n):
    _, adj = _adj_from(init, max_n)
    comp, k = tarjan_scc(adj, cost)
    return {"components": k, "component_of": comp}


#: name -> (fn, exact?, declared complexity, description)
ALGORITHMS: Dict[str, Tuple[Callable, bool, str, str]] = {
    "pagerank": (_alg_pagerank, False, "O(k·(n+m)), k ≤ log(tol)/log(α) iterations",
                 "PageRank by power iteration; approximate with certified L1 error bound"),
    "constrained_pagerank": (_alg_constrained_pagerank, False, "O(k·|Q|·(n+m))",
                             "grammar-constrained random surfer (CGT proposal)"),
    "reach": (_alg_reach, True, "O(n+m), or O(|Q|(|Σ|n+m)) with a language",
              "reachability, optionally language-constrained (THM-001)"),
    "sssp": (_alg_sssp, True, "O((n+m) log n)", "Dijkstra single-source shortest paths"),
    "scc": (_alg_scc, True, "O(n+m)", "Tarjan strongly connected components"),
}


def capabilities() -> Dict[str, Any]:
    return {"contract": CONTRACT, "sdk": __version__, "limits": HARD_LIMITS,
            "structures": {k: {"version": v, "description": d,
                               "moves": None if k == "graph" else
                               sorted(str(m) for m in b({"values": [], "n": 1}, 1).SIGNATURE)}
                           for k, (v, b, d) in STRUCTURES.items()},
            "algorithms": {k: {"exact": e, "complexity": c, "description": d}
                           for k, (_, e, c, d) in ALGORITHMS.items()}}


# ---------------------------------------------------------------- handler
def _limits(req) -> Dict[str, int]:
    lim = dict(HARD_LIMITS)
    for k, v in (req.get("limits") or {}).items():
        if k not in lim:
            raise Rejected("syntax", "bad_limits", f"unknown limit {k!r}")
        if not isinstance(v, (int, float)) or v <= 0:
            raise Rejected("syntax", "bad_limits", f"limit {k} must be positive")
        lim[k] = min(int(v), HARD_LIMITS[k])
    return lim


def _bounded(values, max_items):
    count = 0

    def walk(x):
        nonlocal count
        count += 1
        if isinstance(x, (list, tuple, set, frozenset)):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for y in x.values():
                walk(y)
    walk(values)
    if count > max_items:
        raise Rejected("execution", "quota", f"output has {count} items > max_output_items={max_items}")


def _jsonable(x):
    if isinstance(x, (set, frozenset)):
        return sorted(_jsonable(y) for y in x)
    if isinstance(x, (list, tuple)):
        return [_jsonable(y) for y in x]
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    return x


def handle(req: Any) -> Dict[str, Any]:
    """Evaluate one request; never raises."""
    t0 = time.perf_counter()
    resp: Dict[str, Any] = {"contract": CONTRACT}
    cost = Cost()
    try:
        if not isinstance(req, dict):
            raise Rejected("syntax", "bad_request", "request must be a JSON object")
        if req.get("contract", CONTRACT) != CONTRACT:
            raise Rejected("syntax", "contract_mismatch", f"server speaks {CONTRACT}")
        lim = _limits(req)
        init = req.get("init") or {}
        if not isinstance(init, dict):
            raise Rejected("syntax", "bad_init", "init must be an object")
        if "algorithm" in req:
            name = req["algorithm"]
            if name not in ALGORITHMS:
                raise Rejected("syntax", "unknown_algorithm", f"unknown algorithm {name!r}")
            fn, exact, _, _ = ALGORITHMS[name]
            try:
                result = fn(init, req.get("params") or {}, cost, lim["max_n"])
            except SyntaxError as e:
                raise Rejected("syntax", "bad_language", str(e)) from None
            resp.update(status="ok", exact=exact, result=result)
        else:
            g = req.get("grammar") or {}
            kind, version = g.get("structure"), str(g.get("version", "1"))
            if kind not in STRUCTURES:
                raise Rejected("syntax", "unknown_structure", f"unknown structure {kind!r}")
            if STRUCTURES[kind][0] != version:
                raise Rejected("syntax", "version_mismatch",
                               f"{kind} is at version {STRUCTURES[kind][0]}, request asked {version}")
            structure = STRUCTURES[kind][1](init, lim["max_n"])
            try:
                grammar = OperationalGrammar(structure, g.get("admissible"))
            except (SyntaxError, ValueError) as e:
                raise Rejected("syntax", "bad_language", str(e)) from None
            expr = req.get("expression")
            if not isinstance(expr, str):
                raise Rejected("syntax", "bad_expression", "expression must be a string")
            syn = grammar.check_syntax(expr)
            if not syn.ok:
                raise Rejected("syntax", "inadmissible", syn.error)
            if len(syn.calls) > lim["max_calls"]:
                raise Rejected("execution", "quota", f"{len(syn.calls)} calls > max_calls={lim['max_calls']}")
            values = []
            for i, c in enumerate(syn.calls):
                r = grammar.execute([c], check_adequacy=False)
                cost.merge(r.cost)
                if not r.defined:
                    resp.update(status="undefined", layer="semantics", undefined_at=i, reason=r.reason)
                    break
                values.append(_jsonable(r.value))
                if cost.total > lim["max_cost"]:
                    raise Rejected("execution", "quota", f"cost exceeded max_cost={lim['max_cost']} at call {i}")
                if (time.perf_counter() - t0) * 1000 > lim["timeout_ms"]:
                    raise Rejected("execution", "timeout", f"timeout at call {i}")
            else:
                resp.update(status="ok", exact=True)
            resp["values"] = values
        if cost.total > lim["max_cost"]:
            raise Rejected("execution", "quota", f"cost {cost.total} > max_cost={lim['max_cost']}")
        _bounded(resp.get("values", resp.get("result")), lim["max_output_items"])
    except Rejected as e:
        resp = {"contract": CONTRACT, "status": "rejected", "layer": e.layer,
                "error": {"code": e.code, "message": e.message}}
    except Exception as e:  # pragma: no cover - defensive: never leak a traceback
        resp = {"contract": CONTRACT, "status": "error",
                "error": {"code": "internal", "message": type(e).__name__}}
    resp["cost"] = {"total": cost.total, "counts": cost.snapshot()}
    payload = {k: v for k, v in resp.items() if k not in ("provenance",)}
    resp["provenance"] = {"sdk": __version__, "request_sha256": _sha(req),
                          "result_sha256": _sha(payload), "deterministic": True,
                          "wall_ms": round((time.perf_counter() - t0) * 1000, 3)}
    return resp
