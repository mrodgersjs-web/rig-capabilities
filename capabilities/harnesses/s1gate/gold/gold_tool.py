#!/usr/bin/env python3
"""gold_tool -- the s1gate answer key, with provenance and a regression verb.

Why this exists, one line from the doctrine it was built from:
"Every eval number you report is a comparison against something. Get it wrong
and every downstream metric is precise, reproducible, and meaningless."

What this adds over fixtures/run_fixtures.py (which it does NOT replace):
  * per-case provenance -- who decided, when, why, against which question
    version, and whether it was ever double-labelled or adjudicated;
  * `add` -- the regression-case rule needs a verb, not a policy statement;
  * supersede instead of delete, so the hardest tests cannot be tidied away;
  * agreement reporting against gold rather than a bare pass/fail.

Usage
-----
  gold_tool.py promote                    fold fixtures/ into gold.json (idempotent)
  gold_tool.py run [--kind R] [--json]    run the key through the gate
  gold_tool.py add --kind R --file F --gold green|red --reason "..." [--regression]
  gold_tool.py supersede --id CASE_ID --reason "..."
  gold_tool.py report                     coverage + provenance summary

Exit codes: 0 ok, 1 gold mismatch, 3 usage/config error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
S1 = HERE.parent                      # capabilities/harnesses/s1gate
FIXTURES = S1 / "fixtures"
GOLD = HERE / "gold.json"
ROOT = S1.parents[2]                  # rig-capabilities repo root
GATE = Path.home() / ".rig" / "bin" / "rig-s1gate"

PROMOTED_BY = "fixture author"
PROMOTED_ON = "2026-09-28"


def load() -> dict:
    return json.loads(GOLD.read_text(encoding="utf-8"))


def save(doc: dict) -> None:
    GOLD.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- promote

def cmd_promote(_args) -> int:
    """Fold fixtures/expected.json into gold.json.

    Idempotent by design: existing case records keep their provenance and any
    regression/superseded flags. Only genuinely new cases are appended, so
    re-running promote can never quietly rewrite history.
    """
    expected = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    doc = load()
    kinds = doc.setdefault("kinds", {})
    added = kept = 0

    for kind, cases in sorted(expected.items()):
        bucket = kinds.setdefault(kind, {"question_version": "v0-promoted", "cases": []})
        have = {c["id"] for c in bucket["cases"]}
        for name, want in sorted(cases.items()):
            cid = f"{kind}/{name}"
            if cid in have:
                kept += 1
                continue
            src = FIXTURES / kind / name
            bucket["cases"].append({
                "id": cid, "kind": kind,
                "path": str(src.relative_to(ROOT)),
                "gold": want, "source": "promoted-from-fixtures",
                "decided_by": PROMOTED_BY, "decided_on": PROMOTED_ON,
                "reason": "human-decided expectation carried over from "
                          "fixtures/expected.json; never double-labelled",
                "double_labelled": False, "adjudicated": False,
                "regression": False, "status": "active",
            })
            added += 1

    save(doc)
    total = sum(len(v["cases"]) for v in kinds.values())
    print(f"gold: {added} promoted, {kept} already present, {total} total "
          f"across {len(kinds)} kind(s)")
    print("these carry provenance but were never double-labelled: their "
          "agreement rate is a FLOOR, not a measurement.")
    return 0


# ---------------------------------------------------------------- run

def _gate_check(kind: str, path: Path) -> tuple[str, str]:
    proc = subprocess.run(
        [str(GATE), "check", kind, "--file", str(path),
         "--subject", f"gold:{kind}/{path.name}", "--json"],
        capture_output=True, text=True, cwd=ROOT)
    code = proc.returncode
    got = "infra-error" if code == 3 else ("green" if code == 0 else "red")
    try:
        verdict = json.loads(proc.stdout).get("verdict", "?")
    except Exception:  # noqa: BLE001
        verdict = "?"
    return got, verdict


def cmd_run(args) -> int:
    doc = load()
    kinds = doc.get("kinds", {})
    if args.kind:
        if args.kind not in kinds:
            print(f"gold: no kind {args.kind!r}", file=sys.stderr)
            return 3
        kinds = {args.kind: kinds[args.kind]}

    rows = []
    for kind, bucket in sorted(kinds.items()):
        for c in bucket["cases"]:
            if c.get("status") != "active":
                continue
            p = ROOT / c["path"]
            if not p.exists():
                rows.append((c["id"], c["gold"], "missing", "MISSING", False))
                continue
            got, verdict = _gate_check(kind, p)
            rows.append((c["id"], c["gold"], got, verdict, got == c["gold"]))

    bad = [r for r in rows if not r[4]]
    if args.json:
        print(json.dumps({"cases": len(rows), "mismatches": len(bad),
                          "rows": [{"id": r[0], "gold": r[1], "got": r[2],
                                    "verdict": r[3], "ok": r[4]} for r in rows]}, indent=2))
    else:
        for cid, want, got, verdict, ok in rows:
            print(f"{cid:42} want={want:6} got={got:11} verdict={verdict:9} "
                  f"{'OK' if ok else 'MISMATCH'}")
        agree = len(rows) - len(bad)
        pct = (100.0 * agree / len(rows)) if rows else 0.0
        print("-" * 68)
        print(f"agreement with gold: {agree}/{len(rows)} ({pct:.1f}%)")
        if bad:
            print(f"{len(bad)} mismatch(es). Each is either a bad question or a "
                  f"bad label -- review before changing either.")
    return 1 if bad else 0


# ---------------------------------------------------------------- add / supersede

def cmd_add(args) -> int:
    src = Path(args.file)
    if not src.exists():
        print(f"gold: no such file {src}", file=sys.stderr)
        return 3
    dest = FIXTURES / args.kind / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    doc = load()
    bucket = doc.setdefault("kinds", {}).setdefault(
        args.kind, {"question_version": args.question_version or "v1", "cases": []})
    cid = f"{args.kind}/{src.name}"
    if any(c["id"] == cid for c in bucket["cases"]):
        print(f"gold: {cid} exists. Supersede it to retire it, or edit its "
              f"record -- never delete it.", file=sys.stderr)
        return 3
    bucket["cases"].append({
        "id": cid, "kind": args.kind, "path": str(dest.relative_to(ROOT)),
        "gold": args.gold,
        "source": "regression-case" if args.regression else "manual",
        "decided_by": args.decided_by or "human",
        "decided_on": time.strftime("%Y-%m-%d"), "reason": args.reason,
        "double_labelled": False, "adjudicated": False,
        "regression": bool(args.regression), "status": "active",
    })
    save(doc)
    print(f"gold: added {cid} ({args.gold})" +
          ("  [REGRESSION CASE - never delete]" if args.regression else ""))
    return 0


def cmd_supersede(args) -> int:
    doc = load()
    for bucket in doc.get("kinds", {}).values():
        for c in bucket["cases"]:
            if c["id"] == args.id:
                if c.get("status") == "superseded":
                    print(f"gold: {args.id} already superseded", file=sys.stderr)
                    return 3
                c["status"] = "superseded"
                c["superseded_on"] = time.strftime("%Y-%m-%d")
                c["superseded_reason"] = args.reason
                save(doc)
                print(f"gold: superseded {args.id} -- kept in the key, excluded "
                      f"from runs. Reason recorded.")
                return 0
    print(f"gold: no case {args.id}", file=sys.stderr)
    return 3


# ---------------------------------------------------------------- report

def cmd_report(_args) -> int:
    shipped = sorted(p.stem for p in (S1 / "rubrics").glob("*.json"))
    doc = load()
    kinds = doc.get("kinds", {})
    active = sum(1 for b in kinds.values() for c in b["cases"] if c.get("status") == "active")
    supers = sum(1 for b in kinds.values() for c in b["cases"] if c.get("status") == "superseded")
    regress = sum(1 for b in kinds.values() for c in b["cases"] if c.get("regression"))
    dbl = sum(1 for b in kinds.values() for c in b["cases"] if c.get("double_labelled"))
    adj = sum(1 for b in kinds.values() for c in b["cases"] if c.get("adjudicated"))

    print(f"gold report -- {GOLD.relative_to(ROOT)}")
    print(f"  kinds with gold : {len(kinds)} of {len(shipped)} shipped rubrics")
    print(f"  cases           : {active} active, {supers} superseded, {regress} regression")
    print(f"  provenance      : {dbl} double-labelled, {adj} adjudicated")
    print()
    for kind, bucket in sorted(kinds.items(), key=lambda kv: -len(kv[1]["cases"])):
        n = len([c for c in bucket["cases"] if c.get("status") == "active"])
        print(f"  {kind:24} {n:3} active  q_version={bucket.get('question_version')}")
    missing = [r for r in shipped if r not in kinds]
    print()
    print(f"  NO GOLD ({len(missing)}): " + ", ".join(missing[:18]) +
          (" ..." if len(missing) > 18 else ""))
    print()
    print("  next action: add gold for the highest-volume rubrics in "
          "`rig-s1gate health`. Stratify boring / boundary / adversarial / "
          "regression. Label blind, twice, adjudicate.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="s1gate gold key")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("promote").set_defaults(fn=cmd_promote)
    r = sub.add_parser("run")
    r.add_argument("--kind"); r.add_argument("--json", action="store_true")
    r.set_defaults(fn=cmd_run)
    a = sub.add_parser("add")
    a.add_argument("--kind", required=True); a.add_argument("--file", required=True)
    a.add_argument("--gold", required=True, choices=["green", "red"])
    a.add_argument("--reason", required=True); a.add_argument("--regression", action="store_true")
    a.add_argument("--decided-by"); a.add_argument("--question-version")
    a.set_defaults(fn=cmd_add)
    s = sub.add_parser("supersede")
    s.add_argument("--id", required=True); s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_supersede)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
