"""P6: Certify2031Tests — the seven fable-2031 gates exist, plant, and go RED.

Law L3, honoured literally: this module never calls `self_test`, never names
the `suite` gate, and never runs the full unittest module. It proves the three
things a plant-failure copytree would otherwise have to prove slowly — every
new key is registered in `GATES`, every key owns a branch in `_plant`, and
`self_test` learned the `only` parameter — and then proves each gate actually
turns RED on a hand-built bad fixture, in a temp root, in milliseconds.

The bad-fixture roots hold copies of ONLY the files each gate reads (law L1's
own surface), mutated by the production `_plant` branch itself: the same code
`self_test` runs, minus the repo-sized copy.
"""
from __future__ import annotations

import inspect
import json
import shutil
import tempfile
import types
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

NEW_GATES = ("register", "corpus_refusal", "canary_detection",
             "lease_exclusivity", "fable_dormant", "stage_order",
             "evidence_ledger")
OLD_GATES = ("suite", "index_fresh", "done_tests", "idp_integrity", "acl_jake")


def _stub(root):
    """Repo-shaped stub: every new gate reads only `.root`."""
    return types.SimpleNamespace(root=Path(root))


class Certify2031Tests(unittest.TestCase):
    """Registration, plant-branch presence, shape, and one RED per gate."""

    # ------------------------------------------------------------ machinery

    def _tree(self, relfiles):
        """Fresh root holding copies of repo files at the same relative paths."""
        root = Path(tempfile.mkdtemp(prefix="f31-gate-"))
        self.addCleanup(shutil.rmtree, root, True)
        for rel in relfiles:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / rel, dst)
        return root

    def _planted_red(self, gate, relfiles, expect_in_detail):
        from rig_capabilities.certify import GATES, _plant
        root = self._tree(relfiles)
        note = _plant(gate, root)
        self.assertTrue(isinstance(note, str) and note, f"{gate}: empty plant note")
        out = GATES[gate](_stub(root))
        self.assertIsInstance(out, tuple, f"{gate}: not a (bool, str) tuple")
        self.assertEqual(len(out), 2, f"{gate}: not a (bool, str) tuple")
        ok, detail = out
        self.assertIsInstance(ok, bool, f"{gate}: ok is {type(ok).__name__}")
        self.assertIsInstance(detail, str, f"{gate}: detail is not a str")
        self.assertFalse(ok, f"{gate} stayed GREEN on its plant: {detail}")
        self.assertIn(expect_in_detail, detail,
                      f"{gate}: RED for the wrong reason: {detail}")
        return detail

    # ------------------------------------------------------------ structure

    def test_seven_new_gates_registered_exactly(self):
        from rig_capabilities.certify import GATES
        for name in NEW_GATES:
            with self.subTest(gate=name):
                self.assertIn(name, GATES, f"{name} absent from GATES")
                self.assertTrue(callable(GATES[name]), f"{name} not callable")
        self.assertEqual(set(GATES), set(OLD_GATES) | set(NEW_GATES),
                         "GATES gained or lost a key beyond the locked twelve")
        self.assertNotIn("self_test", str(getattr(self, "_nameTransform", "")))

    def test_self_test_learns_only(self):
        from rig_capabilities.certify import self_test
        params = inspect.signature(self_test).parameters
        self.assertEqual(list(params)[:2], ["repo", "only"],
                         "self_test(repo, only=...) is the P6 contract")
        self.assertIsNone(params["only"].default, "only must default to None")

    def test_every_new_gate_owns_a_plant_branch(self):
        from rig_capabilities.certify import _plant
        empty = Path(tempfile.mkdtemp(prefix="f31-plant-"))
        self.addCleanup(shutil.rmtree, empty, True)
        for name in NEW_GATES:
            with self.subTest(gate=name):
                try:
                    _plant(name, empty)
                except KeyError:
                    self.fail(f"{name}: _plant has no branch — self_test "
                              f"would skip its plant-failure proof")
                except Exception:
                    pass  # missing-file errors PROVE the branch was entered

    def test_unknown_plant_name_still_raises(self):
        from rig_capabilities.certify import _plant
        empty = Path(tempfile.mkdtemp(prefix="f31-plant-"))
        self.addCleanup(shutil.rmtree, empty, True)
        with self.assertRaises(KeyError):
            _plant("zz-no-such-gate", empty)

    def test_gates_return_bool_str_on_live_tree(self):
        from rig_capabilities.certify import GATES
        for name in NEW_GATES:
            with self.subTest(gate=name):
                out = GATES[name](_stub(REPO_ROOT))   # must not raise
                self.assertIsInstance(out, tuple)
                self.assertEqual(len(out), 2)
                self.assertIsInstance(out[0], bool)
                self.assertIsInstance(out[1], str)

    # ------------------------------------------------------------- RED paths
    # each: production _plant mutates a copy of the gate's own L1 surface,
    # then the gate must name the break in its detail.

    def test_register_red_on_blanked_evidence(self):
        self._planted_red("register", ["capability_register.csv"],
                          "acl_policy_surface[evidence_paths_empty]")

    def test_corpus_refusal_red_at_015(self):
        detail = self._planted_red(
            "corpus_refusal", ["tests/fixtures/fable2031/corpus-manifest.json"],
            "rate=0.1500")
        self.assertIn("unclassified=3/20", detail)

    def test_canary_detection_red_when_a_decoy_walks(self):
        # decoy-2 -> all-green packet: registered, enters the detector, walks
        # out unflagged. 2/3 caught is the card-8 kill criterion.
        files = [f"tests/fixtures/fable2031/redteam/decoy-{i}.json"
                 for i in (1, 2, 3)]
        files.append("tests/fixtures/fable2031/handoff-honest.json")
        detail = self._planted_red("canary_detection", files, "2/3")
        self.assertIn("detection_incomplete:2 of 3 caught", detail)
        # decoys 1 and 3 must still be caught by their own distinct causes
        self.assertIn("decoy-1.json[canary_reported_green]:FABRICATED", detail)
        self.assertIn("decoy-3.json", detail)

    def test_lease_exclusivity_red_on_granted_pin(self):
        # The scenario is replayed against a throwaway state root inside the
        # stub tree; op2's flipped `granted` pin contradicts the real denial.
        self._planted_red("lease_exclusivity",
                          ["tests/fixtures/fable2031/lease-scenario.json"],
                          "op2")

    def test_fable_dormant_red_on_injected_fallback(self):
        self._planted_red("fable_dormant",
                          ["tests/fixtures/fable2031/routes/litellm.yaml"],
                          "rig-fable51")

    def test_stage_order_red_on_swapped_stages(self):
        self._planted_red("stage_order",
                          ["tests/fixtures/fable2031/iqrsqpi-run.json"],
                          "stage_backtrack")

    def test_evidence_ledger_red_on_planned_resume(self):
        root = self._tree(["tests/fixtures/fable2031/evidence-ledger-valid.csv"])
        # give every row its evidence file, so the ONLY break is E-104's lane
        for rel in ("rig_capabilities/expert_os.py", "rig_capabilities/certify.py",
                    "rig_capabilities/evidence_ledger.py", "docs/ROADMAP.md"):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("")
        from rig_capabilities.certify import GATES, _plant
        _plant("evidence_ledger", root)
        ok, detail = GATES["evidence_ledger"](_stub(root))
        self.assertFalse(ok, f"gate stayed GREEN on the plant: {detail}")
        self.assertIn("E-104:unverified_claim_on_resume", detail, detail)


if __name__ == "__main__":
    unittest.main()
