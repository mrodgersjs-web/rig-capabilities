"""RIG-MAP-Elites — quality-diversity idea generation over a 25-niche grid.

Build card §4: instead of brainstorming, fill a behaviour grid and keep the
best idea in each niche.

    Axes      Novelty (5 bins) x Time-to-Value (5 bins)  = 25 niches
    Mutation  SCAMPER (7 transforms) + Synectics (4 analogies)
              + a seeded oblique pick
    Selection Keep the elite (highest C_v3 score) per niche
    Output    A menu of the best idea across the diversity landscape

The mutation operators are the transform sets already vendored in
``innovation.py`` — SCAMPER's seven verbs and Synectics' four analogies — so
the collision catalogue and the generator share one source of truth.

Determinism: ``seed`` is a required keyword argument. Every random choice
comes from ``random.Random(seed)``, never the module-level RNG and never the
clock, so two runs with the same seed and candidates replay byte-identically.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from rig_lattice.idea.booster import Idea, score_idea
from rig_lattice.idea.innovation import MethodologyLibrary

NOVELTY_BINS = 5
TTV_BINS = 5
N_NICHES = NOVELTY_BINS * TTV_BINS  # 25

# Oblique Strategies — the seeded random arm of the mutation operator set.
OBLIQUE_STRATEGIES: tuple[str, ...] = (
    "Remove the most impressive part",
    "State the constraint you have been avoiding",
    "Do the opposite of the obvious move",
    "Make it smaller until it is boring, then keep the boring part",
    "Name who this harms",
    "Ship the measurement before the feature",
    "Assume the budget is zero",
    "Assume it must run unattended for a year",
    "Explain it to the person who has to maintain it at 3am",
    "Delete the abstraction and inline the two call sites",
)


def _scamper_transforms() -> tuple[str, ...]:
    """SCAMPER's seven verbs, read from the vendored methodology catalogue."""
    lib = MethodologyLibrary()
    for m in lib.get_all():
        if m["id"] == "scamper":
            return tuple(m["steps"])
    return ()


def _synectics_transforms() -> tuple[str, ...]:
    """Synectics' analogy moves, read from the vendored catalogue."""
    lib = MethodologyLibrary()
    for m in lib.get_all():
        if m["id"] == "synectics":
            return tuple(m["steps"])
    return ()


def mutation_operators() -> tuple[str, ...]:
    """The full deterministic operator set: SCAMPER + Synectics + Oblique."""
    return _scamper_transforms() + _synectics_transforms() + OBLIQUE_STRATEGIES


def _bin_index(value: float, bins: int) -> int:
    """Map a [0,1] score onto a bin index, with 1.0 landing in the last bin."""
    idx = int(max(0.0, min(1.0, value)) * bins)
    return min(idx, bins - 1)


def niche_of(idea: Idea) -> tuple[int, int]:
    """The (novelty_bin, time_to_value_bin) niche an idea occupies."""
    score = score_idea(idea)
    return (
        _bin_index(score.novelty, NOVELTY_BINS),
        _bin_index(idea.time_to_value, TTV_BINS),
    )


def niche_label(niche: tuple[int, int]) -> str:
    return f"N{niche[0]}-T{niche[1]}"


@dataclass(frozen=True)
class Elite:
    niche: str
    title: str
    creativity_score: float
    novelty: float
    time_to_value: float
    operator: str = ""

    def to_dict(self) -> dict:
        return {
            "niche": self.niche,
            "title": self.title,
            "creativity_score": round(self.creativity_score, 4),
            "novelty": round(self.novelty, 4),
            "time_to_value": round(self.time_to_value, 4),
            "operator": self.operator,
        }


def _as_idea(candidate: Idea | dict) -> Idea:
    return candidate if isinstance(candidate, Idea) else Idea.from_mapping(candidate)


def mapelites_grid(
    candidates: list[Idea | dict],
    *,
    seed: int,
    mutations_per_candidate: int = 3,
) -> dict[str, dict]:
    """Fill the 25-niche grid and return the elite per occupied niche.

    Each candidate is scored, placed in its niche, and then mutated
    ``mutations_per_candidate`` times by operators drawn from the seeded RNG.
    A mutation records which operator produced it; it does not fabricate new
    prose, because inventing content is a model's job, not a deterministic
    grid's. The mutant inherits the candidate's fields and carries the
    operator as an appended mechanism, which is what shifts its score.

    Returns ``{niche_label: elite_dict}`` sorted by niche.
    """
    if not isinstance(seed, int):
        raise ValueError("seed must be an int — MAP-Elites runs must replay")

    rng = random.Random(seed)
    operators = mutation_operators()
    if not operators:
        raise RuntimeError(
            "no mutation operators available — innovation.py catalogue is empty"
        )

    grid: dict[tuple[int, int], Elite] = {}

    def consider(idea: Idea, operator: str) -> None:
        score = score_idea(idea)
        niche = (
            _bin_index(score.novelty, NOVELTY_BINS),
            _bin_index(idea.time_to_value, TTV_BINS),
        )
        elite = Elite(
            niche=niche_label(niche),
            title=idea.title,
            creativity_score=score.creativity_score,
            novelty=score.novelty,
            time_to_value=idea.time_to_value,
            operator=operator,
        )
        held = grid.get(niche)
        if held is None or elite.creativity_score > held.creativity_score:
            grid[niche] = elite

    for candidate in candidates:
        idea = _as_idea(candidate)
        consider(idea, "seed")
        for _ in range(mutations_per_candidate):
            operator = rng.choice(operators)
            ttv_shift = rng.choice((-0.25, -0.1, 0.0, 0.1, 0.25))
            mutant = Idea(
                title=idea.title,
                content=idea.content,
                context=idea.context,
                sources=idea.sources,
                claims=idea.claims,
                mechanisms=idea.mechanisms + (operator,),
                corpus=idea.corpus,
                cost_band=idea.cost_band,
                time_to_value=max(0.0, min(1.0, idea.time_to_value + ttv_shift)),
            )
            consider(mutant, operator)

    return {
        niche_label(k): v.to_dict()
        for k, v in sorted(grid.items(), key=lambda kv: kv[0])
    }


def grid_coverage(grid: dict[str, dict]) -> dict:
    """How much of the 25-niche landscape the run actually filled."""
    return {
        "niches_filled": len(grid),
        "niches_total": N_NICHES,
        "coverage": round(len(grid) / N_NICHES, 4),
    }


__all__ = [
    "Elite",
    "NOVELTY_BINS",
    "N_NICHES",
    "OBLIQUE_STRATEGIES",
    "TTV_BINS",
    "grid_coverage",
    "mapelites_grid",
    "mutation_operators",
    "niche_label",
    "niche_of",
]
