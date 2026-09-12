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



def open_live(repo: Path, path: str) -> "BuildIndex":
    """Bind an index to the LIVE authority: cells from the pack generator,
    pack sha from the golden manifest. There is no unbound construction path
    for production use — the constructor stays raw for tests only."""
    from rig_capabilities.criteria_pack import build_rows
    sha = current_pack_sha(repo)
    cells = {r["cell_id"] for r in build_rows()}
    return BuildIndex(path, cells, sha)

class BuildIndex:
    def __init__(self, path: str, valid_cells: set[str], pack_sha: str):
        self.path = path
        self.valid_cells = valid_cells
        self.pack_sha = pack_sha

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

    # -- storage ----------------------------------------------------------
    def _load(self) -> tuple[str | None, dict[str, dict]]:
        """Returns (generation, records). Generation is index-level metadata
        (the first line), never derived per record. Duplicate cell rows or a
        mixed record/generation pair are corruption and raise."""
        gen: str | None = None
        recs: dict[str, dict] = {}
        meta_seen = 0
        body_started = False
        if os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    r = json.loads(line)
                    if "_meta" in r:
                        meta_seen += 1
                        if meta_seen > 1:
                            raise IndexError_(
                                "duplicate _meta header; corrupt")
                        if body_started:
                            raise IndexError_(
                                "late _meta header after records; corrupt "
                                "(never last-wins)")
                        gen = r["_meta"]["pack_sha"]
                        continue
                    body_started = True
                    if r["cell_id"] in recs:
                        raise IndexError_(
                            f"duplicate row for {r['cell_id']}; "
                            "index corrupt (never last-wins)")
                    recs[r["cell_id"]] = r
            if recs and meta_seen == 0:
                raise IndexError_(
                    "records without _meta header; corrupt (deleting the "
                    "header is not an adoption path)")
            if gen is not None:
                bad = {cid for cid, r in recs.items()
                       if r["pack_sha"] != gen}
                if bad:
                    raise IndexError_(
                        f"records {sorted(bad)[:3]} disagree with index "
                        f"generation {gen[:12]}; corrupt")
        return gen, recs

    def _require_writer_gen(self, gen: str | None) -> None:
        """Both insert and update demand writer pack == index generation."""
        if gen is not None and self.pack_sha != gen:
            raise IndexError_(
                f"stale-writer rejected: writer pack "
                f"{self.pack_sha[:12]} != index generation {gen[:12]}; "
                "advance via migrate(), never per-cell CAS")

    def _save(self, gen: str | None, recs: dict[str, dict]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            if gen is not None:
                f.write(json.dumps({"_meta": {"pack_sha": gen}},
                                   sort_keys=True) + "\n")
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
            gen, recs = self._load()
            self._require_writer_gen(gen)
            if cell_id in recs:
                raise IndexError_(f"duplicate cell record: {cell_id}")
            recs[cell_id] = {"cell_id": cell_id, "build_ref": build_ref,
                             "pack_sha": self.pack_sha, "version": 1}
            self._save(self.pack_sha, recs)
        return "inserted"

    def update(self, cell_id: str, build_ref: str, expected_sha: str) -> str:
        """CAS *within* the current generation: writer must match the index
        generation, and expected_sha must match the stored record."""
        with self._locked():
            gen, recs = self._load()
            self._require_writer_gen(gen)
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
            self._save(self.pack_sha, recs)
        return "updated"

    def migrate(self, expected_from: str) -> int:
        """The ONLY way to advance generation: one atomic rewrite of every
        record under a new index-level pack_sha."""
        with self._locked():
            gen, recs = self._load()
            if gen != expected_from:
                raise IndexError_(
                    f"migrate base {expected_from[:12]} != index generation "
                    f"{str(gen)[:12]}")
            for cid, r in recs.items():
                r["pack_sha"] = self.pack_sha
                r["version"] += 1
            self._save(self.pack_sha if (recs or gen is not None) else None,
                       recs)
        return len(recs)


def selftest(argv=None) -> int:
    errs = []
    valid = {f"C{i:03d}" for i in range(1, 589)}
    sha_a = hashlib.sha256(b"pack-a").hexdigest()
    sha_b = hashlib.sha256(b"pack-b").hexdigest()
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "index.jsonl")
        idx = BuildIndex(p, valid, sha_a)
        idx.insert("C001", "build:1")
        idx.insert("C002", "build:2")
        try:
            idx.insert("C001", "build:3")
            errs.append("duplicate accepted")
        except IndexError_ as e:
            if "duplicate" not in str(e):
                errs.append(f"dup wrong reason: {e}")
        try:
            idx.insert("C999", "build:4")
            errs.append("unknown cell accepted")
        except IndexError_ as e:
            if "authority" not in str(e):
                errs.append(f"unknown wrong reason: {e}")
        # stale-writer update: pack-b writer against generation-a index —
        # refused even with a per-record base that matches, because CAS may
        # not migrate one record out of a multi-record generation.
        idx2 = BuildIndex(p, valid, sha_b)
        try:
            idx2.update("C001", "build:5", expected_sha=sha_a)
            errs.append("cross-generation CAS accepted")
        except IndexError_ as e:
            if "stale-writer" not in str(e):
                errs.append(f"cross-gen update wrong reason: {e}")
        # stale-writer insert likewise
        try:
            idx2.insert("C003", "build:6")
            errs.append("stale-writer insert accepted")
        except IndexError_ as e:
            if "stale-writer" not in str(e):
                errs.append(f"stale insert wrong reason: {e}")
        # honest CAS inside generation a: version bumps, generation stays a
        if idx.update("C001", "build:7", expected_sha=sha_a) != "updated":
            errs.append("valid CAS rejected")
        gen, recs = idx._load()
        if gen != sha_a or recs["C001"]["version"] != 2:
            errs.append(f"CAS moved generation or version: {gen} {recs}")
        # migration is atomic and explicit: every record moves to b
        if idx2.migrate(expected_from=sha_a) != 2:
            errs.append("migrate count wrong")
        gen, recs = idx2._load()
        if gen != sha_b or any(r["pack_sha"] != sha_b for r in recs.values()):
            errs.append(f"migrate not atomic: {gen}")
        # wrong-base migrate refused
        try:
            idx.migrate(expected_from=sha_a)
            errs.append("stale migrate accepted")
        except IndexError_ as e:
            if "migrate base" not in str(e):
                errs.append(f"migrate wrong reason: {e}")
        # post-migration writers on b work
        idx2.insert("C003", "build:8")
        # durable rows ordered by cell_id — checked on the clean store,
        # BEFORE any corruption (json sort_keys orders fields, not rows).
        body = [json.loads(l) for l in open(p) if '"_meta"' not in l]
        ids = [r["cell_id"] for r in body]
        if '"_meta"' not in open(p).readline() or ids != sorted(ids):
            errs.append("index rows not ordered by cell_id after meta")
        # duplicate rows on disk are corruption, not last-wins
        with open(p, "a") as f:
            f.write(json.dumps({"cell_id": "C001", "build_ref": "evil",
                                "pack_sha": sha_b, "version": 99}) + "\n")
        try:
            idx2._load()
            errs.append("duplicate rows silently overwritten")
        except IndexError_ as e:
            if "duplicate row" not in str(e):
                errs.append(f"dup-row wrong reason: {e}")
        # record disagreeing with the generation is corruption too
        p3 = os.path.join(td, "index3.jsonl")
        with open(p3, "w") as f:
            f.write(json.dumps({"_meta": {"pack_sha": sha_b}},
                               sort_keys=True) + "\n")
            f.write(json.dumps({"cell_id": "C001", "build_ref": "x",
                                "pack_sha": sha_a, "version": 1},
                               sort_keys=True) + "\n")
        try:
            BuildIndex(p3, valid, sha_b)._load()
            errs.append("mixed record accepted")
        except IndexError_ as e:
            if "disagree" not in str(e):
                errs.append(f"mixed wrong reason: {e}")
        # header deletion is corruption, not a generation-adoption path
        # (built from p3's single clean row — p is already corrupted here)
        p4 = os.path.join(td, "index4.jsonl")
        with open(p4, "w") as f:
            f.write('{"build_ref": "x", "cell_id": "C001", "pack_sha": '
                    '"' + sha_a + '", "version": 1}\n')
        try:
            BuildIndex(p4, valid, sha_b).insert("C100", "adopt")
            errs.append("header-deletion adoption accepted")
        except IndexError_ as e:
            if "without _meta" not in str(e):
                errs.append(f"header-del wrong reason: {e}")
        # duplicate metadata rows refused (no last-wins)
        p5 = os.path.join(td, "index5.jsonl")
        with open(p5, "w") as f:
            for sha in (sha_a, sha_b):
                f.write(json.dumps({"_meta": {"pack_sha": sha}},
                                   sort_keys=True) + "\n")
        try:
            BuildIndex(p5, valid, sha_b)._load()
            errs.append("duplicate _meta accepted")
        except IndexError_ as e:
            if "duplicate _meta" not in str(e):
                errs.append(f"dup-meta wrong reason: {e}")
    print(json.dumps({"ok": not errs, "errors": errs,
                      "cells_valid": len(valid)}))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(selftest())
