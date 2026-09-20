#!/usr/bin/env bash
# live replay: boot lead-agents team, prompt orchestrator, assert SMOKE-OK from a FRESH run
set -euo pipefail
REPO=/Users/rig128gb/Desktop/TAC-Technology-Operating-System/08-omp-build/lead-agents
SID=jex-replay-$$
tmux kill-session -t "$SID" 2>/dev/null || true
tmux new-session -d -s "$SID" -x 220 -y 50 "cd $REPO && exec just teamc .pi/multi-team/opensource-team-config.yaml"
sleep 15; tmux send-keys -t "$SID" Enter; sleep 5
tmux send-keys -t "$SID" -l "Reply with exactly SMOKE-OK. Do not use tools."; tmux send-keys -t "$SID" Enter
sleep 75
OUT=$(tmux capture-pane -p -S -300 -t "$SID")
tmux kill-session -t "$SID" 2>/dev/null || true
echo "$OUT" | grep -q "SMOKE-OK" && { echo "$OUT" | tail -5; echo REPLAY-PASS; } || { echo "REPLAY-FAIL: no SMOKE-OK in capture"; exit 1; }
