"""SkillOS v5: keys conservation, store fail-closed, orphan/witness/receipt plants."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rig_capabilities.catalog import Repo
import rig_capabilities.skillos as skillos
from rig_capabilities.skillos import (
    UNIVERSE,
    WITNESS_DIR,
    check_universe,
    restore_blob,
    doors_count,
    orphan_replay,
    provenance,
    restore_recipe,
    witness_strict,
)


class SkillosV5(unittest.TestCase):
    def setUp(self):
        self.repo = Repo(REPO)

    @staticmethod
    def _manifest(entries: dict[str, bytes]) -> str:
        digest = hashlib.sha256()
        for name, data in sorted(entries.items()):
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(data)
        return digest.hexdigest()

    @staticmethod
    def _snapshot_sha(entries: dict[str, bytes]) -> str:
        digest = hashlib.sha256()
        for name, data in sorted(entries.items()):
            digest.update(name.encode())
            digest.update(hashlib.sha256(data).hexdigest()[:12].encode())
        return digest.hexdigest()[:12]

    def _git_source(
            self, base: Path, files: dict[str, bytes],
            url: str = "https://example.invalid/source.git",
    ) -> tuple[Path, str]:
        source = base / "source"
        source.mkdir(parents=True)
        for name, data in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
               "GIT_CONFIG_SYSTEM": os.devnull, "HOME": str(base)}
        git = ["git", "-c", "core.hooksPath=" + os.devnull]
        subprocess.run([*git, "init", "--quiet", str(source)], check=True, env=env)
        subprocess.run(
            [*git, "-C", str(source), "remote", "add", "origin", url],
            check=True, env=env,
        )
        subprocess.run([*git, "-C", str(source), "add", "."], check=True, env=env)
        subprocess.run(
            [*git, "-C", str(source),
             "-c", "user.name=SkillOS Test",
             "-c", "user.email=skillos@example.invalid",
             "commit", "--quiet", "-m", "fixture"],
            check=True, env=env,
        )
        commit = subprocess.check_output(
            [*git, "-C", str(source), "rev-parse", "HEAD"],
            env=env, text=True,
        ).strip()
        return source, commit

    def _file_recipe(self, path: str, data: bytes, commit: str) -> dict:
        return {
            "status": "recipe",
            "type": "git",
            "kind": "skill",
            "url": "https://example.invalid/source.git",
            "commit": commit,
            "path": path,
            "payload_scope": "file",
            "catalog_sha": hashlib.sha256(data).hexdigest()[:12],
            "snapshot_sha": hashlib.sha256(data).hexdigest()[:12],
            "n_files": 1,
            "tree_manifest": self._manifest({Path(path).name: data}),
        }

    @staticmethod
    def _copy_fetch(source: Path):
        def fetch(_url: str, _commit: str, work: Path) -> dict:
            shutil.copytree(source, work)
            return {"ok": True, "exit_code": 0}
        return fetch

    def test_doors_are_50(self):
        d = doors_count(self.repo)
        self.assertTrue(d["ok"], d)
        self.assertEqual(d["count"], 50)

    def test_provenance_denies_cli_source(self):
        p = provenance(self.repo)
        self.assertTrue(p["ok"], p)

    def test_plant_drop_keys_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skillos_dir = root / "docs/skillos"
            skillos_dir.mkdir(parents=True)
            row = {
                "kind": "skill", "id": "kept", "sha": "a" * 12,
                "store": {"status": "unresolved", "payload_scope": "unknown",
                          "catalog_sha": "a" * 12, "reason": "no evidence"},
            }
            (skillos_dir / "universe.jsonl").write_text(json.dumps(row) + "\n")
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [{"kind": "skill", "id": "kept"}],
            }))
            repo = Repo(root)
            green = check_universe(repo)
            self.assertTrue(green["ok_keys"], green)
            red = check_universe(repo, plant_drop="skill/kept")
            self.assertFalse(red["ok_keys"], red)
            self.assertEqual(red["exit_code"], 1)
            self.assertIn("skill/kept", red["missing_without_receipt"])

    def test_store_gate_red_while_unresolved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            row = {
                "kind": "skill",
                "id": "missing-origin",
                "sha": "a" * 12,
                "store": {
                    "status": "unresolved_bundle",
                    "payload_scope": "descriptor_only",
                    "catalog_sha": "a" * 12,
                    "reason": "external skill not in a clean origin-backed git tree",
                },
            }
            (root / "docs/skillos/universe.jsonl").write_text(
                json.dumps(row) + "\n")
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [{"kind": "skill", "id": "missing-origin"}],
            }))
            with mock.patch.object(skillos, "_fetch_git_recipe") as fetch:
                result = check_universe(Repo(root), stores=True)
            fetch.assert_not_called()
            self.assertFalse(result["ok_stores"], result)
            self.assertEqual(result["unresolved"], 1)
            self.assertEqual(result["valid_store_count"], 0)
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(
                sum(group["count"] for group in result["missing_evidence"]), 1)

    def test_restock_never_rewrites_pinned_receipts(self):
        """A pinned recipe is historical evidence, not a cache entry."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            pinned = {"status": "recipe", "type": "git", "kind": "skill",
                      "url": "https://example.invalid/stale.git",
                      "commit": "b" * 40, "path": "skills/stale/SKILL.md",
                      "payload_scope": "file", "catalog_sha": "c" * 12,
                      "snapshot_sha": "c" * 12, "n_files": 1,
                      "tree_manifest": "d" * 64}
            rows = [
                {"kind": "skill", "id": "pinned", "sha": "c" * 12, "store": pinned},
                {"kind": "skill", "id": "gone", "sha": "e" * 12,
                 "store": {"status": "unresolved", "payload_scope": "unknown",
                           "catalog_sha": "e" * 12, "reason": "no evidence"}},
            ]
            (root / "docs/skillos/universe.jsonl").write_text(
                "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [
                    {"kind": "skill", "id": "pinned", "sha": "c" * 12,
                     "source": "canonical", "path": "nowhere"},
                    {"kind": "skill", "id": "gone", "sha": "e" * 12,
                     "source": "claude-skills", "path": "gone/SKILL.md"},
                ],
            }))
            with mock.patch.object(skillos, "_fetch_git_recipe") as fetch:
                result = skillos.restock_stores(Repo(root))
            fetch.assert_not_called()          # no candidate has an origin to prove
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["blobbed"], 0)
            self.assertEqual(result["recipe_verified"], 0)
            after = [json.loads(line) for line in
                     (root / "docs/skillos/universe.jsonl").read_text().splitlines()]
            self.assertEqual([(r["kind"], r["id"], r["sha"]) for r in after],
                             [("skill", "pinned", "c" * 12),
                              ("skill", "gone", "e" * 12)])
            self.assertEqual(after[0]["store"], pinned)   # never re-pointed at today's tree
            self.assertEqual(after[1]["store"]["status"], "unresolved")

    def test_restock_verifies_recipe_and_preserves_refused_row_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good_url = "https://example.invalid/good.git"
            bad_url = "https://example.invalid/bad.git"
            good_source, _ = self._git_source(
                root / "good-fixture", {"good.txt": b"good\n"}, good_url)
            bad_source, _ = self._git_source(
                root / "bad-fixture", {"bad.txt": b"bad\n"}, bad_url)
            good_payload = good_source / "good.txt"
            bad_payload = bad_source / "bad.txt"
            assets = [
                {"kind": "skill", "id": "good", "source": "test-external",
                 "path": str(good_payload), "abs_path": str(good_payload),
                 "sha": Repo._sha_file(good_payload)},
                {"kind": "skill", "id": "bad", "source": "test-external",
                 "path": str(bad_payload), "abs_path": str(bad_payload),
                 "sha": Repo._sha_file(bad_payload)},
            ]
            rows = [
                {"kind": a["kind"], "id": a["id"], "source": a["source"],
                 "path": a["path"], "sha": a["sha"],
                 "store": {"status": "unresolved", "payload_scope": "unknown",
                           "catalog_sha": a["sha"], "reason": "no evidence"}}
                for a in assets
            ]
            skillos_dir = root / "docs/skillos"
            skillos_dir.mkdir(parents=True)
            good_line = json.dumps(rows[0], separators=(",", ":")).encode() + b"\n"
            refused_line = json.dumps(
                rows[1], separators=(", ", ": ")).encode() + b"\n"
            universe = skillos_dir / "universe.jsonl"
            universe.write_bytes(good_line + refused_line)
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": assets,
            }))

            def fetch(url, _commit, work):
                # The bad URL deliberately returns the wrong checkout. Fetch succeeds,
                # but immutable-recipe verification must reject its absent commit.
                shutil.copytree(good_source, work)
                return {"ok": True, "exit_code": 0}

            with mock.patch.object(skillos, "_fetch_git_recipe", side_effect=fetch):
                result = skillos.restock_stores(Repo(root))

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["recipe_verified"], 1)
            self.assertEqual(result["recipe_refused"], 1)
            after_bytes = universe.read_bytes()
            after_lines = after_bytes.splitlines(keepends=True)
            self.assertEqual(after_lines[1], refused_line)
            after = [json.loads(line) for line in after_lines]
            self.assertEqual(after[0]["store"]["status"], "recipe")
            self.assertEqual(after[1], rows[1])
            self.assertEqual(
                [(r["kind"], r["id"], r["sha"]) for r in after],
                [(r["kind"], r["id"], r["sha"]) for r in rows],
            )

    def test_restock_licence_skipped_counts_only_licence_denials(self):
        """One canonical asset denied by the ledger, one failing for another
        reason (payload unresolvable) — only the first is a licence skip."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            payload = root / "capabilities/skills/uncleared/SKILL.md"
            payload.parent.mkdir(parents=True)
            payload.write_bytes(b"vendored bytes nobody cleared")
            rows = [
                {"kind": "skill", "id": "uncleared", "sha": "a" * 12},
                {"kind": "skill", "id": "ghost", "sha": "b" * 12},
            ]
            (root / "docs/skillos/universe.jsonl").write_text(
                "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [
                    {"kind": "skill", "id": "uncleared", "sha": "a" * 12,
                     "source": "canonical", "abs_path": str(payload)},
                    {"kind": "skill", "id": "ghost", "sha": "b" * 12,
                     "source": "canonical",
                     "abs_path": str(root / "ghost/SKILL.md")},
                ],
            }))
            (root / skillos.BLOB_LEDGER).write_text(json.dumps(
                {"entries": []}))
            result = skillos.restock_stores(Repo(root))
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["licence_skipped"], 1, result)
            self.assertEqual(result["blobbed"], 0)

    def test_restock_rewrite_stays_ascii_like_dump_output(self):
        """dump_universe writes ASCII-escaped rows; a restocked row must not
        smuggle raw UTF-8 back into a file read back via platform encoding."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            payload = root / "capabilities/skills/café/SKILL.md"
            payload.parent.mkdir(parents=True)
            payload.write_bytes(b"cleared content")
            digest = hashlib.sha256(b"cleared content").hexdigest()
            sha12 = Repo._sha_file(payload)
            row = {"kind": "skill", "id": "café", "sha": sha12}
            universe = root / "docs/skillos/universe.jsonl"
            universe.write_bytes(
                json.dumps(row, separators=(",", ":")).encode("utf-8") + b"\n")
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [{"kind": "skill", "id": "café", "sha": sha12,
                            "source": "canonical",
                            "abs_path": str(payload)}],
            }))
            (root / skillos.BLOB_LEDGER).write_text(json.dumps(
                {"entries": [{"kind": "skill", "id": "café",
                              "blob_sha256": digest, "catalog_sha": sha12,
                              "archive_allowed": True}]}))
            result = skillos.restock_stores(Repo(root))
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["blobbed"], 1, result)
            after = universe.read_bytes()
            self.assertIn(b"caf\\u00e9", after)
            self.assertNotIn("café".encode("utf-8"), after)
            self.assertEqual(json.loads(after)["store"]["status"], "blob")

    def test_restock_network_error_leaves_universe_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            assets = []
            sources = {}
            for aid in ("first", "offline"):
                url = f"https://example.invalid/{aid}.git"
                source, _ = self._git_source(
                    root / f"{aid}-fixture", {f"{aid}.txt": aid.encode()}, url)
                payload = source / f"{aid}.txt"
                assets.append({
                    "kind": "skill", "id": aid, "source": "test-external",
                    "path": str(payload), "abs_path": str(payload),
                    "sha": Repo._sha_file(payload),
                })
                sources[url] = source
            rows = [
                {"kind": a["kind"], "id": a["id"], "source": a["source"],
                 "path": a["path"], "sha": a["sha"],
                 "store": {"status": "unresolved", "payload_scope": "unknown",
                           "catalog_sha": a["sha"], "reason": "no evidence"}}
                for a in assets
            ]
            skillos_dir = root / "docs/skillos"
            skillos_dir.mkdir(parents=True)
            universe = skillos_dir / "universe.jsonl"
            before = b"".join(
                json.dumps(row, separators=(", ", ": ")).encode() + b"\n"
                for row in rows)
            universe.write_bytes(before)
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": assets,
            }))

            def fetch(url, _commit, work):
                if url.endswith("/offline.git"):
                    raise ConnectionError("network offline")
                shutil.copytree(sources[url], work)
                return {"ok": True, "exit_code": 0}

            with mock.patch.object(skillos, "_fetch_git_recipe", side_effect=fetch):
                result = skillos.restock_stores(Repo(root))

            self.assertFalse(result["ok"], result)
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(universe.read_bytes(), before)
            after = [json.loads(line) for line in universe.read_text().splitlines()
                     if line.strip()]
            self.assertEqual(len(after), len(rows))
            self.assertEqual(
                [(r["kind"], r["id"], r["sha"]) for r in after],
                [(r["kind"], r["id"], r["sha"]) for r in rows],
            )

    def test_orphan_leak_plant(self):
        corpus = REPO / "docs/skillos/orphan"
        red = orphan_replay(self.repo, corpus, plant_leak=True)
        self.assertFalse(red["ok"], red)
        self.assertEqual(red["exit_code"], 1)
        self.assertTrue(red.get("leaks"))

    def test_duplicate_universe_keys_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            (root / "docs/skillos/universe.jsonl").write_text(
                '{"kind":"skill","id":"x","sha":"a","store":{"status":"blob"}}\n'
                '{"kind":"skill","id":"x","sha":"b","store":{"status":"blob"}}\n'
            )
            (root / ".index.json").write_text('{"assets":[]}\n')
            red = check_universe(Repo(root))
            self.assertEqual(red.get("exit_code"), 1)
            self.assertEqual(red.get("duplicate_universe_keys"), ["skill/x"])

    def test_malformed_witness_json_red_even_with_missing_witnesses(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            witness_dir = root / WITNESS_DIR
            witness_dir.mkdir(parents=True)
            (witness_dir / "iqrsqpi-v10.json").write_text("{")
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [
                    {"kind": "skill", "id": "iqrsqpi-v10", "source": "canonical"},
                    {"kind": "skill", "id": "missing", "source": "canonical"},
                ],
            }))
            red = witness_strict(Repo(root))
            self.assertFalse(red["ok"], red)
            self.assertIn("iqrsqpi-v10", red.get("bad_fixtures") or [])
            self.assertIn("missing", red.get("missing_fixtures") or [])

    def test_swapped_witness_id_red_even_with_missing_witnesses(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            witness_dir = root / WITNESS_DIR
            witness_dir.mkdir(parents=True)
            (witness_dir / "iqrsqpi-v10.json").write_text(json.dumps({
                "kind": "skill", "id": "not-this-skill",
                "check": "rig-capabilities test",
            }))
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [
                    {"kind": "skill", "id": "iqrsqpi-v10", "source": "canonical"},
                    {"kind": "skill", "id": "missing", "source": "canonical"},
                ],
            }))
            red = witness_strict(Repo(root))
            self.assertFalse(red["ok"], red)
            self.assertIn("iqrsqpi-v10", red.get("bad_fixtures") or [])
            self.assertIn("missing", red.get("missing_fixtures") or [])

    def test_forged_receipt_does_not_authorize_drop(self):
        src = REPO / UNIVERSE
        if not src.is_file():
            self.skipTest("universe.jsonl not dumped yet")
        first = src.read_text().splitlines()[0]
        row = json.loads(first)
        drop = f"{row['kind']}/{row['id']}"
        fake = json.dumps({
            "kind": row["kind"], "id": row["id"],
            "snapshot_sha": "deadbeefdead",
            "store": {"status": "blob", "blob_sha256": "0" * 64},
        })
        # built from the row, not from REPO/.index.json: that file is generated and gitignored,
        # so a clean checkout has no index to read.
        assets = [{"kind": row["kind"], "id": row["id"]}]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            (root / UNIVERSE).write_text(first + "\n")
            (root / "docs/skillos/receipts.jsonl").write_text(fake + "\n")
            (root / ".index.json").write_text(
                json.dumps({"generated_epoch": 9999999999, "assets": assets}))
            red = check_universe(Repo(root), plant_drop=drop)
            self.assertFalse(red["ok_keys"], red)
            self.assertIn(drop, red["missing_without_receipt"])
            self.assertIn(drop, red["bad_receipts"])

    def test_provenance_plant_cli_source_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            planted = root / "vendor" / "tesslio" / "cli" / "main.ts"
            planted.parent.mkdir(parents=True)
            planted.write_text("export {}\n")
            red = provenance(Repo(root))
            self.assertFalse(red["ok"], red)
            self.assertEqual(red["exit_code"], 1)
            self.assertTrue(any("tesslio/cli" in h for h in red["hits"]))

    def test_recipe_unreachable_url_red(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = self._file_recipe("SKILL.md", b"fixture\n", "a" * 40)
            row = {
                "kind": "skill",
                "id": "unreachable",
                "sha": store["catalog_sha"],
                "store": store,
            }
            (root / "docs/skillos").mkdir(parents=True)
            (root / "docs/skillos/universe.jsonl").write_text(
                json.dumps(row) + "\n")
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [{"kind": "skill", "id": "unreachable"}],
            }))
            with mock.patch.object(
                    skillos, "_fetch_git_recipe",
                    return_value={
                        "ok": False, "error": "fetch failed", "exit_code": 1,
                    },
            ) as fetch:
                red = check_universe(Repo(root), stores=True)
        fetch.assert_called_once()
        self.assertFalse(red["ok_stores"], red)
        self.assertEqual(red["recipe_verified_count"], 0)
        self.assertEqual(red["recipe_failures"][0]["error"], "fetch failed")
        self.assertEqual(red["exit_code"], 1)

    def test_check_stores_fetches_once_per_url_and_commit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            files = {"alpha.txt": b"alpha\n", "nested/beta.txt": b"beta\n"}
            source, commit = self._git_source(root, files)
            rows = []
            assets = []
            for aid, path in (("alpha", "alpha.txt"), ("beta", "nested/beta.txt")):
                store = self._file_recipe(path, files[path], commit)
                rows.append({
                    "kind": "skill",
                    "id": aid,
                    "sha": store["catalog_sha"],
                    "store": store,
                })
                assets.append({"kind": "skill", "id": aid})
            (root / "docs/skillos").mkdir(parents=True)
            (root / "docs/skillos/universe.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows))
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": assets,
            }))
            with mock.patch.object(
                    skillos, "_fetch_git_recipe",
                    side_effect=self._copy_fetch(source),
            ) as fetch:
                result = check_universe(Repo(root), stores=True)
            self.assertTrue(result["ok_stores"], result)
            self.assertEqual(result["recipe_group_count"], 1)
            self.assertEqual(result["recipe_fetch_count"], 1)
            self.assertEqual(result["recipe_verified_count"], 2)
            self.assertEqual(result["valid_store_count"], 2)
            fetch.assert_called_once()

    def test_recipe_archive_verifies_descriptor_count_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            files = {
                "skill/SKILL.md": b"# Fixture\n",
                "skill/notes.txt": b"bounded evidence\n",
            }
            source, commit = self._git_source(base, files)
            store = {
                "status": "recipe",
                "type": "git",
                "kind": "skill",
                "url": "https://example.invalid/source.git",
                "commit": commit,
                "path": "skill",
                "payload_scope": "tree",
                "catalog_sha": hashlib.sha256(files["skill/SKILL.md"]).hexdigest()[:12],
                "snapshot_sha": self._snapshot_sha({
                    "SKILL.md": files["skill/SKILL.md"],
                    "notes.txt": files["skill/notes.txt"],
                }),
                "n_files": 2,
                "tree_manifest": self._manifest({
                    "SKILL.md": files["skill/SKILL.md"],
                    "notes.txt": files["skill/notes.txt"],
                }),
            }
            with mock.patch.object(
                    skillos, "_fetch_git_recipe",
                    side_effect=self._copy_fetch(source),
            ):
                green = restore_recipe(store, base / "green")
            self.assertTrue(green["ok"], green)
            self.assertEqual(green["n_files"], 2)
            self.assertEqual(green["tree_manifest"], store["tree_manifest"])

            plants = (
                ("catalog_sha", "0" * 12, "restored sha mismatch"),
                ("n_files", 1, "file count mismatch"),
                ("tree_manifest", "0" * 64, "tree manifest mismatch"),
                ("snapshot_sha", "0" * 12, "snapshot sha mismatch"),
            )
            for field, value, error in plants:
                with self.subTest(field=field), mock.patch.object(
                        skillos, "_fetch_git_recipe",
                        side_effect=self._copy_fetch(source),
                ):
                    planted = dict(store)
                    planted[field] = value
                    red = restore_recipe(planted, base / f"red-{field}")
                self.assertFalse(red["ok"], red)
                self.assertEqual(red["error"], error)
                self.assertEqual(red["exit_code"], 1)

            planted = dict(store)
            planted["tree_manifest"] = "0" * 64
            row = {
                "kind": "skill",
                "id": "tree-mismatch",
                "sha": planted["snapshot_sha"],
                "store": planted,
            }
            (base / "docs/skillos").mkdir(parents=True)
            (base / "docs/skillos/universe.jsonl").write_text(
                json.dumps(row) + "\n")
            (base / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [{"kind": "skill", "id": "tree-mismatch"}],
            }))
            with mock.patch.object(
                    skillos, "_fetch_git_recipe",
                    side_effect=self._copy_fetch(source),
            ):
                gate = check_universe(Repo(base), stores=True)
            self.assertFalse(gate["ok_stores"], gate)
            self.assertEqual(
                gate["recipe_failures"][0]["error"], "tree manifest mismatch")


class LicenceGate(unittest.TestCase):
    """Clearance binds to the stored bytes: `blob_sha256` + snapshot SHA12, never asset id."""

    SHA = "3f4017d3a3e2"
    DIGEST = "a" * 64

    def _row(self, digest=None):
        return {"kind": "skill", "id": "a", "sha": self.SHA,
                "store": {"status": "blob", "payload_scope": "file",
                          "catalog_sha": self.SHA,
                          "blob_sha256": digest or self.DIGEST}}

    def _ledger(self, root, entries):
        (root / "docs/skillos").mkdir(parents=True, exist_ok=True)
        (root / skillos.BLOB_LEDGER).write_text(json.dumps({"entries": entries}))

    def test_cleared_content_is_granted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._ledger(root, [{"kind": "skill", "id": "a", "blob_sha256": self.DIGEST,
                                 "catalog_sha": self.SHA, "archive_allowed": True}])
            allowed, problems = skillos._licence_map(root)
            self.assertEqual(allowed, {self.DIGEST: self.SHA})
            self.assertEqual(problems, [])

    def _root_with_one_blob_row(self, root: Path, entries) -> None:
        (root / "docs/skillos").mkdir(parents=True, exist_ok=True)
        (root / skillos.UNIVERSE).write_text(json.dumps(self._row()) + "\n")
        (root / skillos.BLOB_LEDGER).write_text(json.dumps({"entries": entries}))
        (root / ".index.json").write_text(json.dumps({
            "generated_epoch": 9999999999,
            "assets": [{"kind": "skill", "id": "a", "sha": self.SHA}],
        }))

    def test_denied_and_unrestorable_blobs_are_reported_apart(self):
        """A denied blob needs a ledger decision; a cleared-but-broken blob needs its bytes."""
        cleared = [{"kind": "skill", "id": "a", "blob_sha256": self.DIGEST,
                    "catalog_sha": self.SHA, "archive_allowed": True}]
        denied = [dict(cleared[0], archive_allowed=False)]
        with tempfile.TemporaryDirectory() as td_a, tempfile.TemporaryDirectory() as td_b:
            root = Path(td_a)
            self._root_with_one_blob_row(root, denied)
            red = skillos.check_universe(Repo(root))
            self.assertEqual(red["licence_denied"], ["skill/a"],
                             "ledger refusal must be named as a licence decision")
            self.assertEqual(red["unrestorable_blobs"], [])

            root = Path(td_b)
            self._root_with_one_blob_row(root, cleared)   # cleared, but no warehouse blob filed
            red = skillos.check_universe(Repo(root))
            self.assertEqual(red["licence_denied"], [],
                             "cleared content must not be pushed at the ledger")
            self.assertEqual(red["unrestorable_blobs"], ["skill/a"])
            self.assertEqual(red["valid_store_count"], 0)

    def test_missing_or_unparseable_ledger_clears_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            allowed, problems = skillos._licence_map(root)
            self.assertEqual(allowed, {})
            self.assertTrue(problems)
            self.assertFalse(skillos._universe_store_valid(root, self._row(), licence=allowed))
            (root / "docs/skillos").mkdir(parents=True)
            (root / skillos.BLOB_LEDGER).write_text("{")
            allowed, problems = skillos._licence_map(root)
            self.assertEqual(allowed, {})
            self.assertIn("unreadable", problems[0])

    def test_grant_for_other_content_does_not_bless_the_stored_blob(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # same asset id, different bytes — the old grant must not carry over
            self._ledger(root, [{"kind": "skill", "id": "a",
                                 "blob_sha256": "b" * 64, "catalog_sha": self.SHA,
                                 "archive_allowed": True}])
            allowed, _ = skillos._licence_map(root)
            self.assertFalse(skillos._universe_store_valid(root, self._row(), licence=allowed))
            # and a grant tied to a different snapshot of these bytes is refused too
            self._ledger(root, [{"kind": "skill", "id": "a",
                                 "blob_sha256": self.DIGEST, "catalog_sha": "0" * 12,
                                 "archive_allowed": True}])
            allowed, _ = skillos._licence_map(root)
            self.assertFalse(skillos._universe_store_valid(root, self._row(), licence=allowed))

    def test_malformed_conflicting_or_denied_entries_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._ledger(root, [
                {"kind": "skill", "id": "a", "blob_sha256": "nothex",
                 "catalog_sha": self.SHA, "archive_allowed": True},
                {"kind": "skill", "id": "b", "blob_sha256": "c" * 64,
                 "catalog_sha": "short", "archive_allowed": True},
                {"kind": "skill", "id": "c", "blob_sha256": "d" * 64,
                 "catalog_sha": self.SHA, "archive_allowed": "true"},
                {"kind": "skill", "id": "d", "blob_sha256": self.DIGEST,
                 "catalog_sha": self.SHA, "archive_allowed": True},
                {"kind": "skill", "id": "d", "blob_sha256": self.DIGEST,
                 "catalog_sha": "9" * 12, "archive_allowed": True},
            ])
            allowed, problems = skillos._licence_map(root)
            self.assertEqual(allowed, {})
            self.assertEqual(len(problems), 4, problems)   # 2 malformed, 1 non-bool, 1 conflict


    def test_every_duplicate_digest_is_permanently_denied(self):
        cases = {
            "allowed_then_denied": [
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True},
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": False},
            ],
            "third_entry_cannot_readd": [
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True},
                {"blob_sha256": self.DIGEST, "catalog_sha": "9" * 12,
                 "archive_allowed": True},
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True},
            ],
            "identical_duplicate": [
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True},
                {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True},
            ],
        }
        for name, entries in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                self._ledger(root, entries)
                allowed, problems = skillos._licence_map(root)
                self.assertEqual(allowed, {})
                self.assertTrue(
                    any(self.DIGEST[:12] in problem for problem in problems),
                    problems,
                )

    def test_malformed_ledger_shapes_fail_closed_without_raising(self):
        valid = {"blob_sha256": self.DIGEST, "catalog_sha": self.SHA,
                 "archive_allowed": True}
        cases = {
            "document_not_object": (
                [], "licence ledger document is not an object"),
            "entries_not_list": (
                {"entries": {}}, "licence ledger entries is not a list"),
            "entry_not_object": (
                {"entries": [valid, "not-an-object"]}, "entry is not an object"),
        }
        for name, (doc, expected_problem) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                path = root / skillos.BLOB_LEDGER
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(doc))
                allowed, problems = skillos._licence_map(root)
                self.assertEqual(allowed, {})
                self.assertIn(expected_problem, problems)

    def test_uncleared_canonical_content_never_reaches_the_warehouse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = root / "cap" / "SKILL.md"
            payload.parent.mkdir()
            payload.write_text("ours\n")
            asset = {"kind": "skill", "id": "x", "source": "canonical",
                     "abs_path": str(payload), "sha": self.SHA}
            store = skillos._store_for(root, asset, licence={})
            self.assertEqual(store["status"], "unresolved")
            self.assertIn("licence ledger", store["reason"])
            self.assertFalse((root / skillos.WAREHOUSE).exists())
            # cleared for these exact bytes → filed, and the grant is what makes it valid
            digest = skillos._content_digest(payload)
            store = skillos._store_for(root, asset, licence={digest: self.SHA})
            self.assertEqual(store["status"], "blob")
            self.assertTrue((root / store["blob"]).is_file())

    def test_stored_file_licence_is_read_from_its_own_bytes(self):
        """A file blob restores to <tmp>/payload — classifying the directory instead would
        read no frontmatter and wave a vendored file through as repo MIT."""
        spec = importlib.util.spec_from_file_location(
            "blob_license_ledger", REPO / "scripts/blob_license_ledger.py")
        ledger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ledger)
        content = b"---\nlicense: GPL-3.0\n---\nvendored thing\n"
        digest = hashlib.sha256(content).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            blob = root / skillos.WAREHOUSE / digest[:2] / digest
            blob.parent.mkdir(parents=True)
            blob.write_bytes(content)
            got = restore_blob(Repo(root), digest, root / "out")
            self.assertTrue(got["ok"], got)
            self.assertEqual(got["kind"], "file")
            self.assertFalse(
                ledger.classify(root / "out" / "payload")["archive_allowed"])
            self.assertTrue(ledger.classify(root / "out")["archive_allowed"])

    def test_repo_grant_is_not_extended_to_restored_bytes(self):
        """A single restored file has no sibling LICENSE by construction; without its own
        frontmatter declaration the only prior lane was the repo MIT fallback — which is a
        claim about repo files, not about whatever bytes an old blob holds."""
        spec = importlib.util.spec_from_file_location(
            "blob_license_ledger", REPO / "scripts/blob_license_ledger.py")
        ledger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ledger)
        content = b"# vendored without any licence evidence\n"
        digest = hashlib.sha256(content).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            blob = root / skillos.WAREHOUSE / digest[:2] / digest
            blob.parent.mkdir(parents=True)
            blob.write_bytes(content)
            got = restore_blob(Repo(root), digest, root / "out")
            self.assertTrue(got["ok"], got)
            # default (live-tree) lane: repo fallback clears repo files
            self.assertTrue(ledger.classify(root / "out" / "payload")["archive_allowed"])
            # store lane: same bytes, no evidence traveling with them -> denied
            denied = ledger.classify(root / "out" / "payload", repo_fallback=False)
            self.assertFalse(denied["archive_allowed"])
            self.assertIn("not extended to stored bytes", denied["basis"])
        # a declaration inside the bytes still clears even with the fallback denied
        declared = b"---\nlicense: MIT\n---\nfile\n"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "payload"
            p.write_bytes(declared)
            self.assertTrue(ledger.classify(p, repo_fallback=False)["archive_allowed"])

    def _ledger_mod(self):
        spec = importlib.util.spec_from_file_location(
            "blob_license_ledger", REPO / "scripts/blob_license_ledger.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_generator_survives_an_unresolvable_payload(self):
        """`_rel` runs for every entry; a missing payload gives _content_digest "" and _rel None."""
        ledger = self._ledger_mod()
        self.assertEqual(ledger._rel(None), "")
        self.assertEqual(ledger._rel(REPO / "LICENSE"), "LICENSE")

    def test_generator_runs_without_the_frozen_universe(self):
        """universe.jsonl is generated; its absence must only drop drift detection."""
        ledger = self._ledger_mod()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs/skillos").mkdir(parents=True)
            (root / ".index.json").write_text(json.dumps({
                "generated_epoch": 9999999999,
                "assets": [
                    {"kind": "skill", "id": "present", "sha": self.SHA, "source": "canonical",
                     "abs_path": str(root / "capabilities/skills/present/SKILL.md")},
                    {"kind": "skill", "id": "ghost", "sha": self.SHA, "source": "canonical",
                     "abs_path": str(root / "capabilities/skills/ghost/SKILL.md")},
                ],
            }))
            (root / "capabilities/skills/present").mkdir(parents=True)
            (root / "capabilities/skills/present/SKILL.md").write_text(
                "---\nname: present\n---\nbody\n")
            self.assertEqual(ledger.main(root), 0)
            doc = json.loads((root / "docs/skillos/blob-license-ledger.json").read_text())
            self.assertEqual(doc["stored_blobs"], 0)
            by_id = {e["id"]: e for e in doc["entries"]}
            self.assertTrue(by_id["present"]["archive_allowed"])
            self.assertFalse(by_id["ghost"]["archive_allowed"])
            self.assertEqual(by_id["ghost"]["path"], "")   # the _rel(None) crash site
            # The ledger is committed, so a path must be checkout-relative even when `--root`
            # is a symlinked temp dir (macOS /var -> /private/var): resolving only the payload
            # would make relative_to() fail and leak the temp path into a tracked file.
            self.assertEqual(by_id["present"]["path"],
                             "capabilities/skills/present/SKILL.md")
            self.assertIn("skill/ghost", doc["needs_review"])

    def test_own_declaration_outranks_a_permissive_neighbour(self):
        """A vendored file's `license:` is evidence about the file; the directory LICENSE is not."""
        ledger = self._ledger_mod()
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "LICENSE.txt").write_text("MIT License\nPermission is hereby granted\n")
            (d / "SKILL.md").write_text("---\nname: vendored\nlicense: GPL-3.0\n---\nbody\n")
            got = ledger.classify(d)
            self.assertEqual(got["license"], "GPL-3.0")
            self.assertFalse(got["archive_allowed"],
                             "copyleft declared by the asset must not inherit MIT from the dir")

    def test_licence_needles_do_not_match_inside_other_words(self):
        ledger = self._ledger_mod()
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "LICENSE").write_text("Additional permissions are described under MISC "
                                       "NOTICES and our DISCLAIMER below.\n")
            licence, cand = ledger.sibling_license(d)
            # MISC / NOTICES / DISCLAIMER each contain a former bare needle.
            self.assertEqual(licence, "unrecognised licence text")
            self.assertEqual(cand.name, "LICENSE")
            (d / "LICENSE").write_text("ISC License\n\nPermission to use, copy, or distribute "
                                       "this software is hereby granted.\n")
            self.assertEqual(ledger.sibling_license(d)[0], "ISC")

    def test_a_licence_claim_must_look_like_a_licence(self):
        """Two remediations fell to denials before this one.

        The unanchored substring needle `ISC License` accepted `not ISC License` on sight;
        word-bounding then accepted `not ISC licensed`. A title is evidence only when it owns
        its line. Canonical ISC text often has no title at all, so the opening sentence stays
        as an alternative — otherwise tightening the needle would drop real ISC blobs into
        `archive_allowed: false` and lose licensed content.
        """
        ledger = self._ledger_mod()
        cases = [
            # canonical ISC, no title line — must still clear
            ("Permission to use, copy, modify, and/or distribute this software for any\n"
             "purpose with or without fee is hereby granted.\n", "ISC"),
            # titles only when they own the line
            ("ISC License\n\nPermission to use, copy, or distribute this software\n"
             "is hereby granted.\n", "ISC"),
            ("The ISC License\n", "ISC"),
            # denials, in both historic shapes: the substring layer accepted
            # `not ISC License` on sight; word-bounding alone accepted `not ISC licensed`
            ("This software is proprietary and trade secret, not ISC licensed.\n", None),
            ("not ISC License\n", None),
            # clause titles are licences; prose naming one is not
            ("BSD 3-Clause License\n\nRedistribution and reproduction in source, with or\n"
             "without modification, is permitted provided conditions are met.\n",
             "BSD (uncatalogued)"),
            ("BSD-2-Clause License\n", "BSD (uncatalogued)"),
            ("All rights reserved; see the BSD License for terms.\n", None),
            ("Copyright belongs to upstream; see the BSD file for terms.\n", None),
            # MIT: title owns the line; denial prose grants nothing
            ("MIT License\n", "MIT"),
            ("not MIT License\n", None),
            ("This file ships under commercial terms, not MIT License at all.\n", None),
            # Apache: heading, one-line title, and header notice; negation does not
            ("Apache License\nVersion 2.0, January 2004\n", "Apache-2.0"),
            ("The Apache License, Version 2.0 applies.\n\n", None),
            ('   Licensed under the Apache License, Version 2.0 (the "License");\n'
             "you may not use this file except in compliance with the License.\n",
             "Apache-2.0"),
            ('   Licensed under the Apache License, Version 2.0 (the "License") '
             "is not applicable\n", None),
            ('   Licensed under the Apache License, Version 2.0 (the "License");\n',
             "Apache-2.0"),
            ("The bundled tool is not Apache License compatible.\n", None),
            # CC0: `CC0` as a bare substring was the loosest needle of all
            ("CC0 1.0 Universal\n\nStatement of Purpose\n", "CC0-1.0"),
            ("not CC0\n", None),
            ("Rights are reserved; this is not CC0 and not public domain.\n", None),
            ("CC0 1.0 Universal is not applicable to this repository.\n", None),
            ("CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE\n"
             "LEGAL SERVICES.\n", "CC0-1.0"),
            ("CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE\n"
             "LEGAL SERVICES is a false claim.\n", None),
            # suffix denials: a grant prefix is not a grant
            ("Permission is hereby granted? No; all rights reserved.\n", None),
            ("Permission to use, copy, modify, and distribute this software\n"
             "is hereby granted is false.\n", None),
            ("CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE "
             "LEGAL SERVICES. according to this false notice\n", None),
            # ...but the canonical continuation clears across any line wrap
            ("Permission is hereby granted,\nfree of charge, to any person obtaining\n"
             "a copy of this software\n", "MIT"),
            # Apache 3.0 is not Apache-2.0: never mislabel a version we don't grant
            ("Apache License, Version 3.0\n", None),
            ('Licensed under the Apache License, Version 3.0 (the "License");\n', None),
            ("Apache Software License Version 3\n", None),
            ("Apache License\nVersion 2.0 is not applicable\n", None),
            # title words may not span lines; the ONLY vertical form is the canonical
            # two-line heading (License, then Version 2.x alone on the next line)
            ("Apache\nSoftware License Version 2.0 not applicable\n", None),
            ("Apache License\nVersion 2.0, January 2004\n", "Apache-2.0"),
            # the grant may sit past the old 4000-char read window in a full licence text
            ("TERMS AND CONDITIONS\n" * 400
             + '   Licensed under the Apache License, Version 2.0 (the "License");\n',
             "Apache-2.0"),
        ]
        for text, want in cases:
            with tempfile.TemporaryDirectory() as td:
                d = Path(td)
                (d / "LICENSE").write_text(text)
                got = ledger.sibling_license(d)[0]
                if want is None:
                    self.assertEqual(got, "unrecognised licence text",
                                     f"over-claimed as {got!r}: {text[:40]!r}")
                else:
                    self.assertEqual(got, want, f"{text[:40]!r}")

if __name__ == "__main__":
    unittest.main()
