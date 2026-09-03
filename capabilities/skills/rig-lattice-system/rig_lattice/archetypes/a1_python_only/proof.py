"""A1 proof.py — SHA-256 ProofPacket surface (task-named alias of a1_6_proof).

Re-exports the deterministic proof helpers and adds emit_gate_proofpacket(),
which writes a RIG ProofPacket JSON (gate/status/evidence/ts) for a completed
A1 run — the same envelope the platform gate harness consumes.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .a1_6_proof import artifact_hash, make_proof, verify  # noqa: F401
from .contract import Draft, ProofPacket, QualityResult, utcnow_iso


def emit_gate_proofpacket(
    gate: str,
    status: str,
    evidence: list[dict],
    out_path: Path,
    ts: str = "",
) -> Path:
    """Write a RIG ProofPacket JSON. ts defaults to '' (filled by the
    committing step); pass ts=utcnow_iso() to stamp it now."""
    packet = {"gate": gate, "status": status, "evidence": evidence, "ts": ts}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return out_path


def proof_from_draft(
    draft: Draft, quality: QualityResult, signer: str = "a1_python_only"
) -> ProofPacket:
    return make_proof(draft, quality, signer)


__all__ = [
    "artifact_hash",
    "emit_gate_proofpacket",
    "make_proof",
    "proof_from_draft",
    "utcnow_iso",
    "verify",
    "ProofPacket",
]
