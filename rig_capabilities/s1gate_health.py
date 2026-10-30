"""s1gate health and drift -- the gate's own alarm panel.

Why this exists (shipwithjev.com doctrine, judge-drift-monitoring, 2026-10-01):
"A judge pipeline rarely breaks loudly. Nothing throws, latency looks fine, the
dashboard stays green, and three weeks later someone notices the spam rate
halved without anyone fixing spam."

Measured state on 2026-10-01, before this module existed:
    109 rubrics loadable, 0 ENFORCING (105 advisory, 4 advisory+never_auto)
    124,527 logged decisions: BLOCK 0.7% / ESCALATE 41.2% / PASS 58.1%
    per-rubric escalation: mission.completion 100%, jobhunt.hm 99.5%,
                           ultra.proof 98.5%, memory.admission 84.6%

Nobody had printed those numbers together. This module prints them, and every
number comes with the verb it implies. A metric with no action attached is a
dashboard, and a dashboard is not a control.

Two failure shapes this is built to catch, both from the same doctrine:
  * the escalation black hole -- a rubric escalating nearly everything is not
    cautious, it is "a slower way of dropping cases";
  * silent calibration voiding -- `Rubric.rule_enforces` drops a rule back to
    advisory when its hashes stop matching, which is safe but INVISIBLE. Work
    that calibrated a rule is thrown away without anyone being told.

Naming note: `rig_capabilities/canary.py` is the V40 anti-fabrication canary
(a planted failing test that catches invented work). The frozen canary this
module reads is the other thing entirely -- a fixed set of inputs re-run to
separate MODEL drift from INPUT drift. Different mechanism, different files.

Exit-code contract, same as rig-s1gate: 0 healthy, 1 action needed, 3 usage.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .s1gate import (
    DB_PATH,
    JEV_MODEL,
    RUBRIC_DIR,
    _rule_signal,
    list_rubrics,
    load_rubric,
    rule_canonical_sha,
    rubric_canonical_sha,
)


def _resolved_model(timeout: float = 8.0) -> str:
    """Which concrete model does the requested alias actually serve?

    A certification binds to the model that ANSWERED, not the alias asked for
    (s1gate.evaluate: `judged = body["model"]`). The health panel used to compare
    against the alias instead, so every rule calibrated on jev-1.13.0 was
    reported VOIDED the moment the default alias read "jev-latest" -- even though
    the alias serves the same weights and the gate still honours those
    calibrations. This asks the endpoint once, cached per process, so the panel
    judges the same thing the gate does. Returns "" if unreachable, and the
    caller then falls back to the alias-only comparison.
    """
    cached = globals().get("_ALIAS_RESOLVED")
    if cached is not None:
        return cached
    resolved = ""
    if os.environ.get("S1GATE_HEALTH_RESOLVE", "1") != "0":
        try:
            from .s1gate import ask  # local import: health must not cost a call
            body = ask("liveness probe: is the service up?",
                       {"up": {"type": "noul", "instructions":
                               "Is the service responding normally"}},
                       timeout=timeout, retries=0)
            resolved = str(body.get("model") or "")
        except Exception:
            resolved = ""
    globals()["_ALIAS_RESOLVED"] = resolved
    return resolved

# Frozen-canary snapshots live beside the rubrics, NOT in rig_capabilities/, so
# the gate's data stays with the gate and away from the V40 canary's lease tree.
CANARY_DIR = Path(RUBRIC_DIR).parent / "frozen-canary"
CANARY_BASELINE = CANARY_DIR / "baseline.json"
CANARY_HISTORY = CANARY_DIR / "history.jsonl"
GOLD_DIR = Path(RUBRIC_DIR).parent / "gold"

# Thresholds for the detectors. These are deliberately opinionated defaults;
# each is overridable from the CLI so a caller can tune without editing code.
BLACK_HOLE_ESCALATION = 0.50   # above this, with enough volume: not cautious, broken
DEAD_GATE_ESCALATION = 0.02    # below this, with enough volume: the gate stopped gating
MIN_RUBRIC_VOLUME = 100        # below this a rate is noise, not a signal
HYGIENE_BLANK_WARN = 0.10      # >10% unattributable rows means the log cannot be audited
COVERAGE_WARN = 0.25           # fewer than 25% of kinds carrying gold cases


def _pct(num: float, den: float) -> Optional[float]:
    return None if not den else round(100.0 * num / den, 1)


def _conn_ro(db_path: Optional[Path] = None) -> Optional[sqlite3.Connection]:
    """Read-only connection. Returns None when the log does not exist yet, which
    is a fact to report -- never an empty success."""
    p = Path(db_path or DB_PATH)
    if not p.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


# --------------------------------------------------------------------------
# 1. Enforcement coverage and calibration voiding
# --------------------------------------------------------------------------

def enforcement_report() -> Dict[str, Any]:
    """Which rubrics can actually stop anything, and whose calibration rotted.

    `Rubric.rule_enforces` is hash-bound on purpose: edit the rule, edit the
    rubric, or switch the judging model and the certification voids. That is
    correct behaviour -- it refuses to enforce on stale evidence -- but it does
    it silently. Here we name every rule that is sitting on a void cert.
    """
    enforcing: List[str] = []
    advisory: List[str] = []
    voided: List[Dict[str, Any]] = []
    uncertified: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    for name in list_rubrics():
        try:
            rb = load_rubric(name)
        except Exception as exc:  # noqa: BLE001 - a broken rubric is a finding
            errors.append({"rubric": name, "error": str(exc)})
            continue

        # Enforcement is derived, and Rubric.enforcing calls rule_enforces with no
        # model, so it compares each entry to the requested ALIAS. That reported
        # "0 enforcing" while the gate itself was enforcing. Compute it against the
        # model that actually answers -- the same question the runtime asks.
        judged = _resolved_model() or JEV_MODEL
        live = bool(rb.rules) and all(rb.rule_enforces(r, model=judged) for r in rb.rules)
        (enforcing if live else advisory).append(name)

        entries = (rb.calibration or {}).get("rules") or {}
        for rule in rb.rules or []:
            sig = _rule_signal(rule)
            entry = entries.get(sig) if sig else None
            if not entry:
                if rule not in uncertified:
                    uncertified.append({"rubric": name, "signal": sig,
                                        "reason": "no calibration record"})
                continue
            # Ask the same question the runtime asks: would this rule enforce
            # against the model that actually answers? The runtime passes the
            # RESPONSE model (s1gate.py: `judged`); passing nothing here compared
            # the entry to the requested alias and reported live, working
            # calibrations as void.
            if rb.rule_enforces(rule, model=judged):
                continue
            # It has a record but does not enforce: work out which invariant broke.
            # Compare against the model that ANSWERED, same rule the gate uses.
            judged = {m for m in (JEV_MODEL, _resolved_model()) if m}
            if entry.get("model") not in judged:
                why = "model changed (%s -> %s)" % (entry.get("model"), JEV_MODEL)
            elif entry.get("rule_sha256") != rule_canonical_sha(rule):
                why = "rule text changed since calibration (rule_sha256 mismatch)"
            elif entry.get("rubric_sha256") != rubric_canonical_sha(rb):
                why = "rubric changed since calibration (rubric_sha256 mismatch)"
            elif entry.get("label_scope") != "signal" and (
                    len(rb.questions) > 1
                    or len({_rule_signal(r) for r in rb.rules}) > 1):
                why = "needs signal-scoped labels; only whole-decision labels exist"
            else:
                why = "certification does not satisfy rule_enforces"
            voided.append({"rubric": name, "signal": sig,
                           "calibrated_on": entry.get("on") or entry.get("ts"),
                           "why": why})

    total = len(enforcing) + len(advisory)
    findings: List[Dict[str, Any]] = []

    if total and not enforcing:
        findings.append({
            "id": "no-enforcement",
            "severity": "action",
            "metric": "rubrics ENFORCING",
            "value": 0,
            "detail": "%d of %d rubrics are advisory; the gate currently stops "
                      "nothing. advisory_until_calibrated is true, so this is "
                      "honest -- but it must not be mistaken for protection."
                      % (total, total),
            "action": "Calibrate the rubrics that matter most. Use "
                      "`rig-s1gate label <id> good|bad --signal Q.ATTR` then "
                      "`rig-s1gate calibrate <rubric> --signal Q.ATTR --write`. "
                      "Start with the highest-volume rubrics in the health report.",
        })
    if voided:
        findings.append({
            "id": "calibration-void",
            "severity": "action",
            "metric": "rules with voided calibration",
            "value": len(voided),
            "detail": "These had certification and silently lost it. The gate "
                      "dropped back to advisory without telling anyone.",
            "action": "Re-run `rig-s1gate calibrate` for each signal below. "
                      "Do not edit a calibrated rule without expecting to "
                      "recalibrate it -- the hash binding is doing its job.",
            "rules": voided,
        })
    if errors:
        findings.append({
            "id": "rubric-load-errors",
            "severity": "action",
            "metric": "rubrics that fail to load",
            "value": len(errors),
            "detail": "A rubric that cannot load cannot judge.",
            "action": "Fix the JSON. `rig-s1gate list` prints each load error.",
            "rules": errors,
        })

    return {
        "total": total,
        "enforcing": enforcing,
        "advisory_count": len(advisory),
        "voided": voided,
        "uncertified_rules": len(uncertified),
        "load_errors": errors,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# 2. Escalation rate -- "the single most useful signal"
# --------------------------------------------------------------------------

def escalation_report(min_volume: int = MIN_RUBRIC_VOLUME,
                      black_hole: float = BLACK_HOLE_ESCALATION,
                      dead_gate: float = DEAD_GATE_ESCALATION,
                      db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Escalation rate in both directions.

    Doctrine: "A rising escalation rate means questions and reality are
    diverging. A rate falling toward zero is worse, because it usually means the
    gate broke, a threshold got edited, or inputs went empty and started
    producing confident nonsense. Alert on both edges."
    """
    conn = _conn_ro(db_path)
    if conn is None:
        return {
            "available": False,
            "detail": "no decision log at %s -- nothing has been judged yet"
                      % (db_path or DB_PATH),
            "findings": [{
                "id": "no-decision-log",
                "severity": "info",
                "metric": "decision log",
                "value": 0,
                "action": "Run one `rig-s1gate check` to create the log.",
            }],
        }

    try:
        where = "COALESCE(excluded,0)=0 AND TRIM(COALESCE(subject,''))!=''"
        tot = conn.execute(
            f"SELECT COUNT(*) n, SUM(verdict='ESCALATE') e, SUM(verdict='BLOCK') b,"
            f" SUM(verdict='PASS') p FROM decisions WHERE {where}").fetchone()
        overall = {
            "decisions": tot["n"] or 0,
            "escalate": tot["e"] or 0,
            "block": tot["b"] or 0,
            "pass": tot["p"] or 0,
        }
        overall["escalation_rate_pct"] = _pct(overall["escalate"], overall["decisions"])

        rows = conn.execute(
            f"SELECT rubric, COUNT(*) n, SUM(verdict='ESCALATE') e,"
            f" SUM(verdict='BLOCK') b, SUM(verdict='PASS') p"
            f" FROM decisions WHERE {where} GROUP BY rubric ORDER BY n DESC"
        ).fetchall()
    finally:
        conn.close()

    per: List[Dict[str, Any]] = []
    black: List[Dict[str, Any]] = []
    dead: List[Dict[str, Any]] = []
    for r in rows:
        n, e = r["n"] or 0, r["e"] or 0
        rate = (e / n) if n else 0.0
        entry = {
            "rubric": r["rubric"], "decisions": n, "escalate": e,
            "block": r["b"] or 0, "pass": r["p"] or 0,
            "escalation_rate_pct": _pct(e, n),
        }
        per.append(entry)
        if n >= min_volume and rate >= black_hole:
            black.append(entry)
        if n >= min_volume and rate <= dead_gate:
            dead.append(entry)

    findings: List[Dict[str, Any]] = []
    if black:
        findings.append({
            "id": "escalation-black-hole",
            "severity": "action",
            "metric": "rubrics escalating >%d%% of the time" % int(black_hole * 100),
            "value": len(black),
            "detail": "A review queue without an owner, a service level, or a "
                      "daily count is just a slower way of dropping cases. These "
                      "are not being cautious; they are declining to decide.",
            "action": "For each: either sharpen the question so it can rule "
                      "(legislate the edges inside the question), or accept the "
                      "slice as permanently-escalating and route it straight to "
                      "its owner instead of through the gate.",
            "rubrics": black,
        })
    if dead:
        findings.append({
            "id": "gate-not-gating",
            "severity": "action",
            "metric": "rubrics escalating <%d%% of the time" % int(dead_gate * 100),
            "value": len(dead),
            "detail": "A rate falling toward zero usually means the gate broke, a "
                      "threshold got edited, or inputs went empty and started "
                      "producing confident nonsense.",
            "action": "Confirm the inputs are non-empty, then re-run the frozen "
                      "canary. If the canary still passes everything, the "
                      "question lost its teeth -- reword it.",
            "rubrics": dead,
        })

    return {
        "available": True,
        "overall": overall,
        "per_rubric": per,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# 3. Corpus hygiene -- can the log be audited at all?
# --------------------------------------------------------------------------

def hygiene_report(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Rows that cannot be attributed or are quarantined. An unattributable
    decision cannot be labelled, and an unlabelable decision cannot calibrate
    anything."""
    conn = _conn_ro(db_path)
    if conn is None:
        return {"available": False, "findings": []}
    try:
        row = conn.execute(
            "SELECT COUNT(*) total,"
            " SUM(TRIM(COALESCE(subject,''))='') blank,"
            " SUM(COALESCE(excluded,0)=1) quarantined"
            " FROM decisions").fetchone()
    finally:
        conn.close()
    total = row["total"] or 0
    blank, quar = row["blank"] or 0, row["quarantined"] or 0
    clean = total - blank - quar
    findings: List[Dict[str, Any]] = []
    if total and (blank / total) > HYGIENE_BLANK_WARN:
        findings.append({
            "id": "unattributable-rows",
            "severity": "action",
            "metric": "rows with no subject",
            "value": blank,
            "detail": "%.1f%% of the log cannot be attributed. The decision log "
                      "refuses unattributable rows at the CLI for exactly this "
                      "reason; these predate or bypass that check."
                      % (100.0 * blank / total),
            "action": "Find the callers passing --subject blank and fix them. "
                      "Until then these rows cannot calibrate anything.",
        })
    return {
        "available": True,
        "total": total, "blank_subject": blank,
        "quarantined": quar, "clean": clean,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# 4. Gold coverage
# --------------------------------------------------------------------------

def gold_report() -> Dict[str, Any]:
    """How much ground truth exists per kind.

    Doctrine: "a few hundred cases per question as a working floor", and the
    regression-case rule -- every production mistake someone catches becomes a
    permanent gold case and is never deleted.
    """
    kinds = list_rubrics()
    manifest = GOLD_DIR / "gold.json"
    cases: Dict[str, Any] = {}
    if manifest.exists():
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
            # The manifest is {schema, rules, provenance_note, kinds:{...}}.
            # Iterating the top level here silently reported 0 of 109 covered
            # while 25 cases sat one key down. An empty result from a check you
            # just wrote is more often a check bug than an absence.
            cases = doc.get("kinds", {}) if isinstance(doc, dict) else {}
        except json.JSONDecodeError as exc:
            return {
                "available": False,
                "findings": [{
                    "id": "gold-manifest-unreadable",
                    "severity": "action",
                    "metric": "gold.json",
                    "value": 0,
                    "detail": str(exc),
                    "action": "Repair gold/gold.json -- it is the answer key and "
                              "an unreadable key is worse than none.",
                }],
            }

    covered = sorted(k for k in cases if k in kinds)
    counts = {k: len(cases[k].get("cases", []) if isinstance(cases[k], dict) else cases[k])
              for k in covered}
    regression = sum(1 for k in covered
                     for c in (cases[k].get("cases", []) if isinstance(cases[k], dict) else [])
                     if isinstance(c, dict) and c.get("regression"))

    findings: List[Dict[str, Any]] = []
    share = (len(covered) / len(kinds)) if kinds else 0.0
    if kinds and share < COVERAGE_WARN:
        findings.append({
            "id": "thin-gold-coverage",
            "severity": "action",
            "metric": "kinds carrying gold cases",
            "value": len(covered),
            "detail": "%d of %d kinds (%.0f%%). Every accuracy number the estate "
                      "reports is measured against this set, and right now most "
                      "of it is measured against nothing."
                      % (len(covered), len(kinds), 100.0 * share),
            "action": "Add gold cases for the highest-volume kinds first "
                      "(see the escalation report). Stratify: boring, boundary, "
                      "adversarial, regression. Label blind, twice, adjudicate.",
        })
    return {
        "available": True,
        "kinds_total": len(kinds),
        "kinds_covered": len(covered),
        "coverage_pct": _pct(len(covered), len(kinds)),
        "case_counts": counts,
        "regression_cases": regression,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# 5. The frozen canary -- model drift vs input drift
# --------------------------------------------------------------------------

def canary_report(now: Optional[str] = None) -> Dict[str, Any]:
    """Compare the newest canary snapshot against the frozen baseline.

    The one comparison that settles a drift argument in minutes:
      canary verdicts moved, config unchanged  -> the MODEL moved
      canary steady, production shifted        -> the INPUTS moved
    """
    if not CANARY_BASELINE.exists():
        return {
            "available": False,
            "detail": "no frozen baseline at %s" % CANARY_BASELINE,
            "findings": [{
                "id": "no-canary-baseline",
                "severity": "action",
                "metric": "frozen canary baseline",
                "value": 0,
                "action": "Seed it once: `rig-s1gate canary seed`. Then it never "
                          "changes -- that is the whole point of freezing it.",
            }],
        }

    try:
        base = json.loads(CANARY_BASELINE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"available": False, "findings": [{
            "id": "canary-baseline-unreadable", "severity": "action",
            "metric": "baseline.json", "value": 0, "detail": str(exc),
            "action": "Repair frozen-canary/baseline.json or re-seed it.",
        }]}

    snapshots: List[Dict[str, Any]] = []
    if CANARY_HISTORY.exists():
        for line in CANARY_HISTORY.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                snapshots.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    newest = snapshots[-1] if snapshots else None
    findings: List[Dict[str, Any]] = []
    moved: List[Dict[str, Any]] = []
    if newest:
        bmap = {c["id"]: c for c in base.get("cases", [])}
        for c in newest.get("cases", []):
            b = bmap.get(c.get("id"))
            if not b:
                continue
            want = _norm(b.get("expect") or b.get("verdict"))
            got = _norm(c.get("verdict"))
            if want is not None and got is not None and want != got:
                moved.append({
                    "id": c.get("id"),
                    "baseline_verdict": want,
                    "new_verdict": got,
                    "baseline_conf": b.get("confidence"),
                    "new_conf": c.get("confidence"),
                })
        if moved:
            findings.append({
                "id": "canary-moved",
                "severity": "action",
                "metric": "frozen cases whose verdict changed",
                "value": len(moved),
                "detail": "These inputs are frozen and the questions are pinned, "
                          "so a change here is not the world moving. If no config "
                          "changed, the model moved -- check the provider's "
                          "changelog before blaming your questions.",
                "action": "Diff config first (question drift is self-inflicted "
                          "and fastest to confirm), then check whether "
                          + JEV_MODEL + " was updated.",
                "cases": moved,
            })

    return {
        "available": True,
        "model": base.get("model"),
        "frozen_cases": len(base.get("cases", [])),
        "snapshots": len(snapshots),
        "newest_at": newest.get("ts") if newest else None,
        "moved": moved,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# 5b. Seeding and running the frozen canary
# --------------------------------------------------------------------------

def canary_seed(cases: List[Dict[str, Any]], model: Optional[str] = None,
                now: Optional[str] = None) -> Dict[str, Any]:
    """Freeze a set of inputs ONCE. Nothing here is ever updated in place.

    Each case is {id, rubric, state, expect?}. `expect` is the human answer if
    you have one -- it turns the canary into a daily accuracy check as well as a
    drift check. Deliberately refuses to overwrite an existing baseline: a
    baseline you can quietly refresh is not a baseline.
    """
    if CANARY_BASELINE.exists():
        raise S1GateHealthError(
            "baseline already exists at %s. Freezing is the point -- if you "
            "really mean to re-freeze, delete it first and say so." % CANARY_BASELINE)
    if not cases:
        raise S1GateHealthError("canary seed needs at least one case")
    seen: set = set()
    clean: List[Dict[str, Any]] = []
    for i, c in enumerate(cases):
        cid = str(c.get("id") or "case-%03d" % i)
        if cid in seen:
            raise S1GateHealthError("duplicate canary id %r" % cid)
        seen.add(cid)
        if not c.get("rubric") or not c.get("state"):
            raise S1GateHealthError("case %r needs both rubric and state" % cid)
        clean.append({"id": cid, "rubric": c["rubric"], "state": c["state"],
                      "expect": c.get("expect")})
    CANARY_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "frozen_at": now or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": model or JEV_MODEL,
        "note": "FROZEN. Never update in place -- see s1gate_health.canary_report.",
        "cases": clean,
    }
    CANARY_BASELINE.write_text(json.dumps(payload, indent=2, sort_keys=True),
                               encoding="utf-8")
    return payload


def canary_run(model: Optional[str] = None, now: Optional[str] = None) -> Dict[str, Any]:
    """Re-run the frozen set and append a snapshot. Compares against baseline.

    Deliberately passes ``log=None`` to evaluate(): canary rows are excluded from
    production statistics, so a canary run can never distort the escalation rate
    it is there to explain.
    """
    from .s1gate import evaluate as _evaluate  # local: keeps import cost off --help

    if not CANARY_BASELINE.exists():
        raise S1GateHealthError("no baseline. Seed it first: rig-s1gate canary seed --file CASES.json")
    base = json.loads(CANARY_BASELINE.read_text(encoding="utf-8"))
    m = model or base.get("model") or JEV_MODEL

    results: List[Dict[str, Any]] = []
    for c in base.get("cases", []):
        row: Dict[str, Any] = {"id": c["id"], "rubric": c["rubric"]}
        try:
            res = _evaluate(c["rubric"], c["state"],
                            subject="frozen-canary:%s" % c["id"],
                            log=None, model=m)
            row.update({"verdict": res.verdict, "advisory": res.advisory})
            row["confidence"] = _top_confidence(res)
        except Exception as exc:  # noqa: BLE001 - an error is a snapshot too
            row.update({"verdict": "ERROR", "error": str(exc)})
        results.append(row)

    snap = {"ts": now or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "model": m, "cases": results}
    CANARY_DIR.mkdir(parents=True, exist_ok=True)
    with CANARY_HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(snap, sort_keys=True) + "\n")

    bmap = {c["id"]: c for c in base.get("cases", [])}
    moved = []
    for r in results:
        b = bmap.get(r["id"])
        if not b:
            continue
        want = _norm(b.get("expect")) or _norm(_baseline_verdict(r["id"]))
        got = _norm(r.get("verdict"))
        if want is not None and got is not None and want != got:
            moved.append({"id": r["id"], "baseline_verdict": want,
                          "new_verdict": got,
                          "raw_verdict": r.get("verdict")})
    snap["moved"] = moved
    return snap


def _norm(v: Optional[str]) -> Optional[str]:
    """Map both vocabularies onto one. expect is green|red; verdict is
    PASS|BLOCK|ESCALATE. Comparing them raw made the FIRST run report every
    case as moved -- a false alarm from a vocabulary mismatch, not drift.
    Found by running the check once, which is the only way to find it."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("green", "pass", "ok", "true"):
        return "green"
    if s in ("red", "block", "escalate", "fail", "false"):
        return "red"
    return s


def _baseline_verdict(cid: str) -> Optional[str]:
    """Verdict recorded in the first snapshot, if any -- the de-facto baseline."""
    if not CANARY_HISTORY.exists():
        return None
    for line in CANARY_HISTORY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            s = json.loads(line)
        except json.JSONDecodeError:
            continue
        for c in s.get("cases", []):
            if c.get("id") == cid:
                return c.get("verdict")
    return None


def _top_confidence(res) -> Optional[float]:
    """Best-effort top confidence across the answer set; None when unmeasurable."""
    data: Dict[str, Any] = {}
    try:
        data = res.to_dict() if hasattr(res, "to_dict") else {}
    except Exception:  # noqa: BLE001
        data = {}
    answers = data.get("answers") or getattr(res, "answers", None) or {}
    best: Optional[float] = None
    try:
        for ans in answers.values():
            if isinstance(ans, dict) and ans.get("confidence") is not None:
                v = float(ans["confidence"])
                best = v if best is None else max(best, v)
    except (AttributeError, TypeError, ValueError):
        return None
    return best


class S1GateHealthError(RuntimeError):
    """Usage/config error in the health surface. Maps to exit 3."""


# --------------------------------------------------------------------------
# 6. Threshold policy vs what the rubrics actually enforce
# --------------------------------------------------------------------------

def threshold_report() -> Dict[str, Any]:
    """Does the declared per-class threshold policy match the rubric files?

    A thresholds block nobody reads is a dashboard. This makes it load-bearing:
    every rubric's live `confidence_floor` is checked against the band declared
    for its class, and a contradiction is a finding with a verb.
    """
    wc = Path(RUBRIC_DIR).parent / "work-criteria.json"
    if not wc.exists():
        return {"available": False, "findings": [{
            "id": "no-work-criteria", "severity": "action",
            "metric": "work-criteria.json", "value": 0,
            "detail": "missing at %s" % wc,
            "action": "Restore it -- it is the kind map and the threshold policy.",
        }]}
    try:
        doc = json.loads(wc.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"available": False, "findings": [{
            "id": "work-criteria-unreadable", "severity": "action",
            "metric": "work-criteria.json", "value": 0, "detail": str(exc),
            "action": "Repair it. tests/test_s1gate.py guards its shape.",
        }]}

    th = doc.get("thresholds") or {}
    per = th.get("per_class") or {}
    default = th.get("default") or {}
    qv = (doc.get("question_version") or {}).get("current")
    if not th:
        return {"available": False, "findings": [{
            "id": "no-threshold-policy", "severity": "action",
            "metric": "thresholds", "value": 0,
            "detail": "work-criteria.json has no thresholds block.",
            "action": "Add one: two-sided bands + per-class bars. One global "
                      "cutoff over-serves easy classes and under-serves dangerous ones.",
        }]}

    mismatches: List[Dict[str, Any]] = []
    checked = 0
    for kind, cls in sorted(per.items()):
        if kind.startswith("_") or not isinstance(cls, dict):
            continue
        accept = cls.get("accept_at")
        if accept is None:
            continue
        try:
            rb = load_rubric(kind)
        except Exception:  # noqa: BLE001 - an unknown kind is not this report's problem
            continue
        checked += 1
        floor = float(rb.confidence_floor)
        # The rubric's live floor is the line below which it will not act. It
        # must sit at or below the class accept_at, or the class bar can never
        # be reached and the policy is fiction.
        if floor > float(accept) + 1e-9:
            mismatches.append({
                "kind": kind,
                "confidence_floor": floor,
                "declared_accept_at": accept,
                "why": "rubric floor %.2f is ABOVE the class accept_at %.2f, so "
                       "this class can never reach its own bar" % (floor, float(accept)),
            })
    findings: List[Dict[str, Any]] = []
    if mismatches:
        findings.append({
            "id": "threshold-contradiction",
            "severity": "action",
            "metric": "kinds whose live floor contradicts the declared band",
            "value": len(mismatches),
            "detail": "The policy and the rubric files disagree, so one of them "
                      "is not what runs.",
            "action": "Reconcile: either lower confidence_floor to the class "
                      "accept_at, or change the declared band. Record which you "
                      "did and why in the rubric's notes.",
            "rules": mismatches,
        })
    return {
        "available": True,
        "question_version": qv,
        "per_class_entries": len([k for k in per if not k.startswith("_")]),
        "checked": checked,
        "default": default,
        "mismatches": mismatches,
        "findings": findings,
    }


# --------------------------------------------------------------------------
# Roll-up
# --------------------------------------------------------------------------

def health(now: Optional[str] = None) -> Dict[str, Any]:
    enr = enforcement_report()
    esc = escalation_report()
    hyg = hygiene_report()
    gold = gold_report()
    can = canary_report(now)
    thr = threshold_report()

    findings = (enr["findings"] + esc.get("findings", [])
                + hyg.get("findings", []) + gold["findings"]
                + can["findings"] + thr.get("findings", []))
    actioned = [f for f in findings if f.get("severity") == "action"]

    return {
        "generated_at": now or time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model_alias": JEV_MODEL,
        "enforcement": enr,
        "escalation": esc,
        "hygiene": hyg,
        "gold": gold,
        "canary": can,
        "thresholds": thr,
        "findings": findings,
        "actions_required": len(actioned),
        "verdict": "ACTION_NEEDED" if actioned else "HEALTHY",
    }


def render(h: Dict[str, Any]) -> str:
    """Human view. The verb comes first; the number is evidence for it."""
    out: List[str] = []
    out.append("s1gate health -- %s  (model alias %s)"
               % (h["generated_at"], h["model_alias"]))
    out.append("")

    enr = h["enforcement"]
    out.append("ENFORCEMENT   %d rubrics: %d enforcing, %d advisory"
               % (enr["total"], len(enr["enforcing"]), enr["advisory_count"]))
    if enr["voided"]:
        out.append("              %d rule(s) on VOIDED calibration" % len(enr["voided"]))
    out.append("")

    esc = h["escalation"]
    if esc.get("available"):
        o = esc["overall"]
        out.append("ESCALATION    %s decisions | escalate %s (%s%%) | block %s | pass %s"
                   % (o["decisions"], o["escalate"], o["escalation_rate_pct"],
                      o["block"], o["pass"]))
        out.append("              per-rubric volume leaders:")
        for r in esc["per_rubric"][:8]:
            out.append("                %-24s %6d  esc %5s%%"
                       % (r["rubric"], r["decisions"], r["escalation_rate_pct"]))
    else:
        out.append("ESCALATION    unavailable -- %s" % esc.get("detail"))
    out.append("")

    hyg = h["hygiene"]
    if hyg.get("available"):
        out.append("HYGIENE       %s rows | clean %s | blank-subject %s | quarantined %s"
                   % (hyg["total"], hyg["clean"], hyg["blank_subject"], hyg["quarantined"]))
    out.append("")

    gold = h["gold"]
    out.append("GOLD          %s of %s kinds covered (%s%%) | %s regression cases"
               % (gold["kinds_covered"], gold["kinds_total"],
                  gold["coverage_pct"], gold["regression_cases"]))
    out.append("")

    can = h["canary"]
    if can.get("available"):
        out.append("CANARY        %s frozen cases | %s snapshots | %s moved"
                   % (can["frozen_cases"], can["snapshots"], len(can["moved"])))
    else:
        out.append("CANARY        not seeded -- %s" % can.get("detail"))
    out.append("")

    thr = h.get("thresholds") or {}
    if thr.get("available"):
        out.append("THRESHOLDS    q_version=%s | %s per-class entries | %s checked | %s contradiction(s)"
                   % (thr.get("question_version"), thr.get("per_class_entries"),
                      thr.get("checked"), len(thr.get("mismatches", []))))
    out.append("")

    out.append("=" * 68)
    if not h["findings"]:
        out.append("VERDICT       HEALTHY -- nothing needs acting on.")
    else:
        out.append("VERDICT       %s -- %d finding(s)" % (h["verdict"], len(h["findings"])))
        for f in h["findings"]:
            out.append("")
            out.append("[%s] %s: %s" % (f.get("severity", "info").upper(),
                                        f.get("id"), f.get("metric")))
            out.append("        %s" % f.get("detail", ""))
            out.append("  DO:   %s" % f.get("action", ""))
            for r in (f.get("rubrics") or f.get("rules") or [])[:12]:
                if "rubric" in r and "escalation_rate_pct" in r:
                    out.append("        - %-24s %6d decisions, %s%% escalate"
                               % (r["rubric"], r["decisions"], r["escalation_rate_pct"]))
                elif "rubric" in r and "why" in r:
                    out.append("        - %s / %s: %s" % (r["rubric"], r.get("signal"), r["why"]))
                elif "rubric" in r and "error" in r:
                    out.append("        - %s: %s" % (r["rubric"], r["error"]))
                elif "id" in r and "new_verdict" in r:
                    out.append("        - %s: %s -> %s" % (r["id"], r["baseline_verdict"],
                                                           r["new_verdict"]))
    return "\n".join(out)
