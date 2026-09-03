"""Generator — the 588 RIG 3D Lattice execution cells.

Read side (runtime, stdlib only)::

    all_cells()            -> 588 canonical cell ids
    primary_coordinates()  -> 84 primary coordinates (no process step)
    archetypes()           -> 28 archetype ids
    load_cell(cell_id)     -> the vendored cell contract as a dict

Write side (developer tool, needs PyYAML)::

    generate_all(out_dir)  -> re-emit the 588 cell contracts

Cell contracts are stored under ``lattice/cells/`` using the bare-digit
diamond dialect (``L1-1-A1-I1.yaml``) because that is how the 588 files were
generated in the source monorepo. The files are NOT renamed; ``load_cell``
maps a canonical id onto its filename.

At runtime ``load_cell`` reads the compiled ``cells.json`` index produced by
``scripts/compile_criteria.py`` so the A1 path has no third-party dependency.
It falls back to PyYAML (with a one-time warning) when the index is stale or
missing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rig_lattice._paths import CELLS_DIR
from rig_lattice.lattice.constants import (
    ARCHETYPE_MAP,
    BMS_APPROVAL,
    BMS_COST_BAND,
    BMS_NAME,
    BMS_THRESHOLD_EXPR,
    DIAMOND_DIGIT,
    DIAMOND_OWNS,
    DIAMOND_PLANE,
    DIAMONDS,
    FALLBACK_MAP,
    IQRSQPI_SEQUENCE,
    LEVELS,
    MODES,
    N_ARCHETYPES,
    N_CELLS,
    N_PRIMARY_COORDS,
    STEP_NAME,
    STEP_PURPOSE,
    STEPS,
    BMSMode,
)
from rig_lattice.lattice.resolver import CellCoordinate, parse_cell_id

DEFAULT_OUT_DIR = CELLS_DIR
CELLS_INDEX = CELLS_DIR.parent / "cells.json"

_YAML_WARNED = False


# --------------------------------------------------------------------------- #
# Read side
# --------------------------------------------------------------------------- #
def all_cells() -> tuple[str, ...]:
    """All 588 canonical cell ids, in generation order."""
    out: list[str] = []
    for level in LEVELS:
        for diamond in DIAMONDS:
            for mode in MODES:
                for step in STEPS:
                    out.append(
                        f"{level.value}-{diamond.value}-{mode.value}-{step.value}"
                    )
    return tuple(out)


def primary_coordinates() -> tuple[str, ...]:
    """The 84 primary coordinates (level x diamond x mode)."""
    return tuple(
        f"{level.value}-{diamond.value}-{mode.value}"
        for level in LEVELS
        for diamond in DIAMONDS
        for mode in MODES
    )


def archetypes() -> tuple[str, ...]:
    """The 28 reusable archetype ids (mode.step-index)."""
    return tuple(
        ARCHETYPE_MAP[(mode.value, step.value)]
        for mode in MODES
        for step in STEPS
    )


def cell_path(cell_id: str) -> Path:
    """Filesystem path of a cell contract, from any accepted dialect."""
    return CELLS_DIR / parse_cell_id(cell_id).filename


def load_cell(cell_id: str) -> dict:
    """Load one vendored cell contract as a dict.

    Prefers the compiled JSON index; falls back to PyYAML on the individual
    file. Raises RuntimeError when neither source is usable.
    """
    global _YAML_WARNED
    coord = parse_cell_id(cell_id)

    if CELLS_INDEX.exists():
        index = _cells_index()
        card = index.get(coord.cell_id) or index.get(coord.filename[:-5])
        if card is not None:
            return card

    path = CELLS_DIR / coord.filename
    if not path.exists():
        raise RuntimeError(f"cell contract missing: {path}")
    try:
        import yaml  # noqa: PLC0415 — optional, dev-time only
    except ImportError as exc:  # pragma: no cover - depends on host env
        raise RuntimeError(
            f"{CELLS_INDEX.name} missing and PyYAML unavailable — run "
            "scripts/compile_criteria.py to compile the cell contracts"
        ) from exc
    if not _YAML_WARNED:
        _YAML_WARNED = True
        print(
            f"warning: {CELLS_INDEX.name} missing or stale; reading cell "
            "contracts through PyYAML. Run scripts/compile_criteria.py.",
            file=sys.stderr,
        )
    return yaml.safe_load(path.read_text())


def _cells_index() -> dict[str, dict]:
    if not hasattr(_cells_index, "_cache"):
        _cells_index._cache = json.loads(CELLS_INDEX.read_text())  # type: ignore[attr-defined]
    return _cells_index._cache  # type: ignore[attr-defined,no-any-return]


# --------------------------------------------------------------------------- #
# Write side (developer tool)
# --------------------------------------------------------------------------- #
def build_card(level, diamond, mode, step) -> dict:
    """Construct the build-card dict for one (L, D, mode, step) cell."""
    archetype = ARCHETYPE_MAP[(mode.value, step.value)]
    fallback_mode = FALLBACK_MAP[mode.value]
    fallback_arch = f"{fallback_mode}.{archetype}" if fallback_mode else None
    digit = DIAMOND_DIGIT[diamond.value]

    return {
        "cell_id": f"{level.value}-{digit}-{mode.value}-{step.value}",
        "coordinate": {
            "level": level.value,
            "diamond": f"{digit}_{DIAMOND_PLANE[diamond.value]}",
            "diamond_owns": DIAMOND_OWNS[diamond.value],
            "bms_mode": mode.value,
            "bms_name": BMS_NAME[mode.value],
        },
        "process": {
            "sequence": IQRSQPI_SEQUENCE,
            "step_code": step.value,
            "step_name": STEP_NAME[step.value],
            "step_purpose": STEP_PURPOSE[step.value],
        },
        "routing": {
            "archetype": archetype,
            "fallback_archetype": fallback_arch,
            "escalation_policy": "UNKNOWN_OR_LOW_CONFIDENCE",
        },
        "bms": {
            "threshold": BMS_THRESHOLD_EXPR[mode.value],
        },
        "execution": {
            "deterministic": mode == BMSMode.A1,
            "model_in_decision_path": mode != BMSMode.A1,
            "approval_required": mode in (BMSMode.A3, BMSMode.A4),
            "approval_policy": BMS_APPROVAL[mode.value],
            "audit_required": True,
            "proof_required": True,
        },
        "cost_band": BMS_COST_BAND[mode.value],
    }


def all_build_cards() -> list[dict]:
    """Every cell contract, computed rather than read. 588 dicts."""
    return [
        build_card(level, diamond, mode, step)
        for level in LEVELS
        for diamond in DIAMONDS
        for mode in MODES
        for step in STEPS
    ]


def emit_build_card(level, diamond, mode, step, out_dir: Path) -> str:
    """Write one cell's YAML build card. Returns the cell_id."""
    import yaml  # noqa: PLC0415 — developer tool only

    card = build_card(level, diamond, mode, step)
    (out_dir / f"{card['cell_id']}.yaml").write_text(
        yaml.safe_dump(card, sort_keys=False)
    )
    return card["cell_id"]


def generate_all(out_dir: Path = DEFAULT_OUT_DIR) -> int:
    """Emit all 588 cells. Returns the count written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    seen: set[str] = set()
    for level in LEVELS:
        for diamond in DIAMONDS:
            for mode in MODES:
                for step in STEPS:
                    cid = emit_build_card(level, diamond, mode, step, out_dir)
                    if cid in seen:
                        raise RuntimeError(f"Duplicate cell_id emitted: {cid}")
                    seen.add(cid)
                    count += 1
    if count != N_CELLS:
        raise RuntimeError(f"Expected {N_CELLS} cells, emitted {count}")
    return count


def summary() -> dict:
    """The lattice truth, as reported by `rig-lattice lattice summary`."""
    from rig_lattice.lattice.constants import (
        LATTICE_VERSION,
        N_DIAMONDS,
        N_LEVELS,
        N_MODES,
        N_STEPS,
    )

    return {
        "levels": N_LEVELS,
        "diamonds": N_DIAMONDS,
        "bms_modes": N_MODES,
        "steps": N_STEPS,
        "primary": N_PRIMARY_COORDS,
        "cells": N_CELLS,
        "archetypes": N_ARCHETYPES,
        "version": LATTICE_VERSION,
    }


__all__ = [
    "all_cells",
    "primary_coordinates",
    "archetypes",
    "load_cell",
    "cell_path",
    "build_card",
    "all_build_cards",
    "generate_all",
    "summary",
    "CellCoordinate",
]


if __name__ == "__main__":  # pragma: no cover
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT_DIR
    n = generate_all(out)
    print(f"Emitted {n} cells -> {out}")
