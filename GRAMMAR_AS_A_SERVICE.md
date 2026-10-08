# Grammar as a Service: contract `cgt-gaas/0.1`

**Status:** proposed design with a working **local reference implementation** (`sdk/src/cgtsdk/service/`). This is not a deployed service; no hosted endpoint exists or is implied. The rationale and its relation to the theory are in Chapter 19 of the book (`book/content/chapters/19-gaas.md`). This file is the normative contract.

Nothing in the curriculum needs this service: every operation is available in-process through the SDK, with no account, key or network.

## 1. Principles

1. **Versioned grammars.** A request names a structure kind *and* a version. A semantic change to a grammar requires a new version, so results stay cacheable (§6).
2. **Layered rejection.** Every "no" names the layer that produced it: `syntax`, `semantics` or `execution` (CGT three-layer separation, DEF-003).
3. **Quotas in counted cost.** Limits are deterministic, so a request that fits on one machine fits on every machine. Expressing a computation grammatically never makes it free.
4. **Determinism and provenance.** A response is a function of the request. It carries the SHA-256 of the canonical request and of the result.
5. **No client code.** The service executes only moves of registered structures and registered algorithms.

## 2. Request

```json
{
  "contract": "cgt-gaas/0.1",
  "grammar": {"structure": "graph", "version": "1", "admissible": "(a b)*"},
  "init": {"n": 4, "edges": [[0, "a", 1], [1, "b", 2], [2, "a", 3]]},
  "expression": "at(0) a b here",
  "limits": {"max_cost": 10000, "timeout_ms": 500}
}
```

A request also comes in an **algorithm form**: `{"algorithm": "<name>", "init": {...}, "params": {...}, "limits": {...}}`.

| Field | Required | Meaning |
|---|---|---|
| `contract` | no (defaults to the current contract) | if present, it must equal `cgt-gaas/0.1`; otherwise the request is rejected with `contract_mismatch` |
| `grammar.structure` | yes (grammar form) | one of the structures in §4 |
| `grammar.version` | no (defaults to `"1"`) | must equal the registered version; otherwise the request is rejected with `version_mismatch` |
| `grammar.admissible` | no | a regular expression over move names; the projection of the move word onto the letters it mentions must be in the language (D-015) |
| `init` | structure-dependent | the initial state, sent with the request; the service is stateless |
| `expression` | yes (grammar form) | calls separated by `;` or whitespace, e.g. `push(1); pop` |
| `algorithm`, `params` | yes (algorithm form) | one of the algorithms in §4, with its parameters |
| `limits` | no | any subset of §5; a request may lower a limit, values above the hard maximum are clamped to it, and unknown limit names are rejected (`bad_limits`) |

## 3. Response

| Field | Meaning |
|---|---|
| `status` | `ok`; `undefined` (the expression is admissible, but a call is undefined in the current state; semantic layer); `rejected` (syntax or execution layer); or `error` (internal failure; only the exception class is reported, never a traceback) |
| `layer` | for `undefined` and `rejected`: `syntax`, `semantics` or `execution` |
| `error` | `{code, message}`; the codes are listed in §5 |
| `values` | per-call values, up to the first undefined call |
| `undefined_at`, `reason` | for `undefined`: index of the first undefined call and why it is undefined |
| `result`, `exact` | algorithm result and whether it is exact; approximate PageRank results carry `result.l1_error_bound`, the certified L1 error from THM-008 |
| `cost` | `total` and `counts`: counted steps by category (`read`, `write`, `compare`, `arith`, `pointer`, `hash`, `probe`, `alloc`, `edge`, `rule`) |
| `provenance` | `sdk` version, `request_sha256`, `result_sha256` (hash of the response without provenance), `deterministic` flag, `wall_ms`; over HTTP also `cache` (`hit` or `miss`) |

## 4. Registered capabilities

`GET /v1/capabilities` returns the live list. In version 0.1:

- **Structures (all at version 1):**
  - sequences: `array`, `linked_list`, `stack`, `queue`, `deque`;
  - associative: `hash_table`, `heap`, `trie`;
  - trees: `bst` (with `balance: "avl"`), `binary_tree` (pointer or heap representation);
  - graphs: `graph` (edge-labelled digraph with relational semantics, plus `at(v)` and `here`).
- **Algorithms:**

| Algorithm | Cost | Result |
|---|---|---|
| `pagerank` | O(k·(n+m)) | approximate, certified bound |
| `constrained_pagerank` | O(k·\|Q\|·(n+m)) | approximate, certified bound (PROP-010) |
| `reach` | O(n+m), or O(\|Q\|(\|Σ\|n+m)) with a language (THM-001) | exact |
| `sssp` | Dijkstra | exact |
| `scc` | Tarjan | exact |

## 5. Limits and error codes

| Limit | Hard maximum (0.1) |
|---|---|
| `max_calls` | 10,000 |
| `max_cost` | 5,000,000 counted steps |
| `max_output_items` | 100,000 |
| `timeout_ms` | 5,000 |
| `max_n` | 200,000 (vertices or elements in `init`) |

| Layer | Codes |
|---|---|
| syntax | `bad_request`, `contract_mismatch`, `unknown_structure`, `version_mismatch`, `bad_init`, `bad_expression`, `bad_language`, `inadmissible`, `bad_limits`, `unknown_algorithm`, `bad_params`; over HTTP also `bad_json` (400) and `too_large` (413, body > 1 MiB) |
| semantics | status `undefined`, with the index of the first undefined call and the reason |
| execution | `quota` (calls, cost or output exceeded), `timeout` |

A syntax rejection charges nothing. A semantic `undefined` charges the calls executed before it. An execution rejection reports the call at which the quota was exceeded.

**Enforcement scope (D-016).** Cost and time limits are checked *between* the calls of an expression. Algorithm requests are bounded by `max_n` and iteration limits and checked after the fact; they are not preempted. A production service would need preemptive limits (separate processes or cooperative cancellation).

## 6. Caching

The contract is deterministic and grammar versions are immutable. A cached response is therefore valid **exactly** when the canonical-request SHA-256 matches. The reference server caches on that hash, and the tests check that a cache hit returns the same `result_sha256` as fresh evaluation. A stateful variant, where structures are stored server-side, would need the structure snapshot version in the key (book Exercise 19.3).

## 7. HTTP binding

| Method and path | Response |
|---|---|
| `GET /v1/health` | `{"status": "ok", "contract": "cgt-gaas/0.1"}` |
| `GET /v1/capabilities` | registered structures, algorithms and limits |
| `POST /v1/execute` | body is a request (§2); HTTP 200 for `ok` and `undefined`, 422 for `rejected` and `error` |

Run locally with `python3 -m cgtsdk.service.server` (binds `127.0.0.1:8765`). In-process: `from cgtsdk.service import handle, Client`. `Client()` calls `handle`, and `Client("http://127.0.0.1:8765")` speaks HTTP. Both return identical result hashes.

## 8. Security boundary

The reference server:
- binds to localhost;
- has **no authentication**;
- refuses bodies over 1 MiB;
- never evaluates client-supplied code;
- returns no tracebacks.

It is for local study. Exposing it to untrusted networks would require authentication, per-client rate limits, preemptive resource isolation and audit logging, and none of these is provided or claimed.

## 9. Tests

`sdk/tests/test_service.py` covers:
- the semantic layer (`undefined_at`);
- the syntax-layer codes `contract_mismatch`, `version_mismatch`, `inadmissible`, `bad_language`, `bad_limits`, plus unknown moves, unknown algorithms and non-object requests;
- execution quotas in counted cost, with clamping of raised limits;
- algorithm results and certified bounds;
- capabilities;
- determinism of result hashes;
- in-process versus HTTP equivalence;
- cache miss then hit;
- the HTTP 413 `too_large` refusal.

Not covered by tests: the `timeout` path, which depends on wall-clock time.
