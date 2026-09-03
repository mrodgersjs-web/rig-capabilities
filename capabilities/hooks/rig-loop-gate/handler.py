"""rig-loop-gate — Hermes gateway hook handler (Loop-Skill Contract v11).  RIG_LOOP_MANAGED

Hermes calls ``handle(event_type, context)`` and discards the return value for
``emit`` events, so this handler cannot block a tool call or inject context.
What it can do honestly: record the event against the active loop run and print
a NOT-DONE line to the gateway log when an agent turn ends with an unmet stage.
Real enforcement in Hermes is CLI-level: ``rig-loop stage <id> pass`` refuses on
red gates regardless of harness.
"""
from __future__ import annotations

import json
import os
import subprocess

RIG_LOOP = os.environ.get("RIG_LOOP_CLI") or os.path.expanduser("~/Developer/rig-capabilities/bin/rig-loop")
EVENT_MAP = {"session:start": "session-start", "agent:start": "prompt", "agent:end": "stop"}


def handle(event_type, context):
    ev = EVENT_MAP.get(event_type)
    if not ev or not os.path.exists(RIG_LOOP):
        return None
    ctx = context or {}
    payload = {
        "harness": "hermes",
        "cwd": os.getcwd(),
        "session_id": ctx.get("session_id", ""),
        "prompt": (ctx.get("message") or "")[:500],
    }
    try:
        r = subprocess.run(["python3", RIG_LOOP, "hook", ev, "--format", "pi"],
                           input=json.dumps(payload), capture_output=True, text=True, timeout=10)
        out = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
    except Exception:  # noqa: BLE001 — never break the gateway
        return None
    msg = out.get("reason") or out.get("inject")
    if msg:
        print(f"[rig-loop-gate] {event_type}: {msg}", flush=True)
    return msg or None
