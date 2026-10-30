#!/usr/bin/env python3
"""D85-registered entry for the Jev ten-level estate verifier.

Runs the 300-case live suite through usages/verify.py and returns its exit
code. The deterministic verifier is verify.py itself (same directory); this
module is the closed-grammar registration surface for the D85 process
jev_ten_level_estate_v1: literal constants + function definitions only.
"""
import os
import subprocess

HERE = "/Users/rig128gb/Developer/ten-levels-of-jev/usages"
RUNNER = "/usr/bin/python3"
SCRIPT = "/Users/rig128gb/Developer/ten-levels-of-jev/usages/verify.py"
EVIDENCE = "/Users/rig128gb/Developer/ten-levels-of-jev/usages/verify-results.json"


def main():
    """Run the full suite; exit 0 only when every case clears p>=0.90."""
    r = subprocess.run([RUNNER, SCRIPT], cwd=HERE, timeout=1200)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
