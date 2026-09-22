"""v20 proof-packet sealing — Build Card's 12-part packet as one final object.

build_v20_packet assembles the parts the run produced and hashes them.
Parts the run never produced are recorded as MISSING (honest gap), never faked.
"""
from __future__ import annotations
from .models import CommunicationPacket, AudienceModel

PARTS = ("intent", "audience_dossier", "vehicle_choice", "claim_ledger", "message_map",
         "draft_lineage", "evaluator_scores", "risk_classification", "verifier_decision",
         "human_approval", "delivery", "outcome_retrospective")


def build_v20_packet(intent: dict, vehicle: dict, message: str, subject_options: list,
                     audience_model: AudienceModel, claim_ledger: list, risk_flags: list,
                     evaluation_scores: dict, revision_trace: list,
                     verifier_decision: str | None, approval_required: bool,
                     followup_plan: list, delivery: dict | None = None) -> dict:
    present = {
        "intent": bool(intent), "audience_dossier": bool(audience_model.known or audience_model.inferred),
        "vehicle_choice": bool(vehicle), "claim_ledger": True,  # empty ledger is an honest state
        "message_map": bool(message), "draft_lineage": bool(revision_trace),
        "evaluator_scores": bool(evaluation_scores), "risk_classification": True,
        "verifier_decision": verifier_decision in ("pass", "revise", "escalate", "abstain"),
        "human_approval": (not approval_required) or bool(delivery and delivery.get("approval_event")),
        "delivery": bool(delivery), "outcome_retrospective": bool(delivery and delivery.get("outcome")),
    }
    packet = CommunicationPacket(
        message=message, subject_options=subject_options,
        channel_variant=(delivery or {}).get("channel"),
        audience_model=audience_model, claim_ledger=claim_ledger, risk_flags=risk_flags,
        evaluation_scores=evaluation_scores, revision_trace=revision_trace,
        verifier_decision=verifier_decision, approval_required=approval_required,
        followup_plan=followup_plan,
    ).finalize()
    missing = [p for p, ok in present.items() if not ok]
    return {"packet": packet.to_dict(), "parts_present": [p for p, ok in present.items() if ok],
            "parts_missing": missing,
            "complete": not missing,
            "note": "missing parts are gaps to name, not to fake"}


def demo() -> bool:
    from .models import AudienceModel
    r = build_v20_packet({"objective": "ask"}, {"vehicle": "bluf"}, "ship?", ["re: scoping"],
                         AudienceModel(known=[{"field": "role", "provenance": "crm"}]),
                         [], ["low"], {"e_comm": 0.1}, [{"v": 1, "defect": "typo"}],
                         "pass", False, [])
    assert r["packet"]["packet_hash"].startswith("sha256:")
    assert "delivery" in r["parts_missing"] and not r["complete"]
    r2 = build_v20_packet(**{**{}, "intent": {"o": 1}, "vehicle": {"v": 1}, "message": "m",
                             "subject_options": [], "audience_model": AudienceModel(known=[{"f": 1}]),
                             "claim_ledger": [], "risk_flags": [], "evaluation_scores": {"s": 1},
                             "revision_trace": [{"r": 1}], "verifier_decision": "pass",
                             "approval_required": True, "followup_plan": [],
                             "delivery": {"channel": "email", "approval_event": "gd_x",
                                          "outcome": {"won": 1}}})
    assert r2["complete"], r2["parts_missing"]
    return True


if __name__ == "__main__":
    print("seal demo OK" if demo() else "FAIL")
