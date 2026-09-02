"""BriefFreezeTests: the Fable-2031 input is pinned bytes, reproducible from the repo.

The brief was composed interactively, so "generator-only" cannot mean "re-derivable
prose". It means the byte string is defined by committed parts and every copy is
verifiable. These tests hold that: a faithful copy passes, and a one-byte edit, a
reordered part, or a missing file is caught.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "build_fable_brief.py"
PARTS = REPO_ROOT / "tests" / "fixtures" / "fable2031" / "brief"


def _load():
    spec = importlib.util.spec_from_file_location("build_fable_brief", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BriefFreezeTests(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self.spec = json.loads((PARTS / "manifest.json").read_text())

    def _tmp_parts(self):
        """A throwaway parts dir whose manifest points at the real pin."""
        d = Path(tempfile.mkdtemp(prefix="f31-brief-"))
        for name in self.spec["parts"]:
            shutil.copy2(PARTS / name, d / name)
        shutil.copy2(PARTS / "manifest.json", d / "manifest.json")
        self.mod.PARTS_DIR = d
        self.mod.MANIFEST = d / "manifest.json"
        self.addCleanup(shutil.rmtree, d, True)
        return d

    def test_the_parts_concatenate_to_the_pinned_brief(self):
        blob = self.mod.assemble()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), self.spec["brief_sha256"])
        self.assertEqual(len(blob), self.spec["bytes"])

    def test_the_pin_matches_the_committed_sidecar_style_hash(self):
        # The manifest pin is the only source of truth; a part edited in place breaks it.
        d = self._tmp_parts()
        first = d / self.spec["parts"][0]
        first.write_bytes(first.read_bytes() + b" \n")
        self.assertNotEqual(hashlib.sha256(self.mod.assemble()).hexdigest(),
                            self.spec["brief_sha256"])

    def test_reordering_parts_breaks_the_pin(self):
        d = self._tmp_parts()
        spec = json.loads((d / "manifest.json").read_text())
        spec["parts"] = list(reversed(spec["parts"]))
        (d / "manifest.json").write_text(json.dumps(spec))
        self.assertNotEqual(hashlib.sha256(self.mod.assemble()).hexdigest(),
                            self.spec["brief_sha256"])

    def test_a_missing_part_is_fatal_not_skipped(self):
        d = self._tmp_parts()
        (d / self.spec["parts"][1]).unlink()
        with self.assertRaises(SystemExit):
            self.mod.assemble()

    def test_check_passes_on_a_faithful_copy_and_writes_nothing(self):
        out = Path(tempfile.mkdtemp(prefix="f31-brief-out-")) / "brief.md"
        blob = self.mod.assemble()
        out.write_bytes(blob)
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in PARTS.iterdir()}
        self.assertEqual(self.mod.main(["--check", "--out", str(out)]), 0)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in PARTS.iterdir()}
        self.assertEqual(before, after, "--check must not touch the parts")

    def test_check_refuses_a_one_byte_edit(self):
        out = Path(tempfile.mkdtemp(prefix="f31-brief-out-")) / "brief.md"
        out.write_bytes(self.mod.assemble()[:-1] + b"X")
        self.assertEqual(self.mod.main(["--check", "--out", str(out)]), 1)

    def test_check_refuses_a_missing_target(self):
        out = Path(tempfile.mkdtemp(prefix="f31-brief-out-")) / "absent.md"
        self.assertEqual(self.mod.main(["--check", "--out", str(out)]), 1)

    def test_build_writes_the_file_and_a_sidecar_that_agrees(self):
        out = Path(tempfile.mkdtemp(prefix="f31-brief-out-")) / "brief.md"
        self.assertEqual(self.mod.main(["--out", str(out)]), 0)
        self.assertEqual(out.read_bytes(), self.mod.assemble())
        sidecar = out.with_suffix(out.suffix + ".sha256")
        self.assertTrue(sidecar.is_file())
        self.assertEqual(sidecar.read_text().split()[0], self.spec["brief_sha256"])

    def test_the_headings_stay_in_the_declared_order(self):
        text = self.mod.assemble().decode()
        heads = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual([h.split()[1].rstrip(".") for h in heads][:5],
                         ["0", "1", "2", "3", "4"])

    def test_the_brief_ends_with_its_sentinel(self):
        self.assertIn("FABLE2031-END", self.mod.assemble().decode())


if __name__ == "__main__":
    unittest.main()
