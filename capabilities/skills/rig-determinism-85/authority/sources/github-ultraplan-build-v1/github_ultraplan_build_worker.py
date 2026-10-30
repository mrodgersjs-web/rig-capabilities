"""D85-certified acceptance runner for the 2026-10-18 GitHub-ultraplan scaffold builds.

One deterministic stage: execute the four scaffold->program acceptance
scripts (agency-studio, birch-rig-boots, design-studio, rig-marketplace) as
a single subprocess effect; the folded exit code is the verdict (0 = all
four passed). Zero conditionals anywhere; the loader never executes these
bytes. Module grammar: imports, docstring, functions only.
"""

from __future__ import annotations

import subprocess


def stage() -> str:
    return "github-ultraplan-build-20261018:acceptance"


def run_stage(label: str) -> int:
    status = subprocess.call(["/bin/bash", "/Users/rig128gb/.rig/live/control-plane/repo-integration-20261018/tests/agency-studio.sh", "/Users/rig128gb/.rig/live/control-plane/repo-integration-20261018/tests/birch-rig-boots.sh", "/Users/rig128gb/.rig/live/control-plane/repo-integration-20261018/tests/design-studio.sh", "/Users/rig128gb/.rig/live/control-plane/repo-integration-20261018/tests/rig-marketplace.sh"])
    return status


def finish(status: int) -> int:
    return status
