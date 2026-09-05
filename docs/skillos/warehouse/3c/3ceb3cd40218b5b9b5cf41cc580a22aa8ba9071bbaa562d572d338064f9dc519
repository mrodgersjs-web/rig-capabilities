#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when: cmd:T="${TMPDIR:-/tmp}/wm-gate-red-$$"; mkdir -p "$T"; : > "$T/ledger.jsonl"; printf '{"session_id":"wm-gate-fixture","tool_name":"Write","tool_input":{"file_path":"state.json","content":"goal: ship the gate\nstatus: DONE"}}' | RIG_WM_LEDGER="$T/ledger.jsonl" /bin/bash capabilities/hooks/working-memory-commit-gate.sh; rc=$?; rm -rf "$T"; test $rc -eq 2 || cmd:T="${TMPDIR:-/tmp}/wm-gate-syn-$$"; mkdir -p "$T"; printf '{"session_id":"wm-gate-fixture","receipt":"r-1","observation":"pytest green","evidence":"%s/absent-artifact.txt"}\n' "$T" > "$T/ledger.jsonl"; printf '{"session_id":"wm-gate-fixture","tool_input":{"content":"done: true"}}' | RIG_WM_LEDGER="$T/ledger.jsonl" /bin/bash capabilities/hooks/working-memory-commit-gate.sh; rc=$?; rm -rf "$T"; test $rc -eq 2 || cmd:T="${TMPDIR:-/tmp}/wm-gate-pass-$$"; mkdir -p "$T"; printf 'pytest exit=0\n' > "$T/obs.txt"; printf '{"session_id":"wm-gate-fixture","receipt":"r-1","observation":"pytest exit 0","evidence":"%s/obs.txt"}\n' "$T" > "$T/ledger.jsonl"; printf '{"session_id":"wm-gate-fixture","tool_input":{"content":"status: DONE"}}' | RIG_WM_LEDGER="$T/ledger.jsonl" /bin/bash capabilities/hooks/working-memory-commit-gate.sh; rc=$?; rm -rf "$T"; test $rc -eq 0
# great_example: examples/great/agent-engineering/working-memory-commit-gate.md
# quality_floor: 0.6
# wm-commit-gate.sh — PreToolUse deny hook: no DONE without an observation-backed receipt row.
#
# Mechanism (Recuris, arXiv:2608.24876; video F1XqqVNBa4o; repo Gen-Verse/Recuris):
# a working-memory ledger holds a verified task state and the model may only PROPOSE
# state changes — the checker compares each proposal against an external environment
# observation and only the kernel commits supported changes. "working memory proposes
# that the state changed, the checkers compares now the proposal with the external
# evidence" ... "a goal is acknowledged here as completed only if the environment
# observation supports it".
#
# Contract (Claude Code / Codex / Hermes PreToolUse): JSON payload on stdin.
# Exit 2 + stderr message = block the call. Exit 0 = allow.
# Blocks ONLY tool calls whose payload carries a completion claim (done/status/state
# key set to true/DONE/complete, or a YAML-style "status: DONE" / "done: true" inside
# written content or a shell command, or the TASK_COMPLETE sentinel) while the run has
# NO observation-backed receipt row in the working-memory ledger. Everything else
# passes. Internal extraction errors FAIL OPEN (never brick the fleet); the claim
# check itself fails CLOSED — a completion claim with no ledger is a block.
#
# Ledger: $RIG_WM_LEDGER (JSONL, one row per committed state change). A row counts as
# a receipt iff it has a non-empty "receipt" id, a non-empty "observation" (what the
# environment showed), a non-empty "evidence" path that EXISTS on disk, and a
# "session_id" equal to the payload session or "*". A receipt row naming a missing
# evidence artifact is a synthetic receipt: registered here as rejected, exactly as the
# reference repo rejects synthetic receipts. Rows are written by the harness after the
# environment observation — never by the model mid-turn.
#
# Proposal escape hatch (model-facing path): a claim payload carrying
# "proposed": true / "proposal": true is a PROPOSAL, not a commit, and passes. The
# gate exists to block the commit step only the harness may take.
#
# Ceiling inherited from Recuris: this checker cannot authenticate WHO wrote the ledger
# row — an agent with shell access to the ledger could forge a row whose evidence file
# it also created. The evidence-exists check raises the bar (a claim must at least
# name a real artifact) but writer identity remains a harness-kernel concern outside any
# PreToolUse hook. Wiring this hook into a harness settings file is a separate Gate-D
# action; the matcher should cover Write|Edit|MultiEdit|Bash.
#
# Limitation (house rule honored, compiler untouched): catalog.py's `# - item`
# continuation syntax is not used here; all three fixtures ride the `||`-split
# done_when line, so no fixture may itself contain `||`.
set -uo pipefail

payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || exit 0

# Normalize: JSON payloads escape embedded quotes as \" — strip backslashes so one
# pass of grep/sed sees both payload-level keys and keys embedded inside strings.
norm="$(printf '%s' "$payload" | tr -d '\\')"

# 1) Completion claim? JSON key form, YAML/in-content form, or sentinel.
claim_rx='"(done|status|state|task_status)"[[:space:]]*:[[:space:]]*"?(true|DONE|done|complete|completed|COMPLETE)"?|(status|state)[[:space:]]*:[[:space:]]*(DONE|COMPLETE)|(done|complete)[[:space:]]*:[[:space:]]*true|TASK_COMPLETE'
printf '%s' "$norm" | grep -Eq "$claim_rx" || exit 0

# 2) Proposal, not commit? The model's sanctioned path passes untouched.
if printf '%s' "$norm" | grep -Eq '"?(proposed|proposal)"?[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

# 3) Which run is claiming? Sanitize to regex-safe chars.
sid="$(printf '%s' "$norm" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1 | tr -cd 'A-Za-z0-9._-')"

ledger="${RIG_WM_LEDGER:-$HOME/.rig/wm/ledger.jsonl}"

verified=0
if [ -f "$ledger" ]; then
  # Candidate rows: receipt id + observation + session match (payload session or "*").
  # A row with no evidence key never enters this set's pass path (synthetic below).
  rows="$(grep -E '"receipt"[[:space:]]*:[[:space:]]*"[^"]+"' "$ledger" 2>/dev/null \
    | grep -E '"observation"[[:space:]]*:[[:space:]]*"[^"]+"' \
    | grep -E "\"session_id\"[[:space:]]*:[[:space:]]*\"($sid|\*)\"" || true)"
  if [ -n "$rows" ]; then
    evs="$(printf '%s\n' "$rows" | sed -n 's/.*"evidence"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
    while IFS= read -r ev; do
      [ -n "$ev" ] || continue
      if [ -e "$ev" ]; then verified=1; break; fi
    done <<< "$evs"
  fi
fi

if [ "$verified" -eq 1 ]; then
  exit 0
fi

{
  echo "wm-commit-gate: BLOCKED — completion claim with no observation-backed receipt row (session '${sid:-<none>}')."
  echo "  ledger: $ledger"
  echo "  A DONE write requires a harness-committed row:"
  echo "  {\"session_id\":\"<run>\",\"receipt\":\"r-<n>\",\"observation\":\"<what the environment showed>\",\"evidence\":\"<path that exists and proves it>\"}"
  echo "  Model-facing path: write the state change as a proposal (\"proposed\": true) and let the checker commit it on real observation."
} >&2
exit 2
