"""lattice_wire_adapter — admitted adapter for rig_lattice intent routing.

Loads the rig_lattice package by path via importlib (no function-local import
statements, no sys.path mutation) so the collector's lattice routing stays a
SOURCE-graph edge while the vendored package remains outside the estate root.
Returns None on any load failure; callers keep the deterministic fallback.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

LATTICE_SKILL_DIRS = (
    Path.home() / ".hermes" / "skills" / "rig-lattice-system",
    Path.home() / ".claude" / "skills" / "rig-lattice-system",
)

_cache: list[Any] = [None, False]


def _load_package(name: str, init_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        name, init_path, submodule_search_locations=[str(init_path.parent)]
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"no spec for {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def route_intent_fn() -> Any:
    """Return rig_lattice.lattice.wire.route_intent, or None when the package
    is absent or unloadable (caller keeps the deterministic fallback route)."""
    if not _cache[1]:
        _cache[1] = True
        for root in LATTICE_SKILL_DIRS:
            pkg_init = root / "rig_lattice" / "__init__.py"
            lattice_init = root / "rig_lattice" / "lattice" / "__init__.py"
            wire_path = root / "rig_lattice" / "lattice" / "wire.py"
            if not (pkg_init.is_file() and lattice_init.is_file() and wire_path.is_file()):
                continue
            prior = {
                name: module
                for name, module in sys.modules.items()
                if name == "rig_lattice" or name.startswith("rig_lattice.")
            }
            try:
                if sys.modules.get("rig_lattice") is None:
                    _load_package("rig_lattice", pkg_init)
                if sys.modules.get("rig_lattice.lattice") is None:
                    _load_package("rig_lattice.lattice", lattice_init)
                wire = _load_package("rig_lattice.lattice.wire", wire_path)
                _cache[0] = wire.route_intent
                break
            except Exception:
                # rollback: a partial chain never survives into the next root —
                # restore prior entries and drop everything this attempt added
                for name in [n for n in sys.modules if n == "rig_lattice" or n.startswith("rig_lattice.")]:
                    if name not in prior:
                        sys.modules.pop(name, None)
                for name, module in prior.items():
                    sys.modules[name] = module
                continue
    return _cache[0]
