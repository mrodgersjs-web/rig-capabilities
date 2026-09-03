"""A1.6 — Proof (PYTHON_ONLY).

Does: emit a SHA-256-hashed ProofPacket binding the artifact to its sources
and the gates it passed. Deterministic and reproducible: the same draft +
quality result + signer always yields the same artifact_hash (timestamp is
excluded from the hash so it stays stable).

Doctrine: source-per-claim is free here — sources come from structured
fetches, not generative text.
"""
from __future__ import annotations

import hashlib
import json

from ._types import Draft, ProofPacket, QualityResult, utcnow_iso


def _canonical(draft: Draft, quality: QualityResult, signer: str) -> str:
    payload = {
        "body": draft.body,
        "personalization": draft.personalization,
        "sources": [s.uri for s in draft.sources],
        "gates": list(quality.gates_passed),
        "signer": signer,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def artifact_hash(draft: Draft, quality: QualityResult, signer: str) -> str:
    return hashlib.sha256(_canonical(draft, quality, signer).encode("utf-8")).hexdigest()


def make_proof(
    draft: Draft, quality: QualityResult, signer: str = "a1_python_only"
) -> ProofPacket:
    return ProofPacket(
        artifact_hash=artifact_hash(draft, quality, signer),
        sources=[s.uri for s in draft.sources],
        gates=list(quality.gates_passed),
        timestamp=utcnow_iso(),
        signer=signer,
    )


def verify(proof: ProofPacket, draft: Draft, quality: QualityResult) -> bool:
    """Re-derive the hash and confirm the packet is untampered."""
    return proof.artifact_hash == artifact_hash(draft, quality, proof.signer)


def run(
    draft: Draft, quality: QualityResult, signer: str = "a1_python_only"
) -> ProofPacket:
    return make_proof(draft, quality, signer)
