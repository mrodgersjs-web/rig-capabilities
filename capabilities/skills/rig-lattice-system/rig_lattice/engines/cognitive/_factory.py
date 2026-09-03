"""Factory for cognitive engine modules.

Each engine module is a 10-line shim that calls make_cognitive_engine() with
its registry-defined id + slug. The factory wires raw_fn (reads YAML pack)
and baseline_fn (10-sample corpus) and returns a fully-formed DeviationEngine.
"""
from __future__ import annotations
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

from rig_lattice.core.base import DeviationEngine
from rig_lattice.core.registry import resolve_engine, EngineSpec
from rig_lattice.adapters.criteria_runner import raw_score_from_criteria
from rig_lattice.adapters.baselines import baseline_scores_for_engine


def make_cognitive_engine(engine_id: int) -> DeviationEngine:
    """Build a DeviationEngine instance for a cognitive engine by registry id.

    The factory binds:
      - raw_fn:       runs the engine's YAML criteria pack
      - baseline_fn:  returns cached 10-sample baseline scores
      - threshold:    from registry (default +3σ)
      - layer:        'cognitive'
      - is_gate:      False (cognitive engines are scoring, not gating)
    """
    spec = resolve_engine("cognitive", engine_id)

    def raw_fn(artifact: str, _slug=spec.slug) -> float:
        if not isinstance(artifact, str):
            return 0.0
        return raw_score_from_criteria(artifact, _slug)

    def baseline_fn(_slug=spec.slug) -> list[float]:
        return list(baseline_scores_for_engine(_slug))

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
