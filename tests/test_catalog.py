"""Stdlib unittests for rig-capabilities: index, search, install, protocol."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402


def make_fixture(tmp: Path) -> Repo:
    repo = Repo(tmp / "repo")
    hook = repo.cap_root / "hooks" / "guard.sh"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\n# guard hook: blocks dangerous rm -rf commands\n"
                    "echo block\n")
    skill = repo.cap_root / "skills" / "demo-skill"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo capability\n"
                                    "tags: testing, demo\n---\n# Demo Skill\nbody\n")
    ext_skill = tmp / "extskills" / "ext-thing"
    ext_skill.mkdir(parents=True, exist_ok=True)
    (ext_skill / "SKILL.md").write_text("---\nname: ext-thing\n"
                                        "description: external shadowed skill\n---\n"
                                        "# Ext\n")
    dup = tmp / "extskills" / "demo-skill"
    dup.mkdir(parents=True, exist_ok=True)
    (dup / "SKILL.md").write_text("---\nname: demo-skill\ndescription: external copy\n"
                                  "---\n# dup\n")
    repo.config_path.write_text(json.dumps({
        "defaults": False,
        "external_roots": [
            {"label": "ext", "kind": "skill", "path": str(tmp / "extskills"),
             "pattern": "*/SKILL.md"}],
        "install_roots": {
            "hook": {"claude": str(tmp / "claude" / "hooks")},
            "skill": {"claude": str(tmp / "claude" / "skills")}},
    }))
    repo.build_index()
    return repo


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_index_counts(self):
        doc = self.repo.load_index()
        kinds = {(a["id"], a["source"]) for a in doc["assets"]}
        self.assertIn(("guard.sh", "canonical"), kinds)
        self.assertIn(("demo-skill", "canonical"), kinds)
        self.assertIn(("ext-thing", "ext"), kinds)
        # canonical shadows the external same-id copy: exactly one demo-skill
        self.assertEqual(1, len([a for a in doc["assets"] if a["id"] == "demo-skill"]))

    def test_search_ranks_name_match(self):
        rows = self.repo.search("guard")
        self.assertTrue(rows)
        self.assertEqual("guard.sh", rows[0]["id"])

    def test_search_canonical_bonus_and_kind_filter(self):
        rows = self.repo.search("demo", kind="skill")
        self.assertEqual([("demo-skill", "canonical")],
                         [(r["id"], r["source"]) for r in rows])

    def test_install_and_idempotence(self):
        out = self.repo.install("guard.sh", "claude")
        self.assertEqual("installed", out["status"])
        target = Path(out["target"])
        self.assertTrue(target.exists())
        again = self.repo.install("guard.sh", "claude")
        self.assertEqual("already-installed", again["status"])
        led = self.repo.ledger()
        self.assertEqual(1, len(led["guard.sh"]))

    def test_overwrite_refuses_then_force_backs_up(self):
        self.repo.install("guard.sh", "claude")
        (self.repo.cap_root / "hooks" / "guard.sh").write_text("# changed\n" + "x" * 40)
        self.repo.build_index()
        with self.assertRaises(ValueError):
            self.repo.install("guard.sh", "claude")
        out = self.repo.install("guard.sh", "claude", force=True)
        self.assertEqual("replaced", out["status"])
        baks = list((self.tmp / "claude" / "hooks").glob("guard.sh.bak-*"))
        self.assertEqual(1, len(baks))

    def test_external_requires_canonicalize(self):
        with self.assertRaises(ValueError) as cm:
            self.repo.install("ext-thing", "claude")
        self.assertIn("capability_add", str(cm.exception))

    def test_add_canonicalizes_directory(self):
        out = self.repo.add("ext-thing", "skill", str(self.tmp / "extskills" / "ext-thing"))
        self.assertEqual("added", out["status"])
        self.assertTrue((self.repo.cap_root / "skills" / "ext-thing").is_dir())
        installed = self.repo.install("ext-thing", "claude")
        self.assertEqual("installed", installed["status"])

    def test_add_is_idempotent_when_source_is_canonical(self):
        # Registering a skill whose source path IS the canonical dir must not
        # delete the source (regression: rmtree(dst) destroyed src when
        # src.resolve()==dst.resolve(), then copytree ENOENT'd).
        canon = self.repo.cap_root / "skills" / "demo-skill"
        self.assertTrue(canon.is_dir())
        before = (canon / "SKILL.md").read_text()
        out = self.repo.add("demo-skill", "skill", str(canon), overwrite=True)
        self.assertIn(out["status"], ("added", "replaced", "registered"))
        self.assertTrue((canon / "SKILL.md").is_dir() or canon.is_dir())
        self.assertEqual(before, (canon / "SKILL.md").read_text())
        resolved = self.repo.resolve("demo-skill")
        self.assertIsNotNone(resolved)


class ProtocolTests(unittest.TestCase):
    def test_handshake_and_tool_call(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            repo = make_fixture(tmp)
            env = dict(os.environ, RIG_CAP_REPO=str(repo.root))
            req = ("\n".join([
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                            "params": {"protocolVersion": "2025-06-18"}}),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                            "params": {"name": "capabilities_search",
                                       "arguments": {"query": "guard"}}}),
                json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                            "params": {"name": "capability_install",
                                       "arguments": {"id": "guard.sh",
                                                     "harness": "claude"}}}),
                "",
            ])).encode()
            proc = subprocess.run([sys.executable, str(REPO_ROOT / "server.py")],
                                  input=req, capture_output=True, env=env, timeout=30)
            lines = [json.loads(ln) for ln in proc.stdout.decode().splitlines() if ln]
            by_id = {m.get("id"): m for m in lines}
            self.assertEqual("2025-06-18", by_id[1]["result"]["protocolVersion"])
            names = [t["name"] for t in by_id[2]["result"]["tools"]]
            self.assertIn("capabilities_search", names)
            self.assertIn("capability_install", names)
            search_txt = by_id[3]["result"]["content"][0]["text"]
            self.assertIn("guard.sh", search_txt)
            self.assertFalse(by_id[3]["result"]["isError"])
            install_txt = by_id[4]["result"]["content"][0]["text"]
            self.assertIn("installed", install_txt)
            self.assertFalse(by_id[4]["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
