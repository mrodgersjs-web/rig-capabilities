"""Creative Booster bridge — one entry point, two possible engines.

The RIG Creative Booster scores ideas, offers, and roadmap candidates across
novelty / appropriateness / usefulness / surprise / proof-density /
generic-penalty, then accepts, revises, or rejects them.

Two engines can answer:

``"package"``
    The private ``rig-creative-booster`` distribution, if it is importable.
    It wins when present — it carries the embedding-backed Vendi novelty and
    the real KL surprise term.

``"builtin"``
    ``rig_lattice.idea.booster`` — the deterministic V3.1 core rebuilt in this
    bundle from the build card. This is the offline default and the source of
    the gate fixtures. It is a real, discriminating scorer, not a stub.

The vendored source of this file carried a third path: a hand-tuned
weighted-sum stub with its own thresholds (``_STUB_WEIGHTS``,
``_STUB_ACCEPT_THRESHOLD``, ...) that disagreed with the build card's gates.
That is gone. A bundle with two different sets of accept thresholds cannot
tell you whether an idea passed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from rig_lattice.idea import Option
from rig_lattice.idea import asr as _asr
from rig_lattice.idea import booster as _builtin

try:  # optional private package — wins when installed
    from rig_creative_booster.formulas.master import score_idea as _pkg_score_idea
    from rig_creative_booster.gates.engine import (
        final_verdict as _pkg_final_verdict,
        run_gates as _pkg_run_gates,
    )
    from rig_creative_booster.innovation.roadmap import build_roadmap
    from rig_creative_booster.innovation.vectors import (
        headline,
        innovation_index,
        score_innovation_vectors,
    )
    from rig_creative_booster.lattice import lattice_coord
    from rig_creative_booster.models import Audience, CreativeIdeaPacket, LatticeMode
    from rig_creative_booster.proof.proofpacket import build_proof_packet
    from rig_creative_booster.questions.injection_stack import (
        adversarial_survival_rate as _pkg_asr,
    )

    _PACKAGE_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when package absent
    _PACKAGE_AVAILABLE = False


def package_available() -> bool:
    """True if the private rig-creative-booster package is importable."""
    return _PACKAGE_AVAILABLE


def booster_available() -> str:
    """Which engine answers scoring calls: ``"package"`` or ``"builtin"``."""
    return "package" if _PACKAGE_AVAILABLE else "builtin"


@dataclass(frozen=True)
class BoosterEvaluation:
    """The result of a Creative Booster evaluation, whichever engine ran."""

    engine: str  # "package" | "builtin"
    verdict: str  # "accept" | "revise" | "reject"
    creativity_score: float
    deviation_score: float
    adversarial_survival_rate: float
    innovation_index: float
    innovation_headline: str
    available: bool = True
    failed_gates: list[str] = field(default_factory=list)
    next_tests: list[str] = field(default_factory=list)
    proof_packet: dict | None = None

    def to_option(self, title: str, description: str) -> Option:
        """Map the evaluation into an :class:`Option`."""
        risks = [f"gate:{g}" for g in self.failed_gates] + list(self.next_tests)
        return Option(
            id=_idea_id(title),
            title=title,
            description=description,
            score=max(0.0, min(1.0, self.creativity_score)),
            risks=risks,
        )

    def to_dict(self) -> dict:
        return {
            "engine": self.engine,
            "verdict": self.verdict,
            "creativity_score": round(self.creativity_score, 4),
            "deviation_score": round(self.deviation_score, 4),
            "adversarial_survival_rate": round(self.adversarial_survival_rate, 4),
            "innovation_index": round(self.innovation_index, 4),
            "innovation_headline": self.innovation_headline,
            "failed_gates": list(self.failed_gates),
            "next_tests": list(self.next_tests),
        }


def _idea_id(title: str) -> str:
    """Deterministic id from the title (stable across runs)."""
    return "rig-" + hashlib.md5(title.encode("utf-8")).hexdigest()[:10]


# What to suggest when a gate fails — feeds BoosterEvaluation.next_tests.
GATE_ADVICE: dict[str, str] = {
    "anti_randomness": "anchor the novelty: name the audience and their situation",
    "generic_usefulness": "break the median: cut buzzwords, add a named mechanism",
    "theater": "back the deviation with sources, claims, and mechanisms",
    "final_acceptance": "raise the dimension(s) named in the gate reason",
}


def evaluate_idea(
    title: str,
    content: str,
    context: str = "",
    *,
    sources: list[str] | None = None,
    claims: list[str] | None = None,
    mechanisms: list[str] | None = None,
    corpus: list[str] | None = None,
    audience: str = "internal",
    cost_band: float = 0.5,
    time_to_value: float = 0.5,
) -> BoosterEvaluation:
    """Score an idea through whichever Creative Booster engine is available.

    Deterministic for a given set of inputs either way.
    """
    if _PACKAGE_AVAILABLE:
        return _evaluate_with_package(
            title, content, context,
            sources=sources, claims=claims, mechanisms=mechanisms,
            corpus=corpus, audience=audience,
        )

    idea = _builtin.Idea(
        title=title,
        content=content,
        context=context,
        sources=tuple(sources or ()),
        claims=tuple(claims or ()),
        mechanisms=tuple(mechanisms or ()),
        corpus=tuple(corpus or ()),
        cost_band=cost_band,
        time_to_value=time_to_value,
    )
    score = _builtin.score_idea(idea)
    gates = _builtin.run_gates(score)
    verdict = _builtin.final_verdict(gates)
    failed = [g.gate for g in gates if not g.passed]
    stack = _asr.run_stack(idea)

    return BoosterEvaluation(
        engine="builtin",
        available=True,
        verdict=verdict,
        creativity_score=score.creativity_score,
        deviation_score=score.deviation_score,
        adversarial_survival_rate=stack["asr"],
        innovation_index=round((score.novelty + score.surprise) / 2.0, 4),
        innovation_headline=(
            f"C={score.creativity_score:.2f} deviation={score.deviation_score:.2f} "
            f"proof={score.proof_density:.2f} generic={score.generic_penalty:.2f}"
        ),
        failed_gates=failed,
        next_tests=[GATE_ADVICE[g] for g in failed if g in GATE_ADVICE],
        proof_packet={
            "engine": "builtin",
            "idea_id": _idea_id(title),
            **score.to_dict(),
            "gates": [g.to_dict() for g in gates],
            "acceptance": _builtin.acceptance_report(score),
            "asr": {k: v for k, v in stack.items() if k != "questions"},
        },
    )


def _evaluate_with_package(
    title: str,
    content: str,
    context: str,
    *,
    sources: list[str] | None,
    claims: list[str] | None,
    mechanisms: list[str] | None,
    corpus: list[str] | None,
    audience: str,
) -> BoosterEvaluation:  # pragma: no cover - needs the private package
    idea = CreativeIdeaPacket(
        idea_id=_idea_id(title),
        title=title,
        content=content,
        context=context,
        sources=sources or [],
        claims=claims or [],
        mechanisms=mechanisms or [],
    )
    aud = Audience(audience)
    sv = _pkg_score_idea(idea, corpus or [])
    gates = _pkg_run_gates(sv, aud)
    verdict = _pkg_final_verdict(gates)
    rate, _ = _pkg_asr(idea, sv)
    vectors = score_innovation_vectors(idea, sv)
    coord = lattice_coord(level=1, diamond=1, mode=LatticeMode.A1, step="Quality")
    packet = build_proof_packet(
        idea, sv, gates, vectors, rate, audience=aud, lattice_coord=coord
    )
    return BoosterEvaluation(
        engine="package",
        available=True,
        verdict=verdict.value,
        creativity_score=sv.creativity_score,
        deviation_score=sv.deviation_score,
        adversarial_survival_rate=rate,
        innovation_index=innovation_index(vectors),
        innovation_headline=headline(vectors),
        failed_gates=[g.gate for g in gates if not g.passed],
        next_tests=list(packet.next_tests),
        proof_packet=packet.model_dump(mode="json"),
    )


def build_strategy_roadmap(
    title: str,
    content: str,
    context: str = "",
    *,
    sources: list[str] | None = None,
    claims: list[str] | None = None,
    mechanisms: list[str] | None = None,
    corpus: list[str] | None = None,
    top: int | None = None,
) -> dict | None:
    """Future-back capability roadmap for an idea.

    The 10-vector innovation roadmap is a feature of the private package. With
    only the builtin engine available this returns None rather than inventing
    a roadmap shape the rest of RIG does not consume.
    """
    if not _PACKAGE_AVAILABLE:
        return None
    idea = CreativeIdeaPacket(  # pragma: no cover - needs the private package
        idea_id=_idea_id(title), title=title, content=content, context=context,
        sources=sources or [], claims=claims or [], mechanisms=mechanisms or [],
    )
    sv = _pkg_score_idea(idea, corpus or [])
    vectors = score_innovation_vectors(idea, sv)
    roadmap = build_roadmap(idea.idea_id, title, sv, vectors, top=top)
    return roadmap.model_dump(mode="json")


__all__ = [
    "BoosterEvaluation",
    "GATE_ADVICE",
    "booster_available",
    "build_strategy_roadmap",
    "evaluate_idea",
    "package_available",
]
