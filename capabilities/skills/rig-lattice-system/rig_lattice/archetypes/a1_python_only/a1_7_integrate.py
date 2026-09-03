"""A1.7 — Integrate (PYTHON_ONLY).

Does: execute the Action, writing an append-only audit row that ties
ProofPacket -> Action -> Result. Approval is CONDITIONAL at A1 (mandatory
only from A3 up): only actions with requires_approval=True route to AionUI
with a 24h timeout. Everything else auto-executes.

This reference uses injectable executors/approvers/audit sinks so the step
is runnable and testable with no external services.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ._types import Action, ProofPacket, utcnow_iso


@dataclass
class ExecutionResult:
    status: str  # 'executed' | 'blocked'
    detail: str


# An approver returns True to approve, False to block. Default approver is
# conservative: it blocks anything flagged for approval (no auto-approve).
Approver = Callable[[ProofPacket, Action], bool]
# An executor performs the side effect and returns a detail string.
Executor = Callable[[Action], str]


def _default_executor(action: Action) -> str:
    # 'noop' executes cleanly; other kinds are simulated deterministically.
    return f"{action.kind}:ok"


def _default_approver(packet: ProofPacket, action: Action) -> bool:
    return False  # conservative: requires an explicit approver to proceed


def _append_audit(path: Path, packet: ProofPacket, action: Action, result: ExecutionResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": utcnow_iso(),
        "proof_hash": packet.artifact_hash,
        "action_kind": action.kind,
        "requires_approval": action.requires_approval,
        "result_status": result.status,
        "result_detail": result.detail,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def integrate(
    packet: ProofPacket,
    action: Action,
    *,
    executor: Optional[Executor] = None,
    approver: Optional[Approver] = None,
    audit_path: Optional[Path] = None,
) -> ExecutionResult:
    executor = executor or _default_executor
    approver = approver or _default_approver

    if action.requires_approval and not approver(packet, action):
        result = ExecutionResult(status="blocked", detail="approval denied or timed out")
    else:
        result = ExecutionResult(status="executed", detail=executor(action))

    if audit_path is not None:
        _append_audit(audit_path, packet, action, result)
    return result


def run(
    packet: ProofPacket,
    action: Action,
    *,
    executor: Optional[Executor] = None,
    approver: Optional[Approver] = None,
    audit_path: Optional[Path] = None,
) -> ExecutionResult:
    return integrate(
        packet, action, executor=executor, approver=approver, audit_path=audit_path
    )
