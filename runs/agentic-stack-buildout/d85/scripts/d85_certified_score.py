#!/usr/bin/env python3
"""Deterministic certifier-context scorer for D85 gate-d mint_commands.

The loader fingerprint embeds sys.path, so an inventory hash is only
meaningful in the exact interpreter context that produced it. This runner
rebuilds the canonical certifier context — the CLI's own startup path plus
the rig-lattice-system insertion that validate_lattice performs before
score_process — so the verdict it prints is byte-identical to the one the
enforcement path (bin/rig-determinism-85 checklist --process-id) binds to.

Usage: python3 d85_certified_score.py <process-id>
Exit: 0 + verdict JSON on stdout; 2 + AdmissionBlock code/detail on stderr.
Read-only: recomputes inventory/classification/score; mints nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = REPO_ROOT / "capabilities" / "skills" / "rig-determinism-85"
BIN_DIR = SKILL_ROOT / "bin"
LATTICE_ROOT = SKILL_ROOT.parent / "rig-lattice-system"


def enter_certifier_context() -> None:
    # interpreter startup put this script's dir at sys.path[0]; replace it
    # with the CLI bin dir, then replay the CLI's two inserts and the
    # validate_lattice lattice insert, in the CLI's order.
    sys.path[0] = str(BIN_DIR)
    sys.path.insert(0, str(SKILL_ROOT))
    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(LATTICE_ROOT))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: d85_certified_score.py <process-id>", file=sys.stderr)
        return 2
    enter_certifier_context()
    import d85
    import d85_gates

    try:
        verdict = d85_gates.score_realized(d85.AUTHORITY_REGISTRY, argv[1])
    except d85.AdmissionBlock as block:
        print(json.dumps({"reason": block.code, "detail": str(block.detail)},
                         sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
