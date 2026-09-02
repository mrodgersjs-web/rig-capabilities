#!/usr/bin/env python3
"""Name every canonical whose declared `great_example` does not exist on disk.

`great_example` is one of the four quality fields the catalog parses and the
router serves, so an agent asking for "what good looks like" in a lane gets a
path. If that path is a stub, the field is decoration: it reads as rigour and
delivers nothing, and nothing in `certify` notices, because the `done_tests`
gate runs `done_when` and no gate ever opened the exemplar path.

Found while verifying the mh-02 upgrade: mh-02 was the only `mh-0*` harness
whose declared exemplar actually existed, which is when the estate-wide count
was checked. The ratchet test (`tests/test_exemplar_resolution.py`) pins the
number so it can only fall.

Exit 0 when every declared exemplar resolves; exit 1 and print each offender.

    python3 scripts/exemplar_resolution.py [--json] [--index PATH] [--root DIR]

Stdlib only. Reads only repo-rooted files: the index it is pointed at and the
paths the index names. No network, no model, no writes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def dangling(root: Path, index_path: Path) -> dict:
    """Return {declared, resolved, missing:[{id, kind, great_example}]}."""
    if not index_path.is_file():
        raise SystemExit(f"index not found: {index_path} (run "
                         f"`./bin/rig-capabilities reindex`)")
    idx = json.loads(index_path.read_text(encoding="utf-8"))
    declared = 0
    missing = []
    for a in idx.get("assets", []):
        if a.get("source") != "canonical":
            continue
        ge = (a.get("quality") or {}).get("great_example")
        if not ge:
            continue
        declared += 1
        # an exemplar path is repo-relative; absolute paths resolve as written
        p = Path(ge)
        target = p if p.is_absolute() else root / p
        if not target.exists():
            missing.append({"id": a.get("id"), "kind": a.get("kind"),
                            "great_example": ge})
        elif target.is_file() and target.stat().st_size < 40:
            # a placeholder file is a stub, not an example
            missing.append({"id": a.get("id"), "kind": a.get("kind"),
                            "great_example": ge, "stub_bytes": target.stat().st_size})
    missing.sort(key=lambda m: (m.get("kind") or "", m.get("id") or ""))
    return {"declared": declared, "resolved": declared - len(missing),
            "missing": missing}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="exemplar_resolution")
    ap.add_argument("--index", default=".index.json")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--plant", metavar="ID",
                    help="pretend ID's exemplar is missing; proves the detector "
                         "fires. Never writes anything.")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    rep = dangling(root, root / a.index)
    if a.plant:
        hit = next((x for x in _declared_rows(root, root / a.index)
                    if x[0] == a.plant), None)
        if hit is None:
            print(f"plant refused: no canonical declares an exemplar as {a.plant}")
            return 2
        rep["missing"] = rep["missing"] + [{"id": a.plant, "kind": hit[1],
                                            "great_example": hit[2],
                                            "planted": True}]
        rep["missing_count"] = len(rep["missing"])
    n = len(rep["missing"])
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        print(f"declared={rep['declared']} resolved={rep['resolved']} "
              f"dangling={n}")
        for m in rep["missing"]:
            tag = " (planted)" if m.get("planted") else (
                " (stub)" if m.get("stub_bytes") else "")
            print(f"  {m['kind']:<10} {m['id']:<46} -> {m['great_example']}{tag}")
    return 1 if n else 0


def _declared_rows(root: Path, index_path: Path):
    idx = json.loads(index_path.read_text(encoding="utf-8"))
    for a in idx.get("assets", []):
        if a.get("source") != "canonical":
            continue
        ge = (a.get("quality") or {}).get("great_example")
        if ge:
            yield a.get("id"), a.get("kind"), ge


if __name__ == "__main__":
    sys.exit(main())
