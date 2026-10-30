#!/usr/bin/env bash
# done_when: cmd:python3 scripts/hook_fires_misc.py done-gate.sh
# done-gate.sh -- Claude Code Stop hook wrapper for done-gate.py.
# Canonical: rig-capabilities/capabilities/hooks/done-gate.sh
# Contract: stdin JSON payload (transcript_path, stop_hook_active, session_id).
#   exit 0 = proceed, exit 2 = BLOCK (stderr feeds back to the SAME session).
# Shadow-first: DONE_GATE_ENFORCE defaults to 0. Kill switch: DONE_GATE=0.
set -u
[ "${DONE_GATE:-1}" = "0" ] && exit 0
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/done-gate.py"
