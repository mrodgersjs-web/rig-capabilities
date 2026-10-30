import unittest

from scripts.check_promptfoo_outcomes import measure


def case(index, kind="representative", success=True, source="abc"):
    return {
        "success": success,
        "gradingResult": {"pass": success,
                          "componentResults": [{"pass": success}]},
        "testCase": {"metadata": {"case_id": f"case-{index}", "kind": kind,
                                  "asset_id": "sample", "source_sha256": source}},
    }


def suite():
    rows = [case(i) for i in range(30)]
    rows[1] = case(1, "non_trigger")
    rows[2] = case(2, "adversarial")
    return {"evalId": "eval-test", "results": {"results": rows}}


class PromptfooOutcomeScreenTests(unittest.TestCase):
    def test_clean_measurement_is_still_not_promotion(self):
        result = measure(suite(), asset_id="sample", source_sha256="abc")
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["status"], "MEASURED_NOT_VERIFIED")
        self.assertEqual(result["promotion"], "BLOCKED")

    def test_four_of_four_routing_eval_cannot_certify_asset(self):
        payload = suite()
        payload["results"]["results"] = payload["results"]["results"][:4]
        result = measure(payload, asset_id="sample", source_sha256="abc")
        self.assertIn("insufficient_cases", result["failures"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_source_drift_and_missing_trace_block(self):
        payload = suite()
        payload["results"]["results"][0]["testCase"]["metadata"]["source_sha256"] = "stale"
        payload["results"]["results"][1]["gradingResult"]["componentResults"] = []
        result = measure(payload, asset_id="sample", source_sha256="abc")
        self.assertIn("source_binding_mismatch:0", result["failures"])
        self.assertIn("missing_assertion_trace:1", result["failures"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_adversarial_failure_hard_blocks_even_above_90_percent(self):
        payload = suite()
        payload["results"]["results"][2] = case(2, "adversarial", False)
        result = measure(payload, asset_id="sample", source_sha256="abc")
        self.assertGreater(result["score"], 0.90)
        self.assertIn("adversarial_failure_hard_block", result["failures"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_duplicate_case_does_not_inflate_score(self):
        payload = suite()
        payload["results"]["results"][3]["testCase"]["metadata"]["case_id"] = "case-2"
        result = measure(payload, asset_id="sample", source_sha256="abc")
        self.assertIn("missing_or_duplicate_case_id:3", result["failures"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_malformed_export_fails_closed_without_crashing(self):
        payload = suite()
        payload["results"]["results"][0]["testCase"] = "malformed"
        payload["results"]["results"][1]["gradingResult"] = "malformed"
        result = measure(payload, asset_id="sample", source_sha256="abc")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("missing_assertion_trace:1", result["failures"])


if __name__ == "__main__":
    unittest.main()
