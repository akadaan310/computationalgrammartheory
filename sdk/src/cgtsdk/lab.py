"""The algorithm laboratory: deterministic generators, side-by-side
comparison with correctness checking, and serialisable experiment records.

Typical use (book Chapter 2)::

    from cgtsdk.lab import compare_structures, random_index_workload
    from cgtsdk.structures import ArrayStructure, LinkedListStructure

    work = random_index_workload(n=1000, queries=200, seed=1)
    table = compare_structures([ArrayStructure, LinkedListStructure],
                               values=range(1000), expressions=work)
    for row in table:
        print(row.implementation, row.per_query, row.correct)
"""
from __future__ import annotations

import hashlib
import json
import platform
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from . import __version__
from .cost import Cost, Report


# ----------------------------------------------------------------- generators
def random_index_workload(n: int, queries: int, seed: int = 0, op: str = "get") -> List[str]:
    rng = random.Random(seed)
    return [f"{op}({rng.randrange(n)})" for _ in range(queries)]


def random_digraph(n: int, avg_deg: float, seed: int = 0, dag: bool = False) -> List[List[int]]:
    rng = random.Random(seed)
    adj: List[List[int]] = [[] for _ in range(n)]
    seen = set()
    target = int(avg_deg * n)
    limit = n * (n - 1) // (2 if dag else 1)
    while len(seen) < min(target, limit):
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v or (dag and u > v):
            continue
        if (u, v) not in seen:
            seen.add((u, v)); adj[u].append(v)
    return adj


def random_labelled_graph(n: int, avg_deg: float, labels: Sequence[str], seed: int = 0):
    rng = random.Random(seed)
    return [(rng.randrange(n), rng.choice(labels), rng.randrange(n)) for _ in range(int(avg_deg * n))]


def random_weighted(adj: Sequence[Sequence[int]], seed: int = 0, lo: int = 1, hi: int = 20):
    rng = random.Random(seed)
    return [[(v, rng.randint(lo, hi)) for v in nbrs] for nbrs in adj]


def random_parent_array(n: int, seed: int = 0, shape: str = "random") -> List[int]:
    """Rooted tree on 0..n-1 with root 0.  shape: random | path | star | complete."""
    rng = random.Random(seed)
    if shape == "path":
        return [-1] + list(range(n - 1))
    if shape == "star":
        return [-1] + [0] * (n - 1)
    if shape == "complete":
        return [-1] + [(i - 1) // 2 for i in range(1, n)]
    return [-1] + [rng.randrange(i) for i in range(1, n)]


# ----------------------------------------------------------------- comparison
def compare_structures(classes: Sequence[type], values: Iterable[Any], expressions: Sequence[str],
                       baseline: Optional[type] = None) -> List[Report]:
    """Run the same expressions on a fresh instance of each structure class.
    Correctness: each implementation's values must equal the reference
    semantics (adequacy) *and* the baseline implementation's values."""
    values = list(values)
    rows, ref_values = [], None
    base = baseline or classes[0]
    ordered = [base] + [c for c in classes if c is not base]
    for cls in ordered:
        t0 = time.perf_counter()
        build = Cost()
        s = cls(values)
        g = s.grammar()
        build_counts = {"write": len(values)}
        q = Cost()
        vals, ok = [], True
        for e in expressions:
            r = g.execute(e)
            ok &= bool(r.syntax.ok and r.adequate)
            q.merge(r.cost)
            vals.append(r.values)
        if ref_values is None:
            ref_values = vals
        ok &= vals == ref_values
        rows.append(Report(cls.__name__, build_counts, q.snapshot(), len(expressions),
                           s.size_words(), time.perf_counter() - t0, ok))
    return rows


def compare_functions(impls: Dict[str, Callable[..., Any]], inputs: Sequence[Tuple],
                      oracle: Callable[..., Any], builds: Optional[Dict[str, Callable]] = None
                      ) -> List[Report]:
    """Compare algorithm implementations ``f(*args, cost=...)`` on the same
    inputs against an independent oracle.  ``builds`` optionally maps a name
    to a preprocessing function ``b(cost) -> f`` whose cost is reported
    separately as build cost."""
    rows = []
    expected = [oracle(*a) for a in inputs]
    for name, f in impls.items():
        build = Cost()
        t0 = time.perf_counter()
        if builds and name in builds:
            f = builds[name](build)
        q = Cost()
        got = [f(*a, cost=q) for a in inputs]
        rows.append(Report(name, build.snapshot(), q.snapshot(), len(inputs), None,
                           time.perf_counter() - t0, got == expected))
    return rows


def format_table(rows: Sequence[Report]) -> str:
    head = f"{'implementation':28s} {'build':>10s} {'per query':>12s} {'space(w)':>10s} correct"
    lines = [head, "-" * len(head)]
    for r in rows:
        sp = "-" if r.space_words is None else str(r.space_words)
        lines.append(f"{r.implementation:28s} {r.build_total:10d} {r.per_query:12.2f} {sp:>10s} {r.correct}")
    return "\n".join(lines)


# ----------------------------------------------------------------- records
@dataclass
class ExperimentRecord:
    """Serialisable record: what ran, on what, with which seed, and results."""

    experiment: str
    hypothesis: str
    seed: int
    parameters: Dict[str, Any]
    results: List[Dict[str, Any]] = field(default_factory=list)
    falsification: str = ""
    environment: Dict[str, str] = field(default_factory=lambda: {
        "python": sys.version.split()[0], "platform": platform.platform(),
        "cgtsdk": __version__})

    def fingerprint(self) -> str:
        """SHA-256 of the deterministic part (everything except environment
        and wall-clock fields)."""
        def strip(x):
            if isinstance(x, dict):
                return {k: strip(v) for k, v in x.items() if "wall" not in k and k != "environment"}
            if isinstance(x, list):
                return [strip(v) for v in x]
            return x
        blob = json.dumps(strip(asdict(self)), sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()

    def to_json(self) -> str:
        d = asdict(self)
        d["fingerprint"] = self.fingerprint()
        return json.dumps(d, indent=1, default=str)
