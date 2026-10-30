#!/usr/bin/env python3
"""D85-registered entry for the Jev ten-level estate verifier.

Runs the 300-case live suite through usages/verify.py and returns its exit
code. The deterministic verifier is verify.py itself (same directory); this
module is the closed-grammar registration surface for the D85 process
jev_ten_level_estate_v5: imports + function definitions only, closed
expression grammar (no kwargs, no attribute access).
"""
import subprocess


def main():
    """Run the full suite; exit 0 only when every case clears p>=0.90."""
    runner = "/usr/bin/python3"
    script = "/Users/rig128gb/Developer/ten-levels-of-jev/usages/verify.py"
    return subprocess.call([runner, script])
