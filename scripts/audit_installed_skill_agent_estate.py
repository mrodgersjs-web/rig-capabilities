#!/usr/bin/env python3
"""Read-only inventory of configured skill and agent install roots.

An entry in a configured directory proves file presence, not runtime loading,
behavior, source ownership, or promotion eligibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402
AGENT_SUFFIXES = {".md", ".toml", ".json", ".yaml", ".yml"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sources(root: Path) -> dict[str, dict[str, Path]]:
    result: dict[str, dict[str, Path]] = {"skill": {}, "agent": {}}
    for path in sorted((root / "capabilities" / "skills").glob("*/SKILL.md")):
        result["skill"][path.parent.name] = path
    agent_root = root / "capabilities" / "agents"
    for path in sorted(agent_root.iterdir()) if agent_root.is_dir() else []:
        if path.is_file() and path.suffix in AGENT_SUFFIXES:
            result["agent"][path.stem] = path
        elif path.is_dir() and (path / "SKILL.md").is_file():
            result["agent"][path.name] = path / "SKILL.md"
    return result


def unregistered_nested_skills(root: Path) -> list[str]:
    """Expose nested SKILL.md files that the top-level catalog does not own."""
    skill_root = root / "capabilities" / "skills"
    return [str(path) for path in sorted(skill_root.rglob("SKILL.md"))
            if path.parent.parent != skill_root]


def integrity_failures(result: dict) -> list[str]:
    """Check only configured-install integrity; never imply outcome certification."""
    counts = result["counts"]
    failures = []
    if counts["missing_roots"]:
        failures.append("missing_configured_roots")
    for status in ("BROKEN_LINK", "DRIFT_BYTES", "FORMAT_VARIANT_UNVERIFIED"):
        if counts["by_status"].get(status, 0):
            failures.append(status.lower())
    return failures


def inspect(root: Path, install_roots: dict[str, dict[str, str]]) -> dict:
    canonical = canonical_sources(root)
    physical_canonical = {
        kind: {path.resolve(): asset_id for asset_id, path in entries.items()}
        for kind, entries in canonical.items()
    }
    rows: list[dict] = []
    root_states: list[dict] = []
    other_entries: list[dict] = []
    for kind in ("skill", "agent"):
        for harness, configured in sorted(install_roots.get(kind, {}).items()):
            base = Path(configured).expanduser()
            exists = base.is_dir()
            root_states.append({"kind": kind, "harness": harness,
                                "path": str(base), "exists": exists})
            if not exists:
                continue
            for entry in sorted(base.iterdir()):
                location = {"kind": kind, "harness": harness,
                            "entry": entry.name, "path": str(entry)}
                if entry.is_symlink() and not entry.exists():
                    rows.append({**location, "status": "BROKEN_LINK",
                                 "link_target": str(entry.readlink())})
                    continue
                source = entry / "SKILL.md" if kind == "skill" else entry
                if kind == "skill" and not source.is_file():
                    other_entries.append({**location, "reason": "NO_TOP_LEVEL_SKILL_MD"})
                    continue
                if kind == "agent" and (not entry.is_file() or entry.suffix not in AGENT_SUFFIXES):
                    other_entries.append({**location, "reason": "UNSCANNED_AGENT_ENTRY"})
                    continue
                asset_id = entry.name if kind == "skill" else entry.stem
                canonical_path = canonical[kind].get(asset_id)
                physical_owner = physical_canonical[kind].get(source.resolve())
                if physical_owner and physical_owner != asset_id:
                    status = "ALIAS_OF_CANONICAL"
                elif canonical_path is None:
                    status = "NONCANONICAL_INSTALLED"
                elif kind == "agent" and source.suffix != canonical_path.suffix:
                    status = "FORMAT_VARIANT_UNVERIFIED"
                elif digest(source) == digest(canonical_path):
                    status = "EXACT_BYTES"
                else:
                    status = "DRIFT_BYTES"
                rows.append({**location, "asset_id": asset_id,
                             "status": status, "resolved_source": str(source.resolve()),
                             "source_sha256": digest(source),
                             "canonical_source": str(canonical_path) if canonical_path else None,
                             "canonical_owner": physical_owner})
    present = {(row["kind"], row["harness"], row.get("asset_id"))
               for row in rows if row["status"] != "BROKEN_LINK"}
    canonical_absence = [
        {"kind": kind, "harness": harness, "asset_id": asset_id}
        for kind, entries in canonical.items()
        for harness in sorted(install_roots.get(kind, {}))
        for asset_id in sorted(entries)
        if (kind, harness, asset_id) not in present
    ]
    physical = {row["resolved_source"] for row in rows if "resolved_source" in row}
    content_hashes = {row["source_sha256"] for row in rows if "source_sha256" in row}
    counts = Counter(row["status"] for row in rows)
    nested = unregistered_nested_skills(root)
    result = {
        "schema": "rig.installed_skill_agent_estate.v1",
        "claim_limit": "Configured file presence only; runtime load and outcomes unverified.",
        "counts": {"canonical_skills": len(canonical["skill"]),
                   "canonical_agents": len(canonical["agent"]),
                   "configured_roots": len(root_states),
                   "missing_roots": sum(not row["exists"] for row in root_states),
                   "installed_entries": len(rows),
                   "distinct_physical_sources": len(physical),
                   "distinct_content_hashes": len(content_hashes),
                   "physical_alias_entries": sum("resolved_source" in row for row in rows) - len(physical),
                   "duplicate_content_entries": sum("source_sha256" in row for row in rows) - len(content_hashes),
                   "canonical_absence_cells": len(canonical_absence),
                   "other_top_level_entries": len(other_entries),
                   "unregistered_nested_skills": len(nested),
                   "by_status": dict(sorted(counts.items()))},
        "root_states": root_states,
        "entries": rows,
        "canonical_absence": canonical_absence,
        "other_entries": other_entries,
        "unregistered_nested_skills": nested,
    }
    result["install_integrity_failures"] = integrity_failures(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--integrity-gate", action="store_true",
                        help="Fail on missing roots, broken links, byte drift, or unverified format variants; not an outcome gate")
    args = parser.parse_args()
    root = ROOT
    result = inspect(root, {kind: Repo(root).install_roots(kind)
                            for kind in ("skill", "agent")})
    print(json.dumps(result["counts"] if args.summary else result, indent=2))
    if args.integrity_gate and result["install_integrity_failures"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
