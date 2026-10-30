#!/usr/bin/env python3
"""Freshness sensor (goal 347): pull the repo's live head/release, compare to
last seen, store state, exit 0 when the surface answers. A wired tracking
check, not a git clone: the probe proves gh-api reach + our state file moves.

Usage: freshness_sensor.py <owner/name> [releases]   (default: commits)
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE = Path.home() / ".rig/state/goal347-sensors"


def main() -> int:
    repo = sys.argv[1]
    kind = sys.argv[2] if len(sys.argv) > 2 else "commits"
    STATE.mkdir(parents=True, exist_ok=True)
    if kind == "releases":
        cmd = ["gh", "api", f"repos/{repo}/releases/latest",
               "--jq", ".tag_name"]
    else:
        cmd = ["gh", "api", f"repos/{repo}/commits", "--jq", ".[0].sha"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f"sensor {repo}: exec error {e}", file=sys.stderr)
        return 1
    if out.returncode != 0 or not out.stdout.strip():
        print(f"sensor {repo}: gh api rc={out.returncode} "
              f"{out.stderr.strip()[:120]}", file=sys.stderr)
        return 1
    value = out.stdout.strip()
    f = STATE / (repo.replace("/", "__") + ".json")
    prev = json.loads(f.read_text()) if f.exists() else {}
    f.write_text(json.dumps({
        "repo": repo, "kind": kind, "seen": value,
        "changed": prev.get("seen") != value if prev else None,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }))
    print(f"{repo} {kind} {value[:12]} "
          f"{'CHANGED' if prev and prev.get('seen') != value else 'ok'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
