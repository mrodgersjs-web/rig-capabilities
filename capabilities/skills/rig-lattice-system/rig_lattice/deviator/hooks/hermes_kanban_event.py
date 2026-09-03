"""DOCTRINE.md §6 — kanban_event hook.

Fires when a skill / agent / capability is a promotion candidate. Runs the
full 40-engine doctrine pass and promotes ONLY if:
  - RIG-L ≥ 5.0
  - risk_tier ≠ critical
  - All L3 physics gates pass
  - Adversarial Reviewer verdict ≠ BLOCK

Hermes ABI:
    kanban_event(event: dict) -> dict
        # event: {"event": "skill_promotion_candidate", "candidate_id": "...",
        #          "artifact": "...", "risk_tier": "low|medium|critical", ...}
        # returns: {"promote": bool, "reason": str, "scorecard": dict}
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

from rig_lattice.deviator.pipeline.orchestrator import orchestrate
from rig_lattice.deviator.pipeline.audit import audit_log
from rig_lattice.deviator.hooks.hermes_adversarial_review import adversarial_review


PROMOTION_RIG_L_THRESHOLD = 5.0
CRITICAL_RISK_TIER = "critical"


def kanban_event(event: dict) -> dict:
    """Process a kanban event. Returns promotion verdict."""
    event_type = event.get("event", "")
    if event_type not in ("skill_promotion_candidate", "agent_promotion_candidate",
                            "capability_promotion_candidate"):
        # Not a promotion event — pass-through
        return {"promote": False, "reason": f"not a promotion event ({event_type})",
                "scorecard": None}

    candidate_id = event.get("candidate_id", "unknown")
    artifact = event.get("artifact", "")
    risk_tier = event.get("risk_tier", "medium")

    # Hard rule 1: critical risk → never auto-promote
    if risk_tier == CRITICAL_RISK_TIER:
        result = {"promote": False,
                  "reason": "Critical risk tier requires explicit human approval, not auto-promotion.",
                  "scorecard": None, "candidate_id": candidate_id}
        audit_log("hook", candidate_id, "n/a",
                    {"hook": "kanban_event", "promote": False, "reason": result["reason"]},
                    tier="doctrine", actor="hermes.kanban")
        return result

    # Run full doctrine pass
    scorecard = orchestrate(
        text=artifact,
        tier="doctrine",  # skill promotion = doctrine tier
        intent="skill",
        mission_id=f"kanban-{candidate_id}",
        actor="hermes.kanban_event",
    )

    # Hard rule 2: any L3 physics block → no promotion
    if scorecard.physics.short_circuited:
        result = {"promote": False,
                  "reason": f"L3 physics short-circuit: {scorecard.physics.hard_blocks}",
                  "scorecard": scorecard.to_dict(),
                  "candidate_id": candidate_id}
        audit_log("hook", candidate_id, scorecard.artifact_hash,
                    {"hook": "kanban_event", "promote": False, "reason": result["reason"]},
                    tier="doctrine", actor="hermes.kanban")
        return result

    # Hard rule 3: RIG-L below promotion threshold
    if scorecard.rig_l < PROMOTION_RIG_L_THRESHOLD:
        result = {"promote": False,
                  "reason": f"RIG-L {scorecard.rig_l:+.2f} below promotion threshold +{PROMOTION_RIG_L_THRESHOLD}",
                  "scorecard": scorecard.to_dict(),
                  "candidate_id": candidate_id}
        audit_log("hook", candidate_id, scorecard.artifact_hash,
                    {"hook": "kanban_event", "promote": False, "reason": result["reason"]},
                    tier="doctrine", actor="hermes.kanban")
        return result

    # Adversarial review for promotion candidates
    adv = adversarial_review(scorecard.to_dict(), text=artifact)
    if adv["verdict"] == "BLOCK":
        result = {"promote": False,
                  "reason": f"Adversarial Reviewer BLOCKED: {adv['attacks_landed']} attacks landed",
                  "scorecard": scorecard.to_dict(),
                  "adversarial_review": adv,
                  "candidate_id": candidate_id}
        audit_log("hook", candidate_id, scorecard.artifact_hash,
                    {"hook": "kanban_event", "promote": False, "reason": result["reason"]},
                    tier="doctrine", actor="hermes.kanban")
        return result

    # All gates pass → promote
    result = {"promote": True,
              "reason": f"All gates pass. RIG-L {scorecard.rig_l:+.2f}, "
                        f"BDF {scorecard.bdf:+.2f}, adversarial {adv['verdict']}.",
              "scorecard": scorecard.to_dict(),
              "adversarial_review": adv,
              "candidate_id": candidate_id}
    audit_log("promotion", candidate_id, scorecard.artifact_hash,
                {"hook": "kanban_event", "promote": True,
                 "rig_l": scorecard.rig_l, "bdf": scorecard.bdf,
                 "adv_verdict": adv["verdict"]},
                tier="doctrine", actor="hermes.kanban")
    return result
