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
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .ultra_gates import trimmed_mean

__all__ = ["Ledger", "MIN_FORECASTERS", "MIN_FAMILIES", "MIN_RESOLVED_PER_FAMILY",
           "register_payload", "brier", "weights", "UltraForecastError"]

MIN_FORECASTERS = 5
MIN_FAMILIES = 2                 # docs propose 3; 2 is what code can refuse on
MIN_RESOLVED_PER_FAMILY = 4      # below this a family's Brier is noise

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
            cohort_id=None, author=None, author_family=None, resolve_on=None, ts=None):
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


def aggregate(records: Iterable[Dict[str, Any]], trim=1, drop_author=True, author=None):
    """Swarm number: trimmed mean, author-anchored voices dropped, diversity reported."""
    recs = list(records)
    if drop_author and author:
        recs = [r for r in recs if r.get("author") != author]
    probs = [float(r["probability"]) for r in recs]
    fams = sorted({r.get("family") or "?" for r in recs})
    out = trimmed_mean(probs, trim=trim)
    out["families"] = fams
    out["n_families"] = len(fams)
    out["n"] = len(probs)
    refusals = []
    if len(probs) < MIN_FORECASTERS:
        refusals.append("%d forecasts, need >= %d" % (len(probs), MIN_FORECASTERS))
    if len(fams) < MIN_FAMILIES:
        refusals.append("%d weight families, need >= %d" % (len(fams), MIN_FAMILIES))
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
