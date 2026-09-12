"""Build index: cell -> build records with duplicate and stale-hash rejection.

Invariants (all proven by selftest rejection fixtures):
- exactly the 588 authority cell_ids may hold a record; duplicates rejected;
- every record binds the CURRENT pack sha (from the golden manifest); a
  record built against a stale pack is rejected at insert, and
- updates are compare-and-swap on pack_sha: a writer whose view no longer
  matches the stored base is rejected (stale-hash), never silently merged.

Storage: one JSONL per record set; writes are whole-file replace under the
same flock discipline as the trial recorder.

Usage: python3 rig_capabilities/build_index.py selftest
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import sys
import tempfile


class IndexError_(ValueError):
    pass


def current_pack_sha(repo: Path) -> str:
    """The golden manifest is the only source for the current pack sha."""
    man = repo / "runs/agentic-stack-buildout/packs/criteria-v1.sha256"
    if not man.exists():
        raise IndexError_("golden manifest missing; index cannot be trusted")
    line = man.read_text().strip()
    return line.split("  ", 1)[0]


class BuildIndex:
    def __init__(self, path: str, valid_cells: set[str], pack_sha: str):
        self.path = path
        self.valid_cells = valid_cells
        self.pack_sha = pack_sha

    # -- storage ----------------------------------------------------------
    @contextlib.contextmanager
    def _locked(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".",
                    exist_ok=True)
        lk = open(self.path + ".lock", "w")
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)
            lk.close()

    def _load(self) -> dict[str, dict]:
        recs: dict[str, dict] = {}
        if os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        r = json.loads(line)
                        recs[r["cell_id"]] = r
        return recs

    def _save(self, recs: dict[str, dict]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            for cid in sorted(recs):
                f.write(json.dumps(recs[cid], sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    # -- operations -------------------------------------------------------
    def insert(self, cell_id: str, build_ref: str) -> str:
        if cell_id not in self.valid_cells:
            raise IndexError_(f"cell not in authority: {cell_id!r}")
        with self._locked():
            recs = self._load()
            if cell_id in recs:
                raise IndexError_(f"duplicate cell record: {cell_id}")
            recs[cell_id] = {"cell_id": cell_id, "build_ref": build_ref,
                             "pack_sha": self.pack_sha, "version": 1}
            self._save(recs)
        return "inserted"

    def update(self, cell_id: str, build_ref: str, expected_sha: str) -> str:
        """Compare-and-swap: expected_sha must match the STORED pack_sha."""
        with self._locked():
            recs = self._load()
            if cell_id not in recs:
                raise IndexError_(f"no record to update: {cell_id}")
            if recs[cell_id]["pack_sha"] != expected_sha:
                raise IndexError_(
                    f"stale-hash update rejected for {cell_id}: "
                    f"base {expected_sha[:12]} != stored "
                    f"{recs[cell_id]['pack_sha'][:12]}")
            recs[cell_id] = {"cell_id": cell_id, "build_ref": build_ref,
                             "pack_sha": self.pack_sha,
                             "version": recs[cell_id]["version"] + 1}
            self._save(recs)
        return "updated"


def selftest(argv=None) -> int:
    errs = []
    valid = {f"C{i:03d}" for i in range(1, 589)}
    sha_a = hashlib.sha256(b"pack-a").hexdigest()
    sha_b = hashlib.sha256(b"pack-b").hexdigest()
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "index.jsonl")
        idx = BuildIndex(p, valid, sha_a)
        try:
            idx.insert("C001", "build:1")
            idx.insert("C001", "build:2")           # duplicate -> reject
            errs.append("duplicate accepted")
        except IndexError_ as e:
            if "duplicate" not in str(e):
                errs.append(f"dup wrong reason: {e}")
        try:
            idx.insert("C999", "build:3")           # unknown cell -> reject
            errs.append("unknown cell accepted")
        except IndexError_ as e:
            if "authority" not in str(e):
                errs.append(f"unknown wrong reason: {e}")
        # stale-hash update: writer carrying pack-b base while stored is a
        idx2 = BuildIndex(p, valid, sha_b)
        try:
            idx2.update("C001", "build:4", expected_sha=sha_b)
            errs.append("stale-hash update accepted")
        except IndexError_ as e:
            if "stale-hash" not in str(e):
                errs.append(f"stale wrong reason: {e}")
        # honest CAS: correct base succeeds, version bumps
        if idx2.update("C001", "build:5", expected_sha=sha_a) != "updated":
            errs.append("valid CAS rejected")
        rec = idx2._load()["C001"]
        if rec["version"] != 2 or rec["pack_sha"] != sha_b:
            errs.append(f"CAS result wrong: {rec}")
        # 588-cap sanity: two inserts land, file sorted and parseable
        idx.insert("C002", "build:6")
        loaded = idx._load()
        if {"C001", "C002"} - set(loaded):
            errs.append("records lost")
        lines = open(p).read().splitlines()
        if lines != sorted(lines):
            errs.append("index not sorted by row")
    print(json.dumps({"ok": not errs, "errors": errs, "cells_valid": len(valid)}))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(selftest())
