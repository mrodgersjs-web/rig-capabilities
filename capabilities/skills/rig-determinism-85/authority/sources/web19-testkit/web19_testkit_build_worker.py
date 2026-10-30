"""web19-testkit build worker: runs the verification pipeline stage by stage.

One deterministic stage set: the rig-e2e smoke run, the deterministic
measurement/price/calc checker, and the DONE.txt done-test, each as a single
subprocess effect returning its exit code. Zero conditionals anywhere; the
loader never executes these bytes. Module grammar: imports, docstring, functions only.
"""

from __future__ import annotations

import subprocess


def run_smoke() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/Developer/rig-website/candidates/v19-polish && /Users/rig128gb/.rig/bin/rig-e2e smoke http://127.0.0.1:4520/client-intake-test-kit.html"])
    return status


def run_checks() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "python3 /Users/rig128gb/Developer/rig-website/candidates/v19-polish/_re/v19/testkit/check_all.py"])
    return status


def run_done_test() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "head -1 /Users/rig128gb/rig-builds/web19-testkit/DONE.txt | grep -q \'^DONE PASS\'"])
    return status


def close(smoke: int, checks: int, done_test: int) -> int:
    return max(smoke, checks, done_test)
