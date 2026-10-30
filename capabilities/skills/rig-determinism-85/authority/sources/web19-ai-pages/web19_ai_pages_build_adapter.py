"""Adapter binding for the web19-ai-pages build worker."""

from __future__ import annotations

from web19_ai_pages_build_worker import close, run_checks, run_done_test, run_smoke


def execute() -> int:
    exit_smoke = run_smoke()
    exit_checks = run_checks()
    exit_done = run_done_test()
    return close(exit_smoke, exit_checks, exit_done)
