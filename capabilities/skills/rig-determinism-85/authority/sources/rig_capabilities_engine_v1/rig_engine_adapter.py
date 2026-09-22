"""Adapter exposing the rig_capabilities engine registration operation (v1)."""

from rig_engine_worker import run_engine


def execute(job):
    return run_engine(job)
