# cgt-sdk

The executable companion to *Computational Grammar Theory*, the research program of Abed Kadaan. It provides:
- operational grammars with three separated layers (syntax, semantics and execution);
- explicit cost accounting;
- reference data structures and classical algorithms, with oracle tests;
- compiled move words, shared forests and PageRank solvers with certified error bounds;
- a local reference implementation of the Grammar-as-a-Service contract.

Python ≥ 3.10, standard library only.

```sh
python3 -m pip install -e .            # or: export PYTHONPATH=sdk/src
python3 -m unittest discover -s tests
```

```python
from cgtsdk.structures import StackStructure
r = StackStructure([]).grammar().execute("push(1); push(2); pop")
print(r.values, r.defined, r.cost.total)
```

Specification: `../CGT_SDK_SPEC.md`. Tutorial: Chapter 18 of the book.
