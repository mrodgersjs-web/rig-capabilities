"""HTTP federation server with optional Bearer auth.

Public (always):  GET /health /version /public-catalog.json
Protected:        GET /index.json /federation.json
  — if a serve token is configured, these require
    `Authorization: Bearer <token>`.
  — if no token is configured, they stay open and /health reports auth=false.

Token source: RIG_CAPABILITIES_SERVE_TOKEN or `.serve.token` (gitignored).
"""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import VERSION_LADDER, __version__
from .surface import public_assets, write_public_catalog

_PUBLIC = {"/health", "/", "/version", "/public-catalog.json"}
_PROTECTED = {"/index.json", "/federation.json"}


def load_serve_token(repo) -> str | None:
    env = os.environ.get("RIG_CAPABILITIES_SERVE_TOKEN")
    if env and env.strip():
        return env.strip()
    p = Path(repo.root) / ".serve.token"
    if p.exists():
        try:
            t = p.read_text().strip()
        except OSError:
            return None
        return t or None
    return None


def generate_serve_token(repo) -> Path:
    p = Path(repo.root) / ".serve.token"
    if not p.exists():
        p.write_text(os.urandom(24).hex())
        try:
            p.chmod(0o600)
        except OSError:
            pass
    return p


def _json_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode()


def _bearer_ok(header: str, token: str) -> bool:
    if not header or not token:
        return False
    got = header[7:].strip() if header.lower().startswith("bearer ") else ""
    if not got or len(got) != len(token):
        return False
    return hmac.compare_digest(got.encode(), token.encode())


class _Handler(BaseHTTPRequestHandler):
    repo = None
    token = None

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
        if path in _PROTECTED and self.token:
            if not _bearer_ok(self.headers.get("Authorization") or "", self.token):
                self._send(401, _json_bytes({"error": "unauthorized"}))
                return
        if path in ("/health", "/"):
            idx = repo.index_path.exists()
            self._send(200, _json_bytes({
                "status": "ok" if idx else "degraded",
                "index": idx,
                "version": __version__,
                "auth": bool(self.token),
            }))
            return
        if path == "/stats.json":
            from .stats import compute
            try:
                self._send(200, _json_bytes(compute(repo)))
            except Exception as e:  # noqa: BLE001 — panel must never 500 silently
                self._send(500, _json_bytes({"error": type(e).__name__}))
            return
        if path == "/dashboard":
            from .stats import dashboard_html
            body = dashboard_html().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
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
                "auth": bool(self.token),
            }))
            return
        self._send(404, _json_bytes({"error": "not found", "path": path}))


def make_server(repo, host: str = "127.0.0.1", port: int = 8765,
                token: str | None = None) -> ThreadingHTTPServer:
    tok = token if token is not None else load_serve_token(repo)
    handler = type("Handler", (_Handler,), {"repo": repo, "token": tok})
    httpd = ThreadingHTTPServer((host, port), handler)
    httpd.allow_reuse_address = True
    return httpd


def serve(repo, host: str = "127.0.0.1", port: int = 8765,
          token: str | None = None) -> None:
    httpd = make_server(repo, host, port, token=token)
    auth = bool(getattr(httpd.RequestHandlerClass, "token", None))
    print(f"rig-capabilities serve {host}:{port} auth={auth}  "
          f"(public: /health /public-catalog.json; protected: /index.json)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
