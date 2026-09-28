#!/bin/sh
# outcome: code-engineering: App Studio SUB hook - blocks a second build while .app-studio/build.lock is held, so a watcher routine and an agent can never race the same .next or build folder
# done_when: cmd:python3 capabilities/skills/app-studio/scripts/hook_cases.py app-single-builder-guard.sh
# quality_floor: 0.7
# rig app-single-builder-guard - PreToolUse (Bash) guard for App Studio projects.
# Canonical source: rig-capabilities repo. Parent: app-studio-hook.sh. DORMANT until wired.
# Lesson LA-03 (memory/episodic/2026-09-26.md#L122): six competing builders (a watcher
# routine building on every wake plus the agent) produced PageNotFoundError and ENOENT
# renames in .next. The sanctioned detached pattern (app-sandbox-survival rule 3) checks
# and takes the lock itself, so a command mentioning build.lock passes. A lock older than
# APP_BUILD_LOCK_TTL seconds (default 1800) is treated as stale and allowed with a warning.
set -u
APP_HOOK_PAYLOAD=$(cat 2>/dev/null || true)
export APP_HOOK_PAYLOAD
[ -n "$APP_HOOK_PAYLOAD" ] || exit 0
# A caller's PYTHONHOME or PYTHONPATH (the Aside runtime exports one) breaks the system python.
unset PYTHONHOME PYTHONPATH
exec /usr/bin/python3 - <<'PY'
import json, os, re, sys, time
from pathlib import Path
try:
    d = json.loads(os.environ.get("APP_HOOK_PAYLOAD", ""))
except Exception:
    sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command") or "")
build = re.compile(r"\b((npm|pnpm|yarn|bun)\s+(run\s+)?build|next\s+build|flutter\s+build|xcodebuild|eas\s+build\s+--local|gradlew?\s+assemble)")
if not cmd or not build.search(cmd) or "build.lock" in cmd:
    sys.exit(0)
cwd = Path(d.get("cwd") or os.getcwd())
root = next((p for p in [cwd, *cwd.parents] if (p / ".app-studio").is_dir()), None)
if root is None:
    sys.exit(0)
lock = root / ".app-studio" / "build.lock"
if not lock.exists():
    sys.exit(0)
age = time.time() - lock.stat().st_mtime
ttl = float(os.environ.get("APP_BUILD_LOCK_TTL", "1800"))
if age < ttl:
    sys.stderr.write("app-studio single-builder guard BLOCKED (lesson LA-03): .app-studio/build.lock is held"
                     " (age %ds). Another builder is running: poll .app-studio/build.log, or prove the lock"
                     " stale with lsof -t .app-studio/build.log before removing it.\n" % int(age))
    sys.exit(2)
sys.stderr.write("app-studio single-builder guard: stale build.lock (age %ds) ignored\n" % int(age))
sys.exit(0)
PY
