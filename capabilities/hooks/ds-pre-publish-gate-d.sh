#!/bin/sh
# name: ds-pre-publish-gate-d
# tier: main
# parent: ds-session-start
# event: PreToolUse:Bash
# outcome: design-ux: blocks deploy, publish and push commands from studio repos unless an approved Gate-D token is present
# done_when: cmd:python3 ../rig-design-studio-os/tools/hook_cases.py ds-pre-publish-gate-d
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
    print(json.dumps({"decision": "block", "reason": "[ds-pre-publish-gate-d] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
outward = re.search(r"\b(netlify\s+deploy|vercel(\s+--prod|\s+deploy)|git\s+push|gh\s+repo\s+create|npm\s+publish|wrangler\s+(pages\s+)?deploy)\b", cmd)
if outward and "DS_GATE_D_APPROVED=" not in cmd:
    deny("Outward action '" + outward.group(1) + "' needs Mike's Gate-D approval token (DS_GATE_D_APPROVED=<request id>).")
sys.exit(0)
PY
