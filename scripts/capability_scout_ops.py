#!/usr/bin/env python3
"""Weekly-scout operations: dedupe, week-over-week diff, proof seal, cron guard.

The weekly runner (`weekly_capability_scout.py`) verifies citations and queues an
agent pass. This adds the compounding-loop discipline on top of its `week.json`
outputs — the difference between a cron that re-does the same work every week and
one that only surfaces what is new, proves it did, and notices when it has
stalled or drifted:

  dedupe   given all prior weeks + this week, print the source ids that are NEW
           this week. A weekly loop that re-queues last week's papers is noise.
  diff     the set delta between two named weeks (added / removed / retained).
  seal     hash a week's verified evidence into a proof sidecar; re-running seal
           on an unchanged week is idempotent, and a changed week without a new
           seal is detectable — the anti-silent-rewrite guard.
  guard    cron health: STALLED if the newest week is older than 2x the declared
           cadence, DRIFT if the scraped source set no longer matches the source
           registry. Both are exit 2 — a cron that quietly stopped finding new
           evidence looks identical to success without this.

Exit codes: 0 clean / 1 usage-or-file-missing / 2 a finding (stall, drift, or a
seal mismatch). Stdlib only, no network, no model. `seal` writes only its sidecar
under the week dir; every other verb is read-only.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / ".context" / "capability-scout"
SOURCES = REPO / "data" / "capability-scout-sources.json"
CRON = REPO / "data" / "capability-scout-weekly-cron.json"
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verified_ids(week_doc: dict) -> set:
    """Every id this week vouched for: arXiv + repos."""
    return set(week_doc.get("arxiv_verified", {})) | set(week_doc.get("repos_verified", {}))


def _week_docs(out_root: Path) -> dict:
    out = {}
    if out_root.is_dir():
        for wj in sorted(out_root.glob("*/week.json")):
            try:
                d = _load(wj)
            except json.JSONDecodeError:
                continue
            out[wj.parent.name] = d
    return out


def cmd_dedupe(args) -> int:
    docs = _week_docs(Path(args.out))
    if args.week not in docs:
        print(f"week not found: {args.week}", file=sys.stderr)
        return 1
    prior = set()
    for w, d in docs.items():
        if w < args.week:
            prior |= verified_ids(d)
    this = verified_ids(docs[args.week])
    new = sorted(this - prior)
    repeats = sorted(this & prior)
    print(json.dumps({"week": args.week, "new_ids": new, "repeat_ids": repeats,
                      "new_count": len(new), "repeat_count": len(repeats)}, indent=1))
    return 0


def cmd_diff(args) -> int:
    docs = _week_docs(Path(args.out))
    for w in (args.a, args.b):
        if w not in docs:
            print(f"week not found: {w}", file=sys.stderr)
            return 1
    a, b = verified_ids(docs[args.a]), verified_ids(docs[args.b])
    print(json.dumps({"from": args.a, "to": args.b,
                      "added": sorted(b - a), "removed": sorted(a - b),
                      "retained": sorted(a & b)}, indent=1))
    return 0


def _seal_body(week_doc: dict) -> str:
    """Canonical string over the verified evidence only — order-independent."""
    payload = {"arxiv": sorted(week_doc.get("arxiv_verified", {})),
               "repos": sorted(week_doc.get("repos_verified", {}))}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def cmd_seal(args) -> int:
    wdir = Path(args.out) / args.week
    wj = wdir / "week.json"
    if not wj.is_file():
        print(f"week.json not found: {wj}", file=sys.stderr)
        return 1
    doc = _load(wj)
    digest = hashlib.sha256(_seal_body(doc).encode("utf-8")).hexdigest()
    sidecar = wdir / "week.seal.json"
    if args.check:
        if not sidecar.is_file():
            print(f"no seal to check: {sidecar}", file=sys.stderr)
            return 1
        prev = _load(sidecar)
        if prev.get("evidence_sha256") != digest:
            print(f"SEAL_MISMATCH {args.week}: week.json changed since seal "
                  f"({prev.get('evidence_sha256','?')[:12]} -> {digest[:12]})")
            return 2
        print(f"OK seal matches: {args.week} {digest[:12]}")
        return 0
    seal = {"schema": "capability-scout-seal-v1", "week": args.week,
            "evidence_sha256": digest,
            "sealed_utc": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"),
            "arxiv_count": len(doc.get("arxiv_verified", {})),
            "repos_count": len(doc.get("repos_verified", {}))}
    sidecar.write_text(json.dumps(seal, indent=1) + "\n", encoding="utf-8")
    print(f"OK sealed {args.week}: {digest[:12]} "
          f"({seal['arxiv_count']} arxiv, {seal['repos_count']} repos)")
    return 0


def _iso_week_start(week: str) -> datetime.date:
    y, w = week.split("-W")
    return datetime.date.fromisocalendar(int(y), int(w), 1)


def cmd_guard(args) -> int:
    findings = []
    docs = _week_docs(Path(args.out))
    # STALL: newest week older than 2x cadence
    cadence_days = args.cadence_days
    if CRON.is_file():
        try:
            cadence_days = int(_load(CRON).get("cadence_days", cadence_days))
        except (json.JSONDecodeError, ValueError):
            pass
    if not docs:
        findings.append("NO_WEEKS: the scout has never produced a week.json")
    else:
        newest = max(docs)
        age = (args.now - _iso_week_start(newest)).days
        if age > 2 * cadence_days:
            findings.append(f"STALLED: newest week {newest} is {age}d old "
                            f"(> 2x cadence {cadence_days}d)")
    # DRIFT: scraped source slugs != registry enabled slugs
    if SOURCES.is_file():
        reg = {s["slug"] for s in _load(SOURCES).get("sources", [])
               if s.get("enabled", True)}
        if docs:
            scraped = {s["slug"] for s in docs[max(docs)].get("sources", [])}
            missing = reg - scraped
            extra = scraped - reg
            if missing or extra:
                findings.append(f"DRIFT: registry {sorted(reg)} vs scraped "
                                f"{sorted(scraped)} (missing={sorted(missing)}, "
                                f"extra={sorted(extra)})")
    if findings:
        for f in findings:
            print(f)
        print(f"\nguard: {len(findings)} finding(s)")
        return 2
    print(f"OK guard: newest {max(docs)}, cadence {cadence_days}d, sources aligned")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="weekly scout ops")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("dedupe",):
        s = sub.add_parser(name)
        s.add_argument("--week", required=True)
        s.add_argument("--out", default=str(DEFAULT_OUT))
    d = sub.add_parser("diff")
    d.add_argument("--a", required=True)
    d.add_argument("--b", required=True)
    d.add_argument("--out", default=str(DEFAULT_OUT))
    se = sub.add_parser("seal")
    se.add_argument("--week", required=True)
    se.add_argument("--out", default=str(DEFAULT_OUT))
    se.add_argument("--check", action="store_true")
    g = sub.add_parser("guard")
    g.add_argument("--out", default=str(DEFAULT_OUT))
    g.add_argument("--cadence-days", type=int, default=7)
    g.add_argument("--now", type=datetime.date.fromisoformat,
                   default=datetime.date.today())
    args = ap.parse_args(argv)
    try:
        return {"dedupe": cmd_dedupe, "diff": cmd_diff,
                "seal": cmd_seal, "guard": cmd_guard}[args.cmd](args)
    except FileNotFoundError as e:
        print(f"file not found: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
