"""ULTRA forecast swarm ledger: register, aggregate, resolve, score, weight.

The swarm is the outside-view check on the plan author's own number, so the
rules are written to defeat that specific bias:

* forecasters are independent by construction (separate contexts, and separate
  model *weight families*: same-weights models agree for shared-pretraining
  reasons, not because the world is that predictable).
* the aggregate is a trimmed mean, because one confident voice moves a mean.
* nothing is weighted until it has been *resolved*. With no outcomes the only
  honest weight is uniform, and `weights()` says so rather than inventing one.
* the ledger is the source of truth. `register_payload()` produces the exact
  Memory OS `memory_issue_forecast` argument set, but it does not claim the call
  happened: `registered` stays False until a transport reports success.

Brier here is the standard mean squared error of probability vs outcome (0 =
perfect). Reported as a score, never as a verdict: a small crowd's Brier is
noisy, so `weights()` refuses on thin samples.

Correlation caveat (2026-10-01, conductor D-20261001-083903-8fab): separate
weight families are NOT independent oracles. Measured cross-family forecast
errors correlate at r~0.77 across GPT-4o/Claude/Gemini on 568 resolved binary
questions -- "a single oracle with noise, not three independent sources"
(Spiro, arXiv 2605.00844) -- and more accurate models correlate MORE
(arXiv 2506.07962, via secondary summary, origin not read); four frontier
agents gave the identical top pick on 92% of 104 matches with none beating
market Brier (arXiv 2607.17765). Consequences baked in below: (1) spread is
NOT independence -- narrow spread can be shared bias; (2) a deliberately
LOW-correlation member is required, not optional (Metaculus 43363 practice
survey [capture]: winners run 3-7 diverse runs plus one low-correlation
member; capping is the strongest within-winner differentiator, r=+0.48);
(3) probabilities are capped before aggregation; (4) Platt scaling
(calibration) may only be fitted on RESOLVED ledger pairs under the contract
in `platt_fit` -- a calibrator trained on too little history is worse than
none.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .ultra_gates import trimmed_mean

__all__ = ["Ledger", "MIN_FORECASTERS", "MIN_FAMILIES", "MIN_RESOLVED_PER_FAMILY",
           "MIN_LOW_CORRELATION", "CAP_BOUNDS", "PLATT_MIN_RESOLVED", "PLATT_REFIT_EVERY",
           "register_payload", "aggregate", "brier", "weights", "platt_fit", "platt_stale",
           "calibrate", "verify_aggregate", "UltraForecastError"]

MIN_FORECASTERS = 5
MIN_FAMILIES = 3                 # contract W04: three independent weight families.
                                 # Was 2 ("what code can refuse on"); three is what the
                                 # plan demands and what the boundary test pins (2026-09-20).
MIN_RESOLVED_PER_FAMILY = 4      # below this a family's Brier is noise
MIN_LOW_CORRELATION = 1          # one member outside the dominant training lineage;
                                 # families agree r~0.77 by construction (see docstring)
CAP_BOUNDS = (0.02, 0.98)        # winsorize member probabilities before aggregation;
                                 # extreme 0.99/0.01 voices are calibration failures, not
                                 # confidence (Metaculus 43363 [capture], r=+0.48 Brier)
PLATT_MIN_RESOLVED = 20          # fit floor: below this the calibrator is withheld
PLATT_REFIT_EVERY = 50           # refit cadence: every 50 newly resolved forecasts

#: horizon strings the Memory OS resolver accepts (schema-observed shapes)
_HORIZON_RE = None


class UltraForecastError(RuntimeError):
    pass


def _sha(*parts) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(("%r|" % (p,)).encode("utf-8"))
    return h.hexdigest()[:16]


class Ledger:
    """Append-only JSONL. One file per run, so a mission's crowd stays together."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # -- write ---------------------------------------------------------------
    def add(self, run, proposition, forecaster, family, probability, *,
            reasons_for=None, reasons_against=None, reference_class=None, base_rate=None,
            evidence_refs=None, trigger_event=None, target_event=None, horizon=None,
            cohort_id=None, author=None, author_family=None, resolve_on=None, ts=None,
            low_correlation=False):
        p = float(probability)
        if not 0.0 <= p <= 1.0:
            raise UltraForecastError("probability %.4f is not in [0,1]" % p)
        if not str(reasons_for or "").strip() or not str(reasons_against or "").strip():
            # Halawi et al.: generating considerations both ways is most of the
            # gain. A bare number is the thing we are trying to stop collecting.
            raise UltraForecastError("a forecast without considerations for AND against is a guess")
        if author_family and family == author_family:
            # The plan author's own model family re-derives the plan's number;
            # counting it as an independent voice manufactures agreement.
            raise UltraForecastError("forecaster %r shares the plan author's weight family %r"
                                     % (forecaster, family))
        rec = {
            "id": "fc-" + _sha(run, proposition, forecaster, p),
            "run": run, "proposition": proposition, "forecaster": forecaster, "family": family,
            "probability": round(p, 4),
            "reasons_for": str(reasons_for), "reasons_against": str(reasons_against),
            "reference_class": reference_class, "base_rate": base_rate,
            "evidence_refs": list(evidence_refs or []),
            "trigger_event": trigger_event, "target_event": target_event,
            "horizon": horizon, "cohort_id": cohort_id, "author": author,
            "resolve_on": resolve_on,
            "low_correlation": bool(low_correlation),
            "created_at": ts or time.time(),
            "registered": False, "registered_at": None, "transport_error": None,
            "outcome": None, "resolved_at": None,
        }
        self._append(rec)
        return rec

    def _append(self, rec):
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")

    def mark_registered(self, fc_id, ok, at=None, error=None):
        """Record what the transport actually said. Never called by add()."""
        return self._mutate(fc_id, {"registered": bool(ok),
                                    "registered_at": at if ok else None,
                                    "transport_error": None if ok else (error or "unknown")})

    def resolve(self, fc_id, outcome, at=None):
        if outcome not in (0, 1):
            raise UltraForecastError("outcome must be 0 or 1, got %r" % (outcome,))
        rec = self.get(fc_id)
        if rec is None:
            raise UltraForecastError("no forecast %r in %s" % (fc_id, self.path))
        if rec.get("outcome") is not None and rec["outcome"] != outcome:
            raise UltraForecastError("%s already resolved to %s; outcomes are not rewritten"
                                     % (fc_id, rec["outcome"]))
        return self._mutate(fc_id, {"outcome": int(outcome), "resolved_at": at or time.time()})

    def _mutate(self, fc_id, patch):
        recs = self.all()
        hit = False
        for i, r in enumerate(recs):
            if r.get("id") == fc_id:
                r = dict(r); r.update(patch); recs[i] = r; hit = True
                break
        if not hit:
            raise UltraForecastError("no forecast %r in %s" % (fc_id, self.path))
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
        os.replace(tmp, self.path)
        return recs[i]

    # -- read ----------------------------------------------------------------
    def all(self, run=None):
        if not self.path.exists():
            return []
        out = []
        for ln in self.path.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue  # a torn line is skipped, never repaired silently
            if run is None or rec.get("run") == run:
                out.append(rec)
        return out

    def get(self, fc_id):
        for r in self.all():
            if r.get("id") == fc_id:
                return r
        return None

    def pending(self):
        return [r for r in self.all() if not r.get("registered")]


def register_payload(rec: Dict[str, Any]) -> Dict[str, Any]:
    """The exact `memory_issue_forecast` argument set for one record.

    Building the payload is not sending it. The caller must pass this to the
    Memory OS and then `mark_registered(id, ok)` with what came back.
    """
    missing = [k for k in ("horizon", "proposition", "trigger_event", "target_event")
               if not str(rec.get(k) or "").strip()]
    if not rec.get("evidence_refs"):
        missing.append("evidence_refs")
    if missing:
        raise UltraForecastError("cannot register: missing %s" % ", ".join(missing))
    return {
        "resolver_id": rec.get("cohort_id") or "ultra",
        "horizon": rec["horizon"],
        "probability": "%.4f" % float(rec["probability"]),
        "cohort_id": rec.get("cohort_id") or "ultra-%s" % rec["run"],
        "proposition": rec["proposition"][:512],
        "trigger_event": rec["trigger_event"],
        "target_event": rec["target_event"],
        "evidence_refs": list(rec["evidence_refs"]),
    }


def aggregate(records: Iterable[Dict[str, Any]], trim=1, drop_author=True, author=None,
              cap_bounds=CAP_BOUNDS):
    """Swarm number: capped, trimmed mean; author-anchored voices dropped; diversity reported.

    Members are winsorized to `cap_bounds` before aggregation (extreme 0.99/0.01
    voices are calibration failures). `cap_bounds=None` disables capping --
    intended only for planted-failure tests; `verify_aggregate` goes red on any
    aggregate that skipped it. The correlation caveat travels with the result:
    spread is not independence (r~0.77 cross-family errors).
    """
    recs = list(records)
    if drop_author and author:
        recs = [r for r in recs if r.get("author") != author]
    raw = [float(r["probability"]) for r in recs]
    capped_count = 0
    if cap_bounds is not None:
        lo, hi = cap_bounds
        probs = []
        for p in raw:
            c = min(max(p, lo), hi)
            if c != p:
                capped_count += 1
            probs.append(c)
    else:
        probs = raw
    fams = sorted({r.get("family") or "?" for r in recs})
    low_corr = sum(1 for r in recs if r.get("low_correlation"))
    out = trimmed_mean(probs, trim=trim)
    out["families"] = fams
    out["n_families"] = len(fams)
    out["n"] = len(probs)
    out["capped_count"] = capped_count
    out["cap_bounds"] = cap_bounds
    out["low_correlation_members"] = low_corr
    out["correlation_caveat"] = (
        "separate weight families are not independent oracles: cross-family errors "
        "correlate r~0.77 (arXiv 2605.00844); spread is not independence")
    refusals = []
    if len(probs) < MIN_FORECASTERS:
        refusals.append("%d forecasts, need >= %d" % (len(probs), MIN_FORECASTERS))
    if len(fams) < MIN_FAMILIES:
        refusals.append("%d weight families, need >= %d" % (len(fams), MIN_FAMILIES))
    if not refusals and low_corr < MIN_LOW_CORRELATION:
        # checked only for an otherwise-strength-sufficient swarm: an
        # under-strength crowd has bigger problems and its refusals say so.
        refusals.append("no deliberately low-correlation member (need >= %d: a family "
                        "outside the dominant training lineage, flagged low_correlation)"
                        % MIN_LOW_CORRELATION)
    out["refusals"] = refusals
    out["diverse"] = not refusals
    return out


def brier(pairs: List) -> Dict[str, Any]:
    """Mean squared error over (probability, outcome) pairs. Empty -> None."""
    if not pairs:
        return {"brier": None, "n": 0, "insufficient": "no resolved forecasts"}
    vals = []
    for p, o in pairs:
        p, o = float(p), int(o)
        if not 0.0 <= p <= 1.0 or o not in (0, 1):
            raise UltraForecastError("bad pair (%r, %r)" % (p, o))
        vals.append((p - o) ** 2)
    return {"brier": round(sum(vals) / len(vals), 4), "n": len(vals)}


def weights(resolved: List[Dict[str, Any]], min_n=MIN_RESOLVED_PER_FAMILY) -> Dict[str, Any]:
    """Per-family skill from resolved outcomes only. Thin evidence -> uniform.

    A weight derived from two forecasts would move the swarm on noise, so it is
    withheld and the reason is stated.
    """
    by: Dict[str, List] = {}
    for r in resolved:
        if r.get("outcome") is None:
            continue
        by.setdefault(r.get("family") or "?", []).append((float(r["probability"]), int(r["outcome"])))
    scored, thin = {}, {}
    for fam, pairs in by.items():
        if len(pairs) < min_n:
            thin[fam] = "%d resolved (< %d); weight withheld" % (len(pairs), min_n)
            continue
        scored[fam] = brier(pairs)
    if not scored:
        return {"weights": None, "uniform": True, "why": "no family has enough resolved forecasts; weights are uniform by law, not by default",
                "thin": thin, "scored": scored}
    inv = {f: 1.0 / max(s["brier"], 1e-3) for f, s in scored.items()}
    tot = sum(inv.values())
    w = {f: round(v / tot, 4) for f, v in inv.items()}
    for fam in thin:
        w[fam] = None
    return {"weights": w, "uniform": False, "scored": scored, "thin": thin,
            "why": "inverse-Brier over %d resolved forecasts; %d family/families unweighted"
                   % (sum(s["n"] for s in scored.values()), len(thin))}


def _logit(p: float) -> float:
    p = min(max(float(p), 1e-6), 1 - 1e-6)
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def platt_fit(resolved: List[Dict[str, Any]], *, min_n=PLATT_MIN_RESOLVED,
              refit_every=PLATT_REFIT_EVERY, last_fit=None) -> Dict[str, Any]:
    """Fit (or withhold) a Platt calibrator on RESOLVED ledger pairs only.

    The fit contract (conductor D-20261001-083903-8fab, condition 2):

    * FITTED ON: (probability, outcome) pairs from resolved forecasts in this
      ledger -- never on unregistered or unresolved numbers, never on another
      cohort's history.
    * FORM: p_cal = sigmoid(a * logit(p) + b), (a, b) by grid + local refine on
      log-loss.
    * WITHHELD (fit=None) when: fewer than `min_n` resolved pairs, or the
      outcomes are single-class (all 0 or all 1 -- nothing to calibrate
      toward). A calibrator trained on too little history is worse than none.
    * REFIT CADENCE: every `refit_every` newly resolved forecasts. `last_fit`
      (a previous return value) carries `fit_n`; when the ledger has grown by
      `refit_every` since, `platt_stale()` is True and the caller must refit.
    """
    pairs = []
    for r in resolved:
        if r.get("outcome") is None:
            continue
        pairs.append((float(r["probability"]), int(r["outcome"])))
    n = len(pairs)
    classes = {o for _, o in pairs}
    base = {"fit": None, "fit_n": n, "refit_every": refit_every, "min_n": min_n,
            "fitted_on": "resolved ledger (probability, outcome) pairs"}
    if n < min_n:
        base["why"] = ("calibrator withheld: %d resolved pairs (< %d); a calibrator "
                       "trained on too little history is worse than none" % (n, min_n))
        return base
    if len(classes) < 2:
        base["why"] = ("calibrator withheld: single-class outcomes %s; nothing to "
                       "calibrate toward" % sorted(classes))
        return base
    # grid + local refine of (a, b) minimizing log-loss; pure stdlib, no numpy.
    def logloss(a, b):
        s = 0.0
        for p, o in pairs:
            q = min(max(_sigmoid(a * _logit(p) + b), 1e-9), 1 - 1e-9)
            s -= (o * math.log(q) + (1 - o) * math.log(1 - q))
        return s / n
    best = (1.0, 0.0)
    best_ll = logloss(*best)
    for a in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0]:
        for b in [-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0]:
            ll = logloss(a, b)
            if ll < best_ll:
                best, best_ll = (a, b), ll
    step = 0.25
    for _ in range(6):
        a0, b0 = best
        for da in (-step, 0.0, step):
            for db in (-step, 0.0, step):
                cand = (a0 + da, b0 + db)
                ll = logloss(*cand)
                if ll < best_ll:
                    best, best_ll = cand, ll
        step /= 2.0
    base["fit"] = {"a": round(best[0], 4), "b": round(best[1], 4),
                   "log_loss": round(best_ll, 4)}
    base["why"] = ("platt fitted on %d resolved pairs (both outcome classes); "
                   "refit every %d newly resolved" % (n, refit_every))
    return base


def platt_stale(fit_result: Dict[str, Any], resolved_now: int) -> bool:
    """True when the calibrator is past its refit cadence (or was withheld)."""
    if not fit_result or not fit_result.get("fit"):
        return True
    return int(resolved_now) - int(fit_result.get("fit_n") or 0) >= int(
        fit_result.get("refit_every") or PLATT_REFIT_EVERY)


def calibrate(p: float, fit_result: Dict[str, Any]) -> float:
    """Apply a fitted Platt calibrator. A withheld calibrator refuses -- it never
    silently passes numbers through as if they were calibrated."""
    if not fit_result or not fit_result.get("fit"):
        raise UltraForecastError("no fitted calibrator: %s"
                                 % ((fit_result or {}).get("why") or "missing fit"))
    f = fit_result["fit"]
    return round(_sigmoid(float(f["a"]) * _logit(p) + float(f["b"])), 4)


def verify_aggregate(out: Dict[str, Any]) -> Dict[str, Any]:
    """Attestation for an aggregate: goes RED on the planted failures.

    Red when: capping was skipped (`cap_bounds` absent / None), the correlation
    caveat is missing, or a diverse swarm has no low-correlation member. This is
    the check the planted-failure harness proves can fail.
    """
    reasons = []
    if out.get("cap_bounds") is None or "capped_count" not in out:
        reasons.append("capping skipped: member probabilities were not winsorized")
    if not str(out.get("correlation_caveat") or "").strip():
        reasons.append("correlation caveat missing: spread is being passed off as independence")
    if out.get("diverse") and int(out.get("low_correlation_members") or 0) < MIN_LOW_CORRELATION:
        reasons.append("low-correlation slot empty on a diverse swarm")
    return {"ok": not reasons, "reasons": reasons}
