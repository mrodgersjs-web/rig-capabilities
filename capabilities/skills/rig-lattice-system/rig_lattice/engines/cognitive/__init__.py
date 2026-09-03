"""Layer 1 Cognitive engines 01-20 (OUTPUT, ±20σ).

DOCTRINE.md §1.4 + §5. Each engine is a thin module that imports the factory
and registers a DeviationEngine instance bound to its YAML criteria pack.

Auto-discovery: load_cognitive_engines() returns all 20 instances.
"""
from __future__ import annotations
import importlib
import sys
from pathlib import Path

PKG_DIR = Path(__file__).parent

# Auto-import all e*.py modules so they register
_MODULE_NAMES = sorted(p.stem for p in PKG_DIR.glob("e[0-9]*_*.py"))


def load_cognitive_engines() -> list:
    """Load every engine module and return their DeviationEngine instances.

    Each module exposes ENGINE: DeviationEngine.
    """
    engines = []
    for name in _MODULE_NAMES:
        try:
            mod = importlib.import_module(f"rig_lattice.engines.cognitive.{name}")
            if hasattr(mod, "ENGINE"):
                engines.append(mod.ENGINE)
        except Exception as e:
            print(f"[cognitive] failed to load {name}: {e}", file=sys.stderr)
    return engines
