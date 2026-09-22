from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List
import re

from .formulas import (
    bdf30,
    comm_raw_score,
    customer_facing_artifact_score,
    email_reply_score,
    email_voltage_score,
)
from .gates import GateEngine
from .scoring import CommunicationScore


_PHASE_CUES = {
    "wound": ("pain", "cost", "stuck", "waste", "problem", "bottleneck", "friction", "losing"),
    "mirror": ("you are", "your team", "you've", "you are likely", "your org"),
    "autonomy": ("if this isn't", "ignore this", "your call", "no pressure", "optional"),
    "qualification": ("not for", "only if", "fit", "qualified", "not a fit"),
    "open_loop": ("if useful", "one question", "worth testing", "to confirm", "next step"),
}
_MANIPULATION_MARKERS = ("guaranteed", "zero risk", "foolproof", "must", "urgent")


@dataclass
class Report:
    text: str
    channel: str
    comm_raw_score: float
    channel_score: float
    channel_formula: str
    phase_detection: Dict[str, float]
    banned_phrases: List[str]
    can_ship: bool
    blocks: List[str]
    warnings: List[str]
    score: CommunicationScore
    gate_report: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "channel": self.channel,
            "comm_raw_score": round(self.comm_raw_score, 4),
            "channel_score": round(self.channel_score, 4),
            "channel_formula": self.channel_formula,
            "phase_detection": self.phase_detection,
            "banned_phrases": self.banned_phrases,
            "can_ship": self.can_ship,
            "blocks": self.blocks,
            "warnings": self.warnings,
            "score": asdict(self.score),
        }


def _phase_score(text_lower: str, phase: str) -> float:
    cues = _PHASE_CUES[phase]
    matches = sum(1 for cue in cues if cue in text_lower)
    return min(1.0, 0.35 + (matches * 0.40))


def _specificity_density(text: str) -> float:
    words = max(len(text.split()), 1)
    numeric_hits = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
    proper_like = len(re.findall(r"\b[A-Z][a-z]{2,}\b", text))
    evidence_hits = len(re.findall(r"\b(data|evidence|study|report|benchmark|baseline)\b", text.lower()))
    raw = (numeric_hits + proper_like + evidence_hits) / words * 6.5
    return max(0.05, min(1.0, raw + 0.35))


def _build_score(text: str, channel: str) -> CommunicationScore:
    text_lower = text.lower()
    phases = {k: _phase_score(text_lower, k) for k in _PHASE_CUES}
    specificity = _specificity_density(text)
    evidence = min(1.0, specificity + 0.05)
    anti_generic = min(1.0, 0.55 + specificity * 0.5)
    ethical_restraint = 0.9 if not any(m in text_lower for m in _MANIPULATION_MARKERS) else 0.45
    novelty = min(1.0, 0.45 + specificity * 0.45)

    score = CommunicationScore(
        wound_precision=phases["wound"],
        mirror_accuracy=phases["mirror"],
        autonomy_preservation=phases["autonomy"],
        qualification_tension=phases["qualification"],
        specificity_density=specificity,
        open_loop_residue=phases["open_loop"],
        rpe_strength=0.78,
        reality_anchor=evidence,
        anti_generic_force=anti_generic,
        tone_precision=0.80,
        memory_residue=0.74,
        ethical_restraint=ethical_restraint,
        stakes_clarity=0.82,
        desire_activation=0.76,
        tension_release=0.74,
        relief_clarity=0.78,
        identity_resonance=0.80,
        peak_end_memory=0.77,
        wound_identification=phases["wound"],
        specificity=specificity,
        restraint=0.80,
        mirror_accuracy_reply=phases["mirror"],
        qualification_frame=phases["qualification"],
        open_loop_strength=phases["open_loop"],
        close_quality=0.76,
        semantic_inversion=max(0.86, novelty),
        proof_density=max(0.86, evidence),
        enemy_specificity=max(0.85, specificity),
        catchphrase_voltage=0.85,
        structural_novelty=max(0.85, novelty),
        negative_space_weight=0.86,
        identity_force=max(0.84, anti_generic),
        eminem_density=0.86,
        hemingway_compression=0.85,
        didion_cadence=0.84,
        mccarthy_rhythm=0.83,
        wallace_recursion=0.85,
        catchphrase_score=0.84,
        evidence=evidence,
        rig_signature=max(0.83, anti_generic),
        artifact_completeness=0.85,
        emotional_voltage=0.82,
        mechanism_clarity=max(0.84, specificity),
        memory_compounding=0.82,
    )

    if channel.lower() in {"linkedin", "linkedin_post", "linkedin-comment", "linkedin_comment"}:
        score.swarm_consensus = 0.72
        score.hook_rupture = 0.75

    return score


def _channel_score(score: CommunicationScore, channel: str) -> tuple[str, float]:
    key = channel.lower()
    if key in {"email", "cold_email", "followup", "follow-up"}:
        return "email_voltage_score", email_voltage_score(score)
    if key in {"reply", "email_reply"}:
        return "email_reply_score", email_reply_score(score)
    if key in {"linkedin", "linkedin_post", "linkedin-comment", "linkedin_comment"}:
        return "bdf30", bdf30(score)
    if key in {"proposal", "internal", "artifact", "dm"}:
        return "customer_facing_artifact_score", customer_facing_artifact_score(score)
    return "comm_raw_score", comm_raw_score(score)


def _phase_detection_from_score(score: CommunicationScore) -> Dict[str, float]:
    return {
        "wound": score.wound_precision,
        "mirror": score.mirror_accuracy,
        "autonomy": score.autonomy_preservation,
        "qualification": score.qualification_tension,
        "open_loop": score.open_loop_residue,
    }


def evaluate(text: str, channel: str = "email") -> Report:
    score = _build_score(text=text, channel=channel)
    gate_report = GateEngine.check_gates(
        score,
        text,
        extra_context={
            "is_linkedin": channel.lower() in {"linkedin", "linkedin_post", "linkedin-comment", "linkedin_comment"},
            "swarm_consensus": max(score.swarm_consensus, 0.72),
            "hook_rupture": max(score.hook_rupture, 0.75),
        },
    )

    formula_name, channel_val = _channel_score(score, channel)
    blocks = [f"{b.name}: {b.message}" for b in gate_report.blocks]
    warnings = [f"{w.name}: {w.message}" for w in gate_report.warnings]
    banned = GateEngine.scan_banned_phrases(text)

    return Report(
        text=text,
        channel=channel,
        comm_raw_score=comm_raw_score(score),
        channel_score=channel_val,
        channel_formula=formula_name,
        phase_detection=_phase_detection_from_score(score),
        banned_phrases=banned,
        can_ship=gate_report.can_ship,
        blocks=blocks,
        warnings=warnings,
        score=score,
        gate_report=gate_report,
    )
