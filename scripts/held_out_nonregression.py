#!/usr/bin/env python3
"""Held-out non-regression gate: decide promote | refuse for a candidate.

Why this exists (derived mechanism, not transcript prose): an improvement
round promotes a candidate whenever its own done-tests stay green — a
same-task regression check. A contract edit can therefore raise the pass-rate
of exactly the tasks it was written against while silently degrading unseen
work, and the round still prints GREEN (AutoDesign's acceptance gate,
arXiv:2608.13560, refuses exactly this: a candidate replaces the incumbent
only if it beats the incumbent AND does not make unseen tasks worse;
Task-CoEvolve, arXiv:2608.20169, is why the unseen set must be chosen, not
frozen). Videos LEsKxMfRFjA, MvI17TNFW9c.

The gate is mechanical: given a baseline (incumbent) result set, a candidate
result set, and the declared held-out task ids, it refuses promotion when
  R1 no held-out set is declared            (promotion decided on seen tasks
                                             alone is the RED this gate was
                                             built for),
  R2 the promotion record carries no cost envelope next to the quality floor,
  R3 the candidate record drops any task the baseline recorded — a retained
     negative stays VISIBLE; deleting it from the ledger is not fixing it,
  R4 any previously-passing task now fails (named, whichever split it lives
     on),
  R5 the candidate does not strictly beat the incumbent on the train split,
  R6 the held-out pass-rate falls by more than the noise band, or candidate
     cost exceeds the declared envelope.

Noise band: max(--min-band, 2 x robust sigma) where robust sigma is the
RobustMADZ-style scale 1.4826 x MAD of the historical sealed held-out rates
in `history.jsonl` (median absolute deviation, robust to one bad sealed run).
With no history the floor band applies. Refusal names every violated rule;
it never refuses silently and never promotes on judgment.

Fixture format (one directory per case, under examples/fixtures/held-out/):
  held_out.json   {"tasks": ["h1", ...]}       required (task ids NOT used to
                                               produce the candidate)
  baseline.jsonl  one row per task the incumbent was evaluated on
  candidate.jsonl one row per task the candidate was evaluated on
    row = {"task": str, "pass": bool, "tool_calls": num,
           "wall_clock_s": num, "spend_usd": num}   (cost fields optional)
  history.jsonl   optional {"held_out_pass_rate": num} per previously sealed run
  record.json     optional {"budget": {"tool_calls": n, "wall_clock_s": n,
                       "spend_usd": n}}      the promotion record's envelope
  expect.json     {"verdict": "promote"|"refuse", "names": [substr, ...]}
                  (selftest only — what this case must decide)

Exit codes: 0 promote · 1 refuse (reasons and task ids printed) · 2 usage or
malformed input. Bare invocation runs `selftest` over the fixture estate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_ROOT = "examples/fixtures/held-out"
MIN_BAND = 0.02          # never let history collapse the band to zero
BAND_SIGMAS = 2.0        # refuse only outside +-2 robust sigma of sealed runs
BUDGET_KEYS = ("tool_calls", "wall_clock_s", "spend_usd")


def _rows(path: Path) -> dict:
    """task id -> row, from a JSONL results file. Missing file -> {}."""
    out = {}
    if not path.is_file():
        return out
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError as e:
            raise SystemExit(f"held-out gate: {path}:{n}: bad JSON ({e})")
        if not isinstance(row, dict) or "task" not in row or "pass" not in row:
            raise SystemExit(f"held-out gate: {path}:{n}: need task+pass")
        out[str(row["task"])] = row
    return out


def _rates(path: Path, key: str) -> list:
    """One number per JSONL line (`{key: num}`); missing file -> []."""
    out = []
    if not path.is_file():
        return out
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            v = json.loads(line).get(key)
        except ValueError as e:
            raise SystemExit(f"held-out gate: {path}:{n}: bad JSON ({e})")
        if isinstance(v, (int, float)):
            out.append(float(v))
    return out


def _num(row: dict, key: str) -> float:
    v = row.get(key, 0)
    if not isinstance(v, (int, float)):
        raise SystemExit(f"held-out gate: task {row.get('task')}: {key} must be numeric")
    return float(v)


def _rate(rows: dict, tasks) -> float:
    """Pass-rate over `tasks`, counting an absent result as a FAIL —
    silence is never credit."""
    if not tasks:
        return 0.0
    return sum(1 for t in tasks if rows.get(t, {}).get("pass") is True) / len(tasks)


def robust_sigma(values):
    """RobustMADZ scale: 1.4826 x MAD (consistent sigma for a normal sample,
    undominated by one outlier). None when history is too short to speak."""
    if len(values) < 3:
        return None
    s = sorted(values)

    def median(xs):
        n = len(xs)
        mid = n // 2
        return xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2.0

    m = median(s)
    mad = median([abs(x - m) for x in s])
    return 1.4826 * mad


def decide(case: Path, min_band: float = MIN_BAND) -> dict:
    """Pure decision for one case directory -> verdict dict (no I/O beyond
    the case files)."""
    reasons, regressed, hidden = [], [], []

    ho_f = case / "held_out.json"
    base_f, cand_f = case / "baseline.jsonl", case / "candidate.jsonl"
    for f in (base_f, cand_f):
        if not f.is_file():
            raise SystemExit(f"held-out gate: missing {f}")
    baseline, candidate = _rows(base_f), _rows(cand_f)

    # R1 — the unseen set must exist and must be unseen.
    held_out = []
    if ho_f.is_file():
        ho = json.loads(ho_f.read_text(encoding="utf-8"))
        held_out = [str(t) for t in ho.get("tasks", [])]
    train_all = sorted(set(baseline) | set(candidate))
    held_ids = list(dict.fromkeys(held_out))        # declared, deduped
    train_ids = [t for t in train_all if t not in set(held_ids)]
    if not held_ids:
        reasons.append("no held-out set declared: promotion would be decided "
                       "on the seen set alone — overfitting invisible to the gate")

    # R2 — cost envelope next to the quality floor.
    envelope = None
    rec_f = case / "record.json"
    if rec_f.is_file():
        rec = json.loads(rec_f.read_text(encoding="utf-8"))
        env = rec.get("budget")
        if isinstance(env, dict) and all(k in env for k in BUDGET_KEYS):
            envelope = env
    if envelope is None:
        reasons.append("promotion record missing cost budget "
                       "(record.json must declare budget.tool_calls / "
                       "wall_clock_s / spend_usd) — 'complete' means "
                       "complete-within-budget")

    # R3 — retained negatives stay visible.
    for t in sorted(set(baseline) - set(candidate)):
        hidden.append(t)
    if hidden:
        reasons.append("retained negatives removed from the candidate record: "
                       + ", ".join(hidden)
                       + " — a deleted negative is hidden, not fixed")

    # R4 — any previously-passing case regresses.
    for t in sorted(set(baseline) & set(candidate)):
        if baseline[t].get("pass") is True and candidate[t].get("pass") is not True:
            regressed.append(t)
    if regressed:
        reasons.append("regressed cases (pass->fail): " + ", ".join(regressed))

    base_train, cand_train = _rate(baseline, train_ids), _rate(candidate, train_ids)
    base_held, cand_held = _rate(baseline, held_ids), _rate(candidate, held_ids)

    # R5 — candidate must beat the incumbent on the seen split.
    if cand_train <= base_train:
        reasons.append(f"no train gain: {base_train:.4f} -> {cand_train:.4f}")

    # R6a — held-out non-regression beyond the noise band.
    hist = _rates(case / "history.jsonl", "held_out_pass_rate")
    sig = robust_sigma(hist)
    band = max(min_band, BAND_SIGMAS * sig) if sig is not None else min_band
    drop = base_held - cand_held
    if drop > band:
        dropped = sorted(t for t in held_ids
                         if baseline.get(t, {}).get("pass") is True
                         and candidate.get(t, {}).get("pass") is not True)
        named = ", ".join(dropped) if dropped else "new held-out tasks failing"
        reasons.append(f"held-out regression: {base_held:.4f} -> {cand_held:.4f} "
                       f"(drop {drop:.4f} > band {band:.4f}) — tasks: {named}")

    # R6b — cost envelope.
    cost = {k: sum(_num(r, k) for r in candidate.values()) for k in BUDGET_KEYS}
    if envelope is not None:
        over = [f"{k} {cost[k]:g} > {envelope[k]:g}" for k in BUDGET_KEYS
                if cost[k] > float(envelope[k])]
        if over:
            reasons.append("cost envelope exceeded: " + "; ".join(over))

    return {
        "case": case.name,
        "verdict": "refuse" if reasons else "promote",
        "reasons": reasons,
        "regressed": regressed,
        "hidden_negatives": hidden,
        "train": {"baseline": round(base_train, 4), "candidate": round(cand_train, 4)},
        "held_out": {"baseline": round(base_held, 4), "candidate": round(cand_held, 4),
                     "tasks": held_ids},
        "band": round(band, 4),
        "history_runs": len(hist),
        "cost": {k: round(v, 4) for k, v in cost.items()},
    }


def cmd_check(case: Path, min_band: float) -> int:
    try:
        v = decide(case, min_band)
    except SystemExit as e:      # malformed input: usage-class failure
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps(v, indent=1))
    if v["verdict"] == "promote":
        return 0
    for r in v["reasons"]:
        print(f"REFUSE {case.name}: {r}", file=sys.stderr)
    return 1


def cmd_selftest(root: Path, min_band: float) -> int:
    """Every fixture case with an expect.json must decide exactly as declared.
    This is what a planted-softened detector cannot survive."""
    cases = sorted(d for d in root.iterdir()
                   if d.is_dir() and (d / "expect.json").is_file())
    if not cases:
        print(f"held-out gate: no cases with expect.json under {root}", file=sys.stderr)
        return 2
    bad = 0
    for d in cases:
        exp = json.loads((d / "expect.json").read_text(encoding="utf-8"))
        v = decide(d, min_band)
        out = json.dumps(v)
        ok = v["verdict"] == exp["verdict"] and all(
            n in out for n in exp.get("names", []))
        print(f"{'ok  ' if ok else 'FAIL'} {d.name}: verdict={v['verdict']} "
              f"(expected {exp['verdict']})")
        bad += 0 if ok else 1
    print(f"{len(cases) - bad}/{len(cases)} fixture cases decide as declared")
    return 0 if bad == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(prog="held_out_nonregression.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="selftest",
                    choices=("check", "selftest"))
    ap.add_argument("case", nargs="?", help="case directory (with check)")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--min-band", type=float, default=MIN_BAND)
    a = ap.parse_args(argv)
    if a.mode == "check":
        if not a.case:
            ap.error("check needs <case-dir>")
        return cmd_check(Path(a.case), a.min_band)
    return cmd_selftest(Path(a.root), a.min_band)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
