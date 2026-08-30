#!/usr/bin/env bash
# PreToolUse: block Write/Edit if TAC mode requires plan and plan-gate is RED.
# Opt-in via RIG_TAC_ENFORCE=1 (recommended during /tac-build sessions).
set -euo pipefail
if [[ "${RIG_TAC_ENFORCE:-0}" != "1" ]]; then
  exit 0
fi
# Only care about Write|Edit matchers (caller configures matcher)
export PATH="/usr/bin:/bin:/opt/homebrew/bin:$HOME/.rig/bin:$HOME/.rig/tac/bin:$PATH"
if ! python3 "$HOME/.rig/tac/bin/tac" plan-gate >/tmp/tac-plan-gate.out 2>&1; then
  echo "[TAC plan-gate] BLOCKED Write/Edit: no valid plan. Run /tac-plan or: tac init-plan && tac plan-gate" >&2
  cat /tmp/tac-plan-gate.out >&2 || true
  exit 2
fi
exit 0
