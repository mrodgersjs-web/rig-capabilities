#!/usr/bin/env bash
# daemon-rotate-logs.sh — rotate the RIG Deviator daemon logs.
# Keeps 7 days of logs; older logs are gzipped and removed after 30 days.
set -euo pipefail

LOG_DIR="${RIG_DV_LOG_DIR:-/tmp}"
PREFIX="rig-deviator-daemon"

cd "$LOG_DIR"

# Compress logs older than 1 day that haven't been compressed yet
find . -maxdepth 1 -name "${PREFIX}*.log" -type f -mtime +1 \
    ! -name "*.gz" -exec gzip {} \; 2>/dev/null || true

# Delete compressed logs older than 30 days
find . -maxdepth 1 -name "${PREFIX}*.log.gz" -type f -mtime +30 \
    -exec rm -f {} \; 2>/dev/null || true

echo "rotated logs in $LOG_DIR (prefix=$PREFIX)"
