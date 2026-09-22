"""Adapter exposing the immutable nightly cockpit refresh boundary (v2)."""

from cockpit_nightly_worker import run_refresh


def execute(runtime_root, scheduled_at):
    return run_refresh(runtime_root, scheduled_at)
