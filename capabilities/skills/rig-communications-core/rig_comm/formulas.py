"""
RIG Communication Protocol V10 — Formula Registry
All 8 scoring formulas, IDP (IdeaDeviationPotential) with 8 sub-components,
and MemoryCompoundingScore. Each formula function takes a CommunicationScore
and returns a float.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict

from .scoring import CommunicationScore


# ============================================================================
# IDP (IdeaDeviationPotential) — evaluates raw angles before the writing pipeline
# ============================================================================

@dataclass
class IDPScoreInput:
    """Container for all IDP sub-component input values (each 0.0–1.0)."""

    # --- OrthodoxyDestructionDepth ---
    orthodoxy_strength: float = 0.0        # How widely accepted is the belief?
    destruction_quality: float = 0.0       # How thoroughly can you show it's wrong?
    replacement_clarity: float = 0.0       # Is there a clear better alternative?
    audience_impact: float = 0.0           # How many people must update their belief?

    # --- VillainClassSpecificity ---
    named_entity_precision: float = 0.0    # Specific category, not a vague enemy
    profit_transparency: float = 0.0       # Can you show who gains from the problem?
    accountability_surface: float = 0.0    # Can readers ID this villain in their org?
    memetic_contagion: float = 0.0         # Will others adopt this term?

    # --- FalsifiableBetStrength ---
    measurability: float = 0.0             # Can the claim be verified with data?
    stake_magnitude: float = 0.0           # Is the bet large enough to signal conviction?
    timeline_specificity: float = 0.0      # Specific date or window?
    counter_consensus: float = 0.0         # How far from consensus is the prediction?

    # --- SemanticInversionNovelty ---
    prior_term_familiarity: float = 0.0    # How well-known is the original term?
    inversion_distance: float = 0.0        # How far is the new term from old meaning?
    cognitive_stickiness: float = 0.0      # Immediate sense-making + surprise?
    domain_originality: float = 0.0        # Has anyone else used this exact reframe?

    # --- WoundResonance ---
    pain_frequency: float = 0.0            # How many people experience this pain?
    emotional_charge: float = 0.0          # How much does the pain hurt to acknowledge?
    invisibility: float = 0.0              # How normalized/invisible is the wound?
    cost_quantifiability: float = 0.0      # Can cost be $ / hours / market share?

    # --- FormatNovelty ---
    copy_count_inverse: float = 0.0        # Inverse of times used in last 90 days
    structural_originality: float = 0.0    # Genuinely new or just remixed?
    attention_advantage: float = 0.0       # Will the format cause a double-take?

    # --- CatchphrasePotential ---
    phonetic_memorability: float = 0.0     # Alliteration, assonance, rhythm
    compression_density: float = 0.0       # Meaning per syllable maximized
    cross_channel_viability: float = 0.0   # Works in speech as well as text
    visual_logo_potential: float = 0.0     # Could phrase anchor a visual identity?

    # --- ProofAvailability ---
    academic_evidence: float = 0.0         # Peer-reviewed support exists
    industry_data: float = 0.0             # Named companies with published numbers
    primary_research_potential: float = 0.0  # Validatable w/ quick experiment
    anecdotal_strength: float = 0.0        # Compelling stories to humanize data

    # --- MemoryCompoundingScore ---
    doctrine_thread_cont: float = 0.0      # Continuity of doctrine thread
    optimal_spacing: float = 0.0           # Spacing between touchpoints
    catchphrase_recurrence: float = 0.0    # Catchphrase recurrence across artifacts
    villain_consistency: float = 0.0       # Villain name/class consistency


# --- IDP Sub-Component Functions ---

def orthodoxy_destruction_depth(inp: IDPScoreInput) -> float:
    """IDP sub-component 1: How deeply does this idea destroy orthodoxy?

    Weighted sum:
        0.35 * orthodoxy_strength
      + 0.25 * destruction_quality
      + 0.20 * replacement_clarity
      + 0.20 * audience_impact
    """
    return (
        0.35 * inp.orthodoxy_strength
        + 0.25 * inp.destruction_quality
        + 0.20 * inp.replacement_clarity
        + 0.20 * inp.audience_impact
    )


def villain_class_specificity(inp: IDPScoreInput) -> float:
    """IDP sub-component 2: How specific and actionable is this villain?

    Weighted sum:
        0.30 * named_entity_precision
      + 0.25 * profit_transparency
      + 0.25 * accountability_surface
      + 0.20 * memetic_contagion
    """
    return (
        0.30 * inp.named_entity_precision
        + 0.25 * inp.profit_transparency
        + 0.25 * inp.accountability_surface
        + 0.20 * inp.memetic_contagion
    )


def falsifiable_bet_strength(inp: IDPScoreInput) -> float:
    """IDP sub-component 3: How strong and verifiable is the prediction?

    Weighted sum:
        0.35 * measurability
      + 0.25 * stake_magnitude
      + 0.25 * timeline_specificity
      + 0.15 * counter_consensus
    """
    return (
        0.35 * inp.measurability
        + 0.25 * inp.stake_magnitude
        + 0.25 * inp.timeline_specificity
        + 0.15 * inp.counter_consensus
    )


def semantic_inversion_novelty(inp: IDPScoreInput) -> float:
    """IDP sub-component 4: How novel is the semantic inversion?

    Weighted sum:
        0.30 * prior_term_familiarity
      + 0.25 * inversion_distance
      + 0.25 * cognitive_stickiness
      + 0.20 * domain_originality
    """
    return (
        0.30 * inp.prior_term_familiarity
        + 0.25 * inp.inversion_distance
        + 0.25 * inp.cognitive_stickiness
        + 0.20 * inp.domain_originality
    )


def wound_resonance(inp: IDPScoreInput) -> float:
    """IDP sub-component 5: How deeply does the wound resonate?

    Weighted sum:
        0.35 * pain_frequency
      + 0.25 * emotional_charge
      + 0.25 * invisibility
      + 0.15 * cost_quantifiability
    """
    return (
        0.35 * inp.pain_frequency
        + 0.25 * inp.emotional_charge
        + 0.25 * inp.invisibility
        + 0.15 * inp.cost_quantifiability
    )


def format_novelty(inp: IDPScoreInput) -> float:
    """IDP sub-component 6: How novel is the format?

    Weighted sum:
        0.40 * copy_count_inverse
      + 0.30 * structural_originality
      + 0.30 * attention_advantage
    """
    return (
        0.40 * inp.copy_count_inverse
        + 0.30 * inp.structural_originality
        + 0.30 * inp.attention_advantage
    )


def catchphrase_potential(inp: IDPScoreInput) -> float:
    """IDP sub-component 7: What is the catchphrase potential?

    Weighted sum:
        0.35 * phonetic_memorability
      + 0.30 * compression_density
      + 0.25 * cross_channel_viability
      + 0.10 * visual_logo_potential
    """
    return (
        0.35 * inp.phonetic_memorability
        + 0.30 * inp.compression_density
        + 0.25 * inp.cross_channel_viability
        + 0.10 * inp.visual_logo_potential
    )


def proof_availability(inp: IDPScoreInput) -> float:
    """IDP sub-component 8: How available is proof for this claim?

    Weighted sum:
        0.40 * academic_evidence
      + 0.30 * industry_data
      + 0.20 * primary_research_potential
      + 0.10 * anecdotal_strength
    """
    return (
        0.40 * inp.academic_evidence
        + 0.30 * inp.industry_data
        + 0.20 * inp.primary_research_potential
        + 0.10 * inp.anecdotal_strength
    )


def memory_compounding_score(inp: IDPScoreInput) -> float:
    """How well does this artifact compound memory across the campaign?

    Weighted sum:
        0.30 * doctrine_thread_cont
      + 0.25 * optimal_spacing
      + 0.25 * catchphrase_recurrence
      + 0.20 * villain_consistency
    """
    return (
        0.30 * inp.doctrine_thread_cont
        + 0.25 * inp.optimal_spacing
        + 0.25 * inp.catchphrase_recurrence
        + 0.20 * inp.villain_consistency
    )


def compute_idp(inp: IDPScoreInput) -> float:
    """Compute the master IDP (IdeaDeviationPotential) score.

    Weighted sum of all 8 sub-components:
        0.20 * OrthodoxyDestructionDepth
      + 0.15 * VillainClassSpecificity
      + 0.15 * FalsifiableBetStrength
      + 0.12 * SemanticInversionNovelty
      + 0.12 * WoundResonance
      + 0.10 * ProofAvailability
      + 0.08 * FormatNovelty
      + 0.08 * CatchphrasePotential
    """
    return (
        0.20 * orthodoxy_destruction_depth(inp)
        + 0.15 * villain_class_specificity(inp)
        + 0.15 * falsifiable_bet_strength(inp)
        + 0.12 * semantic_inversion_novelty(inp)
        + 0.12 * wound_resonance(inp)
        + 0.10 * proof_availability(inp)
        + 0.08 * format_novelty(inp)
        + 0.08 * catchphrase_potential(inp)
    )


def idp_classify(idp_score: float) -> str:
    """Return the qualitative label for an IDP score.

    0.90–1.00 → Elite
    0.80–0.89 → Exceptional
    0.70–0.79 → Strong
    0.65–0.69 → Marginal
    0.50–0.64 → Insufficient
    0.00–0.49 → Generic
    """
    if idp_score >= 0.90:
        return "Elite — Fast-track to ensemble draft. Ship candidate."
    if idp_score >= 0.80:
        return "Exceptional — Enter tournament at Round 3."
    if idp_score >= 0.70:
        return "Strong — Enter tournament normally."
    if idp_score >= 0.65:
        return "Marginal — Enter tournament at lowest priority."
    if idp_score >= 0.50:
        return "Insufficient — KILL. Will never survive the pipeline."
    return "Generic — KILL. Indistinguishable from median content."


# ============================================================================
# Formula Registry — all 8 scoring formulas
# ============================================================================

def comm_raw_score(score: CommunicationScore) -> float:
    """Formula 1: Communication Raw Score (Universal).

    Weighted sum across all 12 communication dimensions.
    Gate: >= 0.65
    """
    return (
        0.14 * score.wound_precision
        + 0.12 * score.mirror_accuracy
        + 0.11 * score.autonomy_preservation
        + 0.10 * score.qualification_tension
        + 0.09 * score.specificity_density
        + 0.09 * score.open_loop_residue
        + 0.08 * score.rpe_strength
        + 0.08 * score.reality_anchor
        + 0.07 * score.anti_generic_force
        + 0.06 * score.tone_precision
        + 0.04 * score.memory_residue
        + 0.02 * score.ethical_restraint
    )


def email_voltage_score(score: CommunicationScore) -> float:
    """Formula 2: Email Voltage Score.

    Measures the emotional voltage of an outbound email.
    7 dimensions weighted for stakes, desire, tension, and memory.
    """
    return (
        0.22 * score.wound_precision
        + 0.18 * score.stakes_clarity
        + 0.16 * score.desire_activation
        + 0.14 * score.tension_release
        + 0.12 * score.relief_clarity
        + 0.10 * score.identity_resonance
        + 0.08 * score.peak_end_memory
    )


def email_reply_score(score: CommunicationScore) -> float:
    """Formula 3: Email Reply Score.

    Measures reply quality across wound ID, specificity,
    restraint, autonomy, mirror, qualification, open loop, and close.
    """
    return (
        0.20 * score.wound_identification
        + 0.15 * score.specificity
        + 0.15 * score.restraint
        + 0.15 * score.autonomy_preservation
        + 0.12 * score.mirror_accuracy_reply
        + 0.10 * score.qualification_frame
        + 0.08 * score.open_loop_strength
        + 0.05 * score.close_quality
    )


def bdf30(score: CommunicationScore) -> float:
    """Formula 4: Bipolar Deviation Formula (BDF30) — LinkedIn posts.

    Measures how much a post deviates from the LinkedIn median.
    Gate: >= 8.0. Aspiration: +22σ.
    """
    return (
        0.25 * score.semantic_inversion
        + 0.20 * score.proof_density
        + 0.15 * score.enemy_specificity
        + 0.15 * score.catchphrase_voltage
        + 0.10 * score.structural_novelty
        + 0.10 * score.negative_space_weight
        + 0.05 * score.identity_force
    )


def craft_coefficient(score: CommunicationScore) -> float:
    """Formula 5: CraftCoefficient — max across 5 writing archetypes.

    Takes the maximum of:
      EminemDensity, HemingwayCompression, DidionCadence,
      McCarthyRhythm, WallaceRecursion

    Gate: >= 0.85
    """
    return max(
        score.eminem_density,
        score.hemingway_compression,
        score.didion_cadence,
        score.mccarthy_rhythm,
        score.wallace_recursion,
    )


def catchphrase_score(score: CommunicationScore) -> float:
    """Formula 6: CatchphraseScore.

    Returns the stored catchphrase_score field from the CommunicationScore.
    The raw formula (Memorability, SonicEdge, EnemyClarity, etc.) is
    computed upstream and stored in the score container.

    Gate: >= 0.80
    """
    return score.catchphrase_score


def customer_facing_artifact_score(score: CommunicationScore) -> float:
    """Formula 7: Customer-Facing Artifact Score.

    Evaluates evidence, anti-generic force, identity, RIG signature,
    artifact completeness, emotional voltage, mechanism clarity,
    and memory compounding.

    Gate: >= 82 (on 0–100 scale)
    """
    return (
        0.18 * score.evidence
        + 0.18 * score.anti_generic_force
        + 0.14 * score.identity_force
        + 0.14 * score.rig_signature
        + 0.12 * score.artifact_completeness
        + 0.10 * score.emotional_voltage
        + 0.08 * score.mechanism_clarity
        + 0.06 * score.memory_compounding
    )


def rpe(score: CommunicationScore, gamma: float = 0.9) -> float:
    """Formula 8: Reward Prediction Error (Dopamine Engine).

    δₜ = rₜ + γ · V(sₜ₊₁) − V(sₜ)

    rₜ: actual reward delivered by this communication
    γ:  discount factor (default 0.9)
    V(sₜ):   expected value (generic vendor email baseline = 0.35)
    V(sₜ₊₁): predicted future value from the relationship

    Goal: δₜ > 0 — deliver MORE than expected.
    """
    r_t = (
        score.wound_precision * score.specificity_density
        + score.rpe_strength * score.reality_anchor
        + score.emotional_voltage * score.identity_force
    ) / 3.0

    V_st = 0.35   # Generic vendor email baseline
    V_st1 = score.rpe_strength  # Predicted future value

    return r_t + gamma * V_st1 - V_st


# ============================================================================
# Formula Registry
# ============================================================================

#: Mapping of formula name → callable. Each callable takes a CommunicationScore
#: and returns a float.
formula_registry: Dict[str, Callable[..., float]] = {
    "comm_raw_score": comm_raw_score,
    "email_voltage_score": email_voltage_score,
    "email_reply_score": email_reply_score,
    "bdf30": bdf30,
    "craft_coefficient": craft_coefficient,
    "catchphrase_score": catchphrase_score,
    "customer_facing_artifact_score": customer_facing_artifact_score,
    "rpe": rpe,
}

#: IDP sub-component registry (takes IDPScoreInput, returns float).
idp_sub_registry: Dict[str, Callable[[IDPScoreInput], float]] = {
    "orthodoxy_destruction_depth": orthodoxy_destruction_depth,
    "villain_class_specificity": villain_class_specificity,
    "falsifiable_bet_strength": falsifiable_bet_strength,
    "semantic_inversion_novelty": semantic_inversion_novelty,
    "wound_resonance": wound_resonance,
    "format_novelty": format_novelty,
    "catchphrase_potential": catchphrase_potential,
    "proof_availability": proof_availability,
    "memory_compounding_score": memory_compounding_score,
}


# ============================================================================
# Test harness
# ============================================================================

def _test_all_formulas() -> None:
    """Run all formulas against a realistic test score and print results."""
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
        wound_identification=0.88,
        specificity=0.85,
        restraint=0.80,
        mirror_accuracy_reply=0.90,
        qualification_frame=0.82,
        open_loop_strength=0.85,
        close_quality=0.78,
        semantic_inversion=0.90,
        proof_density=0.85,
        enemy_specificity=0.88,
        catchphrase_voltage=0.80,
        structural_novelty=0.78,
        negative_space_weight=0.75,
        identity_force=0.90,
        eminem_density=0.88,
        hemingway_compression=0.85,
        didion_cadence=0.82,
        mccarthy_rhythm=0.80,
        wallace_recursion=0.86,
        catchphrase_score=0.85,
        evidence=0.90,
        rig_signature=0.88,
        artifact_completeness=0.85,
        emotional_voltage=0.82,
        mechanism_clarity=0.80,
        memory_compounding=0.78,
    )

    print("=" * 60)
    print("  RIG Communications V10 — Formula Registry Test Harness")
    print("=" * 60)

    print("\n--- 8 Communication Formulas ---")
    for name, func in formula_registry.items():
        try:
            result = func(score)
            print(f"  {name:40s} → {result:.4f}")
        except Exception as exc:
            print(f"  {name:40s} → ERROR: {exc}")

    print("\n--- RPE with gamma=0.95 ---")
    rpe_095 = rpe(score, gamma=0.95)
    print(f"  rpe(gamma=0.95) → {rpe_095:.4f}")

    print("\n--- IDP Sub-Components ---")
    idp_inp = IDPScoreInput(
        orthodoxy_strength=0.80,
        destruction_quality=0.75,
        replacement_clarity=0.70,
        audience_impact=0.85,
        named_entity_precision=0.90,
        profit_transparency=0.80,
        accountability_surface=0.85,
        memetic_contagion=0.78,
        measurability=0.85,
        stake_magnitude=0.75,
        timeline_specificity=0.70,
        counter_consensus=0.80,
        prior_term_familiarity=0.90,
        inversion_distance=0.85,
        cognitive_stickiness=0.82,
        domain_originality=0.88,
        pain_frequency=0.85,
        emotional_charge=0.80,
        invisibility=0.78,
        cost_quantifiability=0.72,
        copy_count_inverse=0.80,
        structural_originality=0.75,
        attention_advantage=0.82,
        phonetic_memorability=0.85,
        compression_density=0.80,
        cross_channel_viability=0.78,
        visual_logo_potential=0.70,
        academic_evidence=0.75,
        industry_data=0.70,
        primary_research_potential=0.68,
        anecdotal_strength=0.80,
        doctrine_thread_cont=0.85,
        optimal_spacing=0.78,
        catchphrase_recurrence=0.80,
        villain_consistency=0.88,
    )

    for sub_name, sub_func in idp_sub_registry.items():
        try:
            result = sub_func(idp_inp)
            print(f"  {sub_name:40s} → {result:.4f}")
        except Exception as exc:
            print(f"  {sub_name:40s} → ERROR: {exc}")

    print("\n--- Master IDP Score ---")
    idp_val = compute_idp(idp_inp)
    print(f"  IDP = {idp_val:.4f}")
    print(f"  Classification: {idp_classify(idp_val)}")

    print("\n--- MemoryCompoundingScore (standalone) ---")
    mcs = memory_compounding_score(idp_inp)
    print(f"  MemoryCompoundingScore = {mcs:.4f}")

    print("\n" + "=" * 60)
    print("  All tests complete.")
    print("=" * 60)


if __name__ == "__main__":
    _test_all_formulas()
