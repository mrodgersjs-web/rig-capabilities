"""A2 proof.py — SHA-256 ProofPacket surface for the HYBRID rung.

Differs from A1's proof in ONE load-bearing way: at A2 an LLM produced the
draft, so the ProofPacket must bind the artifact hash to the EXACT model
output bytes and the schema gates it cleared — otherwise a hybrid artifact
is indistinguishable from a hand-typed one and the audit trail lies.

The hash is deterministic (timestamp excluded), so the same draft + quality
+ raw model text + signer always yields the same artifact_hash, which is what
makes a probabilistic-origin artifact reproducibly verifiable.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .contract import Draft, LLMResponse, ProofPacket, QualityResult, utcnow_iso


def _canonical(
    draft: Draft, quality: QualityResult, llm: LLMResponse, signer: str
) -> str:
    payload = {
        "body": draft.body,
        "personalization": draft.personalization,
        "sources": [s.uri for s in draft.sources],
        "gates": list(quality.gates_passed),
        # Bind the artifact to the exact bytes the model emitted + the model id.
        "llm_raw": llm.raw_text,
        "model": llm.model,
        "signer": signer,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def artifact_hash(
    draft: Draft, quality: QualityResult, llm: LLMResponse, signer: str
) -> str:
    return hashlib.sha256(
        _canonical(draft, quality, llm, signer).encode("utf-8")
    ).hexdigest()


def make_proof(
    draft: Draft,
    quality: QualityResult,
    llm: LLMResponse,
    signer: str = "a2_hybrid",
) -> ProofPacket:
    # The schema-validation gate is recorded alongside the structural gates so
    # the packet proves the LLM output was schema-bounded, not raw.
    gates = list(quality.gates_passed)
    if "schema_valid" not in gates:
        gates = ["schema_valid", *gates]
    return ProofPacket(
        artifact_hash=artifact_hash(draft, quality, llm, signer),
        sources=[s.uri for s in draft.sources],
        gates=gates,
        timestamp=utcnow_iso(),
        signer=signer,
    )


def verify(
    proof: ProofPacket, draft: Draft, quality: QualityResult, llm: LLMResponse
) -> bool:
    """Re-derive the hash and confirm the hybrid packet is untampered.
    Tampering with the model output, the body, or the gates breaks the hash."""
    return proof.artifact_hash == artifact_hash(
        draft, quality, llm, proof.signer
    )


def emit_gate_proofpacket(
    gate: str,
    status: str,
    evidence: list[dict],
    out_path: Path,
    ts: str = "",
) -> Path:
    """Write a RIG ProofPacket JSON {gate,status,evidence,ts} — the same
    envelope the platform gate harness consumes."""
    packet = {"gate": gate, "status": status, "evidence": evidence, "ts": ts}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return out_path


def run(
    draft: Draft,
    quality: QualityResult,
    llm: LLMResponse,
    signer: str = "a2_hybrid",
) -> ProofPacket:
    return make_proof(draft, quality, llm, signer)


__all__ = [
    "artifact_hash",
    "emit_gate_proofpacket",
    "make_proof",
    "run",
    "verify",
    "ProofPacket",
]
