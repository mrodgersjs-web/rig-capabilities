#!/usr/bin/env python3
"""Recall delta-sync (v15): re-pull the wound cards already exported into
rig-communications-wounds/ and rewrite files whose source card changed in
app.recall.it. Never deletes; never discovers — new cards are added by hand,
then this keeps them fresh. No recall CLI -> honest BLOCKED exit.

Usage: python3 scripts/recall_delta_sync.py            # sync
       python3 scripts/recall_delta_sync.py --check    # report only, no writes
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RECALL = Path.home() / ".local" / "bin" / "recall"
WOUNDS = (Path(__file__).resolve().parents[1] /
          "capabilities/skills/rig-communications-wounds")
LOG = Path(__file__).resolve().parents[1] / "data/comms/recall_delta.log"
UUID = re.compile(r"^---\s*([0-9a-f-]{36})\s*---\s*$", re.M)


def card_body(cid: str) -> str | None:
    r = subprocess.run([str(RECALL), "card", cid], capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 and r.stdout.strip() else None


def main() -> int:
    if not RECALL.exists():
        print(json.dumps({"status": "BLOCKED:recall-cli", "missing": str(RECALL)}))
        return 2
    check_only = "--check" in sys.argv
    changed, unchanged, missing, broken = [], 0, [], []
    for f in sorted(WOUNDS.rglob("*.md")):
        m = UUID.search(f.read_text())
        if not m:
            broken.append(f.name)  # header-only files (READMEs) have no card id
            continue
        cid = m.group(1)
        body = card_body(cid)
        if body is None:
            missing.append(cid)  # card vanished upstream — file kept, logged
            continue
        new_hash = hashlib.sha256(body.encode()).hexdigest()[:12]
        side = f.with_suffix(f.suffix + ".hash")
        old = side.read_text().strip() if side.exists() else ""
        if not old:  # bootstrap: record baseline hash, trust the exported file
            if not check_only:
                side.write_text(new_hash)
            unchanged += 1
            continue
        if old == new_hash:
            unchanged += 1
            continue
        changed.append(f.name)
        if not check_only:
            tmp = f.with_suffix(".tmp")
            tmp.write_text(f.read_text() + f"\n\n<!-- refreshed {time.strftime('%F %T')} -->\n\n" + body)
            tmp.replace(f)  # atomic
            side.write_text(new_hash)
    entry = {"ts": time.strftime("%FT%T"), "changed": changed, "unchanged": unchanged,
             "missing_upstream": missing, "no_card_id": broken, "mode": "check" if check_only else "sync"}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
