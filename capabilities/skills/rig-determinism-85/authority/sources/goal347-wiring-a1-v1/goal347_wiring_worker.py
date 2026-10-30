"""Immutable D85 boundary for the goal-347 daily wiring probe (launchd-owned).

Inventory inspects this boundary statically; registration never invokes it. The
daily trigger runs exactly one argv command; all probe logic lives outside this
boundary in bin/wiring_probe.py (verified separately by run evidence).
"""

import subprocess


def run_wiring_check():
    return subprocess.call([
        "/bin/bash",
        "/Users/rig128gb/.rig/goals/347-harnesses-and-loops-for-aside-browser-benchm/bin/wiring-daily.sh",
    ])
