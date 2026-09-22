#!/usr/bin/env python3
"""D85 rollout launcher: manifest-driven verified copy (candidate -> live).

Unscored orchestration layer for the certified d85_rollout kernel. Deterministic,
fail-closed, hash-verified in both directions. VERIFY_ONLY until EXECUTE is passed.

Usage:
  d85_rollout_launcher.py MANIFEST RECEIPT
  d85_rollout_launcher.py MANIFEST RECEIPT EXECUTE
"""
import hashlib
import json
import stat
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d85_rollout_worker import verify_parts  # noqa: E402


def sha_hex(data):
    return hashlib.sha256(data).hexdigest()


def mode_octal(path):
    if not path.is_file():
        return "missing"
    return format(stat.S_IMODE(path.stat().st_mode), "04o")


def main(argv):
    if len(argv) != 4 or argv[3] != "EXECUTE" and argv[3] != "VERIFY_ONLY":
        print(json.dumps({"status": "REFUSED", "reason": "usage: MANIFEST RECEIPT [EXECUTE|VERIFY_ONLY]"}))
        return 2
    manifest_path = Path(argv[1])
    receipt_path = Path(argv[2])
    mode = argv[3]
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "rig.d85.rollout-manifest.v5":
        print(json.dumps({"status": "REFUSED", "reason": "manifest schema not v5"}))
        return 2
    if manifest.get("status") != "DORMANT_NOT_AUTHORIZED":
        print(json.dumps({"status": "REFUSED", "reason": "manifest is not the dormant rollout packet"}))
        return 2
    candidate = Path(manifest["candidate"])
    live = Path(manifest["live"])
    copy_rows = [row for row in manifest["files"] if row["action"] == "COPY"]
    records = []
    failures = []
    copied = 0
    for row in copy_rows:
        rel = row["path"]
        src = candidate / rel
        dst = live / rel
        if not src.is_file():
            failures.append({"path": rel, "stage": "candidate-missing"})
            continue
        src_bytes = src.read_bytes()
        src_mode = mode_octal(src)
        expected_mode_octal = format(row["candidate"]["mode"], "04o")
        src_digest = sha_hex(src_bytes)
        digest_ok = src_digest == row["candidate"]["sha256"]
        mode_ok = src_mode == expected_mode_octal
        verdict = verify_parts(digest_ok and mode_ok)
        if not verdict:
            failures.append({"path": rel, "stage": "candidate-drift", "digest_ok": digest_ok, "mode_ok": mode_ok})
            continue
        record = {"path": rel, "candidate_sha256": row["candidate"]["sha256"], "candidate_mode": row["candidate"]["mode"]}
        if dst.is_file():
            record["live_before"] = sha_hex(dst.read_bytes())
            record["live_mode_before"] = mode_octal(dst)
        else:
            record["live_before"] = None
            record["live_mode_before"] = "missing"
        if mode == "EXECUTE":
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src_bytes)
            dst.chmod(row["candidate"]["mode"])
            written = sha_hex(dst.read_bytes())
            if written != row["candidate"]["sha256"] or mode_octal(dst) != row["candidate"]["mode"]:
                failures.append({"path": rel, "stage": "post-write-verify"})
                continue
            record["live_after"] = written
            copied = copied + 1
        records.append(record)
    ok = (not failures) and (copied == len(copy_rows) if mode == "EXECUTE" else True)
    receipt = {
        "schema": "rig.d85.install-receipt.v1",
        "manifest_sha256": sha_hex(manifest_bytes),
        "mode": mode,
        "copy_rows": len(copy_rows),
        "copied": copied,
        "failures": failures,
        "records": records,
        "installed": bool(mode == "EXECUTE" and ok),
        "activated": False,
        "pushed": False,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "INSTALL_OK" if ok else "INSTALL_FAILED", "mode": mode, "copied": copied, "rows": len(copy_rows), "failures": len(failures), "receipt": str(receipt_path)}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
