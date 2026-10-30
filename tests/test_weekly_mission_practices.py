import unittest

from scripts.weekly_mission_practices import stage


class WeeklyMissionPracticeTests(unittest.TestCase):
    def test_stage_keeps_metadata_not_source_body(self):
        sources = [{"id": "test", "url": "https://www.promptfoo.dev/example", "topic": "eval"}]
        report = stage(sources, lambda _: b"<title>Test page</title><h1>Useful pattern</h1><p>copyrighted body</p>")
        self.assertEqual(report["sources"][0]["status"], "candidate")
        self.assertNotIn("copyrighted body", str(report))
        self.assertFalse(report["promotion_authorized"])

    def test_fetch_failure_is_visible(self):
        sources = [{"id": "test", "url": "https://www.promptfoo.dev/example", "topic": "eval"}]
        def fail(_):
            raise TimeoutError("timeout")
        report = stage(sources, fail)
        self.assertEqual(report["sources"][0]["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
