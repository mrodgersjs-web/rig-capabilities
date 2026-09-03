#!/usr/bin/env bash
# daemon-install.sh — register the RIG Deviator daemon with launchd.
#
# Usage:
#   bin/daemon-install.sh           # install + load
#   bin/daemon-install.sh uninstall # unload + remove
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LA_DIR="$HOME/Library/LaunchAgents"

DAEMON_PLIST="$ROOT/deploy/launchd/com.rig.deviator.daemon.plist"
ROTATE_PLIST="$ROOT/deploy/launchd/com.rig.deviator.daemon.rotate.plist"

DAEMON_INSTALLED="$LA_DIR/com.rig.deviator.daemon.plist"
ROTATE_INSTALLED="$LA_DIR/com.rig.deviator.daemon.rotate.plist"

ACTION="${1:-install}"

if [ "$ACTION" = "uninstall" ]; then
    echo "Unloading daemon plists..."
    launchctl unload "$DAEMON_INSTALLED" 2>/dev/null || true
    launchctl unload "$ROTATE_INSTALLED" 2>/dev/null || true
    rm -f "$DAEMON_INSTALLED" "$ROTATE_INSTALLED"
    echo "✓ uninstalled"
    exit 0
fi

# Install
mkdir -p "$LA_DIR"
cp "$DAEMON_PLIST" "$DAEMON_INSTALLED"
cp "$ROTATE_PLIST" "$ROTATE_INSTALLED"

# Ensure scripts are executable
chmod +x "$ROOT/bin/daemon-start.sh" "$ROOT/bin/daemon-rotate-logs.sh" \
         "$ROOT/bin/daemon-status.sh" "$ROOT/bin/repo-sentinel-check.sh"

# Reload (unload first in case of update)
launchctl unload "$DAEMON_INSTALLED" 2>/dev/null || true
launchctl unload "$ROTATE_INSTALLED" 2>/dev/null || true
launchctl load "$DAEMON_INSTALLED"
launchctl load "$ROTATE_INSTALLED"

echo "✓ installed + loaded:"
echo "  $DAEMON_INSTALLED"
echo "  $ROTATE_INSTALLED"
echo ""
echo "Verify with: bin/daemon-status.sh"
