#!/usr/bin/env python3
"""Google Ads family claim gate. Two checks against the independent registry
data/corpora/google-ads/manifest.jsonl (+ the local transcript files it names under
.context/google-ads-creators/, never committed - creators' copyrighted words):

  1. every CLAIM(<videoId>[, ...]) resolves to a captured transcript;
  2. every quote line  > "<words>" (<videoId>, @handle)  is a verbatim substring of THAT
     video's transcript (case, punctuation and whitespace normalised; auto-captions only).

usage: claims_check.py [FILE ...]   default: the whole family (google-ads-os, ga-*,
                                     google-ads-doctrine, corpus notes)
       claims_check.py --plant      prove both gates go RED: a bogus id and a fabricated quote
                                     planted in a temp file (exit 0 only if both fire)
exit:  0 all resolve | 1 registry missing | 2 unresolved ids, empty claims or unverifiable quotes
Stdlib only, read-only, no network."""
import glob, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORP = REPO / "data/corpora/google-ads"
MANIFEST = CORP / "manifest.jsonl"
CLAIM = re.compile(r"CLAIM\(([^)]*)\)")
QUOTE = re.compile(r'^>\s*"(.+?)"\s*\(([A-Za-z0-9_-]{11})\s*,', re.M)
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def norm(s):
    return " ".join(re.sub(r"[^a-z0-9' ]+", " ", s.lower().replace("\u2019", "'")).split())


def registry():
    if not MANIFEST.exists():
        print(f"registry missing: {MANIFEST}", file=sys.stderr)
        sys.exit(1)
    reg = {}
    for line in MANIFEST.open():
        if line.strip():
            r = json.loads(line)
            reg[r["video_id"]] = REPO / r["file"]   # repo-relative: .context/google-ads-creators/...
    return reg


_cache = {}


def transcript(reg, vid):
    if vid not in _cache:
        _cache[vid] = norm(reg[vid].read_text(encoding="utf-8"))
    return _cache[vid]


def family():
    pats = [
        "capabilities/skills/google-ads-os/SKILL.md",
        "capabilities/skills/google-ads-os/references/**/*.md",
        "capabilities/skills/ga-*/SKILL.md",
        "capabilities/skills/ga-*/references/**/*.md",
        "capabilities/skills/google-ads-doctrine/SKILL.md",
        "capabilities/skills/google-ads-doctrine/references/**/*.md",
        "data/corpora/google-ads/notes/*.md",
    ]
    out = []
    for p in pats:
        out += sorted(Path(x) for x in glob.glob(str(REPO / p), recursive=True))
    return sorted(set(f for f in out if f.exists()))


def check(files, reg):
    total, bad, empty, quotes, badq = 0, [], [], 0, []
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        for m in CLAIM.finditer(text):
            ids = [x.strip() for x in m.group(1).split(",") if x.strip()]
            if not ids:
                empty.append(str(f))
                continue
            for i in ids:
                if not ID.match(i):
                    continue  # template placeholders like <videoId>
                total += 1
                if i not in reg:
                    bad.append((str(f), i))
        for m in QUOTE.finditer(text):
            q, vid = m.group(1), m.group(2)
            quotes += 1
            if vid not in reg:
                badq.append((str(f), vid, q[:60], "id not in registry"))
            elif norm(q) not in transcript(reg, vid):
                badq.append((str(f), vid, q[:60], "not verbatim in transcript"))
    return total, bad, empty, quotes, badq


def main(argv):
    reg = registry()
    if argv and argv[0] == "--plant":
        some_id = next(iter(reg))
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
            t.write("A planted claim CLAIM(ZZZZZZZZZZZ) that no transcript carries.\n")
            t.write(f'> "the only google ads tactic that matters is buying a billboard in times square" ({some_id}, @planted)\n')
        total, bad, _, quotes, badq = check([Path(t.name)], reg)
        ok = len(bad) == 1 and len(badq) == 1
        print(json.dumps({"plant_bogus_id_red": len(bad) == 1, "plant_fabricated_quote_red": len(badq) == 1, "went_red": ok}))
        return 0 if ok else 2
    files = [Path(a) for a in argv] if argv else family()
    total, bad, empty, quotes, badq = check(files, reg)
    print(json.dumps({
        "files": len(files), "claims_checked": total, "quotes_checked": quotes,
        "unresolved": [f"{i} in {f}" for f, i in bad], "empty_claims": empty,
        "bad_quotes": [f"{v} {why}: \"{q}\" in {f}" for f, v, q, why in badq],
    }, indent=1))
    return 0 if total and not bad and not empty and not badq else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
