"""Canonical filesystem anchors for the rig_lattice package.

Every module that needs a data directory or a runtime output directory imports
from here. This replaces the vendored ``ROOT = Path(__file__).parent.parent``
idiom (which resolved to the old rig-deviator repo root and broke the moment
the tree was repackaged) with one place that knows the layout:

    <skill>/                 SKILL_ROOT
      rig_lattice/           PKG_ROOT
        criteria/            CRITERIA_DIR   (44 yaml packs + compiled json)
        lattice/cells/       CELLS_DIR      (588 cell contracts)
        baselines/           BASELINES_DIR
      runs/                  RUNS_DIR       (all runtime output)

RUNS_DIR is the single sink for anything written at runtime — audit logs,
proof packets, the SQLite DB, rendered reports. Nothing is ever written to
$HOME/Desktop or to an absolute path baked in at vendor time. Override with
RIG_LATTICE_RUNS_DIR when the installed skill directory is read-only.
"""
from __future__ import annotations

import os
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = PKG_ROOT.parent

CRITERIA_DIR = PKG_ROOT / "criteria"
CELLS_DIR = PKG_ROOT / "lattice" / "cells"
BASELINES_DIR = PKG_ROOT / "baselines"
CALIBRATION_FILE = PKG_ROOT / "calibration.yaml"

RUNS_DIR = Path(os.environ.get("RIG_LATTICE_RUNS_DIR") or (SKILL_ROOT / "runs"))

# The vendored tree called this "audits/". Runtime output is unified under
# runs/ so an installed copy has exactly one writable directory.
AUDITS_DIR = RUNS_DIR


def ensure_runs_dir() -> Path:
    """Create RUNS_DIR on demand. Callers that write must call this first."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR


__all__ = [
    "PKG_ROOT",
    "SKILL_ROOT",
    "CRITERIA_DIR",
    "CELLS_DIR",
    "BASELINES_DIR",
    "CALIBRATION_FILE",
    "RUNS_DIR",
    "AUDITS_DIR",
    "ensure_runs_dir",
]
