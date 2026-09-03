"""Adversarial Survival Rate — the 25-question injection stack.

Build card §5: run the question stack against an idea and report the fraction
it survives. Four groups:

    Pre-Ideation     orthodoxy check, 2030 future-back, JTBD gap
    During-Ideation  TRIZ ideal final result, SIT subtraction, Synectics analogy
    Post-Ideation    falsifiable hypothesis, base-rate delta, proof density
    Hostile Skeptic  the $50K/mo buyer audit, "So what?" x3

Every question carries a deterministic ``check`` over the idea's declared
fields, or is marked ``manual=True`` when no honest automated check exists.
Manual questions are **excluded from the denominator** and reported
separately — never silently counted as survived. A survival rate computed
over 18 automatable questions says so; it does not pretend to be 25.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from rig_lattice.idea.booster import (
    GENERIC_PHRASES,
    MECHANISM_MARKERS,
    Idea,
    _content_words,
    _count_markers,
    score_idea,
)


@dataclass(frozen=True)
class Question:
    qid: str
    group: str
    text: str
    check: Callable[[Idea], bool] | None = None
    manual: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.qid,
            "group": self.group,
            "question": self.text,
            "manual": self.manual,
        }


def _has_numbers(idea: Idea) -> bool:
    return bool(re.search(r"\d", f"{idea.content} {' '.join(idea.claims)}"))


def _negates_orthodoxy(idea: Idea) -> bool:
    markers = ("unlike", "contrary", "instead of", "not ", "myth", "conventional",
               "everyone", "usually", "despite", "counter")
    return _count_markers(f"{idea.content} {' '.join(idea.claims)}", markers) > 0


QUESTIONS: tuple[Question, ...] = (
    # ── Pre-Ideation ──────────────────────────────────────────────────────
    Question(
        "PRE-1", "pre_ideation",
        "Orthodoxy check: does it name the inherited belief it breaks?",
        _negates_orthodoxy,
    ),
    Question(
        "PRE-2", "pre_ideation",
        "Future-back: is it stated as an end state, not an activity?",
        lambda i: _count_markers(
            i.all_text, ("by 20", "end state", "so that", "until", "becomes")
        ) > 0,
    ),
    Question(
        "PRE-3", "pre_ideation",
        "JTBD gap: is the job the buyer is trying to do named?",
        lambda i: len(_content_words(i.context)) >= 4,
    ),
    Question(
        "PRE-4", "pre_ideation",
        "Is the audience specific rather than 'businesses'?",
        lambda i: len(_content_words(i.context)) >= 6,
    ),
    Question(
        "PRE-5", "pre_ideation",
        "Would a domain expert consider the framing non-obvious?",
        manual=True,
    ),
    Question(
        "PRE-6", "pre_ideation",
        "Is there a named competitor baseline in the corpus?",
        lambda i: len(i.corpus) > 0,
    ),
    # ── During-Ideation ───────────────────────────────────────────────────
    Question(
        "DUR-1", "during_ideation",
        "TRIZ ideal final result: is the function stated without the form?",
        lambda i: _count_markers(i.content, MECHANISM_MARKERS) >= 2,
    ),
    Question(
        "DUR-2", "during_ideation",
        "SIT subtraction: does removing the flashiest part leave value?",
        lambda i: len(i.mechanisms) >= 2,
    ),
    Question(
        "DUR-3", "during_ideation",
        "Synectics analogy: is a mechanism borrowed from a distant domain?",
        lambda i: _count_markers(
            i.all_text, ("like a", "analogous", "borrowed from", "the same way",
                          "as in", "mirrors")
        ) > 0,
    ),
    Question(
        "DUR-4", "during_ideation",
        "Is the contradiction articulated, not just a trade-off?",
        lambda i: _count_markers(
            i.all_text, ("but ", "however", "while also", "without giving up",
                          "yet ", "at the same time")
        ) > 0,
    ),
    Question(
        "DUR-5", "during_ideation",
        "Does an alternative framing survive its own subtraction test?",
        manual=True,
    ),
    Question(
        "DUR-6", "during_ideation",
        "Is at least one named mechanism, not a benefit, doing the work?",
        lambda i: len(i.mechanisms) >= 1,
    ),
    # ── Post-Ideation ─────────────────────────────────────────────────────
    Question(
        "POST-1", "post_ideation",
        "Falsifiable hypothesis: is there a claim that could be shown false?",
        lambda i: len(i.claims) >= 1,
    ),
    Question(
        "POST-2", "post_ideation",
        "Is a disproof test named for the primary claim?",
        lambda i: _count_markers(
            i.all_text, ("test", "measure", "benchmark", "baseline", "experiment",
                          "falsif", "p95", "control")
        ) > 0,
    ),
    Question(
        "POST-3", "post_ideation",
        "Base-rate delta: is the improvement quantified against a baseline?",
        _has_numbers,
    ),
    Question(
        "POST-4", "post_ideation",
        "Proof density: are there at least three receipts?",
        lambda i: (len(i.sources) + len(i.claims) + len(i.mechanisms)) >= 3,
    ),
    Question(
        "POST-5", "post_ideation",
        "Are sources cited rather than asserted?",
        lambda i: len(i.sources) >= 1,
    ),
    Question(
        "POST-6", "post_ideation",
        "Is the reasoning chain auditable end to end by a reader?",
        manual=True,
    ),
    Question(
        "POST-7", "post_ideation",
        "Does it survive its own proof-density gate (>= 0.60)?",
        lambda i: score_idea(i).proof_density >= 0.60,
    ),
    # ── Hostile Skeptic ───────────────────────────────────────────────────
    Question(
        "HOS-1", "hostile_skeptic",
        "$50K/mo buyer audit: would a paying operator act on this?",
        lambda i: len(i.mechanisms) >= 2 and len(_content_words(i.context)) >= 4,
    ),
    Question(
        "HOS-2", "hostile_skeptic",
        "So what? (1) Is the consequence of ignoring it stated?",
        lambda i: _count_markers(
            i.all_text, ("otherwise", "cost of", "risk", "fails", "loses",
                          "rework", "breaks")
        ) > 0,
    ),
    Question(
        "HOS-3", "hostile_skeptic",
        "So what? (2) Is the effect size credible rather than heroic?",
        lambda i: _has_numbers(i)
        and not re.search(r"\b(10x|100x|1000x|infinite)\b", i.all_text.lower()),
    ),
    Question(
        "HOS-4", "hostile_skeptic",
        "So what? (3) Does it avoid median market language?",
        lambda i: _count_markers(i.all_text, GENERIC_PHRASES) == 0,
    ),
    Question(
        "HOS-5", "hostile_skeptic",
        "Is it cheap to reverse if the thesis is wrong?",
        lambda i: score_idea(i).reversibility >= 0.6,
    ),
    Question(
        "HOS-6", "hostile_skeptic",
        "Would a hostile reviewer call the strongest claim unsupported?",
        manual=True,
    ),
)

assert len(QUESTIONS) == 25, f"expected the 25-question stack, got {len(QUESTIONS)}"

AUTOMATED_QUESTIONS = tuple(q for q in QUESTIONS if not q.manual)
MANUAL_QUESTIONS = tuple(q for q in QUESTIONS if q.manual)


def run_stack(idea: Idea | dict) -> dict:
    """Run every automatable question. Returns the full per-question result."""
    if not isinstance(idea, Idea):
        idea = Idea.from_mapping(idea)

    results = []
    survived = 0
    for q in QUESTIONS:
        if q.manual or q.check is None:
            results.append({**q.to_dict(), "passed": None, "counted": False})
            continue
        try:
            passed = bool(q.check(idea))
        except Exception as exc:  # a broken check must not read as survival
            results.append(
                {**q.to_dict(), "passed": False, "counted": True, "error": str(exc)}
            )
            continue
        survived += int(passed)
        results.append({**q.to_dict(), "passed": passed, "counted": True})

    denominator = len(AUTOMATED_QUESTIONS)
    return {
        "asr": round(survived / denominator, 4) if denominator else 0.0,
        "survived": survived,
        "scored": denominator,
        "manual": len(MANUAL_QUESTIONS),
        "total_questions": len(QUESTIONS),
        "note": (
            f"{len(MANUAL_QUESTIONS)} of {len(QUESTIONS)} questions need human "
            "judgement and are excluded from the denominator, not counted as "
            "survived"
        ),
        "questions": results,
    }


def adversarial_survival_rate(idea: Idea | dict) -> float:
    """Fraction of the automatable questions the idea survives."""
    return run_stack(idea)["asr"]


def groups() -> dict[str, int]:
    """Question count per group."""
    out: dict[str, int] = {}
    for q in QUESTIONS:
        out[q.group] = out.get(q.group, 0) + 1
    return out


__all__ = [
    "AUTOMATED_QUESTIONS",
    "MANUAL_QUESTIONS",
    "QUESTIONS",
    "Question",
    "adversarial_survival_rate",
    "groups",
    "run_stack",
]
