"""RIG 3D Lattice — canonical constants. Single source of truth.

The corrected RIG 3D Lattice geometry:

    X-axis  Level / Altitude       L1 .. L7            (7)
    Y-axis  Triple Diamond         D1/D2/D3            (3)
    Z-axis  BMS Confidence / Mode  A1/A2/A3/A4         (4)

  7 Levels x 3 Diamonds x 4 BMS Modes        =  84 primary coordinates
 84 coordinates x 7 IQRSQPI steps            = 588 execution cells
  4 BMS Modes x 7 IQRSQPI steps              =  28 reusable archetypes

IQRSQPI is the PROCESS that runs *inside* each coordinate. It is NOT the
Z-axis — that was the correction the OpenClaw build card enforces.

Superseded: an earlier card multiplied 40 engines x 6 audience tiers x 7
steps = 1,680; engines are scorers inside a cell, not an axis.

This module fuses three prior implementations:
  - rig-monorepo platform/lattice/constants.py  (geometry doctrine, tables)
  - strategy_studio lattice/_types_reexport.py  (strict cell-id pattern,
    BMSMode.from_score, IQRSQPIStep.sequence)
  - strategy_studio lattice_wire.py             (altitude bonus)
"""

from __future__ import annotations

import re
from enum import Enum

LATTICE_VERSION = "3.0"


# --------------------------------------------------------------------------- #
# X-axis — Level / Altitude (L1 .. L7)
# --------------------------------------------------------------------------- #
class Level(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"

    @property
    def ordinal(self) -> int:
        """1..7 — the numeric altitude."""
        return int(self.value[1:])

    @property
    def description(self) -> str:
        return LEVEL_DESCRIPTION[self.value]


LEVELS: tuple[Level, ...] = tuple(Level)  # 7

LEVEL_DESCRIPTION: dict[str, str] = {
    "L1": "Direct, deterministic, repeatable",
    "L2": "Structured but parameterized",
    "L3": "Workflow with branches",
    "L4": "Bounded agentic with checkpoints",
    "L5": "Mechanism + tradeoff reasoning",
    "L6": "Strategic synthesis required",
    "L7": "Doctrine, exploration, novel frame",
}

# Altitude bonus applied to the raw BMS score. Low altitude is mechanical and
# earns determinism; high altitude is doctrine work and is pushed toward the
# agentic bands. Source: strategy_studio lattice_wire.Altitude.altitude_bonus.
ALTITUDE_BONUS: dict[str, float] = {
    "L1": 0.35,
    "L2": 0.28,
    "L3": 0.12,
    "L4": 0.0,
    "L5": -0.08,
    "L6": -0.20,
    "L7": -0.35,
}


# --------------------------------------------------------------------------- #
# Y-axis — Triple Diamond (Physical / Cognitive / Nature)
# --------------------------------------------------------------------------- #
class Diamond(str, Enum):
    """The three diamonds. Canonical serialization is the D-prefixed form."""

    D1 = "D1"  # Physical  — real-world execution
    D2 = "D2"  # Cognitive — reasoning & knowledge
    D3 = "D3"  # Nature    — adaptive / emergent

    @property
    def digit(self) -> str:
        """Bare-digit form used by the vendored cell filenames ("1".."3")."""
        return DIAMOND_DIGIT[self.value]

    @property
    def plane(self) -> str:
        """Title-case plane name as written into the cell contracts."""
        return DIAMOND_PLANE[self.value]

    @property
    def long_name(self) -> str:
        """Upper-case plane name (PHYSICAL / COGNITIVE / NATURE)."""
        return DIAMOND_PLANE[self.value].upper()


DIAMONDS: tuple[Diamond, ...] = tuple(Diamond)  # 3

DIAMOND_DIGIT: dict[str, str] = {"D1": "1", "D2": "2", "D3": "3"}
DIAMOND_FROM_DIGIT: dict[str, str] = {v: k for k, v in DIAMOND_DIGIT.items()}

DIAMOND_PLANE: dict[str, str] = {
    "D1": "Physical",
    "D2": "Cognitive",
    "D3": "Nature",
}

DIAMOND_OWNS: dict[str, str] = {
    "D1": "operations, assets, logistics, facilities, devices, payments, "
          "inventory, scheduling, infrastructure",
    "D2": "classification, research, synthesis, reasoning workflows, "
          "doctrine, strategy",
    "D3": "feedback loops, cycles, regeneration, resilience, behavior "
          "patterns, ecological metaphors",
}

TRIPLE_DIAMOND: tuple[str, str, str] = ("Physical", "Cognitive", "Nature")

# Dropped dialect. strategy_studio's lattice_wire.py labelled the Y-axis
# D1_STRATEGY / D2_INTELLIGENCE / D3_OPERATIONS. That naming is NOT the
# doctrine and is never an enum here — this lookup exists only so a reader
# of the old artifacts can map them onto the canonical planes.
LEGACY_DIAMOND_LABELS: dict[str, str] = {
    "D1": "STRATEGY",
    "D2": "INTELLIGENCE",
    "D3": "OPERATIONS",
}


# --------------------------------------------------------------------------- #
# Z-axis — BMS Confidence / Build Mode (A1 .. A4)
# --------------------------------------------------------------------------- #
class BMSMode(str, Enum):
    A1 = "A1"  # PYTHON_ONLY      >= 0.75
    A2 = "A2"  # HYBRID           0.45 - 0.74
    A3 = "A3"  # AGENT_BOUNDED    0.25 - 0.44
    A4 = "A4"  # LLM_AGENT_FREE   < 0.25

    @classmethod
    def from_score(cls, score: float) -> "BMSMode":
        """Deterministic confidence -> mode. Sharp, reproducible thresholds."""
        if score >= 0.75:
            return cls.A1
        if score >= 0.45:
            return cls.A2
        if score >= 0.25:
            return cls.A3
        return cls.A4

    @property
    def threshold_range(self) -> str:
        return BMS_THRESHOLD_EXPR[self.value]

    @property
    def description(self) -> str:
        return BMS_NAME[self.value]

    @property
    def doctrine(self) -> str:
        return BMS_DOCTRINE[self.value]

    @property
    def deterministic(self) -> bool:
        return self is BMSMode.A1

    @property
    def model_in_decision_path(self) -> bool:
        return self is not BMSMode.A1

    @property
    def approval_required(self) -> bool:
        return self in (BMSMode.A3, BMSMode.A4)


MODES: tuple[BMSMode, ...] = tuple(BMSMode)  # 4

BMS_NAME: dict[str, str] = {
    "A1": "PYTHON_ONLY",
    "A2": "HYBRID",
    "A3": "AGENT_BOUNDED",
    "A4": "LLM_AGENT_FREE",
}

BMS_DOCTRINE: dict[str, str] = {
    "A1": "A1 PYTHON_ONLY — no model in the decision path. "
          "Dataclasses, regex, pure functions.",
    "A2": "A2 HYBRID — Python gates with small LLM shims; "
          "the gate, not the model, decides.",
    "A3": "A3 AGENT_BOUNDED — bounded agent runtime with hard tool and cost "
          "budgets, mandatory human approval.",
    "A4": "A4 LLM_AGENT_FREE — adversarial, model-free decision path, "
          "mandatory human approval.",
}

# Deterministic BMS thresholds. (lo, hi) band over a confidence in [0,1].
#   A1 >= 0.75 | A2 0.45-0.74 | A3 0.25-0.44 | A4 < 0.25
BMS_THRESHOLD_BANDS: dict[str, tuple[float, float]] = {
    "A1": (0.75, 1.00),
    "A2": (0.45, 0.74),
    "A3": (0.25, 0.44),
    "A4": (0.00, 0.24),
}

# Human-readable threshold expression (used verbatim in build-card YAML)
BMS_THRESHOLD_EXPR: dict[str, str] = {
    "A1": ">=0.75",
    "A2": "0.45-0.74",
    "A3": "0.25-0.44",
    "A4": "<0.25",
}

BMS_COST_BAND: dict[str, str] = {
    "A1": "$0.001",
    "A2": "$0.05",
    "A3": "$1",
    "A4": "$50",
}

# Approval doctrine per mode: A1/A2 -> conditional, A3/A4 -> mandatory.
BMS_APPROVAL: dict[str, str] = {
    "A1": "conditional",
    "A2": "conditional",
    "A3": "mandatory",
    "A4": "mandatory",
}

# Fallback escalation chain (escalate, don't fail). A4 has nowhere higher.
FALLBACK_MAP: dict[str, str | None] = {
    "A1": "A3",
    "A2": "A3",
    "A3": "A4",
    "A4": None,
}


# --------------------------------------------------------------------------- #
# IQRSQPI — the 7-step process inside each coordinate
# --------------------------------------------------------------------------- #
class IQRSQPIStep(str, Enum):
    I1 = "I1"  # Intent
    Q1 = "Q1"  # Question
    R = "R"    # Research
    S = "S"    # Solution
    Q2 = "Q2"  # Quality
    P = "P"    # Proof
    I2 = "I2"  # Integrate

    @classmethod
    def sequence(cls) -> list["IQRSQPIStep"]:
        """Steps in canonical IQRSQPI order."""
        return [cls.I1, cls.Q1, cls.R, cls.S, cls.Q2, cls.P, cls.I2]

    @property
    def step_name(self) -> str:
        return STEP_NAME[self.value]

    @property
    def purpose(self) -> str:
        return STEP_PURPOSE[self.value]

    @property
    def index(self) -> int:
        """1..7 position in the IQRSQPI sequence."""
        return IQRSQPIStep.sequence().index(self) + 1


# The monorepo called this `Step`. Kept as an alias so vendored call sites and
# both prior dialects resolve to one enum.
Step = IQRSQPIStep

STEPS: tuple[IQRSQPIStep, ...] = tuple(IQRSQPIStep.sequence())  # 7

# Canonical ordered sequence string used in every build card.
IQRSQPI_SEQUENCE = "IQRSQPI"

STEP_NAME: dict[str, str] = {
    "I1": "Intent",
    "Q1": "Question",
    "R": "Research",
    "S": "Solution",
    "Q2": "Quality",
    "P": "Proof",
    "I2": "Integrate",
}

STEP_PURPOSE: dict[str, str] = {
    "I1": "Classify the request/event",
    "Q1": "Convert intent to operational question",
    "R": "Retrieve evidence",
    "S": "Produce artifact",
    "Q2": "Safety, grounding, mechanism, policy",
    "P": "Bind sources, gates, signer, timestamp, hash",
    "I2": "Execute / save / send / route",
}

# Step aliases accepted on input. Same semantics as
# rig_capabilities/iqrsqpi_v10.py:normalize_stage.
STEP_ALIASES: dict[str, str] = {
    "I": "I1",
    "Q": "Q1",
    "I5": "I2",
    "INTENT": "I1",
    "QUESTION": "Q1",
    "RESEARCH": "R",
    "SOLUTION": "S",
    "QUALITY": "Q2",
    "PROOF": "P",
    "INTEGRATE": "I2",
}


# --------------------------------------------------------------------------- #
# Cell-id grammar
# --------------------------------------------------------------------------- #
_STEP_ALT = "I1|Q1|R|S|Q2|P|I2"

# Canonical: L{1-7}-D{1-3}-A{1-4}-{step}
CELL_ID_PATTERN_STRICT = re.compile(
    r"^L([1-7])-D([1-3])-A([1-4])-([A-Z][0-9]?)$"
)

# Accepted alias 1 — monorepo bare-digit diamond: L1-1-A1-I1
CELL_ID_PATTERN_BARE_DIAMOND = re.compile(
    rf"^(?P<level>L[1-7])-(?P<diamond>[1-3])-(?P<mode>A[1-4])-(?P<step>{_STEP_ALT})$"
)

# Accepted alias 2 — rig-deviator dotted: intent.D1_physical.A1.intent
CELL_ID_PATTERN_DOTTED = re.compile(
    r"^(?P<head>[A-Za-z0-9_]+)\.D(?P<diamond>[1-3])_[A-Za-z]+\."
    r"A(?P<mode>[1-4])\.(?P<step>[A-Za-z0-9_]+)$"
)

# Rejected — the pre-Z-axis shape that omits the BMS mode: L2-D1-Intent
OLD_CELL_ID_PATTERN = re.compile(r"^L([1-7])-D([1-3])-([A-Za-z][A-Za-z0-9]+)$")

ACCEPTED_CELL_ID_SHAPES = (
    "canonical  L{1-7}-D{1-3}-A{1-4}-{I1|Q1|R|S|Q2|P|I2}   e.g. L3-D2-A2-R",
    "bare-digit L{1-7}-{1-3}-A{1-4}-{step}                 e.g. L3-2-A2-R",
    "dotted     <head>.D{1-3}_<plane>.A{1-4}.<step>        e.g. intent.D1_physical.A1.intent",
)


# --------------------------------------------------------------------------- #
# 28 reusable archetypes — (BMS mode, IQRSQPI step) -> archetype id
# --------------------------------------------------------------------------- #
def _build_archetype_map() -> dict[tuple[str, str], str]:
    """4 modes x 7 steps = 28 archetypes, indexed 1..7 per mode."""
    amap: dict[tuple[str, str], str] = {}
    for m in MODES:
        for idx, s in enumerate(STEPS, start=1):
            amap[(m.value, s.value)] = f"{m.value}.{idx}"
    return amap


ARCHETYPE_MAP: dict[tuple[str, str], str] = _build_archetype_map()


# --------------------------------------------------------------------------- #
# Cardinality invariants — fail fast if anyone edits the enums.
# --------------------------------------------------------------------------- #
N_LEVELS = len(LEVELS)
N_DIAMONDS = len(DIAMONDS)
N_MODES = len(MODES)
N_STEPS = len(STEPS)
N_PRIMARY_COORDS = N_LEVELS * N_DIAMONDS * N_MODES  # 84
N_CELLS = N_PRIMARY_COORDS * N_STEPS               # 588
N_ARCHETYPES = N_MODES * N_STEPS                   # 28

assert (N_LEVELS, N_DIAMONDS, N_MODES, N_STEPS) == (7, 3, 4, 7)
assert N_PRIMARY_COORDS == 84
assert N_CELLS == 588
assert N_ARCHETYPES == 28
assert len(ARCHETYPE_MAP) == 28
assert set(ALTITUDE_BONUS) == {lv.value for lv in LEVELS}
