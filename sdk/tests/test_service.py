"""GaaS contract: layered rejection, quotas, determinism, HTTP transport."""
import json
import threading
import unittest

from cgtsdk.service import Client, capabilities, handle
from cgtsdk.service.server import serve


class TestContract(unittest.TestCase):
    def test_ok_and_provenance(self):
        req = {"grammar": {"structure": "array", "version": "1"}, "init": {"values": [5, 3, 8]},
               "expression": "get(2); set(0, 9); get(0)"}
        r1, r2 = handle(req), handle(req)
        self.assertEqual(r1["status"], "ok")
        self.assertEqual(r1["values"], [8, None, 9])
        self.assertEqual(r1["provenance"]["result_sha256"], r2["provenance"]["result_sha256"])
        self.assertEqual(r1["cost"], r2["cost"])

    def test_layers(self):
        base = {"grammar": {"structure": "stack"}, "init": {"values": []}}
        r = handle(dict(base, expression="push(1) pop pop"))
        self.assertEqual((r["status"], r["layer"], r["undefined_at"]), ("undefined", "semantics", 2))
        r = handle(dict(base, expression="fly"))
        self.assertEqual((r["status"], r["layer"]), ("rejected", "syntax"))
        r = handle({"grammar": {"structure": "array", "version": "2"}, "expression": "len"})
        self.assertEqual(r["error"]["code"], "version_mismatch")
        r = handle({"grammar": {"structure": "graph", "admissible": "(a b)*"},
                    "init": {"n": 3, "edges": [[0, "a", 1], [1, "b", 2]]}, "expression": "a"})
        self.assertEqual(r["error"]["code"], "inadmissible")

    def test_quotas(self):
        req = {"grammar": {"structure": "linked_list"}, "init": {"values": list(range(5000))},
               "expression": "; ".join(["get(4999)"] * 50), "limits": {"max_cost": 10000}}
        r = handle(req)
        self.assertEqual((r["status"], r["layer"], r["error"]["code"]), ("rejected", "execution", "quota"))
        # limits can be lowered, never raised
        r = handle(dict(req, limits={"max_cost": 10 ** 12}, expression="get(1)"))
        self.assertEqual(r["status"], "ok")
        r = handle(dict(req, limits={"bogus": 1}))
        self.assertEqual(r["error"]["code"], "bad_limits")

    def test_algorithms(self):
        g = {"n": 4, "edges": [[0, "a", 1], [1, "b", 2], [2, "a", 3], [3, "b", 0]]}
        r = handle({"algorithm": "pagerank", "init": g, "params": {"alpha": 0.85}})
        self.assertEqual(r["status"], "ok")
        self.assertFalse(r["exact"])
        self.assertAlmostEqual(sum(r["result"]["scores"]), 1.0, places=9)
        r = handle({"algorithm": "reach", "init": g, "params": {"source": 0, "language": "(a b)*"}})
        self.assertEqual(r["result"]["reachable"], [0, 2])
        r = handle({"algorithm": "reach", "init": g, "params": {"source": 0, "language": "(a"}})
        self.assertEqual(r["error"]["code"], "bad_language")
        r = handle({"algorithm": "nope"})
        self.assertEqual(r["status"], "rejected")
        r = handle("not an object")
        self.assertEqual(r["status"], "rejected")

    def test_capabilities(self):
        c = capabilities()
        self.assertIn("array", c["structures"])
        self.assertIn("get(i)", c["structures"]["array"]["moves"])
        self.assertTrue(c["algorithms"]["scc"]["exact"])


class TestHTTP(unittest.TestCase):
    def test_roundtrip(self):
        srv = serve(port=0)
        th = threading.Thread(target=srv.serve_forever, daemon=True)
        th.start()
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}"
            req = {"grammar": {"structure": "heap"}, "init": {"values": [4, 1, 3]},
                   "expression": "pop_min pop_min"}
            a = Client(url).execute(req)
            b = Client(url).execute(req)
            local = Client().execute(req)
            self.assertEqual(a["values"], [1, 3])
            self.assertEqual(a["provenance"]["cache"], "miss")
            self.assertEqual(b["provenance"]["cache"], "hit")
            self.assertEqual(a["provenance"]["result_sha256"], local["provenance"]["result_sha256"])
            bad = Client(url).execute({"grammar": {"structure": "heap"}, "expression": "x"})
            self.assertEqual(bad["status"], "rejected")
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
