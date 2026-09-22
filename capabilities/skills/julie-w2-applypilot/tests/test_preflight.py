import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("preflight", Path(__file__).resolve().parents[1] / "scripts/preflight.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReceiptIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / "receipt.txt"
        self.file.write_text("Employer X: application ABC123 received.")
        self.row = {"status": "submitted", "company": "Employer X", "requisition": "ABC123", "occurred_at": "2026-09-07T05:52:00Z", "receipt": {"kind": "employer_portal_confirmation", "reference": "sha256:" + hashlib.sha256(self.file.read_bytes()).hexdigest(), "readback_path": str(self.file)}}
        self.now = datetime(2026, 9, 7, 6, 5, tzinfo=timezone.utc)

    def run_case(self, rows):
        (self.root / "application-events.jsonl").write_text("\n".join(json.dumps(x) for x in rows))
        return module.verify_receipts(self.root, self.now)

    def test_duplicate_receipts_count_once_and_denver_week_rolls_over(self):
        result = self.run_case([self.row, self.row])
        self.assertTrue(result["pass"])
        self.assertEqual(result["verified_total"], 1)
        self.assertEqual(result["rolling_seven_days"], 1)
        self.assertEqual(result["confirmed_this_denver_week"], 0)

    def test_tampered_readback_fails(self):
        self.file.write_text("ABC123 changed after verification")
        self.assertFalse(self.run_case([self.row])["pass"])

    def test_wrong_requisition_fails_even_with_current_hash(self):
        self.file.write_text("Employer X application OTHER999 received")
        self.row["receipt"]["reference"] = "sha256:" + hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.assertFalse(self.run_case([self.row])["pass"])

    def test_unconfirmed_click_is_not_submission(self):
        self.row["receipt"] = {}
        result = self.run_case([self.row])
        self.assertFalse(result["pass"])
        self.assertEqual(result["verified_total"], 0)

    def test_old_untyped_duplicate_is_allowed_only_with_valid_typed_receipt(self):
        legacy = dict(self.row, receipt={})
        self.assertTrue(self.run_case([legacy, self.row])["pass"])

    def test_future_date_fails(self):
        self.row["occurred_at"] = "2027-01-01T00:00:00Z"
        self.assertFalse(self.run_case([self.row])["pass"])


class SkillContract(unittest.TestCase):
    def setUp(self):
        self.package = Path(__file__).resolve().parents[1]

    def test_application_outreach_model_and_todo_controls_are_load_bearing(self):
        skill = (self.package / "SKILL.md").read_text()
        prompt = (self.package / "PROMPT.md").read_text()
        operations = (self.package / "references" / "OPERATIONS.md").read_text()
        capabilities = (self.package / "references" / "CAPABILITIES.md").read_text()
        start_here = (self.package / "START-HERE.md").read_text()
        workers = (self.package / "prompts" / "WORKERS.md").read_text()
        self.assertIn("Applications first", skill)
        self.assertIn("up to two people I am known to know", prompt)
        self.assertIn("unknown but relevant helper, follow or send a relevant connection request", workers)
        self.assertIn("--oneshot -Q", prompt)
        self.assertIn("Unreliable uncensored-model output", operations)
        self.assertIn("Visible task list lifecycle", operations)
        self.assertIn("confirmed-application-answers-2026-09-06.json", operations)
        self.assertIn("blackwell-qwen38-flash", start_here)
        self.assertIn("chat", start_here)
        self.assertIn("  --oneshot -Q", start_here)
        self.assertIn(" -Q", start_here)
        self.assertIn("--provider rig-blackwell-qwen38-flash", start_here)
        self.assertIn("--run-budget 180 --max-turns 10", start_here)
        self.assertIn("Never use top-level `--oneshot`", start_here)
        self.assertIn("Unreliable uncensored routes are quarantined", capabilities)


if __name__ == "__main__":
    unittest.main()
