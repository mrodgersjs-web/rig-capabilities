"""DOCTRINE.md §8 Day 2 — ApprovalClient (AionUI integration stub).

Tier ≥ published requires Patent Examiner verdict.
Tier ≥ doctrine requires Doctrine Council verdict within 72h.

This is the stub for AionUI integration. The real client will:
  - POST approval requests to AionUI's /approvals endpoint
  - Block (or queue async) until human verdict arrives
  - Log every request + verdict to the audit substrate

For now the stub auto-approves with a logged "auto_approved_stub" note so the
pipeline plumbing works end-to-end. Replace with real AionUI HTTP client when
the operator console exposes the endpoint.
"""
from __future__ import annotations
import json
import os
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal
from rig_lattice._paths import AUDITS_DIR

ApprovalKind = Literal["patent_examiner", "doctrine_council"]


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    mission_id: str
    artifact_hash: str
    tier: str
    kind: ApprovalKind
    summary: str          # one-line description for the approver
    rig_l: float
    bdf: float
    timestamp_utc: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ApprovalVerdict:
    request_id: str
    verdict: Literal["novel", "derivative", "approved", "rejected", "queued"]
    reviewer: str
    rationale: str = ""
    timestamp_utc: str = ""


# Queued approvals persist here until verdicts arrive
APPROVAL_QUEUE_DIR = AUDITS_DIR / "approvals"


class ApprovalClient:
    """Stub client. Real implementation routes to a human approval surface.

    Shipping an auto-approving approval gate into five coding agents is a
    Gate-D bypass, so ``RIG_DV_AUTO_APPROVE`` defaults to "0": with no client
    configured this refuses rather than approves. Offline tests that want the
    stub verdict must opt in explicitly by setting the variable to "1".
    """

    def __init__(self, auto_approve: bool | None = None,
                  queue_dir: Path = APPROVAL_QUEUE_DIR):
        # Env opt-in: RIG_DV_AUTO_APPROVE=1 enables the auto-approving stub.
        # Default is OFF — an unconfigured approval gate must refuse.
        if auto_approve is None:
            auto_approve = os.environ.get("RIG_DV_AUTO_APPROVE", "0") == "1"
        self.auto_approve = auto_approve
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def request(self, mission_id: str, artifact_hash: str, tier: str,
                 kind: ApprovalKind, summary: str,
                 rig_l: float, bdf: float) -> ApprovalRequest:
        """Submit an approval request. Persists to queue dir."""
        req = ApprovalRequest(
            request_id=f"appr-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
            mission_id=mission_id,
            artifact_hash=artifact_hash,
            tier=tier,
            kind=kind,
            summary=summary[:200],
            rig_l=rig_l,
            bdf=bdf,
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        (self.queue_dir / f"{req.request_id}.json").write_text(
            json.dumps(req.to_dict(), indent=2, default=str))
        return req

    def await_verdict(self, request: ApprovalRequest,
                       timeout_seconds: float = 0.0) -> ApprovalVerdict:
        """Block until verdict arrives. Stub returns auto-approve.

        Args:
            timeout_seconds: if 0 (default), return immediately with stub verdict.
                              if > 0, poll the queue for a real verdict.
        """
        if self.auto_approve and timeout_seconds == 0:
            return ApprovalVerdict(
                request_id=request.request_id,
                verdict="novel" if request.kind == "patent_examiner" else "approved",
                reviewer="auto_approved_stub",
                rationale="ApprovalClient stub: auto-approved for plumbing test. "
                          "Replace with AionUI integration before production.",
                timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )

        # Real path: poll the queue for a verdict file
        verdict_path = self.queue_dir / f"{request.request_id}-verdict.json"
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if verdict_path.exists():
                d = json.loads(verdict_path.read_text())
                return ApprovalVerdict(**d)
            time.sleep(2)

        # Timed out → return "queued" verdict
        return ApprovalVerdict(
            request_id=request.request_id,
            verdict="queued",
            reviewer="timeout",
            rationale=f"No verdict within {timeout_seconds}s. Request remains queued.",
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def request_and_await(self, mission_id: str, artifact_hash: str,
                            tier: str, kind: ApprovalKind, summary: str,
                            rig_l: float, bdf: float,
                            timeout_seconds: float = 0.0) -> ApprovalVerdict:
        req = self.request(mission_id, artifact_hash, tier, kind, summary, rig_l, bdf)
        return self.await_verdict(req, timeout_seconds)


def request_approval(
    summary: str,
    *,
    mission_id: str = "adhoc",
    artifact_hash: str = "",
    tier: str = "client",
    kind: ApprovalKind = "human_gate",
    rig_l: float = 0.0,
    bdf: float = 0.0,
    timeout_seconds: float = 0.0,
) -> tuple[bool, str]:
    """Ask for approval. Returns ``(approved, reason)``.

    With no approval client configured (``RIG_DV_AUTO_APPROVE`` unset) this
    returns ``(False, "approval_required_no_client")``. It never returns True
    by default: an outward or irreversible action needs a real human verdict,
    and a missing reviewer is a refusal, not a pass.
    """
    if os.environ.get("RIG_DV_AUTO_APPROVE", "0") != "1":
        return (False, "approval_required_no_client")

    client = ApprovalClient()
    verdict = client.request_and_await(
        mission_id=mission_id,
        artifact_hash=artifact_hash,
        tier=tier,
        kind=kind,
        summary=summary,
        rig_l=rig_l,
        bdf=bdf,
        timeout_seconds=timeout_seconds,
    )
    approved = verdict.verdict in ("approved", "novel")
    return (approved, verdict.verdict)
