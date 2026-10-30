#!/bin/sh
# name: ds-citation-check
# tier: sub
# parent: ds-pre-write-slop-lint
# event: PostToolUse:Write
# outcome: design-ux: runs claims_check on any written studio skill, law or exemplar file and blocks on unresolved or copied citations
# done_when: cmd:python3 ../rig-design-studio-os/tools/hook_cases.py ds-citation-check
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
    print(json.dumps({"decision": "block", "reason": "[ds-citation-check] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if "rig-design-studio-os/" in path and path.endswith(".md") and "/studio-" in path:
    root = path.split("rig-design-studio-os/")[0] + "rig-design-studio-os"
    r = subprocess.run(["/usr/bin/python3", root + "/tools/claims_check.py", path], capture_output=True, text=True)
    if r.returncode == 2 and "no citations" not in r.stdout:
        deny("claims_check RED: " + r.stdout.strip().splitlines()[0][:300])
sys.exit(0)
PY
