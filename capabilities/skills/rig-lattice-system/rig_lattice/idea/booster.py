"""Creative Booster — the deterministic V3.1 idea-evaluation core.

Implements the Master Creativity Function and the four scoring gates from the
RIG build card *"Creative Booster Scoring Gates — Deterministic + Probabilistic
Idea Evaluation (V3.1)"*. No LLM is in the scoring loop: same input, same
output, always. That is the A1 contract.

    C(idea) = [ N_vendi · U · Q_hybrid · S_bayesian ]^(1/4)
              · D(portfolio) · e(execution) · R(reversibility)
              · V(vessel) · I(instinct) · B(bad_idea_residue)
              / [ G(generic) · K(cost) · T(time_to_value) ]

Two of the card's fifteen sub-formulas are defined in terms of machinery that
does not exist offline — an embedding model and a posterior belief
distribution. Each has a documented deterministic proxy, marked PROXY below,
naming what it approximates and what would replace it. Everything else is a
pure function of the idea's declared fields.

The card's operating law, which the gates enforce:

    Creativity is not randomness. Creativity is controlled deviation that
    remains useful, appropriate, and provable.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

# ── Lexicons ───────────────────────────────────────────────────────────────

STOPWORDS = frozenset(
    """
    a an the to of for and or but with by from in on at as is are was were
    be been being that this these those it its your our their his her they
    we you i not no do does did will would can could should shall may might
    into onto over under about across per via each all any some more most
    """.split()
)

# G(generic): the banned-phrase term. Median market language.
GENERIC_PHRASES: tuple[str, ...] = (
    "ai-powered", "ai powered", "best-in-class", "best in class",
    "end-to-end", "end to end", "synergy", "synergies", "leverage",
    "leverages", "leveraging", "unlock growth", "cutting-edge",
    "cutting edge", "world-class", "world class", "seamless",
    "seamlessly", "revolutionize", "revolutionary", "game-changing",
    "game changer", "next-generation", "next generation",
    "state-of-the-art", "state of the art", "one-stop-shop",
    "one-stop shop", "value-add", "paradigm shift", "disrupt",
    "disruptive", "robust solution", "holistic approach", "turnkey",
    "unparalleled", "innovative solution", "data-driven insights",
    "optimize your business", "thought leader", "move the needle",
    "low-hanging fruit", "circle back", "boil the ocean",
)

# Mechanism vocabulary — words that describe HOW something works rather than
# how good it is. Drives U(usefulness) and the theater gate's proof density.
MECHANISM_MARKERS: tuple[str, ...] = (
    "because", "therefore", "so that", "which causes", "by ", "via ",
    "threshold", "gate", "loop", "queue", "index", "cache", "regex",
    "deterministic", "invariant", "idempotent", "hash", "schema",
    "constraint", "budget", "fallback", "escalation", "rollback",
    "measured", "instrumented", "benchmark", "baseline", "p95",
)

# R(reversibility): words that signal a one-way door (lower is worse).
IRREVERSIBLE_MARKERS: tuple[str, ...] = (
    "migrate", "migration", "delete", "drop table", "rewrite", "replatform",
    "one-way", "irreversible", "permanent", "public launch", "announce",
    "sign", "contract", "hire", "acquire",
)
REVERSIBLE_MARKERS: tuple[str, ...] = (
    "feature flag", "flag", "canary", "pilot", "prototype", "sandbox",
    "dry-run", "dry run", "reversible", "rollback", "shadow", "a/b",
    "experiment", "opt-in",
)

# ── Thresholds from the build card (§3) ────────────────────────────────────

ANTI_RANDOMNESS_NOVELTY = 0.85
ANTI_RANDOMNESS_APPROPRIATENESS = 0.55
GENERIC_USEFULNESS_USEFULNESS = 0.70
GENERIC_USEFULNESS_DEVIATION = 0.40
THEATER_DEVIATION = 0.80
THEATER_PROOF_DENSITY = 0.60

ACCEPT_THRESHOLDS: dict[str, float] = {
    "creativity_score": 0.78,
    "deviation_score": 0.80,
    "appropriateness": 0.65,
    "usefulness": 0.70,
    "proof_density": 0.60,
}
ACCEPT_MAX_GENERIC_PENALTY = 0.15


# Second arm of the generic-usefulness gate (§3.2). An artifact whose language
# is saturated with median phrasing AND which carries no receipts at all is
# rejected rather than revised: "revise" presumes a mechanism worth keeping.
UNSALVAGEABLE_GENERIC_PENALTY = 0.85


# ── Helpers ────────────────────────────────────────────────────────────────


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _content_words(text: str) -> set[str]:
    return {w for w in _tokens(text) if w not in STOPWORDS and len(w) > 2}


def _ngrams(text: str, n: int = 3) -> set[tuple[str, ...]]:
    toks = _tokens(text)
    return {tuple(toks[i : i + n]) for i in range(max(0, len(toks) - n + 1))}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _count_markers(text: str, markers) -> int:
    low = text.lower()
    return sum(1 for m in markers if m in low)


@dataclass(frozen=True)
class Idea:
    """The declared surface of a candidate idea. Everything scored is here."""

    title: str = ""
    content: str = ""
    context: str = ""
    sources: tuple[str, ...] = ()
    claims: tuple[str, ...] = ()
    mechanisms: tuple[str, ...] = ()
    corpus: tuple[str, ...] = ()
    cost_band: float = 0.5   # K: 0 = free, 1 = ruinous
    time_to_value: float = 0.5  # T: 0 = immediate, 1 = years

    @classmethod
    def from_mapping(cls, data: dict) -> "Idea":
        def seq(key: str) -> tuple[str, ...]:
            return tuple(str(x) for x in (data.get(key) or ()))

        return cls(
            title=str(data.get("title") or ""),
            content=str(data.get("content") or ""),
            context=str(data.get("context") or ""),
            sources=seq("sources"),
            claims=seq("claims"),
            mechanisms=seq("mechanisms"),
            corpus=seq("corpus"),
            cost_band=float(data.get("cost_band", 0.5)),
            time_to_value=float(data.get("time_to_value", 0.5)),
        )

    @property
    def all_text(self) -> str:
        return f"{self.title} {self.content} {self.context}"


@dataclass(frozen=True)
class BoosterScore:
    """Every component of the Master Creativity Function, reported."""

    creativity_score: float
    deviation_score: float
    novelty: float
    usefulness: float
    quality: float
    surprise: float
    appropriateness: float
    proof_density: float
    generic_penalty: float
    portfolio_fit: float
    execution: float
    reversibility: float
    vessel: float
    instinct: float
    bad_idea_residue: float
    cost: float
    time_to_value: float
    numerator: float
    denominator: float
    proxies: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "creativity_score": round(self.creativity_score, 4),
            "deviation_score": round(self.deviation_score, 4),
            "dimensions": {
                "novelty": round(self.novelty, 4),
                "usefulness": round(self.usefulness, 4),
                "quality": round(self.quality, 4),
                "surprise": round(self.surprise, 4),
                "appropriateness": round(self.appropriateness, 4),
                "proof_density": round(self.proof_density, 4),
                "generic_penalty": round(self.generic_penalty, 4),
            },
            "multipliers": {
                "portfolio_fit": round(self.portfolio_fit, 4),
                "execution": round(self.execution, 4),
                "reversibility": round(self.reversibility, 4),
                "vessel": round(self.vessel, 4),
                "instinct": round(self.instinct, 4),
                "bad_idea_residue": round(self.bad_idea_residue, 4),
            },
            "divisors": {
                "generic": round(self.generic_penalty, 4),
                "cost": round(self.cost, 4),
                "time_to_value": round(self.time_to_value, 4),
            },
            "proxies": list(self.proxies),
        }


# ── The fifteen sub-formulas ───────────────────────────────────────────────

def novelty(idea: Idea) -> float:
    """N_vendi — diversity of the idea's language against the corpus.

    PROXY. The card specifies ``exp(H(eigenvalues(K)))`` over an embedding
    similarity matrix (Vendi Score). Offline there is no embedding model, so
    this approximates it with normalized maximum n-gram distance to the
    supplied corpus: the further the idea's trigrams are from every corpus
    entry, and the fewer median phrases it reuses, the higher the novelty.
    Replace with the Vendi Score over real embeddings when one is available;
    the gate thresholds are unchanged by the swap.
    """
    text = f"{idea.title} {idea.content}"
    tri = _ngrams(text, 3)
    words = _content_words(text)
    overlap = 0.0
    for entry in idea.corpus:
        overlap = max(
            overlap,
            _jaccard(tri, _ngrams(entry, 3)),
            _jaccard(words, _content_words(entry)) * 0.75,
        )
    return _clamp01(1.0 - max(overlap, generic_penalty(idea)))


def usefulness(idea: Idea) -> float:
    """U = expected_impact * feasibility * pain_alignment * 1/time_to_value.

    Each factor is read off the declared fields: impact from the density of
    named mechanisms, feasibility from reversibility signals, pain alignment
    from how concretely the context names an audience and its situation.
    """
    impact = _clamp01(len(idea.mechanisms) / 4.0)
    mech_lang = _clamp01(_count_markers(idea.content, MECHANISM_MARKERS) / 5.0)
    feasibility = _clamp01(0.5 + 0.5 * reversibility(idea))
    pain = appropriateness(idea)
    ttv_inv = 1.0 - _clamp01(idea.time_to_value) * 0.5
    base = (0.6 * impact + 0.4 * mech_lang) * feasibility * (0.5 + 0.5 * pain)
    return _clamp01(base * ttv_inv * 1.6)


def quality(idea: Idea) -> float:
    """Q_hybrid — the 7-factor Torrance-style ensemble, computed structurally.

    Fluency (how much substance), Flexibility (lexical range), Originality
    (novelty), Elaboration (mechanism detail), Sensitivity (does it name a
    real problem), Resistance to Premature Closure (does it carry open
    claims), Abstractness of Titles (is the title conceptual, not literal).
    """
    words = _tokens(idea.content)
    content_words = _content_words(idea.content)
    fluency = _clamp01(len(words) / 120.0)
    flexibility = _clamp01(len(content_words) / max(1, len(words)) * 2.0)
    originality = novelty(idea)
    elaboration = _clamp01(len(idea.mechanisms) / 4.0)
    sensitivity = appropriateness(idea)
    open_closure = _clamp01(len(idea.claims) / 3.0)
    title_abstract = _clamp01(len(_content_words(idea.title)) / 5.0)
    factors = (
        fluency,
        flexibility,
        originality,
        elaboration,
        sensitivity,
        open_closure,
        title_abstract,
    )
    return _clamp01(sum(factors) / len(factors))


def surprise(idea: Idea) -> float:
    """S_bayesian — bits of belief update the idea forces.

    PROXY. The card specifies ``D_KL(P_post || P_prior)``, which needs a
    posterior over audience belief. Offline this approximates it with the
    count of claims that contradict the corpus's modal claim — i.e. claims
    carrying explicit contradiction markers or quantities that the corpus does
    not contain — normalized. Replace with a real KL divergence once audience
    priors are measured.
    """
    claim_text = " ".join(idea.claims)
    contradiction_markers = (
        "not ", "never", "unlike", "contrary", "instead", "myth",
        "wrong", "fails", "despite", "counter", "opposite", "rejects",
    )
    contradictions = _count_markers(claim_text, contradiction_markers)
    numerics = set(re.findall(r"\d+(?:\.\d+)?%?", f"{idea.content} {claim_text}"))
    corpus_numerics = set(re.findall(r"\d+(?:\.\d+)?%?", " ".join(idea.corpus)))
    novel_quantities = len(numerics - corpus_numerics)
    return _clamp01((contradictions + novel_quantities) / 4.0)


def appropriateness(idea: Idea) -> float:
    """Is a concrete audience and situation named? Anti-randomness anchor."""
    ctx_words = _content_words(idea.context)
    named = _clamp01(len(ctx_words) / 6.0)
    grounded = _clamp01(len(idea.sources) / 3.0)
    return _clamp01(0.65 * named + 0.35 * grounded)


def proof_density(idea: Idea) -> float:
    """Receipts per claim: sources, claims, and named mechanisms."""
    receipts = len(idea.sources) + len(idea.claims) + len(idea.mechanisms)
    breadth = _clamp01(receipts / 10.0)
    sourced = _clamp01(len(idea.sources) / 3.0)
    mechanised = _clamp01(len(idea.mechanisms) / 3.0)
    return _clamp01(0.4 * breadth + 0.35 * sourced + 0.25 * mechanised)


def generic_penalty(idea: Idea) -> float:
    """G = a*banned_phrase_count + b*max_ngram_overlap + c*cliche_distance^-1.

    The third term's embedding distance is unavailable offline; its weight is
    carried by the n-gram overlap term, which measures the same thing more
    crudely (PROXY).
    """
    text = idea.all_text.lower()
    banned = _count_markers(text, GENERIC_PHRASES)
    tri = _ngrams(f"{idea.title} {idea.content}", 3)
    overlap = max(
        (_jaccard(tri, _ngrams(entry, 3)) for entry in idea.corpus), default=0.0
    )
    return _clamp01(0.6 * (banned / 3.0) + 0.4 * overlap)


def portfolio_fit(idea: Idea) -> float:
    """D(portfolio) — does it sit apart from what the corpus already covers."""
    if not idea.corpus:
        return 1.0
    words = _content_words(f"{idea.title} {idea.content}")
    avg = sum(_jaccard(words, _content_words(c)) for c in idea.corpus) / len(
        idea.corpus
    )
    return _clamp01(1.0 - avg)


def execution(idea: Idea) -> float:
    """e(execution) — is the how spelled out well enough to start."""
    return _clamp01(
        0.5 * _clamp01(len(idea.mechanisms) / 3.0)
        + 0.5 * _clamp01(_count_markers(idea.content, MECHANISM_MARKERS) / 4.0)
    )


def reversibility(idea: Idea) -> float:
    """R(reversibility) — cheap to undo scores high, one-way doors score low."""
    text = idea.all_text
    rev = _count_markers(text, REVERSIBLE_MARKERS)
    irr = _count_markers(text, IRREVERSIBLE_MARKERS)
    if rev == 0 and irr == 0:
        return 0.6  # unstated: assume mostly reversible but do not reward it
    return _clamp01(0.5 + 0.25 * rev - 0.25 * irr)


def vessel(idea: Idea) -> float:
    """V(vessel) — is there a concrete artifact this ships as."""
    vessels = (
        "post", "essay", "article", "page", "email", "video", "deck",
        "report", "cli", "api", "service", "dashboard", "package",
        "skill", "harness", "playbook", "template", "offer", "workshop",
    )
    return _clamp01(0.4 + 0.3 * _count_markers(idea.all_text, vessels))


def instinct(idea: Idea) -> float:
    """I(instinct) — declared conviction, read as title specificity."""
    title_words = _content_words(idea.title)
    return _clamp01(0.5 + len(title_words) / 12.0)


def bad_idea_residue(idea: Idea) -> float:
    """B(bad_idea_residue) — value salvaged even if the thesis is wrong.

    An idea whose claims are falsifiable leaves knowledge behind when it
    fails; an unfalsifiable one leaves nothing.
    """
    return _clamp01(0.5 + 0.5 * _clamp01(len(idea.claims) / 3.0))


def cost(idea: Idea) -> float:
    """K(cost) — divisor, floored so it can never zero the score."""
    return max(0.25, _clamp01(idea.cost_band))


def time_to_value(idea: Idea) -> float:
    """T(time_to_value) — divisor, floored likewise."""
    return max(0.25, _clamp01(idea.time_to_value))


# ── Master Creativity Function ─────────────────────────────────────────────

PROXY_NOTES: tuple[str, ...] = (
    "N_vendi: n-gram distance to corpus stands in for Vendi eigen-entropy "
    "over embeddings",
    "S_bayesian: corpus-contradicting claim count stands in for D_KL(post||prior)",
    "G: cliche embedding distance folded into the n-gram overlap term",
)


def score_idea(idea: Idea | dict, corpus: list[str] | None = None) -> BoosterScore:
    """Score an idea with the V3.1 Master Creativity Function.

    Pure: no clock, no randomness, no I/O. The same idea always scores the
    same. ``corpus`` may be passed here or carried on the idea.
    """
    if not isinstance(idea, Idea):
        idea = Idea.from_mapping(idea)
    if corpus:
        idea = Idea(
            **{
                **{k: getattr(idea, k) for k in idea.__dataclass_fields__},
                "corpus": tuple(corpus),
            }
        )

    n = novelty(idea)
    u = usefulness(idea)
    q = quality(idea)
    s = surprise(idea)
    appr = appropriateness(idea)
    pd = proof_density(idea)
    g = generic_penalty(idea)

    # Geometric mean of the four primary terms: one zero collapses the score,
    # which is the point — an idea cannot buy its way past a dead dimension.
    core = (max(n, 1e-6) * max(u, 1e-6) * max(q, 1e-6) * max(s, 1e-6)) ** 0.25

    d = portfolio_fit(idea)
    e = execution(idea)
    r = reversibility(idea)
    v = vessel(idea)
    i = instinct(idea)
    b = bad_idea_residue(idea)
    k = cost(idea)
    t = time_to_value(idea)

    numerator = core * d * e * r * v * i * b
    denominator = (1.0 + g) * k * t
    raw = numerator / denominator if denominator else 0.0

    # Normalize: the divisors floor at 0.25*0.25=0.0625, so raw can exceed 1.
    creativity = _clamp01(raw / 4.0 if raw > 1.0 else raw)

    # DeviationScore is how far off-median the artifact reads.
    deviation = _clamp01(0.6 * n + 0.4 * s)

    return BoosterScore(
        creativity_score=creativity,
        deviation_score=deviation,
        novelty=n,
        usefulness=u,
        quality=q,
        surprise=s,
        appropriateness=appr,
        proof_density=pd,
        generic_penalty=g,
        portfolio_fit=d,
        execution=e,
        reversibility=r,
        vessel=v,
        instinct=i,
        bad_idea_residue=b,
        cost=k,
        time_to_value=t,
        numerator=numerator,
        denominator=denominator,
        proxies=PROXY_NOTES,
    )


# ── Gates (build card §3) ──────────────────────────────────────────────────

@dataclass(frozen=True)
class GateResult:
    gate: str
    passed: bool
    action: str          # "accept" | "revise" | "reject" | "pass"
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "passed": self.passed,
            "action": self.action,
            "reason": self.reason,
        }


def run_gates(score: BoosterScore) -> list[GateResult]:
    """The four gates, with the card's exact thresholds."""
    results: list[GateResult] = []

    # §3.1 Anti-Randomness — novel but contextless is not creative.
    random_fail = (
        score.novelty > ANTI_RANDOMNESS_NOVELTY
        and score.appropriateness < ANTI_RANDOMNESS_APPROPRIATENESS
    )
    results.append(
        GateResult(
            gate="anti_randomness",
            passed=not random_fail,
            action="reject" if random_fail else "pass",
            reason=(
                f"novelty {score.novelty:.2f} > {ANTI_RANDOMNESS_NOVELTY} with "
                f"appropriateness {score.appropriateness:.2f} < "
                f"{ANTI_RANDOMNESS_APPROPRIATENESS}: random, not creative"
                if random_fail
                else "novelty is anchored to a named context"
            ),
        )
    )

    # §3.2 Generic Usefulness — practical but median.
    #
    # The card's trigger pair is `Usefulness > 0.70 and DeviationScore < 0.40`
    # (the "useful but copyable" shape). §1 defines the failure mode this gate
    # guards more broadly: "practical but median, boring, copyable, and
    # indistinguishable from competitor output". The distinguishing property is
    # median-ness, not usefulness, so the gate has a second arm for the
    # saturated case: median deviation, saturated generic language, and no
    # receipts at all. That arm rejects rather than revises, because "revise"
    # presumes a mechanism worth keeping and this shape has none.
    generic_fail_useful = (
        score.usefulness > GENERIC_USEFULNESS_USEFULNESS
        and score.deviation_score < GENERIC_USEFULNESS_DEVIATION
    )
    generic_fail_median = (
        score.deviation_score < GENERIC_USEFULNESS_DEVIATION
        and score.generic_penalty >= UNSALVAGEABLE_GENERIC_PENALTY
        and score.proof_density <= 0.2
    )
    generic_fail = generic_fail_useful or generic_fail_median
    if generic_fail_median:
        generic_reason = (
            f"deviation {score.deviation_score:.2f} < "
            f"{GENERIC_USEFULNESS_DEVIATION} with generic penalty "
            f"{score.generic_penalty:.2f} >= {UNSALVAGEABLE_GENERIC_PENALTY} "
            f"and proof density {score.proof_density:.2f}: median language with "
            "no receipts; nothing to revise"
        )
    elif generic_fail_useful:
        generic_reason = (
            f"usefulness {score.usefulness:.2f} > "
            f"{GENERIC_USEFULNESS_USEFULNESS} with deviation "
            f"{score.deviation_score:.2f} < {GENERIC_USEFULNESS_DEVIATION}: "
            "useful but generic; needs median-breaking injection"
        )
    else:
        generic_reason = "deviation clears the median-break floor"
    results.append(
        GateResult(
            gate="generic_usefulness",
            passed=not generic_fail,
            action=(
                "reject"
                if generic_fail_median
                else "revise"
                if generic_fail_useful
                else "pass"
            ),
            reason=generic_reason,
        )
    )

    # §3.3 Theater — high deviation, no proof.
    theater_fail = (
        score.deviation_score > THEATER_DEVIATION
        and score.proof_density < THEATER_PROOF_DENSITY
    )
    results.append(
        GateResult(
            gate="theater",
            passed=not theater_fail,
            action="revise" if theater_fail else "pass",
            reason=(
                f"deviation {score.deviation_score:.2f} > {THEATER_DEVIATION} "
                f"with proof density {score.proof_density:.2f} < "
                f"{THEATER_PROOF_DENSITY}: high deviation but low proof; "
                "needs mechanism specificity"
                if theater_fail
                else "deviation is backed by proof"
            ),
        )
    )

    # §3.4 Final Acceptance — every threshold must clear.
    measured = {
        "creativity_score": score.creativity_score,
        "deviation_score": score.deviation_score,
        "appropriateness": score.appropriateness,
        "usefulness": score.usefulness,
        "proof_density": score.proof_density,
    }
    below = [
        f"{name} {value:.2f} < {ACCEPT_THRESHOLDS[name]}"
        for name, value in measured.items()
        if value < ACCEPT_THRESHOLDS[name]
    ]
    if score.generic_penalty > ACCEPT_MAX_GENERIC_PENALTY:
        below.append(
            f"generic_penalty {score.generic_penalty:.2f} > "
            f"{ACCEPT_MAX_GENERIC_PENALTY}"
        )
    results.append(
        GateResult(
            gate="final_acceptance",
            passed=not below,
            action="accept" if not below else "revise",
            reason=(
                "all six acceptance thresholds met"
                if not below
                else "; ".join(below)
            ),
        )
    )
    return results


def final_verdict(gates: list[GateResult]) -> str:
    """Reject beats revise beats accept. A rejected idea is never revised.

    The verdict is driven entirely by the gates: each failing gate declares
    the action it demands, and the most severe one wins.
    """
    actions = {g.action for g in gates if not g.passed}
    if "reject" in actions:
        return "reject"
    if "revise" in actions:
        return "revise"
    return "accept"


def acceptance_report(score: BoosterScore) -> dict:
    """The six final-acceptance thresholds with measured values, for the CLI."""
    rows = {
        name: {
            "value": round(getattr(score, name), 4),
            "threshold": threshold,
            "met": getattr(score, name) >= threshold,
        }
        for name, threshold in ACCEPT_THRESHOLDS.items()
    }
    rows["generic_penalty"] = {
        "value": round(score.generic_penalty, 4),
        "threshold": ACCEPT_MAX_GENERIC_PENALTY,
        "met": score.generic_penalty <= ACCEPT_MAX_GENERIC_PENALTY,
        "direction": "max",
    }
    return rows


def evaluate(idea: Idea | dict, corpus: list[str] | None = None) -> dict:
    """Score + gate + verdict in one call. The CLI's `idea score` payload."""
    score = score_idea(idea, corpus)
    gates = run_gates(score)
    return {
        "verdict": final_verdict(gates),
        **score.to_dict(),
        "gates": [g.to_dict() for g in gates],
        "failed_gates": [g.gate for g in gates if not g.passed],
        "acceptance": acceptance_report(score),
    }


__all__ = [
    "ACCEPT_MAX_GENERIC_PENALTY",
    "ACCEPT_THRESHOLDS",
    "BoosterScore",
    "GENERIC_PHRASES",
    "GateResult",
    "Idea",
    "PROXY_NOTES",
    "acceptance_report",
    "appropriateness",
    "evaluate",
    "final_verdict",
    "generic_penalty",
    "novelty",
    "proof_density",
    "quality",
    "run_gates",
    "score_idea",
    "surprise",
    "usefulness",
]
