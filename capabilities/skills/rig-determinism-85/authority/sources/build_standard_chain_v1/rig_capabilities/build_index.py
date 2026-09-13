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
from pathlib import Path

if __package__ in (None, ""):  # direct `python3 rig_capabilities/build_index.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class IndexError_(ValueError):
    pass


def current_pack_sha(repo: Path) -> str:
    """The golden manifest is the only source for the current pack sha."""
    man = repo / "runs/agentic-stack-buildout/packs/criteria-v1.sha256"
    if not man.exists():
        raise IndexError_("golden manifest missing; index cannot be trusted")
    first = man.read_text().splitlines()[0]
    return first.split("  ", 1)[0]



def open_live(repo: Path, path: str) -> "BuildIndex":
    """Bind an index to a SINGLE authority: the verified golden bytes.
    `criteria_pack.verify` checks the golden against its manifest (hash,
    filename, rows), the manifest's prov digest, every recorded input
    hash, AND byte-equality with freshly regenerated content — so a
    generator that drifted from the golden FAILS CLOSED here instead of
    rebinding the handle to new cells under the old sha (the s10
    dual-authority defect). Cells and pack sha come from the same
    verified bytes. No unbound construction path exists for production
    use — the constructor stays raw for tests only."""
    from rig_capabilities import criteria_pack
    golden = repo / "runs/agentic-stack-buildout/packs/criteria-v1.jsonl"
    errs, info = criteria_pack.verify(golden)
    if errs:
        raise IndexError_(f"golden pack verification failed: {errs[0]}")
    cells = {json.loads(ln)["cell_id"]
             for ln in golden.read_bytes().decode().splitlines() if ln.strip()}
    return BuildIndex(path, cells, info["sha256"], repo)

class BuildIndex:
    def __init__(self, path: str, valid_cells: set[str], pack_sha: str,
                 repo: Path | None = None):
        self.path = path
        self.valid_cells = valid_cells
        self.pack_sha = pack_sha
        self.repo = repo

    def _assert_live(self) -> None:
        """A handle opened before a golden promotion must refuse, not
        write into the new generation under the old sha. Re-reads the
        manifest on every mutation; raw test handles (repo=None) skip."""
        if self.repo is not None:
            live = current_pack_sha(self.repo)
            if live != self.pack_sha:
                raise IndexError_(
                    f"handle bound to stale pack {self.pack_sha[:12]}; "
                    f"manifest now says {live[:12]}; reopen and migrate")

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
            self._assert_live()
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
            self._assert_live()
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
            self._assert_live()
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
    # freshness: a handle opened under an old manifest must refuse every
    # mutation after a promotion; reopen + migrate is the only advance.
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        man = repo / "runs/agentic-stack-buildout/packs/criteria-v1.sha256"
        man.parent.mkdir(parents=True)
        man.write_text(sha_a + "  criteria-v1.jsonl  rows=588\n")
        idx = BuildIndex(str(repo / "idx.jsonl"), valid, sha_a, repo)
        idx.insert("C001", "b1")
        man.write_text(sha_b + "  criteria-v1.jsonl  rows=588\n"
                       + "prov  " + "0" * 64 + "\n")
        try:
            idx.insert("C002", "b2")
            errs.append("stale handle wrote after promotion")
        except IndexError_ as e:
            if "stale pack" not in str(e):
                errs.append(f"stale-handle refusal misnamed: {e}")
        idx2 = BuildIndex(str(repo / "idx.jsonl"), valid, sha_b, repo)
        try:
            idx2.update("C001", "b1b", sha_a)
            errs.append("cross-generation update accepted")
        except IndexError_ as e:
            if "stale-writer" not in str(e):
                errs.append(f"cross-gen rejection misnamed: {e}")
        if idx2.migrate(sha_a) != 1:
            errs.append("migrate after promotion rewrote wrong count")
    # open_live single authority: cells come from the VERIFIED GOLDEN
    # BYTES, never the live generator. Healthy open serves 588 golden
    # cells; a generator drifted against the golden must fail closed.
    from rig_capabilities import criteria_pack as _cp
    real_repo = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as td:
        ix = open_live(real_repo, os.path.join(td, "live.jsonl"))
        if len(ix.valid_cells) != 588 or ix.pack_sha != current_pack_sha(real_repo):
            errs.append("open_live not bound to golden 588/manifest sha")
        orig = _cp.pack_bytes
        _cp.pack_bytes = lambda: b"drift\n"
        try:
            open_live(real_repo, os.path.join(td, "live2.jsonl"))
            errs.append("open_live accepted drifted source authority")
        except IndexError_ as e:
            if "regenerated" not in str(e):
                errs.append(f"drift refusal misnamed: {e}")
        finally:
            _cp.pack_bytes = orig
    print(json.dumps({"ok": not errs, "errors": errs,
                      "cells_valid": len(valid)}))
    return 0 if not errs else 1


if __name__ == "__main__":
    _a = sys.argv[1:]
    if _a and _a[0] not in ("selftest", "--help"):
        print("usage: build_index.py [selftest|--help]", file=sys.stderr)
        sys.exit(2)
    sys.exit(selftest())
