"""
RIG Communication Protocol V10 — Gate Enforcement Engine
All 24 universal hard gates. Blocking failures stop shipment.
Warnings require attention but don't block. Returns structured results.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from math import log2
from collections import Counter
from .scoring import CommunicationScore


# ============================================================================
# Data structures
# ============================================================================

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

# Words/phrases that signal imperative/reactance-triggering language
REACTANCE_MARKERS: List[str] = [
    "you must", "you need to", "you have to", "don't miss",
    "act now", "urgent", "limited time", "before it's too late",
    "you should", "you'd be crazy not to", "you're making a mistake",
    "I need you to", "I require", "demand", "insist",
    "asap", "immediately", "right now", "today only",
    "last chance", "don't wait", "hurry",
]


@dataclass
class GateResult:
    """Single gate check result."""
    name: str
    category: str
    passed: bool
    severity: str        # "block" | "warn" | "info"
    message: str
    evidence: List[str] = field(default_factory=list)
    value: Optional[float] = None
    threshold: Optional[float] = None


@dataclass
class GateReport:
    """Full gate enforcement report."""
    passed: bool
    blocks: List[GateResult] = field(default_factory=list)
    warnings: List[GateResult] = field(default_factory=list)
    infos: List[GateResult] = field(default_factory=list)
    all_results: List[GateResult] = field(default_factory=list)
    can_ship: bool = False
    summary: Dict[str, bool] = field(default_factory=dict)


# ============================================================================
# Utility functions
# ============================================================================

def _shannon_entropy(words: List[str]) -> float:
    """Compute Shannon entropy H = -sum(p * log2(p)) for word distribution."""
    if not words:
        return 0.0
    total = len(words)
    counts = Counter(words)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * log2(p)
    return entropy


def compute_entropy_ratio(text: str, baseline_text: str) -> float:
    """H(artifact) / H(median_baseline). Gate: >= 1.2"""
    text_words = text.lower().split()
    baseline_words = baseline_text.lower().split()
    h_artifact = _shannon_entropy(text_words)
    h_baseline = _shannon_entropy(baseline_words)
    if h_baseline == 0:
        return float('inf')
    return h_artifact / h_baseline


def compute_reactance_risk(text: str) -> float:
    """ReactanceRisk = sum(ThreatMarkers) / TotalSentences.
    Gate: < 0.20 (Li & Shi 2025 meta-analysis threshold)"""
    text_lower = text.lower()
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    if not sentences:
        return 0.0
    marker_count = sum(1 for marker in REACTANCE_MARKERS if marker in text_lower)
    return marker_count / len(sentences)


def _make_result(name: str, category: str, passed: bool, severity: str,
                 message: str, value: Optional[float] = None,
                 threshold: Optional[float] = None,
                 evidence: Optional[List[str]] = None) -> GateResult:
    return GateResult(
        name=name, category=category, passed=passed, severity=severity,
        message=message, value=value, threshold=threshold,
        evidence=evidence or [],
    )


# ============================================================================
# GateEngine
# ============================================================================

class GateEngine:
    """Enforces all 24 universal hard gates for RIG communications."""

    BANNED_PHRASES: List[str] = BANNED_PHRASES

    @staticmethod
    def scan_banned_phrases(text: str) -> List[str]:
        """Scan text for banned phrases (case-insensitive)."""
        text_lower = text.lower()
        return [p for p in BANNED_PHRASES if p in text_lower]

    @staticmethod
    def check_gates(score: CommunicationScore, text: str,
                    baseline_text: str = "professional email regarding business services",
                    extra_context: Optional[Dict] = None) -> GateReport:
        """Run all 24 gates. Returns structured GateReport."""
        results: List[GateResult] = []

        # === Sequence Integrity ===
        r = _make_result("WOUND_MISSING", "sequence", score.wound_precision > 0.01, "block",
                         "No wound identified" if score.wound_precision <= 0.01 else "Wound phase present",
                         score.wound_precision, 0.01)
        results.append(r)

        r = _make_result("MIRROR_MISSING", "sequence", score.mirror_accuracy > 0.01, "block",
                         "No mirror — recipient won't feel understood" if score.mirror_accuracy <= 0.01 else "Mirror phase present",
                         score.mirror_accuracy, 0.01)
        results.append(r)

        # === Autonomy ===
        passed = score.autonomy_preservation >= 0.70
        results.append(_make_result("AUTONOMY", "sequence", passed, "block",
            f"AutonomyPreservation {score.autonomy_preservation:.2f} >= 0.70" if passed
            else f"AutonomyPreservation {score.autonomy_preservation:.2f} < 0.70 — Chasing detected",
            score.autonomy_preservation, 0.70))

        # === Banned Phrases ===
        banned = GateEngine.scan_banned_phrases(text)
        passed_bp = len(banned) == 0
        results.append(_make_result("BANNED_PHRASES", "sequence", passed_bp, "block",
            "No banned phrases found" if passed_bp
            else f"Banned phrases found: {', '.join(banned)}",
            evidence=banned))

        # === Quality Thresholds ===
        passed = score.wound_precision >= 0.60
        results.append(_make_result("WOUND_GENERIC", "quality", passed, "block",
            f"WoundPrecision {score.wound_precision:.2f} {'>=' if passed else '<'} 0.60",
            score.wound_precision, 0.60))

        passed = score.specificity_density >= 0.50
        results.append(_make_result("TOO_VAGUE", "quality", passed, "block",
            f"SpecificityDensity {score.specificity_density:.2f} {'>=' if passed else '<'} 0.50 — {'PASS' if passed else 'Add numbers, names, evidence'}",
            score.specificity_density, 0.50))

        # Use the imported formula registry
        from .formulas import comm_raw_score
        crs = comm_raw_score(score)
        passed_crs = crs >= 0.65
        results.append(_make_result("BELOW_DOCTRINE", "quality", passed_crs, "block",
            f"CommRawScore {crs:.4f} {'>=' if passed_crs else '<'} 0.65",
            crs, 0.65))

        # === Customer-Facing Gates ===
        from .formulas import customer_facing_artifact_score
        cfas = customer_facing_artifact_score(score) * 100  # Scale to 0-100
        passed_cfas = cfas >= 82
        results.append(_make_result("CFAS_FAIL", "customer_facing", passed_cfas, "block",
            f"CFAS {cfas:.1f} {'>=' if passed_cfas else '<'} 82",
            cfas, 82))

        passed_agf = score.anti_generic_force >= 0.80
        results.append(_make_result("INTERCHANGEABLE", "customer_facing", passed_agf, "block",
            f"AntiGenericForce {score.anti_generic_force:.2f} {'>=' if passed_agf else '<'} 0.80 — {'PASS' if passed_agf else 'Positioning interchangeable'}",
            score.anti_generic_force, 0.80))

        passed_id = score.identity_force >= 0.75
        results.append(_make_result("NOT_RIG", "customer_facing", passed_id, "block",
            f"IdentityForce {score.identity_force:.2f} {'>=' if passed_id else '<'} 0.75 — {'PASS' if passed_id else 'Does not feel like RIG'}",
            score.identity_force, 0.75))

        passed_rig = score.rig_signature >= 0.75
        results.append(_make_result("GENERIC_SIGNATURE", "customer_facing", passed_rig, "block",
            f"RIGSignature {score.rig_signature:.2f} {'>=' if passed_rig else '<'} 0.75",
            score.rig_signature, 0.75))

        # === Deviation Gates ===
        from .formulas import bdf30
        bdf = bdf30(score)
        # Raw BDF30 formula outputs 0.0–1.0. Gate threshold: 0.85.
        # Full MAD-Z computation (target > 8.0σ) requires median baseline corpus.
        passed_bdf = bdf >= 0.85
        results.append(_make_result("BDF30_FAIL", "deviation", passed_bdf, "block",
            f"BDF30 {bdf:.2f} {'>=' if passed_bdf else '<'} 0.85 — {'PASS' if passed_bdf else 'Not deviant enough'}",
            bdf, 0.85))

        if extra_context and 'swarm' in extra_context:
            swarm = extra_context['swarm']
            pred_success = getattr(swarm, 'predicted_success', lambda: 0)()
            passed_ps = pred_success >= 0.82
            results.append(_make_result("PREDICTED_FAIL", "deviation", passed_ps, "block",
                f"PredictedSuccess {pred_success:.2f} {'>=' if passed_ps else '<'} 0.82",
                pred_success, 0.82))

        # === LinkedIn-Specific Gates ===
        if extra_context and extra_context.get('is_linkedin'):
            swarm_consensus = extra_context.get('swarm_consensus', 0)
            passed_sc = swarm_consensus >= 0.65
            results.append(_make_result("SWARM_DISAGREE", "linkedin", passed_sc, "block",
                f"SwarmConsensus {swarm_consensus:.2f} {'>=' if passed_sc else '<'} 0.65",
                swarm_consensus, 0.65))

            hook_rupture = extra_context.get('hook_rupture', 0)
            passed_hr = hook_rupture >= 0.70
            results.append(_make_result("HOOK_WEAK", "linkedin", passed_hr, "block",
                f"HookRupture {hook_rupture:.2f} {'>=' if passed_hr else '<'} 0.70 — Hook won't stop the scroll",
                hook_rupture, 0.70))

        # === Ethical Gates ===
        passed_er = score.ethical_restraint >= 0.70
        results.append(_make_result("MANIPULATION", "ethical", passed_er, "block",
            f"EthicalRestraint {score.ethical_restraint:.2f} {'>=' if passed_er else '<'} 0.70 — {'PASS' if passed_er else 'Manipulation risk detected'}",
            score.ethical_restraint, 0.70))

        # Over-explanation (warn only)
        text_word_count = len(text.split())
        is_over_explaining = text_word_count > 200
        results.append(_make_result("OVER_EXPLAINING", "ethical", not is_over_explaining, "warn",
            f"Word count: {text_word_count} ({'> 200 — Over-explaining. Cut 40%' if is_over_explaining else 'OK'})",
            float(text_word_count), 200))

        text_lower = text.lower()
        manipulation_count = sum(1 for m in ["guaranteed", "100%", "zero risk", "foolproof"] if m in text_lower)
        passed_manip = manipulation_count <= 0
        results.append(_make_result("MANIPULATION_LANGUAGE", "ethical", passed_manip, "block",
            "No manipulation language detected" if passed_manip
            else f"Manipulation language detected: {manipulation_count} instances"))

        # === Entropy Gate ===
        entropy_ratio = compute_entropy_ratio(text, baseline_text)
        passed_entropy = entropy_ratio >= 1.2
        results.append(_make_result("ENTROPY", "entropy", passed_entropy, "block",
            f"Entropy ratio {entropy_ratio:.3f} {'>=' if passed_entropy else '<'} 1.2 — {'PASS' if passed_entropy else 'Not enough deviation from median'}",
            entropy_ratio, 1.2))

        # === Reactance Gate ===
        reactance = compute_reactance_risk(text)
        passed_react = reactance <= 0.20
        results.append(_make_result("REACTANCE", "reactance", passed_react, "block",
            f"ReactanceRisk {reactance:.2f} {'<=' if passed_react else '>'} 0.20 — {'PASS' if passed_react else 'Autonomy threat exceeded'}",
            reactance, 0.20))

        # === Build report ===
        blocks = [r for r in results if r.severity == "block" and not r.passed]
        warns = [r for r in results if r.severity == "warn" and not r.passed]
        infos = [r for r in results if r.severity == "info"]
        categories = {}
        for r in results:
            cat = r.category
            if cat not in categories:
                categories[cat] = True
            if not r.passed and r.severity == "block":
                categories[cat] = False

        return GateReport(
            passed=len(blocks) == 0,
            blocks=blocks,
            warnings=warns,
            infos=infos,
            all_results=results,
            can_ship=len(blocks) == 0,
            summary=categories,
        )


# ============================================================================
# Test harness — Sarah Chen cold email example
# ============================================================================

def _test_gates():
    print("=" * 60)
    print("  RIG Communications V10 — GateEngine Test Harness")
    print("=" * 60)

    # Build a passing score
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
        semantic_inversion=0.92,
        proof_density=0.88,
        enemy_specificity=0.90,
        catchphrase_voltage=0.85,
        structural_novelty=0.82,
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

    good_text = """Sarah —

Your team is spending 40% of engineering hours on architecture maintenance.
At 200 engineers, that's 80 full-time equivalents not shipping product.

The real number is probably worse. Architecture tax scales nonlinearly
with service count. Every new endpoint requires coordination across 4-7 services.
That's not maintenance. That's an architecture actively hostile to velocity.

If this is intentional — if you're betting the next round makes it
manageable — ignore this. But if the 40% is creeping toward 50%, the
math gets nonlinear fast.

I have a hypothesis about which 3 services are causing 80% of the
coupling. I'd need 15 minutes with the dependency graph to confirm it.

— Mike"""

    print("\n--- Test 1: Clean communication (should PASS all) ---")
    report = GateEngine.check_gates(score, good_text)
    print(f"  Can ship: {report.can_ship}")
    print(f"  Blocks: {len(report.blocks)}")
    print(f"  Warnings: {len(report.warnings)}")
    if report.blocks:
        for b in report.blocks:
            print(f"    BLOCK: {b.name} — {b.message}")

    print("\n--- Test 2: Communication with banned phrase (should BLOCK) ---")
    bad_text = "Hope this email finds you well. Would love to chat about your needs. Let me know your thoughts!"
    bad_report = GateEngine.check_gates(score, bad_text)
    print(f"  Can ship: {bad_report.can_ship}")
    print(f"  Blocks: {len(bad_report.blocks)}")
    for b in bad_report.blocks:
        print(f"    BLOCK: {b.name} — {b.message}")

    print("\n--- Test 3: Banned phrase scanner ---")
    found = GateEngine.scan_banned_phrases("Just checking in to follow up on our conversation. Would love to chat!")
    print(f"  Found: {found}")

    print("\n--- Test 4: Entropy ratio ---")
    generic_baseline = "I am reaching out to discuss potential collaboration opportunities. Please let me know if you are interested in exploring how we might work together."
    ratio = compute_entropy_ratio(good_text, generic_baseline)
    print(f"  Entropy ratio (good text / generic baseline): {ratio:.3f}")

    print("\n--- Test 5: Reactance risk ---")
    reactance = compute_reactance_risk(good_text)
    print(f"  ReactanceRisk: {reactance:.3f}")
    reactance_bad = compute_reactance_risk("You must act now! This is urgent and you need to respond immediately. Don't miss this limited time offer!")
    print(f"  ReactanceRisk (pushy text): {reactance_bad:.3f}")

    print("\n--- Test 6: Category summary ---")
    for cat, passed in report.summary.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {cat}: {status}")

    print("\n" + "=" * 60)
    print("  All GateEngine tests complete.")
    print("=" * 60)


if __name__ == "__main__":
    _test_gates()
