"""D85 boundary worker for the job-plays build.

The certifiable boundary is the deterministic done-test pipeline, not the
generators themselves: jobplays.py carries module-level assignments that sit
outside the closed D85 module grammar, so it is reached as an effect, not
imported. Each stage is one subprocess effect returning its exit code; the
verdict is the deterministic max of those exit codes. Zero conditionals.

Stages:
  1. check.py  - the quality gate over every real job-play draft.
  2. verify.py - the done-test: CLI surface, sample artifacts, receipt rule,
                 planted-bad rejection, Jev text gate (ledger-scored) and the
                 Jev image gate with its known-bad control.
  3. done test - DONE.txt first line is DONE PASS.

The model-assisted card/dossier drafting path (modelsec.py) is deliberately
OUTSIDE this boundary: it is not part of the done-test, so no MODEL operation
is declared here. Its drafts are still gated by check.py and the Jev text
gate.
"""

from __future__ import annotations

import subprocess


def run_check() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/rig-builds/job-plays && python3 check.py /Users/rig128gb/.applypilot/job-plays"])
    return status


def run_verify() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "cd /Users/rig128gb/rig-builds/job-plays && python3 verify.py"])
    return status


def run_done_test() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "head -1 /Users/rig128gb/rig-builds/job-plays/DONE.txt | grep -q '^DONE PASS'"])
    return status


def close(check: int, verify: int, done_test: int) -> int:
    return max(check, verify, done_test)
