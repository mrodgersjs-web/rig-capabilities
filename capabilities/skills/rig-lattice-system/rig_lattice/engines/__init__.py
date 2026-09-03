"""DOCTRINE.md §5 engines package.

Auto-discovers every engine module under engines/{cognitive,nature,physics}/
and exposes a unified `load_all_engines()` API.
"""
from rig_lattice.engines.cognitive import load_cognitive_engines
from rig_lattice.engines.nature import load_nature_engines
from rig_lattice.engines.physics import load_physics_engines

__all__ = ["load_cognitive_engines", "load_nature_engines",
            "load_physics_engines", "load_all_engines", "physics_short_circuit"]


def load_all_engines():
    """Return list[DeviationEngine] for all 40 layers (cognitive + nature + physics)."""
    return load_cognitive_engines() + load_nature_engines() + load_physics_engines()


def physics_short_circuit(text: str) -> tuple[bool, list[dict]]:
    """Run physics gates FIRST. If any HARD_BLOCK → short-circuit the pipeline.

    Returns (any_blocked, list of {name, slug, status, madz, reason}).
    Per DOCTRINE.md §4: gate ordering is physics → cognitive → nature → RIG-L,
    and any L3 BLOCK halts everything below.
    """
    failures = []
    for engine in load_physics_engines():
        result = engine.score(text)
        if result.status == "HARD_BLOCK":
            failures.append({
                "name": engine.name,
                "slug": engine.layer + "/" + str(engine.id),
                "engine_id": engine.id,
                "status": result.status,
                "madz": result.madz,
                "reason": result.reason or f"σ {result.madz:+.2f} below threshold {engine.threshold:+.2f}",
            })
    return bool(failures), failures
