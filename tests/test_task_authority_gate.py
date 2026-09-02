"""task-authority-over-skill-authority: the gate must bite, and only bite.

Every class this gate names is one of the ways a skill quietly wins:
inversion (the resolution sides with the skill), undetected conflict (nobody
noticed), uncited rule (nobody logged why), executed losing step (the
resolution papered over and the skill's step ran anyway), phantom record (a
"conflict" the arithmetic cannot reproduce), and malformed record (an assembly
outside the closed grammar gets a CLOSED gate, not a free pass).

The greens matter as much as the reds: a task-won conflict with a cited rule,
a harness guard beating a skill, an escalation with both steps held, and two
compatible directives (requires intersect -> no conflict, no record demanded)
must ALL exit 0, or the gate is just a denial machine.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "capabilities" / "hooks" / "task-authority-over-skill-authority.sh"
CHECKER = (REPO_ROOT / "capabilities" / "hooks" / "task-authority"
           / "check_task_authority.py")
FIXTURES = REPO_ROOT / "capabilities" / "hooks" / "fixtures" / "task-authority"

def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    # never inherit the parent's stdin: an open tty would block `cat` to timeout
    return subprocess.run(["/bin/bash", str(HOOK), *args], cwd=REPO_ROOT,
                          input="" if stdin is None else stdin,
                          capture_output=True, text=True, timeout=15)


class TaskAuthorityGateTests(unittest.TestCase):
    def test_green_task_wins_with_cited_rule(self):
        p = run(str(FIXTURES / "assembly_task_wins.json"))
        self.assertEqual(p.returncode, 0, p.stderr)
        verdict = json.loads(p.stdout)
        self.assertEqual(verdict["verdict"], "CLEAN")
        self.assertEqual(verdict["conflicts_detected"], 1)
        self.assertTrue(verdict["precedence_logged"])

    def test_green_harness_guard_outranks_skill(self):
        p = run(str(FIXTURES / "assembly_harness_wins.json"))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["conflicts_detected"], 1)

    def test_green_compatible_directives_are_not_conflicts(self):
        p = run(str(FIXTURES / "assembly_no_conflict.json"))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["conflicts_detected"], 0)

    def test_green_escalation_holds_both_steps(self):
        p = run(str(FIXTURES / "assembly_escalate.json"))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)["precedence_logged"])

    def test_red_skill_wins_is_an_inversion(self):
        p = run(str(FIXTURES / "assembly_skill_wins.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("AUTHORITY_INVERSION", p.stderr)

    def test_red_undetected_conflict(self):
        p = run(str(FIXTURES / "assembly_conflict_undetected.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("CONFLICT_UNDETECTED", p.stderr)

    def test_red_uncited_precedence_rule(self):
        p = run(str(FIXTURES / "assembly_rule_uncited.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("RULE_UNCITED", p.stderr)

    def test_red_executed_losing_step_is_silent_compliance(self):
        p = run(str(FIXTURES / "assembly_executed_losing_step.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("EXECUTED_LOSING_STEP", p.stderr)

    def test_red_phantom_record_not_reproducible(self):
        p = run(str(FIXTURES / "assembly_phantom_record.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("RESOLUTION_PHANTOM", p.stderr)

    def test_red_authority_outside_the_ladder(self):
        p = run(str(FIXTURES / "assembly_malformed_authority.json"))
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("RECORD_MALFORMED", p.stderr)

    def test_usage_and_missing_record_refuse_never_judge(self):
        no_args = run()
        self.assertEqual(no_args.returncode, 1, "no args is a refusal (1), not a verdict")
        self.assertEqual(no_args.returncode, run("/nonexistent/record.json").returncode)
        self.assertEqual(run(stdin="").returncode, 1, "empty stdin is a refusal")

    def test_unparseable_record_fails_closed(self):
        p = run(stdin="{not json")
        self.assertEqual(p.returncode, 2, "a broken record is the record's violation, not the caller's")
        self.assertIn("RECORD_MALFORMED", p.stdout + p.stderr)

    def test_stdin_seam_gates_the_same_record(self):
        payload = (FIXTURES / "assembly_skill_wins.json").read_text(encoding="utf-8")
        p = run(stdin=payload)
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("AUTHORITY_INVERSION", p.stderr)

    def test_bool_and_int_requires_stay_distinct(self):
        # True and 1 are different required outcomes; a conflict check that
        # collapses them would read {True} vs {1} as intersecting.
        rec = {
            "schema": "rig.authority.assembly.v1",
            "sources": [
                {"id": "t", "authority": "task", "directives": [
                    {"id": "D", "text": "Flag must be set.", "subject": "flag", "require": True}]},
                {"id": "s", "authority": "skill", "directives": [
                    {"id": "S", "text": "Ship the integer 1.", "subject": "flag", "require": 1}]},
            ],
            "resolution": {"conflicts": [], "executed": []},
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(rec, fh)
            path = fh.name
        try:
            p = subprocess.run([sys.executable, str(CHECKER), path],
                               cwd=REPO_ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(p.returncode, 2, p.stdout)
            self.assertIn("CONFLICT_UNDETECTED", p.stderr)
        finally:
            Path(path).unlink()


if __name__ == "__main__":
    unittest.main()
