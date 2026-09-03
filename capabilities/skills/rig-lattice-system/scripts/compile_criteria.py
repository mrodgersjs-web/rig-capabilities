#!/usr/bin/env python3
"""Compile the YAML sources of truth into JSON the runtime can read.

rig-capabilities is a stdlib-only repo, but the 40 deviation engines are
driven by YAML criteria packs and the 588 cell contracts are YAML too. PyYAML
is therefore a *compile-time* dependency, never a runtime one: this tool turns

    rig_lattice/criteria/<slug>.yaml   ->  rig_lattice/criteria/<slug>.json
    rig_lattice/calibration.yaml       ->  rig_lattice/calibration.json
    rig_lattice/lattice/cells/*.yaml   ->  rig_lattice/lattice/cells.json

and the runtime reads only the JSON. That is what keeps the A1 audit path
deterministic and dependency-free.

Usage:
    python3 scripts/compile_criteria.py            # compile everything
    python3 scripts/compile_criteria.py --check     # verify JSON matches YAML
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PKG = SKILL_ROOT / "rig_lattice"
CRITERIA_DIR = PKG / "criteria"
CALIBRATION_YAML = PKG / "calibration.yaml"
CALIBRATION_JSON = PKG / "calibration.json"
CELLS_DIR = PKG / "lattice" / "cells"
CELLS_JSON = PKG / "lattice" / "cells.json"


def _require_yaml():
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        sys.exit(
            "PyYAML is required to compile (not to run). "
            "Install it with: pip3 install pyyaml"
        )
    return yaml


def _dump(path: Path, data: object) -> str:
    text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(text)
    return text


def compile_all(check: bool = False) -> int:
    yaml = _require_yaml()
    problems: list[str] = []
    compiled = 0

    # ── criteria packs ────────────────────────────────────────────────────
    for src in sorted(CRITERIA_DIR.glob("*.yaml")):
        data = yaml.safe_load(src.read_text())
        dst = src.with_suffix(".json")
        if check:
            if not dst.exists():
                problems.append(f"missing {dst.relative_to(SKILL_ROOT)}")
            elif json.loads(dst.read_text()) != data:
                problems.append(f"stale {dst.relative_to(SKILL_ROOT)}")
        else:
            _dump(dst, data)
        compiled += 1

    # ── calibration ladder ────────────────────────────────────────────────
    if CALIBRATION_YAML.exists():
        data = yaml.safe_load(CALIBRATION_YAML.read_text())
        if check:
            if not CALIBRATION_JSON.exists():
                problems.append("missing rig_lattice/calibration.json")
            elif json.loads(CALIBRATION_JSON.read_text()) != data:
                problems.append("stale rig_lattice/calibration.json")
        else:
            _dump(CALIBRATION_JSON, data)
        compiled += 1

    # ── 588 cell contracts -> one index ───────────────────────────────────
    index: dict[str, dict] = {}
    for src in sorted(CELLS_DIR.glob("*.yaml")):
        card = yaml.safe_load(src.read_text())
        # Key by BOTH dialects: the canonical D-prefixed id and the bare-digit
        # filename stem the 588 files actually use.
        stem = src.stem                       # L1-1-A1-I1
        level, digit, mode, step = stem.split("-")
        index[f"{level}-D{digit}-{mode}-{step}"] = card
        index[stem] = card
    if check:
        if not CELLS_JSON.exists():
            problems.append("missing rig_lattice/lattice/cells.json")
        elif json.loads(CELLS_JSON.read_text()) != index:
            problems.append("stale rig_lattice/lattice/cells.json")
    else:
        _dump(CELLS_JSON, index)
    compiled += 1

    if check:
        if problems:
            for p in problems:
                print(f"OUT OF SYNC: {p}", file=sys.stderr)
            print(f"FAIL: {len(problems)} compiled artifact(s) out of sync")
            return 1
        print(f"OK: {compiled} source group(s) in sync with compiled JSON")
        return 0

    n_criteria = len(list(CRITERIA_DIR.glob("*.json")))
    print(
        f"compiled {n_criteria} criteria packs, calibration, and "
        f"{len(list(CELLS_DIR.glob('*.yaml')))} cell contracts "
        f"({len(index)} index keys)"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify the compiled JSON matches the YAML instead of writing",
    )
    args = ap.parse_args()
    return compile_all(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
