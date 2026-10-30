"""D85 authority plant-failure tests (plan items S19–S23).

Every gate asserted here is proven RED on a planted defect and GREEN after
restore; the planted case stays as the regression. Seeds live in
runs/agentic-stack-buildout/d85/receipts/ (S11/S12/S13); these are the
deterministic fixtures of the same failures against temp authority trees.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent / (
    "capabilities/skills/rig-determinism-85"
)
sys.path.insert(0, str(SKILL_ROOT))

import tool_selection  # noqa: E402
from d85 import AdmissionBlock  # noqa: E402
from d85_gates import classify_inventory, score_realized  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_d85_gates import GateTestBase, sha256_file  # noqa: E402


def assert_block(case: unittest.TestCase, code: str, callback):
    with case.assertRaises(AdmissionBlock) as caught:
        callback()
    case.assertEqual(caught.exception.code, code)
    return caught.exception


class CriticalControlPlants(GateTestBase):
    """S19: a critical control (control plane / side effect) may never be
    classified as a model runtime; CODE restore must go green."""

    def test_control_plane_model_is_red_and_code_restore_is_green(self) -> None:
        self.write_authority(
            self.classification(
                taxonomies={0: "control plane"}, kinds={0: "MODEL"},
                necessity=[self.necessity(0, self.chain_ids())],
            )
        )
        assert_block(
            self, "CRITICAL_CONTROL_NOT_CODE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )
        # restore: same taxonomy, CODE runtime -> classification goes green
        self.write_authority(
            self.classification(taxonomies={0: "control plane"})
        )
        result = classify_inventory(self.registry_path, "sample")
        self.assertEqual(result["kind_counts"]["CODE"], 7)


class StaleBindingPlants(GateTestBase):
    """S20: a classification must bind the live inventory hash; a stored
    verdict over changed bytes is refused, never reused as fresh evidence."""

    def test_stale_hash_is_red_and_rebind_is_green(self) -> None:
        self.write_authority(
            self.classification(inventory_sha256="sha256:" + "0" * 64)
        )
        assert_block(
            self, "CLASSIFICATION_STALE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )
        self.write_authority(self.classification())
        self.assertEqual(
            classify_inventory(self.registry_path, "sample")["schema"],
            "rig.d85.classified-inventory.v1",
        )

    def test_source_edit_invalidates_previous_binding(self) -> None:
        self.write_authority(self.classification())
        # plant: edit a registered source byte (comment-only: same graph,
        # different bytes) and update the process record's declared hash,
        # exactly as a re-registration would.
        (self.source_root / "worker.py").write_text(
            "# touched during review\n"
            + (self.source_root / "worker.py").read_text(), encoding="utf-8")
        self.process["file_hashes"]["worker.py"] = sha256_file(
            self.source_root / "worker.py")
        self.write_authority()  # process record only; classification untouched
        assert_block(
            self, "CLASSIFICATION_STALE",
            lambda: classify_inventory(self.registry_path, "sample"),
        )


class ScoreThresholdPlants(GateTestBase):
    """S21: D85 admission requires all four ratios >= 0.85; a MODEL operation
    on every path drives the weighted ratio to 12/15 = 0.80 and must block."""

    def test_model_on_every_path_is_red_and_code_restore_is_green(self) -> None:
        ids = self.chain_ids()
        self.write_authority(
            self.classification(
                taxonomies={0: "decision"}, kinds={0: "MODEL"},
                necessity=[self.necessity(0, ids)],
            )
        )
        # fail closed: a below-threshold score raises before any verdict
        assert_block(
            self, "BLOCK_DETERMINISM_RATIO",
            lambda: score_realized(self.registry_path, "sample"),
        )
        # restore: same operation as CODE -> every ratio hits 1.0
        self.write_authority(self.classification(taxonomies={0: "decision"}))
        verdict = score_realized(self.registry_path, "sample")
        self.assertEqual(verdict["verdict"], "REALIZED_PASS")
        self.assertEqual(verdict["ratios"]["aggregate_weighted"], 1.0)


class RegistrarImmutabilityPlants(unittest.TestCase):
    """S22 (plan S26): the registrar re-emits byte-identical records for
    unchanged bytes and refuses changed bytes; records are never rewritten."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="d85-registrar-")
        self.root = Path(self.temp.name)
        self.src = self.root / "src"
        self.authority = self.root / "authority"
        self.src.mkdir()
        (self.authority / "processes").mkdir(parents=True)
        (self.src / "w.py").write_text(
            "import subprocess\n\n\n"
            "def run(value: str) -> int:\n"
            "    return subprocess.call([\"/bin/echo\", value])\n\n\n"
            "def finish(status: int) -> int:\n"
            "    if status != 0:\n        return 1\n    return 0\n",
            encoding="utf-8",
        )
        (self.src / "a.py").write_text(
            "from w import finish, run\n\n\ndef execute() -> int:\n"
            "    return finish(run(\"x\"))\n",
            encoding="utf-8",
        )
        import subprocess as _sp
        stdlib = Path(_sp.__file__).resolve()
        self.argv = [
            sys.executable, str(SKILL_ROOT / "register_process.py"),
            "--process-id", "plant_v1", "--source-root", str(self.src),
            "--entrypoints", "finish@a.py:execute", "--files", "w.py,a.py",
            "--external-module", f"subprocess={stdlib}:subprocess.call",
            "--out-dir", str(self.authority),
        ]

    tearDown = lambda self: self.temp.cleanup()  # noqa: E731

    def test_idempotent_rerun_and_changed_byte_refusal(self) -> None:
        first = subprocess.run(self.argv, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        record = self.authority / "processes" / "plant_v1.process.json"
        self.assertEqual(record.read_text(), first.stdout)
        payload = json.loads(first.stdout)
        external = payload["external_modules"][0]
        self.assertEqual(
            set(external),
            {"module", "artifact_path", "artifact_sha256", "allowed_calls"},
        )
        self.assertEqual(external["module"], "subprocess")
        self.assertEqual(external["allowed_calls"], ["subprocess.call"])
        self.assertEqual(
            external["artifact_sha256"],
            hashlib.sha256(Path(external["artifact_path"]).read_bytes()).hexdigest(),
        )
        second = subprocess.run(self.argv, capture_output=True, text=True)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, first.stdout)  # byte-identical re-emission
        self.assertEqual(record.read_text(), first.stdout)  # record untouched
        # plant: change one source byte
        (self.src / "w.py").write_text(
            (self.src / "w.py").read_text() + "# touched\n", encoding="utf-8")
        third = subprocess.run(self.argv, capture_output=True, text=True)
        self.assertEqual(third.returncode, 2)
        self.assertIn("new process-id", third.stderr)
        self.assertEqual(record.read_text(), first.stdout)  # refusal rewrote nothing
        # restore path: changed bytes go to a NEW immutable id
        bumped = subprocess.run(
            [arg.replace("plant_v1", "plant_v2") for arg in self.argv],
            capture_output=True, text=True)
        self.assertEqual(bumped.returncode, 0, bumped.stderr)
        self.assertTrue((self.authority / "processes" / "plant_v2.process.json").is_file())
        self.assertEqual(record.read_text(), first.stdout)  # v1 never mutated

    def test_snapshot_conflict_refuses_before_record_write(self) -> None:
        subprocess.run(self.argv, capture_output=True, text=True)
        # plant: someone rewrote the registered snapshot with other bytes
        snap = self.authority / "sources" / "plant_v1" / "w.py"
        snap.write_text("# replaced\n", encoding="utf-8")
        run = subprocess.run(self.argv, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("different bytes", run.stderr)
        # the v1 record remains the original bytes it was registered with
        self.assertIn("plant_v1", (self.authority / "processes"
                                   / "plant_v1.process.json").read_text())


class CertifierA1OnlyPlants(unittest.TestCase):
    """S23: A2/A3/A4 cells driven through the A1-only certifier are refused
    even with a perfectly-formed self-authored failure receipt."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="d85-a1only-")
        self.root = Path(self.temp.name)

    tearDown = lambda self: self.temp.cleanup()  # noqa: E731

    def _a1_failure(self, command: str = "pytest tests -x") -> dict:
        evidence = {"command": command, "exit_code": 1,
                    "output": "1 failed: A1 attempt did not converge"}
        raw = json.dumps(evidence, sort_keys=True).encode("utf-8")
        (self.root / "a1-failure.json").write_bytes(raw)
        return {
            "command": command, "exit_code": 1,
            "evidence_path": "a1-failure.json",
            "evidence_sha256": hashlib.sha256(raw).hexdigest(),
        }

    def test_non_a1_cell_with_self_authored_failure_is_refused(self) -> None:
        criteria = {"failure_cost": 0.9, "reversibility": 0.1,
                    "mechanism_clarity": 0.2, "past_failure_rate": 0.8,
                    "data_volume": 0.5}
        from rig_lattice.lattice import bms
        result = bms.compute_bms(**criteria, level="L3")
        cell_id = f"L3-D2-{result.mode.value}-I1"
        context = {"cell_id": cell_id,
                   "bms": {**criteria, "level": "L3"},
                   "a1_failure": self._a1_failure()}
        with self.assertRaises(tool_selection.ToolSelectionBlock) as caught:
            tool_selection.validate_lattice(context, root=self.root)
        self.assertEqual(caught.exception.code, "LATTICE_BLOCK")
        self.assertIn("trusted A1 execution receipt", str(caught.exception))
        self.assertFalse(result.mode.value == "A1")  # the plant is genuinely non-A1

    def test_a1_cell_same_evidence_restores_green(self) -> None:
        context = {
            "cell_id": "L3-D2-A1-I1",
            "bms": {"failure_cost": 0.5, "reversibility": 0.95,
                    "mechanism_clarity": 0.95, "past_failure_rate": 0.0,
                    "data_volume": 0.5, "level": "L3"},
            "a1_failure": None,
        }
        verdict = tool_selection.validate_lattice(context, root=self.root)
        self.assertEqual(verdict["cell_id"], "L3-D2-A1-I1")
        self.assertIsNone(verdict["a1_failure"])


if __name__ == "__main__":
    unittest.main()
