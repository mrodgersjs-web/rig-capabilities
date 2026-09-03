"""IQRSQPI 7-step meta-pipeline runner.

This module owns the *pipeline runner* — the 7-step process that executes
inside one lattice coordinate. It no longer owns any lattice math: the
geometry, the BMS bands, the cell enumeration and the diamond axis all come
from ``rig_lattice.lattice``, which is the single source of truth.

  588 cells = 7 levels x 3 diamonds x 4 BMS modes x 7 IQRSQPI steps
              84 primary coordinates x 7 steps

An earlier version of this file described the lattice as "7 IQRSQPI steps x 3
layers x 4 BMS modes x 7 IQRSQPI steps". That arrived at 588 by squaring the
process axis, which is wrong: IQRSQPI is the process *inside* a coordinate,
not an axis of it. The X-axis is Level/Altitude.

The 7 IQRSQPI steps:
  1. INTENT      — Classify & Route
  2. QUESTION    — Decompose
  3. RESEARCH    — Sources & Claims
  4. SOLUTION    — Synthesize
  5. QUALITY     — Gates & Score
  6. PROOF       — Verify & Audit
  7. INTEGRATE   — Deliver & Track

The BMS confidence router → A1/A2/A3/A4:
  A1  PYTHON_ONLY      confidence >= 0.75
  A2  HYBRID           0.45 <= confidence < 0.75
  A3  AGENT_BOUNDED    0.25 <= confidence < 0.45
  A4  LLM_AGENT_FREE   confidence < 0.25 (or human gate forced)

The 3 diamonds (Y-axis): D1 Physical, D2 Cognitive, D3 Nature.
"""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

# ── Canonical lattice re-exports ──────────────────────────────────────────
# These names used to be defined here, each a second implementation of the
# same doctrine. They are now bound to the canonical modules so there is one
# BMS band table, one diamond axis and one cell enumeration in the bundle.
from rig_lattice.lattice.constants import (  # noqa: F401
    BMS_THRESHOLD_BANDS,
    N_CELLS,
    BMSMode,
    Diamond,
)
from rig_lattice.lattice.generator import all_cells as _canonical_cell_ids
from rig_lattice.lattice.resolver import CellCoordinate, parse_cell_id

# The 3 D-axes. `Dimension` was a separate enum with "D1_physical" values;
# it is now the canonical Diamond.
Dimension = Diamond

# One cell type for the whole bundle.
LatticeCell = CellCoordinate

# Lower bound of each BMS band, in the shape the vendored call sites expect.
BMS_THRESHOLDS: dict[BMSMode, float] = {
    mode: BMS_THRESHOLD_BANDS[mode.value][0] for mode in BMSMode
}
BMS_THRESHOLDS[BMSMode.A4] = 0.00

TOTAL_CELLS = N_CELLS  # 588


def all_cells() -> list[CellCoordinate]:
    """Every one of the 588 execution cells as a canonical coordinate."""
    return [parse_cell_id(cid) for cid in _canonical_cell_ids()]


def route_bms(confidence: float, force_a4: bool = False) -> BMSMode:
    """Map confidence (0-1) to a BMS mode, with the force_a4 escape hatch.

    Thin wrapper over ``BMSMode.from_score`` so the band table lives in one
    place. ``force_a4=True`` short-circuits to the mandatory human gate.
    """
    if force_a4:
        return BMSMode.A4
    return BMSMode.from_score(confidence)


class IQRSQPIStep(str, Enum):
    INTENT = "intent"
    QUESTION = "question"
    RESEARCH = "research"
    SOLUTION = "solution"
    QUALITY = "quality"
    PROOF = "proof"
    INTEGRATE = "integrate"


IQRSQPI_ORDER = (
    IQRSQPIStep.INTENT,
    IQRSQPIStep.QUESTION,
    IQRSQPIStep.RESEARCH,
    IQRSQPIStep.SOLUTION,
    IQRSQPIStep.QUALITY,
    IQRSQPIStep.PROOF,
    IQRSQPIStep.INTEGRATE,
)


# Canonical step-code mapping. This module's IQRSQPIStep uses word values
# ("intent"), the lattice uses codes ("I1"); handlers are keyed by the former.
CANONICAL_STEP_CODE: dict[str, str] = {
    "intent": "I1",
    "question": "Q1",
    "research": "R",
    "solution": "S",
    "quality": "Q2",
    "proof": "P",
    "integrate": "I2",
}


# ── Pipeline runner ───────────────────────────────────────────────────────
@dataclass
class StepResult:
    step: IQRSQPIStep
    ok: bool
    output: Any = None
    elapsed_ms: float = 0.0
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "step": self.step.value,
            "ok": self.ok,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "reason": self.reason,
        }


@dataclass
class IQRSQPIRun:
    mission_id: str
    bms_mode: BMSMode
    confidence: float
    steps: list[StepResult] = field(default_factory=list)
    ok: bool = True
    short_circuited_at: IQRSQPIStep | None = None

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "bms_mode": self.bms_mode.value,
            "confidence": round(self.confidence, 3),
            "ok": self.ok,
            "short_circuited_at": self.short_circuited_at.value if self.short_circuited_at else None,
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": len(self.steps),
            "passed_steps": sum(1 for s in self.steps if s.ok),
        }


# A step handler is a callable: state_dict → (ok, output, reason)
StepHandler = Callable[[dict], tuple[bool, Any, str]]


def run_iqrsqpi(
    handlers: dict[IQRSQPIStep, StepHandler],
    initial_state: dict | None = None,
    confidence: float = 0.5,
    force_a4: bool = False,
    mission_id: str | None = None,
) -> IQRSQPIRun:
    """Run the 7-step IQRSQPI pipeline.

    Args:
        handlers: dict[step → callable] mapping each step to its implementation
        initial_state: state dict passed through; each handler mutates it
        confidence: 0-1 used by router to pick BMS mode
        force_a4: skip router → A4 (mandatory human gate)
        mission_id: optional ID; auto-generated if omitted

    Returns:
        IQRSQPIRun with per-step results + short-circuit info
    """
    mid = mission_id or f"iqr-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
    mode = route_bms(confidence, force_a4)
    run = IQRSQPIRun(mission_id=mid, bms_mode=mode, confidence=confidence)
    state = dict(initial_state or {})
    state["mission_id"] = mid
    state["bms_mode"] = mode.value
    state["confidence"] = confidence

    for step in IQRSQPI_ORDER:
        handler = handlers.get(step)
        if handler is None:
            run.steps.append(StepResult(step=step, ok=False,
                                          reason=f"no handler for {step.value}"))
            run.ok = False
            run.short_circuited_at = step
            return run

        t0 = time.time()
        try:
            ok, output, reason = handler(state)
        except Exception as e:
            ok, output, reason = False, None, f"handler error: {type(e).__name__}: {e}"
        elapsed_ms = (time.time() - t0) * 1000

        result = StepResult(step=step, ok=ok, output=output,
                              elapsed_ms=elapsed_ms, reason=reason)
        run.steps.append(result)
        # propagate output to state for next step
        state[step.value] = output

        if not ok:
            run.ok = False
            run.short_circuited_at = step
            return run

    return run


def steps_completed(run: IQRSQPIRun) -> list[IQRSQPIStep]:
    return [s.step for s in run.steps if s.ok]


def short_circuit_step(run: IQRSQPIRun) -> IQRSQPIStep | None:
    return run.short_circuited_at
