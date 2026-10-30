#!/usr/bin/env bash
# done_when: cmd:python3 scripts/hook_fires_misc.py s1gate-stage-gate.sh
# s1gate-stage-gate.sh -- stop a coding agent finishing a stage that is not good enough.
#
# Wire as a Claude Code / OMP Stop or PostToolUse hook:
#   exit 0 -> agent proceeds
#   exit 2 -> BLOCKED; stderr is fed back to the agent as correction
#
# Doctrine (rig-capabilities/capabilities/skills/s1gate/SKILL.md):
#   - On failure, re-prompt the SAME session with the reasons. Never restart.
#   - An advisory (uncalibrated) rubric warns but never hard-blocks.
#   - S1GATE_ENFORCE=0 forces warn-only everywhere. Use while building the corpus.
set -uo pipefail

RUBRIC="${1:-code.diff}"
SUBJECT="${2:-$(basename "${PWD}")}"
GATE="${S1GATE_BIN:-$HOME/Developer/rig-capabilities/bin/rig-s1gate}"
MAX_BYTES="${S1GATE_MAX_BYTES:-60000}"

if [ ! -x "$GATE" ]; then
  echo "s1gate: gate binary not found at $GATE -- stage gate NOT applied" >&2
  exit 0   # a missing gate must not silently masquerade as a pass; it warns loudly.
fi

STATE="$(cat)"
if [ -z "${STATE// }" ]; then
  echo "s1gate: empty artifact, nothing to score" >&2
  exit 0
fi
STATE="${STATE:0:$MAX_BYTES}"

OUT="$(printf '%s' "$STATE" | "$GATE" check "$RUBRIC" --stdin --subject "$SUBJECT" 2>&1)"
CODE=$?

case "$CODE" in
  0) exit 0 ;;
  1)
    if [ "${S1GATE_ENFORCE:-1}" = "0" ]; then
      echo "s1gate WARN (enforcement disabled):" >&2; echo "$OUT" >&2; exit 0
    fi
    echo "s1gate BLOCKED this stage. Fix these, then continue in THIS session:" >&2
    echo "$OUT" >&2
    exit 2 ;;
  2)
    echo "s1gate ESCALATE -- not blocking, but a human or System 2 model should look:" >&2
    echo "$OUT" >&2
    exit 0 ;;
  *)
    echo "s1gate misconfigured (exit $CODE); stage gate NOT applied:" >&2
    echo "$OUT" >&2
    exit 0 ;;
esac
