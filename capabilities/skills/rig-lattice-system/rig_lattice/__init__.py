"""RIG Lattice System — coordinate the work before you build it.

    588 cells      7 levels x 3 diamonds x 4 BMS modes x 7 IQRSQPI steps
     84 primaries  level x diamond x mode
     28 archetypes mode x step
     40 engines    20 cognitive / 10 nature / 10 physics (all 10 are gates)

Route a unit of work to an explicit cell and BMS mode before building it,
build A1-first (no model in the decision path), then let the 40 engines score
the artifact and seal a verdict. The idea surface scores candidate ideas
deterministically against the V3.1 Master Creativity Function.

Stdlib only at runtime. PyYAML is needed once, at compile time, by
``scripts/compile_criteria.py``.

    from rig_lattice import parse_cell_id, compute_bms, route_intent
    from rig_lattice import audit_all, score_idea, run_gates

CLI: ``bin/rig-lattice`` or ``python3 -m rig_lattice``.
"""

from __future__ import annotations

__version__ = "3.0.0"
LATTICE_VERSION = "3.0"

from rig_lattice._paths import (  # noqa: E402
    CELLS_DIR,
    CRITERIA_DIR,
    PKG_ROOT,
    RUNS_DIR,
    SKILL_ROOT,
)
from rig_lattice.lattice import (  # noqa: E402
    ALTITUDE_BONUS,
    ARCHETYPE_MAP,
    BMS_APPROVAL,
    BMS_BUDGET_USD,
    BMS_COST_BAND,
    BMS_NAME,
    BMS_THRESHOLD_EXPR,
    BMSMode,
    BMSResult,
    CellCoordinate,
    Diamond,
    IQRSQPIStep,
    Level,
    N_ARCHETYPES,
    N_CELLS,
    N_PRIMARY_COORDS,
    ResolvedCell,
    all_cells,
    archetypes,
    compute_bms,
    evaluate as evaluate_bms,
    is_valid_cell_id,
    load_cell,
    parse_cell_id,
    primary_coordinates,
    resolve,
    summary,
)

__all__ = [
    "ALTITUDE_BONUS",
    "ARCHETYPE_MAP",
    "BMSMode",
    "BMSResult",
    "BMS_APPROVAL",
    "BMS_BUDGET_USD",
    "BMS_COST_BAND",
    "BMS_NAME",
    "BMS_THRESHOLD_EXPR",
    "CELLS_DIR",
    "CRITERIA_DIR",
    "CellCoordinate",
    "Diamond",
    "IQRSQPIStep",
    "LATTICE_VERSION",
    "Level",
    "N_ARCHETYPES",
    "N_CELLS",
    "N_PRIMARY_COORDS",
    "PKG_ROOT",
    "RUNS_DIR",
    "ResolvedCell",
    "SKILL_ROOT",
    "__version__",
    "all_cells",
    "archetypes",
    "audit_all",
    "compute_bms",
    "evaluate_bms",
    "is_valid_cell_id",
    "load_cell",
    "parse_cell_id",
    "primary_coordinates",
    "resolve",
    "route_intent",
    "run_gates",
    "score_idea",
    "summary",
]


def __getattr__(name: str):
    """Lazy re-exports.

    The engine and idea surfaces are imported on first use so that
    ``import rig_lattice`` stays cheap and a broken optional dependency in one
    surface cannot take down the lattice core.
    """
    if name == "audit_all":
        from rig_lattice.deviator.auditor import audit_all

        return audit_all
    if name in ("score_idea", "run_gates"):
        from rig_lattice.idea import booster

        return getattr(booster, name)
    if name == "route_intent":
        from rig_lattice.lattice.wire import route_intent

        return route_intent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
