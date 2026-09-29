#!/bin/sh
# name: ds-contrast-check
# tier: sub
# parent: ds-locks-guard
# event: PostToolUse:Write
# outcome: design-ux: blocks token files whose declared text/background pairs fall under 4.5:1
# done_when: cmd:python3 tools/hook_cases.py ds-contrast-check
# DORMANT until wired into a harness settings file by Mike. Canonical source: rig-design-studio-os/studio-harness.
# JEV FIRST applies to judgments; this hook is deterministic CODE and never calls a model.
set -u
DS_HOOK_PAYLOAD=$(cat 2>/dev/null || true); export DS_HOOK_PAYLOAD
[ -n "$DS_HOOK_PAYLOAD" ] || exit 0
unset PYTHONHOME PYTHONPATH
exec /usr/bin/python3 - <<'PY'
import json, os, re, sys, subprocess
from pathlib import Path
try: d = json.loads(os.environ.get("DS_HOOK_PAYLOAD", ""))
except Exception: sys.exit(0)
ti = d.get("tool_input") or {}
cmd = str(ti.get("command") or ""); path = str(ti.get("file_path") or ti.get("path") or "")
content = str(ti.get("content") or ti.get("new_string") or "")
def deny(msg):
    print(json.dumps({"decision": "block", "reason": "[ds-contrast-check] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if re.search(r"tokens?[^/]*\.json$", path):
    try: tok = json.loads(content or Path(path).read_text())
    except Exception: sys.exit(0)
    def lum(h):
        h = h.lstrip('#'); c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
        c = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
        return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
    bad = []
    for p in tok.get("pairs", []):
        a, b = lum(p["fg"]), lum(p["bg"]); r = (max(a, b)+0.05)/(min(a, b)+0.05)
        need = 3.0 if p.get("large") else 4.5
        if r < need: bad.append(f"{p['fg']} on {p['bg']} = {r:.2f}:1 (< {need})")
    if bad: deny("Contrast fails: " + "; ".join(bad))
sys.exit(0)
PY
