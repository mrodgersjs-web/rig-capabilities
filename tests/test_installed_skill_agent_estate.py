import tempfile
import unittest
from pathlib import Path

from scripts.audit_installed_skill_agent_estate import inspect, integrity_failures


class InstalledEstateTests(unittest.TestCase):
    def test_exact_drift_alias_external_and_missing_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "capabilities" / "skills" / "sample" / "SKILL.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("---\nname: sample\n---\n")
            codex = root / "codex"
            codex.mkdir()
            (codex / "sample").mkdir()
            (codex / "sample" / "SKILL.md").write_bytes(canonical.read_bytes())
            (codex / "alias").symlink_to(canonical.parent, target_is_directory=True)
            (codex / "external").mkdir()
            (codex / "external" / "SKILL.md").write_text("external")
            (codex / "broken").symlink_to(root / "missing", target_is_directory=True)
            claude = root / "claude"
            claude.mkdir()
            (claude / "sample").mkdir()
            (claude / "sample" / "SKILL.md").write_text("changed")
            empty = root / "empty"
            empty.mkdir()
            result = inspect(root, {"skill": {"codex": str(codex),
                                              "claude": str(claude),
                                              "aside": str(empty)}})
            counts = result["counts"]
            self.assertEqual(counts["by_status"], {
                "ALIAS_OF_CANONICAL": 1,
                "BROKEN_LINK": 1,
                "DRIFT_BYTES": 1,
                "EXACT_BYTES": 1,
                "NONCANONICAL_INSTALLED": 1,
            })
            self.assertEqual(counts["canonical_absence_cells"], 1)
            self.assertEqual(counts["distinct_physical_sources"], 4)
            self.assertEqual(counts["distinct_content_hashes"], 3)
            self.assertEqual(counts["duplicate_content_entries"], 1)
            self.assertEqual(counts["canonical_skills"], 1)

    def test_agent_format_variant_is_unverified_and_blocks_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "capabilities" / "agents" / "sample.md"
            source.parent.mkdir(parents=True)
            source.write_text("agent instructions")
            codex = root / "codex"
            codex.mkdir()
            (codex / "sample.toml").write_text("prompt = 'agent instructions'")
            result = inspect(root, {"agent": {"codex": str(codex)}})
            self.assertEqual(result["counts"]["by_status"], {"FORMAT_VARIANT_UNVERIFIED": 1})
            self.assertEqual(result["counts"]["canonical_absence_cells"], 0)
            self.assertEqual(integrity_failures(result), ["format_variant_unverified"])

    def test_nested_skill_resource_is_visible_but_not_silently_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "capabilities" / "skills" / "sample" / "references" / "SKILL.md"
            nested.parent.mkdir(parents=True)
            nested.write_text("---\nname: nested\n---\n")
            result = inspect(root, {})
            self.assertEqual(result["counts"]["canonical_skills"], 0)
            self.assertEqual(result["counts"]["unregistered_nested_skills"], 1)
            self.assertEqual(result["unregistered_nested_skills"], [str(nested)])

    def test_inventory_of_unowned_entries_is_not_an_outcome_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / "codex"
            codex.mkdir()
            (codex / "external").mkdir()
            (codex / "external" / "SKILL.md").write_text("external")
            result = inspect(root, {"skill": {"codex": str(codex)}})
            self.assertEqual(result["counts"]["by_status"], {"NONCANONICAL_INSTALLED": 1})
            self.assertEqual(integrity_failures(result), [])
            self.assertEqual(result["claim_limit"],
                             "Configured file presence only; runtime load and outcomes unverified.")

    def test_missing_root_does_not_claim_runtime_absence_as_tested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = inspect(root, {"skill": {"codex": str(root / "missing")}})
            self.assertEqual(result["counts"]["missing_roots"], 1)
            self.assertEqual(result["counts"]["installed_entries"], 0)


if __name__ == "__main__":
    unittest.main()
