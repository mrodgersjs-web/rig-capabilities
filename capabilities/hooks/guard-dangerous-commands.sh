#!/bin/sh
# rig guard-dangerous-commands — PreToolUse guard for shell tool calls.
# Canonical source: rig-capabilities repo. Installed copies are wired via hook config.
#
# Contract (Claude Code / Codex / Hermes PreToolUse): JSON payload on stdin.
# Exit 2 + stderr message = block the call. Exit 0 = allow. Internal errors
# FAIL OPEN (never brick the fleet); blocks are deterministic pattern matches only.
#
# Blocks: irreversible recursive/system deletes, raw device writes, filesystem
# destruction, forced pushes to default branches, and destructive git resets
# with clean. Everything else passes.
set -u
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0

cmd=$(printf '%s' "$payload" | /usr/bin/python3 -c '
import json,sys
try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input") or {}
    sys.stdout.write(ti.get("command") or ti.get("cmd") or "")
except Exception:
    pass
' 2>/dev/null || true)
[ -n "$cmd" ] || exit 0

block() { echo "rig-guard: blocked — $1. Refine the command or run it manually." >&2; exit 2; }

# irreversible deletes: rm with recursive+force targeting /, $HOME, /*, or system paths
case "$cmd" in
  *sudo*rm*) block "sudo rm is not permitted from agent tool calls" ;;
esac
printf '%s' "$cmd" | /usr/bin/python3 -c '
import re, sys
c = sys.stdin.read()
checks = [
    (r"\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+(-[a-zA-Z]*\s+)*-[a-zA-Z]*f[a-zA-Z]*r", r"(?<![\w/])/(?=\s|$|\*)|(?<![\w])~(?![A-Za-z0-9_-])|(?<![\w])~/|\$HOME(?![A-Za-z0-9_])|\b(usr|etc|sys|boot|var|Library)\b"),  # rm -rf with root/home/system target
    (r"\bmkfs(\.\w+)?\b", None),
    (r"\bdd\b[^\n]*\bof=/dev/(disk|rdisk|nvme|sd|hd)", None),
    (r">\s*/dev/(disk|rdisk|nvme\d|sd[a-z]|hd[a-z])", None),
    (r"\bgit\s+push\b[^\n]*(--force(?!-with-lease)|-f)\b[^\n]*\b(main|master)\b", None),
    (r"\bgit\s+push\b[^\n]*\bmain\b[^\n]*(--force(?!-with-lease)|-f)\b", None),
    (r"\bgit\s+reset\b[^\n]*--hard[^\n]*\s~/|\bgit\s+clean\b[^\n]*-[a-zA-Z]*f[a-zA-Z]*x", None),
    (r"\bchmod\s+-[a-zA-Z]*R[a-zA-Z]*\s+7{3,4}\s+/(?:\s|$)", None),
    (r":\(\)\s*\{.*\|.*&\s*\};\s*:", None),  # fork bomb
]
for sweep, target in checks:
    if re.search(sweep, c):
        if target is None or re.search(target, c):
            sys.exit(1)
sys.exit(0)
' || block "command matches a deterministic irreversible-destruction pattern"
exit 0
