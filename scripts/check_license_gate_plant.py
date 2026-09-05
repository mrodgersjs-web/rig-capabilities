#!/usr/bin/env python3
"""Plant-failure proof for the licence gate.

A gate that never goes RED is theatre. This takes one REAL granted digest out
of the ledger by making its `archive_allowed` non-boolean (the shape the gate
claims to fail closed on), then asserts two things:

  1. the withdrawal denies — `_licence_map` stops mapping that digest, and
  2. `skillos check --stores` names the problem instead of shrugging.

Then it restores the file byte-for-byte and asserts both flip back.

The tamper is on the tracked ledger, so the tree is dirty for a few seconds.
Restore is unconditional (finally) and verified against the bytes read at entry
and against git.

exit 0 = planted defect named and denied; restore clean.
exit 1 = gate accepted the defect, stayed silent, or the tree is not restored.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rig_capabilities import skillos  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "skillos" / "blob-license-ledger.json"
WITNESS = ROOT / "scripts" / "license_gate_witness" / "denied-SKILL.md"


def check_stores() -> str:
    proc = subprocess.run(
        ["./bin/rig-capabilities", "skillos", "check", "--stores"],
        cwd=ROOT, capture_output=True, text=True, timeout=300, check=False,
    )
    return proc.stdout + proc.stderr


def main() -> int:
    problems: list[str] = []

    # A witness fixture that quietly vanished, or arrived wrong, would turn this
    # into a no-op that still exits 0. Missing and malformed both fail.
    if not WITNESS.is_file():
        print(f"FAIL: witness fixture missing: {WITNESS}")
        return 1
    if "license: unknown" not in WITNESS.read_text(encoding="utf-8"):
        problems.append(f"witness fixture malformed: {WITNESS}")

    if not LEDGER.is_file():
        print(f"FAIL: ledger absent: {LEDGER}")
        return 1

    before = LEDGER.read_bytes()
    doc = json.loads(before)
    entries = doc.get("entries") or []
    granted, _ = skillos._licence_map(ROOT)
    if not granted:
        print("FAIL: ledger clears nothing — nothing to withdraw")
        return 1
    victim = next(e for e in entries if e.get("blob_sha256") in granted)
    digest = victim["blob_sha256"]

    try:
        for e in doc["entries"]:
            if e.get("blob_sha256") == digest:
                e["archive_allowed"] = "yes"          # not a bool: must fail closed
                e["basis"] = "PLANTED: non-boolean grant as gate proof"
        LEDGER.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        allowed_now, lic_problems = skillos._licence_map(ROOT)
        denied = digest not in allowed_now
        out = check_stores()
        named = "non-boolean archive_allowed" in out or "archive_allowed" in out
        print(f"planted on {victim['kind']}/{victim['id']} -> denied={denied} named={named}")
        print(f"  licence_problems: {lic_problems[:2] or '(none)'}")
        if not denied:
            problems.append("gate ACCEPTED a non-boolean archive_allowed — withdrawal did not deny")
        if not named:
            problems.append("gate stayed silent; tail: " + out[-400:])
    finally:
        LEDGER.write_bytes(before)

    restored, rest_problems = skillos._licence_map(ROOT)
    if digest not in restored:
        problems.append("restore did not re-grant the planted digest")
    if any("non-boolean" in p for p in rest_problems):
        problems.append("gate still names the restored entry")
    print(f"restored -> re-granted={digest in restored} problems={rest_problems[:2] or '(none)'}")

    if LEDGER.read_bytes() != before:
        problems.append("ledger bytes differ from entry state")
    if subprocess.run(["git", "diff", "--quiet", "--",
                       str(LEDGER.relative_to(ROOT))], cwd=ROOT, check=False).returncode:
        problems.append("ledger differs from HEAD after restore")

    for p in problems:
        print("FAIL:", p)
    if problems:
        return 1
    print("OK: licence gate denies a non-boolean grant, names it, and clears on restore")
    return 0


if __name__ == "__main__":
    sys.exit(main())
