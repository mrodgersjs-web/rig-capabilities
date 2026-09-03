"""Factory for physics engine modules (HARD GATES).

Per DOCTRINE.md §1.3: L3 physics engines short-circuit the pipeline on
failure. The factory sets is_gate=True so DeviationEngine.score() returns
status='HARD_BLOCK' instead of 'BLOCK' when threshold is missed.

Blend:
  - 0.5 × criteria YAML pack score
  - 0.5 × literal physics formula
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

from rig_lattice.core.base import DeviationEngine
from rig_lattice.core.registry import resolve_engine
from rig_lattice.adapters.criteria_runner import raw_score_from_criteria
from rig_lattice.adapters.physics_formulas import physics_score
from rig_lattice.adapters.baselines import get_baseline_samples

CRITERIA_WEIGHT = 0.5
PHYSICS_WEIGHT = 0.5


def make_physics_engine(engine_id: int) -> DeviationEngine:
    """Build a HARD-GATE DeviationEngine for a physics engine (id 31-40)."""
    spec = resolve_engine("physics", engine_id)

    def raw_fn(artifact: str, _slug=spec.slug) -> float:
        if not isinstance(artifact, str):
            return 0.0
        crit = raw_score_from_criteria(artifact, _slug)
        phys = physics_score(_slug, artifact)
        if phys is None:
            return crit
        return CRITERIA_WEIGHT * crit + PHYSICS_WEIGHT * phys

    def baseline_fn(_slug=spec.slug) -> list[float]:
        baselines = []
        for sample in get_baseline_samples():
            crit = raw_score_from_criteria(sample, _slug)
            phys = physics_score(_slug, sample)
            if phys is None:
                baselines.append(crit)
            else:
                baselines.append(CRITERIA_WEIGHT * crit + PHYSICS_WEIGHT * phys)
        return baselines

    return DeviationEngine(
        id=spec.id,
        name=spec.name,
        layer=spec.layer,
        target=spec.target,
        raw_fn=raw_fn,
        baseline_fn=baseline_fn,
        threshold=spec.threshold,
        hard_blocks=(),
        is_gate=True,  # ← physics short-circuit
    )
