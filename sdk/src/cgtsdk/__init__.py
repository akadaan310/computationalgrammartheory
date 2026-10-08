"""cgtsdk -- the Computational Grammar Theory SDK.

The executable companion to *Computational Grammar Theory* (research program
of Abed Kadaan).  Core ideas, each a module:

* :mod:`cgtsdk.grammar`    -- operational grammars and the three layers
                              (syntax, semantics, execution);
* :mod:`cgtsdk.cost`       -- explicit cost accounting;
* :mod:`cgtsdk.automata`   -- admissibility languages (regex -> minimal DFA);
* :mod:`cgtsdk.structures` -- reference structures with grammars;
* :mod:`cgtsdk.algorithms` -- classical baselines and grammar-driven algorithms;
* :mod:`cgtsdk.lab`        -- generators, comparisons, experiment records;
* :mod:`cgtsdk.service`    -- the Grammar-as-a-Service reference contract.

Standard library only.  Python ≥ 3.10.
"""
__version__ = "0.1.0"

from .automata import DFA, compile_regex  # noqa: E402
from .cost import MEMORY, UNIT, Cost, CostModel, Report, break_even  # noqa: E402
from .grammar import (Call, ExecutionResult, Inadmissible, Move, OperationalGrammar,  # noqa: E402
                      Structure, parse_expression)

__all__ = ["__version__", "DFA", "compile_regex", "Cost", "CostModel", "Report", "UNIT", "MEMORY",
           "break_even", "Call", "ExecutionResult", "Inadmissible", "Move", "OperationalGrammar",
           "Structure", "parse_expression"]
