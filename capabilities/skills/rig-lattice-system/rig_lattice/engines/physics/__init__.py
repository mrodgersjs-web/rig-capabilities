"""Layer 3 Physics engines 31-40 (STATE, ±30σ HARD gates).

DOCTRINE.md §1.3 — Physics engines are HARD CONSTRAINTS. Any failure
HARD_BLOCKs the entire pipeline regardless of L1/L2 scores. This is the
short-circuit logic enforced by the orchestrator.

Each engine blends:
  - 0.5 × criteria YAML pack score (structural detection)
  - 0.5 × literal physics formula (numeric proxy)

Higher bio-formula weight (0.5 vs 0.3 for nature) because physics gates
need stricter numeric anchoring.
"""
from __future__ import annotations
import importlib
import sys
from pathlib import Path

PKG_DIR = Path(__file__).parent
_MODULE_NAMES = sorted(p.stem for p in PKG_DIR.glob("e[0-9]*_*.py"))


def load_physics_engines() -> list:
    engines = []
    for name in _MODULE_NAMES:
        try:
            mod = importlib.import_module(f"rig_lattice.engines.physics.{name}")
            if hasattr(mod, "ENGINE"):
                engines.append(mod.ENGINE)
        except Exception as e:
            print(f"[physics] failed to load {name}: {e}", file=sys.stderr)
    return engines
