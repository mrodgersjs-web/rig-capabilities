#!/usr/bin/env python3
"""End-to-end smoke test: start the MCP server over stdio and query the catalog.

Spawns `python -m rig_capabilities` against this checkout (RIG_CAP_REPO), then
speaks newline-delimited JSON-RPC 2.0 exactly as a harness would:

  initialize -> notifications/initialized -> tools/list
  -> tools/call capabilities_search {"query": "proof loop"}
  -> tools/call capabilities_get    {"id": "proof-loop"}

Exits non-zero on any protocol error, missing tool, or if the bundled
`proof-loop` skill is not found as a canonical asset. Stdlib only.

Usage: python scripts/smoke_mcp.py [--repo PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REQUIRED_TOOLS = {"capabilities_search", "capabilities_get", "capabilities_list",
                  "capabilities_stats"}


class Client:
    def __init__(self, repo: Path):
        env = {**os.environ, "RIG_CAP_REPO": str(repo), "PYTHONPATH": str(repo)}
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "rig_capabilities"], cwd=str(repo), env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1)
        self.next_id = 0

    def send(self, method: str, params: dict | None = None, notify: bool = False):
        msg: dict = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self.next_id += 1
            msg["id"] = self.next_id
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read()
            raise SystemExit(f"server closed stdout during {method}; stderr:\n{err[-2000:]}")
        resp = json.loads(line)
        if resp.get("id") != msg["id"]:
            raise SystemExit(f"id mismatch on {method}: {resp}")
        if "error" in resp:
            raise SystemExit(f"{method} error: {resp['error']}")
        return resp["result"]

    def call(self, name: str, args: dict) -> dict:
        res = self.send("tools/call", {"name": name, "arguments": args})
        if res.get("isError"):
            raise SystemExit(f"{name} returned isError: {res}")
        return json.loads(res["content"][0]["text"])

    def close(self) -> None:
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    repo = Path(ap.parse_args().repo).resolve()

    c = Client(repo)
    try:
        init = c.send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                     "clientInfo": {"name": "smoke", "version": "1"}})
        print("initialize:", init.get("serverInfo"))
        c.send("notifications/initialized", notify=True)

        tools = {t["name"] for t in c.send("tools/list")["tools"]}
        missing = REQUIRED_TOOLS - tools
        if missing:
            raise SystemExit(f"tools/list missing {sorted(missing)}")
        print(f"tools/list: {len(tools)} tools")

        hits = c.call("capabilities_search", {"query": "proof loop", "limit": 5})
        ids = [r["id"] for r in hits["results"]]
        print("capabilities_search 'proof loop':", ids)
        if "proof-loop" not in ids:
            raise SystemExit("search did not return the bundled proof-loop skill")

        got = c.call("capabilities_get", {"id": "proof-loop"})
        chosen = got["chosen"]
        print("capabilities_get proof-loop:", chosen["kind"], chosen["source"], got["sha"][:12])
        if chosen["source"] != "canonical" or chosen["kind"] != "skill":
            raise SystemExit(f"expected canonical skill, got {chosen}")
        if "proof" not in got["content"].lower():
            raise SystemExit("content does not look like the proof-loop SKILL.md")
    finally:
        c.close()
    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
