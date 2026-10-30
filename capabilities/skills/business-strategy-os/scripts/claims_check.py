#!/usr/bin/env python3
"""Every CLAIM(<videoId>[, <videoId>...]) in the business-strategy family must resolve to a transcript
in data/corpora/strategy/manifest.jsonl (the independent registry). Stdlib only, read-only.

usage: claims_check.py [FILE ...]      default: the whole family (business-strategy-os, strategy-*, agents/strategy-*)
       claims_check.py --plant         prove the gate goes RED on a planted bogus id (exit 0 only if it does)
exit:  0 all resolve | 1 usage/registry missing | 2 unresolved or missing citations"""
import glob, json, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / "data/corpora/strategy/manifest.jsonl"
PAT = re.compile(r"CLAIM\(([^)]*)\)")
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
def registry():
    if not MANIFEST.exists():
        print(f"registry missing: {MANIFEST}", file=sys.stderr); sys.exit(1)
    return {json.loads(l)["video_id"] for l in MANIFEST.open() if l.strip()}
def family():
    """Every text file the family asserts doctrine in, exemplars included.

    An exemplar is a claim about what good looks like; a fabricated citation inside one is
    the same defect as one in a SKILL.md, so the reference files are inside the gate.
    """
    fs = [REPO / "capabilities/skills/business-strategy-os/SKILL.md"]
    fs += sorted(Path(p) for p in glob.glob(str(REPO / "capabilities/skills/business-strategy-os/references/**/*.md"), recursive=True))
    fs += sorted(Path(p) for p in glob.glob(str(REPO / "capabilities/skills/strategy-*/SKILL.md")))
    fs += sorted(Path(p) for p in glob.glob(str(REPO / "capabilities/skills/strategy-*/references/**/*.md"), recursive=True))
    fs += sorted(Path(p) for p in glob.glob(str(REPO / "capabilities/agents/strategy-*.md")))
    fs += sorted(Path(p) for p in glob.glob(str(REPO / "examples/great/business-ops/great-strategy-*.md")))
    return [f for f in fs if f.exists()]
def check(files, reg):
    total, bad, empty = 0, [], []
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        for m in PAT.finditer(text):
            ids = [x.strip() for x in m.group(1).split(",") if x.strip()]
            if not ids: empty.append(str(f)); continue
            for i in ids:
                if not ID.match(i): continue          # placeholders like <videoId> in templates
                total += 1
                if i not in reg: bad.append((str(f), i))
    return total, bad, empty
def main(argv):
    reg = registry()
    if argv and argv[0] == "--plant":
        t, b, _ = check([], reg)
        planted = Path("/tmp/claims_check_plant.md"); planted.write_text("A planted claim CLAIM(ZZZZZZZZZZZ) that no transcript carries.\n")
        t, b, _ = check([planted], reg)
        ok = len(b) == 1
        print(json.dumps({"plant": "bogus id ZZZZZZZZZZZ", "went_red": ok}))
        return 0 if ok else 2
    files = [Path(a) for a in argv] if argv else family()
    total, bad, empty = check(files, reg)
    print(json.dumps({"files": len(files), "claims_checked": total, "unresolved": [f"{i} in {f}" for f, i in bad], "empty_claims": empty}, indent=1))
    return 0 if total and not bad and not empty else 2
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
