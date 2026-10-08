"""Operational grammars (CGT-DEF-003) and the three-layer execution model.

An :class:`OperationalGrammar` pairs a :class:`Structure` with its move
signature and an optional admissibility language (a :class:`~cgtsdk.automata.DFA`
over move names).  An *operation expression* such as ``"get(2); set(0, 9)"``
is evaluated in three separate layers (FORMAL_MODELS §2):

1. **syntax**     -- is the expression well formed, are the moves known, are
                     arities right, and is the word of move names in ℒ?
2. **semantics**  -- what does it denote?  Computed by the structure's
                     *reference semantics* on an abstract value, at no cost.
3. **execution**  -- what does it cost?  Computed by running the structure's
                     *representation*, counting every elementary step.

:meth:`OperationalGrammar.execute` runs all three and, by default, checks
*adequacy*: the executed values must equal the denoted values.  Every
structure shipped with the SDK is tested for adequacy on random workloads.
"""
from __future__ import annotations

import ast
import copy
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .automata import DFA, compile_regex
from .cost import Cost


class Inadmissible(Exception):
    """Raised when a call is semantically undefined in the current state
    (e.g. an index out of range, popping an empty stack, moving to a missing
    child).  This is the *semantic* layer saying ⟦w⟧(x) = ∅."""


@dataclass(frozen=True)
class Move:
    """One symbol of a move signature."""

    name: str
    params: Tuple[str, ...] = ()
    doc: str = ""
    mutates: bool = False

    @property
    def arity(self) -> int:
        return len(self.params)

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.params)})" if self.params else self.name


@dataclass(frozen=True)
class Call:
    """One occurrence of a move in an expression."""

    name: str
    args: Tuple[Any, ...] = ()

    def __str__(self) -> str:
        return f"{self.name}({', '.join(map(repr, self.args))})" if self.args else self.name


_CALL = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\(([^()]*)\))?\s*[;,]?")


def parse_expression(src: str) -> List[Call]:
    """Parse ``"get(2); set(0, 9) L R"`` into calls.  Arguments are Python
    literals (ints, floats, strings, tuples).  Raises SyntaxError."""
    calls, pos, src = [], 0, src.strip()
    while pos < len(src):
        m = _CALL.match(src, pos)
        if not m or m.end() == pos:
            raise SyntaxError(f"cannot parse expression at {src[pos:pos + 12]!r}")
        name, _, argsrc = m.groups()
        args: Tuple[Any, ...] = ()
        if argsrc is not None and argsrc.strip():
            try:
                val = ast.literal_eval(f"({argsrc},)")
            except (ValueError, SyntaxError) as e:
                raise SyntaxError(f"bad arguments in {name}({argsrc}): {e}") from None
            args = tuple(val)
        calls.append(Call(name, args))
        pos = m.end()
    return calls


class Structure:
    """Base class for a computational structure with an operational grammar.

    Subclasses provide:

    * ``SIGNATURE``: the move signature (tuple of :class:`Move`);
    * ``abstract()``: the abstract value the representation stands for;
    * ``denote(state, call)``: pure reference semantics, returning
      ``(new_state, value)`` or raising :class:`Inadmissible`;
    * ``apply(call, cost)``: execute on the representation, counting cost.
    """

    SIGNATURE: Tuple[Move, ...] = ()
    name = "structure"

    def signature(self) -> Dict[str, Move]:
        return {m.name: m for m in self.SIGNATURE}

    def abstract(self) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    @classmethod
    def denote(cls, state: Any, call: Call) -> Tuple[Any, Any]:  # pragma: no cover
        raise NotImplementedError

    def apply(self, call: Call, cost: Cost) -> Any:  # pragma: no cover
        raise NotImplementedError

    def size_words(self) -> int:
        """Space of the representation in machine words (approximate per
        documented layout; see each structure)."""
        return 0

    def grammar(self, admissible: Optional[str | DFA] = None) -> "OperationalGrammar":
        return OperationalGrammar(self, admissible)


@dataclass
class SyntaxReport:
    ok: bool
    calls: List[Call] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """Outcome of :meth:`OperationalGrammar.execute`, one field per layer."""

    expression: str
    syntax: SyntaxReport
    defined: Optional[bool] = None          # semantic layer
    undefined_at: Optional[int] = None      # index of first undefined call
    reason: Optional[str] = None
    denoted: List[Any] = field(default_factory=list)
    values: List[Any] = field(default_factory=list)   # execution layer
    cost: Cost = field(default_factory=Cost)
    adequate: Optional[bool] = None

    @property
    def value(self) -> Any:
        return self.values[-1] if self.values else None

    def summary(self) -> str:
        if not self.syntax.ok:
            return f"syntax error: {self.syntax.error}"
        if not self.defined:
            return f"undefined at call {self.undefined_at}: {self.reason}"
        return f"values={self.values} cost={self.cost.total} {self.cost.snapshot()}"


class OperationalGrammar:
    """G = (Σ, 𝔄, ⟦·⟧, ℒ): moves, structure, semantics, admissibility."""

    def __init__(self, structure: Structure, admissible: Optional[str | DFA] = None):
        self.structure = structure
        self.moves = structure.signature()
        if isinstance(admissible, str):
            admissible = compile_regex(admissible)
        self.admissible: Optional[DFA] = admissible
        #: ℒ constrains the *projection* of the move word onto the letters ℒ
        #: mentions (Γ ⊆ Σ); other moves (observers such as ``here``) are free.
        self.constrained = frozenset(admissible.alphabet) if admissible is not None else frozenset()
        unknown = self.constrained - set(self.moves)
        if unknown:
            raise ValueError(f"admissibility language mentions unknown moves {sorted(unknown)}")

    # ---------------------------------------------------------- layer 1
    def check_syntax(self, expr: str | Sequence[Call]) -> SyntaxReport:
        try:
            calls = parse_expression(expr) if isinstance(expr, str) else list(expr)
        except SyntaxError as e:
            return SyntaxReport(False, [], str(e))
        for i, c in enumerate(calls):
            m = self.moves.get(c.name)
            if m is None:
                return SyntaxReport(False, calls, f"call {i}: unknown move {c.name!r}; "
                                    f"signature is {sorted(self.moves)}")
            if len(c.args) != m.arity:
                return SyntaxReport(False, calls, f"call {i}: {c.name} takes {m.arity} "
                                    f"argument(s) {m.params}, got {len(c.args)}")
        if self.admissible is not None:
            word = [c.name for c in calls if c.name in self.constrained]
            if not self.admissible.accepts(word):
                return SyntaxReport(False, calls, f"move word {' '.join(word) or 'ε'} is not in "
                                    "the admissibility language")
        return SyntaxReport(True, calls)

    # ---------------------------------------------------------- layer 2
    def denote(self, calls: Sequence[Call]) -> Tuple[bool, List[Any], Optional[int], Optional[str]]:
        state = copy.deepcopy(self.structure.abstract())
        out = []
        for i, c in enumerate(calls):
            try:
                state, v = type(self.structure).denote(state, c)
            except Inadmissible as e:
                return False, out, i, str(e)
            out.append(v)
        return True, out, None, None

    # ---------------------------------------------------------- layer 3
    def execute(self, expr: str | Sequence[Call], trace: bool = False,
                check_adequacy: bool = True) -> ExecutionResult:
        """Run the expression on the representation (mutating it)."""
        src = expr if isinstance(expr, str) else " ".join(map(str, expr))
        syn = self.check_syntax(expr)
        res = ExecutionResult(src, syn, cost=Cost(trace=trace))
        if not syn.ok:
            return res
        defined, denoted, at, why = self.denote(syn.calls) if check_adequacy else (True, [], None, None)
        res.denoted = denoted
        for i, c in enumerate(syn.calls):
            res.cost.note(f"[{i}] {c}")
            try:
                res.values.append(self.structure.apply(c, res.cost))
            except Inadmissible as e:
                res.defined, res.undefined_at, res.reason = False, i, str(e)
                if check_adequacy:
                    res.adequate = (not defined) and at == i and denoted == res.values
                return res
        res.defined = True
        if check_adequacy:
            res.adequate = defined and denoted == res.values
        return res

    def resolve(self, expr: str) -> Any:
        """Execute and return the last value, raising on any failure."""
        r = self.execute(expr)
        if not r.syntax.ok:
            raise SyntaxError(r.syntax.error)
        if not r.defined:
            raise Inadmissible(r.reason)
        if r.adequate is False:
            raise AssertionError(f"representation disagrees with semantics on {expr!r}")
        return r.value
