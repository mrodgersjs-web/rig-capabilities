#!/usr/bin/env bash
# daemon-status.sh — pretty-print current daemon status from launchctl.
set -euo pipefail

LABEL="com.rig.deviator.daemon"

echo "── launchctl ─────────────────────────────────────────────────────"
if launchctl list 2>/dev/null | grep -q "$LABEL"; then
    launchctl list "$LABEL" 2>/dev/null | head -20
    echo ""
    echo "✓ daemon registered with launchd"
else
    echo "✗ daemon NOT loaded — run: launchctl load ~/Library/LaunchAgents/${LABEL}.plist"
fi

echo ""
echo "── recent log ─────────────────────────────────────────────────────"
LOG_DIR="${RIG_DV_LOG_DIR:-/tmp}"
LATEST_LOG="$LOG_DIR/rig-deviator-daemon.log"
if [ -f "$LATEST_LOG" ]; then
    tail -20 "$LATEST_LOG"
else
    echo "(no log file yet at $LATEST_LOG)"
fi

echo ""
echo "── slot health ────────────────────────────────────────────────────"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -c "
import sys; sys.path.insert(0, '$ROOT')
from enterprise.daemon import Daemon
import json
d = Daemon()
print(json.dumps(d.status(), indent=2, default=str))
" 2>&1 | head -80
