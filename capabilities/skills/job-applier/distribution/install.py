#!/usr/bin/env python3
"""Install, verify, or undo this local Aside skill bundle without network access."""
import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_map(root):
    if root.is_symlink():
        raise ValueError(f"Symlink refused: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink refused: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def check_bundle(bundle):
    manifest = json.loads((bundle / "MANIFEST.json").read_text())
    expected = manifest["files"]
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Empty or invalid bundle manifest")
    actual = file_map(bundle)
    actual.pop("MANIFEST.json", None)
    if actual != expected:
        raise ValueError("Bundle files do not match MANIFEST.json; no files installed")
    names = manifest["skills"]
    if not names or len(names) != len(set(names)):
        raise ValueError("Invalid skill list")
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("Unsafe skill name")
        if not (bundle / "skills" / name / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {name}")
    return manifest


def safe_root(home):
    home = home.expanduser().resolve()
    root = home / ".aside/u/0/skills/user"
    for path in [home / ".aside", home / ".aside/u", home / ".aside/u/0",
                 home / ".aside/u/0/skills", root, home / ".job-applier-installs"]:
        if path.is_symlink():
            raise ValueError(f"Symlink refused: {path}")
    return home, root


def save_receipt(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    temp.replace(path)


def install(bundle, home, replace):
    manifest = check_bundle(bundle)
    home, root = safe_root(home)
    plans = []
    for name in manifest["skills"]:
        source = bundle / "skills" / name
        target = root / name
        wanted = file_map(source)
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError(f"Unsupported existing target: {target}")
        exists = target.exists()
        current = file_map(target) if exists else None
        if exists and current == wanted:
            plans.append({"name": name, "status": "unchanged", "files": wanted, "prior_files": current})
        elif exists and not replace:
            raise ValueError(f"Existing skill differs: {target}. Re-run with --replace to back it up first.")
        else:
            plans.append({"name": name, "status": "replace" if exists else "install", "files": wanted, "prior_files": current})
    if all(p["status"] == "unchanged" for p in plans):
        return {"status": "already-installed", "skills": [p["name"] for p in plans]}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    receipt_dir = home / ".job-applier-installs" / stamp
    receipt_dir.mkdir(parents=True)
    root.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / "receipt.json"
    receipt = {"version": 1, "status": "installing", "created_at": stamp,
               "home": str(home), "root": str(root), "entries": plans,
               "bundle_manifest_sha256": digest(bundle / "MANIFEST.json")}
    save_receipt(receipt_path, receipt)
    for entry in plans:
        if entry["status"] == "unchanged":
            continue
        name = entry["name"]
        target = root / name
        current = file_map(target) if target.exists() else None
        if current != entry["prior_files"]:
            raise ValueError(f"Target changed during install planning: {target}; retain the receipt for rollback")
        if target.exists():
            backup = receipt_dir / "backups" / name
            backup.parent.mkdir(exist_ok=True)
            entry["backup"] = str(backup)
            save_receipt(receipt_path, receipt)
            target.rename(backup)
        save_receipt(receipt_path, receipt)
        shutil.copytree(bundle / "skills" / name, target)
        if file_map(target) != entry["files"]:
            raise ValueError(f"Installed hash mismatch: {target}; retain receipt for recovery")
        entry["installed"] = True
        save_receipt(receipt_path, receipt)
    receipt["status"] = "installed"
    save_receipt(receipt_path, receipt)
    return {"status": "installed", "receipt": str(receipt_path), "root": str(root), "skills": len(plans)}


def uninstall(receipt_path, home, preserve_edits):
    home, root = safe_root(home)
    receipt_path = receipt_path.expanduser().resolve()
    receipts_root = home / ".job-applier-installs"
    if receipt_path.parent.parent != receipts_root or receipt_path.name != "receipt.json":
        raise ValueError("Receipt must belong to this home's .job-applier-installs directory")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("home") != str(home) or receipt.get("root") != str(root):
        raise ValueError("Receipt home/root mismatch")
    if receipt.get("status") == "uninstalled":
        return {"status": "already-uninstalled"}
    for entry in receipt["entries"]:
        name = entry["name"]
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("Unsafe receipt name")
        if entry["status"] == "unchanged" or entry.get("restored"):
            continue
        target = root / name
        current = file_map(target) if target.exists() else None
        if not entry.get("backup") and not entry.get("installed") and "prior_files" in entry and current == entry["prior_files"]:
            entry["restored"] = True
            save_receipt(receipt_path, receipt)
            continue
        if entry.get("backup"):
            backup = receipt_path.parent / "backups" / name
            if str(backup) != entry["backup"]:
                raise ValueError("Backup path does not belong to this installation receipt")
            if not backup.exists() and current == entry.get("prior_files"):
                entry["restored"] = True
                save_receipt(receipt_path, receipt)
                continue
        if current is not None and current != entry["files"] and not preserve_edits:
            raise ValueError(f"Installed files changed: {target}. Use --preserve-edits to archive them before restoring.")
        if entry.get("backup"):
            backup = receipt_path.parent / "backups" / name
            if str(backup) != entry["backup"] or file_map(backup) != entry["prior_files"]:
                raise ValueError(f"Backup mismatch: {backup}; no restore performed")
    for entry in receipt["entries"]:
        if entry["status"] == "unchanged" or entry.get("restored"):
            continue
        name = entry["name"]
        target = root / name
        if target.exists():
            saved = receipt_path.parent / "removed" / name
            saved.parent.mkdir(exist_ok=True)
            if saved.exists():
                raise ValueError(f"Recovery archive already exists: {saved}")
            target.rename(saved)
            entry["removed_to"] = str(saved)
            save_receipt(receipt_path, receipt)
        if entry.get("backup"):
            (receipt_path.parent / "backups" / name).rename(target)
        entry["restored"] = True
        save_receipt(receipt_path, receipt)
    receipt["status"] = "uninstalled"
    save_receipt(receipt_path, receipt)
    return {"status": "uninstalled", "receipt": str(receipt_path), "removed_files_preserved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["verify", "install", "uninstall", "canonical-install"])
    parser.add_argument("--home", type=Path, default=Path.home(), help="Recipient home; use a temporary home for testing")
    parser.add_argument("--replace", action="store_true", help="Back up differing existing skills before install")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--preserve-edits", action="store_true")
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    if args.action == "canonical-install":
        source = Path(__file__).resolve().parent.parent
        if not (source / "SKILL.md").is_file() or not (source / "steps").is_dir():
            raise ValueError("canonical-install requires the canonical Job Applier family")
        with tempfile.TemporaryDirectory(prefix="job-applier-canonical-") as scratch:
            staged = Path(scratch)
            shutil.copytree(source, staged / "skills/job-applier",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            manifest = {"skills": ["job-applier"], "files": file_map(staged)}
            (staged / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
            result = install(staged, args.home, args.replace)
    elif args.action == "verify":
        result = {"status": "verified", "skills": check_bundle(bundle)["skills"]}
    elif args.action == "install":
        result = install(bundle, args.home, args.replace)
    else:
        if not args.receipt:
            parser.error("uninstall requires --receipt")
        result = uninstall(args.receipt, args.home, args.preserve_edits)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCK", "error": str(exc)}), file=sys.stderr)
        sys.exit(2)
