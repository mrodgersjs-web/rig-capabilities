#!/usr/bin/env python3
"""Validate the App Studio org chart (hierarchy.json) against what is on disk.

Checks (each violation prints as "V<n> <kind> <id>: <why>"):
  V1  manifest shape: six kinds, one meta each, main and sub lists present
  V2  every path resolves; a skill path is a directory holding SKILL.md
  V3  every sub names a parent in the same kind; parent chains reach the meta or a
      main entry without cycles (no orphans)
  V4  every sub is wired in text: its parent's file names it (JEV subs: the family's
      meta skill or its JEV decision map names it) - a listed-but-unreferenced child is
      the orphan the 2026-09-27 audit found
  V5  every stage has at least one sub-skill and one main skill
  V6  every JEV rubric loads with questions and rules, and every kind an entry claims
      maps to it in work-criteria.json
  V7  every new hook is executable and has fixture cases
  V8  the lesson ledger and the inventory exist and are non-empty
  V10 engine: the studio:mission script runs the meta file, which handles every declared command
      and imports each main module; every also_wired_in site imports its module; each declared bin
      exists; each declared commit exists in its repo (the testlab merge is a real commit)
  V9  prompts: every app-studio-*/app-sub-* prompt in the library registry or on disk is in the
      hierarchy (no orphan prompt); registry, frontmatter and hierarchy agree on path, tier and
      parent; each body still hashes to its content_sha256; the meta prompt names every main
      prompt; each sub is listed as owned by exactly one main prompt, its parent; every LA, TG
      BENCH and CH-<CODE>-NN id a prompt cites resolves (LA in the ledger; TG, BENCH and CH rows
      in references/prompts.md; a CH row must name an existing youtube-<slug> lessons.jsonl line);
      each LA lesson a prompt carries matches the ledger's current mandated_check (no stale doctrine)

Usage:
  validate_hierarchy.py [--manifest PATH] [--plant NAME]
Plants mutate an in-memory copy and exit 2 when the named violation is CAUGHT and 0 when
it ESCAPED, so a done_when of `...; test $? -eq 2` goes red on a blind validator:
  bad_path -> V2, orphan_sub -> V3, unwired_sub -> V4, stage_gap -> V5, kind_unregistered -> V6,
  prompt_orphan -> V9, engine_path_missing -> V2, engine_commit_missing -> V10
Exit 0 clean, 2 violation(s) (or plant caught), 1 usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[2]
KINDS = ("skills", "agents", "harnesses", "loops", "hooks", "jev", "prompts", "engine")
WORK = REPO / "capabilities/harnesses/s1gate/work-criteria.json"
PLANTS = {"bad_path": "V2", "orphan_sub": "V3", "unwired_sub": "V4", "stage_gap": "V5", "kind_unregistered": "V6",
          "prompt_orphan": "V9", "engine_path_missing": "V2", "engine_commit_missing": "V10"}
REFS = SKILL / "references"   # lessons.jsonl and prompts.md; a module global so tests can point it at a copy
CH_ROOT = REPO                # root that CH rows' source lessons resolve against
LESSON_ID = re.compile(r"\b((?:LA|TG|BENCH)-\d{2}|CH-[A-Z]{3}-\d{2,3})\b")
CH_SOURCE = re.compile(r"(capabilities/skills/youtube-[a-z0-9-]+/references/lessons\.jsonl)#([A-Za-z0-9_.:-]+)")
PROMPT_LIB = REPO / "capabilities/prompts"
PROMPT_PREFIXES = ("app-studio-", "app-sub-")


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


def check(m: dict) -> list[str]:
    v: list[str] = []
    tiers = m.get("tiers") or {}
    for k in KINDS:
        t = tiers.get(k)
        if not isinstance(t, dict) or not isinstance(t.get("meta"), dict) or not isinstance(t.get("main"), list) or not isinstance(t.get("sub"), list):
            v.append(f"V1 {k} -: tier missing meta, main, or sub")
    if v:
        return v

    for k in KINDS:
        t = tiers[k]
        for e in [t["meta"], *t["main"], *t["sub"]]:
            p = resolve(e.get("path"))
            ok = p is not None and (p / "SKILL.md").is_file() if (k == "skills" or (p is not None and p.is_dir())) else (p is not None and p.is_file())
            if not ok:
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

    meta_docs = (SKILL / "SKILL.md").read_text(errors="ignore") if (SKILL / "SKILL.md").is_file() else ""
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

    stages = [s["id"] for s in m.get("stages", [])]
    sk = tiers["skills"]
    for s in stages:
        if not any(e.get("stage") == s for e in sk["sub"]):
            v.append(f"V5 skills {s}: stage has no sub-skill")
        if not any(e.get("stage") == s for e in sk["main"]):
            v.append(f"V5 skills {s}: stage has no main skill")

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
            v.append(f"V7 hooks {e['id']}: fixture cases missing at {cases.relative_to(REPO)}")

    for name in (m.get("lessons"), m.get("inventory")):
        p = SKILL / (name or "")
        if not name or not p.is_file() or p.stat().st_size == 0:
            v.append(f"V8 family {name}: missing or empty")
    v.extend(check_prompts(m))
    v.extend(check_engine(m))
    return v


def split_prompt(text: str) -> tuple[dict, str]:
    """Frontmatter keys and the body content_sha256 covers (the separator newline is not body)."""
    meta: dict = {}
    if text.startswith("---\n") and "\n---\n" in text:
        head, body = text[4:].split("\n---\n", 1)
        for line in head.split("\n"):
            if ":" in line:
                k, val = line.split(":", 1)
                meta[k.strip()] = val.strip()
        return meta, body[1:] if body.startswith("\n") else body
    return meta, text


def check_prompts(m: dict) -> list[str]:
    v: list[str] = []
    t = m["tiers"]["prompts"]
    try:
        reg = json.loads((PROMPT_LIB / "registry.json").read_text())["prompts"]
    except (OSError, ValueError, KeyError):
        return ["V9 prompts registry: capabilities/prompts/registry.json unreadable"]
    fam = {p["id"]: p for p in reg if p["id"].startswith(PROMPT_PREFIXES)}
    disk = {d.name for d in (PROMPT_LIB / "prompts").iterdir() if d.is_dir() and d.name.startswith(PROMPT_PREFIXES)}
    meta_id = t["meta"]["id"]
    tiered = {meta_id: ("meta", t["meta"]), **{e["id"]: ("main", e) for e in t["main"]}, **{e["id"]: ("sub", e) for e in t["sub"]}}
    for pid in sorted((set(fam) | disk) - set(tiered)):
        v.append(f"V9 prompts {pid}: in the prompt library but not in the hierarchy (orphan prompt)")
    texts: dict[str, str] = {}
    for pid, (tier, e) in tiered.items():
        r = fam.get(pid)
        if r is None:
            v.append(f"V9 prompts {pid}: in the hierarchy but not in registry.json")
            continue
        if "capabilities/prompts/" + r.get("path", "") != e.get("path"):
            v.append(f"V9 prompts {pid}: registry path {r.get('path')} disagrees with hierarchy {e.get('path')}")
        want_parent = "none" if tier == "meta" else e.get("parent")
        if r.get("tier") != tier or r.get("parent") != want_parent:
            v.append(f"V9 prompts {pid}: registry tier/parent {r.get('tier')}/{r.get('parent')} != hierarchy {tier}/{want_parent}")
        try:  # read through the library root the registry names, so registry and body share one source
            text = (PROMPT_LIB / r.get("path", "")).read_text()
        except OSError:
            text = ""
            v.append(f"V9 prompts {pid}: prompt file unreadable at {r.get('path')}")
        fm, body = split_prompt(text)
        texts[pid] = body
        if fm.get("tier") != tier or fm.get("parent") != want_parent:
            v.append(f"V9 prompts {pid}: frontmatter tier/parent {fm.get('tier')}/{fm.get('parent')} != hierarchy {tier}/{want_parent}")
        if hashlib.sha256(body.encode()).hexdigest() != fm.get("content_sha256") or fm.get("content_sha256") != r.get("content_sha256"):
            v.append(f"V9 prompts {pid}: body no longer hashes to content_sha256 (edited in place; file a new version)")
    line_of = lambda body, key: next((ln for ln in body.split("\n") if ln.startswith(key)), "")
    mains_line = line_of(texts.get(meta_id, ""), "- main prompts:")
    owned: dict[str, list[str]] = {}
    for e in t["main"]:
        if e["id"] not in [x.strip() for x in mains_line.split(":", 1)[-1].split(",")]:
            v.append(f"V9 prompts {e['id']}: the meta prompt's main prompts line does not name it")
        for s in line_of(texts.get(e["id"], ""), "- sub-prompts owned:").split(":", 1)[-1].split(","):
            if s.strip():
                owned.setdefault(s.strip(), []).append(e["id"])
    for e in t["sub"]:
        if owned.get(e["id"], []) != [e.get("parent")]:
            v.append(f"V9 prompts {e['id']}: owned by {owned.get(e['id'], [])}, parent {e.get('parent')} (must be exactly its parent)")
    la, la_text = set(), {}
    try:
        for ln in (REFS / "lessons.jsonl").read_text().splitlines():
            if ln.strip():
                row = json.loads(ln)
                la.add(row["lesson_id"][:5])
                s = row.get("mandated_check", "")
                la_text[row["lesson_id"][:5]] = (s[:1].upper() + s[1:] + ("" if s.endswith(".") else ".")) if s else ""
    except (OSError, ValueError, KeyError):
        v.append("V9 prompts lessons.jsonl: unreadable")
    try:
        ref = (REFS / "prompts.md").read_text()
    except OSError:
        ref = ""
        v.append("V9 prompts references/prompts.md: missing (TG and BENCH lesson tables)")
    known = la | set(re.findall(r"^\| ((?:TG|BENCH)-\d{2}) \|", ref, re.M))
    for row in re.findall(r"^\| (CH-[A-Z]{3}-\d{2,3}) \|(.*)$", ref, re.M):
        src = CH_SOURCE.search(row[1])
        if not src:
            v.append(f"V9 prompts {row[0]}: channel row names no source lesson (youtube-<slug>/references/lessons.jsonl#<lesson_id>)")
            continue
        try:
            ids = {json.loads(ln).get("lesson_id") for ln in (CH_ROOT / src.group(1)).read_text().splitlines() if ln.strip()}
        except (OSError, ValueError):
            ids = set()
        if src.group(2) not in ids:
            v.append(f"V9 prompts {row[0]}: source lesson {src.group(2)} not found in {src.group(1)}")
            continue
        known.add(row[0])
    for pid, body in texts.items():
        for lid in sorted(set(LESSON_ID.findall(body)) - known):
            v.append(f"V9 prompts {pid}: cites unknown lesson id {lid}")
        for lid, carried in re.findall(r"^  - (LA-\d{2}): (.*)$", body, re.M):
            if lid in la_text and carried != la_text[lid]:
                v.append(f"V9 prompts {pid}: carries stale text for {lid} (the ledger changed; file a new version)")
    return v


def check_engine(m: dict) -> list[str]:
    v: list[str] = []
    t = m["tiers"]["engine"]
    meta = t["meta"]
    mt = text_of("engine", meta)
    try:
        scripts = json.loads(resolve(meta.get("package")).read_text()).get("scripts", {})
    except (OSError, ValueError, AttributeError):
        scripts = {}
        v.append(f"V10 engine {meta['id']}: package.json unreadable at {meta.get('package')}")
    if Path(meta["path"]).name not in scripts.get(meta.get("script", ""), ""):
        v.append(f"V10 engine {meta['id']}: script {meta.get('script')!r} does not run {Path(meta['path']).name}")
    for c in meta.get("commands", []):
        if f'"{c}"' not in mt:
            v.append(f"V10 engine {meta['id']}: command {c!r} is not handled in {Path(meta['path']).name}")
    ids = {x["id"]: x for x in [meta, *t["main"], *t["sub"]]}
    for e in t["main"]:
        if e.get("wire") and e["wire"] not in mt:
            v.append(f"V10 engine {e['id']}: the meta file does not import it ({e['wire']})")
    for e in [*t["main"], *t["sub"]]:
        for other in e.get("also_wired_in", []):
            if other not in ids or e.get("wire", "") not in text_of("engine", ids[other]):
                v.append(f"V10 engine {e['id']}: declared use in {other} not found ({e.get('wire')})")
        if e.get("bin"):
            b = resolve(e["bin"])
            if b is None or not b.is_file():
                v.append(f"V10 engine {e['id']}: built entry point missing at {e['bin']}")
        if e.get("commit"):
            repo = resolve(e.get("repo"))
            r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", e["commit"] + "^{commit}"], capture_output=True)
            if r.returncode != 0:
                v.append(f"V10 engine {e['id']}: commit {e['commit']} not found in {e.get('repo')}")
    return v


def plant(m: dict, name: str) -> dict:
    m = copy.deepcopy(m)
    t = m["tiers"]
    if name == "bad_path":
        t["skills"]["sub"][0]["path"] = "capabilities/skills/app-does-not-exist"
    elif name == "orphan_sub":
        t["agents"]["sub"][-1]["parent"] = "no-such-parent"
    elif name == "unwired_sub":
        probe = dict(t["skills"]["sub"][0])
        probe["id"] = "app-unwired-probe"
        t["skills"]["sub"].append(probe)
    elif name == "stage_gap":
        t["skills"]["sub"] = [e for e in t["skills"]["sub"] if e.get("stage") != "mobile"]
    elif name == "engine_path_missing":
        t["engine"]["sub"][-1]["path"] = t["engine"]["sub"][-1]["path"] + ".missing"
    elif name == "engine_commit_missing":
        next(e for e in t["engine"]["sub"] if e.get("commit"))["commit"] = "0000000"
    elif name == "prompt_orphan":
        t["prompts"]["sub"] = t["prompts"]["sub"][:-1]  # the library still holds it: an orphan prompt
    elif name == "kind_unregistered":
        t["jev"]["sub"][0]["kinds"] = list(t["jev"]["sub"][0].get("kinds", [])) + ["app-unregistered-probe"]
    return m


def digest(m: dict) -> str:
    return hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()[:12]


def main(argv: list[str]) -> int:
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
    archived = [e for k in KINDS if k in m.get("tiers", {}) for t in ("main", "sub") for e in m["tiers"][k][t] if e.get("archived")]
    for e in archived:
        print(f"ARCHIVED {e['id']}: {e.get('archived_from')} was archived; the family still depends on it (restore it or drop it from the extends/inventory)")
    counts = {k: f"1/{len(m['tiers'][k]['main'])}/{len(m['tiers'][k]['sub'])}" for k in KINDS if k in m.get("tiers", {})}
    print(f"app-studio hierarchy: {len(viol)} violation(s), {len(archived)} archived dependenc{'y' if len(archived) == 1 else 'ies'}; meta/main/sub {counts}")
    return 2 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
