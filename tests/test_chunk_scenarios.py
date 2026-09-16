"""Thirty named scenarios for rig-chunk.

The count is deliberate: 27 mission/classification scenarios plus 3 independent placement
verdict scenarios. These are consumer-shaped cases, not 30 rows of the same parameter.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rig_capabilities import chunk as C

LOCAL = "874b90fa-2c6c-4f73-b3f6-cfeed9e780a9"
REMOTE = "b26a4433-0653-47f1-bdc7-16b44b0f816e"

BASE: dict[str, Any] = {
    "id": "scenario",
    "title": "Process one bounded artifact",
    "prompt": "Return the requested bounded result.",
    "work_class": "summarize",
    "acceptance": "output matches the declared fixture",
    "reversible": True,
    "failure_cost": 0.1,
}

# (name, overrides, expected lane); `refused` means Chunk.from_obj must fail closed.
SCENARIOS: list[tuple[str, dict[str, Any], str]] = [
    # Design / critical authority stays with Mike.
    ("01-architecture-decision-local", {"prompt": "Architect the durable workflow boundary."}, "local"),
    ("02-public-api-surface-local", {"title": "Choose the public API surface"}, "local"),
    ("03-schema-migration-local", {"prompt": "Write the schema migration for the runs table."}, "local"),
    ("04-naming-convention-local", {"prompt": "Pick the naming convention for task ids."}, "local"),
    ("05-approval-budget-local", {"prompt": "Set the approval budget for workers."}, "local"),
    ("06-retry-idempotency-local", {"prompt": "Decide the retry policy and idempotency key."}, "local"),
    ("07-publish-effect-local", {"prompt": "Publish the approved report."}, "local"),
    ("08-delete-effect-local", {"acceptance": "the obsolete production record is deleted"}, "local"),
    ("09-access-token-local", {"prompt": "Read the access token from the credential store."}, "local"),
    ("10-instruction-surface-local", {"prompt": "Update AGENTS.md with this policy."}, "local"),
    ("11-irreversible-local", {"reversible": False}, "local"),
    ("12-failure-cost-boundary-local", {"failure_cost": 0.5}, "local"),
    ("13-no-acceptance-local", {"acceptance": ""}, "local"),
    # Delegable work really fans out; a conservative gate that holds all work is broken too.
    ("14-summary-fanout", {"prompt": "Summarize this log in two sentences."}, "fanout"),
    ("15-naming-color-not-design", {"acceptance": "one word naming a color"}, "fanout"),
    ("16-bounded-code-fanout", {"work_class": "code", "prompt": "Write a pure CSV row counter.", "acceptance": "fixture count equals 12"}, "fanout"),
    ("17-reasoning-fanout", {"work_class": "reason", "prompt": "Compare the two observed latency distributions."}, "fanout"),
    ("18-long-context-fanout", {"work_class": "longctx", "prompt": "Summarize the provided 100k-token transcript."}, "fanout"),
    ("19-triage-fanout", {"work_class": "triage", "prompt": "Classify this error into one of three labels."}, "fanout"),
    ("20-failure-cost-below-boundary", {"failure_cost": 0.49}, "fanout"),
    # Invalid / unjudgeable contracts refuse; they never fall through into the fleet.
    ("21-missing-id-refused", {"id": ""}, "refused"),
    ("22-missing-title-refused", {"title": ""}, "refused"),
    ("23-missing-prompt-refused", {"prompt": ""}, "refused"),
    ("24-out-of-range-cost-refused", {"failure_cost": 1.01}, "refused"),
    ("25-bool-cost-refused", {"failure_cost": True}, "refused"),
    ("26-string-reversible-refused", {"reversible": "yes"}, "refused"),
    ("27-unknown-work-class-refused", {"work_class": "magic"}, "refused"),
]
assert len(SCENARIOS) == 27


@pytest.mark.parametrize(("name", "overrides", "expected"), SCENARIOS, ids=[row[0] for row in SCENARIOS])
def test_mission_scenarios(name: str, overrides: dict[str, Any], expected: str) -> None:
    obj = BASE | overrides
    if expected == "refused":
        with pytest.raises(C.ChunkError):
            C.Chunk.from_obj(obj)
        return

    chunk = C.Chunk.from_obj(obj)
    assert C.classify(chunk).lane == expected

    # Model-quality invariant: 4B is allowed only for explicit low-stakes triage.
    if chunk.work_class == "triage":
        assert C.WORK_CLASS_MODELS["triage"][0] == "qwen3:4b"
    else:
        assert "qwen3:4b" not in C.WORK_CLASS_MODELS[chunk.work_class]


def members(tmp_path: Path) -> Path:
    path = tmp_path / "members.json"
    path.write_text(json.dumps([
        {"nodeUuid": LOCAL, "ipAddress": "127.0.0.1"},
        {"nodeUuid": REMOTE, "ipAddress": "192.168.68.52"},
    ]))
    return path


def dispatch() -> dict[str, Any]:
    return {
        "run_id": "scenario-placement",
        "results": [{
            "chunk_id": "c1",
            "model": "qwen3.8:27b",
            "state": "completed",
            "started_ms": 1_000_000,
            "finished_ms": 1_010_000,
        }],
    }


def history(tmp_path: Path, node: str | None) -> Path:
    path = tmp_path / "workloads-history.json"
    rows = [] if node is None else [{
        "model": "qwen3.8:27b",
        "startedAt": 1_000_001,
        "scheduledOn": node,
        "state": "completed",
    }]
    path.write_text(json.dumps(rows))
    return path


# Scenarios 28–30: all three terminal placement verdicts.
def test_28_remote_ledger_row_proves_offload(tmp_path: Path) -> None:
    report = C.verify(dispatch(), history=history(tmp_path, REMOTE), members=members(tmp_path), settle_s=0)
    assert report["overall"] == "OFFLOAD_PROVEN"


def test_29_local_ledger_row_blocks_false_offload_claim(tmp_path: Path) -> None:
    report = C.verify(dispatch(), history=history(tmp_path, LOCAL), members=members(tmp_path), settle_s=0)
    assert report["overall"] == "OFFLOAD_VIOLATION"


def test_30_missing_ledger_row_is_unproven_never_green(tmp_path: Path) -> None:
    report = C.verify(dispatch(), history=history(tmp_path, None), members=members(tmp_path), settle_s=0)
    assert report["overall"] == "UNPROVEN"
