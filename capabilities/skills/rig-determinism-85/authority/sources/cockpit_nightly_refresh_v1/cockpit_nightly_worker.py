"""Immutable D85 boundary for the Temporal-owned nightly cockpit refresh.

Inventory inspects this boundary statically; registration never invokes it. The
isolated runtime installer separately copies and hash-verifies the workflow,
activity, shell transaction, scraper, validation, and provider-write sources.
"""

import subprocess


TEMPORAL_PYTHON = "/Users/rig128gb/.rig/meta-harness/.venv/bin/python"


def run_refresh(runtime_root, scheduled_at):
    return subprocess.call([
        "/usr/bin/env",
        "PYTHONPATH=" + runtime_root,
        TEMPORAL_PYTHON,
        "-m",
        "automation.cockpit_refresh",
        "--runtime-root",
        runtime_root,
        "run-once",
        "--scheduled-at",
        scheduled_at,
    ])
