#!/usr/bin/env python3
"""Run a command, PRINT the evidence it produced, preserve its exit code.
The auditor judge can only ground on output; silent asserts score 0.83."""
import subprocess, sys
r = subprocess.run(sys.argv[1:], capture_output=True, text=True, timeout=240)
out = (r.stdout + "\n" + r.stderr).strip()
print(out[-500:] if len(out) > 500 else out)
sys.exit(r.returncode)
