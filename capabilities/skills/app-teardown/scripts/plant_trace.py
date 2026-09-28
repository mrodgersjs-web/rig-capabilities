#!/usr/bin/env python3
"""Planted failures for trace.py: each gate rule is broken in a scratch copy and test_trace.py
must go RED. A plant whose bytes did not change is refused."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLANTS = [
    ("commit existence check off", '        cache[sha] = r.returncode == 0', '        cache[sha] = True'),
    ("SKIP reason rule off", '    if st == "SKIP" and len((r.get("reason") or "").strip()) < 8:', '    if False:'),
    ("MAPPED counts done regardless", '        return bool(r.get("covers")) and all(c in rows and done(c, seen | {i}) for c in r["covers"])',
     '        return True'),
    ("import overwrites decisions", '        rows[row["id"]] = row\n        return "new"', '        rows[row["id"]] = row\n        return "new"\n    rows[row["id"]] = row\n    return "kept"'),
    ("BUILT without commit allowed", '            elif not commits:\n                problems.append', '            elif False:\n                problems.append'),
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:8]


def suite(trace_path):
    env = {**os.environ, "TRACE_PY": trace_path}
    return subprocess.run([sys.executable, os.path.join(HERE, "test_trace.py")], env=env, capture_output=True).returncode


def start(trace_path):
    env = {**os.environ, "TRACE_PY": trace_path}
    return subprocess.Popen([sys.executable, os.path.join(HERE, "test_trace.py")], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# all copies run in parallel so the whole proof fits the estate's 15 s done-test budget
jobs, ok, tmp = [("baseline", None, None, start(os.path.join(HERE, "trace.py")))], True, []
for name, old, new in PLANTS:
    d = tempfile.mkdtemp()
    tmp.append(d)
    p = os.path.join(d, "trace.py")
    shutil.copy2(os.path.join(HERE, "trace.py"), p)
    with open(p) as f:
        src = f.read()
    if old not in src:
        print(f"REFUSED {name}: anchor not found")
        ok = False
        continue
    before = sha(p)
    with open(p, "w") as f:
        f.write(src.replace(old, new, 1))
    after = sha(p)
    if before == after:
        print(f"REFUSED {name}: bytes unchanged")
        ok = False
        continue
    jobs.append((name, before, after, start(p)))
for name, before, after, proc in jobs:
    rc = proc.wait()
    if name == "baseline":
        print(f"baseline rc={rc} (expect 0)")
        ok &= rc == 0
    else:
        print(f"{'RED  ' if rc != 0 else 'GREEN'} {name:34} sha {before}->{after}")
        ok &= rc != 0
for d in tmp:
    shutil.rmtree(d, ignore_errors=True)
print("PLANTS", "ALL RED (gate has teeth)" if ok else "SOME STAYED GREEN (gate is weak)")
sys.exit(0 if ok else 1)
