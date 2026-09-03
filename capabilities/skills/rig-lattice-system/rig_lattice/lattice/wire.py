"""LatticeWire — build cards, quality gates, and deterministic intent routing.

Vendored from strategy_studio ``lattice_wire.py``. Four load-bearing changes:

1. **One Diamond.** The vendored file carried a second Y-axis dialect
   (``D1_STRATEGY`` / ``D2_INTELLIGENCE`` / ``D3_OPERATIONS``). That is not the
   doctrine. The canonical planes are D1 Physical / D2 Cognitive / D3 Nature,
   and the routing keyword sets below are derived from ``DIAMOND_OWNS`` rather
   than from the dropped labels. ``constants.LEGACY_DIAMOND_LABELS`` exists
   only so a reader of the old artifacts can map them across.

2. **No pydantic.** ``BuildCard``, ``QualityGate``, ``GateResult`` and
   ``RouteResult`` are frozen dataclasses with explicit ``to_dict()``.

3. **BMS math lives with the router.** ``compute_bms`` is imported from
   ``rig_lattice.lattice.bms``; it is not redefined here.

4. **No silent A3 downgrade.** The vendored ``_execute_a3`` imported
   ``strategy_studio.langgraph_executor`` and fell back to the A1 deterministic
   path on ImportError — a green that cannot go red. ``archetype_runner``
   raises ``NotImplementedError`` for A3 instead.

The vendored B-engine bridge (``wire_cell_to_engine``, ``_execute_a1..a4``,
``LatticeOrchestrator``, ``generate_lattice_map``) is not carried over: it
called ``strategy_studio.engines`` / ``strategy_studio.core.types``, neither of
which is part of this bundle, so every one of those paths would have been an
import error dressed up as a fallback. The orchestration role belongs to
``rig_lattice.system.orchestrator.run_system`` (7 levels, BMS-routed).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rig_lattice.lattice.bms import BMS_BUDGET_USD, BMSResult, compute_bms
from rig_lattice.lattice.constants import (
    ARCHETYPE_MAP,
    BMS_COST_BAND,
    BMS_DOCTRINE,
    DIAMOND_OWNS,
    DIAMONDS,
    LEVELS,
    STEPS,
    BMSMode,
    Diamond,
    IQRSQPIStep,
    Level,
)

# ═══════════════════════════════════════════════════════════════════════════
# LATTICE CELL — 147 legacy-shape cells (7L x 3D x 7 steps), 588 with the
# BMS axis made explicit.
# ═══════════════════════════════════════════════════════════════════════════

_FULL_RE = re.compile(r"^L([1-7])-(D[1-3])-(A[1-4])-(I1|Q1|R|S|Q2|P|I2)$")
_SHORT_RE = re.compile(r"^L([1-7])-(D[1-3])-(I1|Q1|R|S|Q2|P|I2)$")


@dataclass(frozen=True)
class LatticeCell:
    level: Level
    diamond: Diamond
    step: IQRSQPIStep
    mode: BMSMode = BMSMode.A1

    @property
    def cell_id(self) -> str:
        """147-cell (legacy) shape, BMS axis implicit: L2-D1-S."""
        return f"{self.level.value}-{self.diamond.value}-{self.step.value}"

    @property
    def full_cell_id(self) -> str:
        """588-cell canonical shape: L2-D1-A1-S."""
        return (
            f"{self.level.value}-{self.diamond.value}-"
            f"{self.mode.value}-{self.step.value}"
        )

    @property
    def archetype_id(self) -> str:
        return ARCHETYPE_MAP[(self.mode.value, self.step.value)]

    def __str__(self) -> str:
        return f"{self.full_cell_id} -> {self.archetype_id}"

    @classmethod
    def parse(cls, cell_id: str) -> "LatticeCell":
        """Parse either shape: 588 (L2-D1-A1-S) or 147 (L2-D1-S)."""
        text = cell_id.strip()
        m = _FULL_RE.match(text)
        if m:
            return cls(
                level=Level(f"L{m.group(1)}"),
                diamond=Diamond(m.group(2)),
                mode=BMSMode(m.group(3)),
                step=IQRSQPIStep(m.group(4)),
            )
        m = _SHORT_RE.match(text)
        if m:
            return cls(
                level=Level(f"L{m.group(1)}"),
                diamond=Diamond(m.group(2)),
                step=IQRSQPIStep(m.group(3)),
            )
        raise ValueError(
            f"Invalid cell ID: {cell_id!r}. Expected L{{1-7}}-D{{1-3}}-A{{1-4}}"
            f"-{{step}} (588) or L{{1-7}}-D{{1-3}}-{{step}} (147)"
        )


def get_all_cells() -> list[LatticeCell]:
    """All 147 legacy-shape cells: 7 levels x 3 diamonds x 7 steps."""
    return [
        LatticeCell(level=lv, diamond=dm, step=st)
        for lv in LEVELS
        for dm in DIAMONDS
        for st in STEPS
    ]


def get_all_588_cells() -> list[LatticeCell]:
    """All 588 cells: 7 x 3 x 4 x 7."""
    return [
        LatticeCell(level=lv, diamond=dm, step=st, mode=md)
        for lv in LEVELS
        for dm in DIAMONDS
        for md in BMSMode
        for st in STEPS
    ]


# ═══════════════════════════════════════════════════════════════════════════
# BUILD CARD
# ═══════════════════════════════════════════════════════════════════════════

TOOLS_BY_MODE: dict[str, list[str]] = {
    "A1": ["regex", "dataclasses", "pure_functions", "sha256"],
    "A2": ["regex", "small_llm_shim", "schema_validation", "python_gate"],
    "A3": ["agent_runtime", "tool_allowlist", "cost_budget", "mechanism_map"],
    "A4": ["adversarial_review", "falsifier", "brier_eval", "human_gate"],
}

VALIDATION_BY_MODE: dict[str, list[str]] = {
    "A1": ["rule_gates", "schema_validation", "sha256_audit"],
    "A2": ["rubric_combo", "signed_packet", "source_trace"],
    "A3": ["mechanism_map", "proof_check", "mandatory_approval", "audit_trail"],
    "A4": ["10_rubrics", "20_adversarial", "brier_score", "falsification_charter"],
}

ESCALATION_BY_MODE: dict[str, str] = {
    "A1": "A3.1",
    "A2": "A3.1",
    "A3": "A4.1",
    "A4": "A4.1",
}


@dataclass(frozen=True)
class BuildCard:
    cell_id: str
    full_cell_id: str
    level: int
    diamond: str
    step: str
    step_name: str
    mode: str
    archetype_id: str
    cost_band: str
    budget_usd: float
    doctrine: str
    tools: tuple[str, ...] = ()
    validation_criteria: tuple[str, ...] = ()
    escalation_target: str = ""
    bms_score: float = 0.5
    approval_required: bool = False

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "full_cell_id": self.full_cell_id,
            "level": self.level,
            "diamond": self.diamond,
            "step": self.step,
            "step_name": self.step_name,
            "mode": self.mode,
            "archetype_id": self.archetype_id,
            "cost_band": self.cost_band,
            "budget_usd": self.budget_usd,
            "doctrine": self.doctrine,
            "tools": list(self.tools),
            "validation_criteria": list(self.validation_criteria),
            "escalation_target": self.escalation_target,
            "bms_score": self.bms_score,
            "approval_required": self.approval_required,
        }


def generate_build_card(cell: LatticeCell, bms: BMSResult) -> BuildCard:
    """Build the card for a cell, with the BMS result choosing the mode."""
    mode = bms.mode
    resolved = LatticeCell(
        level=cell.level, diamond=cell.diamond, step=cell.step, mode=mode
    )
    return BuildCard(
        cell_id=cell.cell_id,
        full_cell_id=resolved.full_cell_id,
        level=cell.level.ordinal,
        diamond=cell.diamond.value,
        step=cell.step.value,
        step_name=cell.step.step_name,
        mode=mode.value,
        archetype_id=resolved.archetype_id,
        cost_band=BMS_COST_BAND[mode.value],
        budget_usd=BMS_BUDGET_USD[mode.value],
        doctrine=BMS_DOCTRINE[mode.value],
        tools=tuple(TOOLS_BY_MODE[mode.value]),
        validation_criteria=tuple(VALIDATION_BY_MODE[mode.value]),
        escalation_target=ESCALATION_BY_MODE[mode.value],
        bms_score=round(bms.confidence, 4),
        approval_required=mode.approval_required,
    )


def generate_all_build_cards() -> list[BuildCard]:
    """One card per legacy-shape cell (147), mode derived from altitude."""
    return [
        generate_build_card(cell, compute_bms(level=cell.level))
        for cell in get_all_cells()
    ]


def get_build_card(cell_id: str) -> BuildCard:
    cell = LatticeCell.parse(cell_id)
    return generate_build_card(cell, compute_bms(level=cell.level))


# ═══════════════════════════════════════════════════════════════════════════
# ARCHETYPE DISPATCH
# ═══════════════════════════════════════════════════════════════════════════

def archetype_runner(mode: BMSMode | str):
    """Return the vendored archetype ``run`` entry point for a BMS mode.

    A1 and A2 are implemented. A3 is not: it needs a bounded agent runtime
    (state graph, tool allowlist, cost budget) that this stdlib-only bundle
    deliberately does not carry. Rather than silently running the A1
    deterministic path and reporting an A3 result — the failure mode in the
    vendored source — this raises. Escalate to the A4 human gate instead.
    """
    m = BMSMode(mode)
    if m is BMSMode.A1:
        from rig_lattice.archetypes.a1_python_only.run import A1Pipeline

        return A1Pipeline
    if m is BMSMode.A2:
        from rig_lattice.archetypes.a2_hybrid import run as a2_run

        return a2_run
    if m is BMSMode.A3:
        raise NotImplementedError(
            "A3 requires an agent runtime; escalate to A4 human gate"
        )
    raise NotImplementedError(
        "A4 LLM_AGENT_FREE is a human decision path — route to the approval "
        "gate (rig_lattice.deviator.pipeline.approval_client), not to a runner"
    )


# ═══════════════════════════════════════════════════════════════════════════
# QUALITY GATES
# ═══════════════════════════════════════════════════════════════════════════

class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class QualityGate:
    name: str
    status: GateStatus
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
        }


@dataclass(frozen=True)
class GateResult:
    cell_id: str
    step: str
    mode: str
    gates: tuple[QualityGate, ...] = ()
    overall: GateStatus = GateStatus.UNKNOWN

    @property
    def passed(self) -> bool:
        return self.overall in (GateStatus.PASS, GateStatus.SKIPPED)

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "step": self.step,
            "mode": self.mode,
            "overall": self.overall.value,
            "passed": self.passed,
            "gates": [g.to_dict() for g in self.gates],
        }


def run_quality_gates(cell: LatticeCell, output: dict[str, Any]) -> GateResult:
    """Run the per-cell quality gates on an execution output."""
    status = output.get("status", "UNKNOWN")
    gates: list[QualityGate] = [
        QualityGate(
            name="execution_complete",
            status=GateStatus.PASS if status == "PASS" else GateStatus.FAIL,
            message=f"Execution status: {status}",
        ),
        QualityGate(
            name="no_errors",
            status=GateStatus.FAIL if "error" in output else GateStatus.PASS,
            message=output.get("error", "No errors"),
        ),
    ]

    has_content = bool(
        output.get("rationale")
        or output.get("recommendation")
        or output.get("options")
    )
    gates.append(
        QualityGate(
            name="output_has_content",
            status=GateStatus.PASS if has_content else GateStatus.WARN,
            message=(
                "Output contains substantive content"
                if has_content
                else "Output may be thin"
            ),
        )
    )

    # A1 never guesses — an UNKNOWN in the deterministic band must escalate.
    if cell.mode is BMSMode.A1 and status == "UNKNOWN":
        gates.append(
            QualityGate(
                name="a1_no_guess",
                status=GateStatus.FAIL,
                message="A1 returned UNKNOWN — must escalate, not guess",
            )
        )

    overall = GateStatus.PASS
    if any(g.status is GateStatus.FAIL for g in gates):
        overall = GateStatus.FAIL
    elif any(g.status is GateStatus.WARN for g in gates):
        overall = GateStatus.WARN

    return GateResult(
        cell_id=cell.cell_id,
        step=cell.step.step_name,
        mode=cell.mode.value,
        gates=tuple(gates),
        overall=overall,
    )


# ═══════════════════════════════════════════════════════════════════════════
# DETERMINISTIC INTENT ROUTING — text -> lattice cell
# ═══════════════════════════════════════════════════════════════════════════

# Keyword sets are derived from constants.DIAMOND_OWNS, not from the dropped
# STRATEGY/INTELLIGENCE/OPERATIONS labels. D1 owns physical execution, D2 owns
# reasoning and doctrine, D3 owns adaptive/cyclical behavior.
DIAMOND_KEYWORDS: dict[str, tuple[str, ...]] = {
    "D1": (
        "operations", "asset", "logistics", "facility", "device", "payment",
        "inventory", "scheduling", "infrastructure", "supply chain",
        "manufacturing", "deployment", "procurement", "vendor", "process",
        "automation", "throughput", "fulfillment", "hardware",
    ),
    "D2": (
        "classification", "research", "synthesis", "reasoning", "doctrine",
        "strategy", "analysis", "market entry", "go-to-market", "gtm",
        "positioning", "pricing", "competitive", "due diligence", "insight",
        "benchmark", "intelligence", "discovery", "taxonomy", "knowledge",
    ),
    "D3": (
        "feedback loop", "cycle", "regeneration", "resilience", "behavior",
        "ecological", "adaptation", "emergent", "retention", "churn",
        "compounding", "flywheel", "seasonality", "recovery", "homeostasis",
    ),
}

_COMPLEXITY_UP: dict[str, int] = {
    "agentic": 4, "multi-agent": 4, "autonomous": 4, "llm": 4, "ai-native": 4,
    "cross-border": 3, "multi-jurisdiction": 3, "regulatory": 3, "complex": 3,
    "novel": 3, "doctrine": 3,
    "workflow": 1, "pipeline": 1, "integration": 1, "branch": 1,
}
_COMPLEXITY_DOWN: dict[str, int] = {
    "one-time": -2, "simple": -2, "straightforward": -2, "basic": -2,
    "deterministic": -2, "repeatable": -2, "mechanical": -2,
}


@dataclass(frozen=True)
class RouteResult:
    intent: str
    diamond: str
    level: str
    mode: str
    cell_id: str
    archetype: str
    primary_coordinate: str
    step: str
    bms_score: float
    budget_usd: float
    approval_required: bool
    deterministic: bool
    rationale: str
    evidence_keywords: tuple[str, ...] = ()
    cell_ids: tuple[str, ...] = field(default=())

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "cell_id": self.cell_id,
            "primary_coordinate": self.primary_coordinate,
            "level": self.level,
            "diamond": self.diamond,
            "mode": self.mode,
            "step": self.step,
            "archetype": self.archetype,
            "bms_score": self.bms_score,
            "budget_usd": self.budget_usd,
            "approval_required": self.approval_required,
            "deterministic": self.deterministic,
            "rationale": self.rationale,
            "evidence_keywords": list(self.evidence_keywords),
            "cell_ids": list(self.cell_ids),
        }


def _matches(text: str, keywords) -> list[str]:
    lower = text.lower()
    return [k for k in keywords if k.lower() in lower]


def route_intent(
    intent: str,
    *,
    step: IQRSQPIStep | str = IQRSQPIStep.I1,
    domain: str = "",
    failure_cost: float = 0.5,
    reversibility: float = 0.5,
    mechanism_clarity: float = 0.5,
) -> RouteResult:
    """Route free text to a lattice cell. Pure keyword rules, no model.

    Diamond comes from ``DIAMOND_KEYWORDS`` hit counts (ties resolve to D2,
    the reasoning plane, because an unclassified request is a thinking problem
    before it is an execution problem). Level comes from complexity keywords.
    Mode comes from ``compute_bms`` at that level.
    """
    step_enum = step if isinstance(step, IQRSQPIStep) else IQRSQPIStep(step)
    text = f"{intent} {domain}"

    hits = {d: _matches(text, kws) for d, kws in DIAMOND_KEYWORDS.items()}
    counts = {d: len(v) for d, v in hits.items()}
    best = max(counts.values())
    diamond = "D2" if best == 0 else min(d for d, c in counts.items() if c == best)

    score = 3  # neutral -> L3
    for kw, delta in _COMPLEXITY_UP.items():
        if kw in text.lower():
            score += delta
    for kw, delta in _COMPLEXITY_DOWN.items():
        if kw in text.lower():
            score += delta
    level_ordinal = max(1, min(7, score))
    level = Level(f"L{level_ordinal}")

    bms = compute_bms(
        failure_cost=failure_cost,
        reversibility=reversibility,
        mechanism_clarity=mechanism_clarity,
        level=level,
    )
    cell = LatticeCell(
        level=level, diamond=Diamond(diamond), step=step_enum, mode=bms.mode
    )
    return RouteResult(
        intent=intent,
        diamond=diamond,
        level=level.value,
        mode=bms.mode.value,
        cell_id=cell.full_cell_id,
        archetype=cell.archetype_id,
        primary_coordinate=(
            f"{level.value}-{diamond}-{bms.mode.value}"
        ),
        step=step_enum.value,
        bms_score=round(bms.confidence, 4),
        budget_usd=BMS_BUDGET_USD[bms.mode.value],
        approval_required=bms.mode.approval_required,
        deterministic=bms.mode.deterministic,
        rationale=(
            f"diamond {diamond} ({counts[diamond]} keyword hits, owns: "
            f"{DIAMOND_OWNS[diamond].split(',')[0].strip()}); "
            f"complexity score {score} -> {level.value}; "
            f"BMS {bms.confidence:.3f} -> {bms.mode.value}"
        ),
        evidence_keywords=tuple(hits[diamond]),
        cell_ids=tuple(
            LatticeCell(
                level=level, diamond=Diamond(diamond), step=s, mode=bms.mode
            ).full_cell_id
            for s in STEPS
        ),
    )


def lattice_summary() -> dict[str, Any]:
    """Card-level summary: how the 147 legacy cells distribute across modes."""
    cards = generate_all_build_cards()
    by_mode: dict[str, int] = {}
    by_level: dict[str, int] = {}
    by_diamond: dict[str, int] = {}
    for card in cards:
        by_mode[card.mode] = by_mode.get(card.mode, 0) + 1
        by_level[f"L{card.level}"] = by_level.get(f"L{card.level}", 0) + 1
        by_diamond[card.diamond] = by_diamond.get(card.diamond, 0) + 1
    return {
        "total_cells_147": len(cards),
        "total_cells_588": 588,
        "by_mode": by_mode,
        "by_level": by_level,
        "by_diamond": by_diamond,
        "by_step": {s.value: 21 for s in STEPS},
        "archetypes": 28,
        "doctrine": "7x3x4x7=588 cells, 4x7=28 archetypes",
    }


__all__ = [
    "BuildCard",
    "DIAMOND_KEYWORDS",
    "GateResult",
    "GateStatus",
    "LatticeCell",
    "QualityGate",
    "RouteResult",
    "archetype_runner",
    "generate_all_build_cards",
    "generate_build_card",
    "get_all_588_cells",
    "get_all_cells",
    "get_build_card",
    "lattice_summary",
    "route_intent",
    "run_quality_gates",
]
