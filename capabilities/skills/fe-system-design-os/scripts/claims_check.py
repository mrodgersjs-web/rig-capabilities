#!/usr/bin/env python3
"""FE System Design family claim gate.

Every CLAIM(<videoId>[@mm:ss][, ...]) in the family must resolve against the independent registry
data/corpora/frontend-engineer/manifest.jsonl: the id must be a captured video, and a timestamp,
when given, must fall inside that video's duration AND match a real transcript line start
(+/- 15 s). Transcripts live in gitignored .context/frontend-engineer-yt/ (creator's words, never
committed).

usage: claims_check.py [FILE ...]   default: fe-system-design-os, fe-system-design-doctrine, fesd-*,
                                     capabilities/agents/fesd-*.md
       claims_check.py --plant      plant a bogus id and an out-of-range timestamp in a temp file;
                                     exit 0 only if BOTH go RED
exit: 0 all resolve | 1 registry missing | 2 findings. Stdlib only, read-only, no network."""
import glob, json, re, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / "data/corpora/frontend-engineer/manifest.jsonl"
CLAIM = re.compile(r"CLAIM\(([^)]*)\)")
REF = re.compile(r"^([A-Za-z0-9_-]{11})(?:@(\d{1,3}):(\d{2})(?::(\d{2}))?)?$")
LINE_TS = re.compile(r"^\[(\d+):(\d{2})(?::(\d{2}))?\s*-", re.M)


def registry():
    if not MANIFEST.exists():
        print(f"registry missing: {MANIFEST}", file=sys.stderr)
        sys.exit(1)
    reg = {}
    for line in MANIFEST.open():
        if line.strip():
            r = json.loads(line)
            reg[r["video_id"]] = r
    return reg


_ts = {}


def starts(reg, vid):
    if vid not in _ts:
        f = REPO / reg[vid]["file"]
        s = []
        if f.exists():
            for m in LINE_TS.finditer(f.read_text(encoding="utf-8")):
                a, b, c = m.groups()
                s.append(int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b))
        _ts[vid] = s
    return _ts[vid]


def family():
    pats = ["capabilities/skills/fe-system-design-os/**/*.md",
            "capabilities/skills/fe-system-design-doctrine/**/*.md",
            "capabilities/skills/fesd-*/**/*.md",
            "capabilities/agents/fesd-*.md"]
    out = set()
    for p in pats:
        out |= {Path(x) for x in glob.glob(str(REPO / p), recursive=True)}
    return sorted(out)


def check(files, reg):
    total, bad = 0, []
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        for m in CLAIM.finditer(text):
            for raw in [x.strip() for x in m.group(1).split(",") if x.strip()]:
                if raw.startswith("<"):
                    continue  # template placeholder
                total += 1
                r = REF.match(raw)
                if not r:
                    bad.append(f"{f}: malformed ref {raw!r}")
                    continue
                vid, mm, ss, hh = r.groups()
                if vid not in reg:
                    bad.append(f"{f}: unknown video id {vid}")
                    continue
                if mm is not None:
                    t = int(mm) * 3600 + int(ss) * 60 + int(hh) if hh else int(mm) * 60 + int(ss)
                    dur = reg[vid].get("duration_s") or 0
                    if dur and t > dur:
                        bad.append(f"{f}: {raw} beyond duration {dur}s")
                        continue
                    st = starts(reg, vid)
                    if st and min(abs(t - x) for x in st) > 15:
                        bad.append(f"{f}: {raw} matches no transcript line (+/-15s)")
    return total, bad


def main(argv):
    reg = registry()
    if argv and argv[0] == "--plant":
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
            t.write("law A CLAIM(ZZZZZZZZZZZ)\nlaw B CLAIM(5vyKhm2NTfw@999:00)\n")
        n, bad = check([t.name], reg)
        ok = len(bad) == 2
        print(f"plant: {len(bad)}/2 planted defects caught -> {'RED as expected' if ok else 'GATE IS BLIND'}")
        return 0 if ok else 2
    files = [Path(a) for a in argv] or family()
    n, bad = check(files, reg)
    for b in bad:
        print("RED", b)
    print(f"{len(files)} files, {n} citations, {len(bad)} unresolved")
    if n == 0:
        print("RED no citations found (empty family is not a pass)")
        return 2
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
