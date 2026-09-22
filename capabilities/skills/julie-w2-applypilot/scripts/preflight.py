#!/usr/bin/env python3
"""Read-only dependency and actual receipt integrity check; no inference or sends."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def verify_receipts(root, now=None):
    root = Path(root).resolve()
    now = now or datetime.now(timezone.utc)
    failures, valid, legacy = [], {}, set()
    try:
        rows = [json.loads(line) for line in (root / "application-events.jsonl").read_text().splitlines() if line.strip()]
    except (OSError, ValueError) as exc:
        return {"pass": False, "failures": [f"application ledger: {type(exc).__name__}"]}
    for row in rows:
        if not isinstance(row, dict):
            failures.append("non-object application event")
            continue
        if row.get("status") != "submitted":
            continue
        company, req = row.get("company"), row.get("requisition")
        if not isinstance(company, str) or not company.strip() or not isinstance(req, str) or not req.strip():
            failures.append("submitted event without employer/requisition")
            continue
        key = (company.casefold().strip(), req.casefold().strip())
        receipt = row.get("receipt")
        if not isinstance(receipt, dict) or not receipt.get("kind") or not receipt.get("reference"):
            legacy.add(key)
            continue
        try:
            file = Path(receipt["readback_path"]).resolve()
            file.relative_to(root)
            payload = file.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            if receipt["reference"] != "sha256:" + digest:
                raise ValueError("receipt hash mismatch")
            if req.casefold() not in payload.decode("utf-8").casefold():
                raise ValueError("exact requisition absent from readback")
            at = datetime.fromisoformat(row["occurred_at"].replace("Z", "+00:00"))
            if at.tzinfo is None or at > now:
                raise ValueError("invalid or future event timestamp")
            previous = valid.get(key)
            if previous is None or at < previous["at"]:
                valid[key] = {"company": company, "requisition": req, "at": at, "evidence_sha256": digest}
        except (OSError, KeyError, TypeError, ValueError, UnicodeError) as exc:
            failures.append(f"{company}/{req}: {type(exc).__name__}: {str(exc)[:120]}")
    for company, req in legacy - set(valid):
        failures.append(f"{company}/{req}: submitted without typed verified receipt")
    local = now.astimezone(ZoneInfo("America/Denver"))
    week = (local - timedelta(days=local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    counts = {
        "verified_total": len(valid),
        "confirmed_this_denver_week": sum(v["at"] >= week for v in valid.values()),
        "rolling_seven_days": sum(v["at"] >= now - timedelta(days=7) for v in valid.values()),
        "week_starts_at": week.isoformat(),
    }
    return {"pass": not failures, "failures": failures, **counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path.home() / ".applypilot"))
    parser.add_argument("--ledger-only", action="store_true")
    args = parser.parse_args()
    package = Path(__file__).resolve().parents[1]
    missing, tools = [], {}
    if not args.ledger_only:
        manifest = json.loads((package / "manifest.json").read_text())
        for item in manifest["required_files"]:
            path = Path(item).expanduser()
            if not path.is_file():
                missing.append(str(path))
        for name in manifest["required_commands"]:
            tools[name] = shutil.which(name)
            if tools[name] is None:
                missing.append("command:" + name)
    receipt = verify_receipts(args.root)
    result = {
        "schema": "julie.hermes.preflight.v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not missing and receipt["pass"] else "BLOCKED",
        "missing_dependencies": missing,
        "commands": tools,
        "receipts": receipt,
        "browser_execution_tested": False,
        "model_inference_tested": False,
        "new_application_submitted": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
