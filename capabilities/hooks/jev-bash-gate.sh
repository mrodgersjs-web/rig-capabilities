#!/bin/sh
# done_when: cmd:python3 scripts/hook_fires_misc.py jev-bash-gate.sh
# jev-bash-gate — Level 6 guardrail hook (PreToolUse, Claude/Codex hook contract).
# The deterministic deny-list lives in guard-dangerous-commands.sh; this is the
# Jev layer for what string lists miss (find -delete, prune, reset --hard).
# Contract: JSON payload on stdin; exit 2 + stderr = block. Fail-OPEN on every
# error (unreachable Jev, timeout, bad JSON) — never bricks the fleet.
# Kill switch: JEV_GATE=0 in the agent env disables this gate.
# Canonical: rig-capabilities/capabilities/hooks/jev-bash-gate.sh
set -u
[ "${JEV_GATE:-1}" = "0" ] && exit 0
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0
printf '%s' "$payload" | /usr/bin/python3 -c '
import json, subprocess, sys, datetime
try:
    payload = json.load(sys.stdin)
    cmd = (payload.get("tool_input") or {}).get("command") or ""
except Exception:
    sys.exit(0)
if len(cmd) < 6 or cmd.lstrip().startswith(("/Users/rig128gb/.rig/bin/rig-s1gate", "rig-s1gate ")):
    sys.exit(0)
try:
    r = subprocess.run(["/Users/rig128gb/.rig/bin/rig-s1gate", "check", "jev.bash-gate", "--stdin", "--json"],
                       input=cmd, capture_output=True, text=True, timeout=6)
    ans = json.loads(r.stdout)["answers"]["destructive_irreversible"]
    p = ans["noul"] if "noul" in ans else ans.get("probabilities", {}).get("yes", 0.0) if ans.get("choice") == "yes" else 0.0
except Exception:
    sys.exit(0)
try:
    with open("/Users/rig128gb/.rig/s1gate/jev-gate.log", "a") as f:
        f.write("%s destr=%.2f cmd=%r\n" % (datetime.datetime.now(), p, cmd[:140]))
except Exception:
    pass
if p >= 0.90:
    sys.stderr.write(
        "jev-bash-gate BLOCK: Jev reads this command as destructive/irreversible "
        "(p=%.2f >= 0.90). Confirm with a human, run it yourself, or set JEV_GATE=0 "
        "for this session. Command: %s\n" % (p, cmd[:200]))
    sys.exit(2)
sys.exit(0)
'
