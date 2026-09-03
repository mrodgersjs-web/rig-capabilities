"""The RIG idea surface — generate, score, gate, and amplify.

Four layers, all deterministic:

``booster``      the V3.1 Master Creativity Function and its four gates
``mapelites``    the 25-niche quality-diversity grid
``asr``          the 25-question adversarial survival stack
``innovation``   the 16-framework collision catalogue (MethodologyLibrary)
``bridge``       one entry point over the builtin engine and the optional
                 private ``rig-creative-booster`` package
plus DES-squared amplification re-exported from ``rig_lattice.deviator``.

``Option`` is defined here rather than imported: the vendored bridge took it
from ``strategy_studio.core.types``, which is not part of this bundle. Only
the fields the bridge actually touches are carried.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Option:
    """A scored candidate. The subset of the Strategy Studio type in use here."""

    id: str
    title: str
    description: str = ""
    score: float = 0.0
    risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "score": round(self.score, 4),
            "risks": list(self.risks),
        }


# Imported after Option so the bridge can bind it from this module.
from rig_lattice.deviator.des2_innerloop import (  # noqa: E402
    AMP_PRODUCT_MAX,
    amplify_engine,
    brier_mae,
    record_outcome,
    record_prediction,
    verify_compound_rigor,
)
from rig_lattice.deviator.des_squared import AMP_PRODUCT, amplify  # noqa: E402
from rig_lattice.idea.asr import (  # noqa: E402
    AUTOMATED_QUESTIONS,
    MANUAL_QUESTIONS,
    QUESTIONS,
    adversarial_survival_rate,
    run_stack,
)
from rig_lattice.idea.booster import (  # noqa: E402
    ACCEPT_THRESHOLDS,
    BoosterScore,
    GateResult,
    Idea,
    acceptance_report,
    evaluate,
    final_verdict,
    run_gates,
    score_idea,
)
from rig_lattice.idea.bridge import (  # noqa: E402
    BoosterEvaluation,
    booster_available,
    build_strategy_roadmap,
    evaluate_idea,
    package_available,
)
from rig_lattice.idea.innovation import MethodologyLibrary  # noqa: E402
from rig_lattice.idea.mapelites import (  # noqa: E402
    N_NICHES,
    Elite,
    grid_coverage,
    mapelites_grid,
    mutation_operators,
)

__all__ = [
    "ACCEPT_THRESHOLDS",
    "AMP_PRODUCT",
    "AMP_PRODUCT_MAX",
    "AUTOMATED_QUESTIONS",
    "BoosterEvaluation",
    "BoosterScore",
    "Elite",
    "GateResult",
    "Idea",
    "MANUAL_QUESTIONS",
    "MethodologyLibrary",
    "N_NICHES",
    "Option",
    "QUESTIONS",
    "acceptance_report",
    "adversarial_survival_rate",
    "amplify",
    "amplify_engine",
    "booster_available",
    "brier_mae",
    "build_strategy_roadmap",
    "evaluate",
    "evaluate_idea",
    "final_verdict",
    "grid_coverage",
    "mapelites_grid",
    "mutation_operators",
    "package_available",
    "record_outcome",
    "record_prediction",
    "run_gates",
    "run_stack",
    "score_idea",
    "verify_compound_rigor",
]
