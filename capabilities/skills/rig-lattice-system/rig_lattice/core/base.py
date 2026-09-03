"""DOCTRINE.md §5.1 — DeviationEngine base class.

Every engine is a DeviationEngine dataclass with:
  - raw_fn:      artifact → raw score (engine-specific signal)
  - baseline_fn: () → list[float] generic baseline corpus
  - threshold:   minimum RobustMADZ to PASS (default +3σ)
  - hard_blocks: tuple of (artifact → bool) predicates; any True → BLOCK

The DeviationEngine.score() method runs the full deviation check and returns
an EngineResult.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Sequence, Any

from rig_lattice.core.robust_mad_z import robust_mad_z


@dataclass
class EngineResult:
    """Standardized output of a DeviationEngine.score() call."""
    engine: str            # codename (e.g. "GravityEscape")
    engine_id: int         # 01–40
    layer: str             # cognitive | nature | physics
    target: str            # output | process | state
    status: str            # PASS | BLOCK | HARD_BLOCK
    raw: float = 0.0       # raw engine score (pre-MAD-Z)
    madz: float = 0.0      # Robust-MAD-Z (signed σ)
    reason: str = ""       # hard-block reason if blocked

    def to_dict(self) -> dict:
        return {
            "engine": self.engine, "engine_id": self.engine_id,
            "layer": self.layer, "target": self.target,
            "status": self.status,
            "raw": self.raw, "madz": round(self.madz, 3),
            "reason": self.reason,
        }


@dataclass
class DeviationEngine:
    """A single DES engine. Implementations live under engines/<layer>/eNN_*.py."""
    id: int
    name: str                                # codename, e.g. "GravityEscape"
    layer: str                               # cognitive | nature | physics
    target: str                              # output | process | state
    raw_fn: Callable[[Any], float]           # artifact → raw score
    baseline_fn: Callable[[], Sequence[float]]  # () → list[float]
    threshold: float = 3.0
    hard_blocks: Sequence[Callable[[Any], bool]] = field(default_factory=tuple)
    is_gate: bool = False                    # True for L3 physics engines

    def score(self, artifact: Any) -> EngineResult:
        """Run all hard-block predicates then compute Robust-MAD-Z."""
        # Hard-block predicates short-circuit before any scoring
        for hb in self.hard_blocks:
            try:
                if hb(artifact):
                    return EngineResult(
                        engine=self.name, engine_id=self.id,
                        layer=self.layer, target=self.target,
                        status="HARD_BLOCK" if self.is_gate else "BLOCK",
                        reason=getattr(hb, "__name__", "hard_block"),
                    )
            except Exception as e:
                return EngineResult(
                    engine=self.name, engine_id=self.id,
                    layer=self.layer, target=self.target,
                    status="BLOCK",
                    reason=f"hard_block_error: {e}",
                )

        # Compute raw score + Robust-MAD-Z
        raw = self.raw_fn(artifact)
        baseline = self.baseline_fn()
        z = robust_mad_z(raw, baseline)

        # Clamp σ to layer-appropriate limits per DOCTRINE.md §1.3:
        #   cognitive / nature → ±20σ
        #   physics           → ±30σ
        cap = 30.0 if self.layer == "physics" else 20.0
        if z > cap:
            z = cap
        elif z < -cap:
            z = -cap

        # Layer-specific status logic
        if self.is_gate:
            # L3 physics: pass = positive sigma, fail = HARD_BLOCK
            status = "PASS" if z >= self.threshold else "HARD_BLOCK"
        else:
            status = "PASS" if z >= self.threshold else "BLOCK"

        return EngineResult(
            engine=self.name, engine_id=self.id,
            layer=self.layer, target=self.target,
            status=status, raw=raw, madz=z,
        )
