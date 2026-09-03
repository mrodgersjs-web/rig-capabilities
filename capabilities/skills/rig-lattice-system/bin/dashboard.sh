#!/usr/bin/env bash
# dashboard.sh — start the RIG Deviator dashboard.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${RIG_DV_DASHBOARD_PORT:-8088}"
HOST="${RIG_DV_DASHBOARD_HOST:-127.0.0.1}"

echo "Starting RIG Deviator™ dashboard at http://$HOST:$PORT"
echo "(set RIG_DV_DASHBOARD_HOST=0.0.0.0 to expose on LAN)"
exec python3 -m dashboard
