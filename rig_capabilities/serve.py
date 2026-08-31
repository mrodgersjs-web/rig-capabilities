"""Cross-machine federation server — stdlib http.server.

Exposes:
  GET /health
  GET /version
  GET /public-catalog.json
  GET /index.json          (full catalog; large)
  GET /federation.json     (counts + peer health, no asset bodies)

Bind defaults to 127.0.0.1. Cross-machine: pass --bind 0.0.0.0 and a
firewall/ACL of your own — this process does not authenticate.
"""
from __future__ import annotations

import json
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import VERSION_LADDER, __version__
from .surface import public_assets, write_public_catalog


def _json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode()


class _Handler(BaseHTTPRequestHandler):
    repo = None  # set via factory

    def log_message(self, fmt, *args):
        return

    def _send(self, code: int, body: bytes, ctype: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        repo = self.repo
        if path in ("/health", "/"):
            idx = repo.index_path.exists()
            self._send(200, _json_bytes({
                "status": "ok" if idx else "degraded",
                "index": idx,
                "version": __version__,
            }))
            return
        if path == "/version":
            self._send(200, _json_bytes({"version": __version__,
                                         "ladder": VERSION_LADDER}))
            return
        if path == "/public-catalog.json":
            write_public_catalog(repo)
            p = repo.root / ".public-catalog.json"
            self._send(200, p.read_bytes() if p.exists() else _json_bytes({"count": 0, "assets": []}))
            return
        if path == "/index.json":
            doc = repo.load_index()
            slim = [{"id": a["id"], "kind": a["kind"], "source": a["source"],
                     "name": a.get("name"), "description": a.get("description"),
                     "sha": a.get("sha"), "tags": a.get("tags") or [],
                     "okf": a.get("okf") or {}, "installable": False}
                    for a in doc.get("assets") or []]
            self._send(200, _json_bytes({"count": len(slim), "assets": slim,
                                         "generated_at": doc.get("generated_at")}))
            return
        if path == "/federation.json":
            doc = repo.load_index()
            pub = public_assets(repo)
            self._send(200, _json_bytes({
                "version": __version__,
                "assets": doc.get("count", 0),
                "public": len(pub),
            }))
            return
        self._send(404, _json_bytes({"error": "not found", "path": path}))


def make_server(repo, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    handler = type("Handler", (_Handler,), {"repo": repo})
    httpd = ThreadingHTTPServer((host, port), handler)
    httpd.allow_reuse_address = True
    return httpd


def serve(repo, host: str = "127.0.0.1", port: int = 8765) -> None:
    httpd = make_server(repo, host, port)
    print(f"rig-capabilities serve {host}:{port}  (health /index.json /public-catalog.json)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
