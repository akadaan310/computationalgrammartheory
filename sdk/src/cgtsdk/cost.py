"""Cost accounting (CGT-DEF-005).

A :class:`Cost` counts elementary steps by *category*.  A :class:`CostModel`
assigns a weight to each category and fixes the machine word size, so the
same execution can be reported under different models without re-running it.

Every number produced here is a **count of operations performed by the
code**, never an estimate -- with one documented exception: operations on
multi-word integers are charged ``ceil(bits / word_bits)`` word operations
via :meth:`Cost.word_arith`, which is how the word-RAM model is defined.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

#: Categories used throughout the SDK.  New categories may be added freely;
#: unknown categories get weight 1 in every model.
CATEGORIES = (
    "read",      # read one memory cell / field
    "write",     # write one memory cell / field
    "compare",   # one comparison
    "arith",     # one word-RAM arithmetic or bitwise operation
    "pointer",   # follow one pointer
    "hash",      # evaluate a hash function once
    "probe",     # one probe of a hash table slot
    "alloc",     # allocate one cell
    "edge",      # inspect one edge (graph algorithms)
    "rule",      # attempt one grammar rule / product transition
)


@dataclass(frozen=True)
class CostModel:
    """Weights per category and the machine word size (bits)."""

    name: str = "unit"
    word_bits: int = 64
    weights: Tuple[Tuple[str, float], ...] = ()

    def weight(self, category: str) -> float:
        for k, v in self.weights:
            if k == category:
                return v
        return 1.0


UNIT = CostModel()
#: Example alternative: memory traffic only (reads, writes, pointer hops, probes).
MEMORY = CostModel("memory", 64, tuple((c, 1.0 if c in ("read", "write", "pointer", "probe") else 0.0)
                                     for c in CATEGORIES))


class Cost:
    """Mutable operation counter, optionally recording a trace."""

    __slots__ = ("counts", "trace", "word_bits", "_tracing")

    def __init__(self, trace: bool = False, word_bits: int = 64):
        self.counts: Dict[str, int] = {}
        self.trace: List[Tuple[str, str]] = []
        self.word_bits = word_bits
        self._tracing = trace

    # -- counting ------------------------------------------------------
    def add(self, category: str, k: int = 1, note: Optional[str] = None) -> None:
        self.counts[category] = self.counts.get(category, 0) + k
        if self._tracing and note is not None:
            self.trace.append((category, note))

    def word_arith(self, bits: int, k: int = 1, note: Optional[str] = None) -> None:
        """Charge k arithmetic operations on `bits`-bit integers."""
        self.add("arith", k * max(1, -(-bits // self.word_bits)), note)

    def note(self, text: str) -> None:
        if self._tracing:
            self.trace.append(("note", text))

    # -- reporting -----------------------------------------------------
    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def weighted(self, model: CostModel = UNIT) -> float:
        return sum(model.weight(c) * k for c, k in self.counts.items())

    def snapshot(self) -> Dict[str, int]:
        return dict(sorted(self.counts.items()))

    def merge(self, other: "Cost") -> None:
        for c, k in other.counts.items():
            self.add(c, k)
        self.trace.extend(other.trace)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Cost(total={self.total}, {self.snapshot()})"


def null_cost() -> Cost:
    """A counter for callers that do not care about cost."""
    return Cost()


@dataclass
class Report:
    """A cost profile row (CGT-DEF-005) for one implementation on one workload."""

    implementation: str
    build: Dict[str, int] = field(default_factory=dict)
    query: Dict[str, int] = field(default_factory=dict)
    queries: int = 0
    space_words: Optional[int] = None
    wall_seconds: Optional[float] = None
    correct: Optional[bool] = None

    @property
    def build_total(self) -> int:
        return sum(self.build.values())

    @property
    def query_total(self) -> int:
        return sum(self.query.values())

    @property
    def per_query(self) -> float:
        return self.query_total / self.queries if self.queries else 0.0

    def as_dict(self) -> dict:
        return {"implementation": self.implementation, "build": self.build,
                "build_total": self.build_total, "query": self.query,
                "query_total": self.query_total, "queries": self.queries,
                "per_query": self.per_query, "space_words": self.space_words,
                "wall_seconds": self.wall_seconds, "correct": self.correct}


def break_even(build_a: float, per_query_a: float, per_query_b: float) -> float:
    """Queries after which scheme A (build cost, cheaper queries) beats B
    (no build).  CGT-PROP-005 with a single epoch.  inf if A never wins."""
    d = per_query_b - per_query_a
    return build_a / d if d > 0 else float("inf")
