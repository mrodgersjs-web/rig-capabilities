"""Adapter binding for the github-ultraplan acceptance runner worker."""

from __future__ import annotations

from github_ultraplan_build_worker import finish, run_stage, stage


def execute() -> int:
    label = stage("acceptance")
    status = run_stage(label)
    return finish(status)
