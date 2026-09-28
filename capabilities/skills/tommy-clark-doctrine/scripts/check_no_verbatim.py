#!/usr/bin/env python3
"""Anti-copy gate for tommy-clark-doctrine.

The doctrine must be synthesis, never transcript text. Builds 12-word
shingles from the LOCAL transcript corpus and fails if any doctrine file
shares one. Also checks the source index covers all 79 videos.
Exit 0 = GREEN, 2 = RED, 3 = SKIPPED (corpus not on this machine; never a pass).
Usage: check_no_verbatim.py [doctrine_dir] [--corpus DIR] [--n 12] [--no-index]
  --no-index  scan any skill folder (SKILL.md, references/*.md, eden/*.md)
              without requiring the 79-row source index.
"""
import os, re, sys, pathlib

args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
corpus = pathlib.Path(os.path.expanduser(opt("--corpus", "~/Developer/brand-workspace/youtube-intel-pipeline/tommy-clark/transcripts-clean")))
n = int(opt("--n", "12"))
need_index = "--no-index" not in args
args = [a for a in args if a != "--no-index"]
root = pathlib.Path(args[0]) if args else pathlib.Path(__file__).resolve().parent.parent
if not corpus.is_dir():
    print(f"SKIPPED corpus missing: {corpus}"); sys.exit(3)

def words(t):
    return re.findall(r"[a-z0-9']+", t.lower())

if "--self-test" in sys.argv:
    # Planted-failure regression: paste a 16-word run from a real transcript
    # into a TEMP copy of the doctrine and require RED; the real doctrine must
    # stay GREEN. The planted text never touches the skill folder.
    import shutil, subprocess, tempfile
    base = pathlib.Path(__file__).resolve().parent.parent
    first = sorted(corpus.glob("*.txt"))[0]
    w = words(first.read_text(encoding="utf-8", errors="ignore").split("\n\n", 1)[-1])
    planted = " ".join(w[100:116])
    with tempfile.TemporaryDirectory() as td:
        dst = pathlib.Path(td) / "doctrine"
        shutil.copytree(base, dst, ignore=shutil.ignore_patterns("__pycache__"))
        f = dst / "references" / "positioning.md"
        f.write_text(f.read_text(encoding="utf-8") + "\n" + planted + "\n")
        run = lambda d: subprocess.run([sys.executable, __file__, str(d)], capture_output=True, text=True).returncode
        r_bad, r_real = run(dst), run(base)
    ok = (r_bad, r_real) == (2, 0)
    print(f"self-test planted_verbatim={r_bad} real={r_real} planted_words={len(planted.split())}")
    print("GREEN" if ok else "RED")
    sys.exit(0 if ok else 2)

shingles = set()
for f in sorted(corpus.glob("*.txt")):
    body = f.read_text(encoding="utf-8", errors="ignore").split("\n\n", 1)[-1]
    w = words(body)
    for i in range(len(w) - n + 1):
        shingles.add(" ".join(w[i:i + n]))
docs = sorted(list(root.glob("SKILL.md")) + list(root.glob("references/*.md")) + list(root.glob("eden/*.md")))
hits = []
for d in docs:
    w = words(d.read_text(encoding="utf-8"))
    for i in range(len(w) - n + 1):
        s = " ".join(w[i:i + n])
        if s in shingles:
            hits.append((d.name, s)); break
idx = root / "references" / "source-index.md"
rows = len(re.findall(r"^\|\s*\d+\s*\|", idx.read_text(encoding="utf-8"), re.M)) if idx.exists() else 0
print(f"corpus_shingles={len(shingles)} docs={len(docs)} verbatim_hits={len(hits)} source_rows={rows} n={n}")
for name, s in hits:
    print(f"VERBATIM {name}: {s}")
if hits or (need_index and rows < 79) or len(docs) < 1:
    print("RED"); sys.exit(2)
print("GREEN")
