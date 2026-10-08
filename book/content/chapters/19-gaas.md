---
title: Grammar as a Service
status: proposed
statusnote: A research-backed service design with a working local reference implementation; not a deployed service.
description: A contract for requesting operations on versioned grammars, with layered rejection, quotas, determinism, provenance and cache validity — and an argument about what should run where.
---

::: objectives
- State the request/response contract `cgt-gaas/0.1` and the reasons for each of its parts.
- Explain layered rejection — syntax, semantics, execution — as a service-level consequence of the three layers.
- Explain why quotas are stated in counted cost, and why expressing a computation grammatically never makes it free.
- Decide which work belongs locally, ahead of time, in a cache, or remotely.
- Use the reference implementation in-process and over HTTP.
:::

## Why a service at all {#sec:why}

The SDK runs locally, and everything in this book can be done without accounts, keys or a network. A service becomes useful when several clients want to apply the *same* versioned grammars and algorithms to their structures, with uniform validation, cost accounting and provenance — for instance, a team validating agent plans against shared policies (Chapter 17), or a pipeline that needs reproducible, auditable ranking computations. The design question is not "how do we put grammars behind an API" but **what contract makes such a service honest**: a request whose cost the client can bound in advance, a rejection that says which layer failed, and a result whose provenance can be checked.

## The contract {#sec:contract}

A request is a JSON object. It either names a **grammar** — a structure kind and a version — together with an initial state and an operation expression, or names an **algorithm** with declared capabilities, an input and parameters. Both may lower the service's limits.

```text
{ "contract": "cgt-gaas/0.1",
  "grammar":  { "structure": "graph", "version": "1", "admissible": "(a b)*" },
  "init":     { "n": 4, "edges": [[0,"a",1], [1,"b",2], [2,"a",3]] },
  "expression": "at(0) a b here",
  "limits":   { "max_cost": 10000, "timeout_ms": 500 } }
```

A response always contains a status, a cost report and provenance:

| Field | Meaning |
|---|---|
| `status` | `ok`, `undefined` (semantic layer), `rejected` (syntax or execution layer, with `layer` and an error code), or `error` (internal; no details leaked) |
| `values` / `result` | per-call values of an expression, or an algorithm's result |
| `exact` | whether the result is exact or approximate with a stated bound (PageRank returns its certified $L_1$ bound) |
| `cost` | counted steps by category, under the SDK's cost conventions |
| `provenance` | SDK version, SHA-256 of the canonical request and of the result, determinism flag, wall time |

The reference implementation is a pure function, `cgtsdk.service.handle(request) -> response`, wrapped by a small HTTP server. Calling the function in-process and calling the server return the same result hashes.

```python run
from cgtsdk.service import Client

svc = Client()                      # in-process; Client("http://host:port") talks to a server
base = {"grammar": {"structure": "stack", "version": "1"}, "init": {"values": []}}
for expr in ["push(1); push(2); pop", "push(1); pop; pop", "push(1); fly"]:
    r = svc.execute(dict(base, expression=expr))
    print(f"{expr:24s} -> {r['status']:9s} layer={r.get('layer', '-'):9s} values={r.get('values')} cost={r['cost']['total']}"
          + (f" error={r['error']['code']}" if 'error' in r else ""))
r = svc.execute({"grammar": {"structure": "stack", "version": "2"}, "expression": "pop"})
print("version mismatch ->", r["status"], r["error"]["code"], "|", r["error"]["message"])
```

```output
push(1); push(2); pop    -> ok        layer=-         values=[None, None, 2] cost=8
push(1); pop; pop        -> undefined layer=semantics values=[None, 1] cost=4
push(1); fly             -> rejected  layer=syntax    values=None cost=0 error=inadmissible
version mismatch -> rejected version_mismatch | stack is at version 1, request asked 2
```

## Layered rejection {#sec:gaas-layers}

The three layers of Chapter 1 become three kinds of "no":

1. **Syntax** — the request is malformed, names an unknown structure or move, has the wrong arity, asks for the wrong version, or its move word is not in the admissibility language. Nothing is executed and nothing is charged.
2. **Semantics** — the expression is admissible but undefined in the current state. The response reports the index of the first undefined call and the reason; values computed before that call are returned, and their cost is charged.
3. **Execution** — the computation would exceed a quota: too many calls, too much counted cost, too large an output, too much time.

Separating them matters to clients. A syntax rejection is a bug in the request, and retrying will not help. A semantic "undefined" is a fact about the state and may be the expected answer. An execution rejection says the request may succeed with larger limits — but never larger than the service's hard limits.

## Quotas in counted cost {#sec:quotas}

Every request is bounded by `max_calls`, `max_cost` (counted steps), `max_output_items`, `timeout_ms` and `max_n`. A request may lower any limit and never raise one. Stating the main quota in **counted cost** rather than time has two advantages: it is deterministic, so a request that fits its quota on one machine fits it on every machine; and it forces the cost model to be explicit. It also makes the central point of this book operational: **expressing a computation grammatically does not make it cheap.** A `get(4999)` on a linked list of 5,000 elements costs about 5,000 steps whether it is sent as code, as an expression or as a service request, and the quota sees exactly that:

```python run
from cgtsdk.service import handle

req = {"grammar": {"structure": "linked_list"}, "init": {"values": list(range(5000))},
       "expression": "; ".join(["get(4999)"] * 50), "limits": {"max_cost": 100000}}
r = handle(req)
print(r["status"], r["layer"], r["error"]["code"], "-", r["error"]["message"])
r = handle(dict(req, grammar={"structure": "array"}))
print(r["status"], "cost", r["cost"]["total"], "for the same 50 calls on an array")
```

```output
rejected execution quota - cost exceeded max_cost=100000 at call 19
ok cost 150 for the same 50 calls on an array
```

The reference server enforces cost and time limits *between* calls of an expression. Algorithm requests are bounded by input size and iteration limits and checked after the fact; a production service would need preemptive enforcement (separate processes or cooperative cancellation), which the reference implementation does not provide (\ledger{CGT-D-016}).

## Determinism, provenance and caching {#sec:cache}

Every result carries the SHA-256 of the canonical request and of the result. Because the contract is a deterministic function of the request, **a cached result is valid exactly when the request hash matches and the grammar version is unchanged**; the reference server caches on the request hash, and its tests check that a cache hit returns the same result hash as a fresh evaluation. Cache validity becomes conditional when any of the following holds, and a production design must then include them in the key or invalidate explicitly:

- a grammar or algorithm is updated *without* a version change (forbidden by the contract: semantic changes require a new version);
- results depend on external state (a mutable stored structure rather than one sent in `init`);
- results are approximate with non-deterministic algorithms (randomized solvers must take the seed as a parameter).

## What should run where {#sec:where}

The mechanisms of Chapter 7 suggest a placement rule:

| Work | Where | Why |
|---|---|---|
| syntax checks (parsing, arity, admissibility DFA) | client or edge | cheap, deterministic, needs no data; rejects bad requests before any transfer |
| compiling admissibility languages, compiling move words (Ch. 13) | ahead of time, cached by grammar version | M-PRE on the *query* side: pay once per version |
| building indexes (closures, labelings) | where the data lives, with break-even accounting | M-PRE on the *data* side: only worthwhile past $Q^*$ queries per epoch (Ch. 12) |
| executing expressions on large structures | where the structure lives | moving the structure costs more than moving the request |
| small structures sent in `init` | anywhere; the service is stateless | determinism and caching are then unconditional |

The reference implementation is deliberately stateless: structures arrive in `init`, so every request is self-contained, reproducible and cacheable. Stateful services — structures stored server-side and mutated by requests — need access control, isolation between clients and versioned snapshots, and are outside the current contract.

## Security boundaries {#sec:security}

The reference server binds to `127.0.0.1` by default, has no authentication, refuses bodies larger than 1 MiB, never executes client-supplied code (only moves of registered structures and registered algorithms), and returns no tracebacks. It is for local study. Exposing it to untrusted networks would require authentication, rate limiting per client, preemptive resource limits and audit logging — none of which is claimed here.

::: exercise {#exr:19-1}
Write a request that asks the service for language-constrained reachability on a graph you choose, and a second request whose answer you can predict to be `undefined` in the semantic layer. Verify both with `Client()`.
:::

::: exercise {#exr:19-2}
Extend the contract with a `compile` operation that returns the compiled form of a move word for heap-shaped trees (Chapter 13). Which layer rejects a word with an unknown move? Is the compiled form cacheable, and under which key?
:::

::: exercise {#exr:19-3}
Design the cache key and invalidation rule for a *stateful* variant of the service in which structures are stored server-side and mutated by requests.
:::

::: summary
- `cgt-gaas/0.1` requests name a versioned grammar or a declared algorithm; responses carry status, values, exactness, counted cost and provenance hashes.
- Rejections are layered — syntax, semantics, execution — and mean different things to clients.
- Quotas are stated in counted cost, deterministic across machines; a grammatical request costs what its execution costs.
- Results are cacheable by request hash because the contract is deterministic and grammar versions are immutable.
- Syntax checks and compilation belong ahead of the data; index building belongs with the data and must pass break-even; the reference server is local, stateless and not hardened.
:::
