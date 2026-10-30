#!/usr/bin/env bash
# done_when: cmd:python3 scripts/hook_fires_misc.py s1gate-stage-gate-redacted.sh
# s1gate-stage-gate-redacted.sh -- the s1gate stage gate with secrets redacted from
# the state BEFORE it leaves the machine. Wraps ./s1gate-stage-gate.sh and keeps its
# exit contract exactly:
#   0 -> agent proceeds
#   2 -> BLOCKED; stderr is fed back to the SAME session as correction
#   anything else -> warns loudly and proceeds (a missing gate must not masquerade
#                    as a pass, and must not wedge every session)
#
# Usage: s1gate-stage-gate-redacted.sh [RUBRIC] [SUBJECT]   (state on stdin)
# Defaults: RUBRIC=code.review (cheap broad screen), SUBJECT=session-stop.
#
# S1GATE_ENFORCE defaults to 0 (warn-only) here: this path feeds whole session
# transcripts into a hosted classifier, and only calibrated rubrics may hard-block
# (s1gate law 3). Flip to enforcement per-surface once the rubric is calibrated via
# `rig-s1gate label` + `rig-s1gate calibrate`, and only with false-block tuning done
# (law 4: a gate that blocks good work gets switched off).
set -uo pipefail

RUBRIC="${1:-code.review}"
SUBJECT="${2:-session-stop}"
SRC="${BASH_SOURCE[0]}"; while [ -L "$SRC" ]; do SRC="$(readlink "$SRC")"; done
HERE="$(cd "$(dirname "$SRC")" && pwd)"
REDACT="$HERE/redact_state.py"
GATE_HOOK="$HERE/s1gate-stage-gate.sh"

if [ ! -f "$REDACT" ]; then
  echo "s1gate: redactor missing at $REDACT -- state NOT sent, stage gate NOT applied" >&2
  exit 0
fi
if [ ! -x "$GATE_HOOK" ]; then
  echo "s1gate: gate hook missing at $GATE_HOOK -- stage gate NOT applied" >&2
  exit 0
fi

STATE="$(cat)"
CLEAN="$(printf '%s' "$STATE" | python3 "$REDACT")"
export S1GATE_ENFORCE="${S1GATE_ENFORCE:-0}"
printf '%s' "$CLEAN" | "$GATE_HOOK" "$RUBRIC" "$SUBJECT"
