"""Factory for nature engine modules.

Each nature engine combines:
  - criteria YAML pack (process signals expressed structurally)
  - bio-inspired formula (literal numeric proxy)

Blend: 0.7 × criteria_score + 0.3 × bio_formula_score. The blend ensures
the engine respects the spec's "exact bio-inspired formulas" requirement
while still using the deterministic YAML criteria as the primary signal.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

from rig_lattice.core.base import DeviationEngine
from rig_lattice.core.registry import resolve_engine
from rig_lattice.adapters.criteria_runner import raw_score_from_criteria
from rig_lattice.adapters.baselines import baseline_scores_for_engine
from rig_lattice.adapters.bio_formulas import bio_score, BIO_RAW_FNS

CRITERIA_WEIGHT = 0.7
BIO_WEIGHT = 0.3


def make_nature_engine(engine_id: int) -> DeviationEngine:
    """Build a DeviationEngine for a nature engine (id 21-30).

    The factory blends:
      - 70% YAML criteria pack score
      - 30% bio-inspired formula (Lévy, pheromone, whale spiral, etc.)

    If no bio-formula maps to the slug, the criteria score is used 100%.
    """
    spec = resolve_engine("nature", engine_id)

    def raw_fn(artifact: str, _slug=spec.slug) -> float:
        if not isinstance(artifact, str):
            return 0.0
        crit = raw_score_from_criteria(artifact, _slug)
        bio = bio_score(_slug, artifact)
        if bio is None:
            return crit
        return CRITERIA_WEIGHT * crit + BIO_WEIGHT * bio

    def baseline_fn(_slug=spec.slug) -> list[float]:
        # For nature, baselines pass through the same blended formula so
        # the σ comparison is apples-to-apples.
        from rig_lattice.adapters.baselines import get_baseline_samples
        from rig_lattice.adapters.criteria_runner import raw_score_from_criteria as _crit
        baselines = []
        for sample in get_baseline_samples():
            crit = _crit(sample, _slug)
            bio = bio_score(_slug, sample)
            if bio is None:
                baselines.append(crit)
            else:
                baselines.append(CRITERIA_WEIGHT * crit + BIO_WEIGHT * bio)
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
        is_gate=spec.is_gate,
    )
