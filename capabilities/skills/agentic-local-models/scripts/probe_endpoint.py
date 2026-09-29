#!/usr/bin/env python3
"""Prove one OpenAI-compatible model route answers with real content (proof level L3).

A 200 is not a completion: a reasoning model can spend the whole max_tokens budget in
reasoning_content and return empty content with finish_reason "length" (lesson AS-07).
This probe lists models, sends one short completion with thinking disabled, and
passes only when content is non-empty AND finish_reason is "stop".

Usage:
  env -u PYTHONHOME -u PYTHONPATH python3 probe_endpoint.py --base-url http://127.0.0.1:8771/v1 \
      [--model ID] [--key-item com.rig.env.NAME] [--expect ready] [--timeout 90]

--key-item names a macOS keychain item; its value is read into this process only and is
never printed, logged, or written. Omit it for keyless local routes.

Exit: 0 ANSWERED_OK; 2 ANSWERED_EMPTY or wrong answer; 3 UNREACHABLE/TIMEOUT; 4 HTTP_ERROR
(401/403 reported as KEYED); 1 usage. Prints one JSON line. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request


def keychain(item: str) -> str:
    r = subprocess.run(["security", "find-generic-password", "-s", item, "-w"],
                       capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        raise SystemExit(json.dumps({"verdict": "KEY_ITEM_MISSING", "key_item": item}))
    return r.stdout.strip()


def call(url: str, payload: dict | None, key: str | None, timeout: float):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8", "ignore") or "{}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model")
    ap.add_argument("--key-item")
    ap.add_argument("--expect", default="ready")
    ap.add_argument("--timeout", type=float, default=90)
    a = ap.parse_args()
    base = a.base_url.rstrip("/")
    key = keychain(a.key_item) if a.key_item else None
    out = {"base_url": base, "key_item": a.key_item}
    t0 = time.time()
    try:
        _, models = call(base + "/models", None, key, min(a.timeout, 10))
        ids = [m.get("id") for m in models.get("data", [])]
        model = a.model or (ids[0] if ids else None)
        out.update({"models": ids[:8], "model": model})
        if not model:
            out["verdict"] = "ANSWERED_EMPTY"
            print(json.dumps(out)); return 2
        payload = {"model": model, "temperature": 0, "max_tokens": 64,
                   "messages": [{"role": "user", "content": f"Reply with the single word: {a.expect}"}],
                   "chat_template_kwargs": {"enable_thinking": False}}
        status, body = call(base + "/chat/completions", payload, key, a.timeout)
    except urllib.error.HTTPError as e:
        out.update({"verdict": "KEYED" if e.code in (401, 403) else "HTTP_ERROR", "http": e.code})
        print(json.dumps(out)); return 4
    except Exception as e:  # noqa: BLE001
        msg = str(getattr(e, "reason", e))[:160]
        out.update({"verdict": "TIMEOUT" if "timed out" in msg.lower() else "UNREACHABLE", "error": msg})
        print(json.dumps(out)); return 3
    choice = (body.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    out.update({"http": status, "finish_reason": choice.get("finish_reason"), "content": content[:80],
                "reasoning_chars": len(msg.get("reasoning_content") or ""),
                "completion_tokens": (body.get("usage") or {}).get("completion_tokens"),
                "seconds": round(time.time() - t0, 2)})
    ok = bool(content) and choice.get("finish_reason") == "stop" and a.expect.lower() in content.lower()
    out["verdict"] = "ANSWERED_OK" if ok else "ANSWERED_EMPTY"
    print(json.dumps(out))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
