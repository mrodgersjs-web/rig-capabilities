"""Immutable D85 boundary for the Temporal-owned nightly cockpit refresh.

Inventory inspects this boundary statically; registration never invokes it. The
isolated runtime installer separately copies and hash-verifies the workflow,
activity, shell transaction, scraper, validation, and provider-write sources.
"""

import subprocess


def run_refresh(scheduled_at):
    return subprocess.call([
        "/usr/bin/env",
        "PYTHONPATH=/Users/rig128gb/.rig/cockpit-nightly-v1",
        "/Users/rig128gb/.rig/meta-harness/.venv/bin/python",
        "-m",
        "automation.cockpit_refresh",
        "--runtime-root",
        "/Users/rig128gb/.rig/cockpit-nightly-v1",
        "run-once",
        "--scheduled-at",
        scheduled_at,
    ])
