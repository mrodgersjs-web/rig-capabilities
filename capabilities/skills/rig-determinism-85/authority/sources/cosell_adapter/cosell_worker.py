"""Worker for the CoSell Copilot Strategy Studio MCP adapter."""

from __future__ import annotations

import json
import subprocess


def execute_impl(action: str, question: str = "", case_path: str | None = None) -> dict:
    if action == "status":
        return _mcp_status()
    return _route(question, case_path)


def _mcp_status() -> dict:
    proc = subprocess.run(
        ["python3", "/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-determinism-85/authority/sources/cosell_adapter/cosell_impl.py", "status"],
        capture_output=True, text=True, timeout=15,
    )
    return json.loads(proc.stdout)


def _route(question: str, case_path: str | None = None) -> dict:
    args = ["python3", "/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-determinism-85/authority/sources/cosell_adapter/cosell_impl.py", "route", question]
    if case_path:
        args.append(case_path)
    proc = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return json.loads(proc.stdout)
