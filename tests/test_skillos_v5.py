"""SkillOS v5: keys conservation, store fail-closed, orphan/witness/receipt plants."""
from __future__ import annotations

import hashlib
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

    def _git_source(self, base: Path, files: dict[str, bytes]) -> tuple[Path, str]:
        source = base / "source"
        source.mkdir()
        for name, data in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
               "GIT_CONFIG_SYSTEM": os.devnull, "HOME": str(base)}
        git = ["git", "-c", "core.hooksPath=" + os.devnull]
        subprocess.run([*git, "init", "--quiet", str(source)], check=True, env=env)
        subprocess.run([*git, "-C", str(source), "add", "."], check=True, env=env)
        subprocess.run(
            [*git, "-C", str(source),
             "-c", "user.name=SkillOS Test",
             "-c", "user.email=skillos@example.invalid",
             "commit", "--quiet", "-m", "fixture"],
            check=True, env=env,
        )
        commit = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
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
        uni = REPO / UNIVERSE
        if not uni.is_file() or uni.stat().st_size < 10:
            self.skipTest("universe.jsonl not dumped yet")
        green = check_universe(self.repo)
        self.assertTrue(green["ok_keys"], green)
        row = json.loads(uni.read_text().splitlines()[0])
        drop = f"{row['kind']}/{row['id']}"
        red = check_universe(self.repo, plant_drop=drop)
        self.assertFalse(red["ok_keys"], red)
        self.assertEqual(red["exit_code"], 1)
        self.assertIn(drop, red["missing_without_receipt"])

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

    def test_malformed_witness_json_red(self):
        path = REPO / WITNESS_DIR / "iqrsqpi-v10.json"
        if not path.is_file():
            self.skipTest("witness fixtures missing")
        bak = path.read_text()
        try:
            path.write_text("{")
            red = witness_strict(self.repo)
            self.assertFalse(red["ok"], red)
            self.assertIn("iqrsqpi-v10", red.get("bad_fixtures") or [])
        finally:
            path.write_text(bak)

    def test_swapped_witness_id_red(self):
        path = REPO / WITNESS_DIR / "iqrsqpi-v10.json"
        if not path.is_file():
            self.skipTest("witness fixtures missing")
        bak = path.read_text()
        try:
            path.write_text(json.dumps({
                "kind": "skill", "id": "not-this-skill",
                "check": "rig-capabilities test",
            }))
            red = witness_strict(self.repo)
            self.assertFalse(red["ok"], red)
            self.assertIn("iqrsqpi-v10", red.get("bad_fixtures") or [])
        finally:
            path.write_text(bak)

    def test_forged_receipt_does_not_authorize_drop(self):
        uni = REPO / UNIVERSE
        recp = REPO / "docs/skillos/receipts.jsonl"
        if not uni.is_file():
            self.skipTest("universe.jsonl not dumped yet")
        row = json.loads(uni.read_text().splitlines()[0])
        drop = f"{row['kind']}/{row['id']}"
        fake = json.dumps({
            "kind": row["kind"], "id": row["id"],
            "snapshot_sha": "deadbeefdead",
            "store": {"status": "blob", "blob_sha256": "0" * 64},
        })
        bak = recp.read_text() if recp.is_file() else ""
        try:
            recp.write_text(fake + "\n")
            red = check_universe(self.repo, plant_drop=drop)
            self.assertFalse(red["ok_keys"], red)
            self.assertIn(drop, red["missing_without_receipt"])
        finally:
            recp.write_text(bak)

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

if __name__ == "__main__":
    unittest.main()
