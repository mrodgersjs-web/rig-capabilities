#!/usr/bin/env bash
# repo-sentinel-check.sh — verify REPO_GUARD.md is present before any
# destructive operation in this tree.
#
# Usage:
#   bin/repo-sentinel-check.sh           # exit 0 if guard present, 1 if missing
#   bin/repo-sentinel-check.sh --quiet   # silent mode for scripts
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARD="$ROOT/REPO_GUARD.md"
QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

if [ ! -f "$GUARD" ]; then
    [ "$QUIET" = "0" ] && echo "ERROR: REPO_GUARD.md missing at $ROOT — refusing to proceed"
    exit 1
fi

[ "$QUIET" = "0" ] && echo "OK: REPO_GUARD.md present at $ROOT"
exit 0
