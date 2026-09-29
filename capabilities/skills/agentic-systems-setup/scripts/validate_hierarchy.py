#!/usr/bin/env python3
"""Validate the agentic-systems-setup org chart (hierarchy.json) against what is on disk.

Adapted from capabilities/skills/app-studio/scripts/validate_hierarchy.py. Checks (each
violation prints as "V<n> <kind> <id>: <why>"):
  V1  manifest shape: six kinds, one meta each, main and sub lists present
  V2  every path resolves; a skill path is a directory holding SKILL.md
      (entries marked "expected": true that have not landed print PENDING; --strict makes them V2)
  V3  every sub names a parent in the same kind; parent chains reach meta or main, no cycles
  V4  every sub is named in its parent's file (the orphan the 2026-09-27 audit found)
  V5  every stage has at least one sub-skill (stage or stages); every lane has a main skill
  V6  every JEV rubric loads with questions and rules; every claimed kind maps to it in
      work-criteria.json ("kinds_proposed" print PENDING registration, --strict makes them V6)
  V7  every new hook is executable and has fixture cases
  V8  the lesson ledger and the inventory exist and are non-empty; the candidates file (if named)
      holds well-formed rows with status "candidate" and compilable triggers
  V9  every new skill's frontmatter fits in head_bytes (4096): beyond it the loader cannot see it
  V10 the meta agent (conductor) names every framework main skill (agentic-setup-*) and every
      sub-skill, so no framework is reachable only by accident

Usage:
  validate_hierarchy.py [--manifest PATH] [--strict] [--plant NAME]
Plants mutate an in-memory copy; exit 2 when the named violation is CAUGHT, 0 when ESCAPED:
  bad_path->V2, orphan_sub->V3, unwired_sub->V4, stage_gap->V5, lane_gap->V5,
  kind_unregistered->V6, bad_candidate->V8, fat_frontmatter->V9, unrouted_framework->V10
Exit 0 clean, 2 violation(s) (or plant caught), 1 usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[2]
KINDS = ("skills", "agents", "harnesses", "loops", "hooks", "jev")
WORK = REPO / "capabilities/harnesses/s1gate/work-criteria.json"
PLANTS = {"bad_path": "V2", "orphan_sub": "V3", "unwired_sub": "V4", "stage_gap": "V5",
          "lane_gap": "V5", "kind_unregistered": "V6", "bad_candidate": "V8", "fat_frontmatter": "V9",
          "unrouted_framework": "V10"}
CAND_FIELDS = ("lesson_id", "trigger", "match", "mandated_check", "evidence", "status")


def resolve(p: str | None) -> Path | None:
    if not p:
        return None
    if p.startswith("~/"):
        return Path.home() / p[2:]
    return Path(p) if p.startswith("/") else REPO / p


def exists(kind: str, e: dict) -> bool:
    p = resolve(e.get("path"))
    if p is None:
        return False
    if kind == "skills" or p.is_dir():
        return (p / "SKILL.md").is_file()
    return p.is_file()


def text_of(e: dict) -> str:
    p = resolve(e.get("path"))
    if p is None:
        return ""
    if p.is_dir():
        p = p / "SKILL.md"
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def covers(e: dict, stage: str) -> bool:
    return e.get("stage") == stage or stage in (e.get("stages") or [])


def check(m: dict, strict: bool) -> tuple[list[str], list[str]]:
    v: list[str] = []
    pending: list[str] = []
    tiers = m.get("tiers") or {}
    for k in KINDS:
        t = tiers.get(k)
        if not isinstance(t, dict) or not isinstance(t.get("meta"), dict) or not isinstance(t.get("main"), list) or not isinstance(t.get("sub"), list):
            v.append(f"V1 {k} -: tier missing meta, main, or sub")
    if v:
        return v, pending

    for k in KINDS:
        t = tiers[k]
        for e in [t["meta"], *t["main"], *t["sub"]]:
            if exists(k, e):
                continue
            if e.get("expected") and not strict:
                pending.append(f"PENDING {k} {e.get('id')} ({e.get('owner', '?')}): not landed at {e.get('path')}")
            else:
                v.append(f"V2 {k} {e.get('id')}: path does not resolve: {e.get('path')}")

    for k in KINDS:
        t = tiers[k]
        ids = {t["meta"]["id"]: t["meta"], **{e["id"]: e for e in t["main"]}, **{e["id"]: e for e in t["sub"]}}
        anchors = {t["meta"]["id"], *(e["id"] for e in t["main"])}
        for e in t["sub"]:
            seen, cur = set(), e
            while True:
                par = cur.get("parent")
                if par is None or par not in ids:
                    v.append(f"V3 {k} {e['id']}: parent chain breaks at {cur['id']} (parent {par!r} not in tier)")
                    break
                if par in anchors:
                    break
                if par in seen:
                    v.append(f"V3 {k} {e['id']}: parent cycle through {par}")
                    break
                seen.add(par)
                cur = ids[par]

    for k in KINDS:
        t = tiers[k]
        ids = {t["meta"]["id"]: t["meta"], **{e["id"]: e for e in t["main"]}, **{e["id"]: e for e in t["sub"]}}
        for e in t["sub"]:
            par = ids.get(e.get("parent"))
            if par is not None and e["id"] not in text_of(par):
                v.append(f"V4 {k} {e['id']}: not named in its parent {par['id']}'s file")

    sk = tiers["skills"]
    for s in [x["id"] for x in m.get("stages", [])]:
        if not any(covers(e, s) for e in sk["sub"]):
            v.append(f"V5 skills {s}: stage has no sub-skill")
    for lane in [x["id"] for x in m.get("lanes", [])]:
        live = [e for e in sk["main"] if e.get("lane") == lane and (strict is False or exists("skills", e))]
        if not live:
            v.append(f"V5 skills {lane}: lane has no main skill")

    try:
        kinds_map = json.loads(WORK.read_text())["kinds"]
    except (OSError, ValueError, KeyError):
        kinds_map = {}
        v.append("V6 jev work-criteria.json: unreadable")
    j = tiers["jev"]
    for e in [j["meta"], *j["main"], *j["sub"]]:
        p = resolve(e.get("path"))
        try:
            r = json.loads(p.read_text()) if p else {}
            if not r.get("questions") or not isinstance(r.get("rules"), list):
                v.append(f"V6 jev {e['id']}: rubric lacks questions or rules")
        except (OSError, ValueError):
            v.append(f"V6 jev {e['id']}: rubric does not load")
        for kind in e.get("kinds", []):
            if kinds_map.get(kind) != e["id"]:
                v.append(f"V6 jev {e['id']}: kind {kind!r} is not mapped to it in work-criteria.json")
        for kind in e.get("kinds_proposed", []):
            if kinds_map.get(kind) != e["id"]:
                msg = f"kind {kind!r} proposed, not yet mapped in work-criteria.json"
                (v.append(f"V6 jev {e['id']}: {msg}") if strict else pending.append(f"PENDING jev {e['id']}: {msg}"))

    for e in [tiers["hooks"]["meta"], *tiers["hooks"]["main"], *tiers["hooks"]["sub"]]:
        if not e.get("new"):
            continue
        p = resolve(e.get("path"))
        if p is None or not p.is_file() or not os.access(p, os.X_OK):
            v.append(f"V7 hooks {e['id']}: missing or not executable")
        cases = REPO / "capabilities/hooks/fixtures" / e["id"] / "cases.json"
        try:
            if not json.loads(cases.read_text()):
                v.append(f"V7 hooks {e['id']}: fixture cases empty")
        except (OSError, ValueError):
            v.append(f"V7 hooks {e['id']}: fixture cases missing")

    for name in (m.get("lessons"), m.get("inventory")):
        p = SKILL / (name or "")
        if not name or not p.is_file() or p.stat().st_size == 0:
            v.append(f"V8 family {name}: missing or empty")
    cand_rows = m.get("_candidate_rows")
    if cand_rows is None and m.get("lessons_candidates"):
        cp = SKILL / m["lessons_candidates"]
        try:
            cand_rows = [json.loads(ln) for ln in cp.read_text().splitlines() if ln.strip()]
        except (OSError, ValueError) as e:
            v.append(f"V8 family {m['lessons_candidates']}: unreadable ({e})")
            cand_rows = []
    for i, row in enumerate(cand_rows or [], 1):
        miss = [f for f in CAND_FIELDS if not row.get(f)]
        if miss or row.get("status") != "candidate":
            v.append(f"V8 candidates row {i} {row.get('lesson_id')}: missing {miss or '-'} or status {row.get('status')!r} is not 'candidate'")
            continue
        try:
            re.compile(row["trigger"])
        except re.error as e:
            v.append(f"V8 candidates {row['lesson_id']}: trigger does not compile ({e})")

    limit = int(m.get("head_bytes", 4096))
    for e in [sk["meta"], *sk["sub"], *sk["main"]]:
        if not e.get("new") or not exists("skills", e):
            continue
        b = text_of(e).encode()
        end = b.find(b"\n---", 4)
        size = end + 4 if b.startswith(b"---") and end > 0 else len(b)
        if size > limit:
            v.append(f"V9 skills {e['id']}: frontmatter {size} bytes exceeds {limit}")

    conductor = text_of(tiers["agents"]["meta"])
    for e in [*sk["main"], *sk["sub"]]:
        if (e["id"].startswith("agentic-setup-") or e in sk["sub"]) and e["id"] not in conductor:
            v.append(f"V10 agents {tiers['agents']['meta']['id']}: does not route {e['id']}")
    return v, pending


def plant(m: dict, name: str) -> dict:
    m = copy.deepcopy(m)
    t = m["tiers"]
    if name == "bad_path":
        t["skills"]["sub"][0]["path"] = "capabilities/skills/agentic-does-not-exist"
    elif name == "orphan_sub":
        t["agents"]["sub"][-1]["parent"] = "no-such-parent"
    elif name == "unwired_sub":
        probe = dict(t["skills"]["sub"][0])
        probe["id"] = "agentic-unwired-probe"
        t["skills"]["sub"].append(probe)
    elif name == "stage_gap":
        t["skills"]["sub"] = [e for e in t["skills"]["sub"] if not covers(e, "secrets")]
    elif name == "lane_gap":
        t["skills"]["main"] = [e for e in t["skills"]["main"] if e.get("lane") != "data-pipeline"]
    elif name == "kind_unregistered":
        t["jev"]["meta"]["kinds"] = list(t["jev"]["meta"].get("kinds", [])) + ["agentic-unregistered-probe"]
    elif name == "fat_frontmatter":
        m["head_bytes"] = 200
    elif name == "bad_candidate":
        m["_candidate_rows"] = [{"lesson_id": "AS-99-probe", "trigger": "(unclosed", "match": "regex",
                                 "mandated_check": "x", "evidence": ["x"], "status": "active"}]
    elif name == "unrouted_framework":
        probe = dict(next(e for e in t["skills"]["main"] if e["id"].startswith("agentic-setup-")))
        probe["id"] = "agentic-setup-unrouted-probe"
        t["skills"]["main"].append(probe)
    return m


def digest(m: dict) -> str:
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:12]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(SKILL / "hierarchy.json"))
    ap.add_argument("--strict", action="store_true", help="expected-but-missing entries and proposed kinds become violations")
    ap.add_argument("--plant", choices=sorted(PLANTS))
    a = ap.parse_args(argv)
    try:
        m = json.loads(Path(a.manifest).read_text())
    except (OSError, ValueError) as e:
        print(f"usage: manifest unreadable: {e}", file=sys.stderr)
        return 1
    if a.plant:
        planted = plant(m, a.plant)
        before, after = digest(m), digest(planted)
        if before == after:
            print(f"PLANT {a.plant}: bytes did not move ({before}); refusing to report", file=sys.stderr)
            return 0
        want = PLANTS[a.plant]
        hits = [x for x in check(planted, a.strict)[0] if x.startswith(want + " ")]
        print(f"PLANT {a.plant}: manifest {before} -> {after}; expected {want}: {'CAUGHT' if hits else 'ESCAPED'}")
        for h in hits[:3]:
            print("  " + h)
        return 2 if hits else 0
    viol, pending = check(m, a.strict)
    for x in viol:
        print(x)
    for x in pending:
        print(x)
    counts = {k: f"1/{len(m['tiers'][k]['main'])}/{len(m['tiers'][k]['sub'])}" for k in KINDS if k in m.get("tiers", {})}
    mode = "strict" if a.strict else "lenient"
    print(f"agentic-systems-setup hierarchy ({mode}): {len(viol)} violation(s); {len(pending)} pending; meta/main/sub {counts}")
    return 2 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
