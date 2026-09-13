"""V07 / V17: the two claims the estate keeps asserting without running them —
that the criteria pack is deterministic, and that an install works on a machine
that has never had it. Both are cheap to prove and both were unproven."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _run(code: str, home: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "HOME": str(home)}
    env.pop("RIG_CAP_DSN", None)
    return subprocess.run([sys.executable, "-c", code], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=300)


class V07CriteriaPackDeterminism(unittest.TestCase):
    """Two generations of the pack must be the same bytes. A pack that embeds a
    timestamp or dict order is not a golden authority, and every `stale pack`
    verdict downstream becomes noise."""

    def test_generate_is_byte_identical_twice(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.jsonl", Path(td) / "b.jsonl"
            for out in (a, b):
                r = subprocess.run([sys.executable, "rig_capabilities/criteria_pack.py",
                                    "generate", "--out", str(out)], cwd=REPO,
                                   capture_output=True, text=True, timeout=300)
                self.assertEqual(r.returncode, 0, r.stderr[-400:])
            da, db = a.read_bytes(), b.read_bytes()
            self.assertEqual(hashlib.sha256(da).hexdigest(), hashlib.sha256(db).hexdigest(),
                             "criteria pack generation is not deterministic")
            cells = [json.loads(l)["cell_id"] for l in da.decode().splitlines() if l.strip()]
            self.assertEqual(len(cells), len(set(cells)), "pack repeats a cell")
            self.assertGreaterEqual(len(cells), 588, f"pack covers {len(cells)} cells")
            self.assertNotIn(str(REPO).encode(), da, "pack embeds a machine-specific path")


class V17FreshInstall(unittest.TestCase):
    """A runtime that has never received these assets must receive them from the
    canonical repo with no force and no manual step — and the real HOME must not
    move while we prove it."""

    CODE = ("import sys,json;sys.path.insert(0,'.');"
            "from rig_capabilities.catalog import Repo;"
            "print(json.dumps(Repo('.').install('rig-build-standard', harness='omp')))")

    def test_install_into_an_untouched_home(self):
        real = Path.home() / ".rig/universal-skills-registry/skills/rig-build-standard/SKILL.md"
        before = real.read_bytes() if real.is_file() else None
        canon = REPO / "capabilities/skills/rig-build-standard/SKILL.md"
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            r = _run(self.CODE, fake)
            self.assertEqual(r.returncode, 0, r.stderr[-400:])
            got = json.loads(r.stdout)
            self.assertEqual(got["status"], "installed", got)
            self.assertEqual(Path(got["target"]).parent,
                             fake / ".rig/universal-skills-registry/skills",
                             "install escaped the isolated HOME")
            landed = Path(got["target"], "SKILL.md").read_bytes()
            self.assertEqual(landed, canon.read_bytes(), "installed bytes differ from canonical")
        if before is not None:
            self.assertEqual(real.read_bytes(), before, "proof run touched the real HOME")

if __name__ == "__main__":
    unittest.main(verbosity=2)
