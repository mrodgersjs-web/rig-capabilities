#!/usr/bin/env python3
"""Quote colon-bearing descriptions in the known YouTube and Jev skill family.

This changes YAML syntax only. It leaves every instruction and quality claim
unchanged. Run without --apply for a read-only preview.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "capabilities" / "skills"


def repaired_text(path: Path) -> str | None:
    if not (path.parent.name.startswith("youtube-") or path.parent.name == "jev-system1-cascade"):
        return None
    original = path.read_text(encoding="utf-8")
    if not original.startswith("---\n") or "\n---\n" not in original:
        return None
    header, body = original.split("\n---\n", 1)
    try:
        yaml.safe_load(header[4:])
        return None
    except yaml.YAMLError:
        pass
    lines = header.splitlines()
    description = next((i for i, line in enumerate(lines) if line.startswith("description: ")), None)
    if description is None:
        return None
    value = lines[description].split(": ", 1)[1]
    if ": " not in value:
        return None
    lines[description] = "description: " + json.dumps(value, ensure_ascii=False)
    for i, line in enumerate(lines):
        if line.startswith("  handle: @"):
            lines[i] = "  handle: " + json.dumps(line.split(": ", 1)[1], ensure_ascii=False)
    candidate = "\n".join(lines) + "\n---\n" + body
    parsed = yaml.safe_load("\n".join(lines[1:]))
    if not isinstance(parsed, dict) or parsed.get("name") != path.parent.name:
        raise ValueError(f"repair did not produce valid skill metadata: {path}")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    changes = []
    for path in sorted(ROOT.glob("*/SKILL.md")):
        candidate = repaired_text(path)
        if candidate is None:
            continue
        changes.append(str(path.relative_to(ROOT.parents[1])))
        if args.apply:
            path.write_text(candidate, encoding="utf-8")
    print(json.dumps({"mode": "apply" if args.apply else "check", "count": len(changes), "paths": changes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
