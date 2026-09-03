"""Codename -> engine id aliases. GENERATED — do not hand-edit.

The ~40 ``rig-<codename>`` skills and the Alfred LinkedIn pipeline address the
deviation engines by short codename (COLLIDER, SURPRISE, BREAKER, ...). This
table is the machine-readable twin of the table in
``capabilities/commands/rig-lattice.md``; a done-test asserts the two agree.

Regenerate with::

    PYTHONPATH=. python3 scripts/gen_engine_aliases.py

Source of truth: ``rig_lattice/core/registry.py`` for the id ordering and
``rig_lattice/criteria/<slug>.json`` for the codename. Nothing here is typed
by hand, so the table cannot drift from the registry silently.

One known upstream conflict, preserved rather than papered over: engine 15 is
``hermeneutic_density`` / ``SourcePerClaim`` — per-claim source weighting,
which is the WITNESS engine. Its criteria pack is labelled ``WELLSPRING``
(the hedonic-adaptation concept, a different engine entirely). Both codenames
resolve to e15 so either caller works; the mislabel is recorded in
PROVENANCE.md.
"""

from __future__ import annotations

CODENAME_TO_ENGINE_ID: dict[str, str] = {
    "GRAVITON": "e01",                    # gravity_escape (cognitive)
    "ANCHOR": "e02",                      # reality_anchor (cognitive)
    "XRAY": "e03",                        # feynman_xray (cognitive)
    "FORGE": "e04",                       # mechanism_furnace (cognitive)
    "BREAKER": "e05",                     # rupture (cognitive)
    "COLLIDER": "e06",                    # frame_collision (cognitive)
    "VOLT": "e07",                        # voltage (cognitive)
    "DARWIN": "e08",                      # darwinian_selection (cognitive)
    "ECHO": "e09",                        # memory_residue (cognitive)
    "HORIZON": "e10",                     # temporal_horizon_integrity (cognitive)
    "SOVEREIGN": "e11",                   # autonomy_calibration (cognitive)
    "SURPRISE": "e12",                    # predictive_surprise (cognitive)
    "ANTISLOPAUDITOR": "e13",             # anti_slop_auditor (cognitive)
    "GLYPH": "e14",                       # kolmogorov_originality (cognitive)
    "WELLSPRING": "e15",                  # hermeneutic_density (cognitive)
    "FALSIFICATIONPREREG": "e16",         # falsification_prereg (cognitive)
    "REBOUND": "e17",                     # opponent_process (cognitive)
    "BAYES": "e18",                       # bayesian_calibration (cognitive)
    "SHIELD": "e19",                      # cognitive_sovereignty (cognitive)
    "COMPOUNDINGEDGE": "e20",             # compounding_edge (cognitive)
    "SWARM": "e21",                       # pheromone_swarm (nature)
    "BEEFORAGINGALLOCATOR": "e22",        # bee_foraging (nature)
    "SLIME": "e23",                       # physarum_prune (nature)
    "CLONAL": "e24",                      # clonal_refinement (nature)
    "ALBATROSS": "e25",                   # levy_flight (nature)
    "LUMINA": "e26",                      # bioluminescent_attraction (nature)
    "COLI": "e27",                        # chemotaxis_gradient (nature)
    "HUMPBACK": "e28",                    # humpback_spiral (nature)
    "CUCKOO": "e29",                      # cuckoo_parasitic (nature)
    "REEF": "e30",                        # coral_reef_synthesis (nature)
    "TUNNEL": "e31",                      # quantum_tunnel (physics)
    "PAULI": "e32",                       # pauli_exclusion (physics)
    "CASIMIR": "e33",                     # casimir_force (physics)
    "PARSEC": "e34",                      # fine_structure (physics)
    "HORIZON-GATE": "e35",                # hawking_horizon (physics)
    "LUMEN": "e36",                       # speed_of_lumen (physics)
    "KELVIN": "e37",                      # absolute_zero (physics)
    "CRITICAL": "e38",                    # critical_phase (physics)
    "BELL": "e39",                        # bell_entanglement (physics)
    "ZEROPOINT": "e40",                   # vacuum_zeropoint (physics)
    # Upstream mislabel: e15's pack says WELLSPRING, the engine is WITNESS.
    "WITNESS": "e15",
}

ENGINE_ID_TO_CODENAME: dict[str, str] = {
    engine_id: codename
    for codename, engine_id in CODENAME_TO_ENGINE_ID.items()
    if codename not in {'WITNESS'}
}

ENGINE_ID_TO_SLUG: dict[str, str] = {
    "e01": "gravity_escape",
    "e02": "reality_anchor",
    "e03": "feynman_xray",
    "e04": "mechanism_furnace",
    "e05": "rupture",
    "e06": "frame_collision",
    "e07": "voltage",
    "e08": "darwinian_selection",
    "e09": "memory_residue",
    "e10": "temporal_horizon_integrity",
    "e11": "autonomy_calibration",
    "e12": "predictive_surprise",
    "e13": "anti_slop_auditor",
    "e14": "kolmogorov_originality",
    "e15": "hermeneutic_density",
    "e16": "falsification_prereg",
    "e17": "opponent_process",
    "e18": "bayesian_calibration",
    "e19": "cognitive_sovereignty",
    "e20": "compounding_edge",
    "e21": "pheromone_swarm",
    "e22": "bee_foraging",
    "e23": "physarum_prune",
    "e24": "clonal_refinement",
    "e25": "levy_flight",
    "e26": "bioluminescent_attraction",
    "e27": "chemotaxis_gradient",
    "e28": "humpback_spiral",
    "e29": "cuckoo_parasitic",
    "e30": "coral_reef_synthesis",
    "e31": "quantum_tunnel",
    "e32": "pauli_exclusion",
    "e33": "casimir_force",
    "e34": "fine_structure",
    "e35": "hawking_horizon",
    "e36": "speed_of_lumen",
    "e37": "absolute_zero",
    "e38": "critical_phase",
    "e39": "bell_entanglement",
    "e40": "vacuum_zeropoint",
}


def resolve_codename(codename: str) -> str:
    """Codename (any case) -> engine id. Raises KeyError on an unknown name."""
    return CODENAME_TO_ENGINE_ID[codename.strip().upper()]


def engine_slug(engine_id: str) -> str:
    """Engine id (e01..e40) -> criteria slug."""
    return ENGINE_ID_TO_SLUG[engine_id.strip().lower()]


__all__ = [
    "CODENAME_TO_ENGINE_ID",
    "ENGINE_ID_TO_CODENAME",
    "ENGINE_ID_TO_SLUG",
    "engine_slug",
    "resolve_codename",
]
