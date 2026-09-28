#!/usr/bin/env python3
"""Done-test for linkedin-viral.

Every routed child in references/routing.md must resolve on disk, and the
table must carry at least MIN_ROUTES routes (a truncated table is RED, not
green). Exit 0 = GREEN. Exit 2 = RED (dangling route or short table).
Usage: check_routes.py [routing.md] [--min N]
"""
import os, re, sys, pathlib

args = [a for a in sys.argv[1:]]
if "--self-test" in args:
    # Planted-failure regression: a dangling route and a truncated table must
    # both go RED, and the real table must stay GREEN. Temp copies only.
    import subprocess, tempfile
    real = pathlib.Path(__file__).resolve().parent.parent / "references" / "routing.md"
    with tempfile.TemporaryDirectory() as td:
        bad = pathlib.Path(td) / "routing.md"
        bad.write_text(real.read_text(encoding="utf-8") + "\n| planted | S | | all | `~/.planted-failure/does-not-exist/SKILL.md` | planted |\n")
        short = pathlib.Path(td) / "short.md"
        short.write_text("| one | `~/.aside` |\n")
        run = lambda f: subprocess.run([sys.executable, __file__, str(f)], capture_output=True, text=True).returncode
        r_bad, r_short, r_real = run(bad), run(short), run(real)
    ok = (r_bad, r_short, r_real) == (2, 2, 0)
    print(f"self-test planted_dangling={r_bad} planted_short={r_short} real={r_real}")
    print("GREEN" if ok else "RED")
    sys.exit(0 if ok else 2)
min_routes = 40
if "--min" in args:
    i = args.index("--min"); min_routes = int(args[i + 1]); del args[i:i + 2]
here = pathlib.Path(__file__).resolve().parent.parent
routing = pathlib.Path(args[0]) if args else here / "references" / "routing.md"
text = routing.read_text(encoding="utf-8")
paths = re.findall(r"`((?:~|/Users)/[^`\s]+)`", text)
seen, dangling = [], []
for p in paths:
    if p in seen:
        continue
    seen.append(p)
    if not os.path.exists(os.path.expanduser(p)):
        dangling.append(p)
print(f"routes={len(seen)} resolved={len(seen) - len(dangling)} dangling={len(dangling)} min={min_routes}")
for d in dangling:
    print(f"DANGLING {d}")
if dangling or len(seen) < min_routes:
    print("RED")
    sys.exit(2)
print("GREEN")
