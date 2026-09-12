"""Criteria pack: deterministic 588-row flattening of the lattice authority.

The cell CONTRACTS already exist (lattice/cells.json, 588 canonical cells).
This module does not re-derive them (no second generator); it flattens the
authority into one sorted JSONL row per cell — coordinate, expanded criteria,
the five BMS measurement bindings (UNKNOWN until measurement-rules-v1 receipts
exist — never a substituted 0.5), and process/archetype dependency links —
then binds the pack to a sha256 golden manifest.

`generate --verify PATH` is READ-ONLY and fails closed unless PATH exists
AND its .sha256 sidecar matches — exact hash, filename, row count,
byte-equality with freshly regenerated content — AND the manifest's `prov`
line digests the input-provenance sidecar (`<pack>.inputs.json`), AND every
input hash recorded in that sidecar still matches the real file. There is
NO public command that re-writes provenance or the manifest for an existing
golden: re-attestation over drifted inputs would launder the drift. Plain
`generate` refuses the canonical golden path outright — a regenerated pack
lands at `--out PATH`, and promotion to canonical is a human-reviewed
commit, not a module verb.

Usage:
  python3 rig_capabilities/criteria_pack.py selftest
  python3 rig_capabilities/criteria_pack.py generate --out PATH
  python3 rig_capabilities/criteria_pack.py generate --verify PATH
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "capabilities" / "skills" / "rig-lattice-system"))

from rig_lattice.lattice import generator as gen  # noqa: E402

DEFAULT_OUT = REPO / "runs/agentic-stack-buildout/packs/criteria-v1.jsonl"
BMS_SCALARS = ("failure_cost", "reversibility", "mechanism_clarity",
               "past_failure_rate", "data_volume")
MANIFEST_RX = re.compile(r"^([0-9a-f]{64})  (\S+)  rows=(\d+)$")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _input_paths() -> dict[str, Path]:
    """Every file that deterministically produces pack bytes: the
    transitive closure of local ``rig_lattice`` imports of the generator
    (constants, resolver, _paths, ...), plus this module and the cells
    index. A byte that can change a row is always named by the sidecar.
    (rig_lattice imports are all absolute; relative imports are out of
    the closure rule by construction.)"""
    root = Path(gen.__file__).resolve().parent.parent
    named: dict[str, Path] = {
        "criteria_pack.py": Path(__file__).resolve(),
        "cells.json": Path(gen.CELLS_INDEX).resolve(),
    }
    frontier = [Path(gen.__file__).resolve()]
    while frontier:
        f = frontier.pop()
        named.setdefault(f"rig_lattice/{f.relative_to(root)}", f)
        try:
            tree = ast.parse(f.read_text())
        except (OSError, SyntaxError):
            continue
        mods: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name for a in node.names)
            elif (isinstance(node, ast.ImportFrom) and node.level == 0
                  and node.module):
                mods.add(node.module)
        for m in sorted(mods):
            if m != root.name and not m.startswith(root.name + "."):
                continue
            rel = m.split(".", 1)[1] if "." in m else ""
            stem = root / rel.replace(".", "/") if rel else root
            target = stem if stem.is_dir() else stem.with_suffix(".py")
            if target.is_file() and target not in named.values():
                frontier.append(target.resolve())
    return named


def input_provenance(pack_sha: str) -> dict:
    """Gap G8: the pack sha alone says WHICH bytes, not WHAT MADE them.
    This sidecar hash-binds each input source, so input drift after
    generation is named, not silently re-bound."""
    return {
        "pack_sha256": pack_sha,
        "inputs": {n: _sha(p) for n, p in sorted(_input_paths().items())},
    }


def _prov_path(out: Path) -> Path:
    return out.with_suffix(".inputs.json")


def _is_canonical(out: Path) -> bool:
    """True for the canonical golden path (or its manifest/provenance
    siblings). Generation NEVER writes there; promotion is a commit."""
    return out.resolve() == DEFAULT_OUT.resolve()


def build_rows() -> list[dict]:
    steps = [s.value for s in gen.STEPS]
    ids = sorted(gen.all_cells())
    if len(ids) != 588:
        raise AssertionError(f"authority returned {len(ids)} cells, expected 588")
    rows = []
    for cid in ids:  # cid is the CANONICAL dialect from all_cells()
        c = gen.load_cell(cid)
        step = c["process"]["step_code"]
        if step not in steps:
            raise AssertionError(f"{cid}: step {step!r} not in {steps}")
        i = steps.index(step)
        # Lossless AND identity-safe: the full source contract is embedded
        # unchanged under "contract" (its own vendored bare-digit cell_id is
        # kept as source_cell_id provenance); top-level cell_id stays the
        # canonical all_cells() dialect — load_cell's contract uses a
        # different dialect and must never overwrite the pack identity.
        row = {
            "cell_id": cid,
            "source_cell_id": c["cell_id"],
            "contract": c,
            "bms_inputs": {k: "UNKNOWN-no-receipt" for k in BMS_SCALARS},
            "deps": {
                "archetype": c["routing"]["archetype"],
                "fallback_archetype": c["routing"]["fallback_archetype"],
                "escalation_policy": c["routing"]["escalation_policy"],
                "prev_step": steps[i - 1] if i > 0 else None,
                "next_step": steps[i + 1] if i < len(steps) - 1 else None,
            },
        }
        rows.append(row)
    if [r["cell_id"] for r in rows] != ids:
        raise AssertionError("top-level cell ids drifted from all_cells()")
    return rows


def row_covers(row: dict, contract: dict) -> bool:
    """True iff the row embeds the source contract exactly, unchanged."""
    return row.get("contract") == contract


def selftest() -> int:
    errs: list[str] = []
    rows = {r["cell_id"]: r for r in build_rows()}
    if len(rows) != 588:
        errs.append(f"expected 588 unique cells, got {len(rows)}")
    if sorted(rows) != sorted(gen.all_cells()):
        errs.append("top-level ids != gen.all_cells() dialect")
    for cid, row in sorted(rows.items()):
        c = gen.load_cell(cid)
        if not row_covers(row, c):
            errs.append(f"{cid}: embedded contract differs from load_cell")
        if row.get("source_cell_id") != c["cell_id"]:
            errs.append(f"{cid}: source_cell_id provenance wrong")
        if "sequence" not in row.get("contract", {}).get("process", {}):
            errs.append(f"{cid}: process contract stripped")
        if "escalation_policy" not in row.get("deps", {}):
            errs.append(f"{cid}: escalation_policy missing")
    # self-proof the validator is not blind: a row whose contract is replaced
    # by the s4b top-level flattening (identity-clobbering shape) must fail.
    probe = sorted(rows)[0]
    s4b_shape = {**rows[probe]["contract"], "cell_id": rows[probe]["cell_id"]}
    if row_covers(s4b_shape, gen.load_cell(probe)):
        errs.append("row_covers accepts identity-clobbering shape")
    lossy = {k: v for k, v in rows[probe].items() if k != "contract"}
    if row_covers(lossy, gen.load_cell(probe)):
        errs.append("row_covers accepts contract-stripped row (validator blind)")
    # provenance is not theater, in either direction.
    if not _is_canonical(DEFAULT_OUT):
        errs.append("canonical guard blind: generate could overwrite golden")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "pack.jsonl"
        if main(["generate", "--out", str(tmp)]) != 0:
            errs.append("selftest: generate failed in tempdir")
        elif main(["generate", "--verify", str(tmp)]) != 0:
            errs.append("selftest: verify rejected a freshly generated pack")
        else:
            import io
            from contextlib import redirect_stdout
            prov = _prov_path(tmp)
            if "rig_lattice/lattice/constants.py" not in json.loads(
                    prov.read_text())["inputs"]:
                errs.append("input closure missing"
                            " rig_lattice/lattice/constants.py")
            # laundering: sidecar rewritten over drifted inputs while the
            # checked manifest keeps the old prov digest -> must go RED.
            pv = json.loads(prov.read_text())
            pv["inputs"]["cells.json"] = "0" * 64
            prov.write_text(json.dumps(pv, sort_keys=True) + "\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["generate", "--verify", str(tmp)])
            if rc == 0:
                errs.append("verify launders rewritten provenance"
                            " (manifest prov digest blind)")
            # full forgery: manifest digest also reforged -> the per-input
            # recompute must still NAME the drifted source.
            digest = hashlib.sha256(prov.read_bytes()).hexdigest()
            man = tmp.with_suffix(".sha256")
            man.write_text(man.read_text().splitlines()[0]
                           + f"\nprov  {digest}\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(["generate", "--verify", str(tmp)])
            if rc2 == 0 or "cells.json" not in buf2.getvalue():
                errs.append("verify blind to input drift under forged digest")
            # completeness bypass: drop an input key and re-cut the digest
            # — exact key-set equality must refuse.
            pv3 = json.loads(prov.read_text())
            victim = next((k for k in pv3["inputs"]
                           if k.endswith("constants.py")),
                          sorted(pv3["inputs"])[-1])
            del pv3["inputs"][victim]
            raw3 = json.dumps(pv3, sort_keys=True) + "\n"
            prov.write_text(raw3)
            d3 = hashlib.sha256(raw3.encode()).hexdigest()
            man.write_text(man.read_text().splitlines()[0]
                           + f"\nprov  {d3}\n")
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(["generate", "--verify", str(tmp)])
            if rc3 == 0 or "incomplete" not in buf3.getvalue():
                errs.append("verify accepts incomplete provenance set")
    # naming proof: a real constants-layer input, really changed, must
    # be named by verify (fixtures the transitive-closure machinery).
    import io as _io
    from contextlib import redirect_stdout as _rso
    real_ip = _input_paths
    with tempfile.TemporaryDirectory() as td2:
        fixture = Path(td2) / "constants.py"
        fixture.write_text("VERSION = 1\n")

        def _patched() -> dict[str, Path]:
            base = real_ip()
            base["constants-fixture.py"] = fixture
            return base

        globals()["_input_paths"] = _patched
        try:
            tmp3 = Path(td2) / "pack.jsonl"
            if main(["generate", "--out", str(tmp3)]) == 0:
                fixture.write_text("VERSION = 2\n")  # real input change
                buf4 = _io.StringIO()
                with _rso(buf4):
                    rc4 = main(["generate", "--verify", str(tmp3)])
                if rc4 == 0 or "constants-fixture.py" not in buf4.getvalue():
                    errs.append("verify blind to changed constants input")
        finally:
            globals()["_input_paths"] = real_ip
    print(json.dumps({"ok": not errs, "errors": errs[:10],
                      "cells_checked": len(rows)}))
    return 0 if not errs else 1

def pack_bytes() -> bytes:
    return "".join(json.dumps(r, sort_keys=True) + "\n"
                   for r in build_rows()).encode()


def _fail(target: Path, reason: str) -> int:
    print(json.dumps({"verify": str(target), "error": reason}))
    return 2

def verify(target: Path) -> tuple[list[str], dict]:
    """READ-ONLY golden verification, callable from open_live: returns
    (refusal, {}) — at most one, fail-fast like the CLI — or ([], info).
    Same checks and messages the `generate --verify` branch performs."""
    if not target.exists():
        return ["golden missing"], {}
    have = target.read_bytes()
    rows_have = have.count(b"\n")
    man = target.with_suffix(".sha256")
    if not man.exists():
        return ["manifest missing"], {}
    lines = man.read_text().splitlines()
    m = MANIFEST_RX.match(lines[0].strip()) if lines else None
    if not m:
        return ["manifest unparseable"], {}
    man_sha, man_name, man_rows = m.group(1), m.group(2), int(m.group(3))
    golden_sha = hashlib.sha256(have).hexdigest()
    regen = hashlib.sha256(pack_bytes()).hexdigest()
    for bad in (
        man_sha != golden_sha and f"manifest sha != golden sha ({man_sha[:12]})",
        man_sha != regen and "manifest sha != regenerated sha",
        man_name != target.name and f"manifest filename {man_name!r}",
        man_rows != rows_have and f"manifest rows={man_rows} vs {rows_have}",
        golden_sha != regen and "golden bytes != regenerated bytes",
    ):
        if bad:
            return [bad], {}
    prov = _prov_path(target)
    if not prov.exists():
        return ["input provenance missing; no verb re-attests a golden — "
                "regenerate to a fresh --out and promote by review"], {}
    prov_bytes = prov.read_bytes()
    ln2 = lines[1].strip() if len(lines) > 1 else ""
    m2 = re.match(r"^prov  ([0-9a-f]{64})$", ln2)
    if not m2:
        return ["manifest carries no prov digest; provenance unbound — refuse"], {}
    if hashlib.sha256(prov_bytes).hexdigest() != m2.group(1):
        return ["provenance digest mismatch: sidecar rewritten after the "
                "manifest was cut (laundering refused)"], {}
    try:
        p = json.loads(prov_bytes)
    except json.JSONDecodeError as e:
        return [f"provenance sidecar unparseable: {e}"], {}
    if p.get("pack_sha256") != golden_sha:
        return ["provenance bound to a different pack sha"], {}
    paths = _input_paths()
    ins = p.get("inputs")
    if not isinstance(ins, dict) or set(ins) != set(paths):
        got = sorted(ins) if isinstance(ins, dict) else type(ins).__name__
        return [f"provenance input set incomplete: expected {sorted(paths)}, "
                f"found {got}"], {}
    for name, want in sorted(ins.items()):
        if not isinstance(want, str) or not re.fullmatch(r"[0-9a-f]{64}", want):
            return [f"provenance digest for {name} is malformed"], {}
        src = paths[name]
        if not src.exists():
            return [f"provenance names missing input {name!r}"], {}
        if _sha(src) != want:
            return [f"input drift: {name} changed since generation"], {}
    return [], {"sha256": golden_sha, "rows": rows_have, "manifest": str(man)}



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
        errs, info = verify(target)
        if errs:
            return _fail(target, errs[0])
        print(json.dumps({"verify": str(target), "match": True,
                          "sha256": info["sha256"], "rows": info["rows"],
                          "manifest": info["manifest"]}))
        return 0
    if _is_canonical(out):
        return _fail(out, "canonical golden is promotion-controlled:"
                          " generate to a fresh --out PATH; promotion is a"
                          " human-reviewed commit, not a module verb")
    rows = data.count(b"\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    prov_bytes = (json.dumps(input_provenance(sha), sort_keys=True)
                  + "\n").encode()
    _prov_path(out).write_bytes(prov_bytes)
    man = out.with_suffix(".sha256")
    man.write_text(
        f"{sha}  {out.name}  rows={rows}\n"
        f"prov  {hashlib.sha256(prov_bytes).hexdigest()}\n")
    print(json.dumps({"wrote": str(out), "sha256": sha, "rows": rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
