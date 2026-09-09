"""CLI regression tests — select / checklist / estate-validate subcommands and
the typed exit-2 block paths for both exception families."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tool_selection import _live_inventory_sha256

CLI = (Path(__file__).resolve().parents[1]
       / "capabilities/skills/rig-determinism-85/bin/rig-determinism-85")

CLOCK = {"clock_critical": {"named_consumer": "x", "failure_mode": "y",
                            "sla_start_latency_seconds": 30,
                            "recovery_policy": "catch_up"}}


def run_cli(*argv: str) -> tuple[int, dict | str]:
    with tempfile.TemporaryDirectory(prefix="d85-cli-") as home:
        Path(home, "enforcement.json").write_text(json.dumps({"roots": [home], "ttl_hours": 24}))
        env = {k: v for k, v in os.environ.items() if k != "RIG_D85_DISABLE"}
        env["RIG_D85_HOME"] = home
        proc = subprocess.run([sys.executable, str(CLI), *argv],
                              capture_output=True, text=True, timeout=30, env=env)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = proc.stdout
    return proc.returncode, payload


class CliSelectTests(unittest.TestCase):
    def test_select_happy_path_exit_0(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(CLOCK, fh)
            path = fh.name
        code, payload = run_cli("select", path)
        self.assertEqual(code, 0)
        self.assertEqual(payload["framework"], "temporal")

    def test_select_block_exit_2_typed_json(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"resident_service": {"resource_kind": "keepalive_daemon",
                                             "resource_detail": "x"}}, fh)
            path = fh.name
        code, payload = run_cli("select", path)
        self.assertEqual(code, 2)
        self.assertEqual(payload["schema"], "rig.d85.tool-selection-block.v1")
        self.assertEqual(payload["code"], "TOOL_SELECTION_MALFORMED")

    def test_select_duplicate_json_key_is_malformed(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"clock_critical": null, "clock_critical": null}')
            path = fh.name
        code, payload = run_cli("select", path)
        self.assertEqual(code, 2)
        self.assertEqual(payload.get("reason") or payload.get("code"), "SUBMITTED_MALFORMED")

    def test_admission_block_paths_still_typed(self) -> None:
        # Old commands must keep their typed exit-2 behavior: a compare against
        # a malformed file exercises the AdmissionBlock handler.
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{not json")
            path = fh.name
        code, payload = run_cli("compare", "never-scored", path)
        self.assertEqual(code, 2)
        self.assertEqual(payload.get("reason") or payload.get("code"), "SUBMITTED_MALFORMED")

class CliChecklistTests(unittest.TestCase):
    def _build_file(self, fields: dict) -> str:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(fields, fh)
            return fh.name

    def _fields(self, **over) -> dict:
        base = {
            "process_id": "julie_synthetic",
            "inventory_sha256": _live_inventory_sha256(),
            "framework": "kestra_pydantic",
            "properties": {},
            "durable_system": True,
            "pydantic_models": ["In", "Out"],
            "model_necessity_claims": ["classify: deterministic sort failed"],
            "archify_diagram_path": "diagram.json",
            "d85_realized_pass": True,
            "orchestration_is_code": True,
        }
        base.update(over)
        return base

    def _diagram_dir(self) -> Path:
        d = Path(tempfile.mkdtemp())
        (d / "diagram.json").write_text('{"diagram_type": "workflow"}')
        self.addCleanup(lambda: (d / "diagram.json").unlink())
        return d

    def test_unbound_checklist_blocks_even_when_checks_pass(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields())
        code, payload = run_cli("checklist", path, "--root", str(root))
        self.assertEqual(code, 2)
        self.assertEqual(payload["inventory_binding"], "unbound")
        self.assertEqual(payload["verdict"], "CHECKLIST_BLOCK")
        self.assertIn("binding_reason", payload)

    def test_bound_checklist_passes_with_inventory_hash(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields())
        code, payload = run_cli("checklist", path, "--root", str(root),
                                "--process-id", "julie_synthetic")
        self.assertEqual(code, 0)
        self.assertEqual(payload["inventory_binding"], "bound")
        self.assertEqual(payload["verdict"], "CHECKLIST_PASS")
        self.assertEqual(len(payload["inventory_sha256"]), 64)

    def test_bound_hash_is_deterministic_across_runs(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields())
        hashes = set()
        for _ in range(2):
            code, payload = run_cli("checklist", path, "--root", str(root),
                                    "--process-id", "julie_synthetic")
            self.assertEqual(code, 0)
            hashes.add(payload["inventory_sha256"])
        self.assertEqual(len(hashes), 1)

    def test_bound_checklist_still_blocks_on_failing_check(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields(d85_realized_pass=False))
        code, payload = run_cli("checklist", path, "--root", str(root),
                                "--process-id", "julie_synthetic")
        self.assertEqual(code, 2)
        self.assertEqual(payload["verdict"], "CHECKLIST_BLOCK")
        self.assertIsNotNone(payload["inventory_sha256"])

    def test_declared_process_mismatch_blocks(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields(process_id="some_other_process"))
        code, payload = run_cli("checklist", path, "--root", str(root),
                                "--process-id", "julie_synthetic")
        self.assertEqual(code, 2)
        self.assertEqual(payload["inventory_binding"], "mismatched")
        self.assertEqual(payload["verdict"], "CHECKLIST_BLOCK")
        self.assertIn("binding_reason", payload)

    def test_unknown_process_id_blocks(self) -> None:
        root = self._diagram_dir()
        path = self._build_file(self._fields(process_id="no_such_process"))
        code, payload = run_cli("checklist", path, "--root", str(root),
                                "--process-id", "no_such_process")
        self.assertEqual(code, 2)
        self.assertEqual(payload.get("reason") or payload.get("code"), "UNKNOWN_PROCESS")

    def test_stale_hash_replay_blocks(self) -> None:
        root = self._diagram_dir()
        stale = self._fields(inventory_sha256="0" * 64)
        path = self._build_file(stale)
        code, payload = run_cli("checklist", path, "--root", str(root),
                                "--process-id", "julie_synthetic")
        self.assertEqual(code, 2)
        self.assertEqual(payload["inventory_binding"], "stale")
        self.assertEqual(payload["verdict"], "CHECKLIST_BLOCK")
        self.assertIn("binding_reason", payload)

    def test_verify_cert_honest_replay_exits_zero(self) -> None:
        root = self._diagram_dir()
        build_path = self._build_file(self._fields())
        code, certificate = run_cli("checklist", build_path, "--root", str(root),
                                    "--process-id", "julie_synthetic")
        self.assertEqual(code, 0)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(certificate, fh)
            cert_path = fh.name
        code, payload = run_cli("verify-cert", build_path, cert_path, "--root", str(root))
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "CERTIFICATION_VERIFIED")
        self.assertEqual(payload["checklist_sha256"], certificate["checklist_sha256"])

    def test_verify_cert_mutated_build_replay_exits_two(self) -> None:
        root = self._diagram_dir()
        build_path = self._build_file(self._fields())
        code, certificate = run_cli("checklist", build_path, "--root", str(root),
                                    "--process-id", "julie_synthetic")
        self.assertEqual(code, 0)
        mutated = self._fields(framework="temporal")
        mutated_path = self._build_file(mutated)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(certificate, fh)
            cert_path = fh.name
        code, payload = run_cli("verify-cert", mutated_path, cert_path, "--root", str(root))
        self.assertEqual(code, 2)
        self.assertEqual(payload["verdict"], "CERTIFICATION_BLOCK")
        self.assertIn("post-cert mutation", payload["binding_reason"])

    def test_verify_cert_tampered_certificate_snapshot_blocks(self) -> None:
        root = self._diagram_dir()
        build_path = self._build_file(self._fields())
        code, certificate = run_cli("checklist", build_path, "--root", str(root),
                                    "--process-id", "julie_synthetic")
        self.assertEqual(code, 0)
        certificate["inventory_sha256"] = "f" * 64
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(certificate, fh)
            cert_path = fh.name
        code, payload = run_cli("verify-cert", build_path, cert_path, "--root", str(root))
        self.assertEqual(code, 2)
        self.assertEqual(payload["verdict"], "CERTIFICATION_BLOCK")
        self.assertIn("tampered or mispaired", payload["binding_reason"])

    def test_verify_cert_unknown_certificate_field_blocks(self) -> None:
        root = self._diagram_dir()
        build_path = self._build_file(self._fields())
        code, certificate = run_cli("checklist", build_path, "--root", str(root),
                                    "--process-id", "julie_synthetic")
        self.assertEqual(code, 0)
        certificate["extra_field"] = "smuggled"
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(certificate, fh)
            cert_path = fh.name
        code, payload = run_cli("verify-cert", build_path, cert_path, "--root", str(root))
        self.assertEqual(code, 2)
        self.assertEqual(payload["code"], "CERTIFICATION_MALFORMED")


class CliEstateTests(unittest.TestCase):
    def test_estate_validate_exit_0_on_consistent_ledger(self) -> None:
        code, payload = run_cli("estate-validate")
        self.assertEqual(code, 0)
        self.assertTrue(payload["consistent"])
        self.assertEqual(payload["problems"], [])


if __name__ == "__main__":
    unittest.main()
