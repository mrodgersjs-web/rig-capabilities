"""DOCTRINE.md §6 — completion_scorer hook.

Fires on every mission packet completion. Runs full 40-engine pass on the
result_packet artifact and attaches the scorecard.

Hermes ABI:
    completion_scorer(mission_packet: dict) -> dict
        # mission_packet: {"mission_id", "artifact", "tier", "intent", ...}
        # returns: enriched mission_packet with `dv_scorecard` attached
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

from rig_lattice.deviator.pipeline.orchestrator import orchestrate
from rig_lattice.deviator.pipeline.audit import audit_log


def completion_scorer(mission_packet: dict) -> dict:
    """Run full pipeline on the mission's artifact; attach scorecard.

    Args:
        mission_packet: dict with required keys:
            - mission_id: str
            - artifact:   str (text) OR str path to file
            - tier:       str (defaults 'client')
            - intent:     str optional (resolves to tier + mode + cost cap)

    Returns:
        The mission_packet with `dv_scorecard` and `dv_status` added.
    """
    mission_id = mission_packet.get("mission_id")
    artifact = mission_packet.get("artifact", "")
    tier = mission_packet.get("tier", "client")
    intent = mission_packet.get("intent")

    if not artifact:
        mission_packet["dv_scorecard"] = None
        mission_packet["dv_status"] = "skipped"
        mission_packet["dv_reason"] = "no artifact in mission_packet"
        return mission_packet

    # Read file if artifact is a path
    text = artifact
    if isinstance(artifact, str) and len(artifact) < 1024 and Path(artifact).exists():
        text = Path(artifact).read_text()

    result = orchestrate(
        text=text,
        tier=tier,
        intent=intent,
        mission_id=mission_id,
        actor="hermes.completion_scorer",
    )

    mission_packet["dv_scorecard"] = result.to_dict()
    mission_packet["dv_status"] = result.status
    mission_packet["dv_rig_l"] = result.rig_l
    mission_packet["dv_next_action"] = result.next_action

    audit_log("hook", result.mission_id, result.artifact_hash,
                {"hook": "completion_scorer", "status": result.status,
                 "rig_l": result.rig_l},
                tier=tier, actor="hermes.completion_scorer")

    return mission_packet
