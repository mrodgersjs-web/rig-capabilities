#!/usr/bin/env python3
"""Build (or verify) the FABLE-2031 brief from committed parts. Stdlib only.

The brief's prose was composed interactively, so no script can re-derive its TEXT.
What a script CAN guarantee is that the pinned bytes are reproducible from the repo
and that no copy drifts: the brief is defined as the concatenation of the committed
parts, in manifest order.

    build_fable_brief.py              # write /tmp/fable-2031-brief.md + .sha256
    build_fable_brief.py --out PATH   # write somewhere else
    build_fable_brief.py --check      # verify the default target byte for byte
    build_fable_brief.py --check --out PATH

Exit codes: 0 ok, 1 mismatch (check) or missing part (build). Never writes a file
it was not asked to write, and `--check` never writes at all.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PARTS_DIR = REPO / "tests" / "fixtures" / "fable2031" / "brief"
MANIFEST = PARTS_DIR / "manifest.json"
DEFAULT_OUT = Path("/tmp/fable-2031-brief.md")


def assemble() -> bytes:
    """Concatenate the committed parts in manifest order."""
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    blobs = []
    for name in spec["parts"]:
        path = PARTS_DIR / name
        if not path.is_file():
            raise SystemExit(f"1 missing brief part: {path}")
        blobs.append(path.read_bytes())
    return b"".join(blobs)


def check(target: Path, blob: bytes, spec: dict) -> int:
    reasons = []
    if not target.is_file():
        reasons.append(f"missing:{target}")
    else:
        got = target.read_bytes()
        real = hashlib.sha256(got).hexdigest()
        if got != blob:
            reasons.append("bytes_differ:got=%d_want=%d" % (len(got), len(blob)))
        if real != spec["brief_sha256"]:
            reasons.append(f"sha_mismatch:{real[:16]}!={spec['brief_sha256'][:16]}")
    if reasons:
        print(json.dumps({"verdict": "MISMATCH", "target": str(target),
                          "reasons": reasons}, indent=1))
        return 1
    print(json.dumps({"verdict": "OK", "target": str(target),
                      "sha256": spec["brief_sha256"]}, indent=1))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="target file")
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    ap.add_argument("--json", action="store_true",
                    help="output is already JSON; accepted for scripts")
    args = ap.parse_args(argv)
    target, blob = Path(args.out), assemble()
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if spec["brief_sha256"] != hashlib.sha256(blob).hexdigest():
        print(json.dumps({"verdict": "MISMATCH",
                          "reasons": ["parts_do_not_match_manifest"]}, indent=1))
        return 1
    if args.check:
        return check(target, blob, spec)
    target.write_bytes(blob)
    sidecar = target.with_suffix(target.suffix + ".sha256")
    sidecar.write_text(spec["brief_sha256"] + "  " + str(target) + "\n")
    print(json.dumps({"verdict": "OK", "wrote": str(target), "bytes": len(blob),
                      "sidecar": str(sidecar), "sha256": spec["brief_sha256"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
