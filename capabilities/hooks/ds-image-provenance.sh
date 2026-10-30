#!/bin/sh
# name: ds-image-provenance
# tier: sub
# parent: ds-locks-guard
# event: PostToolUse:Write
# outcome: design-ux: blocks site images written without a provenance sidecar (<file>.provenance.json naming source, license, generator)
# done_when: cmd:python3 ../rig-design-studio-os/tools/hook_cases.py ds-image-provenance
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
    print(json.dumps({"decision": "block", "reason": "[ds-image-provenance] " + msg + " This block is final; do not work around it."}))
    sys.exit(2)
if re.search(r"\.(png|jpe?g|webp|avif)$", path, re.I) and ("/site" in path or "/public/" in path):
    if not Path(path + ".provenance.json").exists():
        deny("Image " + os.path.basename(path) + " has no provenance sidecar (source, license, generator).")
sys.exit(0)
PY
