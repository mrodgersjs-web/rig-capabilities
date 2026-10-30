"""Adapter binding for the job-plays done-test build worker."""

from __future__ import annotations

from job_plays_worker import close, run_check, run_done_test, run_verify


def execute() -> int:
    exit_check = run_check()
    exit_verify = run_verify()
    exit_done = run_done_test()
    return close(exit_check, exit_verify, exit_done)
