#!/bin/bash -p
# outcome: agent-engineering:
# done_when: cmd:python3 scripts/hook_fires.py rig-loop-hook.sh
# great_example: examples/great/agent-engineering/iqrsqpi-v11.md
# quality_floor: 0.7
# rig-loop hook entry for Claude Code / Codex (Claude-compatible hook schema).
#   usage: rig-loop-hook.sh <session-start|prompt|pre-tool|post-tool|stop> [claude|codex]
# Reads the hook JSON on stdin, delegates to the rig-loop engine, mirrors its exit code.
# With no active loop run this is a silent no-op (exit 0, no output). A missing engine
# warns and allows — D85 is a build-certification gate, not a pre-tool admission.  RIG_LOOP_MANAGED
set -u
EVENT="${1:-prompt}"
FMT="${2:-claude}"
RIG_LOOP="/Users/rig128gb/Developer/rig-capabilities/bin/rig-loop"
PY="/Users/rig128gb/.homebrew/Cellar/python@3.14/3.14.7/bin/python3"
[ -x "$PY" ] || PY="$(command -v python3)"
if [ ! -f "$RIG_LOOP" ]; then
  echo "[rig-loop] hook engine unavailable — $EVENT allowed (advisory only)" >&2
  exit 0
fi
exec "$PY" -I -B -S "$RIG_LOOP" hook "$EVENT" --format "$FMT"
