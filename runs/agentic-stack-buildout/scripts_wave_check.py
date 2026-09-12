#!/usr/bin/env python3
"""Wave checker: verifies Section I inventory files (existence, size, Claims/Gaps
sections). Paths resolve relative to this script's directory so the checker can
run from any CWD. No args = all three files; one arg = that single file.
Success-only marker on stdout."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ALL = [
    "inventory/C18-runtime-inventory.md",
    "inventory/C17-C19-estate-schedulers.md",
    "inventory/C20-process-surfaces.md",
]

targets = sys.argv[1:] or ALL
problems = []
for rel in targets:
    path = os.path.join(BASE, rel)
    if not os.path.isfile(path):
        problems.append(f"missing: {rel}")
        continue
    size = os.path.getsize(path)
    text = open(path, encoding="utf-8", errors="replace").read()
    if size < 2000:
        problems.append(f"too small ({size}B): {rel}")
    if "## Claims" not in text:
        problems.append(f"no '## Claims' section: {rel}")
    if "## Gaps" not in text:
        problems.append(f"no '## Gaps' section: {rel}")

for p in problems:
    print("FAIL:", p)
if problems:
    sys.exit(1)
print("wave inventories ok")
