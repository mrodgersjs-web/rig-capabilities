"""Layer 2 Nature engines 21-30 (PROCESS, ±20σ).

DOCTRINE.md §1.4. Each engine combines a YAML criteria pack (structural signals)
with a literal bio-inspired formula (process signals) to produce a blended raw
score. Then Robust-MAD-Z against the 10-baseline corpus.

Blend: 0.7 × criteria_score + 0.3 × bio_formula_score.
"""
from __future__ import annotations
import importlib
import sys
from pathlib import Path

PKG_DIR = Path(__file__).parent
_MODULE_NAMES = sorted(p.stem for p in PKG_DIR.glob("e[0-9]*_*.py"))


def load_nature_engines() -> list:
    engines = []
    for name in _MODULE_NAMES:
        try:
            mod = importlib.import_module(f"rig_lattice.engines.nature.{name}")
            if hasattr(mod, "ENGINE"):
                engines.append(mod.ENGINE)
        except Exception as e:
            print(f"[nature] failed to load {name}: {e}", file=sys.stderr)
    return engines
