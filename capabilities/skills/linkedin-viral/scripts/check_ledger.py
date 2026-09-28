#!/usr/bin/env python3
"""Done-test for linkedin-viral stage skills (lv-*).

GREEN only when, for the stage folder given:
  1. SKILL.md frontmatter `name` equals the folder name, the description carries
     the JEV-FIRST MANDATE, and the body opens with a `## JEV-first mandate` section;
  2. references/ holds at least 3 sub-skills of 400+ bytes, plus ledger.md;
  3. ledger.md has a row for EVERY asset the stage map assigns to this stage
     (roles merge, tool, runner), and each row names an action
     (merged / tool / runner / dropped);
  4. every backticked ~/ or /Users path in the skill resolves on disk;
  5. no sub-skill shares a 12-word run with a third-party merge source.
Exit 0 GREEN, 2 RED.

Usage: check_ledger.py <stage_dir> | --all | --self-test <stage_dir>
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

LV = pathlib.Path(__file__).resolve().parent.parent
MAP = LV / "references" / "stage-map.json"
SKILLS = LV.parent


def words(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def check(stage_dir):
    d = pathlib.Path(stage_dir).resolve()
    stage, errs = d.name, []
    rows = [r for r in json.load(open(MAP)) if r.get("stage") == stage and r.get("role") in ("merge", "tool", "runner")]
    sk = d / "SKILL.md"
    if not sk.exists():
        return ["missing SKILL.md"], len(rows)
    t = sk.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if not m:
        errs.append("no frontmatter")
    else:
        fm, body = m.group(1), m.group(2)
        if not re.search(r"^name:\s*" + re.escape(stage) + r"\s*$", fm, re.M):
            errs.append("frontmatter name != folder name")
        if "JEV-FIRST MANDATE" not in fm:
            errs.append("description lacks JEV-FIRST MANDATE")
        if not re.search(r"^## JEV-first mandate", body[:2500], re.M):
            errs.append("body does not open with a '## JEV-first mandate' section")
    refs = d / "references"
    subs = sorted(p for p in refs.glob("*.md") if p.name != "ledger.md") if refs.is_dir() else []
    if len(subs) < 3:
        errs.append(f"only {len(subs)} sub-skills (need >= 3)")
    small = [p.name for p in subs if p.stat().st_size < 400]
    if small:
        errs.append(f"sub-skills under 400 bytes: {small}")
    led = refs / "ledger.md"
    if not led.exists():
        errs.append("missing references/ledger.md")
    else:
        lines = [l for l in led.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
        for r in rows:
            pat = re.compile(r"\|\s*`?" + re.escape(r["id"]) + r"`?\s*\|")
            hit = [l for l in lines if pat.search(l)]
            if not hit:
                errs.append(f"ledger missing row for {r['id']}")
            elif not re.search(r"\b(merged|tool|runner|dropped)\b", hit[0], re.I):
                errs.append(f"ledger row for {r['id']} names no action")
    for f in [sk] + subs + ([led] if led.exists() else []):
        for p in re.findall(r"`((?:~|/Users)/[^`\s]+)`", f.read_text(encoding="utf-8")):
            if not os.path.exists(os.path.expanduser(p)):
                errs.append(f"dangling path in {f.name}: {p}")
    tp = [r for r in rows if r.get("third_party")]
    if tp:
        mine = set()
        for f in [sk] + subs:
            w = words(f.read_text(encoding="utf-8"))
            mine |= {" ".join(w[i:i + 12]) for i in range(len(w) - 11)}
        for r in tp:
            src = os.path.expanduser(r.get("read_from") or r["path"])
            if os.path.isfile(src):
                w = words(open(src, encoding="utf-8", errors="ignore").read())
                if any(" ".join(w[i:i + 12]) in mine for i in range(len(w) - 11)):
                    errs.append(f"12-word run copied from third-party source {r['id']}")
    return errs, len(rows)


def report(stage_dir):
    errs, n = check(stage_dir)
    name = pathlib.Path(stage_dir).resolve().name
    print(f"{name}: expected_ledger_rows={n} errors={len(errs)}")
    for e in errs:
        print(f"  RED {e}")
    return not errs


args = sys.argv[1:]
if args[:1] == ["--self-test"]:
    real = pathlib.Path(args[1]).resolve()
    rows = [r for r in json.load(open(MAP)) if r.get("stage") == real.name and r.get("role") in ("merge", "tool", "runner")]
    with tempfile.TemporaryDirectory() as td:
        copy = pathlib.Path(td) / real.name
        shutil.copytree(real, copy)
        led = copy / "references" / "ledger.md"
        victim = rows[0]["id"]
        kept = [l for l in led.read_text(encoding="utf-8").splitlines()
                if not re.search(r"\|\s*`?" + re.escape(victim) + r"`?\s*\|", l)]
        led.write_text("\n".join(kept) + "\n", encoding="utf-8")
        planted_errs, _ = check(copy)
    real_errs, _ = check(real)
    ok = bool(planted_errs) and not real_errs
    print(f"self-test planted_missing_row={'RED' if planted_errs else 'GREEN(!)'} real={'GREEN' if not real_errs else 'RED'}")
    print("GREEN" if ok else "RED")
    sys.exit(0 if ok else 2)
if args[:1] == ["--all"]:
    dirs = sorted(p for p in SKILLS.glob("lv-*") if p.is_dir() and not p.name.startswith("lv-creator-"))
    oks = [report(p) for p in dirs]
    print(f"stages={len(dirs)} green={sum(oks)}")
    print("GREEN" if dirs and all(oks) else "RED")
    sys.exit(0 if dirs and all(oks) else 2)
ok = report(args[0])
print("GREEN" if ok else "RED")
sys.exit(0 if ok else 2)
