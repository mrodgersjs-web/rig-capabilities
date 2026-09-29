#!/usr/bin/env python3
"""Deterministic OpenAI-compatible fake model server for L2 hello proofs.

Any framework that can point at an OpenAI-compatible base URL (CrewAI, OpenAI Agents SDK,
LangChain ChatOpenAI, LlamaIndex OpenAILike, Pydantic AI, Mastra, n8n, Dify, Flowise,
Langflow) gets a scripted, network-free model: same input, same output, every time.

Endpoints: GET /v1/models; POST /v1/chat/completions (non-streaming and "stream": true SSE);
POST /v1/completions. Replies cycle through --reply values (default "ready"). If the last user
message contains "2 plus 3" the reply is "5", so hello_baseline-style assertions hold.
Every request is appended to --log as JSON (method, path, model, last user message) so a test
can assert the framework actually called the model.

Usage:
  python3 fake_openai_server.py [--port 18999] [--reply ready --reply done] [--log calls.jsonl]
  python3 fake_openai_server.py --selftest     # starts on an ephemeral port, calls itself, exits 0/2
Bind is 127.0.0.1 only. Stdlib only. Any API key is accepted and never logged.
"""
from __future__ import annotations

import argparse
import itertools
import json
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_ID = "fake:scripted"


def make_handler(replies, log_path):
    cycle = itertools.cycle(replies)
    lock = threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence default stderr logging
            pass

        def _json(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _record(self, path, model, text):
            if log_path:
                with lock, open(log_path, "a") as fh:
                    fh.write(json.dumps({"t": time.time(), "path": path, "model": model, "user": text[:200]}) + "\n")

        def do_GET(self):
            if self.path.rstrip("/").endswith("/models"):
                return self._json(200, {"object": "list", "data": [{"id": MODEL_ID, "object": "model", "owned_by": "rig-fake"}]})
            return self._json(404, {"error": {"message": "not found"}})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                req = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                return self._json(400, {"error": {"message": "bad json"}})
            msgs = req.get("messages") or [{"role": "user", "content": req.get("prompt", "")}]
            user = next((m for m in reversed(msgs) if m.get("role") == "user"), {})
            text = user.get("content") if isinstance(user.get("content"), str) else json.dumps(user.get("content"))
            with lock:
                reply = "5" if "2 plus 3" in (text or "") else next(cycle)
            self._record(self.path, req.get("model"), text or "")
            created = int(time.time())
            if self.path.rstrip("/").endswith("/completions") and "chat" not in self.path:
                return self._json(200, {"id": "cmpl-fake", "object": "text_completion", "created": created, "model": MODEL_ID,
                                        "choices": [{"index": 0, "text": reply, "finish_reason": "stop"}],
                                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
            if req.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for delta, fin in (({"role": "assistant", "content": reply}, None), ({}, "stop")):
                    chunk = {"id": "chatcmpl-fake", "object": "chat.completion.chunk", "created": created, "model": MODEL_ID,
                             "choices": [{"index": 0, "delta": delta, "finish_reason": fin}]}
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                self.wfile.write(b"data: [DONE]\n\n")
                return
            return self._json(200, {"id": "chatcmpl-fake", "object": "chat.completion", "created": created, "model": MODEL_ID,
                                    "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
                                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})

    return H


def selftest() -> int:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(["ready"], None))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}/v1"
    try:
        models = json.loads(urllib.request.urlopen(base + "/models", timeout=5).read())
        req = urllib.request.Request(base + "/chat/completions", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"model": MODEL_ID, "messages": [{"role": "user", "content": "What is 2 plus 3?"}]}).encode())
        body = json.loads(urllib.request.urlopen(req, timeout=5).read())
        a = body["choices"][0]["message"]["content"]
        req2 = urllib.request.Request(base + "/chat/completions", headers={"Content-Type": "application/json"},
                                      data=json.dumps({"model": MODEL_ID, "messages": [{"role": "user", "content": "hello"}]}).encode())
        b = json.loads(urllib.request.urlopen(req2, timeout=5).read())["choices"][0]["message"]["content"]
        ok = models["data"][0]["id"] == MODEL_ID and a == "5" and b == "ready"
        print(json.dumps({"selftest": "PASS" if ok else "FAIL", "port": port, "answers": [a, b]}))
        return 0 if ok else 2
    finally:
        srv.shutdown()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=18999)
    ap.add_argument("--reply", action="append")
    ap.add_argument("--log")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(a.reply or ["ready"], a.log))
    print(json.dumps({"serving": f"http://127.0.0.1:{a.port}/v1", "model": MODEL_ID}), flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
