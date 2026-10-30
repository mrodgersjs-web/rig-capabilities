"""Adapter binding for the web19-polish buildout verification worker."""

from __future__ import annotations

from web19_polish_buildout_worker import (
    close,
    run_axe,
    run_claim_lint,
    run_deslop,
    run_done_test,
    run_e2e,
    run_extract,
    run_outward,
    run_struct,
    run_transform,
)


def execute() -> int:
    exit_transform = run_transform()
    exit_struct = run_struct()
    exit_extract = run_extract()
    exit_deslop = run_deslop()
    exit_outward = run_outward()
    exit_claim = run_claim_lint()
    exit_e2e = run_e2e()
    exit_axe = run_axe()
    exit_done = run_done_test()
    return close(
        exit_transform,
        exit_struct,
        exit_extract,
        exit_deslop,
        exit_outward,
        exit_claim,
        exit_e2e,
        exit_axe,
        exit_done,
    )
