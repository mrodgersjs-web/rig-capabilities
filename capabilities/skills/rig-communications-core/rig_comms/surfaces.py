"""Surface registry — the twelve surfaces of Mike's writing life.

Single source of truth for per-surface lanes, sigma targets, rubrics, bx
fusions, deviation-engine assignments and budgets (master plan v5.2, v6, v7.1,
v13.1/3/8). Lane rules are CODE, not documentation: love-notes is private and
never autonomous (v19.6 hard rule enforced in cli/gates).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Surface:
    id: str
    lane: str                       # public | internal | private
    template: str                   # rig_comm template id or ""
    agf_min: int
    sigma_target: int               # master-comms-v1 per-output-type target
    wounds_required: bool
    rubric: str                     # bdf30 | chase | eas | beats | none
    bx: tuple                       # v4 fusion skills to load before drafting
    engines: tuple                  # v13 deviation engines (canonical ids)
    physics_first: bool             # v13.4 short-circuit on outward claims
    budget: int                     # v13.8 deviation budget per artifact class
    keywords: tuple                 # v9.3 route INTENT -> surface
    persona_default: str = ""


# Deviation budget ordering per plan: novel > post > email (v13.8).
SURFACES: dict[str, Surface] = {s.id: s for s in (
    Surface("prompts", "internal", "", 85, 10, False, "none",
            ("bx-measurement-steward",),
            ("SpecificityGate", "FeynmanXRay", "AntiSlopAuditor",
             "MechanismFurnace", "AutonomyCalibration"),
            False, 1, ("prompt", "agent prompt", "system prompt", "co-star")),
    Surface("film-scripts", "internal", "", 85, 10, True, "beats",
            ("bx-emotion-cartographer", "bx-falsifier"),
            ("VoltageReactor", "MemoryResidue", "RuptureEngine",
             "EvolutionaryMemoryFlywheel", "CoralReefEvolver"),
            False, 3, ("screenplay", "script", "scene", "treatment", "beat sheet")),
    Surface("resumes", "internal", "", 85, 10, True, "none",
            ("bx-committee-simulator", "bx-need-architect"),
            ("RealityAnchor", "SpecificityGate", "SourcePerClaim",
             "AbsoluteZeroFloor"),
            True, 0, ("resume", "cv", "job application", "bullet")),
    Surface("linkedin", "public", "linkedin_post", 85, 15, True, "chase",
            ("bx-emotion-cartographer", "bx-influence-designer", "bx-falsifier"),
            ("GravityEscape", "PredictiveErrorCalibration", "VoltageReactor",
             "MemoryResidue", "CuckooParasite"),
            False, 2, ("linkedin", "post", "carousel", "alfred"),
            persona_default="icp-pe-operator"),
    Surface("songs", "internal", "", 85, 10, True, "eas",
            ("bx-emotion-cartographer",),
            ("VoltageReactor", "MemoryResidue", "EvolutionaryMemoryFlywheel",
             "BellEntanglement"),
            False, 3, ("song", "lyric", "suno", "chorus", "hook")),
    Surface("emails", "internal", "cold_email", 85, 12, True, "bdf30",
            ("bx-need-architect", "bx-intervention-designer"),
            ("RealityAnchor", "AutonomyCalibration", "SpecificityGate",
             "MechanismFurnace"),
            True, 1, ("email", "reply", "outreach", "follow-up")),
    Surface("substack", "public", "case_study", 85, 15, True, "none",
            ("bx-process-miner", "bx-falsifier"),
            ("MemoryResidue", "RuptureEngine", "CollisionCollider",
             "TemporalHorizonIntegrity"),
            False, 2, ("substack", "essay", "newsletter", "long-form"),
            persona_default="substack-operator-reader"),
    Surface("novels", "internal", "", 85, 10, True, "none",
            ("bx-emotion-cartographer", "bx-need-architect"),
            ("RuptureEngine", "VoltageReactor", "EvolutionaryMemoryFlywheel",
             "WhaleSpiral", "CoralReefEvolver", "SlimeMoldNetwork"),
            False, 4, ("novel", "chapter", "fiction", "character arc")),
    Surface("specs", "internal", "", 85, 0, False, "none",
            ("bx-decision-modeler", "bx-committee-simulator"),
            ("MechanismFurnace", "FeynmanXRay", "SpeedOfLightCausality",
             "FalsificationPrereg"),
            True, 0, ("spec", "rfc", "design doc", "bdd", "openspec")),
    Surface("code", "internal", "", 85, 0, False, "none",
            ("bx-measurement-steward",),
            ("MechanismFurnace", "FeynmanXRay", "AntiSlopAuditor",
             "PauliExclusion"),
            False, 0, ("code as writing", "commit message", "docstring", "naming")),
    Surface("love-notes", "private", "", 85, 0, True, "none",
            ("bx-emotion-cartographer",),
            ("AutonomyCalibration", "VoltageReactor", "MemoryResidue"),
            False, 1, ("love note", "james", "letter"),
            persona_default="james"),
)}

# v6.12 / v19.6: the private lane is never autonomous and never federated.
PRIVATE_SURFACES = frozenset(k for k, v in SURFACES.items() if v.lane == "private")

ALIASES = {"email": "emails", "screenplay": "film-scripts", "cv": "resumes",
           "lyrics": "songs", "essay": "substack", "rfc": "specs", "james": "love-notes"}


def resolve(name: str) -> Surface | None:
    s = name.strip().lower()
    s = ALIASES.get(s, s)
    return SURFACES.get(s)


def route(intent: str) -> list[tuple[str, int]]:
    """Keyword-score every surface against a natural-language intent."""
    text = intent.lower()
    hits = []
    for s in SURFACES.values():
        score = sum(1 for k in s.keywords if k in text)
        if score:
            hits.append((s.id, score))
    hits.sort(key=lambda kv: -kv[1])
    return hits
