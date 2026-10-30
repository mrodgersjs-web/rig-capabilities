#!/bin/sh
# name: ds-pre-write-slop-lint
# tier: main
# parent: ds-session-start
# event: PreToolUse:Write
# outcome: design-ux: blocks writing page copy that carries banned AI tells (em dashes, 'unlock', 'elevate', 'seamless', 'in today's fast-paced')
# done_when: cmd:python3 ../rig-design-studio-os/tools/hook_cases.py ds-pre-write-slop-lint
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
    print(json.dumps({"decision": "block", "reason": "[ds-pre-write-slop-lint] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if re.search(r"\.(html|md|mdx|tsx|jsx)$", path) and ("/copy/" in path or "/site" in path or "/pages/" in path):
    tells = [t for t in ["\u2014", "unlock", "elevate", "seamless", "in today's fast-paced", "delve", "game-changer", "leverage"] if t.lower() in content.lower()]
    if tells:
        deny("Copy contains AI tells: " + ", ".join(repr(t) for t in tells) + ". Rewrite via ds-slop-rewrite-loop.")
sys.exit(0)
PY
