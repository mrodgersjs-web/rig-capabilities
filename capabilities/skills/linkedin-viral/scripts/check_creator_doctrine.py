#!/usr/bin/env python3
"""Done-test for LinkedIn creator doctrine skills (lv-creator-<slug>).

GREEN only when, for the skill folder given:
  1. frontmatter `name` equals the folder name; the description carries the
     JEV-FIRST MANDATE; the body opens with a `## JEV-first mandate` section;
  2. references/ holds 3+ topic sub-skills (hooks, writing, visuals, engagement,
     timing-and-algorithm, strategy-and-growth) of 400+ bytes each;
  3. references/source-index.md lists exactly as many videos as the creator's
     local manifest reports transcripts for;
  4. no skill file shares a 12-word run with that creator's local transcripts;
  5. every backticked ~/ or /Users path resolves on disk.
Exit 0 GREEN, 2 RED, 3 SKIPPED (corpus not on this machine; never a pass).

Also:  --scan <dir>   no-copy scan of any folder against ALL creator corpora
       --all          check every lv-creator-* folder
       --self-test <dir>  plant a 16-word transcript run in a temp copy; must go RED
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

PIPE = pathlib.Path(os.path.expanduser("~/Developer/brand-workspace/youtube-intel-pipeline"))
SKILLS = pathlib.Path(__file__).resolve().parent.parent.parent
TOPICS = {"hooks.md", "writing.md", "visuals.md", "engagement.md", "timing-and-algorithm.md", "strategy-and-growth.md"}
N = 12


def words(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def shingles_of_corpus(slug):
    d = PIPE / slug / "transcripts-clean"
    if not d.is_dir():
        return None
    out = set()
    for f in sorted(d.glob("*.txt")):
        w = words(f.read_text(encoding="utf-8", errors="ignore").split("\n\n", 1)[-1])
        out.update(" ".join(w[i:i + N]) for i in range(len(w) - N + 1))
    return out


def skill_files(d):
    return sorted([p for p in [d / "SKILL.md"] if p.exists()] + list((d / "references").glob("*.md")) if (d / "references").is_dir() else [p for p in [d / "SKILL.md"] if p.exists()])


def copied(files, sh):
    hits = []
    for f in files:
        w = words(f.read_text(encoding="utf-8"))
        for i in range(len(w) - N + 1):
            s = " ".join(w[i:i + N])
            if s in sh:
                hits.append((f.name, s)); break
    return hits


def check(d):
    d = pathlib.Path(d).resolve()
    errs, slug = [], d.name.replace("lv-creator-", "", 1)
    man = PIPE / slug / "manifest.json"
    if not man.exists():
        return ["SKIPPED: manifest missing " + str(man)], True
    sk = d / "SKILL.md"
    if not sk.exists():
        return ["missing SKILL.md"], False
    t = sk.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if not m:
        errs.append("no frontmatter")
    else:
        fm, body = m.groups()
        if not re.search(r"^name:\s*" + re.escape(d.name) + r"\s*$", fm, re.M):
            errs.append("frontmatter name != folder name")
        if "JEV-FIRST MANDATE" not in fm:
            errs.append("description lacks JEV-FIRST MANDATE")
        if not re.search(r"^## JEV-first mandate", body[:2500], re.M):
            errs.append("body does not open with '## JEV-first mandate'")
    refs = d / "references"
    topics = [p for p in refs.glob("*.md") if p.name in TOPICS] if refs.is_dir() else []
    if len(topics) < 3:
        errs.append(f"only {len(topics)} topic sub-skills (need >= 3 of {sorted(TOPICS)})")
    small = [p.name for p in topics if p.stat().st_size < 400]
    if small:
        errs.append(f"topic sub-skills under 400 bytes: {small}")
    stray = [p.name for p in refs.glob("*.md") if p.name not in TOPICS | {"source-index.md"}] if refs.is_dir() else []
    if stray:
        errs.append(f"non-standard reference files: {stray}")
    want = json.load(open(man)).get("transcriptsOk")
    si = refs / "source-index.md"
    rows = len(re.findall(r"^\|\s*\d+\s*\|", si.read_text(encoding="utf-8"), re.M)) if si.exists() else 0
    if rows != want:
        errs.append(f"source-index rows {rows} != manifest transcripts {want}")
    files = skill_files(d)
    for f in files:
        for p in re.findall(r"`((?:~|/Users)/[^`\s]+)`", f.read_text(encoding="utf-8")):
            if not os.path.exists(os.path.expanduser(p)):
                errs.append(f"dangling path in {f.name}: {p}")
    sh = shingles_of_corpus(slug)
    if sh is None:
        return ["SKIPPED: corpus missing"], True
    for name, s in copied(files, sh):
        errs.append(f"12-word run copied from transcripts in {name}: {s}")
    return errs, False


def report(d):
    errs, skipped = check(d)
    print(f"{pathlib.Path(d).name}: errors={0 if skipped else len(errs)}{' SKIPPED' if skipped else ''}")
    for e in errs:
        print(f"  {'SKIP' if skipped else 'RED'} {e}")
    return (not errs) and not skipped, skipped


args = sys.argv[1:]
if args[:1] == ["--scan"]:
    target = pathlib.Path(args[1]).resolve()
    files = [p for p in target.rglob("*.md")]
    total = 0
    for man in sorted(PIPE.glob("*/manifest.json")):
        sh = shingles_of_corpus(man.parent.name)
        if not sh:
            continue
        hits = copied(files, sh)
        total += len(hits)
        for name, s in hits:
            print(f"  RED {name} copies {man.parent.name}: {s}")
    print(f"scan {target.name}: files={len(files)} corpora={len(list(PIPE.glob('*/manifest.json')))} hits={total}")
    print("GREEN" if total == 0 else "RED")
    sys.exit(0 if total == 0 else 2)
if args[:1] == ["--self-test"]:
    real = pathlib.Path(args[1]).resolve()
    if not real.is_dir():
        print(f"RED skill folder missing: {real}"); sys.exit(2)
    slug = real.name.replace("lv-creator-", "", 1)
    cdir = PIPE / slug / "transcripts-clean"
    # Pick the plant source with the MOST tokens: never plant from a file too
    # short (or non-Latin) to yield a 16-word run, which would make the plant a
    # silent no-op (an all-green run on an unplanted test).
    best, best_n = None, 0
    for f in sorted(cdir.glob("*.txt")):
        n = len(words(f.read_text(encoding="utf-8", errors="ignore").split("\n\n", 1)[-1]))
        if n > best_n:
            best, best_n = f, n
    if best is None or best_n < 240:
        print(f"RED self-test cannot plant: no transcript with >= 240 tokens in {cdir}")
        sys.exit(2)
    w = words(best.read_text(encoding="utf-8", errors="ignore").split("\n\n", 1)[-1])
    planted = " ".join(w[200:216])
    if len(planted.split()) != 16:
        print(f"RED self-test plant run is {len(planted.split())} words, not 16: source {best.name}")
        sys.exit(2)
    with tempfile.TemporaryDirectory() as td:
        cp = pathlib.Path(td) / real.name
        shutil.copytree(real, cp)
        topic_files = sorted(p_ for p_ in (cp / "references").glob("*.md") if p_.name in TOPICS)
        if not topic_files:
            print("RED self-test: no topic sub-skill to plant into"); sys.exit(2)
        tf = topic_files[0]
        before = tf.stat().st_size
        tf.write_text(tf.read_text(encoding="utf-8") + "\n" + planted + "\n", encoding="utf-8")
        after = tf.stat().st_size
        if after <= before:
            print("RED self-test: planted bytes did not move the file"); sys.exit(2)
        bad, _ = check(cp)
    good, _ = check(real)
    ok = any("copied" in e for e in bad) and not good
    print(f"self-test source={best.name} planted16=ok file_moved={before}->{after} planted_copy={'RED' if bad else 'GREEN(!)'} real={'RED' if good else 'GREEN'}")
    print("GREEN" if ok else "RED")
    sys.exit(0 if ok else 2)

if args[:1] == ["--all"]:
    dirs = sorted(p for p in SKILLS.glob("lv-creator-*") if p.is_dir())
    res = [report(p) for p in dirs]
    greens = sum(1 for ok, sk in res if ok)
    print(f"creator skills={len(dirs)} green={greens} skipped={sum(1 for ok, sk in res if sk)}")
    ok = bool(dirs) and greens == len(dirs)
    print("GREEN" if ok else "RED")
    sys.exit(0 if ok else 2)
ok, skipped = report(args[0])
print("SKIPPED" if skipped else ("GREEN" if ok else "RED"))
sys.exit(3 if skipped else (0 if ok else 2))
