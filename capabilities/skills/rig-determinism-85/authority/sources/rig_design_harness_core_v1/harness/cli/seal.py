from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

TRUSTED_PROOF_ROOT = Path.home() / ".rig" / "proof"

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _check_receipt(receipt_path: Path, root: Path, build: dict) -> tuple[bool, str]:
    trusted_root = TRUSTED_PROOF_ROOT.resolve()
    receipt_path = receipt_path.expanduser().resolve()
    if receipt_path.is_relative_to(root) or not receipt_path.is_relative_to(trusted_root):
        return False, f"receipt path must be under {trusted_root} and outside {root}"
    receipt = _read_json(receipt_path)
    if receipt is None:
        return False, "receipt is missing or invalid JSON"
    if receipt.get("schema_version") != "rig.proofpacket.v1":
        return False, "receipt schema is not rig.proofpacket.v1"
    proof_hash = receipt.get("proof_hash")
    unsigned = dict(receipt)
    unsigned.pop("proof_hash", None)
    expected_hash = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if proof_hash != expected_hash:
        return False, "proof_hash mismatch"
    manifest = root / "proof" / "manifest.json"
    if not manifest.is_file():
        return False, f"manifest missing: {manifest}"
    if receipt.get("manifest_sha256") != _sha256(manifest):
        return False, "manifest_sha256 mismatch"
    builder_family = str(build.get("builder_family") or "omp/task")
    sealed_by = receipt.get("sealed_by")
    if not isinstance(sealed_by, str) or not sealed_by or sealed_by == builder_family:
        return False, "sealed_by must name a non-builder family"
    return True, f"receipt={receipt_path} sealed_by={sealed_by}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="rdh seal")
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    build_file = args.build.expanduser().resolve()
    build = _read_json(build_file)
    if build is None:
        print(f"REFUSED build record is missing or invalid JSON: {build_file}")
        return 1

    root = Path(build.get("root") or build_file.parents[1]).expanduser().resolve()
    if args.check is not None:
        verified, detail = _check_receipt(args.check, root, build)
        print(f"{'VERIFIED' if verified else 'NOT VERIFIED'} {detail}")
        return 0 if verified else 1

    proof_dir = root / "proof"
    required = [
        proof_dir / "pytest-output.txt",
        build_file,
        root / "mutation_ledger.jsonl",
        root / "docs" / "decisions" / "ledger-bakeoff.md",
    ]
    bench = sorted((root / "golden").glob("*/bench.jsonl"))
    missing = [path for path in required if not path.is_file()]
    if not bench:
        missing.append(root / "golden" / "*" / "bench.jsonl")
    if missing:
        for path in missing:
            print(f"REFUSED missing artifact: {path}")
        return 1

    certificate = proof_dir / "d85-certificate.json"
    paths = [*required, *bench, *([certificate] if certificate.is_file() else [])]
    artifacts = {
        str(path.relative_to(root) if path.is_relative_to(root) else path): {
            "path": str(path),
            "sha256": _sha256(path),
        }
        for path in paths
    }
    manifest = {
        "schema_version": "rig.design_harness.manifest.v1",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
    }
    proof_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = proof_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    verifier = build.get("verifier") if isinstance(build.get("verifier"), dict) else {}
    seal_request = {
        "schema_version": "rig.design_harness.seal_request.v1",
        "manifest_path": str(manifest_path),
        "manifest_sha256": _sha256(manifest_path),
        "build_record_sha256": _sha256(build_file),
        "certificate_sha256": _sha256(certificate) if certificate.is_file() else "absent",
        "verifier_verdict_path": str(
            verifier.get("verdict_path") or verifier.get("transcript_path") or "absent"
        ),
        "builder_family": str(build.get("builder_family") or "omp/task"),
    }
    request_path = proof_dir / "seal-request.json"
    request_path.write_text(json.dumps(seal_request, indent=2, sort_keys=True) + "\n")
    print("MANIFEST READY — seal via the conductor's official ProofPacket sealer")
    return 0
