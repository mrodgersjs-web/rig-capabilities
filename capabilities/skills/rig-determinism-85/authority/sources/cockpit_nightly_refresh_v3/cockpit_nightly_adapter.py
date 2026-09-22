"""Adapter exposing the immutable nightly cockpit refresh boundary (v3)."""

from cockpit_nightly_worker import run_refresh


def execute(scheduled_at):
    return run_refresh(scheduled_at)
