"""DOCTRINE.md §1.4 + §5.2 + §8 Day 5 — literal physics formulas.

These are textbook physics constants and formulas that underlie Layer 3
Physics engines (31-40). Each formula returns a 0-100 score that feeds the
engine's raw_fn. Physics engines are gates (is_gate=True) — any failure
HARD_BLOCKs the entire pipeline.

References:
  - WKB tunneling:           Griffiths, "Quantum Mechanics" §8.2
  - Bell inequality:         Clauser, Horne, Shimony, Holt (1969) CHSH
  - Heisenberg uncertainty:  ΔE·Δt ≥ ℏ/2
  - Pauli exclusion:         no two fermions in same quantum state
  - Casimir force:           F/A = −π²ℏc/240d⁴ (per unit area)
  - Hawking radiation:       S = k_B·A/4ℓ_P² (Bekenstein-Hawking entropy)
  - Fine-tuning:             viable band / parameter space < 0.10
  - Third law:               S → 0 as T → 0 (Nernst theorem)
  - Light-cone causality:    effects within future light cone of cause
  - Phase transition:        T_critical with hysteresis loop area
"""
from __future__ import annotations
import math
import re
from typing import Iterable

# ── Physical constants (SI) ───────────────────────────────────────────────
H_BAR = 1.054571817e-34       # ℏ (reduced Planck constant), J·s
SPEED_OF_LIGHT = 299_792_458  # c, m/s
K_BOLTZMANN = 1.380649e-23    # k_B, J/K
PLANCK_LENGTH = 1.616255e-35  # ℓ_P, m
PI = math.pi


# ── e31 Quantum Tunneling — WKB approximation ────────────────────────────
# T ≈ exp(-2·∫√(2m(V-E))/ℏ dx)  for E < V_barrier
#
# Anti-orthodoxy: artifact must penetrate an apparent barrier (industry
# default) with non-zero probability via mechanism that wasn't classically
# available.

def wkb_tunneling_probability(barrier_height: float, particle_energy: float,
                                barrier_width: float, mass: float = 1.0) -> float:
    """WKB tunneling probability for a rectangular barrier.

    Returns 0-1 probability. Higher when barrier is thin AND energy is
    closer to barrier top.
    """
    if particle_energy >= barrier_height:
        return 1.0  # over the barrier, not through
    if barrier_width <= 0 or mass <= 0:
        return 0.0
    delta = barrier_height - particle_energy
    if delta <= 0:
        return 1.0
    # Simplified: kappa = sqrt(2m·ΔV)/ℏ, T ~ exp(-2·kappa·width)
    kappa = math.sqrt(2 * mass * delta) / H_BAR
    exponent = -2 * kappa * barrier_width
    # Clamp to prevent overflow
    if exponent < -700:
        return 0.0
    return math.exp(exponent)


def quantum_tunnel_score(text: str) -> float:
    """Score textual evidence of barrier-penetration: explicit refusals of
    standard moves + structural moats that justify the refusal."""
    refusals = re.findall(
        r"\bwe (do not|don.t|will not|won.t|refuse|reject)\b",
        text, re.IGNORECASE,
    )
    moats = re.findall(
        r"\b(CMMC|certified|certifi|patent|moat|structural barrier|"
        r"\d+[- ]year (defense|delivery|track) record|prime contractor)\b",
        text, re.IGNORECASE,
    )
    if not refusals or not moats:
        return 0.0
    return min(100.0, 30 + len(refusals) * 10 + len(moats) * 5)


# ── e32 Pauli Exclusion — no two artifacts in same quantum state ────────
# In physics: ψ(a, b) = −ψ(b, a) for fermions; identical state ⇒ ψ=0
# In doctrine: no two paragraphs occupy the same semantic state.

def pauli_exclusion_score(text: str) -> float:
    """Penalize verbatim duplication of paragraphs."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 80]
    if len(paragraphs) < 2:
        return 100.0  # nothing to collide with
    seen = set()
    collisions = 0
    for p in paragraphs:
        h = p[:80]  # first 80 chars as signature
        if h in seen:
            collisions += 1
        else:
            seen.add(h)
    # 0 collisions → 100; each collision drops 25 points
    return max(0.0, 100.0 - 25 * collisions)


def fermion_state_collision(states: Iterable[str]) -> bool:
    """True if any two states are identical (Pauli violation)."""
    seen = set()
    for s in states:
        if s in seen:
            return True
        seen.add(s)
    return False


# ── e33 Casimir Force — constrained space generates measurable force ────
# F/A = −π²·ℏ·c / (240·d⁴)   per unit area between parallel plates
# In doctrine: tight constraints (short sentences, terse paragraphs)
# generate measurable force.

def casimir_force_per_area(plate_distance: float) -> float:
    """Casimir attractive force per unit area between two parallel plates.

    Returns force per m² (Pa). Always negative (attractive).
    Closer plates → stronger force, scaling as 1/d⁴.
    """
    if plate_distance <= 0:
        return float("-inf")
    return -(PI ** 2 * H_BAR * SPEED_OF_LIGHT) / (240 * plate_distance ** 4)


def casimir_terseness_score(text: str) -> float:
    """Score sentence terseness: shorter avg sentence → tighter constraint
    → stronger Casimir force in the doctrine analog."""
    sentences = re.split(r"[.!?]+\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if not sentences:
        return 0.0
    avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
    # 0-22 words = optimal; 22+ degrades
    if avg_words <= 22:
        return 100.0
    if avg_words >= 50:
        return 0.0
    return max(0.0, 100.0 - (avg_words - 22) * 3.5)


# ── e34 Fine-Tuning Ratio — viable band / parameter space ───────────────
# Cosmological fine-tuning: ratio of life-permitting parameter range
# to total parameter space. Must be < 10% for a "fine-tuned" claim.
# In doctrine: every parameter must be specific, not generic.

FINE_TUNING_THRESHOLD = 0.10

def fine_tuning_ratio(viable_band: float, parameter_space: float) -> float:
    """Ratio of viable parameter range to total space. < 0.10 = fine-tuned."""
    if parameter_space <= 0:
        return 1.0
    return min(1.0, abs(viable_band / parameter_space))


def fine_structure_score(text: str) -> float:
    """Score specificity: count of named entities + dated dollar amounts
    vs total word count. Lower density → less fine-tuned."""
    specifics = re.findall(
        r"(\$\d+[\d,.]*[KMB]?|\d{4}\s*(Q[1-4]|year)|"
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b|"
        r"\d+(?:\.\d+)?\s*%)",
        text,
    )
    words = max(len(text.split()), 1)
    density = len(specifics) / words
    # 0.05 density = 100; 0.01 = 20; 0.005 = 10
    return round(min(100.0, density * 2000), 2)


# ── e35 Hawking Radiation — information must leak through opaque boundary ─
# Bekenstein-Hawking entropy: S = k_B · A / (4 · ℓ_P²)
# Surface area, not volume, sets entropy bound.
# In doctrine: artifact must expose internal mechanisms through its
# surface (text). InternalVolume > 10·SurfaceArea → black box.

HAWKING_VOLUME_RATIO_MAX = 10.0          # InternalVolume / SurfaceArea max
HAWKING_ENTROPY_THRESHOLD = 0.4          # ObservedEntropy / ExpectedEntropy min

def bekenstein_hawking_entropy(area_m2: float) -> float:
    """Bekenstein-Hawking entropy in J/K for a black hole of given surface area."""
    if area_m2 <= 0:
        return 0.0
    return K_BOLTZMANN * area_m2 / (4 * PLANCK_LENGTH ** 2)


def hawking_horizon_score(text: str) -> float:
    """Score proof-of-access density: 'we have / own / built / deliver'
    statements per 1000 words. Internal volume must leak through surface."""
    proof_phrases = re.findall(
        r"\b(we (have|own|built|deliver|ship|operate|run|control|hold))\b",
        text, re.IGNORECASE,
    )
    if len(proof_phrases) >= 6:
        return 100.0
    return min(100.0, len(proof_phrases) * 15)


# ── e36 Speed-of-Light Causality — effects cannot precede causes ────────
# In SR: events outside the future light cone cannot be causally affected.
# In doctrine: phase X+1 cannot enable phase X without time-travel.

def lightcone_separation(time_delta: float, space_delta: float) -> str:
    """Classify spacetime interval: timelike (causal), spacelike (acausal), null."""
    s_squared = (SPEED_OF_LIGHT * time_delta) ** 2 - space_delta ** 2
    if s_squared > 0:
        return "timelike"   # causal connection possible
    if s_squared < 0:
        return "spacelike"  # acausal — no causal link
    return "null"           # light-cone surface


def causality_score(text: str) -> float:
    """Detect causal-ordering violations. Score penalized by:
      - 'as shown above' referencing content below it
      - placeholder citations [TBD] [SOURCE]
      - phases out of order
    """
    violations = 0
    # Forward-reference-as-already-proven
    if re.search(r"as (shown|established|proven|demonstrated) above[\s\S]{0,800}"
                  r"(will (show|demonstrate|prove)|we.ll (demonstrate|show))",
                  text, re.IGNORECASE):
        violations += 1
    # Placeholder citations
    placeholders = re.findall(r"\[(TBD|SOURCE|CITATION|PLACEHOLDER|TODO)\]", text)
    violations += len(placeholders)
    if violations == 0:
        return 100.0
    return max(0.0, 100.0 - 30 * violations)


# ── e37 Absolute Zero — Nernst's third law (no perfection claims) ───────
# S → 0 as T → 0
# Achievable only asymptotically; no system reaches T = 0 in finite steps.
# In doctrine: no claim of "zero downtime / 100% / perfect / always."

BANNED_PERFECTION_PATTERNS = [
    r"\bzero downtime\b",
    r"\b(perfect (uptime|reliability|delivery|results|accuracy)|perfectly reliable)\b",
    r"\b(always works|never fails|never break|always available|always on)\b",
    r"\b100% (reliable|accurate|guaranteed|effective|complete|secure)\b",
    r"\b(cannot be argued|undeniable|irrefutable|self-evident)\b",
]


def absolute_zero_score(text: str) -> float:
    """Detect unreachable-floor claims. Any match = HARD_BLOCK signal."""
    violations = 0
    for pattern in BANNED_PERFECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations += 1
    if violations == 0:
        return 100.0
    return max(0.0, 100.0 - 25 * violations)


# ── e38 Phase Transition — critical temperature with hysteresis ─────────
# Order parameter discontinuity at T_c. Hysteresis loop area > 0 → first-order.
# In doctrine: commitment statements + named no-retreat point.

def phase_transition_score(text: str) -> float:
    """Score commitment density + named no-retreat point."""
    commitments = re.findall(
        r"\b(we (will|commit|are committing|are betting|are staking)|"
        r"past this point|cannot retreat|burn the boats|no going back|"
        r"crossing the threshold|once we cross)\b",
        text, re.IGNORECASE,
    )
    skin_in_game = re.search(
        r"(production-?or-?nothing|extend at no additional fee|refund pro-?rata|"
        r"outcome guarantee|tied to outcomes|success fee|equity stake|we (extend|refund|stake))",
        text, re.IGNORECASE,
    )
    if not commitments:
        return 0.0
    base = min(100.0, len(commitments) * 12)
    return base + 20 if skin_in_game else base


def hysteresis_loop_area(T_up: list[float], T_down: list[float],
                          order_param_up: list[float],
                          order_param_down: list[float]) -> float:
    """Trapezoidal area between heating and cooling curves.

    First-order transition: area > 0. Second-order: area ≈ 0.
    """
    if len(T_up) != len(order_param_up) or len(T_down) != len(order_param_down):
        return 0.0
    up_area = sum((T_up[i+1] - T_up[i]) * (order_param_up[i] + order_param_up[i+1]) / 2
                   for i in range(len(T_up) - 1))
    down_area = sum((T_down[i+1] - T_down[i]) * (order_param_down[i] + order_param_down[i+1]) / 2
                     for i in range(len(T_down) - 1))
    return abs(up_area - down_area)


# ── e39 Bell Entanglement — |S| > 2 violates local realism ──────────────
# CHSH inequality: S = E(a,b) − E(a,b') + E(a',b) + E(a',b')
# Classical (local realist): |S| ≤ 2. Quantum-entangled: |S| up to 2√2 ≈ 2.828.
# In doctrine: claim + evidence + falsification co-located (entangled).

BELL_CLASSICAL_BOUND = 2.0
BELL_QUANTUM_BOUND = 2.0 * math.sqrt(2)  # ≈ 2.828, Tsirelson bound


def chsh_parameter(E_ab: float, E_ab_prime: float,
                    E_a_prime_b: float, E_a_prime_b_prime: float) -> float:
    """CHSH parameter S = E(a,b) − E(a,b') + E(a',b) + E(a',b')."""
    return E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime


def bell_violation(S: float) -> bool:
    """True iff |S| > 2 (genuine entanglement, not classical correlation)."""
    return abs(S) > BELL_CLASSICAL_BOUND


def bell_entanglement_score(text: str) -> float:
    """Score density of co-located claim+evidence+falsification triangles."""
    # Match paragraphs where revenue/% claim AND date AND kill criterion appear within 800 chars
    triangles = re.findall(
        r"(\$\d|\d+%).{0,400}(source|cite|footnote|per\s+\w+|\[\d+\]).{0,400}"
        r"(kill|wrong if|terminate if|<.+by\s+Q|by\s+\d{4})",
        text, re.IGNORECASE,
    )
    if len(triangles) >= 3:
        return 100.0
    if len(triangles) >= 1:
        return 30 + len(triangles) * 25
    return 0.0


# ── e40 Vacuum Fluctuation — baseline activity ──────────────────────────
# Even "empty" space has non-zero ground-state energy: ΔE·Δt ≥ ℏ/2
# In doctrine: artifact must show baseline metric activity, not silent telemetry.

def heisenberg_min_uncertainty(delta_t_seconds: float) -> float:
    """Minimum energy uncertainty for given time uncertainty.

    ΔE·Δt ≥ ℏ/2 → ΔE_min = ℏ / (2·Δt)
    """
    if delta_t_seconds <= 0:
        return float("inf")
    return H_BAR / (2 * delta_t_seconds)


def vacuum_fluctuation_score(text: str) -> float:
    """Score concrete-metric density. Vacuum can't be artificially silent."""
    dollars = len(re.findall(r"\$\d+(?:\.\d+)?(?:\s*[KMBT]|,\d{3})?", text))
    percents = len(re.findall(r"\b\d+(?:\.\d+)?\s*%", text))
    times = len(re.findall(
        r"\b\d+(?:\.\d+)?\s*(days?|weeks?|months?|years?|hours?|minutes?|seconds?|ms)\b",
        text, re.IGNORECASE,
    ))
    if dollars + percents + times >= 30:
        return 100.0
    return min(100.0, (dollars + percents + times) * 3.5)


# ── Physics-formula router ──────────────────────────────────────────────
PHYSICS_RAW_FNS = {
    "quantum_tunnel":     quantum_tunnel_score,
    "pauli_exclusion":    pauli_exclusion_score,
    "casimir_force":      casimir_terseness_score,
    "fine_structure":     fine_structure_score,
    "hawking_horizon":    hawking_horizon_score,
    "speed_of_lumen":     causality_score,
    "absolute_zero":      absolute_zero_score,
    "critical_phase":     phase_transition_score,
    "bell_entanglement":  bell_entanglement_score,
    "vacuum_zeropoint":   vacuum_fluctuation_score,
}


def physics_score(slug: str, text: str) -> float | None:
    """Run a physics engine's formula. Returns None if no formula maps."""
    fn = PHYSICS_RAW_FNS.get(slug)
    return fn(text) if fn else None
