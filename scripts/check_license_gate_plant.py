#!/usr/bin/env python3
"""Adversarial proof that the licence/store gate fails closed.

All tampering happens in temporary roots.  The tracked SkillOS ledger,
universe, receipts, and warehouse are read-only inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rig_capabilities import skillos  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKILLOS = ROOT / "docs" / "skillos"
LEDGER = SKILLOS / "blob-license-ledger.json"
UNIVERSE = SKILLOS / "universe.jsonl"
RECEIPTS = SKILLOS / "receipts.jsonl"
INDEX = ROOT / ".index.json"
WITNESS = ROOT / "scripts" / "license_gate_witness" / "denied-SKILL.md"
CANONICAL_INPUTS = (LEDGER, UNIVERSE, RECEIPTS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "<absent>"


def _git_status() -> str:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--", "docs/skillos/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(f"git status failed ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout


def _print_status(label: str, status: str) -> None:
    print(f"canonical git status ({label}):")
    print(status, end="" if status.endswith("\n") else "\n") if status else print("(clean)")


def _fixture_problems(fixtures: list[tuple[str, Path]]) -> list[str]:
    """Return every missing/malformed fixture complaint; never stop at the first."""
    problems = []
    for label, path in fixtures:
        if not path.is_file():
            problems.append(f"{label}: missing fixture: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)
        if len(frontmatter) < 3 or not any(
            line.strip() == "license: unknown" for line in frontmatter[1].splitlines()
        ):
            problems.append(f"{label}: malformed fixture: {path}")
    return problems


def _copy_input(source: Path, root: Path) -> None:
    dest = root / source.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


def _prepare_gate_root(root: Path) -> None:
    for source in (LEDGER, UNIVERSE, INDEX):
        _copy_input(source, root)
    if RECEIPTS.is_file():
        _copy_input(RECEIPTS, root)

    # Keep Repo.load_index() on the copied index rather than rebuilding it from
    # the deliberately minimal temporary tree.
    index_path = root / INDEX.relative_to(ROOT)
    index_doc = json.loads(index_path.read_text(encoding="utf-8"))
    index_doc["generated_epoch"] = int(time.time())
    index_path.write_text(json.dumps(index_doc), encoding="utf-8")


def _universe_rows(root: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in (root / UNIVERSE.relative_to(ROOT)).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _select_victim(root: Path) -> tuple[dict, dict, Path]:
    allowed, licence_problems = skillos._licence_map(root)
    if licence_problems:
        raise RuntimeError(f"pristine copied ledger has complaints: {licence_problems}")
    ledger_doc = json.loads(
        (root / LEDGER.relative_to(ROOT)).read_text(encoding="utf-8")
    )
    entries = ledger_doc.get("entries") or []
    entry_counts: dict[str, int] = {}
    for entry in entries:
        if isinstance(entry, dict) and entry.get("archive_allowed") is True:
            digest = entry.get("blob_sha256") or ""
            entry_counts[digest] = entry_counts.get(digest, 0) + 1

    for row in _universe_rows(root):
        store = row.get("store") or {}
        digest = store.get("blob_sha256") or ""
        source_blob = ROOT / skillos.WAREHOUSE / digest[:2] / digest
        if (
            store.get("status") == "blob"
            and entry_counts.get(digest) == 1
            and allowed.get(digest) == row.get("sha")
            and source_blob.is_file()
            and _sha256(source_blob) == digest
        ):
            entry = next(
                item
                for item in entries
                if isinstance(item, dict)
                and item.get("archive_allowed") is True
                and item.get("blob_sha256") == digest
            )
            if (entry.get("kind"), entry.get("id")) != (row.get("kind"), row.get("id")):
                continue
            return row, entry, source_blob
    raise RuntimeError("no unique, licensed universe blob is available to withdraw")


def _prune_to_victim(root: Path, row: dict) -> None:
    """Shrink the gate root to the one row under test.

    The real snapshot carries 293 recipe rows across 6 groups, and `stores=True` fetches every
    one of their pinned origins. Proof 'a' is about the licence verdict, so those rows are both
    irrelevant and the only thing that would put the plant on the network.
    """
    universe = root / UNIVERSE.relative_to(ROOT)
    universe.write_text(json.dumps(row) + "\n", encoding="utf-8")
    index_path = root / INDEX.relative_to(ROOT)
    index_doc = json.loads(index_path.read_text(encoding="utf-8"))
    index_doc["assets"] = [
        a for a in (index_doc.get("assets") or [])
        if (a.get("kind"), a.get("id")) == (row["kind"], row["id"])
    ]
    index_path.write_text(json.dumps(index_doc), encoding="utf-8")


def _proof(problems: list[str], label: str, ok: bool, detail: str) -> None:
    print(f"{'PASS' if ok else 'RED'} {label}: {detail}")
    if not ok:
        problems.append(f"{label}: {detail}")


def _prove_ledger_gate(temp_base: Path, problems: list[str]) -> None:
    gate_root = temp_base / "gate-root"
    _prepare_gate_root(gate_root)
    copied_ledger = gate_root / LEDGER.relative_to(ROOT)
    pristine_ledger = copied_ledger.read_bytes()
    row, victim, source_blob = _select_victim(gate_root)
    _prune_to_victim(gate_root, row)
    digest = victim["blob_sha256"]
    key = f"{row['kind']}/{row['id']}"
    complaint = f"non-boolean archive_allowed for {key}"

    copied_blob = gate_root / skillos.WAREHOUSE / digest[:2] / digest
    copied_blob.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_blob, copied_blob)

    tampered = json.loads(pristine_ledger)
    changed = 0
    for entry in tampered["entries"]:
        if entry.get("blob_sha256") == digest:
            entry["archive_allowed"] = "yes"
            changed += 1
    copied_ledger.write_text(json.dumps(tampered), encoding="utf-8")

    allowed, map_problems = skillos._licence_map(gate_root)
    # stores=True is what makes the store-gate exit code meaningful (without it the exit code
    # derives from key coverage, so a denied blob would still exit 0). The root was pruned to the
    # one blob row, so no recipe origins remain to fetch and the plant stays hermetic.
    gate = skillos.check_universe(skillos.Repo(gate_root), stores=True)
    red = (
        changed == 1
        and digest not in allowed
        and complaint in map_problems
        and complaint in gate.get("licence_problems", [])
        and key in gate.get("licence_denied", [])
        and gate.get("exit_code") == 1
    )
    _proof(
        problems,
        "a",
        red,
        f"withdraw {key}; gate_exit={gate.get('exit_code')} "
        f"denied={digest not in allowed and key in gate.get('licence_denied', [])} "
        f"named={complaint in gate.get('licence_problems', [])}",
    )

    copied_ledger.write_bytes(pristine_ledger)
    restored_allowed, restored_map_problems = skillos._licence_map(gate_root)
    restored_gate = skillos.check_universe(skillos.Repo(gate_root), stores=True)
    restored = (
        digest in restored_allowed
        and complaint not in restored_map_problems
        and complaint not in restored_gate.get("licence_problems", [])
        and key not in restored_gate.get("licence_denied", [])
    )
    _proof(
        problems,
        "b",
        restored,
        f"restore {key}; regranted={digest in restored_allowed} "
        f"specific_complaint_cleared={complaint not in restored_gate.get('licence_problems', [])}",
    )


def _prove_unlicensed_witness(temp_base: Path, problems: list[str]) -> None:
    witness_root = temp_base / "witness-root"
    _copy_input(LEDGER, witness_root)
    asset_dir = witness_root / "capabilities" / "skills" / "license-gate-witness-denied"
    asset_dir.mkdir(parents=True)
    shutil.copy2(WITNESS, asset_dir / "SKILL.md")
    asset = {
        "kind": "skill",
        "id": asset_dir.name,
        "source": "canonical",
        "path": str(asset_dir.relative_to(witness_root)),
        "abs_path": str(asset_dir),
        "sha": skillos.Repo._sha_dir(asset_dir),
    }
    allowed, _ = skillos._licence_map(witness_root)
    warehouse = witness_root / skillos.WAREHOUSE
    before = {p.relative_to(warehouse) for p in warehouse.rglob("*") if p.is_file()}
    store = skillos._store_for(witness_root, asset, licence=allowed)
    after = {p.relative_to(warehouse) for p in warehouse.rglob("*") if p.is_file()}
    refused = store.get("status") == "unresolved" and before == after == set()
    _proof(
        problems,
        "c",
        refused,
        f"unlicensed fixture store={store.get('status')} warehouse_files_written={len(after - before)}",
    )


def _prove_fixture_diagnostics(temp_base: Path, problems: list[str]) -> None:
    malformed = temp_base / "malformed-SKILL.md"
    malformed.write_text("---\nname: malformed-witness\n---\n\n# malformed\n", encoding="utf-8")
    fixture_problems = _fixture_problems(
        [
            ("missing-witness", temp_base / "missing-SKILL.md"),
            ("malformed-witness", malformed),
        ]
    )
    missing_named = any("missing-witness: missing fixture:" in p for p in fixture_problems)
    malformed_named = any("malformed-witness: malformed fixture:" in p for p in fixture_problems)
    _proof(
        problems,
        "d",
        missing_named and malformed_named and len(fixture_problems) == 2,
        "one-pass diagnostics=" + " | ".join(fixture_problems),
    )


def _run(temp_base: Path, problems: list[str]) -> None:
    witness_problems = _fixture_problems([("denied-witness", WITNESS)])
    problems.extend(witness_problems)
    for problem in witness_problems:
        print("RED fixture:", problem)

    required = (LEDGER, UNIVERSE, INDEX)
    missing_inputs = [str(path) for path in required if not path.is_file()]
    for path in missing_inputs:
        problem = f"required input missing: {path}"
        problems.append(problem)
        print("RED input:", problem)

    if not missing_inputs:
        _prove_ledger_gate(temp_base, problems)
    if not witness_problems and LEDGER.is_file():
        _prove_unlicensed_witness(temp_base, problems)
    _prove_fixture_diagnostics(temp_base, problems)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep-tmp",
        action="store_true",
        help="keep the isolated roots and print their location for debugging",
    )
    args = parser.parse_args()

    problems: list[str] = []
    baseline_status = _git_status()
    baseline_hashes = {str(path.relative_to(ROOT)): _sha256(path) for path in CANONICAL_INPUTS}
    _print_status("baseline", baseline_status)

    if args.keep_tmp:
        temp_base = Path(tempfile.mkdtemp(prefix="license-gate-plant-"))
        print(f"temporary roots kept at {temp_base}")
        try:
            _run(temp_base, problems)
        except Exception as exc:  # the plant reports failure instead of hiding it in a traceback
            problems.append(f"plant raised {type(exc).__name__}: {exc}")
    else:
        with tempfile.TemporaryDirectory(prefix="license-gate-plant-") as td:
            try:
                _run(Path(td), problems)
            except Exception as exc:
                problems.append(f"plant raised {type(exc).__name__}: {exc}")

    exit_status = _git_status()
    exit_hashes = {str(path.relative_to(ROOT)): _sha256(path) for path in CANONICAL_INPUTS}
    _print_status("exit", exit_status)
    status_unchanged = exit_status == baseline_status
    hashes_unchanged = exit_hashes == baseline_hashes
    _proof(
        problems,
        "canonical-evidence",
        status_unchanged and hashes_unchanged,
        f"status_delta={'none' if status_unchanged else 'CHANGED'} "
        f"input_sha256_delta={'none' if hashes_unchanged else 'CHANGED'}",
    )

    for problem in problems:
        if not problem.startswith(("a:", "b:", "c:", "d:", "canonical-evidence:")):
            print("RED:", problem)
    if problems:
        print(f"RED: licence gate plant failed ({len(problems)} complaint(s))")
        return 1
    print("OK: all four licence/store plant proofs passed in isolated temporary roots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
