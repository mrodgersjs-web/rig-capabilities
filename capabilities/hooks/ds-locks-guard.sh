#!/bin/sh
# name: ds-locks-guard
# tier: main
# parent: ds-session-start
# event: PreToolUse:Edit|Write
# outcome: design-ux: blocks edits to locked flagship regions (LOCK:SCREEN-00/01, LOCK:CTA-WIRING, LOCK:ENGINE-CORE) without an unlock
# done_when: cmd:python3 ../rig-design-studio-os/tools/hook_cases.py ds-locks-guard
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
    print(json.dumps({"decision": "block", "reason": "[ds-locks-guard] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if "rig-design-studio/" in path and "rig-design-studio-os" not in path:
    locked = re.search(r"LOCK:(SCREEN-0[01]|CTA-WIRING|ENGINE-CORE)", content)
    if locked and "DS_UNLOCK=" not in os.environ.get("DS_UNLOCK_ENV", ""):
        deny("Write touches locked flagship region LOCK:" + locked.group(1) + "; the flagship is extended, never rebuilt. Ask Mike for an explicit unlock.")
    if re.search(r"/(engine)/", path) and not os.environ.get("DS_UNLOCK_ENV"):
        deny("engine/ is LOCK:ENGINE-CORE territory; explicit unlock required.")
sys.exit(0)
PY
