#!/bin/sh
# name: ds-session-start
# tier: meta
# event: SessionStart
# outcome: design-ux: prints the design-studio-os load instruction and the Jev-first mandate at session start
# done_when: cmd:python3 tools/hook_cases.py ds-session-start
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
    print(json.dumps({"decision": "block", "reason": "[ds-session-start] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if d.get("hook_event_name") == "SessionStart" or d.get("event") == "SessionStart":
    print("Design Studio OS: load studio-skills/skills/design-studio-os/SKILL.md first. JEV FIRST: typed judgments go to rig-s1gate before any frontier call; DEFERRED when the classifier is down.")
sys.exit(0)
PY
