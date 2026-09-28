#!/usr/bin/env python3
"""Structural + no-verbatim gate for the Google Ads family.

For each directory checked:
  - SKILL.md exists, its body opens (first H2) with "## JEV-first mandate" (ga-* stages);
  - every `references/<file>.md` the SKILL.md names exists and is >= 400 bytes;
  - no run of 12 consecutive words from any corpus transcript appears in the directory's files
    (skills paraphrase and cite; transcript text stays in the local corpus).

usage: check_family.py [DIR ...]   default: every ga-* stage plus google-ads-os and google-ads-doctrine
       check_family.py --self-test   plant a copied 12-word run and a missing sub-skill in a temp copy;
                                     exit 0 only if both go RED and the real family stays GREEN
exit:  0 clean | 2 findings"""
import json, re, shutil, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SK = REPO / "capabilities/skills"
CORP = REPO / "data/corpora/google-ads"
N = 12
WORD = re.compile(r"[a-z0-9']+")


def words(t):
    return WORD.findall(t.lower().replace("\u2019", "'"))


def grams(ws):
    return {" ".join(ws[i:i + N]) for i in range(len(ws) - N + 1)}


def stage_dirs(names):
    if names:
        return [SK / n for n in names]
    return sorted([p for p in SK.glob("ga-*") if p.is_dir()]
                  + [SK / "google-ads-os", SK / "google-ads-doctrine"])


def check(dirs):
    findings = []
    skill_grams = {}
    for d in dirs:
        sk = d / "SKILL.md"
        if not sk.exists():
            findings.append(f"{d.name}: SKILL.md missing")
            continue
        text = sk.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1]
        first_h2 = next((l for l in body.splitlines() if l.startswith("## ")), "")
        if d.name.startswith("ga-") and not first_h2.startswith("## JEV-first mandate"):
            findings.append(f"{d.name}: body does not open with the JEV-first section (first H2: {first_h2!r})")
        for ref in set(re.findall(r"`references/([\w.-]+\.md)`", text)):
            p = d / "references" / ref
            if not p.exists():
                findings.append(f"{d.name}: sub-skill references/{ref} missing")
            elif p.stat().st_size < 400:
                findings.append(f"{d.name}: sub-skill references/{ref} under 400 bytes")
        for f in [sk] + sorted((d / "references").glob("*.md")):
            for g in grams(words(f.read_text(encoding="utf-8"))):
                skill_grams.setdefault(g, f)
    copied = {}
    for line in (CORP / "manifest.jsonl").open():
        if not line.strip():
            continue
        r = json.loads(line)
        ws = words((REPO / r["file"]).read_text(encoding="utf-8"))
        for i in range(len(ws) - N + 1):
            g = " ".join(ws[i:i + N])
            if g in skill_grams and g not in copied:
                copied[g] = (skill_grams[g], r["video_id"])
    for g, (f, vid) in copied.items():
        findings.append(f"verbatim 12-word run from {vid} in {f.relative_to(REPO) if f.is_relative_to(REPO) else f}: \"{g}\"")
    return findings


def self_test():
    real = check(stage_dirs([]))
    tmp = Path(tempfile.mkdtemp())
    try:
        src = SK / "ga-strategy"
        dst = tmp / "ga-strategy"
        shutil.copytree(src, dst)
        # plant 1: a 12-word run copied from a real transcript
        r = json.loads(next(l for l in (CORP / "manifest.jsonl").open() if l.strip()))
        ws = words((REPO / r["file"]).read_text(encoding="utf-8"))
        (dst / "SKILL.md").write_text((dst / "SKILL.md").read_text() + "\nPlanted: " + " ".join(ws[200:214]) + "\n")
        # plant 2: a named sub-skill that does not exist
        (dst / "SKILL.md").write_text((dst / "SKILL.md").read_text() + "\n| `references/planted-missing.md` | x |\n")
        planted = check([dst])
        red_copy = any("verbatim" in f for f in planted)
        red_missing = any("planted-missing.md missing" in f for f in planted)
        ok = red_copy and red_missing and not real
        print(json.dumps({"real_family_green": not real, "plant_verbatim_red": red_copy, "plant_missing_subskill_red": red_missing, "pass": ok}))
        return 0 if ok else 2
    finally:
        shutil.rmtree(tmp)


def main(argv):
    if argv and argv[0] == "--self-test":
        return self_test()
    dirs = stage_dirs(argv)
    f = check(dirs)
    print(json.dumps({"stages": [d.name for d in dirs], "findings": f}, indent=1))
    return 2 if f else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
