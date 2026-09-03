"""DOCTRINE.md §1.4 + §5 — Canonical 40-engine registry.

Every engine resolves to exactly one entry here with:
  {id, name (codename), layer, target, threshold, slug, module_path}

`module_path` points to the implementation file (will be filled in as
engines/<layer>/eNN_*.py modules are written in Days 3-5).
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineSpec:
    id: int
    name: str          # CodeName (display + lookup)
    slug: str          # snake_case slug (matches criteria/<slug>.yaml)
    layer: str         # cognitive | nature | physics
    target: str        # output | process | state
    threshold: float   # default min σ to PASS
    module_path: str   # engines/<layer>/eNN_*.py (Days 3-5)
    is_gate: bool = False  # True for L3 physics engines


# ── Layer 1: Cognitive (01–20, OUTPUT, ±20σ) ──────────────────────────────
COGNITIVE = [
    EngineSpec( 1, "GravityEscape",                "gravity_escape",                "cognitive", "output", 3.0, "engines/cognitive/e01_gravity_escape.py"),
    EngineSpec( 2, "RealityAnchor",                "reality_anchor",                "cognitive", "output", 3.0, "engines/cognitive/e02_reality_anchor.py"),
    EngineSpec( 3, "FeynmanXRay",                  "feynman_xray",                  "cognitive", "output", 3.0, "engines/cognitive/e03_feynman_xray.py"),
    EngineSpec( 4, "MechanismFurnace",             "mechanism_furnace",             "cognitive", "output", 3.0, "engines/cognitive/e04_mechanism_furnace.py"),
    EngineSpec( 5, "RuptureEngine",                "rupture",                       "cognitive", "output", 3.0, "engines/cognitive/e05_rupture_engine.py"),
    EngineSpec( 6, "CollisionCollider",            "frame_collision",               "cognitive", "output", 3.0, "engines/cognitive/e06_collision_collider.py"),
    EngineSpec( 7, "VoltageReactor",               "voltage",                       "cognitive", "output", 3.0, "engines/cognitive/e07_voltage_reactor.py"),
    EngineSpec( 8, "EvolutionaryMemoryFlywheel",   "darwinian_selection",           "cognitive", "output", 3.0, "engines/cognitive/e08_evolutionary_memory_flywheel.py"),
    EngineSpec( 9, "MemoryResidue",                "memory_residue",                "cognitive", "output", 3.0, "engines/cognitive/e09_memory_residue.py"),
    EngineSpec(10, "TemporalHorizonIntegrity",     "temporal_horizon_integrity",    "cognitive", "output", 3.0, "engines/cognitive/e10_temporal_horizon_integrity.py"),
    EngineSpec(11, "AutonomyCalibration",          "autonomy_calibration",          "cognitive", "output", 3.0, "engines/cognitive/e11_autonomy_calibration.py"),
    EngineSpec(12, "PredictiveErrorCalibration",   "predictive_surprise",           "cognitive", "output", 3.0, "engines/cognitive/e12_predictive_error_calibration.py"),
    EngineSpec(13, "AntiSlopAuditor",              "anti_slop_auditor",             "cognitive", "output", 3.0, "engines/cognitive/e13_anti_slop_auditor.py"),
    EngineSpec(14, "SpecificityGate",              "kolmogorov_originality",        "cognitive", "output", 3.0, "engines/cognitive/e14_specificity_gate.py"),
    EngineSpec(15, "SourcePerClaim",               "hermeneutic_density",           "cognitive", "output", 3.0, "engines/cognitive/e15_source_per_claim.py"),
    EngineSpec(16, "FalsificationPrereg",          "falsification_prereg",          "cognitive", "output", 3.0, "engines/cognitive/e16_falsification_prereg.py"),
    EngineSpec(17, "DissentRecorder",              "opponent_process",              "cognitive", "output", 3.0, "engines/cognitive/e17_dissent_recorder.py"),
    EngineSpec(18, "BrierCalibrator",              "bayesian_calibration",          "cognitive", "output", 3.0, "engines/cognitive/e18_brier_calibrator.py"),
    EngineSpec(19, "CognitiveSovereignty",         "cognitive_sovereignty",         "cognitive", "output", 3.0, "engines/cognitive/e19_cognitive_sovereignty.py"),
    EngineSpec(20, "CompoundingEdge",              "compounding_edge",              "cognitive", "output", 3.0, "engines/cognitive/e20_compounding_edge.py"),
]

# ── Layer 2: Nature (21–30, PROCESS, ±20σ) ────────────────────────────────
NATURE = [
    EngineSpec(21, "AntColonyPheromone",  "pheromone_swarm",           "nature", "process", 3.0, "engines/nature/e21_ant_colony.py"),
    EngineSpec(22, "BeeForagingAllocator","bee_foraging",              "nature", "process", 3.0, "engines/nature/e22_bee_foraging.py"),
    EngineSpec(23, "SlimeMoldNetwork",    "physarum_prune",            "nature", "process", 3.0, "engines/nature/e23_slime_mold.py"),
    EngineSpec(24, "GeneticDiversityPump","clonal_refinement",         "nature", "process", 3.0, "engines/nature/e24_genetic_diversity.py"),
    EngineSpec(25, "ParticleSwarmCohesion","levy_flight",              "nature", "process", 3.0, "engines/nature/e25_particle_swarm.py"),
    EngineSpec(26, "FireflySynchronization","bioluminescent_attraction","nature","process",3.0, "engines/nature/e26_firefly_sync.py"),
    EngineSpec(27, "ResourceAllocator",   "chemotaxis_gradient",       "nature", "process", 3.0, "engines/nature/e27_resource_allocator.py"),
    EngineSpec(28, "WhaleSpiral",         "humpback_spiral",           "nature", "process", 3.0, "engines/nature/e28_whale_spiral.py"),
    EngineSpec(29, "CuckooParasite",      "cuckoo_parasitic",          "nature", "process", 3.0, "engines/nature/e29_cuckoo_parasite.py"),
    EngineSpec(30, "CoralReefEvolver",    "coral_reef_synthesis",      "nature", "process", 3.0, "engines/nature/e30_coral_reef.py"),
]

# ── Layer 3: Physics (31–40, STATE, ±30σ HARD) ────────────────────────────
PHYSICS = [
    EngineSpec(31, "QuantumTunneling",   "quantum_tunnel",       "physics", "state", 3.0, "engines/physics/e31_quantum_tunneling.py", is_gate=True),
    EngineSpec(32, "PauliExclusion",     "pauli_exclusion",      "physics", "state", 3.0, "engines/physics/e32_pauli_exclusion.py", is_gate=True),
    EngineSpec(33, "CasimirPressure",    "casimir_force",        "physics", "state", 3.0, "engines/physics/e33_casimir_pressure.py", is_gate=True),
    EngineSpec(34, "FineTuningRatio",    "fine_structure",       "physics", "state", 3.0, "engines/physics/e34_fine_tuning.py", is_gate=True),
    EngineSpec(35, "HawkingRadiation",   "hawking_horizon",      "physics", "state", 3.0, "engines/physics/e35_hawking_radiation.py", is_gate=True),
    EngineSpec(36, "SpeedOfLightCausality","speed_of_lumen",     "physics", "state", 3.0, "engines/physics/e36_speed_of_light.py", is_gate=True),
    EngineSpec(37, "AbsoluteZeroFloor",  "absolute_zero",        "physics", "state", 3.0, "engines/physics/e37_absolute_zero.py", is_gate=True),
    EngineSpec(38, "PhaseTransition",    "critical_phase",       "physics", "state", 3.0, "engines/physics/e38_phase_transition.py", is_gate=True),
    EngineSpec(39, "BellEntanglement",   "bell_entanglement",    "physics", "state", 3.0, "engines/physics/e39_bell_entanglement.py", is_gate=True),
    EngineSpec(40, "VacuumFluctuation",  "vacuum_zeropoint",     "physics", "state", 3.0, "engines/physics/e40_vacuum_fluctuation.py", is_gate=True),
]

# ── The canonical registry ────────────────────────────────────────────────
ENGINE_REGISTRY: list[EngineSpec] = COGNITIVE + NATURE + PHYSICS

# Sanity: exactly 40, exactly 20/10/10 per layer
assert len(ENGINE_REGISTRY) == 40, f"Expected 40 engines, got {len(ENGINE_REGISTRY)}"
assert len(COGNITIVE) == 20, f"Expected 20 cognitive, got {len(COGNITIVE)}"
assert len(NATURE) == 10, f"Expected 10 nature, got {len(NATURE)}"
assert len(PHYSICS) == 10, f"Expected 10 physics, got {len(PHYSICS)}"


# ── Resolver functions ────────────────────────────────────────────────────
def resolve_engine(layer: str, engine_id: int) -> EngineSpec:
    """Resolve an engine by (layer, id)."""
    for e in ENGINE_REGISTRY:
        if e.layer == layer and e.id == engine_id:
            return e
    raise KeyError(f"No engine with layer={layer} id={engine_id}")


def resolve_by_codename(name: str) -> EngineSpec:
    """Resolve an engine by codename (case-insensitive)."""
    target = name.lower()
    for e in ENGINE_REGISTRY:
        if e.name.lower() == target:
            return e
    raise KeyError(f"No engine with codename={name}")


def resolve_by_slug(slug: str) -> EngineSpec:
    """Resolve an engine by snake_case slug."""
    for e in ENGINE_REGISTRY:
        if e.slug == slug:
            return e
    raise KeyError(f"No engine with slug={slug}")


def list_engines_by_layer(layer: str) -> list[EngineSpec]:
    """All engines for a given layer."""
    return [e for e in ENGINE_REGISTRY if e.layer == layer]


def physics_engines() -> list[EngineSpec]:
    """All L3 physics engines (gate-mode)."""
    return [e for e in ENGINE_REGISTRY if e.is_gate]


def engine_count_by_layer() -> dict[str, int]:
    """Summary count per layer."""
    counts: dict[str, int] = {}
    for e in ENGINE_REGISTRY:
        counts[e.layer] = counts.get(e.layer, 0) + 1
    return counts
