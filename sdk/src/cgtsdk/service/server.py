"""Minimal HTTP transport for the GaaS contract (local reference server).

    python -m cgtsdk.service.server --port 8765

Endpoints: ``GET /v1/health``, ``GET /v1/capabilities``, ``POST /v1/execute``.
Bodies larger than 1 MiB are refused.  Results are cached by the SHA-256 of
the canonical request: the contract is deterministic, so a cache hit is
exactly the result a fresh evaluation would produce (cache validity is
therefore unconditional for this reference server; see
GRAMMAR_AS_A_SERVICE.md §6 for when it is not).

This server is for local study.  It binds to 127.0.0.1 by default and has no
authentication; do not expose it to untrusted networks.
"""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

from .contract import CONTRACT, _sha, capabilities, handle

MAX_BODY = 1 << 20
_CACHE: "OrderedDict[str, dict]" = OrderedDict()
_LOCK = Lock()
CACHE_SIZE = 256


def cached_handle(req):
    key = _sha(req)
    with _LOCK:
        if key in _CACHE:
            _CACHE.move_to_end(key)
            hit = dict(_CACHE[key]); hit["provenance"] = dict(hit["provenance"], cache="hit")
            return hit
    resp = handle(req)
    with _LOCK:
        _CACHE[key] = resp
        while len(_CACHE) > CACHE_SIZE:
            _CACHE.popitem(last=False)
    return dict(resp, provenance=dict(resp["provenance"], cache="miss"))


class Handler(BaseHTTPRequestHandler):
    server_version = "cgt-gaas/0.1"

    def _send(self, code, obj):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/v1/health":
            return self._send(200, {"status": "ok", "contract": CONTRACT})
        if self.path == "/v1/capabilities":
            return self._send(200, capabilities())
        self._send(404, {"status": "rejected", "error": {"code": "not_found", "message": self.path}})

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/execute":
            return self._send(404, {"status": "rejected", "error": {"code": "not_found"}})
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return self._send(413, {"status": "rejected", "layer": "syntax",
                                    "error": {"code": "too_large", "message": f"body > {MAX_BODY} bytes"}})
        try:
            req = json.loads(self.rfile.read(n) or b"null")
        except json.JSONDecodeError as e:
            return self._send(400, {"status": "rejected", "layer": "syntax",
                                    "error": {"code": "bad_json", "message": str(e)}})
        resp = cached_handle(req)
        self._send(200 if resp["status"] in ("ok", "undefined") else 422, resp)

    def log_message(self, *args):  # quiet
        pass


def serve(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main():  # pragma: no cover
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    srv = serve(a.host, a.port)
    print(f"cgt-gaas reference server on http://{a.host}:{a.port}")
    srv.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    main()
