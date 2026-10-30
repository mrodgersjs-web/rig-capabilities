#!/usr/bin/env python3
"""Console build probe (goal 347): repo is checked out at GitHub head AND a
real build artifact exists. Red on drift (upstream moved) or missing build.

Usage: console_build_probe.py <owner/name> <local-path> <artifact-file>
"""
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo, local, artifact = sys.argv[1], Path(sys.argv[2]).expanduser(), Path(sys.argv[3])
    head = subprocess.run(["git", "-C", str(local), "rev-parse", "HEAD"],
                          capture_output=True, text=True, timeout=30)
    if head.returncode != 0:
        print(f"{repo}: no local git head", file=sys.stderr)
        return 1
    remote = subprocess.run(["gh", "api", f"repos/{repo}/commits", "--jq", ".[0].sha"],
                            capture_output=True, text=True, timeout=60)
    if remote.returncode != 0:
        print(f"{repo}: gh api failed: {remote.stderr[:120]}", file=sys.stderr)
        return 1
    built = (local / artifact)
    if not built.exists():
        print(f"{repo}: build artifact missing: {built}", file=sys.stderr)
        return 1
    local_sha, remote_sha = head.stdout.strip(), remote.stdout.strip()
    if local_sha != remote_sha:
        print(f"{repo}: drift local {local_sha[:8]} != remote {remote_sha[:8]}",
              file=sys.stderr)
        return 1
    print(f"{repo} head={local_sha[:12]} built={built.name} ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
