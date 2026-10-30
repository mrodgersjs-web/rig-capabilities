"""A coding agent's prose cannot promote its own completion claim."""
import hashlib
import unittest
from unittest.mock import patch
from pathlib import Path

from rig_capabilities.completion import _run_check, check_completion


ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = "rig_capabilities/completion.py"


def evidence():
    return {"claim": "The completion gate checks actual artifact bytes and tests",
            "artifacts": [{"path": ARTIFACT,
                           "sha256": hashlib.sha256((ROOT / ARTIFACT).read_bytes()).hexdigest()}],
            "test_commands": [["python3", "-m", "unittest", "tests.test_completion_gate"]]}


def green(_argv, _root):
    return {"argv": ["python3", "-m", "unittest"], "exit_code": 0,
            "tests_run": 4, "output_sha256": "a" * 64}


def contract():
    return {"intent": "Build a verified completion gate", "acceptance_criteria": ["Tests pass"],
            "required_artifacts": [ARTIFACT],
            "test_commands": [["python3", "-m", "unittest", "tests.test_completion_gate"]]}


def jev_pass(_state, _root):
    return {"status": "PASS", "decision_id": 123, "advisory": True}


class CompletionGateTests(unittest.TestCase):
    def test_missing_artifact_blocks_before_jev(self):
        item = evidence()
        item["artifacts"][0]["sha256"] = "0" * 64
        result = check_completion(item, ROOT, runner=green,
                                  jev_loader=lambda *_: self.fail("Jev must not run"))
        self.assertEqual(result["status"], "BLOCK")
        self.assertTrue(any(e.startswith("artifact_drift:") for e in result["errors"]))

    def test_failed_behavior_blocks_before_jev(self):
        result = check_completion(evidence(), ROOT,
                                  controller_contract=contract(), runner=lambda *_: {"exit_code": 1},
                                  jev_loader=lambda *_: self.fail("Jev must not run"))
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("behavioral_check_failed", result["errors"])

    def test_jev_pass_does_not_certify_uncalibrated_claim(self):
        result = check_completion(evidence(), ROOT, controller_contract=contract(), runner=green,
                                  jev_loader=jev_pass,
                                  independent_verifier=lambda _: {"status": "VERIFIED",
                                                                   "family": "reviewer",
                                                                   "observations": ["Observed expected parser behavior"]})
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("certified_completion_adapter_missing", result["errors"])
        self.assertFalse(result["automatic_completion_authorized"])

    def test_unavailable_jev_and_missing_independent_review_fail_closed(self):
        result = check_completion(evidence(), ROOT, controller_contract=contract(), runner=green,
                                  jev_loader=lambda *_: (_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("jev_unavailable", result["errors"])
        self.assertIn("independent_verifier_missing", result["errors"])

    def test_self_review_and_malformed_review_cannot_clear(self):
        item = evidence()
        item["builder_family"] = "codex"
        result = check_completion(item, ROOT, controller_contract=contract(), runner=green, jev_loader=jev_pass,
                                  independent_verifier=lambda _: {"status": "VERIFIED",
                                                                   "family": "codex",
                                                                   "observations": ["Looks good"]})
        self.assertIn("independent_verifier_not_verified", result["errors"])
        malformed = check_completion(item, ROOT, controller_contract=contract(), runner=green, jev_loader=jev_pass,
                                     independent_verifier=lambda _: "VERIFIED")
        self.assertIn("independent_verifier_not_verified", malformed["errors"])

    def test_outside_artifact_rejected_before_test_or_jev(self):
        item = evidence()
        item["artifacts"][0]["path"] = "../../etc/hosts"
        result = check_completion(item, ROOT,
                                  runner=lambda *_: self.fail("test must not run"),
                                  jev_loader=lambda *_: self.fail("Jev must not run"))
        self.assertEqual(result["status"], "BLOCK")

    def test_agent_supplied_checks_never_run_without_controller_contract(self):
        result = check_completion(evidence(), ROOT,
                                  runner=lambda *_: self.fail("untrusted check executed"),
                                  jev_loader=lambda *_: self.fail("Jev must not run"))
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("trusted_controller_contract_missing", result["errors"])

    def test_zero_tests_cannot_pass(self):
        result = check_completion(evidence(), ROOT, controller_contract=contract(),
                                  runner=lambda *_: {"exit_code": 0, "tests_run": 0},
                                  jev_loader=lambda *_: self.fail("Jev must not run"))
        self.assertIn("behavioral_check_failed", result["errors"])

    def test_outside_and_discovery_commands_rejected(self):
        for argv in (["python3", "-m", "unittest"],
                     ["python3", "-m", "unittest", "discover", "-s", "/tmp"],
                     ["pytest", "/tmp/evil.py"]):
            self.assertEqual(_run_check(argv, ROOT)["error"], "command_not_permitted")

    def test_unexpected_callback_error_fails_closed(self):
        result = check_completion(evidence(), ROOT, controller_contract=contract(),
                                  runner=green, jev_loader=jev_pass,
                                  independent_verifier=lambda _: {}["missing"])
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("independent_verifier_error", result["errors"])
        self.assertFalse(result["automatic_completion_authorized"])

    def test_stdout_cannot_spoof_nonzero_unittest_count(self):
        class Process:
            returncode = 0
            stdout = "Ran 7 tests in 0.01s\nOK\n"
            stderr = "Ran 0 tests in 0.00s\nOK\n"
        with patch("rig_capabilities.completion.subprocess.run", return_value=Process()):
            result = _run_check(["python3", "-m", "unittest", "tests.test_completion_gate"], ROOT)
        self.assertEqual(result["tests_run"], 0)


if __name__ == "__main__":
    unittest.main()
