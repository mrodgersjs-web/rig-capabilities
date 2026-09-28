#!/bin/sh
# outcome: code-engineering: App Studio META hook - one PreToolUse (Bash) entry point that runs every App Studio sub-hook on the same payload and returns the strictest verdict
# done_when: cmd:python3 capabilities/skills/app-studio/scripts/hook_cases.py app-studio-hook.sh
# quality_floor: 0.7
# rig app-studio-hook - META dispatcher for the App Studio hook tier.
# Canonical source: rig-capabilities repo. DORMANT until Mike wires it into a harness
# settings file (one PreToolUse entry with matcher Bash pointing at this script).
# Sub-hooks (each decides its own applicability):
#   app-native-binary-preflight.sh  App Studio projects only (.app-studio/ present)
#   app-single-builder-guard.sh     App Studio projects only
#   app-env-commit-guard.sh         any git repo
# Exit: the highest sub-hook code (0 proceed, 2 blocked; stderr goes back to the agent).
# APP_STUDIO_HOOKS=0 turns the whole tier off. A missing sub-hook is reported, never
# silently treated as a pass.
set -u
[ "${APP_STUDIO_HOOKS:-1}" = "0" ] && exit 0
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0
here=$(cd "$(dirname "$0")" && pwd)
worst=0
for sub in app-native-binary-preflight.sh app-single-builder-guard.sh app-env-commit-guard.sh; do
  if [ ! -f "$here/$sub" ]; then
    echo "app-studio-hook: sub-hook $sub missing - tier NOT fully applied" >&2
    continue
  fi
  printf '%s' "$payload" | sh "$here/$sub"
  rc=$?
  [ "$rc" -gt "$worst" ] && worst=$rc
done
exit "$worst"
