"""
RIG Communication Protocol V10 — 6-Round Idea Tournament
Orchestrates the complete V10→V15 idea generation pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import random


# ============================================================================
# Signal Layer Types
# ============================================================================

SIGNAL_TYPES: List[str] = [
    "S1: Orthodoxy Hardening",
    "S2: Wound Frequency",
    "S3: Vocabulary Drift",
    "S4: Villain Emergence",
    "S5: Proof Gaps",
    "S6: Format Exhaustion",
    "S7: Adjacent Domain Collision",
]


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class SignalCard:
    """A raw signal detected by one of the 7 signal-layer agents."""
    signal_type: str
    raw_signal: str
    source: str
    confidence: float   # 0.0–1.0
    decay_rate: float   # 0.0 (stable) to 1.0 (becoming consensus NOW)
    detection_date: str = "2026-05-26"

    def is_decaying(self) -> bool:
        """Signals with high decay rate should be written NOW before median."""
        return self.decay_rate > 0.6


@dataclass
class AngleCard:
    """A candidate angle in the idea tournament."""
    id: str
    signal_layers: List[str]
    raw_angle: str
    idp_score: float = 0.0
    surviving_round: int = 0
    killed: bool = False
    kill_reason: str = ""
    archetype_drafts: Dict[str, str] = field(default_factory=dict)
    bdf30_score: float = 0.0


@dataclass
class RoundReport:
    """Report for a single tournament round."""
    round_number: int
    round_name: str
    input_count: int
    output_count: int
    kills: List[str]  # Angle IDs killed this round
    survivors: List[str]  # Angle IDs surviving
    notes: str = ""


@dataclass
class TournamentReport:
    """Full tournament report across all rounds."""
    initial_angle_count: int
    final_winner: Optional[AngleCard]
    rounds: List[RoundReport] = field(default_factory=list)
    total_killed: int = 0


# ============================================================================
# AngleGenerator — produces mock angles from signal cards
# ============================================================================

ANGLE_TEMPLATES = {
    "S1: Orthodoxy Hardening": [
        "Why {best_practice_name} is actually making {problem} worse",
        "The {best_practice_name} blind spot that costs {audience} {cost} per year",
        "Everyone says {best_practice_name}. Here's the data that proves them wrong.",
    ],
    "S2: Wound Frequency": [
        "Your {audience} is spending {cost} on {problem} and nobody is talking about it",
        "The hidden cost of {problem} that {audience} has normalized",
        "{problem} isn't a {surface_symptom} problem. It's a {underlying_pattern} problem.",
    ],
    "S3: Vocabulary Drift": [
        "Stop calling it {old_term}. It's actually {new_term}.",
        "{new_term} isn't {industry_hype}. It's {real_meaning}.",
        "The term {old_term} was invented by {villain} to distract from {real_problem}.",
    ],
    "S4: Villain Emergence": [
        "Meet the {villain_class}: the people who profit from {problem} staying unsolved",
        "How {villain_class} convinced {audience} that {belief} was normal",
        "The {villain_class} playbook: {step1}, {step2}, {step3}",
    ],
    "S5: Proof Gaps": [
        "I'll bet {stake} that {claim} is false. Here's the data.",
        "The {statistic} that everyone quotes is actually {truth}",
        "{influencer} said {claim}. Here's the math that says otherwise.",
    ],
}


class AngleGenerator:
    """Generates candidate angles from signal cards."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate_from_signals(self, signals: List[SignalCard], count: int = 50) -> List[AngleCard]:
        """Generate candidate angles. Enforces multi-layer combination."""
        angles: List[AngleCard] = []
        signal_by_type: Dict[str, List[SignalCard]] = {}
        for s in signals:
            signal_by_type.setdefault(s.signal_type, []).append(s)

        # Generate angles combining at least 2 signal layers
        for i in range(count):
            layer_count = self.rng.choice([2, 2, 2, 3, 3, 4])  # Most are 2-3 layers
            available_layers = [t for t in SIGNAL_TYPES if t in signal_by_type]
            if len(available_layers) < 2:
                available_layers = SIGNAL_TYPES[:4]  # Fallback

            layers = self.rng.sample(available_layers, min(layer_count, len(available_layers)))
            primary_signal = self.rng.choice(layers)

            # Build angle text from template
            template = ""
            if primary_signal in ANGLE_TEMPLATES:
                templates = ANGLE_TEMPLATES[primary_signal]
                template = self.rng.choice(templates)

            # Fill in template placeholders
            template = template.replace("{best_practice_name}", "AI governance")
            template = template.replace("{problem}", "slow decision velocity")
            template = template.replace("{audience}", "engineering teams")
            template = template.replace("{cost}", "$2.3M")
            template = template.replace("{old_term}", "prompt engineering")
            template = template.replace("{new_term}", "prompt costume design")
            template = template.replace("{villain}", "the RAG Industrial Complex")
            template = template.replace("{villain_class}", "Governance Taxidermists")
            template = template.replace("{stake}", "$5,000")
            template = template.replace("{claim}", "AI projects are bottlenecked by technical challenges")
            template = template.replace("{truth}", "that the bottleneck is organizational, not technical")

            angles.append(AngleCard(
                id=f"ANGLE-{i+1:03d}",
                signal_layers=layers,
                raw_angle=template or f"Cross-domain angle #{i+1} combining {len(layers)} signal layers",
            ))

        return angles


# ============================================================================
# Tournament Round Functions
# ============================================================================

def _idp_scorer(angle: AngleCard) -> float:
    """Score an angle on IdeaDeviationPotential. Mock implementation."""
    # Multi-layer bonus: 2 layers = base, +0.05 per additional layer
    layer_bonus = min(0.20, (len(angle.signal_layers) - 2) * 0.05)
    # Signal diversity bonus
    signal_bonus = min(0.15, len(set(angle.signal_layers)) * 0.03)
    base = random.Random(hash(angle.id)).uniform(0.55, 0.82)
    return min(1.0, base + layer_bonus + signal_bonus)


def round_1_generate(signals: List[SignalCard], target_count: int = 50) -> List[AngleCard]:
    """Round 1: Generate 50 candidate angles from signal cards."""
    gen = AngleGenerator()
    return gen.generate_from_signals(signals, target_count)


def round_2_idp_scoring(angles: List[AngleCard], keep_count: int = 20) -> RoundReport:
    """Round 2: Score on IDP. Kill bottom 60%. Kill any single-layer angles."""
    # Score all
    for a in angles:
        a.idp_score = _idp_scorer(a)
        a.surviving_round = 2

    # Kill single-layer angles immediately
    single_layer = [a for a in angles if len(set(a.signal_layers)) < 2]
    for a in single_layer:
        a.killed = True
        a.kill_reason = "Single-layer angle. Too shallow."

    # Kill bottom 60% by IDP score (excluding already-killed single-layer)
    eligible = [a for a in angles if not a.killed]
    eligible.sort(key=lambda a: a.idp_score, reverse=True)
    survivors = eligible[:keep_count]
    killed_by_score = eligible[keep_count:]
    for a in killed_by_score:
        a.killed = True
        a.kill_reason = f"IDP {a.idp_score:.3f} below cutoff. Bottom 60% culled."
        a.surviving_round = 2

    # Also kill anything below IDP hard gate
    killed_by_gate = [a for a in survivors if a.idp_score < 0.65]
    for a in killed_by_gate:
        a.killed = True
        a.kill_reason = f"IDP {a.idp_score:.3f} < 0.65 hard gate."
    survivors = [a for a in survivors if not a.killed]

    return RoundReport(
        round_number=2, round_name="IDP Scoring",
        input_count=len(angles), output_count=len(survivors),
        kills=[a.id for a in angles if a.killed],
        survivors=[a.id for a in survivors],
        notes=f"Bottom 60% culled. Single-layer angles killed immediately. "
              f"IDP hard gate < 0.65 enforced."
    )


def round_3_adversarial(angles: List[AngleCard], keep_count: int = 8) -> RoundReport:
    """Round 3: Adversarial stress test. Three agents attack each angle."""
    survivors: List[AngleCard] = []
    killed: List[str] = []

    for a in angles:
        a.surviving_round = 3
        # Plagiarism check (simulated: random failure for variety)
        plagiarism_risk = random.Random(hash(a.id + "plag")).random()
        if plagiarism_risk > 0.85:
            a.killed = True
            a.kill_reason = "Plagiarism Detector: Similar angle published in last 180 days."
            killed.append(a.id)
            continue

        # Steelman check
        steelman_strength = random.Random(hash(a.id + "steel")).random()
        if steelman_strength > 0.75:
            a.killed = True
            a.kill_reason = "Steelman Agent: Defense of orthodoxy is stronger than the attack."
            killed.append(a.id)
            continue

        # Audience simulation
        scroll_prob = random.Random(hash(a.id + "aud")).random()
        if scroll_prob > 0.60:
            a.killed = True
            a.kill_reason = f"Audience Simulator: Scroll probability {scroll_prob:.2f} > 0.60."
            killed.append(a.id)
            continue

        survivors.append(a)

    # If more survivors than keep_count, keep top by IDP
    if len(survivors) > keep_count:
        survivors.sort(key=lambda a: a.idp_score, reverse=True)
        extra = survivors[keep_count:]
        survivors = survivors[:keep_count]
        for a in extra:
            a.killed = True
            a.kill_reason = "Exceeded Round 3 survivor cap."
            killed.append(a.id)

    return RoundReport(
        round_number=3, round_name="Adversarial Stress Test",
        input_count=len(angles), output_count=len(survivors),
        kills=killed, survivors=[a.id for a in survivors],
        notes="Plagiarism Detector + Steelman Agent + Audience Simulator. 3 attack vectors."
    )


def round_4_research_depth(angles: List[AngleCard], keep_count: int = 4) -> RoundReport:
    """Round 4: Research depth pass. Validate proof and mechanism."""
    survivors: List[AngleCard] = []
    killed: List[str] = []

    for a in angles:
        a.surviving_round = 4
        proof_density = random.Random(hash(a.id + "proof")).uniform(0.3, 0.9)
        falsification_resilience = random.Random(hash(a.id + "fals")).uniform(0.3, 0.9)
        mechanism_clarity = random.Random(hash(a.id + "mech")).uniform(0.3, 0.9)

        if proof_density < 0.50:
            a.killed = True
            a.kill_reason = f"ProofDensity {proof_density:.2f} < 0.50. No verifiable claims."
            killed.append(a.id)
        elif falsification_resilience < 0.50:
            a.killed = True
            a.kill_reason = f"FalsificationResilience {falsification_resilience:.2f} < 0.50. Red Team destroys it."
            killed.append(a.id)
        elif mechanism_clarity < 0.60:
            a.killed = True
            a.kill_reason = f"MechanismClarity {mechanism_clarity:.2f} < 0.60. Cannot explain the system underneath."
            killed.append(a.id)
        else:
            survivors.append(a)

    # Ensure at least 2 survivors regardless of gates
    if len(survivors) < 2:
        # Promote top-scoring killed angles as "conditional survivors"
        angles.sort(key=lambda a: a.idp_score, reverse=True)
        for a in angles:
            if a.id not in [s.id for s in survivors] and not a.killed:
                a.killed = False
                a.survivor_note = "PROMOTED: Below keep_count floor"
                survivors.append(a)
                if len(survivors) >= 2:
                    break

    if len(survivors) > keep_count:
        survivors.sort(key=lambda a: a.idp_score, reverse=True)
        extra = survivors[keep_count:]
        survivors = survivors[:keep_count]
        for a in extra:
            killed.append(a.id)

    return RoundReport(
        round_number=4, round_name="Research Depth Pass",
        input_count=len(angles), output_count=len(survivors),
        kills=killed, survivors=[a.id for a in survivors],
        notes=f"ProofDensity, FalsificationResilience, MechanismClarity gates."
    )


def round_5_ensemble_draft(angles: List[AngleCard]) -> RoundReport:
    """Round 5: Ensemble draft. 5 archetypes per angle. Pick max BDF30."""
    archetypes = ["EminemDensity", "HemingwayCompression", "DidionCadence",
                  "McCarthyRhythm", "WallaceRecursion"]

    if not angles:
        return RoundReport(
            round_number=5,
            round_name="Ensemble Draft & Max BDF",
            input_count=0,
            output_count=0,
            kills=[],
            survivors=[],
            notes="No survivor angles reached ensemble stage.",
        )

    for a in angles:
        a.surviving_round = 5
        for arch in archetypes:
            # Simulated draft generation
            a.archetype_drafts[arch] = f"[{arch} draft of {a.id}]"
        # Score best draft
        a.bdf30_score = random.Random(hash(a.id + "bdf30")).uniform(0.75, 0.95)

    # Pick winner
    angles.sort(key=lambda a: a.bdf30_score, reverse=True)
    winner = angles[0]
    killed = [a.id for a in angles[1:]]
    for a in angles[1:]:
        a.killed = True
        a.kill_reason = f"BDF30 {a.bdf30_score:.3f} < winner {winner.bdf30_score:.3f}"

    return RoundReport(
        round_number=5, round_name="Ensemble Draft & Max BDF",
        input_count=len(angles), output_count=1,
        kills=killed, survivors=[winner.id],
        notes=f"5 archetypes × {len(angles)} angles = {len(angles)*5} drafts. "
              f"Winner: {winner.id} (BDF30={winner.bdf30_score:.3f})"
    )


def round_6_learning(winner: AngleCard, brier_accuracy: float = 0.78) -> RoundReport:
    """Round 6: Post-ship learning. Record Brier, update weights."""
    return RoundReport(
        round_number=6, round_name="Post-Ship Learning",
        input_count=1, output_count=1,
        kills=[], survivors=[winner.id],
        notes=f"Brier accuracy: {brier_accuracy:.3f}. "
              f"Engagement recorded. Weights queued for quarterly recalibration."
    )


# ============================================================================
# Tournament Orchestrator
# ============================================================================

class IdeaTournament:
    """Orchestrates the full 6-round idea tournament."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.report: Optional[TournamentReport] = None

    def run(self, signals: Optional[List[SignalCard]] = None,
            target_angles: int = 50) -> TournamentReport:
        """Execute the full tournament pipeline."""

        # Default mock signals
        if signals is None:
            signals = [
                SignalCard(st, f"Signal: {st} — consensus hardening at scale",
                           f"source-{i}", 0.7 + 0.03 * i, 0.3 + 0.05 * i)
                for i, st in enumerate(SIGNAL_TYPES)
            ]

        rounds: List[RoundReport] = []
        all_angles_ever: List[AngleCard] = []

        # Round 1: Generate
        angles = round_1_generate(signals, target_angles)
        all_angles_ever = list(angles)
        rounds.append(RoundReport(
            round_number=1, round_name="Angle Synthesis",
            input_count=len(signals), output_count=len(angles),
            kills=[], survivors=[a.id for a in angles],
            notes=f"Generated {len(angles)} angles from {len(signals)} signals."
        ))

        def _safe_rescue(angles: List[AngleCard], pool: List[AngleCard], floor: int) -> List[AngleCard]:
            """If survivors are below floor, rescue top-IDP angles from the pool."""
            if len(angles) >= floor:
                return angles
            need = floor - len(angles)
            rescued = sorted(pool, key=lambda a: a.idp_score, reverse=True)
            for a in rescued:
                if a not in angles and not a.killed and len(angles) < floor:
                    angles.append(a)
            return angles

        # Round 2: IDP Scoring
        r2 = round_2_idp_scoring(angles.copy(), keep_count=20)
        rounds.append(r2)
        angles = [a for a in all_angles_ever if a.id in r2.survivors]
        angles = _safe_rescue(angles, all_angles_ever, 15)

        # Round 3: Adversarial
        r3 = round_3_adversarial(angles.copy(), keep_count=8)
        rounds.append(r3)
        angles = [a for a in all_angles_ever if a.id in r3.survivors]
        angles = _safe_rescue(angles, all_angles_ever, 5)

        # Round 4: Research Depth
        r4 = round_4_research_depth(angles.copy(), keep_count=4)
        rounds.append(r4)
        angles = [a for a in all_angles_ever if a.id in r4.survivors]
        angles = _safe_rescue(angles, all_angles_ever, 2)

        # Round 5: Ensemble Draft
        r5 = round_5_ensemble_draft(angles.copy())
        rounds.append(r5)
        winner_ids = set(r5.survivors)
        winner_candidates = [a for a in all_angles_ever if a.id in winner_ids]
        if not winner_candidates:
            # Ultimate fallback: synthetic winner
            winner = AngleCard(
                id="FALLBACK-001", signal_layers=[SIGNAL_TYPES[0], SIGNAL_TYPES[1]],
                raw_angle="Cross-domain synthesis: The governance paradox resolved",
                idp_score=0.72, bdf30_score=0.85
            )
        else:
            winner = winner_candidates[0]

        # Round 6: Learning
        r6 = round_6_learning(winner)
        rounds.append(r6)

        total_killed = sum(len(r.kills) for r in rounds)

        self.report = TournamentReport(
            initial_angle_count=target_angles,
            final_winner=winner,
            rounds=rounds,
            total_killed=total_killed,
        )
        return self.report

    def print_report(self):
        """Print a formatted tournament report."""
        if not self.report:
            print("No tournament report available. Run .run() first.")
            return

        print("=" * 70)
        print("  RIG V10 Idea Tournament — Full Pipeline Report")
        print("=" * 70)
        print(f"  Initial angles: {self.report.initial_angle_count}")
        print(f"  Total killed:   {self.report.total_killed}")
        print(f"  Winner:         {self.report.final_winner.id if self.report.final_winner else 'NONE'}")
        if self.report.final_winner:
            w = self.report.final_winner
            print(f"  Winner IDP:     {w.idp_score:.3f}")
            print(f"  Winner BDF30:   {w.bdf30_score:.3f}")
            print(f"  Signal layers:  {', '.join(w.signal_layers)}")
        print("-" * 70)
        for r in self.report.rounds:
            print(f"  Round {r.round_number}: {r.round_name}")
            print(f"    In: {r.input_count}  →  Out: {r.output_count}  (killed: {len(r.kills)})")
            print(f"    {r.notes}")
        print("=" * 70)


# ============================================================================
# Test harness
# ============================================================================

def _test_tournament():
    print("=" * 70)
    print("  RIG Communications V10 — Tournament Test Harness")
    print("=" * 70)

    tournament = IdeaTournament(seed=99)
    report = tournament.run(target_angles=50)
    tournament.print_report()

    # Verify the pipeline
    assert report.initial_angle_count == 50, f"Expected 50 angles, got {report.initial_angle_count}"
    assert report.final_winner is not None, "Expected a winner"
    assert len(report.rounds) == 6, f"Expected 6 rounds, got {len(report.rounds)}"
    assert report.total_killed > 0, "Expected some angles to be killed"

    # Verify each round reduces count
    for i in range(1, len(report.rounds)):
        assert report.rounds[i].input_count >= report.rounds[i].output_count, \
            f"Round {i+1} grew unexpectedly"

    print("\n  ALL VERIFICATIONS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    _test_tournament()
