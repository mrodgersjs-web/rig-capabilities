"""DOCTRINE.md §8 Day 3 — ProofPacket → Action → Result writes.

Every engine score produces a ProofPacket: an immutable record of
  - what was scored (input_hash)
  - what action was taken (the engine's raw_fn + baseline_fn)
  - what result emerged (raw, madz, status, evidence)

ProofPackets are append-only — they chain into the audit substrate from Day 2.
"""
from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
PROOF_DIR = AUDITS_DIR / "proof_packets"


@dataclass(frozen=True)
class ProofPacket:
    """One immutable per-engine score record."""
    packet_id: str
    mission_id: str
    engine_id: int
    engine_name: str
    engine_slug: str
    layer: str
    input_hash: str
    action: str               # 'score' | 'baseline_recal' | 'amplify'
    raw_score: float
    baseline_size: int
    madz: float
    status: str               # PASS | BLOCK | HARD_BLOCK
    evidence: list[dict] = field(default_factory=list)
    timestamp_utc: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def hash(self) -> str:
        body = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(body.encode()).hexdigest()[:24]


def hash_input(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def emit_proof_packet(*,
                       mission_id: str,
                       engine_id: int,
                       engine_name: str,
                       engine_slug: str,
                       layer: str,
                       input_text: str,
                       raw_score: float,
                       baseline_size: int,
                       madz: float,
                       status: str,
                       evidence: list[dict] | None = None,
                       action: str = "score") -> ProofPacket:
    """Build and persist a ProofPacket. Returns the packet."""
    packet = ProofPacket(
        packet_id=f"pp-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
        mission_id=mission_id,
        engine_id=engine_id,
        engine_name=engine_name,
        engine_slug=engine_slug,
        layer=layer,
        input_hash=hash_input(input_text),
        action=action,
        raw_score=raw_score,
        baseline_size=baseline_size,
        madz=madz,
        status=status,
        evidence=evidence or [],
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    out = PROOF_DIR / f"{packet.packet_id}.json"
    out.write_text(json.dumps(packet.to_dict(), indent=2, default=str))
    return packet
