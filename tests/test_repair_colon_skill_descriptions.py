import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.repair_colon_skill_descriptions import repaired_text


class RepairColonSkillDescriptionsTests(unittest.TestCase):
    def test_repairs_only_yaml_syntax_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "youtube-example" / "SKILL.md"
            skill.parent.mkdir()
            body = "# Instructions\nKeep this body unchanged.\n"
            skill.write_text(
                "---\nname: youtube-example\n"
                "description: Use for this: specific task\n"
                "metadata:\n  handle: @example\n---\n" + body,
                encoding="utf-8",
            )
            repaired = repaired_text(skill)
            self.assertIsNotNone(repaired)
            self.assertTrue(repaired.endswith(body))
            metadata = yaml.safe_load(repaired.split("\n---\n", 1)[0][4:])
            self.assertEqual(metadata["description"], "Use for this: specific task")
            self.assertEqual(metadata["metadata"]["handle"], "@example")
            skill.write_text(repaired, encoding="utf-8")
            self.assertIsNone(repaired_text(skill))

    def test_unrelated_skill_is_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "different-skill" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text("---\nname: different-skill\ndescription: This: breaks YAML\n---\n")
            self.assertIsNone(repaired_text(skill))


if __name__ == "__main__":
    unittest.main()
