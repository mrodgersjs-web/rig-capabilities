"""web19-polish buildout worker: runs the 9-page build-and-verify pipeline stage by stage.

One deterministic stage set: regenerate the pages, structural fail-closed check, text extraction,
SlopMonster deslop, the outward-gate chain, claim-lint, rig-e2e smoke, axe, and the DONE.txt
done-test, each as a single subprocess effect returning its exit code. Zero conditionals
anywhere; the loader never executes these bytes.
Module grammar: imports, docstring, functions only.
"""

from __future__ import annotations

import subprocess


def run_transform() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "python3 /Users/rig128gb/rig-builds/rig-sites-buildout/gen/transform.py"])
    return status


def run_struct() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "python3 /Users/rig128gb/rig-builds/rig-sites-buildout/gen/d85_struct.py"])
    return status


def run_extract() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "python3 /Users/rig128gb/rig-builds/rig-sites-buildout/gen/extract_txt.py"])
    return status


def run_deslop() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "for p in client-intake-automation one-workflow-review ai-packages professional-ai-packages rig-desk private-ai agent-governance website-design offerings; do python3 /Users/rig128gb/Developer/SlopMonster/tools/deslop.py /tmp/v/txt/$p.txt > /dev/null || exit 1; done"])
    return status


def run_outward() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "for p in client-intake-automation one-workflow-review ai-packages professional-ai-packages rig-desk private-ai agent-governance website-design offerings; do python3 /Users/rig128gb/.aside/u/0/skill-library/outward-gate/scripts/gate.py run --file /tmp/v/txt/$p.txt --label \"v19 buildout page $p\" --jev > /dev/null || exit 1; done"])
    return status


def run_claim_lint() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "node /Users/rig128gb/rig-builds/rig-sites-buildout/gen/lint_claim.js client-intake-automation one-workflow-review ai-packages professional-ai-packages rig-desk private-ai agent-governance website-design offerings"])
    return status


def run_e2e() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "for p in client-intake-automation one-workflow-review ai-packages professional-ai-packages rig-desk private-ai agent-governance website-design offerings; do /Users/rig128gb/.rig/bin/rig-e2e smoke http://127.0.0.1:4520/$p > /dev/null || exit 1; done"])
    return status


def run_axe() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "node /Users/rig128gb/rig-builds/rig-sites-buildout/gen/axe.mjs"])
    return status


def run_done_test() -> int:
    status = subprocess.call(["/bin/zsh", "-c", "head -1 /Users/rig128gb/rig-builds/rig-sites-buildout/DONE.txt | grep -q '^DONE PASS'"])
    return status


def close(*statuses: int) -> int:
    return max(statuses)
