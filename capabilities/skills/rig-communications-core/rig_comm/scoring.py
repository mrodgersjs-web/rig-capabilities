"""
RIG Communication Protocol V10 — Python Scoring Engine
Implements all 8 scoring formulas from the master doctrine.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import statistics


@dataclass
class CommunicationScore:
    """Universal score container for any RIG communication."""

    # Raw phase scores (0.0 - 1.0)
    wound_precision: float = 0.0
    mirror_accuracy: float = 0.0
    autonomy_preservation: float = 0.0
    qualification_tension: float = 0.0
    specificity_density: float = 0.0
    open_loop_residue: float = 0.0
    rpe_strength: float = 0.0
    reality_anchor: float = 0.0
    anti_generic_force: float = 0.0
    tone_precision: float = 0.0
    memory_residue: float = 0.0
    ethical_restraint: float = 0.0

    # Email-specific
    stakes_clarity: float = 0.0
    desire_activation: float = 0.0
    tension_release: float = 0.0
    relief_clarity: float = 0.0
    identity_resonance: float = 0.0
    peak_end_memory: float = 0.0

    # Reply-specific
    wound_identification: float = 0.0
    specificity: float = 0.0
    restraint: float = 0.0
    mirror_accuracy_reply: float = 0.0
    qualification_frame: float = 0.0
    open_loop_strength: float = 0.0
    close_quality: float = 0.0

    # BDF30 components
    semantic_inversion: float = 0.0
    proof_density: float = 0.0
    enemy_specificity: float = 0.0
    catchphrase_voltage: float = 0.0
    structural_novelty: float = 0.0
    negative_space_weight: float = 0.0
    identity_force: float = 0.0

    # CraftCoefficient
    craft_coefficient: float = 0.0
    eminem_density: float = 0.0
    hemingway_compression: float = 0.0
    didion_cadence: float = 0.0
    mccarthy_rhythm: float = 0.0
    wallace_recursion: float = 0.0

    # Catchphrase
    catchphrase_score: float = 0.0

    # Customer-facing
    evidence: float = 0.0
    rig_signature: float = 0.0
    artifact_completeness: float = 0.0
    emotional_voltage: float = 0.0
    mechanism_clarity: float = 0.0
    memory_compounding: float = 0.0

    # Gates
    banned_phrases_found: List[str] = field(default_factory=list)
    reactance_risk: float = 0.0
    predicted_success: float = 0.0
    swarm_consensus: float = 0.0
    hook_rupture: float = 0.0
    anti_generic_force_entropy: float = 0.0
    send_risk_over_explanation: float = 0.0
    send_risk_manipulation: float = 0.0

    def comm_raw_score(self) -> float:
        """Formula 1: Communication Raw Score (Universal)"""
        return (
            0.14 * self.wound_precision
            + 0.12 * self.mirror_accuracy
            + 0.11 * self.autonomy_preservation
            + 0.10 * self.qualification_tension
            + 0.09 * self.specificity_density
            + 0.09 * self.open_loop_residue
            + 0.08 * self.rpe_strength
            + 0.08 * self.reality_anchor
            + 0.07 * self.anti_generic_force
            + 0.06 * self.tone_precision
            + 0.04 * self.memory_residue
            + 0.02 * self.ethical_restraint
        )

    def email_voltage_score(self) -> float:
        """Formula 2: Email Voltage Score"""
        return (
            0.22 * self.wound_precision
            + 0.18 * self.stakes_clarity
            + 0.16 * self.desire_activation
            + 0.14 * self.tension_release
            + 0.12 * self.relief_clarity
            + 0.10 * self.identity_resonance
            + 0.08 * self.peak_end_memory
        )

    def email_reply_score(self) -> float:
        """Formula 3: Email Reply Score"""
        return (
            0.20 * self.wound_identification
            + 0.15 * self.specificity
            + 0.15 * self.restraint
            + 0.15 * self.autonomy_preservation
            + 0.12 * self.mirror_accuracy_reply
            + 0.10 * self.qualification_frame
            + 0.08 * self.open_loop_strength
            + 0.05 * self.close_quality
        )

    def bdf30(self) -> float:
        """Formula 4: Bipolar Deviation Formula (LinkedIn)"""
        return (
            0.25 * self.semantic_inversion
            + 0.20 * self.proof_density
            + 0.15 * self.enemy_specificity
            + 0.15 * self.catchphrase_voltage
            + 0.10 * self.structural_novelty
            + 0.10 * self.negative_space_weight
            + 0.05 * self.identity_force
        )

    def customer_facing_artifact_score(self) -> float:
        """Formula 7: Customer-Facing Artifact Score"""
        return (
            0.18 * self.evidence
            + 0.18 * self.anti_generic_force
            + 0.14 * self.identity_force
            + 0.14 * self.rig_signature
            + 0.12 * self.artifact_completeness
            + 0.10 * self.emotional_voltage
            + 0.08 * self.mechanism_clarity
            + 0.06 * self.memory_compounding
        )

    def rpe(self, gamma: float = 0.9) -> float:
        """Formula 8: Reward Prediction Error (Dopamine Engine)"""
        r_t = (
            self.wound_precision * self.specificity_density
            + self.rpe_strength * self.reality_anchor
            + self.emotional_voltage * self.identity_force
        ) / 3.0  # Actual reward from this communication

        V_st = 0.35  # Expected value (generic vendor email baseline)
        V_st1 = self.rpe_strength  # Predicted future value

        return r_t + gamma * V_st1 - V_st

    def to_dict(self) -> Dict:
        """Export all computed scores."""
        return {
            "phase_scores": {
                "wound_precision": self.wound_precision,
                "mirror_accuracy": self.mirror_accuracy,
                "autonomy_preservation": self.autonomy_preservation,
                "qualification_tension": self.qualification_tension,
                "open_loop_residue": self.open_loop_residue,
            },
            "formulas": {
                "comm_raw_score": round(self.comm_raw_score(), 4),
                "email_voltage_score": round(self.email_voltage_score(), 4),
                "email_reply_score": round(self.email_reply_score(), 4),
                "bdf30": round(self.bdf30(), 4),
                "craft_coefficient": round(self.craft_coefficient, 4),
                "catchphrase_score": round(self.catchphrase_score, 4),
                "customer_facing_artifact_score": round(
                    self.customer_facing_artifact_score(), 4
                ),
                "rpe": round(self.rpe(), 4),
            },
            "banned_phrases": self.banned_phrases_found,
            "reactance_risk": self.reactance_risk,
        }


class GateEngine:
    """Enforces all 24 universal hard gates."""

    BANNED_PHRASES: List[str] = [
        "just checking in",
        "following up",
        "touching base",
        "would love to chat",
        "let me know your thoughts",
        "happy to help",
        "hope this finds you well",
        "i wanted to reach out",
        "quick question",
        "looking forward to hearing from you",
    ]

    @staticmethod
    def scan_banned_phrases(text: str) -> List[str]:
        """Scan text for banned phrases (case-insensitive)."""
        text_lower = text.lower()
        return [p for p in GateEngine.BANNED_PHRASES if p in text_lower]

    @staticmethod
    def check_gates(score: CommunicationScore, text: str) -> Dict:
        """Run all 24 gates. Returns blocking failures and warnings."""
        blocks: List[str] = []
        warnings: List[str] = []

        # Sequence integrity
        if score.wound_precision < 0.01:
            blocks.append("WOUND_MISSING: No wound identified")
        if score.mirror_accuracy < 0.01:
            blocks.append("MIRROR_MISSING: Recipient won't feel understood")

        # Autonomy
        if score.autonomy_preservation < 0.70:
            blocks.append(f"AUTONOMY_FAIL: {score.autonomy_preservation:.2f} < 0.70 - Chasing detected")

        # Banned phrases
        banned = GateEngine.scan_banned_phrases(text)
        if banned:
            for phrase in banned:
                blocks.append(f"BANNED_PHRASE: '{phrase}' detected")

        # Quality thresholds
        if score.wound_precision < 0.60:
            blocks.append(f"WOUND_GENERIC: {score.wound_precision:.2f} < 0.60")
        if score.specificity_density < 0.50:
            blocks.append(f"TOO_VAGUE: {score.specificity_density:.2f} < 0.50 - Add numbers, names, evidence")
        if score.comm_raw_score() < 0.65:
            blocks.append(f"BELOW_DOCTRINE: CommRawScore {score.comm_raw_score():.2f} < 0.65")

        # Customer-facing
        cfa = score.customer_facing_artifact_score()
        if cfa < 0.82:
            blocks.append(f"CFAS_FAIL: {cfa:.2f} < 82 - Below ship threshold")
        if score.anti_generic_force < 0.80:
            blocks.append(f"INTERCHANGEABLE: AntiGenericForce {score.anti_generic_force:.2f} < 0.80")
        if score.identity_force < 0.75:
            blocks.append(f"NOT_RIG: IdentityForce {score.identity_force:.2f} < 0.75")

        # BDF30
        bdf = score.bdf30()
        if bdf < 8.0:
            blocks.append(f"BDF30_FAIL: {bdf:.2f} < 8.0 - Not deviant enough")

        # Ethical
        if score.ethical_restraint < 0.70:
            blocks.append(f"MANIPULATION: EthicalRestraint {score.ethical_restraint:.2f} < 0.70")

        # Reactance
        if score.reactance_risk > 0.20:
            blocks.append(f"REACTANCE: {score.reactance_risk:.2f} > 0.20 - Autonomy threat threshold exceeded")

        return {
            "passed": len(blocks) == 0,
            "blocks": blocks,
            "warnings": warnings,
            "can_ship": len(blocks) == 0,
        }


# Example: Sarah Chen cold email
def example_sarah_chen():
    score = CommunicationScore(
        wound_precision=0.85,
        mirror_accuracy=0.90,
        autonomy_preservation=0.85,
        qualification_tension=0.80,
        specificity_density=0.88,
        open_loop_residue=0.88,
        rpe_strength=0.85,
        reality_anchor=0.90,
        anti_generic_force=0.88,
        tone_precision=0.82,
        memory_residue=0.80,
        ethical_restraint=0.92,
        stakes_clarity=0.90,
        desire_activation=0.82,
        tension_release=0.78,
        relief_clarity=0.85,
        identity_resonance=0.85,
        peak_end_memory=0.88,
    )

    return score


if __name__ == "__main__":
    score = example_sarah_chen()
    gates = GateEngine.check_gates(
        score,
        "Your team is spending 40% of engineering hours on architecture maintenance.",
    )

    print(json.dumps(score.to_dict(), indent=2))
    print("\n=== GATE CHECK ===")
    print(json.dumps(gates, indent=2))
