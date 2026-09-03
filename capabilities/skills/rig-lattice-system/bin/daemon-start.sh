#!/usr/bin/env bash
# daemon-start.sh — start the RIG Deviator daemon foreground (used by launchd).
#
# Reads the canonical 9-slot Daemon from enterprise.daemon and runs it
# under PID 1 of the launchd job, logging to /tmp/rig-deviator-daemon-*.log.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Sentinel guard
if [ ! -f "$ROOT/REPO_GUARD.md" ]; then
    echo "ERROR: REPO_GUARD.md missing — refusing to start daemon"
    exit 1
fi

# Use repo-local venv if present, else system python3
PYTHON="${RIG_DV_PYTHON:-python3}"
if [ -x "$ROOT/.venv/bin/python" ]; then
    PYTHON="$ROOT/.venv/bin/python"
fi

# Log dir
LOG_DIR="${RIG_DV_LOG_DIR:-/tmp}"
mkdir -p "$LOG_DIR"

# Tick interval — daemon tick loop sleep (seconds)
TICK_INTERVAL="${RIG_DV_TICK_INTERVAL:-5}"

# Daemon entrypoint
exec "$PYTHON" -c "
import sys
sys.path.insert(0, '$ROOT')
from enterprise.daemon import Daemon
import json, time, signal

print(f'[daemon] starting at {time.strftime(\"%Y-%m-%dT%H:%M:%SZ\", time.gmtime())}', flush=True)
d = Daemon()
print(f'[daemon] {len(d.slots)} slots registered:', [s.name for s in d.slots], flush=True)

stopped = False
def _stop(sig, frame):
    global stopped
    stopped = True
    print(f'[daemon] received signal {sig}, stopping', flush=True)

signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)

while not stopped:
    executed = d.tick()
    if executed:
        for r in executed:
            print(f'[daemon] {r[\"slot\"]} state={r[\"state\"]} elapsed_ms={r[\"elapsed_ms\"]}', flush=True)
    time.sleep($TICK_INTERVAL)

print(f'[daemon] stopped cleanly', flush=True)
"
