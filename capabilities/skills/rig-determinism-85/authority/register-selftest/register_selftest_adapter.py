"""Adapter binding for the register_process.py loader-compat selftest.

The registered entrypoint: the operator drives execute(); execution reaches
the worker's run_stage/finish. Synthetic selftest asset — see
register_selftest_worker.py for scope.
"""

from __future__ import annotations

from register_selftest_worker import finish, run_stage


def execute() -> int:
    status = run_stage("register-selftest")
    return finish(status)
