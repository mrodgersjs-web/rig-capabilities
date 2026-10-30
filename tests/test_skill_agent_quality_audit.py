import tempfile
import unittest
from pathlib import Path

from scripts.audit_skill_agent_quality import audit_asset, report


class SkillAgentQualityAuditTests(unittest.TestCase):
    def test_inventory_reads_source_not_ttl_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: sample\n---\n")
            agent = root / "capabilities" / "agents" / "new-agent"
            agent.mkdir(parents=True)
            (agent / "SKILL.md").write_text("---\nname: new-agent\n---\n")
            counts = report(root)["counts"]
            self.assertEqual(counts["assets"], 2)
            self.assertEqual(counts["by_kind"], {"agent": 1, "skill": 1})
            self.assertEqual(counts["promotable"], 0)

    def test_nested_subskill_is_audited_and_cannot_disappear_from_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "capabilities" / "skills" / "parent" / "references"
            nested.mkdir(parents=True)
            (nested / "SKILL.md").write_text("---\nname: references\n---\n")
            result = report(root)
            self.assertEqual(result["counts"]["by_kind"], {"subskill": 1})
            self.assertEqual(result["counts"]["outcome_verified"], 0)
            self.assertEqual(result["assets"][0]["id"], "parent/references")
            self.assertEqual(result["assets"][0]["promotion"], "BLOCKED")

    def test_file_existence_is_not_a_behavioral_done_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Use for sample tasks\n"
                "owner: test\ndomain: test\noutcome: useful result\n"
                "done_when:\n  - file:capabilities/skills/sample/SKILL.md\n"
                "quality_floor: 0.95\ngreat_example: examples/sample.md\n---\n"
            )
            (root / "examples").mkdir()
            (root / "examples" / "sample.md").write_text("example")
            row = audit_asset({"id": "sample", "kind": "skill",
                               "path": "capabilities/skills/sample"}, root)
            self.assertIn("no_behavioral_done_test", row["spec_gaps"])
            self.assertIsNone(row["outcome_score"])
            self.assertEqual(row["promotion"], "BLOCKED")

    def test_spec_ready_does_not_claim_outcome_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Use for sample tasks\n"
                "owner: test\ndomain: test\noutcome: useful result\n"
                "done_when:\n  - cmd:python3 -m unittest tests.test_sample\n"
                "quality_floor: 0.95\ngreat_example: examples/sample.md\n---\n"
            )
            (root / "examples").mkdir()
            (root / "examples" / "sample.md").write_text("example")
            row = audit_asset({"id": "sample", "kind": "skill",
                               "path": "capabilities/skills/sample"}, root)
            self.assertTrue(row["spec_ready"])
            self.assertFalse(row["portable_frontmatter_screen"])
            self.assertEqual(row["outcome_status"], "UNVERIFIED")
            self.assertEqual(row["promotion"], "BLOCKED")

    def test_prose_or_invalid_exemplar_path_is_a_gap_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            for exemplar in ("x" * 300, "../outside.md", "/outside.md"):
                (skill / "SKILL.md").write_text(
                    f"---\nname: sample\ngreat_example: {exemplar}\n---\n"
                )
                row = audit_asset({"id": "sample", "kind": "skill",
                                   "path": "capabilities/skills/sample"}, root)
                self.assertIn("missing_real_exemplar", row["spec_gaps"])

    def test_unreadable_agent_source_is_a_gap_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents = root / "capabilities" / "agents"
            agents.mkdir(parents=True)
            (agents / "bad.md").write_bytes(b"\xff")
            row = audit_asset({"id": "bad", "kind": "agent",
                               "path": "capabilities/agents/bad.md"}, root)
            self.assertIn("unreadable_source", row["spec_gaps"])
            self.assertEqual(row["promotion"], "BLOCKED")

    def test_portable_key_screen_is_separate_from_rig_quality_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Use for sample tasks\n"
                "metadata:\n  owner: test\n---\n"
            )
            row = audit_asset({"id": "sample", "kind": "skill",
                               "path": "capabilities/skills/sample"}, root)
            self.assertTrue(row["portable_frontmatter_screen"])
            self.assertFalse(row["spec_ready"])
            self.assertEqual(row["promotion"], "BLOCKED")

    def test_portable_metadata_satisfies_owner_domain_outcome_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "capabilities" / "skills" / "sample"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: sample\ndescription: Use for sample tasks\n"
                "compatibility: Requires Python 3\n"
                "metadata:\n  owner: test\n  domain: routing\n"
                "  outcome: correct route\n---\n"
            )
            row = audit_asset({"id": "sample", "kind": "skill",
                               "path": "capabilities/skills/sample"}, root)
            self.assertTrue(row["portable_frontmatter_screen"])
            self.assertNotIn("missing_owner", row["spec_gaps"])
            self.assertNotIn("missing_domain", row["spec_gaps"])
            self.assertNotIn("missing_outcome", row["spec_gaps"])
            self.assertEqual(row["promotion"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
