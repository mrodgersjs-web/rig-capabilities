"""web19-github storefront build worker: runs the verification pipeline stage by stage.

One deterministic stage set: the frame sweep, the rig-e2e smoke run, the SlopMonster deslop
check, and the DONE.txt done-test, each as a single subprocess effect returning its exit code.
Zero conditionals anywhere; the loader never executes these bytes.
Module grammar: imports, docstring, functions only.
"""

from __future__ import annotations

import subprocess


def run_sweep() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/Developer/rig-website/candidates/v19-polish && node _re/v19/github/sweep.cjs"])
    return status


def run_e2e() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/Developer/rig-website/candidates/v19-polish && /Users/rig128gb/.rig/bin/rig-e2e smoke http://127.0.0.1:4520/github-repos"])
    return status


def run_deslop() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/Developer/rig-website/candidates/v19-polish && python3 /Users/rig128gb/Developer/SlopMonster/tools/deslop.py github-repos.html"])
    return status


def run_done_test() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "head -1 /Users/rig128gb/rig-builds/web19-github/DONE.txt | grep -q '^DONE PASS'"])
    return status


def close(sweep: int, e2e: int, deslop: int, done_test: int) -> int:
    return max(sweep, e2e, deslop, done_test)
