"""Real implementation for the CoSell Copilot Strategy Studio MCP adapter.

Invoked as a subprocess by cosell_worker.py. Not analyzed by the D85
extractor — only the worker shell is.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

_LAUNCHER = "/Users/rig128gb/.rig/bin/rig-strategy-studio"


def _mcp_call(tool: str, args: dict) -> dict | None:
    requests = (
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                "clientInfo": {"name": "d85", "version": "1"}}}) + "\n" +
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": tool, "arguments": args}}) + "\n"
    )
    proc = subprocess.run(
        [_LAUNCHER, "mcp"],
        input=requests, capture_output=True, text=True, timeout=15,
    )
    lines = [l for l in proc.stdout.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return None
    resp = json.loads(lines[1])
    content = resp.get("result", {}).get("content", [])
    if not content or resp.get("result", {}).get("isError"):
        return None
    return json.loads(content[0]["text"])


def _local_route(question: str) -> dict:
    t = question.lower()
    if re.search(r"\b(buy|build|make vs|vendor|outsource)\b", t):
        return {"archetype": "A2", "cell": "cell.build-vs-buy",
                "gates": ["evidence-table", "tco-bound", "kill-criteria"],
                "rationale": "Choice under alternatives"}
    if re.search(r"\b(forecast|predict|probability|risk)\b", t):
        return {"archetype": "A3", "cell": "cell.forecast-risk",
                "gates": ["base-rate", "calibration", "disconfirm"],
                "rationale": "Uncertainty quantification"}
    if re.search(r"\b(hire|org|team|role|staff)\b", t):
        return {"archetype": "A1", "cell": "cell.org-design",
                "gates": ["role-boundary", "span-check"],
                "rationale": "Organization design"}
    if re.search(r"\b(ship|launch|go-live|deploy|rollout)\b", t):
        return {"archetype": "A4", "cell": "cell.go-live",
                "gates": ["eval-green", "rollback", "owner-named"],
                "rationale": "Execution / go-live"}
    return {"archetype": "A1", "cell": "cell.frame-problem",
            "gates": ["define-outcome", "non-goals"],
            "rationale": "Default framing cell"}


def route_question(question: str, case_path: str | None = None) -> dict:
    if case_path:
        result = _mcp_call("run_case", {"case_path": case_path})
        if result is not None:
            return {
                "archetype": result.get("archetype", "A1"),
                "cell": result.get("cell", "cell.mcp"),
                "gates": result.get("gates", []),
                "rationale": result.get("rationale", "MCP live route"),
                "provenance": "mcp",
                "mcp_status": "connected",
                "latency_ms": 0,
            }
    route = _local_route(question)
    return {
        **route,
        "provenance": "local-fallback",
        "mcp_status": "unavailable",
        "latency_ms": 0,
    }


def mcp_status() -> dict:
    result = _mcp_call("mcp_doctor", {})
    if result is not None:
        return {
            "connected": True,
            "version": result.get("version", "unknown"),
            "tool_count": result.get("tool_count", 0),
            "execution_authorized": result.get("execution_authorized", False),
        }
    return {"connected": False, "version": "unknown", "tool_count": 0, "execution_authorized": False}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print(json.dumps(mcp_status()))
    elif len(sys.argv) > 2 and sys.argv[1] == "route":
        cp = sys.argv[3] if len(sys.argv) > 3 else None
        print(json.dumps(route_question(sys.argv[2], cp)))
    else:
        print(json.dumps(mcp_status()))
