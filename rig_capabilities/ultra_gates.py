"""ULTRA consumer routing contracts.

The studio docs name Jev signals. This module is where those signals *go*:
one declared route per studio gate, so a verdict changes control flow instead
of decorating a log.

Ordering is deliberate and is the whole point of the module:

    deterministic code checks  ->  Jev (advisory until calibrated)  ->  human authority

* Code checks run first and are authoritative. A missing required fact is
  undecidable, never a pass (s1gate law 1, fail closed).
* An uncalibrated Jev verdict annotates and escalates; it cannot hard-block a
  quality judgment (law 3). A provider error is a halt, not a pass.
* ``requires_human`` survives a clean PASS: a machine PASS is not an
  authorisation (law 6). Gate-D is unchanged by anything in here.

Jev generates no text, so every reason string here is written by code from the
answer it came with. Nothing in this module mutates a workflow, spawns an
agent, or advances a mission -- it returns a route name and the calling studio
decides what to do with it.
"""
from __future__ import annotations

import re
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import ultra_plan
from .s1gate import BLOCK, ESCALATE, PASS, S1GateError, evaluate, load_rubric

__all__ = ["Route", "NOT_CLEARED", "Gate", "GATES", "CODE_CHECKS", "ANGLE_CLASSES",
           "route", "contract", "coverage", "information", "trimmed_mean", "UltraRouteError"]


# ---------------------------------------------------------------------------
# Routes. A closed set: the caller switches on these strings.
# ---------------------------------------------------------------------------


class Route:
    ADVANCE = "advance"                       # cleared; caller may proceed
    ANNOTATE_ADVANCE = "annotate_advance"     # advisory finding, no bar crossed
    REWORK = "rework"                         # back to the producing cell
    ESCALATE_REVIEW = "escalate_review"       # hand to a System 2 model
    HUMAN_CARD = "human_card"                 # this was always a human decision
    HALT_FAILCLOSED = "halt_failclosed"       # provider unusable; nothing advanced
    BLOCKED_UNKNOWN = "blocked_unknown_gate"  # nobody declared this gate
    OFFLINE_CODE_ONLY = "offline_code_only"   # Jev not consulted: not a cleared gate


#: routes that mean "did not clear"
NOT_CLEARED = frozenset({
    Route.REWORK, Route.ESCALATE_REVIEW, Route.HUMAN_CARD, Route.HALT_FAILCLOSED,
    Route.BLOCKED_UNKNOWN, Route.OFFLINE_CODE_ONLY,
})


class UltraRouteError(RuntimeError):
    pass


Check = Callable[[Dict[str, Any]], Tuple[Optional[bool], str]]


# ---------------------------------------------------------------------------
# Deterministic checks. (True, note) / (False, note) / (None, note) where None
# means undecidable -- treated as not-cleared, never as satisfied.
# ---------------------------------------------------------------------------


def _present(facts: Dict[str, Any], key: str) -> bool:
    v = facts.get(key)
    return not (v is None or v == "" or v == [] or v == {})


def check_card_has_recommendation(facts):
    if not _present(facts, "card_options"):
        return None, "card_options absent; cannot check the card shape"
    n = len(facts["card_options"])
    if n < 2:
        return False, "a card with one option is a statement, not a decision"
    if not _present(facts, "card_recommendation"):
        return False, "card without a recommendation: the house rule is one rec per card"
    return True, "%d options, recommendation present" % n


def check_citation_liveness(facts):
    if not _present(facts, "citation_url"):
        return False, "no url to check"
    if not _present(facts, "citation_fetched_at"):
        return False, "citation has no fetched_at: provenance is not reconstructable later"
    live = facts.get("citation_live")
    if live is None:
        return None, "liveness unmeasured: run the liveness check before citing"
    return (bool(live), "live" if live else "url does not resolve, or never existed")


def check_swarm_diversity(facts):
    if facts.get("forecast_family_count") is None:
        return None, "no family count: diversity unverified"
    if facts.get("forecast_count") is None:
        return None, "no forecast count"
    n = int(facts["forecast_family_count"])
    if n < 2:
        return False, "%d weight famil%s: one family is one opinion, not a swarm" % (
            n, "y" if n == 1 else "ies")
    return True, "%d forecasts across %d families" % (int(facts["forecast_count"]), n)


def check_alternatives_documented(facts):
    """Diverge before converge, and count mechanisms rather than headings."""
    alts = facts.get("alternatives")
    if alts is None:
        return None, "alternatives list absent"
    got = ultra_plan.diverge(alts, minimum=int(facts.get("diverge_minimum", ultra_plan.DIVERGE_MINIMUM)))
    if not got["ok"]:
        return False, got["why"]
    return True, got["why"]


def check_outside_view_declared(facts):
    got = ultra_plan.outside_view(facts)
    if not got["ok"]:
        return False, got["why"]
    return True, got["why"]


def check_lease_held(facts):
    holder = facts.get("lease_holder")
    if holder is None:
        return None, "lease state unknown"
    if not holder:
        return False, "no writer holds the lease for this checkout"
    if facts.get("writer_family") and facts.get("verifier_family") == facts.get("writer_family"):
        return False, "builder and verifier share a model family: the gate would grade its own homework"
    return True, "lease held by %s; verifier family differs" % holder


_ASSERTION_PREFIXES = ("cmd:", "pytest", "python3 -m unittest", "npm test", "make", "bash -c", "cargo test")


def _run(cmd: str, timeout: int):
    """Execute one assertion. Facts are caller-supplied and the gate caller already
    holds a shell -- this runs inside the local trust domain, not a sandbox."""
    import subprocess, time
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        tail = (p.stdout or p.stderr or "")[-160:].strip()
        return p.returncode, tail, int((time.monotonic() - t0) * 1000)
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after %ds" % timeout, timeout * 1000


def check_done_test_executable(facts):
    """A done-test that only greps for a file, or asserts nothing, is theater --
    and an assertion named but never RUN is the same theater with a longer name.
    Every recognised assertion is executed here; all must exit 0."""
    cmds = facts.get("done_test_cmds")
    if cmds is None:
        return None, "done_test_cmds absent"
    asserts = []
    for c in cmds:
        c = str(c).strip()
        if c.startswith("cmd:"):
            asserts.append(c[4:].strip())
        elif c.startswith(_ASSERTION_PREFIXES):
            asserts.append(c)
    if not asserts:
        return False, "done-test has no runnable assertion (existence checks only)"
    try:
        timeout = min(int(facts.get("done_test_timeout", 300)), 900)
    except (TypeError, ValueError):
        return False, "done_test_timeout is not a number"
    for c in asserts:
        code, tail, ms = _run(c, timeout)
        if code != 0:
            return False, "assertion exited %d after %dms: %s | %s" % (code, ms, c[:80], tail)
    return True, "%d assertion(s) EXECUTED, all exit 0" % len(asserts)


def check_planted_failure_receipt(facts):
    if not _present(facts, "planted_failure_receipt"):
        return False, "no RED->GREEN receipt: this gate has never been shown able to fail"
    return True, "planted-failure receipt present"


def check_chain_intact(facts):
    v = facts.get("chain_verified")
    if v is None:
        return None, "chain verification not run"
    return (bool(v), "chain intact" if v else "hash chain broken: nothing downstream is trustworthy")


def check_held_out_improvement(facts):
    if not (_present(facts, "score_before") and _present(facts, "score_after")):
        return None, "held-out scores missing: improvement is unmeasured"
    if not _present(facts, "holdout_split_id"):
        return False, "scores without a held-out split id: in-sample improvement is not improvement"
    before, after = float(facts["score_before"]), float(facts["score_after"])
    if after <= before:
        return False, "no held-out improvement (%.3f -> %.3f)" % (before, after)
    return True, "held-out %.3f -> %.3f" % (before, after)


def check_live_artifact_untouched(facts):
    if facts.get("live_artifact_edited"):
        return False, "a live prompt/rubric was edited in place: variants only, adoption is a separate decision"
    return True, "live artifacts untouched; variant proposed"


def check_human_decision_exists(facts):
    """Gate-D: an outward action needs a recorded human decision for THIS action."""
    if not facts.get("human_approved_this_action"):
        return False, "no recorded approval for this specific action"
    if not _present(facts, "approval_quote"):
        return False, "approval flag without a quote: nothing binds the action to the approval"
    return True, "approval recorded for this action"


CODE_CHECKS: Dict[str, Check] = {
    "card_has_recommendation": check_card_has_recommendation,
    "citation_liveness": check_citation_liveness,
    "swarm_diversity": check_swarm_diversity,
    "alternatives_documented": check_alternatives_documented,
    "outside_view_declared": check_outside_view_declared,
    "lease_held": check_lease_held,
    "done_test_executable": check_done_test_executable,
    "planted_failure_receipt": check_planted_failure_receipt,
    "chain_intact": check_chain_intact,
    "held_out_improvement": check_held_out_improvement,
    "live_artifact_untouched": check_live_artifact_untouched,
    "human_decision_exists": check_human_decision_exists,
}


# ---------------------------------------------------------------------------
# Gate table: one entry per declared consumer in the studios.
# ---------------------------------------------------------------------------


@dataclass
class Gate:
    id: str
    studio: str
    pack: Optional[str]                  # None = code + human authority only
    when: str                            # where in the studio process it fires
    checks: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    escalate_is_blocking: bool = False   # kill-switch style gates do not annotate
    requires_human: bool = False         # survives a clean PASS
    note: str = ""


GATES: Dict[str, Gate] = {g.id: g for g in [
    Gate("plan.dq_before_build", "judgment", "ultra.judgment",
         "S gate: plan -> build",
         checks=["alternatives_documented", "outside_view_declared"],
         requires=["alternatives", "reference_class", "base_rate", "base_rate_source", "n_in_class"],
         note="dq.information is computed from ultra.questioning over the 14 classes, not asked here."),
    Gate("questioning.card_before_ask", "questioning", "ultra.questioning",
         "before a card reaches Mike",
         checks=["card_has_recommendation"],
         requires=["card_options", "card_recommendation", "question_text"],
         requires_human=True,
         note="a card is by definition a human decision; this gate only keeps facts and noise off it."),
    Gate("research.citation_before_cite", "research", "ultra.research",
         "before a finding settles a node",
         checks=["citation_liveness"],
         requires=["citation_url", "citation_fetched_at", "claim_text", "source_text"]),
    Gate("forecast.forecast_before_average", "forecasting", "ultra.forecasting",
         "before a forecast enters the swarm average",
         checks=["swarm_diversity"],
         requires=["forecast_text", "forecast_count", "forecast_family_count"]),
    Gate("execution.slice_before_integrate", "execution", "ultra.execution",
         "before a built slice is integrated",
         checks=["lease_held"],
         requires=["diff_text", "claims_text", "lease_holder", "writer_family", "verifier_family"]),
    Gate("execution.tripwire_before_next_wave", "execution", "ultra.execution",
         "between waves; kill switch",
         escalate_is_blocking=True,
         requires=["tripwire_text", "fresh_evidence_text"],
         note="a kill switch that only annotates is not a kill switch."),
    Gate("proof.gate_before_register", "proof", "ultra.proof",
         "when a done-test or gate is registered",
         checks=["done_test_executable", "planted_failure_receipt"],
         requires=["done_test_text", "done_test_cmds", "planted_failure_receipt"]),
    Gate("proof.seal_before_forecast_resolve", "proof", "ultra.proof",
         "before an outcome is written into the forecast ledger",
         checks=["chain_intact", "planted_failure_receipt"],
         escalate_is_blocking=True,
         requires=["chain_verified", "planted_failure_receipt", "artifact_text"],
         note="a forecast scored against unproven evidence corrupts calibration, which is the one thing that cannot be redone."),
    Gate("learning.variant_before_adopt", "learning", "ultra.learning",
         "before a prompt/rubric variant replaces the live one",
         checks=["held_out_improvement", "live_artifact_untouched"],
         requires=["variant_text", "live_text", "score_before", "score_after", "holdout_split_id"]),
    Gate("outward.gate_d", "execution", None,
         "any outward, spend, publish or irreversible action",
         checks=["human_decision_exists"],
         requires=["approval_quote", "action_text", "target"],
         requires_human=True,
         note="no pack: Jev cannot authorise an outward action. Code checks an approval exists; Mike decides."),
]}


# ---------------------------------------------------------------------------
# Derived metrics: computed in code, never asked of a model.
# ---------------------------------------------------------------------------

#: The 14 angle classes. `ANGLE_CLASSES` stays the readable label list for docs and
#: humans; the canonical key is the `cls` slug in the live `ultra.questioning` pack,
#: because that is what a tagging run actually writes back. Both spellings normalise
#: to the same key -- without this, a stage that records `customer/job` against a pack
#: whose option is `customer_job` would report every class missing and a coverage of 0.
ANGLE_CLASSES = [
    "customer/job", "buyer/money", "competitor/landscape", "technical feasibility",
    "distribution/channel", "timing/why-now", "legal/compliance", "people/capacity",
    "second-order effects", "failure modes", "exit/kill", "measurement",
    "dependencies/assumptions", "ethics/reputation",
]

_FALLBACK_SLUGS = [
    "customer_job", "buyer_money", "competitor_landscape", "technical_feasibility",
    "distribution_channel", "timing_why_now", "legal_compliance", "people_capacity",
    "second_order_effects", "failure_modes", "exit_kill", "measurement",
    "dependencies_assumptions", "ethics_reputation",
]


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")


def angle_slugs() -> List[str]:
    """The canonical class list, read from the live pack so the two cannot drift."""
    try:
        crit = load_rubric("ultra.questioning").questions["cls"]["criteria"]
        keys = list(crit)
        if len(keys) == len(_FALLBACK_SLUGS):
            return keys
    except Exception:  # noqa: BLE001 -- an unreadable pack must not break a meter
        pass
    return list(_FALLBACK_SLUGS)


def _canon_map() -> Dict[str, str]:
    slugs = angle_slugs()
    m = {_norm(s): s for s in slugs}
    for slug, label in zip(slugs, ANGLE_CLASSES):
        m.setdefault(_norm(label), slug)
    return m


def canonical_class(name: str) -> Optional[str]:
    return _canon_map().get(_norm(name))


def angle_label(slug: str) -> str:
    """Readable form of a canonical slug, for anything a human reads."""
    slugs = angle_slugs()
    if slug in slugs:
        return ANGLE_CLASSES[slugs.index(slug)]
    return slug


def coverage(counts: Dict[str, Any], minimum: int = 1) -> Dict[str, Any]:
    """Fraction of angle classes with at least `minimum` answered questions.

    An unreported class counts as missing, never as free credit. Keys may be pack
    slugs or readable labels; anything that is neither is reported as `unknown`
    rather than silently credited to the class it vaguely resembles.
    """
    slugs = angle_slugs()
    canon: Dict[str, int] = {}
    unknown: Dict[str, int] = {}
    for k, v in (counts or {}).items():
        c = canonical_class(k)
        try:
            n = int(v or 0)
        except (TypeError, ValueError):
            return {"coverage": None, "insufficient_input": "count for %r is not a number: %r" % (k, v),
                    "missing": slugs, "classes": len(slugs)}
        if c is None:
            unknown[k] = n
        else:
            canon[c] = canon.get(c, 0) + n
    missing = [c for c in slugs if canon.get(c, 0) < minimum]
    return {"coverage": round((len(slugs) - len(missing)) / float(len(slugs)), 4),
            "missing": missing, "missing_readable": [angle_label(c) for c in missing],
            "answered": canon, "classes": len(slugs), "unknown_classes": unknown}


def information(class_resolved: Dict[str, float]) -> Dict[str, Any]:
    """dq.information is the WEAKEST angle class, not the mean.

    A plan with one unresolved class has an unresolved class; averaging hides
    it. All 14 must be reported, or the answer is `insufficient_input` -- never
    a default 1.0.
    """
    slugs = angle_slugs()
    canon: Dict[str, float] = {}
    for k, v in (class_resolved or {}).items():
        c = canonical_class(k)
        if c is None or v is None:
            continue
        canon[c] = float(v)
    unknown = [k for k in (class_resolved or {}) if canonical_class(k) is None]
    if unknown:
        return {"dq_information": None, "insufficient_input": "unrecognised angle class(es): %s" % unknown,
                "worst_class": None}
    vals: Dict[str, float] = {}
    for c in slugs:
        if c not in canon:
            return {"dq_information": None, "insufficient_input": "no answer for %r" % c, "worst_class": None}
        vals[c] = canon[c]
    worst = min(vals, key=lambda k: vals[k])
    return {"dq_information": round(vals[worst], 4), "worst_class": worst,
            "worst_class_readable": angle_label(worst),
            "mean": round(statistics.fmean(vals.values()), 4)}


def trimmed_mean(values: List[float], trim: int = 1) -> Dict[str, Any]:
    """Swarm aggregation: drop the extremes rather than average one loud voice."""
    if not values:
        return {"value": None, "insufficient_input": "no forecasts to aggregate", "n": 0}
    n = len(values)
    if n < 3:
        return {"value": round(statistics.fmean(values), 4), "n": n, "trimmed": 0,
                "warning": "fewer than 3 forecasts: no trimming possible"}
    t = max(0, min(trim, (n - 1) // 2))
    mid = sorted(values)[t:n - t] if t else sorted(values)
    return {"value": round(statistics.fmean(mid), 4), "n": n, "trimmed": t}


# ---------------------------------------------------------------------------
# The router
# ---------------------------------------------------------------------------


def _reason_lines(answers: Dict[str, Any]) -> List[str]:
    """Code-owned reason strings. Jev returns numbers, never prose."""
    out = []
    for qname, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue
        t = ans.get("type")
        if t == "noul":
            out.append("%s.noul=%.2f" % (qname, float(ans.get("noul") or 0.0)))
        elif t == "choice":
            out.append("%s.choice=%s conf=%s" % (qname, ans.get("choice"), ans.get("confidence")))
        elif t == "score":
            out.append("%s.score=%s conf=%s" % (qname, ans.get("score"), ans.get("confidence")))
    return out


def route(
    gate_id: str,
    state: str,
    facts: Optional[Dict[str, Any]] = None,
    *,
    live: bool = False,
    subject: Optional[str] = None,
    log=None,
    model: Optional[str] = None,
    timeout: float = 20.0,
    evaluator: Callable[..., Any] = evaluate,
) -> Dict[str, Any]:
    """Decide the route for one declared gate. Never raises on a bad gate id.

    ``live=False`` (the default) does not contact the provider. That is not a
    pass: the route comes back ``offline_code_only`` with ``cleared`` False, so
    an unattended caller cannot mistake a code-only check for a cleared gate.
    """
    facts = dict(facts or {})
    gate = GATES.get(gate_id)
    if gate is None:
        return {"gate": gate_id, "studio": None, "pack": None, "route": Route.BLOCKED_UNKNOWN,
                "cleared": False, "advance": False, "human_required": True,
                "reasons": ["no gate %r is declared: refusing to invent one" % gate_id],
                "code_checks": [], "verdict": None, "advisory": False, "enforced": False,
                "jev": {}, "decision_id": None, "jev_skipped": True}

    reasons: List[str] = []
    checks: List[Dict[str, Any]] = []

    missing = [k for k in gate.requires if k not in facts]
    if missing:
        reasons.append("missing required facts: %s -- a missing input is not consent" % ", ".join(missing))

    code_failed = code_undecidable = False
    if not missing:
        for cname in gate.checks:
            fn = CODE_CHECKS.get(cname)
            if fn is None:
                code_undecidable = True
                checks.append({"check": cname, "ok": None, "note": "no such check registered"})
                continue
            try:
                ok, note = fn(facts)
            except Exception as exc:  # a broken check is not a passing check
                ok, note = None, "check %r raised %s: %s" % (cname, type(exc).__name__, exc)
            checks.append({"check": cname, "ok": ok, "note": note})
            if ok is False:
                code_failed = True
                reasons.append("code check %s failed: %s" % (cname, note))
            elif ok is None:
                code_undecidable = True
                reasons.append("code check %s returned no verdict: %s" % (cname, note))
    else:
        reasons.append("code checks skipped: required facts missing")

    base: Dict[str, Any] = {"gate": gate.id, "studio": gate.studio, "pack": gate.pack,
                            "code_checks": checks, "reasons": reasons, "jev": {},
                            "verdict": None, "advisory": False, "enforced": False,
                            "decision_id": None, "note": gate.note}

    def decide(r: str, **over) -> Dict[str, Any]:
        out = dict(base)
        out.update(over)
        out["route"] = r
        out["cleared"] = r in (Route.ADVANCE, Route.ANNOTATE_ADVANCE)
        out["advance"] = out["cleared"]
        out["human_required"] = bool(gate.requires_human)
        # Human authority overrides a *clear*, never a defect: a failed code check
        # stays rework so the artifact gets fixed, and the caller still sees
        # human_required=True telling them a clean pass was never the end state.
        if gate.requires_human and out["cleared"]:
            out["route"] = Route.HUMAN_CARD
            out["cleared"] = False
            out["advance"] = False
            out["reasons"] = list(out.get("reasons", reasons)) + [
                "requires_human: a machine PASS is a recommendation, not an authorisation"]
        return out

    if missing or code_failed:
        return decide(Route.REWORK if not gate.escalate_is_blocking else Route.ESCALATE_REVIEW,
                      jev_skipped=True)
    if code_undecidable:
        return decide(Route.ESCALATE_REVIEW, jev_skipped=True)

    if not live:
        return decide(Route.OFFLINE_CODE_ONLY, jev_skipped=True,
                      reasons=reasons + ["Jev not consulted (live=False): code checks only, not a cleared gate"])

    if gate.pack is None:
        return decide(Route.ADVANCE, jev_skipped=True,
                      reasons=reasons + ["no pack: this gate is code + human authority by design"])

    try:
        rb = load_rubric(gate.pack)
    except S1GateError as exc:
        return decide(Route.HALT_FAILCLOSED, jev_skipped=True,
                      reasons=reasons + ["pack %r unreadable: %s" % (gate.pack, exc)])

    try:
        res = evaluator(rb, state, subject=subject or gate.id, log=log, model=model, timeout=timeout)
    except Exception as exc:  # evaluator may raise before s1gate's own fail-closed path
        return decide(Route.HALT_FAILCLOSED, jev_skipped=True,
                      reasons=reasons + ["Jev call raised %s: %s" % (type(exc).__name__, exc)])

    merged = list(reasons) + list(res.reasons or []) + _reason_lines(getattr(res, "answers", {}))
    extra = {"verdict": res.verdict, "advisory": bool(res.advisory), "enforced": bool(res.enforced),
             "decision_id": res.decision_id, "jev": dict(res.answers or {}), "jev_skipped": False}

    if getattr(res, "error", None):
        return decide(Route.HALT_FAILCLOSED, reasons=merged + ["provider error: failing closed"], **extra)
    if any("undecidable" in r for r in (res.reasons or [])):
        # s1gate law 1: an undecidable rule escalates, it never passes quietly --
        # including when the pack is advisory. Malformed or missing answers land
        # here rather than being read as consent.
        return decide(Route.ESCALATE_REVIEW, reasons=merged + ["a rule could not be evaluated from the answers"], **extra)
    if res.verdict == PASS:
        return decide(Route.ADVANCE, reasons=merged, **extra)
    if res.verdict == BLOCK and res.enforced:
        return decide(Route.REWORK, reasons=merged, **extra)
    if res.advisory:
        # Law 3: uncalibrated. Annotate, do not halt -- unless this gate is a
        # kill switch, where an escalation is treated as blocking by design.
        r = Route.ESCALATE_REVIEW if gate.escalate_is_blocking else Route.ANNOTATE_ADVANCE
        return decide(r, reasons=merged + ["advisory only: pack not calibrated"], **extra)
    if res.verdict == BLOCK:
        return decide(Route.REWORK, reasons=merged, **extra)
    return decide(Route.ESCALATE_REVIEW, reasons=merged, **extra)


def contract() -> List[Dict[str, Any]]:
    """The route table as data, for docs and `rig-ultra contract`."""
    rows = []
    for g in GATES.values():
        d = asdict(g)
        d["pack_calibrated"] = None
        if g.pack:
            try:
                rb = load_rubric(g.pack)
                d["pack_calibrated"] = bool(rb.calibrated)
                d["pack_questions"] = sorted(rb.questions)
            except S1GateError as exc:
                d["pack_error"] = str(exc)
        rows.append(d)
    return rows


def coverage_from_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Turn one `ultra.questioning` answer set into the counts the meter wants.

    Convenience for a stage that has the Jev answers in hand and should not have to
    know the keying rules. A `cls` answer with no choice is not a zero: it is reported
    as unresolved, because crediting an unanswered class would inflate coverage.
    """
    counts: Dict[str, int] = {}
    for cls in angle_slugs():
        counts[cls] = 0
    for qname, ans in (answers or {}).items():
        if not isinstance(ans, dict):
            continue
        if ans.get("type") == "choice" and qname == "cls":
            c = canonical_class(ans.get("choice") or "")
            if c:
                counts[c] += 1
        elif ans.get("type") == "noul":
            continue
    return coverage(counts)
