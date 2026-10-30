#!/usr/bin/env python3
"""Validate the Traject OS org chart (hierarchy.json) against what is on disk.

Checks (each violation prints as "V<n> <kind> <id>: <why>"):
  V1  manifest shape: six kinds, one meta each, main and sub lists present
  V2  every path resolves; a skill path is a directory holding SKILL.md
  V3  every sub names a parent in the same kind; parent chains reach the meta or a
      main entry without cycles (no orphans)
  V4  every sub is wired in text: its parent's file names it (JEV subs: the family's
      meta skill or its JEV decision map names it) - a listed-but-unreferenced child is
      an orphan
  V5  every stage is covered by at least one sub-skill and one main skill
  V6  every JEV rubric loads with questions and rules, and every kind an entry claims
      maps to it in work-criteria.json
  V7  every NEW hook is executable and has fixture cases (reused hooks are skipped)
  V8  the lesson ledger exists and is non-empty

Usage:
  validate_hierarchy.py [--manifest PATH] [--plant NAME]
Plants mutate an in-memory copy and exit 2 when the named violation is CAUGHT and 0 when
it ESCAPED, so a done_when of `...; test $? -eq 2` goes red on a blind validator:
  bad_path -> V2, orphan_sub -> V3, unwired_sub -> V4, stage_gap -> V5, kind_unregistered -> V6
Exit 0 clean, 2 violation(s) (or plant caught), 1 usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[2]
KINDS = ("skills", "agents", "harnesses", "loops", "hooks", "jev")
WORK = REPO / "capabilities/harnesses/s1gate/work-criteria.json"
PLANTS = {"bad_path": "V2", "orphan_sub": "V3", "unwired_sub": "V4", "stage_gap": "V5",
          "kind_unregistered": "V6"}


def resolve(p: str | None) -> Path | None:
    if not p:
        return None
    if p.startswith("~/"):
        return Path.home() / p[2:]
    return Path(p) if p.startswith("/") else REPO / p


def text_of(kind: str, e: dict) -> str:
    p = resolve(e.get("path"))
    if p is None:
        return ""
    if p.is_dir():
        p = p / "SKILL.md"
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def covers_of(e: dict) -> set:
    return set(e.get("covers") or []) | ({e["stage"]} if e.get("stage") else set())


def check(m: dict) -> list:
    v: list = []
    tiers = m.get("tiers") or {}
    for k in KINDS:
        t = tiers.get(k)
        if not isinstance(t, dict) or not isinstance(t.get("meta"), dict) \
                or not isinstance(t.get("main"), list) or not isinstance(t.get("sub"), list):
            v.append(f"V1 {k} -: tier missing meta, main, or sub")
    if v:
        return v

    # V2 paths
    for k in KINDS:
        t = tiers[k]
        for e in [t["meta"], *t["main"], *t["sub"]]:
            p = resolve(e.get("path"))
            if p is None:
                v.append(f"V2 {k} {e.get('id')}: path does not resolve: {e.get('path')}")
            elif p.is_dir():
                if not (p / "SKILL.md").is_file():
                    v.append(f"V2 {k} {e.get('id')}: directory has no SKILL.md: {e.get('path')}")
            elif k == "skills":
                v.append(f"V2 {k} {e.get('id')}: not a skill directory with SKILL.md: {e.get('path')}")
            elif not p.is_file():
                v.append(f"V2 {k} {e.get('id')}: path does not resolve: {e.get('path')}")

    # V3 parent chains
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

    # V4 wiring
    meta_docs = ""
    if (SKILL / "SKILL.md").is_file():
        meta_docs = (SKILL / "SKILL.md").read_text(errors="ignore")
    jev_map = SKILL / "references" / "jev-decisions.md"
    meta_docs += jev_map.read_text(errors="ignore") if jev_map.is_file() else ""
    for k in KINDS:
        t = tiers[k]
        ids = {t["meta"]["id"]: t["meta"], **{e["id"]: e for e in t["main"]}, **{e["id"]: e for e in t["sub"]}}
        for e in t["sub"]:
            par = ids.get(e.get("parent"))
            if par is None:
                continue
            hay = meta_docs if k == "jev" else text_of(k, par)
            if (e.get("wire") or e["id"]) not in hay:
                v.append(f"V4 {k} {e['id']}: not named in its parent {par['id']}'s file")

    # V5 stage coverage
    stages = [s["id"] for s in m.get("stages", [])]
    sk = tiers["skills"]
    sub_cov = set().union(*[covers_of(e) for e in sk["sub"]]) if sk["sub"] else set()
    main_cov = set().union(*[covers_of(e) for e in sk["main"]]) if sk["main"] else set()
    for s in stages:
        if s not in sub_cov:
            v.append(f"V5 skills {s}: stage has no sub-skill")
        if s not in main_cov:
            v.append(f"V5 skills {s}: stage has no main skill")

    # V6 jev rubrics and kinds
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

    # V7 new hooks
    for e in [tiers["hooks"]["meta"], *tiers["hooks"]["sub"]]:
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
            v.append(f"V7 hooks {e['id']}: fixture cases missing at capabilities/hooks/fixtures/{e['id']}/cases.json")

    # V8 lesson ledger
    for name in (m.get("lessons"),):
        p = SKILL / (name or "")
        if not name or not p.is_file() or p.stat().st_size == 0:
            v.append(f"V8 family {name}: missing or empty")
    return v


def plant(m: dict, name: str) -> dict:
    m = copy.deepcopy(m)
    t = m["tiers"]
    if name == "bad_path":
        t["skills"]["sub"][0]["path"] = "capabilities/skills/traject-does-not-exist"
    elif name == "orphan_sub":
        t["agents"]["sub"][-1]["parent"] = "no-such-parent"
    elif name == "unwired_sub":
        probe = dict(t["skills"]["sub"][0])
        probe["id"] = "traject-unwired-probe"
        probe["parent"] = "traject-os"
        t["skills"]["sub"].append(probe)
    elif name == "stage_gap":
        t["skills"]["main"] = [e for e in t["skills"]["main"] if "interview-day" not in covers_of(e)]
    elif name == "kind_unregistered":
        t["jev"]["sub"][0]["kinds"] = list(t["jev"]["sub"][0].get("kinds", [])) + ["traject-unregistered-probe"]
    return m


def digest(m: dict) -> str:
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:12]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(SKILL / "hierarchy.json"))
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
        hits = [x for x in check(planted) if x.startswith(want + " ")]
        print(f"PLANT {a.plant}: manifest {before} -> {after}; expected {want}: {'CAUGHT' if hits else 'ESCAPED'}")
        for h in hits[:3]:
            print("  " + h)
        return 2 if hits else 0
    viol = check(m)
    for x in viol:
        print(x)
    counts = {k: f"1/{len(m['tiers'][k]['main'])}/{len(m['tiers'][k]['sub'])}" for k in KINDS if k in m.get("tiers", {})}
    print(f"traject-os hierarchy: {len(viol)} violation(s); meta/main/sub {counts}")
    return 2 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
