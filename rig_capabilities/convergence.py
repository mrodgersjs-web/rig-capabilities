"""V41-P3: convergence math — E_cap(t), C_t, A_t, RobustMADZ, the weekly gate.

One number measures distance-to-2031, recomputed weekly, gated by a node that
can say FAIL. Decimal throughout: no float drift in a score anyone can quote.

    E_cap(t) = sum_i w_i * (1 - min(M_i,t, M_i*) / M_i*)
    C_t      = 1 - E_cap(t) / sum_i w_i
    A_t      = sum_i w_i * 1[band_i in {A1,A2}] / sum_i w_i

Weekly gate: dC_t > 0 AND dA_t >= 0 AND unclassified_rate <= 10% AND
booked qualified conversations > 0 AND no unresolved >=5 sigma flag.

`score_week` is the ONLY caller of `corpus.corpus_report()` — an unclassified
rate over the halt means no week gets scored at all.
"""
from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
from decimal import Decimal, localcontext
from pathlib import Path

from .register import (  # register.py owns the vocabularies and the store
    _as_int, _as_null_str, _as_str, _repo_root, bookings_path as bookings_path_for,
    load_bookings, load_register,
)

MADZ_DEEP_REVIEW_SIGMA = 5.0
MADZ_COEFFICIENT = Decimal("0.6745")
HALT_UNCLASSIFIED_RATE = Decimal("0.10")
AUTONOMY_BANDS = ("A1", "A2")
PRECISION = 34
CROSSCHECK_TOL = Decimal("1e-9")
CROSSCHECK_BIN = "rig-math-exec"
MATURITY_JUMP_LEVELS = 3

REALIGN_DIR = ".context/realign"
AUTO_REPORT = "auto"


def realign_root(repo) -> Path:
    """The parent of the week directories, resolved at call time.

    `RIG_REALIGN_ROOT` relocates it exactly as `RIG_PROOF_ROOT` relocates the proof tree
    and `RIG_LEASE_STATE_ROOT` the lease ledger. Without it, a verb that reads *prior*
    weeks out of the live repo can never be tested twice with the same answer: the first
    legitimate `realign --apply` created a prior week and silently turned a read-only
    test's expected BASELINE_ONLY into a real FAIL. Production default is unchanged.
    """
    override = os.environ.get("RIG_REALIGN_ROOT")
    if override:
        return Path(override).expanduser()
    return _repo_root(repo) / REALIGN_DIR


ZERO = Decimal(0)
ONE = Decimal(1)


class ConvergenceError(Exception):
    """A week that cannot be scored for a reason other than the corpus halt."""


class CorpusHalt(Exception):
    """Stand-in for `corpus.CorpusRefusal` when P2's module is not importable."""


# ------------------------------------------------------------------ row sets

def active_rows(rows) -> list[dict]:
    """Rows that count: not declared a duplicate of another capability."""
    out = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if _as_null_str(row.get("duplicate_of")) is not None:
            continue
        if _as_int(row.get("weight_w")) is None:
            continue
        out.append(row)
    return out


def scored_rows(rows) -> list[dict]:
    """Active rows with a maturity, a weight, and a 2031 target > 0."""
    out = []
    for row in active_rows(rows):
        maturity = _as_int(row.get("maturity_M0_5"))
        target = _as_int(row.get("target_M_2031"))
        if maturity is None or target is None or target <= 0:
            continue
        out.append(row)
    return out


def degenerate_targets(rows) -> list[dict]:
    """Active rows whose `target_M_2031` is 0: they contribute 0 to E_cap and
    are excluded from the ratio, so the omission is named, never hidden."""
    out = []
    for row in active_rows(rows):
        target = _as_int(row.get("target_M_2031"))
        if target is None or target > 0:
            continue
        out.append({"id": _as_str(row.get("id")),
                    "weight_w": target_weight(row),
                    "maturity_M0_5": _as_int(row.get("maturity_M0_5"))})
    return out


def target_weight(row) -> int:
    return _as_int(row.get("weight_w")) or 0


# ---------------------------------------------------------------- the math

def e_cap(rows) -> Decimal:
    """Remaining capability debt, weighted. Rows with no target add nothing."""
    total = ZERO
    with localcontext() as ctx:
        ctx.prec = PRECISION
        for row in scored_rows(rows):
            weight = Decimal(target_weight(row))
            maturity = Decimal(_as_int(row.get("maturity_M0_5")) or 0)
            target = Decimal(_as_int(row.get("target_M_2031")) or 0)
            total += weight * (ONE - min(maturity, target) / target)
        return +total


def c_t(rows) -> Decimal:
    """Convergence 0 -> 1. An empty register is 0, never a division by zero."""
    scored = scored_rows(rows)
    denom = sum((Decimal(target_weight(r)) for r in scored), ZERO)
    if denom <= 0:
        return ZERO
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return +(ONE - e_cap(scored) / denom)


def a_t(rows) -> Decimal:
    """Automation ratio over the whole active register — targets are irrelevant."""
    active = active_rows(rows)
    denom = sum((Decimal(target_weight(r)) for r in active), ZERO)
    if denom <= 0:
        return ZERO
    numer = sum((Decimal(target_weight(r)) for r in active
                 if _as_str(r.get("automation_band")) in AUTONOMY_BANDS), ZERO)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return +(numer / denom)


def metrics(rows) -> dict:
    """JSON-safe scoreboard for one register state."""
    scored = scored_rows(rows)
    active = active_rows(rows)
    return {
        "e_cap": str(e_cap(rows)),
        "c_t": str(c_t(rows)),
        "a_t": str(a_t(rows)),
        "rows_total": len(list(rows or [])),
        "rows_active": len(active),
        "rows_scored": len(scored),
        "weight_scored": str(sum((Decimal(target_weight(r)) for r in scored), ZERO)),
        "weight_active": str(sum((Decimal(target_weight(r)) for r in active), ZERO)),
        "degenerate_targets": degenerate_targets(rows),
    }


def delta(prev, cur) -> dict:
    """dC_t / dA_t between two register states; `None` when incomputable."""
    a, b = _dec(prev), _dec(cur)
    return {"prev": prev, "cur": cur,
            "delta": None if (a is None or b is None) else b - a}


# ------------------------------------------------------------------ RobustMADZ

def _dec(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    text = str(value).strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except Exception:
        return None


def _madz(score: float, values: list[float]) -> tuple[float, Decimal]:
    median = Decimal(str(statistics.median(values)))
    deviations = sorted(abs(Decimal(str(v)) - median) for v in values)
    mad = Decimal(str(statistics.median([float(d) for d in deviations])))
    if mad == 0:
        return median, ZERO
    z = MADZ_COEFFICIENT * (Decimal(str(score)) - median) / mad
    return median, +z


def _rig_math_exec(score, values) -> float | None:
    """Advisory cross-check. Absent binary, timeout, or garbage = no opinion."""
    exe = os.environ.get("RIG_MATH_EXEC", CROSSCHECK_BIN)
    if os.environ.get("RIG_MATH_EXEC_DISABLE") or shutil.which(exe) is None:
        return None
    argv = [exe, "robust-madz", str(score)] + [str(v) for v in values]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or "").strip().splitlines()
    if not text:
        return None
    try:
        return float(text[-1])
    except ValueError:
        return None


def robust_madz(score, baseline, crosscheck: bool = True) -> tuple[float, str]:
    """`0.6745 * (score - median) / MAD` -> `(z, flag)`.

    `MAD == 0` has no spread to judge: `(0.0, 'mad_zero')`, never infinity.
    The `rig-math-exec` cross-check runs only when `MAD > 0`, is advisory, and
    never overrides the local value — a disagreement > 1e-9 flags
    `BLOCKED_DEEP_REVIEW` while `z` stays the locally computed number.
    """
    values = []
    for raw in (baseline or []):
        d = _dec(raw)
        if d is not None:
            values.append(float(d))
    s = _dec(score)
    if not values or s is None:
        return 0.0, "no_baseline"
    median, z_dec = _madz(float(s), values)
    if _mad_is_zero(values):
        return 0.0, "mad_zero"
    z = float(z_dec)
    flag = "deep_review" if abs(z) >= MADZ_DEEP_REVIEW_SIGMA else "ok"
    if crosscheck and z_dec != 0:
        remote = _rig_math_exec(float(s), values)
        if remote is not None and abs(Decimal(str(remote)) - z_dec) > CROSSCHECK_TOL:
            flag = "BLOCKED_DEEP_REVIEW"
    return z, flag


def _mad_is_zero(values: list[float]) -> bool:
    median = statistics.median(values)
    deviations = sorted(abs(v - median) for v in values)
    return statistics.median(deviations) == 0


def c_t_madz_flags(series, current) -> list[dict]:
    """MADZ flags for this week's C_t against the series of prior sealed weeks."""
    prior = [d for d in (_dec(v) for v in (series or [])) if d is not None]
    cur = _dec(current)
    if cur is None or len(prior) < 3:
        return []
    z, flag = robust_madz(cur, prior)
    return [{"capability": "C_t", "z": z, "flag": flag, "resolved": False}]


def maturity_jump_flags(prev, cur, threshold: int = MATURITY_JUMP_LEVELS) -> list[dict]:
    """A capability jumping `threshold` maturity levels in one week is a scoring
    bug, not progress. Recorded as an unresolved flag, never scored silently."""
    before = {_as_str(r.get("id")): _as_int(r.get("maturity_M0_5"))
              for r in (prev or []) if isinstance(r, dict)}
    flags = []
    for row in cur or []:
        if not isinstance(row, dict):
            continue
        rid = _as_str(row.get("id"))
        after = _as_int(row.get("maturity_M0_5"))
        if rid not in before or after is None or before[rid] is None:
            continue
        jump = after - before[rid]
        if jump >= threshold:
            flags.append({"capability": rid, "from": before[rid], "to": after,
                          "levels": jump, "z": None,
                          "flag": "maturity_jump", "resolved": False})
    return flags


# -------------------------------------------------------------- weekly gate

def _scores(week) -> tuple[Decimal | None, Decimal | None]:
    """Accept a register state, a precomputed metrics mapping, or None."""
    if week is None:
        return None, None
    if isinstance(week, dict):
        return _dec(week.get("c_t")), _dec(week.get("a_t"))
    return c_t(week), a_t(week)


def _booking_count(bookings) -> int:
    if isinstance(bookings, dict):
        return _as_int(bookings.get("count")) or 0
    if isinstance(bookings, (list, tuple)):
        return len(bookings)
    return _as_int(bookings) or 0


def _flag_entries(madz_flags) -> list[dict]:
    out = []
    for entry in (madz_flags or []):
        if isinstance(entry, dict):
            z = _dec(entry.get("z", entry.get("sigma", entry.get("madz"))))
            name = _as_str(entry.get("capability", entry.get("name", entry.get("id")))) or "?"
            resolved = bool(entry.get("resolved", False))
            flag = _as_str(entry.get("flag"))
        elif isinstance(entry, (list, tuple)):
            vals = list(entry)
            name = _as_str(vals[0]) if vals else "?"
            z = _dec(vals[1]) if len(vals) > 1 else None
            resolved = bool(vals[2]) if len(vals) > 2 else False
            flag = _as_str(vals[3]) if len(vals) > 3 else ""
        else:
            name, z, resolved, flag = "?", _dec(entry), False, ""
        out.append({"capability": name, "z": z, "resolved": resolved, "flag": flag})
    return out


def _sigma_blocks(entries) -> list[str]:
    causes = []
    for entry in entries:
        if entry["resolved"]:
            continue
        z = entry["z"]
        if z is None:
            continue
        if abs(z) >= Decimal(str(MADZ_DEEP_REVIEW_SIGMA)) or entry["flag"] == "BLOCKED_DEEP_REVIEW":
            causes.append(f"madz_deep_review:{entry['capability']}")
    return causes


def _fail_streak(history, this_failed: bool) -> int:
    if not this_failed:
        return 0
    streak = 1
    for rec in reversed(list(history or [])):
        if isinstance(rec, dict) and _as_str(rec.get("verdict")).upper() == "FAIL":
            streak += 1
        else:
            break
    return streak


def _zero_booking_rise_streak(history, c_t_cur, bookings: int) -> int:
    """Consecutive weeks (ending with this one) where C_t rose AND bookings were 0."""
    pts: list[Decimal] = []
    marks: list[int] = []
    for rec in (history or []):
        if not isinstance(rec, dict):
            continue
        d = _dec(rec.get("c_t"))
        if d is None:
            continue
        pts.append(d)
        marks.append(_booking_count(rec.get("bookings")))
    cur = _dec(c_t_cur)
    if cur is None:
        return 0
    pts.append(cur)
    marks.append(bookings)
    streak = 0
    for j in range(len(pts) - 1, 0, -1):
        if pts[j] > pts[j - 1] and marks[j] == 0:
            streak += 1
        else:
            break
    return streak


def weekly_gate(prev, cur, madz_flags, bookings, *, unclassified_rate=None,
                history=None, week: str | None = None) -> dict:
    """The node that can say FAIL. PASS needs all five conditions.

    `prev`/`cur` take a register state (list of rows) or a precomputed
    `{c_t, a_t}` mapping; `prev is None` means there is no prior sealed week,
    which is `BASELINE_ONLY` — never a dC_t PASS.
    `unclassified_rate` comes from `corpus.corpus_report()`; unreported is not
    the same as zero and never PASSes.
    """
    c_prev, a_prev = _scores(prev)
    c_cur, a_cur = _scores(cur)
    count = _booking_count(bookings)
    rate = _dec(unclassified_rate)
    entries = _flag_entries(madz_flags)

    d_c = None if c_prev is None or c_cur is None else c_cur - c_prev
    d_a = None if a_prev is None or a_cur is None else a_cur - a_prev

    causes: list[str] = []
    if c_cur is None or a_cur is None:
        causes.append("current_week_unscorable")
    if rate is None:
        causes.append("unclassified_rate_unreported")
    elif rate > HALT_UNCLASSIFIED_RATE:
        causes.append("unclassified_rate_above_halt")
    if count <= 0:
        causes.append("booked_qualified_conversations")
    causes.extend(_sigma_blocks(entries))

    baseline_only = c_prev is None or a_prev is None
    if baseline_only:
        verdict = "BASELINE_ONLY"
    else:
        if d_c is None or d_c <= 0:
            causes.append("c_t_not_improving")
        if d_a is None or d_a < 0:
            causes.append("a_t_regressing")
        verdict = "PASS" if not causes else "FAIL"

    escalations: list[str] = []
    rises = _zero_booking_rise_streak(history, c_cur, count)
    if rises >= 3:
        escalations.append("WEIGHTS_INVALID")
    fails = _fail_streak(history, verdict == "FAIL")
    if fails >= 3:
        escalations.append("LOOP_REBUILD_REQUIRED")
    if "LOOP_REBUILD_REQUIRED" in escalations:
        verdict = "LOOP_REBUILD_REQUIRED"
    elif "WEIGHTS_INVALID" in escalations and verdict == "FAIL":
        verdict = "WEIGHTS_INVALID"

    return {
        "week": week,
        "verdict": verdict,
        "causes": causes,
        "escalations": escalations,
        "fail_streak": fails,
        "zero_booking_rise_streak": rises,
        "d_c_t": None if d_c is None else str(d_c),
        "d_a_t": None if d_a is None else str(d_a),
        "c_t_previous": None if c_prev is None else str(c_prev),
        "c_t_current": None if c_cur is None else str(c_cur),
        "a_t_previous": None if a_prev is None else str(a_prev),
        "a_t_current": None if a_cur is None else str(a_cur),
        "bookings": count,
        "unclassified_rate": None if rate is None else str(rate),
        "madz_flags": [{"capability": e["capability"], "flag": e["flag"],
                        "resolved": e["resolved"],
                        "z": None if e["z"] is None else str(e["z"])}
                       for e in entries],
        "checks": {
            "prior_sealed_week": not baseline_only,
            "d_c_t_positive": None if d_c is None else bool(d_c > 0),
            "d_a_t_non_negative": None if d_a is None else bool(d_a >= 0),
            "unclassified_rate_within_halt": None if rate is None
            else bool(rate <= HALT_UNCLASSIFIED_RATE),
            "booked_qualified_conversations": count > 0,
            "madz_clear": not _sigma_blocks(entries),
        },
    }


# ------------------------------------------------------------- corpus seam

def corpus_report(roots=None) -> dict:
    """The single indirection to `corpus.corpus_report()` — so a week can be
    scored against a stubbed corpus and so the dependency stays one-way."""
    from . import corpus  # P2 owns this module; imported lazily, never at import time
    return corpus.corpus_report(roots)


def _corpus_refusal():
    try:
        from .corpus import CorpusRefusal
        return CorpusRefusal
    except Exception:
        return CorpusHalt


def sealed_series(repo, exclude_week: str | None = None) -> list[dict]:
    """C_t of prior weeks under `.context/realign/`, oldest first."""
    root = realign_root(repo)
    out = []
    if not root.is_dir():
        return out
    for day in sorted(root.iterdir()):
        proof = day / "proof" / "convergence.json"
        if not day.is_dir() or not proof.is_file() or day.name == exclude_week:
            continue
        try:
            doc = _json(proof)
        except Exception:
            continue
        c_t_val = _dec((doc.get("exact") or {}).get("c_t") or doc.get("c_t"))
        if c_t_val is None:
            continue
        verdict = ""
        gate_doc = day / "proof" / "weekly-gate.json"
        if gate_doc.is_file():
            try:
                verdict = str(_json(gate_doc).get("verdict") or "")
            except Exception:
                verdict = ""
        out.append({"week": day.name, "c_t": str(c_t_val),
                    "a_t": str(_dec((doc.get("exact") or {}).get("a_t")
                                    or doc.get("a_t"))),
                    "verdict": verdict,
                    "bookings": _as_int((doc.get("gate") or {}).get("bookings")) or 0})
    return out


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def score_week(repo, roots=None, *, week: str | None = None,
               bookings_path=None, previous=None, history=None,
               madz_flags=None, report=AUTO_REPORT) -> dict:
    """Score one week. Raises `corpus.CorpusRefusal` past the halt — no week
    gets scored on a register the classifier cannot place.

    `score_week` is the only caller of `corpus.corpus_report()`. Pass
    `report=None` only when a driver has already recorded the corpus state: the
    rate then reads as unreported, which never PASSes.
    """
    if isinstance(report, str) and report == AUTO_REPORT:
        report = corpus_report(roots)
    if report is None:
        report = {"present": False, "unclassified_rate": None, "ok": None}
    rate = _dec(report.get("unclassified_rate")) if isinstance(report, dict) else None
    if not isinstance(report, dict) or rate is None:
        if isinstance(report, dict) and report.get("present") is False:
            rate = None
        else:
            raise _corpus_refusal()(f"corpus_report_unusable:{report!r:.120}")
    if rate is not None and (report.get("ok") is False
                             or rate > HALT_UNCLASSIFIED_RATE):
        raise _corpus_refusal()(
            f"unclassified_rate_above_halt:{rate} halt:{HALT_UNCLASSIFIED_RATE}")

    rows = load_register(repo)
    week = week or _week_of(repo)
    if bookings_path is None:
        candidate = bookings_path_for(repo, week)
        bookings = (load_bookings(candidate) if candidate.is_file()
                    else {"week": week, "count": 0, "records": [],
                          "total": 0, "invalid": [],
                          "note": "bookings_artifact_absent"})
    elif isinstance(bookings_path, dict):
        bookings = bookings_path
    else:
        bookings = load_bookings(Path(bookings_path))

    prev_rows = _previous_rows(repo, previous, week)
    prior = sealed_series(repo, exclude_week=week)
    flags = list(madz_flags or [])
    flags.extend(c_t_madz_flags([d["c_t"] for d in prior], c_t(rows)))
    if isinstance(prev_rows, list):
        flags.extend(maturity_jump_flags(prev_rows, rows))

    gate = weekly_gate(prev_rows, rows, flags, bookings,
                       unclassified_rate=rate,
                       history=prior if history is None else history, week=week)
    return {
        "week": week,
        "corpus": {"present": report.get("present", True),
                   "raw": report.get("raw"), "unique": report.get("unique"),
                   "classified": report.get("classified"),
                   "unclassified": report.get("unclassified"),
                   "unclassified_rate": None if rate is None else str(rate),
                   "ok": report.get("ok"),
                   "halt": str(HALT_UNCLASSIFIED_RATE)},
        "metrics": metrics(rows),
        "previous_metrics": (metrics(prev_rows) if isinstance(prev_rows, list)
                             else prev_rows),
        "sealed_weeks_prior": [d["week"] for d in prior],
        "bookings": {"week": bookings.get("week"), "count": bookings.get("count"),
                     "total": bookings.get("total"),
                     "invalid": bookings.get("invalid"),
                     "note": bookings.get("note")},
        "gate": gate,
    }


def _week_of(repo) -> str:
    from .realign import week_id
    return week_id()


def _previous_rows(repo, previous, week: str):
    """`previous` may be rows, a CSV path, a metrics mapping, or None — in which
    case the most recent prior week under `.context/realign/` is used."""
    if previous is not None:
        if isinstance(previous, (str, os.PathLike)):
            path = Path(previous)
            return load_register(repo, path=path) if path.is_file() else None
        return previous
    series = sealed_series(repo, exclude_week=week)
    if not series:
        return None
    record = series[-1]
    rows = _sealed_rows(repo, record["week"])
    if rows is not None:
        return rows
    return {"c_t": record["c_t"], "a_t": record["a_t"]}


def _sealed_rows(repo, week: str):
    path = realign_root(repo) / week / "proof" / "register-rows.json"
    if not path.is_file():
        return None
    try:
        doc = _json(path)
    except Exception:
        return None
    rows = doc.get("rows") if isinstance(doc, dict) else doc
    return rows if isinstance(rows, list) else None
