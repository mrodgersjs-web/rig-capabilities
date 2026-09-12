"""BMS scorer — deterministic confidence -> Build Mode (A1..A4).

The Z-axis of the RIG 3D Lattice is BMS confidence, NOT IQRSQPI.
A confidence score in [0.0, 1.0] maps to exactly one mode:

    A1  PYTHON_ONLY     >= 0.75   deterministic, no model in decision path
    A2  HYBRID          0.45-0.74 python-gated LLM assist
    A3  AGENT_BOUNDED   0.25-0.44 bounded agent runtime, mandatory approval
    A4  LLM_AGENT_FREE  < 0.25    adversarial, model-free decision path,
                                  mandatory human approval

The thresholds are sharp and reproducible — the same input always yields the
same mode. No floating ambiguity at boundaries: 0.75 is A1, 0.45 is A2,
0.25 is A3, anything below 0.25 is A4.

Two entry points (this module is the EVIDENCE-GATED eligibility scorer;
heuristic routing lives in ``wire`` and never produces a BMSResult):

``_evaluate(confidence)`` (private): confidence -> mode + doctrine.
    Reached only from ``compute_bms``; there is no public receipt-free path.

``compute_bms(failure_cost=, reversibility=, mechanism_clarity=,
              past_failure_rate=, data_volume=, level=)``
    You have ALL criteria receipts and want the number computed. Every
    scalar is REQUIRED: absent evidence raises ``BMSEvidenceMissing``
    (UNKNOWN, C24-BLOCKED per scoring-contract). Scoring for
    eligibility from fabricated defaults is the defect this API exists
    to refuse (scoring-contract fail-closed rule, verifier gap G9):

        raw   = (1 - failure_cost)*0.4 + reversibility*0.3 + mechanism_clarity*0.3
        final = clamp(raw - past_failure_rate*0.2
                          + (data_volume - 0.5)*0.1
                          + ALTITUDE_BONUS[level], 0.0, 1.0)
        mode  = BMSMode.from_score(final)


"""

from __future__ import annotations

from dataclasses import dataclass

from rig_lattice.lattice.constants import (
    ALTITUDE_BONUS,
    BMS_APPROVAL,
    BMS_COST_BAND,
    BMS_NAME,
    BMS_THRESHOLD_EXPR,
    BMSMode,
    Level,
)

# Per-mission USD budget per mode. A1 spends nothing because no model is in
# the decision path; A4 spends nothing because the decision is a human gate,
# not a model call. Source: rig-deviator system/orchestrator.py.
BMS_BUDGET_USD: dict[str, float] = {
    "A1": 0.00,
    "A2": 0.10,
    "A3": 0.50,
    "A4": 0.00,
}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _check_unit(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be a number in [0,1], got {value!r}")
    if not (0.0 <= float(value) <= 1.0):
        raise ValueError(f"{name} must be in [0,1], got {value!r}")
    return float(value)


@dataclass(frozen=True)
class BMSResult:
    confidence: float
    mode: BMSMode
    mode_name: str                # "PYTHON_ONLY"
    threshold: str                # ">=0.75"
    cost_band: str                # "$0.001"
    approval: str                 # "conditional" | "mandatory"
    deterministic: bool           # True only for A1
    model_in_decision_path: bool  # False only for A1
    approval_required: bool       # True for A3/A4
    budget_usd: float = 0.0
    raw: float | None = None
    adj_failure: float = 0.0
    adj_volume: float = 0.0
    adj_altitude: float = 0.0
    level: str | None = None

    def to_dict(self) -> dict:
        return {
            "confidence": round(self.confidence, 6),
            "mode": self.mode.value,
            "mode_name": self.mode_name,
            "threshold": self.threshold,
            "cost_band": self.cost_band,
            "budget_usd": self.budget_usd,
            "approval": self.approval,
            "deterministic": self.deterministic,
            "model_in_decision_path": self.model_in_decision_path,
            "approval_required": self.approval_required,
            "level": self.level,
            "raw": None if self.raw is None else round(self.raw, 6),
            "adjustments": {
                "past_failure": round(self.adj_failure, 6),
                "data_volume": round(self.adj_volume, 6),
                "altitude": round(self.adj_altitude, 6),
            },
        }


def score_to_mode(confidence: float) -> BMSMode:
    """Deterministic confidence -> BMSMode. Sharp thresholds."""
    _check_unit("confidence", confidence)
    return BMSMode.from_score(float(confidence))


def _evaluate(confidence: float, **detail: object) -> BMSResult:
    """Private: confidence -> mode + execution doctrine. Only compute_bms
    may call this; a bare confidence alone never yields an eligibility result."""
    mode = score_to_mode(confidence)
    v = mode.value
    return BMSResult(
        confidence=float(confidence),
        mode=mode,
        mode_name=BMS_NAME[v],
        threshold=BMS_THRESHOLD_EXPR[v],
        cost_band=BMS_COST_BAND[v],
        approval=BMS_APPROVAL[v],
        deterministic=mode.deterministic,
        model_in_decision_path=mode.model_in_decision_path,
        approval_required=mode.approval_required,
        budget_usd=BMS_BUDGET_USD[v],
        **detail,  # type: ignore[arg-type]
    )


def raw_score(
    failure_cost: float,
    reversibility: float,
    mechanism_clarity: float,
) -> float:
    """The unadjusted weighted criteria score. All three criteria are
    REQUIRED — there are no defaults (fail-closed scoring contract).

    failure_cost enters as its complement: higher consequence of failure
    means LOWER confidence in autonomous mode. A defect regression (2026-09
    S08) previously used +failure_cost and routed max-consequence work to A1;
    tests/test_bms_monotonicity.py guards the sign permanently.
    """
    fc = _check_unit("failure_cost", failure_cost)
    rv = _check_unit("reversibility", reversibility)
    mc = _check_unit("mechanism_clarity", mechanism_clarity)
    return (1.0 - fc) * 0.4 + rv * 0.3 + mc * 0.3


class BMSEvidenceMissing(ValueError):
    """Absent evidence is UNKNOWN (C24-BLOCKED), never a fabricated default."""


def compute_bms(
    failure_cost: float | None = None,
    reversibility: float | None = None,
    mechanism_clarity: float | None = None,
    past_failure_rate: float | None = None,
    data_volume: float | None = None,
    level: str | Level | None = None,
) -> BMSResult:
    """Criteria -> adjusted confidence -> mode, with every term reported.

    Every scalar is REQUIRED (fail-closed scoring contract): an absent
    receipt is UNKNOWN evidence and raises BMSEvidenceMissing naming the
    field — never silently scored at 0.5/0.0/L2. The old defaults turned
    zero evidence into confidence 0.78 / mode A1 (verifier gap G9); the
    exact repro is frozen in tests/test_lattice_math.py."""
    missing = [name for name, val in (
        ("failure_cost", failure_cost), ("reversibility", reversibility),
        ("mechanism_clarity", mechanism_clarity),
        ("past_failure_rate", past_failure_rate),
        ("data_volume", data_volume), ("level", level),
    ) if val is None]
    if missing:
        raise BMSEvidenceMissing(
            f"no receipt for BMS scalars {missing}; absent evidence is "
            "UNKNOWN, never a default")
    lv = Level(level) if not isinstance(level, Level) else level
    raw = raw_score(failure_cost, reversibility, mechanism_clarity)
    adj_failure = -_check_unit("past_failure_rate", past_failure_rate) * 0.2
    adj_volume = (_check_unit("data_volume", data_volume) - 0.5) * 0.1
    adj_altitude = ALTITUDE_BONUS[lv.value]
    final = _clamp01(raw + adj_failure + adj_volume + adj_altitude)
    return _evaluate(
        final,
        raw=raw,
        adj_failure=adj_failure,
        adj_volume=adj_volume,
        adj_altitude=adj_altitude,
        level=lv.value,
    )




if __name__ == "__main__":  # pragma: no cover
    for c in (0.92, 0.75, 0.60, 0.45, 0.30, 0.25, 0.10):
        r = _evaluate(c)
        print(
            f"conf={c:>4}  -> {r.mode.value} {r.mode_name:<14} "
            f"{r.threshold:<10} {r.cost_band:<8} approval={r.approval} "
            f"deterministic={r.deterministic}"
        )
