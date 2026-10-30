#!/usr/bin/env python3
"""Report each business-strategy-os done_when check individually, so a failure names itself."""
import json, re, subprocess, sys
from pathlib import Path
REPO = Path("/Users/rig128gb/Developer/rig-capabilities")
FM = (REPO / "capabilities/skills/business-strategy-os/SKILL.md").read_text(encoding="utf-8")
fence = FM.split("\n---\n", 1)[0]
items = []
in_dw = False
for line in fence.splitlines():
    if re.match(r"^done_when\s*:", line):
        in_dw = True; continue
    if in_dw:
        m = re.match(r'^\s*-\s+"?([^"]+)"?\s*$', line)
        if m: items.append(m.group(1)); continue
        if line.strip() and not line.startswith((" ", "-")): break
def run(check: str):
    kind, _, rest = check.partition(":")
    if kind == "file":
        p = REPO / rest
        return p.exists(), f"exists={p.exists()}"
    if kind == "grep":
        path, _, pat = rest.rpartition(":")
        p = REPO / path
        if not p.exists(): return False, f"file missing: {path}"
        rx = re.compile(pat)
        hit = any(rx.search(l) for l in p.read_text(encoding="utf-8").splitlines())
        return hit, f"pattern {pat!r} found={hit}"
    if kind == "cmd":
        r = subprocess.run(rest, shell=True, cwd=REPO, capture_output=True, text=True, timeout=300)
        return r.returncode == 0, f"exit={r.returncode} out={(r.stdout or r.stderr).strip()[:120]}"
    return False, "unknown check kind"
ok_all = True
for c in items:
    ok, detail = run(c)
    ok_all &= ok
    print(("PASS " if ok else "FAIL ") + c[:74] + "\n      " + detail)
print("\nALL PASS" if ok_all else "\nSOME FAILED")
sys.exit(0 if ok_all else 2)
