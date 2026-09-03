"""DOCTRINE.md §4 — Pipeline orchestrator with canonical gate ordering.

  1. Physics State Gates (L3, ±30σ)   → if any BLOCK → SHORT-CIRCUIT
  2. Cognitive Output Gates (L1, ±20σ) → score & gate
  3. Nature Process Gates (L2, ±20σ)   → score & gate
  4. Composite RIG-L                   → headline verdict
  5. Detonation Gate (tier × patent × council)

A single L3 physics failure short-circuits everything below. The orchestrator
returns an OrchestrationResult dataclass with full per-layer scorecards.
"""
from __future__ import annotations
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent

from rig_lattice.core.thresholds import detonation_gate, Verdict, has_banned_phrase, THRESHOLDS
from rig_lattice.core.rig_l import rig_l_composite, rig_l_label
from rig_lattice.core.bdf import bdf
from rig_lattice.core.escalation import escalation_cost
from rig_lattice.deviator.pipeline.audit import audit_log, hash_artifact
from rig_lattice.deviator.pipeline.intent_map import resolve_intent
from rig_lattice.deviator.pipeline.approval_client import ApprovalClient


@dataclass
class LayerResult:
    """Per-layer scorecard."""
    layer: str
    sigmas: dict[str, float] = field(default_factory=dict)  # engine_slug → σ
    statuses: dict[str, str] = field(default_factory=dict)  # engine_slug → PASS|BLOCK|HARD_BLOCK
    hard_blocks: list[str] = field(default_factory=list)    # engine_slugs that hard-blocked
    short_circuited: bool = False                           # True if pipeline aborted at this layer


@dataclass
class OrchestrationResult:
    """Full pipeline output per DOCTRINE.md §4."""
    mission_id: str
    artifact_hash: str
    tier: str
    intent: str

    physics: LayerResult
    cognitive: LayerResult
    nature: LayerResult

    rig_l: float
    rig_l_label: str
    bdf: float
    detonation_verdict: str   # "PASS" | "BLOCK"
    detonation_reason: str
    escalation_cost: int
    status: str               # "PASS" | "BLOCK" | "HARD_BLOCK"
    next_action: str
    timestamp_utc: str
    audit_record_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "artifact_hash": self.artifact_hash,
            "tier": self.tier,
            "intent": self.intent,
            "physics": {
                "sigmas": self.physics.sigmas,
                "statuses": self.physics.statuses,
                "hard_blocks": self.physics.hard_blocks,
                "short_circuited": self.physics.short_circuited,
            },
            "cognitive": {
                "sigmas": self.cognitive.sigmas,
                "statuses": self.cognitive.statuses,
                "hard_blocks": self.cognitive.hard_blocks,
            },
            "nature": {
                "sigmas": self.nature.sigmas,
                "statuses": self.nature.statuses,
                "hard_blocks": self.nature.hard_blocks,
            },
            "rig_l": self.rig_l,
            "rig_l_label": self.rig_l_label,
            "bdf": self.bdf,
            "detonation_verdict": self.detonation_verdict,
            "detonation_reason": self.detonation_reason,
            "escalation_cost": self.escalation_cost,
            "status": self.status,
            "next_action": self.next_action,
            "timestamp_utc": self.timestamp_utc,
            "audit_record_ids": self.audit_record_ids,
        }


# ── Default scorer: wraps the existing auditor (YAML criteria packs) ──────
def _default_scorer(text: str) -> dict:
    """Run the existing v3 auditor and return its dict."""
    from rig_lattice.deviator.auditor import audit_all
    return audit_all(text, llm_enabled=False)


def _split_by_layer(audit_dict: dict) -> tuple[LayerResult, LayerResult, LayerResult]:
    """Split audit_all() output into physics/cognitive/nature LayerResults."""
    phys = LayerResult(layer="physics")
    cog  = LayerResult(layer="cognitive")
    nat  = LayerResult(layer="nature")
    for slug, r in audit_dict.get("engines", {}).items():
        target = {"physics": phys, "cognitive": cog, "nature": nat}.get(r.get("layer"))
        if target is None:
            continue
        target.sigmas[slug] = r["sigma"]
        target.statuses[slug] = r["status"]
        if r["status"] == "HARD_BLOCK":
            target.hard_blocks.append(slug)
    return phys, cog, nat


# ── Orchestrator ──────────────────────────────────────────────────────────
def orchestrate(text: str,
                 tier: str = "client",
                 intent: str | None = None,
                 mission_id: str | None = None,
                 patent_verdict: str = "not_required",
                 actor: str = "system",
                 approval_client: ApprovalClient | None = None) -> OrchestrationResult:
    """Run the full DES pipeline per DOCTRINE.md §4.

    Args:
        text: the artifact to audit.
        tier: target audience tier (internal_note → civilization).
        intent: mission intent keyword (resolves to tier + mode + cost cap).
        mission_id: optional caller-supplied ID. Auto-generated otherwise.
        patent_verdict: Patent Examiner verdict if pre-determined.
        actor: who/what initiated the run (for audit trail).
        approval_client: optional ApprovalClient. Constructs default if None.

    Returns:
        OrchestrationResult with full per-layer scorecards + detonation verdict.
    """
    binding = resolve_intent(intent)
    if intent and not tier:
        tier = binding.tier
    tier = tier or binding.tier

    if approval_client is None:
        approval_client = ApprovalClient()

    mid = mission_id or f"des-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    artifact_hash = hash_artifact(text)
    audit_ids: list[str] = []

    # ── Stage 0: hard-banned-phrase check (DOCTRINE §4.2) ─────────────────
    found, hits = has_banned_phrase(text)
    if found and THRESHOLDS[tier]["minSigma"] >= 3:
        # tier ≥ internal_artifact must not contain banned phrases
        rec_id = audit_log("gate", mid, artifact_hash,
                            {"stage": "banned_phrase", "hits": hits, "verdict": "BLOCK"},
                            tier=tier, actor=actor)
        audit_ids.append(rec_id)
        return _short_circuit_result(
            mid, artifact_hash, tier, binding.intent,
            f"Banned phrases at tier {tier}: {hits}",
            audit_ids,
            phys=LayerResult("physics"),
            cog=LayerResult("cognitive"),
            nat=LayerResult("nature"),
        )

    # ── Run full audit (returns per-engine sigmas + statuses) ────────────
    audit = _default_scorer(text)
    phys, cog, nat = _split_by_layer(audit)

    # ── Stage 1: Physics gates first (DOCTRINE §4 rule 1) ─────────────────
    if phys.hard_blocks:
        phys.short_circuited = True
        rec_id = audit_log("gate", mid, artifact_hash,
                            {"stage": "physics_short_circuit",
                             "hard_blocked_engines": phys.hard_blocks,
                             "sigmas": phys.sigmas},
                            tier=tier, actor=actor)
        audit_ids.append(rec_id)
        return _short_circuit_result(
            mid, artifact_hash, tier, binding.intent,
            f"Physics layer HARD_BLOCK on: {phys.hard_blocks}",
            audit_ids, phys=phys, cog=cog, nat=nat,
        )

    # Log physics PASS
    rec_id = audit_log("gate", mid, artifact_hash,
                        {"stage": "physics_pass", "sigmas": phys.sigmas},
                        tier=tier, actor=actor)
    audit_ids.append(rec_id)

    # ── Stage 2: Cognitive gates ──────────────────────────────────────────
    rec_id = audit_log("gate", mid, artifact_hash,
                        {"stage": "cognitive", "sigmas": cog.sigmas,
                         "hard_blocks": cog.hard_blocks},
                        tier=tier, actor=actor)
    audit_ids.append(rec_id)

    # ── Stage 3: Nature gates ─────────────────────────────────────────────
    rec_id = audit_log("gate", mid, artifact_hash,
                        {"stage": "nature", "sigmas": nat.sigmas,
                         "hard_blocks": nat.hard_blocks},
                        tier=tier, actor=actor)
    audit_ids.append(rec_id)

    # ── Stage 4: Composite RIG-L ──────────────────────────────────────────
    rig_l_val = rig_l_composite(
        layer_sigmas={
            "physics": list(phys.sigmas.values()),
            "cognitive": list(cog.sigmas.values()),
            "nature": list(nat.sigmas.values()),
        },
        hard_blocks=len(cog.hard_blocks) + len(nat.hard_blocks),
    )
    bdf_val = bdf(intent=1.0, madz=rig_l_val, craft=1.0, restraint=1.0)
    cost = escalation_cost(rig_l_val)

    # ── Stage 5: Detonation gate (tier + patent) ─────────────────────────
    # If tier requires Patent Examiner and no verdict given, request one
    t_cfg = THRESHOLDS[tier]
    if patent_verdict == "not_required" and t_cfg.get("requiresPatentExaminer"):
        if rig_l_val >= 5.0:
            verdict = approval_client.request_and_await(
                mission_id=mid,
                artifact_hash=artifact_hash,
                tier=tier,
                kind="patent_examiner",
                summary=f"Tier {tier} requires Patent Examiner review. "
                        f"RIG-L {rig_l_val:+.2f}. Engines flagged: {len(cog.hard_blocks)+len(nat.hard_blocks)} blocks.",
                rig_l=rig_l_val,
                bdf=bdf_val,
            )
            patent_verdict = verdict.verdict
            rec_id = audit_log("review", mid, artifact_hash,
                                {"stage": "patent_examiner",
                                 "verdict": patent_verdict,
                                 "reviewer": verdict.reviewer,
                                 "rationale": verdict.rationale},
                                tier=tier, actor=actor)
            audit_ids.append(rec_id)

    det = detonation_gate(rig_l_val, patent_verdict=patent_verdict, tier=tier)
    final_status = "PASS" if det.status == "PASS" else "BLOCK"

    # Stage 5b: Doctrine Council for tier ≥ doctrine
    if final_status == "PASS" and t_cfg.get("requiresDoctrineCouncil"):
        council = approval_client.request_and_await(
            mission_id=mid,
            artifact_hash=artifact_hash,
            tier=tier,
            kind="doctrine_council",
            summary=f"Tier {tier} requires Doctrine Council review (≤72h). "
                    f"RIG-L {rig_l_val:+.2f}.",
            rig_l=rig_l_val,
            bdf=bdf_val,
        )
        rec_id = audit_log("review", mid, artifact_hash,
                            {"stage": "doctrine_council",
                             "verdict": council.verdict,
                             "reviewer": council.reviewer,
                             "rationale": council.rationale},
                            tier=tier, actor=actor)
        audit_ids.append(rec_id)
        if council.verdict not in ("approved", "novel"):
            final_status = "BLOCK"
            det = Verdict("BLOCK", f"Doctrine Council: {council.verdict}")

    # ── Compose result + final audit record ──────────────────────────────
    next_action = _derive_next_action(audit, phys, cog, nat, final_status, det.reason)
    result = OrchestrationResult(
        mission_id=mid,
        artifact_hash=artifact_hash,
        tier=tier,
        intent=binding.intent,
        physics=phys, cognitive=cog, nature=nat,
        rig_l=rig_l_val,
        rig_l_label=rig_l_label(rig_l_val),
        bdf=round(bdf_val, 2),
        detonation_verdict=det.status,
        detonation_reason=det.reason,
        escalation_cost=cost,
        status=final_status,
        next_action=next_action,
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        audit_record_ids=audit_ids,
    )
    rec_id = audit_log("gate", mid, artifact_hash,
                        {"stage": "final", "result": result.to_dict()},
                        tier=tier, actor=actor)
    result.audit_record_ids.append(rec_id)
    return result


def _short_circuit_result(mid, artifact_hash, tier, intent, reason, audit_ids,
                           phys, cog, nat) -> OrchestrationResult:
    """Build a short-circuited OrchestrationResult for hard-fail cases."""
    return OrchestrationResult(
        mission_id=mid,
        artifact_hash=artifact_hash,
        tier=tier,
        intent=intent,
        physics=phys, cognitive=cog, nature=nat,
        rig_l=-30.0,
        rig_l_label="block",
        bdf=0.0,
        detonation_verdict="BLOCK",
        detonation_reason=reason,
        escalation_cost=escalation_cost(-30),
        status="HARD_BLOCK",
        next_action=f"Fix the short-circuit cause: {reason}",
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        audit_record_ids=audit_ids,
    )


def _derive_next_action(audit, phys, cog, nat, status, reason) -> str:
    """Surface the most leveraged next move for the operator."""
    if status == "HARD_BLOCK":
        return f"Resolve hard-block: {reason}"
    # Find weakest engine across cognitive + nature
    all_failed = []
    for layer in (cog, nat):
        for slug, sigma in layer.sigmas.items():
            if layer.statuses.get(slug) != "PASS":
                all_failed.append((sigma, slug))
    if not all_failed:
        return "Ship."
    all_failed.sort()
    sigma, slug = all_failed[0]
    return f"Strengthen weakest engine: {slug} at {sigma:+.2f}σ"
