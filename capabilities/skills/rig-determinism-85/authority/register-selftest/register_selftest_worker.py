"""Deterministic selftest worker for register_process.py (synthetic loader-compat asset).

This driver exists ONLY to prove that register_process.py emits records the
existing D85 loader accepts unchanged (inventory exits 0 with a non-empty
operation inventory). It earns no work credit for any estate process; the
estate and build-standard processes are registered from their real bytes and
their real verdicts (pass or block) are recorded verbatim in
runs/agentic-stack-buildout/d85/. Grammar per the julie_synthetic /
cockpit_v2_vercel_deploy_v1 precedent: one subprocess.call, no conditionals
around effects, no exception handling, no dynamic dispatch — the loader
statically analyzes these bytes and never executes them.
"""

from __future__ import annotations

import subprocess

RUN_ID = "register-selftest"


def stage(name: str) -> str:
    return "selftest:" + name + ":" + RUN_ID


def run_stage(name: str) -> int:
    status = subprocess.call(["/bin/echo", stage(name)])
    return status


def finish(status: int) -> int:
    if status != 0:
        return 1
    return 0
