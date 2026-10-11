#!/usr/bin/env python3
"""Gate-D-as-code demo: the permission gate lives inside the agent loop, not beside it.

Drives the REAL anthropics/claude-agent-sdk-python permission callback
(``can_use_tool``, verified against claude-agent-sdk 0.2.148):

    CanUseTool = Callable[
        [str, dict[str, Any], ToolPermissionContext],
        Awaitable[PermissionResultAllow | PermissionResultDeny],
    ]

No LLM or network is needed for this proof: ``SYNTHETIC_CASES`` replays the
exact tool-use payloads (tool_name, input dict) the SDK would hand the
callback at runtime, and we assert the verdicts.

Decision semantics mirror the two house guard hooks
(~/.claude/hooks/guard-dangerous-commands.sh and guard-secret-write.sh):

  1. Bash commands: deny rm with recursive+force targeting /, ~, ~/, $HOME,
     or system paths; plus sudo rm, mkfs, raw-device writes, forced pushes
     to main/master, git reset --hard ~, git clean -fx, chmod -R 777 /,
     fork bombs.
  2. Any tool input whose content fields (content/new_string/command/text,
     per the hook, generalized to every nested string value) contain an AWS
     access key id (AKIA[0-9A-Z]{16}) or a PEM PRIVATE KEY header — plus the
     hook's other deterministic credential prefixes (GitHub, Slack, Stripe,
     Google).

Every decision is appended as one JSON line to ``gate_d_ledger.jsonl`` next
to this script, with credential matches masked before logging.

Run:  ~/Developer/rig-capabilities/.venvs/claude-sdk/bin/python examples/gate_d_sdk_demo.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    ClaudeAgentOptions,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

# Rule tables live in rig_capabilities.gate_d (stdlib, no SDK).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rig_capabilities.gate_d import CASES, evaluate, sanitize  # noqa: E402

LEDGER = Path(__file__).with_name("gate_d_ledger.jsonl")
SYNTHETIC_CASES = [(tool, payload) for tool, payload, _ in CASES]
EXPECTED = [want for _, _, want in CASES]


def _record(decision, rule_id, tool_name, input_data, tool_use_id):
    line = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": tool_name,
        "tool_use_id": tool_use_id,
        "decision": decision,
        "rule": rule_id,
        "tool_input": sanitize(input_data),
    }
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")


async def gate_d(
    tool_name: str,
    input_data: dict[str, Any],
    context: ToolPermissionContext,
) -> PermissionResultAllow | PermissionResultDeny:
    decision, rule_id = evaluate(tool_name, input_data)
    _record(decision, rule_id, tool_name, input_data, getattr(context, "tool_use_id", ""))
    if decision == "deny":
        return PermissionResultDeny(
            message=f"rig-guard: blocked by Gate-D rule '{rule_id}'. "
            "Refine the call or run it manually under explicit human approval."
        )
    return PermissionResultAllow()


# Payloads shaped exactly as the SDK delivers them at runtime.
SYNTHETIC_CASES: list[tuple[str, dict[str, Any]]] = [
    ("Bash", {"command": "rm -rf / --no-preserve-root"}),
    ("Bash", {"command": "mkdir out && rm -rf $HOME/Documents"}),
    ("Write", {"file_path": "notes/aws.md", "content": "key: AKIAIOSFODNN7EXAMPLE\n"}),
    ("Write", {"file_path": "id.pem", "content": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n"}),
    ("Bash", {"command": "rm -rf ./build && npm run build"}),
    ("Edit", {"file_path": "README.md", "new_string": "Shipped 2026-08-30."}),
]

EXPECTED = ["deny", "deny", "deny", "deny", "allow", "allow"]


async def main() -> int:
    LEDGER.write_text("", encoding="utf-8")  # fresh ledger per demo run
    # Prove the wiring compiles against the real options surface (no CLI spawn).
    options = ClaudeAgentOptions(can_use_tool=gate_d, permission_mode="default")
    assert options.can_use_tool is gate_d

    ctx = ToolPermissionContext()
    failures = 0
    for i, (tool_name, payload) in enumerate(SYNTHETIC_CASES, 1):
        ctx.tool_use_id = f"toolu_synth_{i:02d}"
        result = await gate_d(tool_name, payload, ctx)
        verdict = result.behavior
        ok = verdict == EXPECTED[i - 1]
        failures += not ok
        rule = getattr(result, "message", "") or ""
        rule = rule.split("'")[1] if "'" in rule else "no-rule-match"
        print(f"[{'OK ' if ok else 'FAIL'}] {verdict:5s} {tool_name:6s} rule={rule}")
        assert isinstance(result, (PermissionResultAllow, PermissionResultDeny))
    print(f"ledger: {LEDGER} ({len(LEDGER.read_text().splitlines())} lines)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
