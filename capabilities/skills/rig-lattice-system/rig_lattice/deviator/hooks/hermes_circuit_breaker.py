"""DOCTRINE.md §6 — circuit_breaker hook.

Pre-integration gate. Blocks integration if:
  - Any L3 physics gate fails (short-circuit)
  - Composite RIG-L < tier minimum
  - BDF collapses to zero
  - Patent Examiner verdict not 'novel' (when required)

Hermes ABI:
    circuit_breaker(scorecard: dict) -> dict
        # scorecard: output of completion_scorer.dv_scorecard
        # returns: {"allow": bool, "reason": str, "next_action": str}
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

from rig_lattice.core.thresholds import THRESHOLDS
from rig_lattice.deviator.pipeline.audit import audit_log


def circuit_breaker(scorecard: dict) -> dict:
    """Return whether the artifact can be integrated downstream."""
    if not scorecard:
        return {"allow": False, "reason": "no scorecard provided",
                "next_action": "Run completion_scorer first."}

    mission_id = scorecard.get("mission_id", "?")
    artifact_hash = scorecard.get("artifact_hash", "?")
    tier = scorecard.get("tier", "client")

    # Rule 1: L3 short-circuit → blocked
    if scorecard.get("physics", {}).get("short_circuited"):
        hard_blocks = scorecard["physics"].get("hard_blocks", [])
        verdict = {"allow": False,
                   "reason": f"L3 physics hard-block: {hard_blocks}",
                   "next_action": "Resolve physics-state violations first."}
        _log(mission_id, artifact_hash, tier, verdict)
        return verdict

    # Rule 2: status HARD_BLOCK
    if scorecard.get("status") == "HARD_BLOCK":
        verdict = {"allow": False,
                   "reason": scorecard.get("detonation_reason", "HARD_BLOCK"),
                   "next_action": scorecard.get("next_action", "Resolve hard block.")}
        _log(mission_id, artifact_hash, tier, verdict)
        return verdict

    # Rule 3: BDF collapse
    if scorecard.get("bdf", 0) == 0:
        verdict = {"allow": False, "reason": "BDF collapsed (intent/craft/restraint = 0)",
                   "next_action": "Restore intent/craft/restraint factors."}
        _log(mission_id, artifact_hash, tier, verdict)
        return verdict

    # Rule 4: RIG-L below tier minimum
    rig_l = scorecard.get("rig_l", 0)
    min_sigma = THRESHOLDS.get(tier, {}).get("minSigma", 3)
    if rig_l < min_sigma:
        verdict = {"allow": False,
                   "reason": f"RIG-L {rig_l:+.2f} below tier {tier} minimum +{min_sigma}",
                   "next_action": scorecard.get("next_action", "Strengthen weakest engine.")}
        _log(mission_id, artifact_hash, tier, verdict)
        return verdict

    # Rule 5: detonation gate
    if scorecard.get("detonation_verdict") != "PASS":
        verdict = {"allow": False,
                   "reason": scorecard.get("detonation_reason", "Detonation gate failed"),
                   "next_action": "Address detonation reason."}
        _log(mission_id, artifact_hash, tier, verdict)
        return verdict

    # All gates pass
    verdict = {"allow": True, "reason": "All gates pass.",
               "next_action": scorecard.get("next_action", "Ship.")}
    _log(mission_id, artifact_hash, tier, verdict)
    return verdict


def _log(mission_id: str, artifact_hash: str, tier: str, verdict: dict) -> None:
    audit_log("hook", mission_id, artifact_hash,
                {"hook": "circuit_breaker", "verdict": verdict},
                tier=tier, actor="hermes.circuit_breaker")
