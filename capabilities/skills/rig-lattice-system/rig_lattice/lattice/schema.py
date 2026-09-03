"""Frozen lattice schema — stdlib dataclasses, no pydantic.

Vendored from strategy_studio ``lattice/_types_reexport.py``. Two changes were
load-bearing:

1. The enums are no longer redefined here. ``constants`` is the single source
   of truth; this module re-exports them so existing call sites keep working.
2. ``LatticeCoordinate`` was a ``pydantic.BaseModel``; it is now a frozen
   dataclass with the same field names, the same properties, and an explicit
   ``to_dict()``. The validation pydantic performed (enum coercion) happens in
   ``__post_init__`` and raises ``ValueError``.

The strategy_studio re-exports of ``Action``/``ActionResult``/``AuditRow``/
``InboundPayload``/``Draft``/``ResearchPack``/``StructuredQuery``/``Source``/
``QualityGateResult``/``QualityResult``/``ProofPacket``/``IntentKey`` are gone:
they lived in ``strategy_studio.core.types``, which is not part of this bundle.
The archetype contract surface at ``rig_lattice.archetypes.a1_python_only._types``
carries the equivalents that the vendored archetypes actually use.
"""

from __future__ import annotations

from dataclasses import dataclass

from rig_lattice.lattice.constants import (
    CELL_ID_PATTERN_STRICT,
    LATTICE_VERSION,
    OLD_CELL_ID_PATTERN,
    BMSMode,
    Diamond,
    IQRSQPIStep,
    Level,
)


@dataclass(frozen=True)
class LatticeCoordinate:
    """A single cell in the 7L x 3D x 4BMS lattice, plus its process step."""

    level: Level
    diamond: Diamond
    bms_mode: BMSMode
    step: IQRSQPIStep

    def __post_init__(self) -> None:
        # Coerce/validate every axis. Frozen dataclass -> object.__setattr__.
        for field_name, enum_cls in (
            ("level", Level),
            ("diamond", Diamond),
            ("bms_mode", BMSMode),
            ("step", IQRSQPIStep),
        ):
            value = getattr(self, field_name)
            if not isinstance(value, enum_cls):
                try:
                    value = enum_cls(value)
                except ValueError as exc:
                    raise ValueError(
                        f"{field_name}={getattr(self, field_name)!r} is not a "
                        f"valid {enum_cls.__name__}"
                    ) from exc
                object.__setattr__(self, field_name, value)

    @property
    def cell_id(self) -> str:
        """Full cell ID string, e.g. L2-D1-A1-I1."""
        return (
            f"{self.level.value}-{self.diamond.value}-"
            f"{self.bms_mode.value}-{self.step.value}"
        )

    @property
    def primary_coordinate(self) -> str:
        """Primary (3-axis) coordinate, e.g. L1-D1-A1."""
        return f"{self.level.value}-{self.diamond.value}-{self.bms_mode.value}"

    @property
    def is_a1(self) -> bool:
        """True if BMS mode is A1 (PYTHON_ONLY)."""
        return self.bms_mode == BMSMode.A1

    @property
    def requires_approval(self) -> bool:
        """True if the mode requires human signoff (A3, A4)."""
        return self.bms_mode.approval_required

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "primary_coordinate": self.primary_coordinate,
            "level": self.level.value,
            "diamond": self.diamond.value,
            "bms_mode": self.bms_mode.value,
            "step": self.step.value,
            "is_a1": self.is_a1,
            "requires_approval": self.requires_approval,
        }

    def __str__(self) -> str:
        return self.cell_id


@dataclass(frozen=True)
class LatticeCoord:
    """Lightweight lattice coordinate (no bms_mode required)."""

    level: Level
    diamond: Diamond
    step: IQRSQPIStep

    def __str__(self) -> str:
        return f"{self.level.value}-{self.diamond.value}-{self.step.value}"

    @property
    def cell_id(self) -> str:
        return str(self)


__all__ = [
    "BMSMode",
    "CELL_ID_PATTERN_STRICT",
    "Diamond",
    "IQRSQPIStep",
    "LATTICE_VERSION",
    "LatticeCoord",
    "LatticeCoordinate",
    "Level",
    "OLD_CELL_ID_PATTERN",
]
