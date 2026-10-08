"""Grammar as a Service: contract (pure function), local server, client."""
from .contract import CONTRACT, ALGORITHMS, STRUCTURES, capabilities, handle

__all__ = ["CONTRACT", "ALGORITHMS", "STRUCTURES", "capabilities", "handle", "Client"]


class Client:
    """Tiny client.  ``Client()`` calls the contract in-process; pass a URL to
    talk to a server instead.  Both return the same JSON."""

    def __init__(self, url: str = ""):
        self.url = url.rstrip("/")

    def execute(self, request: dict) -> dict:
        if not self.url:
            return handle(request)
        import json
        import urllib.error
        import urllib.request
        req = urllib.request.Request(self.url + "/v1/execute", data=json.dumps(request).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())
