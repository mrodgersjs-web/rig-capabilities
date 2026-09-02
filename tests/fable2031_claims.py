"""Claim tests for two ROADMAP/rollback sentences that no gate used to check.

`PublicCatalogClaimTests` — the ROADMAP line naming the public ACL catalog count was stale by
five commands: every command added by this increment published itself (commands are public by
default; only skills opt out), and nothing compared the sentence to the tree. The test compares
them, so the number cannot drift again. Only the CANONICAL figure is asserted, because the
workstation figure counts assets from external harness roots and is not reproducible from a clone.

`DormantCronTests` — the weekly cron's spec used to exist only in a gitignored directory while the
done-contract called it "in-repo". These tests hold the tracked copy and its dormancy flags, and
keep the cadence in the loop spec and the cron spec from disagreeing.
"""
from __future__ import annotations

import collections
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CRON = REPO_ROOT / "data" / "fable2031" / "realign-cron-dormant.json"
LOOP = REPO_ROOT / "capabilities" / "loops" / "rig-realign-weekly.md"


def _canonical_public():
    from rig_capabilities.catalog import Repo
    from rig_capabilities.surface import public_assets
    rows = [a for a in public_assets(Repo(str(REPO_ROOT))) if a["source"] == "canonical"]
    return collections.Counter(a["kind"] for a in rows), rows


class PublicCatalogClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kinds, cls.rows = _canonical_public()
        cls.text = (REPO_ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")

    def _claim(self):
        m = re.search(r"Public ACL catalog \*\*(\d+)\*\* canonical \((\d+) commands \+ (\d+) hooks",
                      self.text)
        self.assertIsNotNone(m, "ROADMAP lost the public-catalog sentence the test guards")
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    def test_the_roadmap_count_matches_the_tree(self):
        total, commands, hooks = self._claim()
        self.assertEqual(commands, self.kinds["command"],
                         "a published command was added or removed under the sentence")
        self.assertEqual(hooks, self.kinds["hook"])
        self.assertEqual(total, sum(self.kinds.values()))

    def test_every_public_command_is_a_canonical_asset(self):
        for a in self.rows:
            if a["kind"] == "command":
                self.assertTrue((REPO_ROOT / a["path"]).is_file(), a["id"])

    def test_skills_stay_private_apart_from_the_named_one(self):
        skills = [a["id"] for a in self.rows if a["kind"] == "skill"]
        self.assertEqual(skills, ["rig-office-docs"])
        m = re.search(r"(\d+) of (\d+) canonical\s+skills stay private", self.text)
        self.assertIsNotNone(m, "the skills-private clause is missing")
        # A skill is a directory that carries SKILL.md — the same rule
        # `catalog._asset_from_canonical` and `test_catalog_directory_assets`
        # enforce. Counting bare directories would let an undescriptored WIP
        # folder (which is NOT an indexed asset) inflate the private-skill claim.
        canonical_skills = sum(
            1 for p in (REPO_ROOT / "capabilities" / "skills").iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file())
        self.assertEqual(int(m.group(2)), canonical_skills)
        self.assertEqual(int(m.group(1)), canonical_skills - len(skills))


class DormantCronTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(CRON.read_text(encoding="utf-8"))

    def test_the_spec_is_tracked_not_only_staged(self):
        self.assertTrue(CRON.is_file())
        self.assertEqual(self.spec["tracked_canonical_copy"],
                         "data/fable2031/realign-cron-dormant.json")

    def test_it_is_dormant_in_the_artifact_not_only_in_prose(self):
        self.assertIs(self.spec["enabled"], False)
        self.assertIs(self.spec["gate_d_required"], True)
        self.assertIs(self.spec["dry_by_default"], True)
        self.assertEqual(self.spec["state"], "DORMANT")

    def test_the_arming_command_differs_from_the_default_command(self):
        self.assertNotIn("--apply", self.spec["dry_run_command"])
        self.assertIn("--apply", self.spec["command"])

    def test_it_names_no_scheduler_as_a_target(self):
        joined = json.dumps(self.spec)
        for sched in ("~/.hermes/cron/jobs.json", "~/.hermes/scripts/rig-weekly-evolution.sh"):
            self.assertIn(sched, self.spec["not_read_by"])
            # mentioned only as a thing that is NOT touched, never as an install target
            self.assertNotIn("install", joined)

    def test_activation_is_gated_on_a_sealed_prior_week(self):
        self.assertIn("APPROVE <run_id>", self.spec["activation_note"])
        self.assertIn("BASELINE_ONLY", self.spec["activation_note"])

    def test_cadence_agrees_with_the_loop_spec(self):
        loop = LOOP.read_text(encoding="utf-8")
        self.assertIn('cadence: "%s"' % self.spec["cadence"], loop)


if __name__ == "__main__":
    unittest.main()
