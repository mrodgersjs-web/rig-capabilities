#!/usr/bin/env python3
"""Paired-run evidence checker — stdlib only. An unpaired claim is noise.

Mechanism (arXiv:2608.11888 'Agent Skills Can Be Harmful', video TA5QzGTQU_U;
arXiv:2608.13951 HELIX, video 5S9NemR7Fwo; repos benchflow-ai/skillsbench,
HKUDS/HELIX): hold the model, framework, tools, repo, container, input data and
verifier fixed and vary exactly ONE thing — the skill, or one named swap point.
A claim about a change is admissible only from such a PAIRED run: both sides'
config hashes recorded, the single differing key named. Acceptance is two-axis:
correctness delta AND cost delta (tokens, wall time) — ">=2x on either axis is
an efficiency regression even when the run passes" (2608.11888 found 182 such
regressions no pass/fail gate catches). Failed variants are RETAINED: the red
half of the pair is eval data that shrinks the search space, so a ledger row
recorded once is never allowed to disappear because it became inconvenient
("the failed harness configurations are real gold mines", 5S9NemR7Fwo).

Ledger: JSONL, one run record per line:
  {"id": "PR-01", "pair_id": "P-77", "side": "baseline", "task": "T-42",
   "claim": false, "correct": true, "tokens": 48200, "wall_ms": 185000,
   "config": {...frozen everything...}, "config_hash": "<sha256>",
   "differs_in": "skill", "verifier": "done-test", "trace": "traces/a.jsonl"}

Rules, all mechanical — exit 1 (never a silent pass) when:
  * a row claims an improvement ("claim": true) but no single counterpart
    shares its pair_id          -> no_pair / ambiguous_pair;
  * either side lacks config or config_hash, or the declared hash does not
    match the recomputed canonical hash of its own config (tamper check), or
    a declared cost field is missing/non-numeric -> cost delta unevaluable;
  * the two configs are identical (hash-for-hash)      -> identical_config:
    a claimed improvement with nothing varied is theater;
  * more than one config key differs -> two_variables_differ: the pair proves
    nothing about any single change, so it is rejected outright;
  * exactly one key differs but the claiming row does not name it in
    differs_in, or names the wrong key -> differs_in_missing/mismatch;
  * the claimed variant costs >= 2x its baseline on tokens or wall_ms ->
    cost_regression, flagged even when correctness improved;
  * --baseline PATH names an earlier ledger whose recorded ids are not all
    still present -> retained_negative_missing, one violation per dropped id.

Otherwise exit 0, echoing each claimed pair's correctness delta and token /
wall-time multipliers to stdout. THE CHECKER NEVER REWRITES THE LEDGER: it
opens every file read-only; retention it enforces, editing it never performs.

Exit codes: 0 = every claim admissible · 1 = any violation (all printed, none
swallowed) · unreadable input is red, never green-on-noise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXIT_GREEN = 0
EXIT_RED = 1
COST_FIELDS = ("tokens", "wall_ms")
REGRESSION_RATIO = 2.0  # >=2x on either cost axis is a regression


def canonical_hash(config: dict) -> str:
    """sha256 over canonical JSON — the identity of a frozen config."""
    blob = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _load(path, origin, violations):
    """Parse a JSONL ledger read-only. Any unreadable/malformed input is red."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        violations.append(f"{origin}_unreadable: {path}: {e.strerror or e}")
        return []
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        where = f"{origin}:{n}"
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            violations.append(f"{where}: row_not_json: {e}")
            continue
        if not isinstance(obj, dict):
            violations.append(f"{where}: row_not_object: a ledger row must be one JSON object")
            continue
        rid = obj.get("id")
        if not isinstance(rid, str) or not rid.strip():
            violations.append(f"{where}: row_missing_id: every retained result needs a stable id")
            continue
        obj["_where"] = where
        rows.append(obj)
    seen = {}
    for r in rows:
        if r["id"] in seen:
            violations.append(f"{r['_where']}: duplicate_row_id: '{r['id']}' "
                              f"already recorded at {seen[r['id']]}")
        else:
            seen[r["id"]] = r["_where"]
    return rows


def _config_side(row, side_id, violations):
    """Return the row's config if it carries a self-consistent hashed config."""
    cfg = row.get("config")
    declared = row.get("config_hash")
    if not isinstance(cfg, dict) or not cfg:
        violations.append(f"{row['_where']}: config_missing: {side_id} carries no config map, "
                          f"so 'everything else frozen' cannot be proven")
        return None
    if not isinstance(declared, str) or not declared.strip():
        violations.append(f"{row['_where']}: config_hash_missing: {side_id} must record the "
                          f"hash of its own frozen config")
        return None
    actual = canonical_hash(cfg)
    if actual != declared.strip():
        violations.append(f"{row['_where']}: config_hash_mismatch: declared {declared.strip()!r} "
                          f"does not match recomputed {actual!r} — the config was edited "
                          f"after (or not at) recording")
        return None
    return cfg


def _cost(row, field, side_id, violations):
    v = row.get(field)
    if not _is_number(v):
        violations.append(f"{row['_where']}: missing_cost_delta: {side_id} has no numeric "
                          f"{field!r}; acceptance is correctness AND cost, both axes")
        return None
    if v <= 0:
        violations.append(f"{row['_where']}: nonpositive_cost: {side_id} {field}={v}")
        return None
    return v


def _ratio(new, old):
    return new / old if old else float("inf")


def _check_pair(claim, peers, violations):
    """Validate one claimed improvement against its single counterpart.
    Returns a summary line (or None when the pair was rejected)."""
    pid = claim.get("pair_id")
    where = claim["_where"]
    if not isinstance(pid, str) or not pid.strip():
        violations.append(f"{where}: no_pair: a claimed improvement must name a pair_id")
        return None
    if len(peers) == 0:
        violations.append(f"{where}: no_pair: pair {pid!r} has no counterpart run recorded — "
                          f"an improvement claim needs the frozen baseline beside it")
        return None
    if len(peers) > 1:
        violations.append(f"{where}: ambiguous_pair: pair {pid!r} has {len(peers)} "
                          f"counterparts; a controlled experiment has two sides")
        return None
    other = peers[0]
    cfg_a = _config_side(claim, "claimed side", violations)
    cfg_b = _config_side(other, "counterpart side", violations)
    costs = {}
    ok_costs = True
    for row, side in ((claim, "claimed side"), (other, "counterpart side")):
        got = [_cost(row, f, side, violations) for f in COST_FIELDS]
        ok_costs = ok_costs and all(g is not None for g in got)
        costs[side] = got
    if cfg_a is None or cfg_b is None or not ok_costs:
        return None
    keys = set(cfg_a) | set(cfg_b)
    diff = sorted(k for k in keys if cfg_a.get(k, "<absent>") != cfg_b.get(k, "<absent>"))
    if len(diff) == 0:
        violations.append(f"{where}: identical_config: pair {pid!r} ran the same configuration "
                          f"twice and calls the second run an improvement")
        return None
    if len(diff) > 1:
        violations.append(f"{where}: two_variables_differ: pair {pid!r} varies "
                          f"{', '.join(diff)} — a pair with >1 free variable proves nothing "
                          f"about any single change and is rejected outright")
        return None
    named = claim.get("differs_in")
    if not isinstance(named, str) or not named.strip():
        violations.append(f"{where}: differs_in_missing: the single difference "
                          f"{diff[0]!r} must be named on the claiming row")
        return None
    if named.strip() != diff[0]:
        violations.append(f"{where}: differs_in_mismatch: claims {named.strip()!r}, "
                          f"configs actually differ in {diff[0]!r}")
        return None
    base_tok, base_wall = costs["counterpart side"]
    var_tok, var_wall = costs["claimed side"]
    rt, rw = _ratio(var_tok, base_tok), _ratio(var_wall, base_wall)
    c_base, c_var = bool(other.get("correct")), bool(claim.get("correct"))
    if c_base and c_var and (rt >= REGRESSION_RATIO or rw >= REGRESSION_RATIO):
        violations.append(f"{where}: cost_regression: pair {pid!r} costs "
                          f"x{rt:.2f} tokens / x{rw:.2f} wall time at unchanged correctness — "
                          f">=2x on either axis is a regression even when the run passes")
    delta = "improved" if (c_var and not c_base) else \
            "regressed" if (c_base and not c_var) else "unchanged"
    return (f"PAIR {pid} ({claim.get('task', '?')}): correctness "
            f"{str(c_base).lower()}->{str(c_var).lower()} delta={delta} | "
            f"tokens {base_tok}->{var_tok} x{rt:.2f} | "
            f"wall_ms {base_wall}->{var_wall} x{rw:.2f} | differs_in={diff[0]}")


def check(path, baseline=None) -> int:
    """Adjudicate one paired-run ledger. Returns the exit code (0/1).
    When `baseline` is given, every id recorded there must still be present —
    retained negatives are not deletable evidence. Read-only, always."""
    violations: list = []
    summaries: list = []
    rows = _load(path, "ledger", violations)
    by_pair: dict = {}
    for r in rows:
        pid = r.get("pair_id")
        if isinstance(pid, str) and pid.strip():
            by_pair.setdefault(pid.strip(), []).append(r)
    for r in rows:
        if r.get("claim") is True:
            peers = [p for p in by_pair.get(str(r.get("pair_id") or "").strip(), [])
                     if p is not r]
            line = _check_pair(r, peers, violations)
            if line:
                summaries.append(line)
    if baseline is not None:
        bl = _load(baseline, "baseline", violations)
        present = {r["id"] for r in rows}
        for r in bl:
            if r["id"] not in present:
                violations.append(
                    f"baseline:{r['_where']}: retained_negative_missing: '{r['id']}' was "
                    f"recorded in {baseline} and is gone from {path} — a red run deleted for "
                    f"inconvenience destroys the negative half of the evidence")
    for v in violations:
        print(f"PAIRED-RUNS RED: {v}", file=sys.stderr)
    for s in summaries:
        print(s)
    if not violations and not summaries:
        print("PAIRED-RUNS GREEN: no improvement claims recorded "
              "(no claim, no verdict — nothing here is admissible evidence either)")
    return EXIT_RED if violations else EXIT_GREEN


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="paired_runs.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=("check",),
                    help="the only verb: adjudicate a ledger, never edit it")
    ap.add_argument("ledger", help="JSONL paired-run ledger to adjudicate")
    ap.add_argument("--baseline", default=None,
                    help="earlier ledger; every id it recorded must still be retained")
    args = ap.parse_args(argv)
    return check(args.ledger, baseline=args.baseline)


if __name__ == "__main__":
    sys.exit(main())
