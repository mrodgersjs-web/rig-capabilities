#!/usr/bin/env python3
"""Read-only, fail-closed inventory of canonical skill and agent quality.

This is a readiness audit, not an outcome evaluator. A source file or a Jev
confidence value cannot establish that an asset succeeds on real tasks.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

MEANINGFUL_TEST = re.compile(r"^(cmd|mcp):")
MIN_FLOOR = 0.91
AGENT_SKILLS_TOP_LEVEL = {
    "name", "description", "license", "compatibility", "allowed-tools", "metadata",
}


def frontmatter(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        return None
    if not raw.startswith("---\n"):
        return None
    parts = raw.split("\n---\n", 1)
    if len(parts) != 2:
        return None
    try:
        data = yaml.safe_load(parts[0][4:])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def audit_asset(asset: dict, root: Path = ROOT) -> dict:
    kind = asset["kind"]
    path = root / asset["path"]
    source = path / "SKILL.md" if path.is_dir() else path
    fm = frontmatter(source)
    gaps = []
    policy_gaps = []
    portable_frontmatter = False
    if fm is None:
        gaps.append("missing_or_invalid_frontmatter")
        fm = {}
    if not str(fm.get("name", "")).strip():
        gaps.append("missing_name")
    if not str(fm.get("description", "")).strip():
        gaps.append("missing_description")
    if kind in ("skill", "subskill") and fm.get("name") != source.parent.name:
        gaps.append("skill_name_directory_mismatch")
    if kind in ("skill", "subskill") and fm:
        # This only screens top-level keys. Full Agent Skills validation also
        # checks types, naming and length; do not call it conformance proof.
        portable_frontmatter = not (set(fm) - AGENT_SKILLS_TOP_LEVEL)
    metadata = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    for key in ("owner", "domain", "outcome"):
        value = fm.get(key) or metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            gaps.append("missing_" + key)
    done = fm.get("done_when") or []
    if isinstance(done, str):
        done = [done]
    if not isinstance(done, list) or not any(
        isinstance(item, str) and MEANINGFUL_TEST.match(item) for item in done
    ):
        gaps.append("no_behavioral_done_test")
    exemplar = fm.get("great_example")
    exemplar_exists = False
    if isinstance(exemplar, str) and exemplar.strip():
        candidate = Path(exemplar)
        if not candidate.is_absolute() and ".." not in candidate.parts:
            try:
                exemplar_exists = (root / candidate).is_file()
            except OSError:
                pass
    if not exemplar_exists:
        gaps.append("missing_real_exemplar")
    try:
        floor = float(fm.get("quality_floor", 0))
    except (ValueError, TypeError):
        floor = 0
    if floor < MIN_FLOOR or floor > 1:
        policy_gaps.append("declared_quality_floor_below_0.91_or_invalid")
    if kind == "agent":
        # Agent Standards requires these contracts; existence in prose alone
        # cannot certify them, so this is only a low-cost discovery screen.
        try:
            text = source.read_text(encoding="utf-8") if source.is_file() else ""
        except (UnicodeError, OSError):
            text = ""
            gaps.append("unreadable_source")
        for term in ("input", "output", "verifier", "memory"):
            if term not in text.lower():
                gaps.append("agent_missing_" + term + "_contract")
    return {
        "id": asset["id"],
        "kind": kind,
        "source": str(source.relative_to(root)),
        "spec_gaps": sorted(set(gaps)),
        "policy_gaps": sorted(set(policy_gaps)),
        "spec_ready": not gaps,
        "portable_frontmatter_screen": portable_frontmatter if kind in ("skill", "subskill") else None,
        "outcome_score": None,
        "outcome_status": "UNVERIFIED",
        "promotion": "BLOCKED",
    }


def report(root: Path = ROOT) -> dict:
    # Scan canonical roots directly. The catalog index has a TTL and may be
    # stale; asking Repo.load_index() can also rewrite it during a read audit.
    assets = []
    skill_root = root / "capabilities" / "skills"
    for path in sorted(skill_root.rglob("SKILL.md")):
        nested = path.parent.parent != skill_root
        assets.append({"id": str(path.parent.relative_to(skill_root)) if nested else path.parent.name,
                       "kind": "subskill" if nested else "skill",
                       "path": str(path.parent.relative_to(root))})
    agent_root = root / "capabilities" / "agents"
    for path in sorted(agent_root.glob("*.md")):
        assets.append({"id": path.stem, "kind": "agent",
                       "path": str(path.relative_to(root))})
    for path in sorted(agent_root.glob("*/SKILL.md")):
        assets.append({"id": path.parent.name, "kind": "agent",
                       "path": str(path.parent.relative_to(root))})
    rows = [audit_asset(a, root) for a in assets]
    rows.sort(key=lambda row: (row["kind"], row["id"]))
    return {
        "schema": "rig.asset_quality_readiness.v1",
        "standard": "spec ready + independent held-out outcome > 0.90 + zero hard blocks",
        "note": "This audit does not synthesize outcome scores from metadata or Jev confidence.",
        "counts": {
            "assets": len(rows),
            "by_kind": dict(Counter(r["kind"] for r in rows)),
            "spec_ready": sum(r["spec_ready"] for r in rows),
            "portable_skill_frontmatter_screen": sum(
                r["portable_frontmatter_screen"] is True for r in rows
            ),
            "outcome_verified": 0,
            "promotable": 0,
            "spec_gaps": dict(Counter(g for r in rows for g in r["spec_gaps"])),
            "policy_gaps": dict(Counter(g for r in rows for g in r["policy_gaps"])),
        },
        "assets": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true", help="Print counts only")
    parser.add_argument("--gate", action="store_true",
                        help="Fail unless every canonical skill and agent is promotable")
    args = parser.parse_args()
    result = report()
    print(json.dumps(result["counts"] if args.summary else result, indent=2))
    counts = result["counts"]
    if args.gate and (counts["assets"] == 0 or counts["promotable"] != counts["assets"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
