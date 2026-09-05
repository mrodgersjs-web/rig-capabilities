"""The `great_example` ratchet.

`great_example` is a served quality field: the router hands an agent a path to
"what good looks like". 78 of 105 canonicals point at a file that does not
exist (55 harnesses, 14 loops, 7 hooks, 2 skills) and no gate ever noticed,
because `certify`'s `done_tests` gate executes `done_when` and nothing opened
the exemplar path. The count was found while verifying the mh-02 upgrade —
mh-02 was the only `mh-0*` harness whose declared exemplar existed.

This test does three things:

1. proves the detector fires (via `--plant`, which fabricates a dangling entry
   in its own report and writes nothing), and refuses a plant for an asset that
   declares no exemplar;
2. ratchets the estate number: it may only go DOWN. `BASELINE` is the count at
   the time the gap was found. Raising it requires editing this file, which is
   the point;
3. gates the assets introduced by this increment *hard*: anything authored in
   the fable-2031 work must ship a real exemplar, so the debt is never added to.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

SCRIPT = REPO_ROOT / "scripts" / "exemplar_resolution.py"

# Found at 78 on the day this gap was measured; the four exemplars written in
# this increment (mh-02, the orchestration loop, mh-01, mh-05) brought it to 74.
# Lower is better. Raising this number means new decoration shipped: a
# `great_example` that points at nothing is a quality field that reads as rigour
# and delivers nothing.
BASELINE = 74

# Assets authored or upgraded in this increment. Hard gate: no dangling, no stub.
NEW_ASSETS = (
    "mh-02-harness-forge-session.yaml",
    "doer-checker-validator.md",
    "adversarial-agent-orchestration.md",
    "mh-01-skill-genesis-session.yaml",
    "mh-05-asset-pruning-session.yaml",
    "working-memory-commit-gate.sh",
    "skill-preload-precondition-gate.sh",
    "rail-registry-four-way-gate.sh",
    "gamma-trace-record-and-failure-attribution",
    "capabilities-round.md",
    "capabilities-done-test.md",
    "rig-capabilities-register.md",
    "experience-lesson-records",
    "evaluator-forge-from-exemplars",
    "task-authority-over-skill-authority.sh",
    "harness-assembly-contract.md",
    "immutable-surface-guard.sh",
    "attempt-identity-ledger-and-equal-weight",
    "evidence-retrieval-citations-gate",
    # RIG Lattice System bundle — six assets, six real exemplars.
    "rig-lattice-system",
    "rig-deviation-engines",
    "rig-idea-generator",
    "rig-lattice-system.md",
    "rig-lattice-router.md",
    "mh-07-lattice-application-session.yaml",
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=REPO_ROOT, capture_output=True, text=True,
                          timeout=600)


def _report() -> dict:
    proc = _run("--json")
    body = proc.stdout
    return json.JSONDecoder().raw_decode(body[body.find("{"):])[0]


class ExemplarResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # `.index.json` is a generated artifact and is gitignored, so a clean checkout has no
        # index and every reader below would die on a missing file instead of testing anything.
        index = REPO_ROOT / ".index.json"
        if not index.is_file():
            from rig_capabilities.catalog import Repo
            Repo(str(REPO_ROOT)).build_index()
            cls.assertTrue(index.is_file(), "build_index wrote no index")

    def test_detector_fires_on_a_planted_dangling_entry(self):
        clean = _run()
        self.assertEqual(clean.returncode, 0, clean.stdout[-200:])
        self.assertEqual(_report()["missing"], [])
        planted = _run("--plant", "semgrep-rule-creator")
        self.assertEqual(planted.returncode, 1, planted.stdout[-200:])
        self.assertIn("(planted)", planted.stdout,
                      "the plant must be distinguishable from a real finding")
        base = _report()
        body = _run("--json", "--plant", "semgrep-rule-creator").stdout
        rep = json.JSONDecoder().raw_decode(body[body.find("{"):])[0]
        self.assertEqual(len(rep["missing"]), len(base["missing"]) + 1,
                         "the plant did not add exactly one finding")
        self.assertEqual(rep["missing_count"], len(rep["missing"]))
        self.assertIn("semgrep-rule-creator",
                      [m["id"] for m in rep["missing"] if m.get("planted")])

    def test_plant_refused_for_an_asset_with_no_exemplar(self):
        proc = _run("--plant", "no-such-asset-2031")
        self.assertEqual(proc.returncode, 2, proc.stdout[-200:])
        self.assertIn("plant refused", proc.stdout + proc.stderr)

    def test_ratchet_number_may_only_fall(self):
        rep = _report()
        n = len(rep["missing"])
        self.assertLessEqual(n, BASELINE,
                             f"dangling exemplars rose to {n} (baseline {BASELINE}); "
                             f"new assets must ship a real examples/great/ file")
        self.assertEqual(rep["declared"] - rep["resolved"], n,
                         "declared/resolved/missing do not reconcile")

    def test_fable_2031_assets_have_real_exemplars(self):
        rep = _report()
        dangling = {m["id"] for m in rep["missing"]}
        bad = sorted(a for a in NEW_ASSETS if a in dangling)
        self.assertEqual(bad, [], f"these ship a stub exemplar: {bad}")

    def test_each_named_exemplar_is_substantive(self):
        """Not just present: an exemplar shorter than a paragraph is a stub."""
        idx = json.loads((REPO_ROOT / ".index.json").read_text(encoding="utf-8"))
        by_id = {a["id"]: a for a in idx["assets"] if a.get("source") == "canonical"}
        for name in NEW_ASSETS:
            a = by_id.get(name)
            if a is None:
                continue        # not registered yet in this working tree
            ge = (a.get("quality") or {}).get("great_example")
            self.assertTrue(ge, f"{name} declares no exemplar")
            p = REPO_ROOT / ge
            self.assertTrue(p.is_file(), f"{name}: {ge} missing")
            self.assertGreater(p.stat().st_size, 400,
                               f"{name}: {ge} is {p.stat().st_size} bytes — a stub")
            self.assertIn("\n", p.read_text(encoding="utf-8")[:400],
                          f"{name}: {ge} has no structure")


if __name__ == "__main__":
    unittest.main()
