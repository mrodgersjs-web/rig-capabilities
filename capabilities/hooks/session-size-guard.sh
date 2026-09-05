#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when: cmd:python3 scripts/hook_fires.py session-size-guard.sh
# great_example: examples/great/agent-engineering/session-size-guard.md
# quality_floor: 0.6
# session-size-guard.sh — PostToolUse guardrail (non-blocking).
#
# Warns when the LIVE Claude transcript crosses grounded size tiers, enforcing the
# Context-Health doctrine (checkpoint by ~50-60%) automatically instead of relying
# on the model to remember.
#
# Tiers grounded in the AgentForge coach audit (2026-07-19): sessions in this
# environment START ~0.5MB from the doctrine preamble, so a 500KB threshold is pure
# noise. The actionable mega-tail from the audit was 2MB (checkpoint soon) and 5MB+
# (checkpoint + fresh session now; the audit found 11 sessions >5MB, largest 27MB).
#
# Built by Jake, 2026-07-19, from the ai-coach-check finding "109 mega-sessions".
set -uo pipefail

payload="$(cat)"

# Extract transcript_path with pure sed — no jq/python dependency, so it survives a
# minimal hook-execution PATH. A filesystem path never contains an escaped quote.
tp="$(printf '%s' "$payload" | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
if [ -z "$tp" ]; then
  sid="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  [ -n "$sid" ] && tp="$(find "$HOME/.claude/projects" -name "${sid}.jsonl" -type f 2>/dev/null | head -1)"
fi
[ -n "$tp" ] && [ -f "$tp" ] || exit 0

bytes="$(stat -f '%z' "$tp" 2>/dev/null || stat -c '%s' "$tp" 2>/dev/null || echo 0)"
mb=$(( bytes / 1048576 ))

tier=0
if   [ "$bytes" -ge 5242880 ]; then tier=5   # 5 MiB
elif [ "$bytes" -ge 2097152 ]; then tier=2   # 2 MiB
fi
[ "$tier" -gt 0 ] || exit 0

# Throttle: warn at most once per tier per session (so it doesn't spam every tool).
marker="${TMPDIR:-/tmp}/claude-sessguard-$(basename "$tp").tier"
last=0; [ -f "$marker" ] && last="$(cat "$marker" 2>/dev/null || echo 0)"
[ "$tier" -gt "$last" ] || exit 0
printf '%s' "$tier" > "$marker" 2>/dev/null || true

if [ "$tier" -ge 5 ]; then
  msg="🔴 Session transcript ${mb}MB (>5MB). Context-Health doctrine: checkpoint (HANDOFF / obsidian-bridge) and start a FRESH session NOW — decisions degrade past this point."
else
  msg="🟠 Session transcript ${mb}MB (>2MB). Checkpoint soon and plan a fresh session before it snowballs (mega-sessions were the coach audit's top finding)."
fi

esc="$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf '{"systemMessage":"%s","suppressOutput":true}\n' "$esc"
exit 0
