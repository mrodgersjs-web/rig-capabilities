"""Criteria pack: deterministic 588-row flattening of the lattice authority.

The cell CONTRACTS already exist (lattice/cells.json, 588 canonical cells).
This module does not re-derive them (no second generator); it flattens the
authority into one sorted JSONL row per cell — coordinate, expanded criteria,
the five BMS measurement bindings (UNKNOWN until measurement-rules-v1 receipts
exist — never a substituted 0.5), and process/archetype dependency links —
then binds the pack to a sha256 golden manifest.

`generate --verify PATH` fails closed unless PATH exists AND its .sha256
sidecar exists and matches: exact hash, filename, row count, and byte-equality
with freshly regenerated content. A stale, forged, or missing manifest is a
hard failure; a golden artifact can never self-create.

Usage:
  python3 rig_capabilities/criteria_pack.py generate [--verify PATH] [--out PATH]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "capabilities" / "skills" / "rig-lattice-system"))

from rig_lattice.lattice import generator as gen  # noqa: E402

DEFAULT_OUT = REPO / "runs/agentic-stack-buildout/packs/criteria-v1.jsonl"
BMS_SCALARS = ("failure_cost", "reversibility", "mechanism_clarity",
               "past_failure_rate", "data_volume")
MANIFEST_RX = re.compile(r"^([0-9a-f]{64})  (\S+)  rows=(\d+)$")


def build_rows() -> list[dict]:
    steps = [s.value for s in gen.STEPS]
    ids = sorted(gen.all_cells())
    if len(ids) != 588:
        raise AssertionError(f"authority returned {len(ids)} cells, expected 588")
    rows = []
    for cid in ids:
        c = gen.load_cell(cid)
        step = c["process"]["step_code"]
        if step not in steps:
            raise AssertionError(f"{cid}: step {step!r} not in {steps}")
        i = steps.index(step)
        # Lossless: every field of the source cell contract is carried at the
        # top level (no selective copying), plus two pack-only derivations.
        row = dict(c)
        row["bms_inputs"] = {k: "UNKNOWN-no-receipt" for k in BMS_SCALARS}
        row["deps"] = {
            "archetype": c["routing"]["archetype"],
            "fallback_archetype": c["routing"]["fallback_archetype"],
            "escalation_policy": c["routing"]["escalation_policy"],
            "prev_step": steps[i - 1] if i > 0 else None,
            "next_step": steps[i + 1] if i < len(steps) - 1 else None,
        }
        rows.append(row)
    return rows


def row_covers(row: dict, contract: dict) -> bool:
    """True iff row carries every source contract field, unchanged."""
    return all(k in row and row[k] == v for k, v in contract.items())


def selftest() -> int:
    errs: list[str] = []
    rows = {r["cell_id"]: r for r in build_rows()}
    if len(rows) != 588:
        errs.append(f"expected 588 unique cells, got {len(rows)}")
    for cid, row in sorted(rows.items()):
        c = gen.load_cell(cid)
        if not row_covers(row, c):
            missing = [k for k in c if k not in row]
            diffs = [k for k in c if k in row and row[k] != c[k]]
            errs.append(f"{cid}: missing={missing} differs={diffs}")
        if "sequence" not in row.get("process", {}):
            errs.append(f"{cid}: process contract stripped")
        if "escalation_policy" not in row.get("deps", {}):
            errs.append(f"{cid}: escalation_policy missing")
    # self-proof the validator is not blind: the OLD lossy projection — and
    # any field dropped from a correct row — must fail coverage.
    probe = sorted(rows)[0]
    lossy = {k: v for k, v in rows[probe].items() if k != "process"}
    if row_covers(lossy, gen.load_cell(probe)):
        errs.append("row_covers accepts lossy row (validator blind)")
    old_shape = {k: rows[probe][k] for k in
                 ("cell_id", "coordinate", "bms_inputs")}
    if row_covers(old_shape, gen.load_cell(probe)):
        errs.append("row_covers accepts s4-era lossy shape")
    print(json.dumps({"ok": not errs, "errors": errs[:10],
                      "cells_checked": len(rows)}))
    return 0 if not errs else 1

def pack_bytes() -> bytes:
    return "".join(json.dumps(r, sort_keys=True) + "\n"
                   for r in build_rows()).encode()


def _fail(target: Path, reason: str) -> int:
    print(json.dumps({"verify": str(target), "error": reason}))
    return 2


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="criteria_pack")
    ap.add_argument("cmd", choices=("generate", "selftest"))
    ap.add_argument("--verify", metavar="PATH", nargs="?", const="", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    out = Path(a.out)
    data = pack_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if a.verify is not None:
        target = Path(a.verify) if a.verify else out
        if not target.exists():
            return _fail(target, "golden missing")
        have = target.read_bytes()
        rows_have = have.count(b"\n")
        man = target.with_suffix(".sha256")
        if not man.exists():
            return _fail(target, "manifest missing")
        m = MANIFEST_RX.match(man.read_text().strip())
        if not m:
            return _fail(target, "manifest unparseable")
        man_sha, man_name, man_rows = m.group(1), m.group(2), int(m.group(3))
        golden_sha = hashlib.sha256(have).hexdigest()
        for bad in (
            man_sha != golden_sha and f"manifest sha != golden sha ({man_sha[:12]})",
            man_sha != sha and "manifest sha != regenerated sha",
            man_name != target.name and f"manifest filename {man_name!r}",
            man_rows != rows_have and f"manifest rows={man_rows} vs {rows_have}",
            have != data and "golden bytes != regenerated bytes",
        ):
            if bad:
                return _fail(target, bad)
        print(json.dumps({"verify": str(target), "match": True,
                          "sha256": sha, "rows": rows_have,
                          "manifest": str(man)}))
        return 0
    rows = data.count(b"\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    man = out.with_suffix(".sha256")
    man.write_text(f"{sha}  {out.name}  rows={rows}\n")
    print(json.dumps({"wrote": str(out), "sha256": sha, "rows": rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
