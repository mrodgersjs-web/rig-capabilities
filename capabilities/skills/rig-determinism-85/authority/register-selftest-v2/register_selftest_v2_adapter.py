"""Adapter binding for the pure-computation selftest v2 (see worker docstring)."""

from __future__ import annotations

from register_selftest_v2_worker import finish, run_stage


def execute() -> int:
    label = run_stage("register-selftest-v2")
    return finish(label)
