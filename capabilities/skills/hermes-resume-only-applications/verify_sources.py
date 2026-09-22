#!/usr/bin/env python3
"""Read-only source/dependency checks. No inference, browser actions or submissions."""
import hashlib
import json
from pathlib import Path
import shutil
import sys


def verify(manifest):
    results = []
    for name, source in manifest["sources"].items():
        path = Path(source["path"])
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        results.append({"source": name, "path": str(path), "status": "PASS" if actual == source["sha256"] else "BLOCK_MISSING_OR_CHANGED_SOURCE", "sha256": actual})
    return results


def main():
    manifest = json.loads((Path(__file__).parent / "sources.json").read_text())
    checks = verify(manifest)
    skills = {name: (Path.home()/".hermes/skills"/name/"SKILL.md").is_file() for name in ("job-application-cockpit", "rig-write-resumes", "application-packet-builder", "browser-skill")}
    ok = len(checks) == 3 and all(c["status"] == "PASS" for c in checks) and all(skills.values())
    print(json.dumps({"status": "PASS_SOURCE_BINDINGS_AND_SKILL_FILES" if ok else "BLOCK", "checks": checks, "skills": skills, "hermes_cli_found": bool(shutil.which("hermes")), "browser_cli_found": bool(shutil.which("bsk")), "browser_runtime": "NOT_TESTED_BY_THIS_SCRIPT; run bsk doctor", "application_execution": "NOT_RUN", "submission": False}, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
