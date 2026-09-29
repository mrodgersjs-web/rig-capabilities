#!/usr/bin/env python3
"""Framework-free hello proof: the plain-code baseline every framework must beat.

Anthropic's guidance is to find the simplest solution first; this is that solution for a
"hello agent": one tool (add), one model turn that must pick it, one assertion.

  --model fake   L2: a deterministic scripted model (no network) picks the tool; asserts 2+3=5
  --model local  L3: the same loop against a local OpenAI-compatible endpoint (thinking disabled);
                 asserts the reply contains 5 and finish_reason is stop

Usage: env -u PYTHONHOME -u PYTHONPATH python3 hello_baseline.py --model fake|local
           [--base-url http://127.0.0.1:8771/v1] [--model-id ID]
Exit 0 assertion held; 2 assertion failed; 3 endpoint unreachable. Prints one JSON line.
Stdlib only; no keys (local routes are keyless).
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request


def add(a: int, b: int) -> int:
    return a + b


def fake_model(question: str) -> dict:
    """Deterministic scripted model: always requests the add tool with the two integers it sees."""
    nums = [int(t) for t in question.replace("?", " ").split() if t.isdigit()]
    return {"tool": "add", "args": {"a": nums[0], "b": nums[1]}}


def local_model(base: str, model_id: str | None, question: str) -> tuple[str, str, str]:
    if not model_id:
        with urllib.request.urlopen(base + "/models", timeout=10) as r:
            model_id = json.loads(r.read())["data"][0]["id"]
    payload = {"model": model_id, "temperature": 0, "max_tokens": 64,
               "chat_template_kwargs": {"enable_thinking": False},
               "messages": [{"role": "system", "content": "Answer with the number only."},
                            {"role": "user", "content": question}]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read())
    ch = body["choices"][0]
    return model_id, (ch["message"].get("content") or "").strip(), ch.get("finish_reason")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["fake", "local"], required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8771/v1")
    ap.add_argument("--model-id")
    a = ap.parse_args()
    q = "What is 2 plus 3?"
    t0 = time.time()
    if a.model == "fake":
        call = fake_model(q)
        result = add(**call["args"]) if call["tool"] == "add" else None
        ok = result == 5
        out = {"level": "L2", "model": "fake:scripted-add", "tool_call": call, "result": result, "assertion": "add(2,3)==5"}
    else:
        try:
            mid, content, finish = local_model(a.base_url.rstrip("/"), a.model_id, q)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"level": "L3", "verdict": "UNREACHABLE", "error": str(e)[:160]}))
            return 3
        ok = "5" in content and finish == "stop"
        out = {"level": "L3", "endpoint": a.base_url, "model": mid, "content": content[:40],
               "finish_reason": finish, "assertion": "reply contains 5 and finish_reason stop"}
    out.update({"verdict": "PASS" if ok else "FAIL", "seconds": round(time.time() - t0, 2)})
    print(json.dumps(out))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
