#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when: file:capabilities/hooks/rig-loop-hook.sh || echo '{}' | bash capabilities/hooks/rig-loop-hook.sh pre-tool claude
# great_example: examples/great/agent-engineering/iqrsqpi-v11.md
# quality_floor: 0.7
# rig-loop hook entry for Claude Code / Codex (Claude-compatible hook schema).
#   usage: rig-loop-hook.sh <session-start|prompt|pre-tool|post-tool|stop> [claude|codex]
# Reads the hook JSON on stdin, delegates to the rig-loop engine, mirrors its exit code.
# With no active loop run this is a silent no-op (exit 0, no output).  RIG_LOOP_MANAGED
set -u
EVENT="${1:-prompt}"
FMT="${2:-claude}"
RIG_LOOP="${RIG_LOOP_CLI:-$HOME/Developer/rig-capabilities/bin/rig-loop}"
if [ ! -f "$RIG_LOOP" ]; then
  exit 0
fi
exec python3 "$RIG_LOOP" hook "$EVENT" --format "$FMT"
