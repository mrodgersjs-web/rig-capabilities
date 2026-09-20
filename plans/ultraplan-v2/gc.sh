#!/usr/bin/env bash
# gc.sh -- gate-checked commit. Runs the test command FIRST; a nonzero exit
# refuses to commit. Born from three red commits this session, all caused by
# `test && commit` chains whose test result was masked or reordered.
# Usage: gc.sh <repo> <test-command...> -- <git-args...>
set -euo pipefail
REPO="$1"; shift
TESTS=(); while [ $# -gt 0 ] && [ "$1" != "--" ]; do TESTS+=("$1"); shift; done
[ "${1:-}" = "--" ] && shift
cd "$REPO"
echo "== gate: ${TESTS[*]}"
if ! "${TESTS[@]}"; then
  echo "gc: REFUSED -- test gate red, nothing committed"; exit 1
fi
git add -A -- ':!.local-runs'
git -c user.name="rig128gb" -c user.email="mike@mrodgers.tech" commit "$@"
