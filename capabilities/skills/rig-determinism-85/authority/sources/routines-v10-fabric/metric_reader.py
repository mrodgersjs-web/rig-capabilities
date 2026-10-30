"""Deterministic primary-metric reader: clean routine fires/day.

Fire      = a `sessions` row with routine_id NOT NULL created inside the window.
Clean     = that session's status == 'idle' (finished without error).
Rates     = fires per day over the window; clean rate = clean / fires.
Bounds    = Poisson one-sided 95% LCB on the daily fire rate (count data),
            Clopper-Pearson one-sided 95% LCB on the clean rate (proportion).
Exact computation by bisection (no scipy); unit-tested against published
values. Offline and read-only; the outcome log is append-only JSONL.
Exit codes: 0 ok, 2 zero fires in window (no data — never a pass), 3 db error.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

READER_VERSION = "routine-fabric-metric/1.0"
STATE_DIR = Path(os.environ.get("RIG_FABRIC_STATE", os.path.expanduser("~/.rig/state/routine-fabric")))
OUTCOME_LOG = STATE_DIR / "metric-outcomes.jsonl"
DB_PATH = Path(os.environ.get("RIG_ROUTINE_DB", os.path.expanduser("~/.aside/u/0/state.db")))


# ---------- exact one-sided confidence bounds ----------

def _poisson_tail_ge(k: int, lam: float) -> float:
    """P(X >= k) for X ~ Poisson(lam)."""
    if lam <= 0:
        return 1.0 if k <= 0 else 0.0
    s = 0.0
    log_lam = math.log(lam)
    for i in range(k):
        s += math.exp(-lam + i * log_lam - math.lgamma(i + 1))
    return max(0.0, min(1.0, 1.0 - s))


def poisson_lcb(k: int, exposure_days: float = 1.0, alpha: float = 0.05) -> float:
    """One-sided lower 95% bound for the Poisson rate (events/day)."""
    if k <= 0:
        return 0.0
    lo, hi = 0.0, float(k) * 2 + 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X >= k | lam) increases in lam; solve tail = alpha below the MLE
        if _poisson_tail_ge(k, mid) > alpha:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2 / exposure_days


def _binom_tail_ge(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if p <= 0:
        return 1.0 if k <= 0 else 0.0
    if p >= 1:
        return 1.0 if k <= n else 0.0
    s = 0.0
    log_p, log_q = math.log(p), math.log1p(-p)
    for i in range(k, n + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                      + i * log_p + (n - i) * log_q)
    return max(0.0, min(1.0, s))


def clopper_pearson_lcb(k: int, n: int, alpha: float = 0.05) -> float:
    """One-sided lower 95% bound for a binomial proportion."""
    if n <= 0 or k <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X >= k | p) increases in p; solve tail = alpha below p-hat
        if _binom_tail_ge(k, n, mid) > alpha:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ---------- the reader ----------

def read(db: Path | str | None = None, days: float = 7.0,
         end_epoch: float | None = None) -> dict:
    import sqlite3
    path = Path(db) if db else DB_PATH
    end = float(end_epoch) if end_epoch else time.time()
    start = end - days * 86400.0
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """SELECT status, COUNT(*) c FROM sessions
               WHERE routine_id IS NOT NULL AND created_at >= ? AND created_at < ?
               GROUP BY status""", (int(start), int(end)))
        breakdown = {r["status"]: r["c"] for r in cur.fetchall()}
        total = sum(breakdown.values())
        clean = breakdown.get("idle", 0)
        routines_fired = conn.execute(
            """SELECT COUNT(DISTINCT routine_id) FROM sessions
               WHERE routine_id IS NOT NULL AND created_at >= ? AND created_at < ?""",
            (int(start), int(end))).fetchone()[0]
        per_day = []
        for r in conn.execute(
                """SELECT date(created_at, 'unixepoch') d, COUNT(*) fires,
                          SUM(CASE WHEN status='idle' THEN 1 ELSE 0 END) clean
                   FROM sessions
                   WHERE routine_id IS NOT NULL AND created_at >= ? AND created_at < ?
                   GROUP BY d ORDER BY d""", (int(start), int(end))):
            per_day.append({"date": r["d"], "fires": r["fires"], "clean": r["clean"]})
        conn.close()
    except sqlite3.Error as e:
        raise RuntimeError(f"cannot read {path}: {e}") from e

    report = {
        "reader": READER_VERSION,
        "db": str(path),
        "window_start_utc": datetime.fromtimestamp(start, timezone.utc).isoformat(timespec="seconds"),
        "window_end_utc": datetime.fromtimestamp(end, timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "fires": total,
        "clean": clean,
        "status_breakdown": breakdown,
        "routines_fired": routines_fired,
        "fires_per_day": total / days if days else 0.0,
        "fires_per_day_lcb95_poisson": poisson_lcb(total, days),
        "clean_rate": (clean / total) if total else None,
        "clean_rate_lcb95_clopper_pearson": clopper_pearson_lcb(clean, total) if total else None,
        "per_day": per_day,
        "zero_fires": total == 0,
    }
    return report


def append_outcome(report: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTCOME_LOG, "a") as f:
        f.write(json.dumps(report, sort_keys=True) + "\n")
    return OUTCOME_LOG


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--end-epoch", type=float, default=None)
    ap.add_argument("--db", default=None)
    ap.add_argument("--append-outcome", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        report = read(args.db, args.days, args.end_epoch)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    if args.append_outcome:
        path = append_outcome(report)
        report["outcome_log"] = str(path)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json
          else _fmt(report))
    return 2 if report["zero_fires"] else 0


def _fmt(r: dict) -> str:
    lines = [
        f"reader: {r['reader']}",
        f"window: {r['window_start_utc']} .. {r['window_end_utc']} ({r['days']:.2f}d)",
        f"fires: {r['fires']}  clean: {r['clean']}  routines: {r['routines_fired']}",
        f"breakdown: {r['status_breakdown']}",
        f"fires/day: {r['fires_per_day']:.2f}  LCB95(poisson): {r['fires_per_day_lcb95_poisson']:.2f}",
        f"clean rate: {r['clean_rate'] if r['clean_rate'] is not None else 'n/a'}"
        f"  LCB95(clopper-pearson): {r['clean_rate_lcb95_clopper_pearson']}",
    ]
    for d in r["per_day"]:
        lines.append(f"  {d['date']}: fires={d['fires']} clean={d['clean']}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
