"""Adapter binding for the web19-github storefront build worker."""

from __future__ import annotations

from web19_github_build_worker import close, run_deslop, run_done_test, run_e2e, run_sweep


def execute() -> int:
    exit_sweep = run_sweep()
    exit_e2e = run_e2e()
    exit_deslop = run_deslop()
    exit_done = run_done_test()
    return close(exit_sweep, exit_e2e, exit_deslop, exit_done)
