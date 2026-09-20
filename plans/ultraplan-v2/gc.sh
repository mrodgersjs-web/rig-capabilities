#!/usr/bin/env bash
# gc.sh -- gate-checked commit. Runs the test command FIRST; nonzero exit refuses.
# Stages ONLY the paths named after `--staged` (explicit, no -A: the exclusion
# variant already land-grabbed 1575 foreign paths once).
# Usage: gc.sh <repo> <test-command...> --staged <path...> -- <git-args...>
set -euo pipefail
REPO="$1"; shift
TESTS=(); while [ $# -gt 0 ] && [ "$1" != "--staged" ] && [ "$1" != "--" ]; do TESTS+=("$1"); shift; done
STAGED=()
if [ "${1:-}" = "--staged" ]; then shift; while [ $# -gt 0 ] && [ "$1" != "--" ]; do STAGED+=("$1"); shift; done; fi
[ "${1:-}" = "--" ] && shift
cd "$REPO"
echo "== gate: ${TESTS[*]}"
if ! "${TESTS[@]}"; then
  echo "gc: REFUSED -- test gate red, nothing committed"; exit 1
fi
if [ ${#STAGED[@]} -eq 0 ]; then
  echo "gc: REFUSED -- no explicit --staged paths; refusing to guess (the -A land-grab lesson)"; exit 1
fi
git add -- "${STAGED[@]}"
git -c user.name="rig128gb" -c user.email="mike@mrodgers.tech" commit "$@"
