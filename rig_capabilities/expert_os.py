"""Known Expert OS — the 12-Phase master prompt card, transcribed and made executable.

Source card: "RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI
Strategist & Engineer.md" (530 lines). Every string below is transcribed VERBATIM from
that card; nothing was authored here. The card is truncated on disk: Phase 11 keeps only
its one-line objective and Phase 12 is absent entirely, so ``GATES`` has keys 1..10 ONLY
— ``GATES[11]`` and ``GATES[12]`` raise ``KeyError`` and no substitute criterion may ever
be written for them. A phase whose gate text is not on the card can never be reported as
passed.

Register linkage (documented here; ``register.py`` owns the rows, this module writes
none): Phase 1-10 deliverables become register rows with studio ``Strategy`` or ``GTM``
— subsystem ``steering`` for intake and offer work, ``aero`` for the public surface —
and the Phase-11 offering is a row of ``type: offer`` pinned at ``maturity_M0_5: 0`` for
as long as its source section stays truncated. The card's lagging indicator "qualified
conversations" maps onto the EXISTING ``booked_qualified_conversations`` register row; it
is never a second revenue KPI.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
import unicodedata
from typing import Any

SOURCE_CARD = ("RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed "
               "AI Strategist & Engineer.md")

# The eleven phase headings that exist on disk, verbatim, in card order. There is no
# twelfth heading; the card ends with Phase 11's objective and a Sources section.
PHASES: tuple[tuple[int, str], ...] = (
    (1, "Select the problem to own"),
    (2, "Reverse-engineer the market and target roles"),
    (3, "Mine scars, decisions, and proof"),
    (4, "Construct the category point of view"),
    (5, "Create signature intellectual property"),
    (6, "Build the guinea-pig reference implementation"),
    (7, "Convert positioning into résumé evidence"),
    (8, "Engineer the interview system"),
    (9, "Build the searchable expertise architecture"),
    (10, "Run the 90-day MAP deployment"),
    (11, "Turn the system into the RIG offering"),
)

PHASE_HEADINGS: tuple[str, ...] = tuple(f"# Phase {n} — {title}" for n, title in PHASES)

GATED = "gated"
OBJECTIVE_ONLY_TRUNCATED = "objective_only_truncated"
ABSENT_AT_SOURCE = "absent_at_source"

# 1..10 have a gate on the card. 11 has a heading and one objective sentence and nothing
# else. 12 has no heading, no objective, and no gate anywhere in the file.
PHASE_STATUS: dict[int, str] = {
    1: GATED,
    2: GATED,
    3: GATED,
    4: GATED,
    5: GATED,
    6: GATED,
    7: GATED,
    8: GATED,
    9: GATED,
    10: GATED,
    11: OBJECTIVE_ONLY_TRUNCATED,
    12: ABSENT_AT_SOURCE,
}

# The only Phase 11 content on disk, verbatim.
PHASE_11_OBJECTIVE = "Translate the validated expertise into a bounded offer."

# Gate 1..10 verbatim from the card's `### Gate N` sections. Keys 11 and 12 do not exist.
GATES: dict[int, str] = {
    1: ("Advance only with an identifiable economic buyer, costly status quo, observable "
        "transformed state, credible evidence alignment, and a path to demonstration."),
    2: ("Every major career claim must map to direct evidence, an honest transferable "
        "capability, a concrete artifact, or a clearly labeled plan."),
    3: ("No positioning claim advances without a firsthand story, working artifact, "
        "measured result, or explicit testable procedure."),
    4: ("The point of view must be relevant, evidenced, operationally useful, meaningfully "
        "different, falsifiable, and bounded."),
    5: ("A competent third party must be able to use the framework to make a better "
        "decision without needing me to translate it."),
    6: ("No successful-deployment claim until an independent verifier confirms predefined "
        "tests and proof obligations."),
    7: ("Every bullet must pass truth, relevance, specificity, outcome, differentiation, "
        "and ten-minute interview defensibility."),
    8: ("The narrative must remain consistent with the résumé, survive technical scrutiny, "
        "connect to commercial outcomes, and admit unknowns without pretending to know "
        "confidential information."),
    9: ("Reject content that is generic, lacks judgment, is disconnected from buyer pain, "
        "cannot be supported honestly, or could be generated unchanged without my "
        "experience."),
    10: ("Do not increase volume below the quality threshold, and do not abandon the system "
         "because early audience numbers are small. Optimize for the right 30 people, not "
         "the wrong 30,000."),
}

# Non-negotiable rules 1-15, verbatim, in card order. The card numbers them 1..15.
NON_NEGOTIABLE_RULES: tuple[str, ...] = (
    "Never invent experience, metrics, clients, deployments, qualifications, or technical "
    "capabilities.",
    "Classify important assertions as verified fact, supported inference, hypothesis, "
    "unverified claim, or future plan.",
    "Never place an unverified claim on a résumé.",
    "Publishing does not confer expertise.",
    "Expertise requires original decisions, working artifacts, measured outcomes, credible "
    "explanations, external feedback, and repeatable procedures.",
    "Optimize for recognition among people who can hire, sponsor, buy, refer, or validate "
    "the work—not generic popularity.",
    "Reject anything a commodity AI consultant could publish unchanged.",
    "Every major output requires a proof obligation and acceptance criterion.",
    "Nothing ships at 0σ.",
    "Enforce GEV separation: generators produce, evaluators critique, verifiers decide, "
    "humans approve external, destructive, financial, or reputational actions.",
    "No component certifies its own output.",
    "Record retries and failures; do not hide them.",
    "Prefer minimum viable proof over maximum speculative scope.",
    "Use buyer language first and technical language only when it increases precision.",
    "Maintain an Evidence Ledger:",
)

NO_UNVERIFIED_ON_RESUME_RULE = "Never place an unverified claim on a résumé."

# The three success horizons, verbatim headings + bodies.
HORIZONS: tuple[tuple[str, str], ...] = (
    ("Horizon 1 — Career proof",
     "Make my résumé, portfolio, professional profile, and interview narrative prove that I "
     "already think and operate like a forward-deployed strategist and AI engineer."),
    ("Horizon 2 — RIG offering",
     "Turn the same intellectual property into a differentiated commercial offer for "
     "organizations that need to move AI initiatives into governed production."),
    ("Horizon 3 — RIG 2031",
     "Convert every validated procedure, decision rule, evaluator, template, and artifact "
     "into a reusable RIG component. The career campaign must generate the first proven "
     "blocks of the future business."),
)

# Phase 3's depth ladder, verbatim.
DEPTH_LEVELS = ("L1_surface", "L2_synthesis", "L3_scar", "L4_judgment", "L5_procedure")
DEPTH_TEXT: tuple[str, ...] = (
    "L1 Surface: generic information",
    "L2 Synthesis: useful organization of known information",
    "L3 Scar: firsthand success, failure, or tradeoff",
    "L4 Judgment: a decision rule that changes expert action",
    "L5 Procedure: repeatable executable system with tests and evidence",
)
MIN_PUBLISHABLE_DEPTH = "L3_scar"
DEPTH_PRIORITY = "Prioritize L3–L5."

# Phase 10's 90-day MAP cadence, verbatim. The card's title spells MAP with the three
# week blocks: Mine, Accelerate, Position.
MAP_CADENCE: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Weeks 1–2", "Mine", (
        "Finalize the problem, study buyer language, generate 30–50 problem-led topics, "
        "select 12, construct content chains, establish evidence and baseline dashboards, "
        "script four pieces, and define evaluator/verifier rubrics.",
    )),
    ("Weeks 3–8", "Accelerate", (
        "Publish at least one substantial proof asset weekly; prefer two only if gates "
        "hold. Derive one professional-network post and one reusable RIG component from "
        "each major asset.",
        "Each piece must identify the problem, establish relevance, explain stakes, expose "
        "the conventional assumption, provide my model, show evidence, disclose "
        "limitations, and route to the next piece.",
    )),
    ("Weeks 9–12", "Position", (
        "Move toward narrower situations, deeper cases, stronger defensible opinions, real "
        "architecture, quantified results, failures, tradeoffs, and signature frameworks.",
        "Track consistency, quality, buyer relevance, completion, qualified engagement, "
        "framework recall, conversations, proof created, procedure crystallization, and "
        "residual evidence gaps.",
    )),
)

MAP_PHASES: tuple[str, ...] = tuple(name for _, name, _ in MAP_CADENCE)


def _slug(text: str) -> str:
    """Deterministic deliverable key: accents folded, non-alphanumerics → underscores."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^0-9A-Za-z]+", "_", folded)).strip("_").lower()


# Named deliverables per phase, verbatim card phrases. Phases 1-7 declare them under a
# `### Deliverables` heading. Phases 8 and 9 declare no such heading; their named items
# are the card's "Create …" sentences. Phase 10 declares no `### Deliverables` heading
# either; its named artifacts are the ones the Weeks 1–2 / Weeks 3–8 blocks require.
# Phase 11 names nothing — its section is truncated after the objective.
PHASE_DELIVERABLES: dict[int, tuple[tuple[str, str], ...]] = {
    1: tuple((_slug(t), t) for t in (
        "primary and secondary problems",
        "one rejected broad position",
        "one-sentence problem statement",
        "market narrative",
        "“for / not for” definition",
        "five buyer-language versions",
        "evidence table",
    )),
    2: tuple((_slug(t), t) for t in (
        "market and role brief",
        "role outcome map",
        "hiring-manager scorecard",
        "top 10 rejection risks",
        "evidence or mitigation for each",
        "“why this problem / role / me / now” narrative",
        "prohibited unsupported claims",
    )),
    3: tuple((_slug(t), t) for t in (
        "accomplishment inventory",
        "20 scar stories",
        "10 defensible contrarian positions",
        "10 reusable decision rules",
        "five demonstrable procedures",
        "proof-gap backlog",
        "public-safe redactions",
    )),
    4: tuple((_slug(t), t) for t in (
        "A 50-word thesis",
        "150-word thesis",
        "500-word manifesto",
        "system diagram",
        "claims/counterclaims",
        "objections from five buyer roles",
        "required evidence",
        "prohibited overclaims",
    )),
    5: tuple((_slug(t), t) for t in (
        "Flagship framework",
        "visual model",
        "scorecard",
        "checklist",
        "decision tree",
        "diagnostic",
        "glossary",
        "field guide",
        "five examples",
        "five counterexamples",
    )),
    6: tuple((_slug(t), t) for t in (
        "Reference plan",
        "architecture",
        "baseline",
        "weekly experiments",
        "proof-packet template",
        "public case study",
        "private appendix",
        "postmortem",
    )),
    7: tuple((_slug(t), t) for t in (
        "Master résumé",
        "target-role version",
        "one-page version",
        "ATS version",
        "executive version",
        "bullet-level evidence ledger",
        "rejected-claims list",
        "professional profile",
        "10 interview stories",
    )),
    8: tuple((_slug(t), t) for t in (
        "90-second introduction",
        "five-minute career narrative",
        "15-minute case study",
        "technical deep dive",
        "discovery example",
        "failure story",
        "disagreement story",
        "architecture-tradeoff story",
        "30/60/90 plan",
        "opportunity memo",
        "high-value questions",
    )),
    9: tuple((_slug(t), t) for t in (
        "30 searchable topics",
        "12 deep positioning topics",
        "six case studies",
        "six contrarian essays",
        "four demonstrations",
        "four interview-relevant technical explanations",
    )),
    10: tuple((_slug(t), t) for t in (
        "30–50 problem-led topics",
        "select 12",
        "content chains",
        "evidence and baseline dashboards",
        "script four pieces",
        "evaluator/verifier rubrics",
        "one substantial proof asset weekly",
        "one professional-network post",
        "one reusable RIG component",
    )),
}


def title(phase: int) -> str:
    """Verbatim phase title for a phase number."""
    for n, t in PHASES:
        if n == phase:
            return t
    raise ValueError(f"unknown_phase:{phase}")


def deliverable_slugs(phase: int) -> tuple[str, ...]:
    """The slug of every deliverable the card names for that phase."""
    return tuple(slug for slug, _ in PHASE_DELIVERABLES.get(phase, ()))


def advance(phase: int, deliverables: Mapping[str, Any] | None = None) -> dict:
    """Check declared deliverables against the phase's verbatim gate. Never scores 11/12.

    ``deliverables`` maps a deliverable slug (see ``PHASE_DELIVERABLES``) to whatever the
    caller produced for it. A slug is satisfied only by a truthy value. The returned gate
    text is the card's own sentence, so the caller can never lose the criterion it is
    being held to. Phases 11 and 12 have no gate on the card, so they always return
    ``ok: False`` with their truncation status — never a pass, never an invented gate.
    """
    if phase not in PHASE_STATUS:
        raise ValueError(f"unknown_phase:{phase}")
    status = PHASE_STATUS[phase]
    given = deliverables or {}
    if not isinstance(given, Mapping):
        raise TypeError("deliverables must be a mapping of slug to artifact")
    if status != GATED:
        return {"ok": False, "gate": "", "missing": list(deliverable_slugs(phase)),
                "status": status}
    missing = [slug for slug, _ in PHASE_DELIVERABLES[phase] if not given.get(slug)]
    return {"ok": not missing, "gate": GATES[phase], "missing": missing, "status": status}
