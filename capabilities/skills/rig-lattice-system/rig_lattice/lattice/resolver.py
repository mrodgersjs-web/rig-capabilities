"""Resolver — map a lattice cell to its archetype + fallback routing.

The canonical cell id is::

    L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}      e.g.  L3-D2-A2-R
    Level 3 / Cognitive diamond / HYBRID / Research

``parse_cell_id`` also accepts the two legacy dialects this bundle fused and
normalizes them to the canonical shape:

    bare-digit diamond (rig-monorepo)   L3-2-A2-R
    dotted             (rig-deviator)   intent.D1_physical.A1.intent

Every one of the 588 execution cells resolves to exactly one of the 28
reusable archetypes (4 BMS modes x 7 IQRSQPI steps).
"""

from __future__ import annotations

from dataclasses import dataclass

from rig_lattice.lattice.constants import (
    ACCEPTED_CELL_ID_SHAPES,
    ARCHETYPE_MAP,
    BMS_APPROVAL,
    BMS_COST_BAND,
    BMS_NAME,
    BMS_THRESHOLD_EXPR,
    CELL_ID_PATTERN_BARE_DIAMOND,
    CELL_ID_PATTERN_DOTTED,
    CELL_ID_PATTERN_STRICT,
    DIAMOND_FROM_DIGIT,
    DIAMOND_PLANE,
    OLD_CELL_ID_PATTERN,
    STEP_ALIASES,
    STEP_NAME,
    FALLBACK_MAP,
    BMSMode,
)


@dataclass(frozen=True)
class CellCoordinate:
    level: str      # "L3"
    diamond: str    # "D2"  (canonical, D-prefixed)
    mode: str       # "A2"
    step: str       # "R"

    @property
    def cell_id(self) -> str:
        """Canonical id: L3-D2-A2-R."""
        return f"{self.level}-{self.diamond}-{self.mode}-{self.step}"

    @property
    def primary_coordinate(self) -> str:
        """The 3-axis coordinate without the process step: L3-D2-A2."""
        return f"{self.level}-{self.diamond}-{self.mode}"

    @property
    def filename(self) -> str:
        """Vendored cell-contract filename, which uses the bare-digit dialect."""
        digit = self.diamond[1:]
        return f"{self.level}-{digit}-{self.mode}-{self.step}.yaml"

    @property
    def is_a1(self) -> bool:
        return self.mode == "A1"

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "primary_coordinate": self.primary_coordinate,
            "level": self.level,
            "diamond": self.diamond,
            "mode": self.mode,
            "step": self.step,
        }


@dataclass(frozen=True)
class ResolvedCell:
    coordinate: CellCoordinate
    archetype: str                   # "A2.3"
    fallback_archetype: str | None   # "A3.A2.3", or None for A4
    diamond_plane: str               # "Cognitive"
    step_name: str                   # "Research"
    bms_name: str                    # "HYBRID"
    bms_threshold: str               # "0.45-0.74"
    cost_band: str                   # "$0.05"
    approval: str                    # "conditional" | "mandatory"
    deterministic: bool
    model_in_decision_path: bool
    approval_required: bool
    escalation_policy: str = "UNKNOWN_OR_LOW_CONFIDENCE"

    def to_dict(self) -> dict:
        return {
            **self.coordinate.to_dict(),
            "archetype": self.archetype,
            "fallback_archetype": self.fallback_archetype,
            "diamond_plane": self.diamond_plane,
            "step_name": self.step_name,
            "bms_name": self.bms_name,
            "bms_threshold": self.bms_threshold,
            "cost_band": self.cost_band,
            "approval": self.approval,
            "deterministic": self.deterministic,
            "model_in_decision_path": self.model_in_decision_path,
            "approval_required": self.approval_required,
            "escalation_policy": self.escalation_policy,
        }


def normalize_step(text: str) -> str:
    """Normalize a step token to its canonical code (I1/Q1/R/S/Q2/P/I2)."""
    raw = text.strip()
    if raw in STEP_NAME:
        return raw
    upper = raw.upper()
    if upper in STEP_NAME:
        return upper
    if upper in STEP_ALIASES:
        return STEP_ALIASES[upper]
    raise ValueError(
        f"Unknown IQRSQPI step {text!r}; expected one of "
        f"{sorted(STEP_NAME)} or an alias {sorted(STEP_ALIASES)}"
    )


def _invalid(cell_id: str, extra: str = "") -> ValueError:
    shapes = "\n  ".join(ACCEPTED_CELL_ID_SHAPES)
    tail = f"\n{extra}" if extra else ""
    return ValueError(
        f"Invalid cell_id {cell_id!r}. Accepted shapes:\n  {shapes}{tail}"
    )


def parse_cell_id(cell_id: str) -> CellCoordinate:
    """Parse any accepted dialect into a canonical CellCoordinate.

    Raises ValueError naming the three accepted shapes on anything else.
    """
    if not isinstance(cell_id, str):
        raise _invalid(str(cell_id))
    text = cell_id.strip()

    # canonical — L3-D2-A2-R
    m = CELL_ID_PATTERN_STRICT.match(text)
    if m:
        level, diamond, mode, step = m.groups()
        return CellCoordinate(
            level=f"L{level}",
            diamond=f"D{diamond}",
            mode=f"A{mode}",
            step=normalize_step(step),
        )

    # alias — bare-digit diamond, L3-2-A2-R
    m = CELL_ID_PATTERN_BARE_DIAMOND.match(text)
    if m:
        return CellCoordinate(
            level=m.group("level"),
            diamond=DIAMOND_FROM_DIGIT[m.group("diamond")],
            mode=m.group("mode"),
            step=normalize_step(m.group("step")),
        )

    # alias — dotted, intent.D1_physical.A1.intent
    m = CELL_ID_PATTERN_DOTTED.match(text)
    if m:
        head = m.group("head")
        # The dotted dialect carries no level; the head names the step and the
        # level defaults to L1 only when the head itself is a step token.
        try:
            step = normalize_step(m.group("step"))
        except ValueError:
            step = normalize_step(head)
        return CellCoordinate(
            level="L1",
            diamond=f"D{m.group('diamond')}",
            mode=f"A{m.group('mode')}",
            step=step,
        )

    if OLD_CELL_ID_PATTERN.match(text):
        raise _invalid(
            text,
            "This is the pre-Z-axis shape (no BMS mode). The Z-axis is BMS "
            "confidence, not IQRSQPI — add the A{1-4} segment.",
        )
    raise _invalid(text)


def is_valid_cell_id(cell_id: str) -> bool:
    """True when parse_cell_id accepts the input."""
    try:
        parse_cell_id(cell_id)
        return True
    except ValueError:
        return False


def is_old_format(cell_id: str) -> bool:
    """True for the rejected pre-Z-axis shape (L2-D1-Intent)."""
    return bool(OLD_CELL_ID_PATTERN.match(cell_id.strip()))


def resolve(cell_id: str) -> ResolvedCell:
    """Resolve any accepted cell-id dialect -> archetype + routing metadata."""
    return resolve_coordinate(parse_cell_id(cell_id))


def resolve_coordinate(coord: CellCoordinate) -> ResolvedCell:
    archetype = ARCHETYPE_MAP[(coord.mode, coord.step)]
    fb_mode = FALLBACK_MAP[coord.mode]
    fallback = f"{fb_mode}.{archetype}" if fb_mode else None
    mode = BMSMode(coord.mode)
    return ResolvedCell(
        coordinate=coord,
        archetype=archetype,
        fallback_archetype=fallback,
        diamond_plane=DIAMOND_PLANE[coord.diamond],
        step_name=STEP_NAME[coord.step],
        bms_name=BMS_NAME[coord.mode],
        bms_threshold=BMS_THRESHOLD_EXPR[coord.mode],
        cost_band=BMS_COST_BAND[coord.mode],
        approval=BMS_APPROVAL[coord.mode],
        deterministic=mode.deterministic,
        model_in_decision_path=mode.model_in_decision_path,
        approval_required=mode.approval_required,
    )


if __name__ == "__main__":  # pragma: no cover
    demo = resolve("L3-D2-A2-R")
    print(
        f"{demo.coordinate.cell_id} -> archetype {demo.archetype} "
        f"(fallback {demo.fallback_archetype}) | "
        f"{demo.diamond_plane}/{demo.step_name}/{demo.bms_name} "
        f"@ {demo.cost_band} approval={demo.approval}"
    )
