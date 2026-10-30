"""Adapter exposing the goal-347 daily wiring-probe boundary (A1 deterministic lane)."""

from goal347_wiring_worker import run_wiring_check


def execute():
    return run_wiring_check()
