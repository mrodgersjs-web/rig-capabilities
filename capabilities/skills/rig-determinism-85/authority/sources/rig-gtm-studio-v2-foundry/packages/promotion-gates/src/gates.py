"""packages/promotion-gates/src/gates.py — Promotion Gates (fail-closed).

Implements the 10 promotion gates from the build card.
Missing required evidence = blocked. All receipts bound to capability ID + hash.

Fail-closed by default: receipts must be verified by the released authority
adapter. Self-authored booleans/dicts/IDs are rejected.
"""
from __future__ import annotations

import time
from typing import Optional


def _bind_receipt(capability: dict, gate: int, status: str, reason: str = "") -> dict:
    """Bind a gate receipt to the capability ID and content hash."""
    return {
        "gate": gate,
        "name": f"gate_{gate}",
        "status": status,
        "reason": reason,
        "capability_id": capability.get("skill_id") or capability.get("lesson_id"),
        "content_hash": capability.get("content_hash"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def gate_1_provenance_complete(capability: dict) -> dict:
    """Gate 1: Provenance complete."""
    source_refs = capability.get("source_refs", [])
    if not source_refs:
        return _bind_receipt(capability, 1, "fail", "No source references")
    for ref in source_refs:
        if not ref.get("video_id") or not ref.get("channel_id"):
            return _bind_receipt(capability, 1, "fail", "Incomplete source ref")
    return _bind_receipt(capability, 1, "pass")


def gate_2_rights_status(capability: dict, rights_verified: bool = False) -> dict:
    """Gate 2: Rights status acceptable (requires explicit verification)."""
    if not rights_verified:
        return _bind_receipt(capability, 2, "blocked", "Rights not verified")
    return _bind_receipt(capability, 2, "pass")


def gate_3_no_contradiction(capability: dict) -> dict:
    """Gate 3: No unresolved critical contradiction."""
    if capability.get("status") == "contradicted":
        return _bind_receipt(capability, 3, "fail", "Capability is contradicted")
    return _bind_receipt(capability, 3, "pass")


def gate_4_golden_suite(capability: dict, golden_results: Optional[list] = None) -> dict:
    """Gate 4: Golden suite passes (bound to capability ID and content hash)."""
    if not golden_results:
        return _bind_receipt(capability, 4, "blocked", "No golden test results provided")

    cap_id = capability.get("skill_id") or capability.get("lesson_id")
    cap_hash = capability.get("content_hash")
    for result in golden_results:
        if result.get("capability_id") != cap_id:
            return _bind_receipt(capability, 4, "fail", "Golden results not bound to this capability")
        if cap_hash and result.get("content_hash") != cap_hash:
            return _bind_receipt(capability, 4, "fail", "Golden results not bound to this content hash")

    failed = [r for r in golden_results if r.get("status") == "fail"]
    if failed:
        return _bind_receipt(capability, 4, "fail", f"{len(failed)} golden tests failed")
    return _bind_receipt(capability, 4, "pass")


def gate_5_adversarial_suite(capability: dict, adversarial_results: Optional[list] = None) -> dict:
    """Gate 5: Adversarial suite passes (bound to capability ID and content hash)."""
    if not adversarial_results:
        return _bind_receipt(capability, 5, "blocked", "No adversarial test results provided")

    cap_id = capability.get("skill_id") or capability.get("lesson_id")
    cap_hash = capability.get("content_hash")
    for result in adversarial_results:
        if result.get("capability_id") != cap_id:
            return _bind_receipt(capability, 5, "fail", "Adversarial results not bound to this capability")
        if cap_hash and result.get("content_hash") != cap_hash:
            return _bind_receipt(capability, 5, "fail", "Adversarial results not bound to this content hash")

    failed = [r for r in adversarial_results if r.get("status") == "fail"]
    if failed:
        return _bind_receipt(capability, 5, "fail", f"{len(failed)} adversarial tests failed")
    return _bind_receipt(capability, 5, "pass")


def gate_6_beats_baseline(capability: dict, baseline_result: Optional[dict] = None) -> dict:
    """Gate 6: Candidate beats or safely extends baseline."""
    if baseline_result is None:
        return _bind_receipt(capability, 6, "blocked", "No baseline provided")

    if capability.get("confidence", 0) >= baseline_result.get("confidence", 0):
        return _bind_receipt(capability, 6, "pass")
    return _bind_receipt(capability, 6, "fail", "Lower confidence than baseline")


def gate_7_gev_regression(capability: dict, gev_results: Optional[list] = None) -> dict:
    """Gate 7: GEV regression shows no unacceptable tail failures."""
    if not gev_results:
        return _bind_receipt(capability, 7, "blocked", "No GEV results provided")

    tail_failures = [r for r in gev_results if r.get("tail_failure")]
    if tail_failures:
        return _bind_receipt(capability, 7, "fail", f"{len(tail_failures)} tail failures")
    return _bind_receipt(capability, 7, "pass")


def gate_8_meta_evaluator(capability: dict, meta_eval: Optional[dict] = None) -> dict:
    """Gate 8: Meta-evaluator approves evaluation quality."""
    if meta_eval is None:
        return _bind_receipt(capability, 8, "blocked", "No meta-evaluation provided")

    if not meta_eval.get("approved"):
        return _bind_receipt(capability, 8, "fail", "Meta-evaluator did not approve")
    return _bind_receipt(capability, 8, "pass")


def gate_9_independent_verifier(capability: dict, verifier_id: Optional[str] = None) -> dict:
    """Gate 9: Independent verifier signs release."""
    if not verifier_id:
        return _bind_receipt(capability, 9, "blocked", "No verifier ID provided")

    # Verifier must be different from compiler
    if verifier_id == capability.get("compiler_version"):
        return _bind_receipt(capability, 9, "fail", "Verifier is not independent")
    return _bind_receipt(capability, 9, "pass")


def gate_10_mike_approval(capability: dict, gate_d_artifact: Optional[dict] = None) -> dict:
    """Gate 10: Mike approves via typed Gate-D artifact."""
    if not gate_d_artifact:
        return _bind_receipt(capability, 10, "blocked", "No Gate-D artifact provided")

    if gate_d_artifact.get("approved_by") != "mike":
        return _bind_receipt(capability, 10, "fail", "Not approved by Mike")
    return _bind_receipt(capability, 10, "pass")


def run_all_gates(capability: dict, **kwargs) -> dict:
    """Run all 10 promotion gates (fail-closed)."""
    gates = [
        gate_1_provenance_complete(capability),
        gate_2_rights_status(capability, kwargs.get("rights_verified")),
        gate_3_no_contradiction(capability),
        gate_4_golden_suite(capability, kwargs.get("golden_results")),
        gate_5_adversarial_suite(capability, kwargs.get("adversarial_results")),
        gate_6_beats_baseline(capability, kwargs.get("baseline_result")),
        gate_7_gev_regression(capability, kwargs.get("gev_results")),
        gate_8_meta_evaluator(capability, kwargs.get("meta_eval")),
        gate_9_independent_verifier(capability, kwargs.get("verifier_id")),
        gate_10_mike_approval(capability, kwargs.get("gate_d_artifact")),
    ]

    # Caller-supplied values cannot authorize promotion. The released authority
    # adapter must replace this block with an unforgeable verified-evidence type.
    authority_block = _bind_receipt(
        capability,
        0,
        "blocked",
        "canonical receipt authority adapter unavailable",
    )
    all_pass = False
    blocked = [authority_block] + [
        gate for gate in gates if gate["status"] == "blocked"
    ]
    failed = [gate for gate in gates if gate["status"] == "fail"]

    return {
        "capability_id": capability.get("skill_id") or capability.get("lesson_id"),
        "gates": gates,
        "all_pass": all_pass,
        "blocked_gates": blocked,
        "failed_gates": failed,
    }
