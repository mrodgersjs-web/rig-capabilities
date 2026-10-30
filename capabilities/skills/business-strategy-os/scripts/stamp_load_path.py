#!/usr/bin/env python3
"""Restate the load path affirmatively in each strategy-* pillar.

The first wording said a pillar "is not itself an always-loaded instruction surface", which is
true but reads as a disclaimer. The accurate affirmative claim is that a routed strategy run
loads this pillar as its first action and does not execute anything ahead of the mandate.
"""
import pathlib, sys
ROOT = pathlib.Path("/Users/rig128gb/Developer/rig-capabilities/capabilities/skills")
LOAD = ("> **Task-start surface.** A routed strategy run loads this pillar as its first action:\n"
        "> `business-strategy-os` is the always-loaded instruction surface, it routes to exactly one\n"
        "> pillar, and the `strategy-director` meta-agent loads this file before doing anything\n"
        "> else. Nothing here executes ahead of the Jev mandate above.\n")
def main() -> int:
    n = 0
    for p in sorted(ROOT.glob("strategy-*/SKILL.md")):
        t = p.read_text(encoding="utf-8")
        if "**Task-start surface.**" in t:
            print("skip", p.parent.name); continue
        lines = t.splitlines(keepends=True)
        i = next(k for k, l in enumerate(lines) if l.startswith("# "))
        j = next((k for k in range(i + 1, min(i + 14, len(lines))) if not lines[k].strip()), i + 1)
        lines.insert(j + 1, LOAD)
        p.write_text("".join(lines), encoding="utf-8")
        print("stated", p.parent.name); n += 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
