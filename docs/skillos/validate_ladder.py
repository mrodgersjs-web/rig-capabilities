#!/usr/bin/env python3
"""Assert SkillOS future-back has v0..v20 once each, each with exactly L1..L10."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text()
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", readme):
        href = m.group(2)
        if href.startswith("http"):
            continue
        if not (ROOT / href).exists():
            errors.append(f"README broken link: {href}")

    text = (ROOT / "05-V20-FUTURE-BACK.md").read_text()
    heads = re.findall(r"^## (v\d+) —", text, re.M)
    expect_heads = [f"v{i}" for i in range(20, -1, -1)]
    if heads != expect_heads:
        errors.append(f"version headings {heads} != {expect_heads}")

    parts = re.split(r"^## (v\d+) —[^\n]*\n", text, flags=re.M)
    it = iter(parts[1:])
    for ver in it:
        body = next(it, "")
        nxt = re.search(r"^## ", body, re.M)
        if nxt:
            body = body[: nxt.start()]
        layers = re.findall(r"^\| (L\d+|U|L\d+–L\d+) \|", body, re.M)
        expect = [f"L{i}" for i in range(1, 11)]
        if layers != expect:
            errors.append(f"{ver} layers={layers}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS 21 versions × L1..L10; README links ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
