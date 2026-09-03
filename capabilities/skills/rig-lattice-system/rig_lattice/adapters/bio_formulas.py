"""DOCTRINE.md §1.4 + §8 Day 4 — literal bio-inspired formulas.

These are the textbook formulas underlying Layer 2 Nature engines (21-30).
They proxy adaptive-process signals in static text artifacts.

Each formula returns a 0-100 score that feeds the engine's raw_fn alongside
the criteria YAML pack. Most engines combine: 70% criteria score + 30% bio-formula.

References:
  - Lévy flight:        Yang & Deb (2009), Cuckoo Search via Lévy Flights
  - Ant colony / pheromone:  Dorigo & Stützle (2004), Ant Colony Optimization
  - Whale spiral:       Mirjalili & Lewis (2016), Whale Optimization Algorithm
  - Physarum slime mold: Tero et al. (2010), Rules for Biologically Inspired Adaptive Network Design
  - Coral reef:         Salcedo-Sanz et al. (2014), Coral Reefs Optimization with Substrate Layers
  - PSO:                Kennedy & Eberhart (1995), Particle Swarm Optimization
"""
from __future__ import annotations
import math
import re
import statistics
from typing import Iterable


# ── e21 Ant Colony Pheromone ─────────────────────────────────────────────
# Pheromone evaporation: τ(t+1) = (1-ρ)·τ(t) + Δτ
# Healthy process: signals reinforce strong paths, evaporate from weak ones.

EVAPORATION_RHO = 0.1  # standard ACO evaporation rate
MIN_PHEROMONE = 0.01

def pheromone_reinforcement_score(text: str) -> float:
    """Count explicit reinforcement-vs-evaporation language balance.

    Healthy artifact: ≥2 reinforcement signals + ≥1 evaporation signal,
    indicating the process prunes as well as reinforces.
    """
    reinforce = len(re.findall(
        r"\b(double down|invest more in|primary bet|core bet|leading path|"
        r"reinforces|strengthens|amplif(y|ies)|focus on|all-in on)\b",
        text, re.IGNORECASE,
    ))
    evaporate = len(re.findall(
        r"\b(abandon|deprecate|prune|drop|kill (path|option)|let .+ fade|"
        r"de-emphasize|wind down|sunset|retire)\b",
        text, re.IGNORECASE,
    ))
    # 0-100 scale: balance of both signals matters
    if reinforce + evaporate == 0:
        return 0.0
    balance = min(reinforce, evaporate) / max(reinforce, evaporate, 1)
    intensity = min((reinforce + evaporate) / 10, 1.0)
    return round(100 * balance * intensity, 2)


# ── e23 Slime Mold Network (Physarum) ────────────────────────────────────
# Tube reinforcement: D_ij(t+1) = (Q_ij^μ + D_ij(t)) / (1 + D_ij(t))
# Strong paths thicken; weak paths atrophy.

def physarum_path_concentration(text: str) -> float:
    """Score how concentrated the resource flow is on top paths vs scattered."""
    # Approximated by: explicit kills / explicit reinforcements ratio
    kills = re.findall(
        r"(killed because|abandoned because|deprecated because|"
        r"dropped because|pruned because|will not pursue)",
        text, re.IGNORECASE,
    )
    if len(kills) >= 2:
        return min(100.0, 40 + len(kills) * 15)
    return len(kills) * 30.0


# ── e24 Genetic Diversity Pump (Clonal Refinement) ───────────────────────
# Hamming-distance proxy: how different are the explicit alternatives?

def diversity_score(text: str) -> float:
    """Higher when alternatives are genuinely distinct (not minor variants)."""
    alternatives = re.findall(
        r"(alternative \d|option [A-Z]|path [A-Z]|scenario \d|wedge \d)",
        text, re.IGNORECASE,
    )
    if len(alternatives) < 2:
        return 20.0
    # 100 if ≥3 alternatives, scaled
    return min(100.0, 30 + len(alternatives) * 20)


# ── e25 Lévy Flight (Particle Swarm) ─────────────────────────────────────
# Heavy-tail step distribution: P(step > L) ~ L^(-β), with 1 < β ≤ 3
# Adaptive search: occasional long jumps to escape local optima.

LEVY_BETA = 1.5  # standard Lévy exponent

def levy_jump_score(text: str) -> float:
    """Count cross-domain analogy density. True Lévy = jumps to non-adjacent domains."""
    distant_domains = re.findall(
        r"\b(Bloomberg|iOS|App Store|Stripe|Tesla|Spotify|Netflix|Snowflake|"
        r"Databricks|AWS|GitHub|Salesforce|Topcon|Wabtec|Allison|Cummins|Trimble)\b",
        text, re.IGNORECASE,
    )
    unique_jumps = len(set(d.lower() for d in distant_domains))
    if unique_jumps == 0:
        return 0.0
    # Lévy exponent: more unique jumps scale super-linearly
    return min(100.0, 25 * (unique_jumps ** (1 / LEVY_BETA)))


def levy_step_prob(step_size: float, beta: float = LEVY_BETA) -> float:
    """Probability density of a Lévy-distributed step of magnitude step_size."""
    if step_size <= 0:
        return 0.0
    return step_size ** (-beta)


# ── e26 Firefly Synchronization (Bioluminescent Attraction) ─────────────
# Attractiveness β(r) = β_0 · exp(-γ·r²), with γ light absorption constant
# Healthy process: strong signals attract resources from distance.

def firefly_attractiveness_score(text: str) -> float:
    """Score visible economic gradient ($/unit clear and proportional)."""
    revenue_markers = re.findall(
        r"\$\d+(?:\.\d+)?\s*(?:per (?:unit|seat|controller|asset|customer)|"
        r"/(?:mo|year|controller|seat|OEM)|K/mo|M ARR)",
        text, re.IGNORECASE,
    )
    if len(revenue_markers) >= 3:
        return min(100.0, 50 + len(revenue_markers) * 10)
    return len(revenue_markers) * 20.0


# ── e27 Resource Allocator (Chemotaxis Gradient) ─────────────────────────
# E. coli tumble vs swim: gradient-follow if signal increases, tumble if flat.

def chemotaxis_gradient_score(text: str) -> float:
    """Score concrete next-action gradient (specific monthly milestones)."""
    # Non-greedy + non-period to prevent matches from spanning multiple sentences
    monthly_steps = re.findall(
        r"(Month \d+\b|Phase \d|Week \d+)\b[^.\n]{0,80}(audit|launch|ship|sign|train|deploy)",
        text, re.IGNORECASE,
    )
    if len(monthly_steps) >= 6:
        return 100.0
    return min(100.0, len(monthly_steps) * 15)


# ── e28 Whale Spiral (WOA — Whale Optimization Algorithm) ───────────────
# Spiral position update: X(t+1) = D'·e^(bl)·cos(2πl) + X*(t)
# Helical narrowing around current best — anneal exploration → exploitation.

def whale_spiral_annealing(text: str) -> float:
    """Score 3-phase narrowing structure (Foundation → Activation → Scale)."""
    phases = re.findall(
        r"(Foundation|Activation|Scale|Phase 1|Phase 2|Phase 3)",
        text, re.IGNORECASE,
    )
    if len(phases) < 3:
        return 0.0
    # Verify chronological ordering (rough proxy)
    has_progression = bool(re.search(
        r"(?s)Foundation.{20,3000}Activation.{20,3000}Scale",
        text, re.IGNORECASE,
    ))
    base = min(100.0, len(phases) * 8)
    return base if has_progression else base * 0.5


def whale_spiral_step(t: int, total_iter: int, b: float = 1.0) -> tuple[float, float]:
    """One spiral step. Returns (D_prime_coefficient, exponent_factor)."""
    a = 2 - t * (2 / total_iter)  # linearly decreasing exploration radius
    l = -1 + 2 * (t / total_iter)  # spiral parameter -1→1
    return a, math.exp(b * l) * math.cos(2 * math.pi * l)


# ── e29 Cuckoo Parasite ─────────────────────────────────────────────────
# Probability p_a that a host (weakest nest) detects and abandons the parasitic egg.
# In CSO: replace fraction p_a of worst nests each generation.

CUCKOO_ABANDON_PROBABILITY = 0.25  # standard Yang/Deb default

def cuckoo_parasitism_score(text: str) -> float:
    """Score whether the doc injects a parasitic high-deviation idea."""
    parasitic_markers = re.findall(
        r"(radical reframe|first principles?|orthodoxy|industry assumes|"
        r"contrarian|anti-?consensus|the real (category|business|game)|"
        r"category-creating|Bloomberg of|iOS of)",
        text, re.IGNORECASE,
    )
    return min(100.0, len(parasitic_markers) * 12)


def cuckoo_replacement_count(pop_size: int, p_a: float = CUCKOO_ABANDON_PROBABILITY) -> int:
    """How many parasitic eggs replace the worst nests this generation."""
    return max(1, int(pop_size * p_a))


# ── e30 Coral Reef Evolver (CRO-SL) ─────────────────────────────────────
# 5 substrate layers: broadcast, brood, bud, fragment, deprecate
# Each generation runs all 5 modes. Reef diversity preserved by tracking
# substrate occupancy + replacement-probability bounds.

REEF_SUBSTRATES = ("broadcast", "brood", "bud", "fragment", "deprecate")
REEF_DIVERSITY_FLOOR = 0.40           # minimum substrate coverage to stay healthy
REEF_REPLACEMENT_PROB_MAX = 0.30      # cap on how aggressively coral replaces
REEF_STARVATION_FLOOR = 0.05          # minimum allocation per substrate


def coral_reef_substrate_coverage(text: str) -> dict[str, bool]:
    """Detect presence of each of the 5 substrate layers in text."""
    patterns = {
        "broadcast": r"(broadcast|mass-?distribute|ship to every|every controller)",
        "brood":     r"(brood|keep internal|in-?house|engineering productivity)",
        "bud":       r"(bud|spin[- ]?off|sibling product|second product line)",
        "fragment":  r"(fragment|peel off|split out|second-?line)",
        "deprecate": r"(deprecate|kill (offering|feature|line)|sunset|retire|prune)",
    }
    return {name: bool(re.search(p, text, re.IGNORECASE))
            for name, p in patterns.items()}


def coral_reef_score(text: str) -> float:
    """0-100: percentage of 5 substrates that show up in the artifact."""
    coverage = coral_reef_substrate_coverage(text)
    n = sum(1 for v in coverage.values() if v)
    return round((n / len(REEF_SUBSTRATES)) * 100, 2)


def reef_diversity_check(coverage: dict[str, bool]) -> tuple[bool, str]:
    """Boundary test: does substrate coverage exceed the diversity floor?"""
    ratio = sum(1 for v in coverage.values() if v) / len(coverage)
    if ratio < REEF_DIVERSITY_FLOOR:
        return False, f"Reef diversity {ratio:.0%} below floor {REEF_DIVERSITY_FLOOR:.0%}"
    return True, f"Reef diversity {ratio:.0%} above floor"


def reef_replacement_probability(generation: int, max_gens: int) -> float:
    """How aggressively this generation replaces worst nests. Caps at MAX."""
    # Linear ramp from 0.05 to MAX over generations
    progress = min(1.0, generation / max(max_gens, 1))
    p = 0.05 + (REEF_REPLACEMENT_PROB_MAX - 0.05) * progress
    return min(REEF_REPLACEMENT_PROB_MAX, p)


def starvation_floor_ok(substrate_allocations: Iterable[float]) -> tuple[bool, str]:
    """Verify no substrate is below the starvation floor."""
    allocations = list(substrate_allocations)
    if not allocations:
        return False, "no allocations"
    min_alloc = min(allocations)
    if min_alloc < REEF_STARVATION_FLOOR:
        return False, f"substrate at {min_alloc:.2%} below floor {REEF_STARVATION_FLOOR:.0%}"
    return True, f"all substrates above floor (min {min_alloc:.2%})"


# ── Bio-formula router (engine slug → blended raw score) ─────────────────
BIO_RAW_FNS = {
    "pheromone_swarm":          pheromone_reinforcement_score,
    "physarum_prune":           physarum_path_concentration,
    "clonal_refinement":        diversity_score,
    "levy_flight":              levy_jump_score,
    "bioluminescent_attraction":firefly_attractiveness_score,
    "chemotaxis_gradient":      chemotaxis_gradient_score,
    "humpback_spiral":          whale_spiral_annealing,
    "cuckoo_parasitic":         cuckoo_parasitism_score,
    "coral_reef_synthesis":     coral_reef_score,
}


def bio_score(slug: str, text: str) -> float | None:
    """Run an engine's bio-formula on text. Returns None if no formula maps."""
    fn = BIO_RAW_FNS.get(slug)
    return fn(text) if fn else None
