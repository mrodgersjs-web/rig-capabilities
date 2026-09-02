"""A directory is an asset only when it says so with a SKILL.md.

`catalog._asset_from_canonical` accepted any non-dot directory under a kind
directory and took "the first file `rglob` finds, sorted" as its main text. Two
phantoms followed, both created by ordinary work in this repo:

    capabilities/hooks/fixtures      -> indexed as a HOOK
    capabilities/loops/__pycache__   -> indexed as a LOOP

The second is the serious one. A `.pyc` read with `errors="replace"` clears the
10-character text floor easily, so compiled bytecode was published as a
capability and would have reappeared on every reindex while anyone ran the loop
it claimed to be. It also inflated the served hook count in `docs/ROADMAP.md`,
which `tests/fable2031_claims.py` caught as a claim mismatch.

These tests pin the rule from both sides: skills (which legitimately are
directories) survive, support directories do not appear at all, and a
deliberately planted `__pycache__` under a kind directory is not scanned.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402

BODY = "---\nname: probe\ndescription: a probe asset with enough prose to index\n---\n\n# Probe\n\nBody.\n"


class DirectoryAssetTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo(REPO_ROOT)

    def _canonical(self):
        return [a for a in self.repo.load_index()["assets"]
                if a["source"] == "canonical"]

    def test_no_support_directory_is_an_asset(self):
        from rig_capabilities.catalog import DIR_DESCRIPTOR
        bad = []
        for a in self._canonical():
            p = REPO_ROOT / a["path"]
            if not p.is_dir():
                continue
            desc = DIR_DESCRIPTOR.get(a["kind"])
            if desc is None or not (p / desc).is_file():
                bad.append(f"{a['id']} ({a['kind']}) at {a['path']}")
        self.assertEqual(bad, [], f"phantom directory assets: {bad}")

    def test_skills_may_still_be_directories(self):
        """Non-vacuity: the rule above is not 'directories are never assets'."""
        dirs = [a for a in self._canonical()
                if a["kind"] == "skill" and (REPO_ROOT / a["path"]).is_dir()]
        self.assertGreater(len(dirs), 5,
                           "if this is zero the scanner stopped seeing skills")
        for a in dirs:
            self.assertTrue((REPO_ROOT / a["path"] / "SKILL.md").is_file(), a["id"])

    def test_a_planted_pycache_under_a_kind_directory_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for kind in ("loops", "hooks", "commands"):
                d = root / "capabilities" / kind
                d.mkdir(parents=True)
                (d / "real.md").write_text(BODY, encoding="utf-8")
                (d / "__pycache__").mkdir()
                (d / "__pycache__" / "real.cpython-311.pyc").write_bytes(
                    b"\x00" * 4096)               # clears the text floor as text
                (d / "fixtures").mkdir()
                (d / "fixtures" / "payload.json").write_text(
                    '{"a": 1, "b": "some fixture content"}', encoding="utf-8")
            ids = [(a["kind"], a["id"]) for a in
                   Repo(str(root)).build_index()["assets"]]
        kinds = {k for k, _ in ids}
        self.assertIn("loop", kinds, "the probe tree itself was not scanned")
        for bad_id in ("__pycache__", "fixtures"):
            self.assertNotIn((bad_id, bad_id), ids)
            self.assertFalse(any(i == bad_id for _, i in ids),
                             f"{bad_id} indexed as an asset: {ids}")

    def test_bytecode_never_becomes_main_text(self):
        from rig_capabilities.catalog import _pick_main_text
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.pyc"
            p.write_bytes(b"\x00\x01\x02" * 2000)
            text = _pick_main_text(p)
        # whatever the reader returns for binary, it must not look like prose
        # that could carry frontmatter: no decodable `name:` key survives
        self.assertNotIn("name:", text)

    def test_data_assets_are_directories_with_a_descriptor(self):
        """The `data` kind packages like a skill: a directory is a data asset
        only when it carries DATA.md. Non-vacuity for the descriptor generaliser."""
        from rig_capabilities.catalog import DIR_DESCRIPTOR
        self.assertEqual(DIR_DESCRIPTOR.get("data"), "DATA.md")
        data = [a for a in self._canonical() if a["kind"] == "data"]
        self.assertGreaterEqual(len(data), 1, "no data asset indexed")
        for a in data:
            self.assertTrue((REPO_ROOT / a["path"] / "DATA.md").is_file(), a["id"])

    def test_a_data_directory_without_its_descriptor_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "capabilities" / "data"
            (d / "real-asset").mkdir(parents=True)
            (d / "real-asset" / "DATA.md").write_text(BODY, encoding="utf-8")
            (d / "support").mkdir()                 # no DATA.md -> not an asset
            (d / "support" / "notes.json").write_text('{"x": 1}', encoding="utf-8")
            ids = [(a["kind"], a["id"]) for a in Repo(str(root)).build_index()["assets"]]
        self.assertIn(("data", "real-asset"), ids)
        self.assertFalse(any(i == "support" for _, i in ids),
                         f"support dir indexed as data: {ids}")


if __name__ == "__main__":
    unittest.main()
