"""V35: copy compiled GoalSpecs into the engine spec dir.

ADOPTION-PLAN remaining step: out/harness-goalspecs/*.yaml →
~/.hermes/skills/goal-loop/yaml-specs/. Default is dry-run. --apply
writes; never deletes extras in dest.
"""
from __future__ import annotations

import shutil
from pathlib import Path

DEFAULT_DEST = Path.home() / ".hermes" / "skills" / "goal-loop" / "yaml-specs"


def harness_install(repo, dest: str | Path | None = None,
                    apply: bool = False) -> dict:
    src = Path(repo.root) / "out" / "harness-goalspecs"
    dest_p = Path(dest) if dest else DEFAULT_DEST
    files = sorted(src.glob("*.yaml")) if src.is_dir() else []
    planned, written = [], []
    for f in files:
        target = dest_p / f.name
        planned.append(str(target))
        if not apply:
            continue
        dest_p.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() == f.read_bytes():
            continue
        shutil.copy2(f, target)
        written.append(f.name)
    return {"ok": True, "apply": apply, "src": str(src), "dest": str(dest_p),
            "count": len(files), "planned": len(planned), "written": written,
            "src_missing": not src.is_dir()}
