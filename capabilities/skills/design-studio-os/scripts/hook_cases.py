#!/usr/bin/env python3
"""Thin wrapper: the Design Studio OS gates are authored and run in the studio meta repo
(`~/Developer/rig-design-studio-os/tools/hook_cases.py`); this keeps a repo-relative done_when working from
rig-capabilities. Fails loudly when the studio repo is absent."""
import os, subprocess, sys
from pathlib import Path
root = Path(os.environ.get("DS_STUDIO_ROOT", str(Path.home() / "Developer/rig-design-studio-os")))
target = root / "tools" / "hook_cases.py"
if not target.exists():
    print(f"BLOCKED: studio repo not found at {root}; set DS_STUDIO_ROOT. Not a pass.", file=sys.stderr)
    sys.exit(1)
sys.exit(subprocess.run([sys.executable, str(target), *sys.argv[1:]]).returncode)
