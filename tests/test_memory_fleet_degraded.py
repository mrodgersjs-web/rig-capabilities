"""The hook must retain authenticated partial knowledge without calling it success."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

SPEC = importlib.util.spec_from_file_location("memory_fleet_degraded",
    Path(__file__).parents[1] / "capabilities/hooks/memory-fleet.py")
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class DegradedKnowledgeTests(unittest.TestCase):
    def value(self):
        return {"status": "degraded", "tenant_id": "rig-default",
                "operator_scope": "rig-coding-fleet", "index_status": "unavailable",
                "retrieval_scope": "recent_intake_only", "failures": ["knowledge_deadline_exceeded"],
                "items": [{"reference": "Knowledge/memory-os-intake-test.md",
                           "source_status": "candidate", "content": "Saved correction."}]}

    def test_transport_preserves_degraded_state_and_value(self):
        def runner(*args, **kwargs):
            return subprocess.CompletedProcess(args, 0, json.dumps(self.value()), "")
        result = HOOK.call("memory.search_knowledge", {"query": "test"}, runner=runner)
        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["value"], self.value())

    def test_turn_retains_candidates_and_reports_retrieval_limit(self):
        def caller(operation, payload, **kwargs):
            if operation == "memory.search_knowledge":
                return {"status": "degraded", "reason": "memory_os_degraded", "value": self.value()}
            return {"status": "ok", "value": {"tenant_id": "rig-default",
                    "operator_scope": "rig-coding-fleet", "retrieved_items": []}}
        result = HOOK.retrieve("codex", "turn", {"prompt": "Aside"}, caller=caller)
        self.assertEqual(result["status"], "degraded")
        self.assertIn("knowledge=degraded", result["metadata"])
        self.assertIn("recent_intake_only", result["reference_text"])
        self.assertIn("Saved correction.", result["reference_text"])

    def test_degraded_scope_mismatch_fails_closed(self):
        def caller(operation, payload, **kwargs):
            if operation == "memory.search_knowledge":
                return {"status": "degraded", "reason": "memory_os_degraded", "value": self.value()}
            return {"status": "ok", "value": {"tenant_id": "other",
                    "operator_scope": "rig-coding-fleet", "retrieved_items": []}}
        result = HOOK.retrieve("codex", "turn", {"prompt": "Aside"}, caller=caller)
        self.assertEqual(result["reason"], "authenticated_scope_mismatch")
        self.assertEqual(result["reference_text"], "")


if __name__ == "__main__":
    unittest.main()
