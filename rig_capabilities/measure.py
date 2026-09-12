"""Measurement spine for the durable/repeatable qualification gate (S01-S07).

Frozen constants live in the rules file (measurement-rules-v1.yaml); this module
only implements the estimators and the crash-safe recorder:

- wilson_lb(): one-sided Wilson score lower bound (never Wald — the zero/one
  boundary is exactly where Wald is unreliable, see research wave 1).
- alpha_j(): Bonferroni-style geometric sequential spend, 0.05/(m*2**j).
- Recorder: append-only JSONL, fsync per line, duplicate trial_id REJECTED
  (idempotent retries; WAL record-then-act shape; re-seal mints new ids).

Stdlib only. `measure.py selfcheck <rules>` is the slice done-test.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
from contextlib import contextmanager
from statistics import NormalDist

_Z = NormalDist()


def wilson_lb(successes: int, n: int, alpha: float = 0.05) -> float:
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError(f"need 0<=successes<=n and n>0, got {successes}/{n}")
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must be in (0, 0.5)")
    z = _Z.inv_cdf(1.0 - alpha)
    p = successes / n
    denom = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return (centre - spread) / denom


def alpha_j(m: int, j: int) -> float:
    if m < 1 or j < 1:
        raise ValueError("m and j must be >= 1")
    return 0.05 / (m * 2 ** j)


class Recorder:
    """Append-only trial ledger. Retry-safe AND concurrency-safe: one
    process-wide exclusive flock spans heal -> ID scan -> append+fsync, so a
    duplicate trial_id can never land even under competing writers."""

    def __init__(self, path: str):
        self.path = path

    def existing_ids(self) -> set[str]:
        ids = set()
        if os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            ids.add(json.loads(line)["trial_id"])
                        except (json.JSONDecodeError, KeyError):
                            continue  # torn tail line: ignored, never trusted
        return ids

    def heal_tail(self) -> str | None:
        """Crash-safe append needs a newline-terminated file. A torn final line
        (crash mid-write) is truncated back to the last newline and the
        fragment preserved in a .recovered sidecar — never coalesced with the
        next row. Returns the removed fragment, if any."""
        if not os.path.exists(self.path):
            return None
        with open(self.path, "rb+") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() == 0:
                return None
            f.seek(-1, os.SEEK_END)
            if f.read(1) == b"\n":
                return None
            f.seek(0)
            data = f.read()
            cut = data.rfind(b"\n") + 1  # 0 when no complete line exists
            fragment = data[cut:].decode("utf-8", "replace")
            f.seek(cut)
            f.truncate()
            f.flush()
            os.fsync(f.fileno())
        side = f"{self.path}.recovered-{int(time.time())}"
        with open(side, "w") as f:
            f.write(fragment + "\n")
            f.flush()
            os.fsync(f.fileno())
        return fragment

    @contextmanager
    def _locked(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        lk = open(self.path + ".lock", "w")
        try:
            fcntl.flock(lk, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)
            lk.close()

    def _append_locked(self, row: dict) -> None:
        self.heal_tail()
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def append(self, trial_id: str, cell: str, outcome: str, **extra) -> dict:
        if outcome not in ("success", "failure"):
            raise ValueError("outcome must be success|failure")
        row = {"trial_id": trial_id, "cell": cell, "outcome": outcome,
               "ts": time.time(), **extra}
        with self._locked():
            self._append_locked(row)
        return row

    def record_once(self, trial_id: str, cell: str, outcome: str) -> str:
        """One critical section: scan-then-append under the same lock.
        Returns 'recorded' or 'duplicate'. Safe to retry after a crash."""
        with self._locked():
            if trial_id in self.existing_ids():
                return "duplicate"
            self._append_locked({"trial_id": trial_id, "cell": cell,
                                 "outcome": outcome, "ts": time.time()})
            return "recorded"


def record_idempotent(rec: Recorder, trial_id: str, cell: str, outcome: str) -> str:
    return rec.record_once(trial_id, cell, outcome)




def _mini_yaml(path: str) -> dict:
    """Three-level YAML subset (root -> section -> item -> scalar); no PyYAML."""
    root: dict = {}
    section: dict | None = None
    item: dict | None = None
    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            key, _, val = line.strip().partition(":")
            val = val.strip()
            if indent == 0:
                section = root[key] = {}
                item = None
            elif indent == 2:
                if section is None:
                    raise ValueError(f"orphan line: {raw!r}")
                if val == "":
                    item = section[key] = {}
                else:
                    section[key] = val
                    item = None
            elif indent >= 4:
                if item is None:
                    raise ValueError(f"orphan deep line: {raw!r}")
                item[key] = val
            else:
                raise ValueError(f"unsupported rules line: {raw!r}")
    return root
REQUIRED_SCALAR_KEYS = ("command", "estimator", "min_trials")


def selfcheck(rules_path: str) -> int:
    rules = _mini_yaml(rules_path)
    errors: list[str] = []

    # 1. every scalar: keys present, command DRY-PARSES to an executable
    #    template (real script path + required flags + placeholders), estimator
    #    honestly typed (wilson-lb-* for binaries, count-* for counts)
    import shlex
    scalars = rules.get("scalars") or {}
    if len(scalars) < 5:
        errors.append(f"need >=5 scalars, got {len(scalars)}")
    for name, spec in scalars.items():
        for key in REQUIRED_SCALAR_KEYS:
            if not spec.get(key):
                errors.append(f"{name}: missing {key}")
        argv = shlex.split(spec.get("command", ""))
        if len(argv) < 3 or argv[0] != "python3" or not argv[1].endswith("measure.py"):
            errors.append(f"{name}: command not a measure.py invocation")
        elif not os.path.exists(argv[1]):
            errors.append(f"{name}: script missing: {argv[1]}")
        for flag, placeholder in (("--trial-id", "{trial_id}"),
                                  ("--cell", "{cell}"),
                                  ("--outcome", "{outcome}")):
            if flag not in argv:
                errors.append(f"{name}: command missing {flag}")
            if placeholder not in spec.get("command", ""):
                errors.append(f"{name}: command missing {placeholder}")
        est = spec.get("estimator", "")
        if not (est.startswith("wilson-lb-") or est.startswith("count-")):
            errors.append(f"{name}: estimator not wilson-lb-*/count-*: {est!r}")

    # 2. floors match the frozen contract
    want = {"durable_min_runs": "10", "durable_min_spacing_hours": "24",
            "repeatable_min_trials": "72", "joint_lb_floor": "0.95",
            "joint_rule": "min"}
    cons = rules.get("constraints") or {}
    for key, expect in want.items():
        if cons.get(key) != expect:
            errors.append(f"constraints.{key}={cons.get(key)!r} expected {expect!r}")

    # 3. estimator known-values regression (planted boundaries)
    if not wilson_lb(72, 72, 0.05) >= 0.95:
        errors.append("72/72 must clear 0.95 one-sided")
    if wilson_lb(71, 72, 0.05) >= 0.95:
        errors.append("71/72 must NOT clear 0.95 (gate needs a real floor)")
    if wilson_lb(0, 72, 0.05) >= 0.05:
        errors.append("0/72 lower bound must be near zero")

    # 4. alpha spend: first 10 looks at m=1 must stay under 0.05 total
    total = sum(alpha_j(1, j) for j in range(1, 11))
    if total > 0.05:
        errors.append(f"alpha spend over 10 looks = {total} > 0.05")

    # 5. recorder idempotence on a throwaway ledger
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rec = Recorder(os.path.join(td, "trials.jsonl"))
        a = record_idempotent(rec, "t1", "C01", "success")
        b = record_idempotent(rec, "t1", "C01", "success")
        c = record_idempotent(rec, "t2", "C01", "failure")
        if (a, b, c) != ("recorded", "duplicate", "recorded"):
            errors.append(f"dedupe broken: {(a, b, c)}")
        rows = [json.loads(l) for l in open(os.path.join(td, "trials.jsonl"))]
        if len(rows) != 2:
            errors.append(f"duplicate landed: {len(rows)} rows")

    # 6. torn-tail crash fixture: unterminated fragment must be healed to the
    # last newline, preserved in a sidecar, and never coalesced with next row
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "trials.jsonl")
        with open(p, "w") as f:
            f.write(json.dumps({"trial_id": "t1", "cell": "C01",
                                "outcome": "success"}) + "\n")
            f.write('{"trial_id": "t2", "cell": "C01", "out')  # crash mid-write
        rec = Recorder(p)
        frag = rec.heal_tail()
        status = record_idempotent(rec, "t3", "C01", "success")
        rows = [json.loads(l) for l in open(p)]
        if frag is None or '"t2"' not in frag:
            errors.append("torn fragment not healed/returned")
        if status != "recorded" or [r["trial_id"] for r in rows] != ["t1", "t3"]:
            errors.append(f"torn-tail recovery lost rows: {status} {[r['trial_id'] for r in rows]}")
        if not any(fn.startswith("trials.jsonl.recovered-") for fn in os.listdir(td)):
            errors.append("fragment not preserved to sidecar")

    # 7. concurrent contention (advisor blocker 3): 8 real subprocesses race
    # ONE shared trial_id through the CLI -> exactly one row lands. Plain
    # Popen (no mp semaphores) and the real `record` entrypoint.
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "trials.jsonl")
        me = os.path.abspath(__file__)
        def spawn(tid):
            return subprocess.Popen(
                [sys.executable, me, "record", "--ledger", p,
                 "--trial-id", tid, "--cell", "C01", "--outcome", "success"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs = [spawn("shared") for _ in range(8)]
        codes = [c.wait(timeout=60) for c in procs]
        rows = [json.loads(l) for l in open(p)] if os.path.exists(p) else []
        if sum(c == 0 for c in codes) != 1 or len(rows) != 1:
            errors.append(f"shared-ID race: {codes.count(0)} exit-0,"
                          f" {len(rows)} rows (lock not holding)")
        procs = [spawn(f"u{i}") for i in range(8)]
        codes = [c.wait(timeout=60) for c in procs]
        rows = [json.loads(l) for l in open(p)]
        if codes.count(0) != 8 or len(rows) != 9:
            errors.append(f"distinct-ID race: {codes.count(0)} exit-0,"
                          f" {len(rows)} rows (expected 8 / 9)")

    print(json.dumps({"ok": not errors, "errors": errors,
                      "wilson_lb_72_72": wilson_lb(72, 72, 0.05),
                      "wilson_lb_71_72": wilson_lb(71, 72, 0.05)}))
    return 0 if not errors else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="measure")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("selfcheck")
    sc.add_argument("rules")
    lb = sub.add_parser("lb")
    lb.add_argument("successes", type=int)
    lb.add_argument("n", type=int)
    lb.add_argument("--alpha", type=float, default=0.05)
    rc = sub.add_parser("record")
    rc.add_argument("--ledger", required=True)
    rc.add_argument("--trial-id", required=True)
    rc.add_argument("--cell", required=True)
    rc.add_argument("--outcome", required=True, choices=("success", "failure"))
    args = ap.parse_args(argv)
    if args.cmd == "selfcheck":
        return selfcheck(args.rules)
    if args.cmd == "lb":
        print(f"{wilson_lb(args.successes, args.n, args.alpha):.6f}")
        return 0
    status = record_idempotent(Recorder(args.ledger), args.trial_id,
                               args.cell, args.outcome)
    print(status)
    return 0 if status == "recorded" else 2


if __name__ == "__main__":
    sys.exit(main())
