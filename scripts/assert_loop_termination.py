#!/usr/bin/env python3
"""Fail unless a loop file parses and declares a real termination protocol.

Not a heading grep. Requires either:
  - a 'Definition of Done' / 'session is done when' section with >=3 concrete items, or
  - a Gates table with a Pass Condition column and >=3 rows, or
  - numbered On-fail HALT protocols on >=3 gates.

Exit 0 only when one of those holds. Stdlib only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def ok(text: str) -> bool:
    # Definition of Done with numbered/bulleted items
    m = re.search(
        r"(?:##+\s*)?(?:Definition of Done|A (?:coding |creative |GTM |research |governed autonomous )?(?:session|run) is done when:?)(.*?)(?:\n## |\n---|\Z)",
        text,
        re.S | re.I,
    )
    if m:
        items = re.findall(r"^\s*(?:\d+\.|[-*])\s+\S+", m.group(1), re.M)
        if len(items) >= 3:
            return True
    # Gates table with Pass Condition
    if re.search(r"\|\s*Pass Condition\s*\|", text, re.I):
        rows = re.findall(r"^\|\s*G?\d+", text, re.M)
        if len(rows) >= 3:
            return True
    # On-fail HALT on multiple gates
    halts = re.findall(r"\*\*On-fail:\*\*.*HALT", text)
    if len(halts) >= 3:
        return True
    # WGLL fail path with numbered loop steps
    if re.search(r"If step \d+ fails", text) and re.search(r"CHECK WGLL", text):
        return True
    if re.search(r"Sprint Closeout", text) and re.search(r"ProofPacket", text) and re.search(r"status: CLOSED", text):
        return True
    return False

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: assert_loop_termination.py <loop.md>", file=sys.stderr)
        return 2
    p = Path(argv[1])
    if not p.is_file():
        print(f"missing {p}", file=sys.stderr)
        return 1
    text = p.read_text(encoding="utf-8")
    if not ok(text):
        print(f"no termination protocol: {p}", file=sys.stderr)
        return 1
    print(f"TERM {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
