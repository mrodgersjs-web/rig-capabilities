"""ULTRA plan-quality mechanics: diverge before converge, outside view before inside.

Both exist because the failure they prevent is specific and common:

* A plan with one option is not a plan, it is a decision already made. Five
  alternatives only count if they differ in *mechanism* -- five pricings of the
  same idea is one alternative. Checked structurally here, judged by Jev later.
* An inside-view estimate (this project's details) is systematically optimistic.
  The fix is arithmetic, not attitude: name a reference class, take its base
  rate, and only then adjust for this case.

Deterministic first: this module never calls a model. `ultra_gates` decides
whether the *content* is good; this decides whether the *structure* exists.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

__all__ = ["DIVERGE_MINIMUM", "diverge", "outside_view", "plan_facts", "UltraPlanError"]

#: Design hypothesis, not a measured constant. Five is the number the plan docs
#: have carried since the first draft; diverge() reports exactly what it
#: rejected, so the number can be argued with evidence instead of inherited.
DIVERGE_MINIMUM = 5

#: `name` or `title` labels an alternative; `mechanism` is what makes it a
#: different plan. A `why` that describes benefits is not a mechanism, so it is
#: not accepted -- five identical `why` strings must collapse to one alternative.
_LABEL_KEYS = ("name", "title")
_MECHANISM_KEYS = ("mechanism",)

#: A base rate from a class nobody counted is decoration, not an outside view.
MIN_CLASS_N = 5

#: Sources that mean "I made the number up". Checked case-folded and whole, so
#: a real citation containing the word is not punished.
_FILLER_SOURCES = {"vibes", "vibe", "guess", "a guess", "gut", "gut feel", "feel",
                   "tbd", "todo", "unknown", "none", "n/a", "self", "me", "author"}


class UltraPlanError(RuntimeError):
    pass


def _refused(reason, **extra):
    out = {"ok": False, "why": reason}
    out.update(extra)
    return out


def diverge(alternatives, minimum=DIVERGE_MINIMUM):
    """Are there `minimum` alternatives that differ in mechanism, not wording?

    Two alternatives sharing a mechanism string collapse into one. Mechanism is
    free text on purpose: the author has to write the phrase that makes them the
    same, which is the cheapest honest test available before Jev's
    `genuinely_different` pairwise call is calibrated.
    """
    if not isinstance(alternatives, list):
        return _refused("alternatives must be a list of objects, got %s" % type(alternatives).__name__)
    malformed = [i for i, a in enumerate(alternatives)
                 if not isinstance(a, dict)
                 or not any(str(a.get(k) or "").strip() for k in _LABEL_KEYS)
                 or not any(str(a.get(k) or "").strip() for k in _MECHANISM_KEYS)]
    if malformed:
        return _refused("alternatives %s need a label (name|title) and a mechanism: what structurally "
                        "differs, not what is good about it" % malformed,
                        count=len(alternatives), malformed=malformed)

    by_mech = {}
    for a in alternatives:
        key = " ".join(str(a["mechanism"]).lower().split())
        label = next(str(a[k]) for k in _LABEL_KEYS if str(a.get(k) or "").strip())
        by_mech.setdefault(key, []).append(label)
    collapsed = {m: names for m, names in by_mech.items() if len(names) > 1}
    distinct = len(by_mech)
    if distinct < minimum:
        detail = ("; collapsed: " + "; ".join("'%s' = %s" % (m, "+".join(n)) for m, n in collapsed.items())
                  if collapsed else "")
        return _refused("%d distinct mechanism%s, need %d%s"
                        % (distinct, "" if distinct == 1 else "s", minimum, detail),
                        count=len(alternatives), distinct_mechanisms=distinct, collapsed=collapsed)
    return {"ok": True, "count": len(alternatives), "distinct_mechanisms": distinct,
            "collapsed": collapsed, "minimum": minimum,
            "why": "%d distinct mechanisms >= %d" % (distinct, minimum)}


def outside_view(facts):
    """An estimate with no reference class is an opinion, so refuse it.

    Expected shape::

        {"reference_class": "governed AI studios, first 12 months to first revenue",
         "base_rate": 0.28,
         "base_rate_source": "https://... or a measured dataset id",
         "n_in_class": 41}
    """
    ref = str(facts.get("reference_class") or "").strip()
    if len(ref.split()) < 3:
        return _refused("no reference class named: this is an inside-view guess")
    rate = facts.get("base_rate")
    if rate is None:
        return _refused("reference class named but no base rate taken from it", reference_class=ref)
    try:
        rate = float(rate)
    except (TypeError, ValueError):
        return _refused("base rate is not a number: %r" % rate, reference_class=ref)
    if not 0.0 <= rate <= 1.0:
        return _refused("base rate %.4f is not a probability" % rate, reference_class=ref)
    src = str(facts.get("base_rate_source") or "").strip()
    if not src:
        return _refused("a base rate with no source is a number invented to look like evidence",
                        reference_class=ref, base_rate=rate)
    if src.lower().strip(". ") in _FILLER_SOURCES:
        return _refused("base_rate_source %r is not a source" % src, reference_class=ref, base_rate=rate)
    n = facts.get("n_in_class")
    if n is None:
        return _refused("no n_in_class: a base rate from an uncounted class is not an outside view",
                        reference_class=ref, base_rate=rate)
    try:
        n = int(n)
    except (TypeError, ValueError):
        return _refused("n_in_class is not a count: %r" % n, reference_class=ref)
    if n < MIN_CLASS_N:
        return _refused("reference class holds %d case%s: too thin to carry a rate, too thin to be outside"
                        % (n, "" if n == 1 else "s"), reference_class=ref, base_rate=rate, n_in_class=n)
    return {"ok": True, "reference_class": ref, "base_rate": rate, "n_in_class": n,
            "why": "outside view %.3f from %s (n=%s)" % (rate, src, n if n is not None else "unreported")}


def plan_facts(alternatives, ov=None, **extra):
    """Build the fact bag `plan.dq_before_build` expects so a caller cannot
    forget a field the gate needs. A missing piece stays missing: absent is a
    refusal, a default would be a lie.
    """
    facts = {"alternatives": alternatives}
    for source in [ov or {}, extra]:
        facts.update({k: v for k, v in source.items() if v is not None})
    return facts
