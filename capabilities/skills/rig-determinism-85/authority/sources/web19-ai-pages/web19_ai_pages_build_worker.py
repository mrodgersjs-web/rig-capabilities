"""web19-ai-pages build worker: runs the verification pipeline stage by stage.

One deterministic stage set: the four rig-e2e smoke runs, the JSON-LD/price/sitemap
checker, and the DONE.txt done-test, each as a single subprocess effect returning
its exit code. Zero conditionals anywhere; the loader never executes these bytes.
Module grammar: imports, docstring, functions only.
"""

from __future__ import annotations

import subprocess


def run_smoke() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/Developer/rig-website/candidates/v19-polish && for s in who-is-a-fractional-chief-ai-officer-in-denver who-builds-governed-ai-agents-for-healthcare-operations who-helps-with-ai-governance-for-regulated-industries-in-denver who-is-mike-rodgers-rodgers-intelligence-group; do /Users/rig128gb/.rig/bin/rig-e2e smoke http://127.0.0.1:4520/$s || exit 1; done"])
    return status


def run_checks() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "python3 /Users/rig128gb/Developer/rig-website/candidates/v19-polish/_re/v19/ai-pages/check_all.py"])
    return status


def run_done_test() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "head -1 /Users/rig128gb/rig-builds/web19-ai-pages/DONE.txt | grep -q \'^DONE PASS\'"])
    return status


def close(smoke: int, checks: int, done_test: int) -> int:
    return max(smoke, checks, done_test)
