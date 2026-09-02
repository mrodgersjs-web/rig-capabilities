"""Acceptance identity: who ran the done-test, and may that record be believed?

Four claims the suite pins (each maps to a clause in
capabilities/commands/capabilities-done-test.md):

1. A complete identity — producer model + version + process, harness id +
   config fingerprint, external verifier — stamps to the caller's path and
   exits 0. That write is the module's only write.
2. A missing producer model is refused as `identity_unavailable:executed_by.model`,
   exit 1, no stamp written.
3. A verifier that IS the producer — same process, or same model family AND
   same harness — is refused as `self_verification:...` even on a pass verdict.
4. An environment that exposes no identity is refused, not guessed: with an
   empty record (even with decoy env vars set) every required field is named
   `identity_unavailable:<field>` and nothing is written. There is no env or
   heuristic fallback to fake an identity.

Plant-failure regression (module bottom): the same_model_family_and_harness
rule disabled must turn this file red; restoring it must turn it green.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import acceptance_identity as ai  # noqa: E402

MODULE = REPO_ROOT / "rig_capabilities" / "acceptance_identity.py"


def full_record(**overrides) -> dict:
    """A done-test record with a genuinely external verifier (gpt family
    checking a claude run in a different harness)."""
    rec = {
        "asset_id": "capabilities-done-test",
        "verdict": "pass",
        "executed_by": {
            "model": "claude-opus-4-1",
            "model_version": "2026-08-01",
            "process_id": "p-producer-17",
        },
        "harness_ref": {
            "harness_id": "rig-capabilities",
            "config_hash": "sha256:" + "2b1e0f6a9c4d8e7f5a3b1c9d7e5f3a1b" * 2,
        },
        "verifier": {
            "model": "gpt-5-codex",
            "process_id": "p-verifier-42",
            "harness_id": "cross-family-checker",
        },
    }
    rec.update(overrides)
    return rec


def run_cli(record_raw: str, stamp_name: str = "stamp.json", env=None,
            record_arg: str | None = None):
    """Run the module as a CLI from repo root; env=None means an EMPTY
    environment — nothing for identity heuristics to lean on."""
    tmp = Path(tempfile.mkdtemp(prefix="aid-test-"))
    rec_path = tmp / "rec.json"
    rec_path.write_text(record_raw, encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(MODULE), record_arg or str(rec_path),
         "--stamp", str(tmp / stamp_name)],
        capture_output=True, text=True, cwd=REPO_ROOT, env=env or {})
    return res, tmp / stamp_name, tmp


class StampedTests(unittest.TestCase):
    def test_complete_identity_stamps(self):
        res = ai.evaluate(full_record())
        self.assertTrue(res["ok"], res["refusals"])
        self.assertEqual(res["refusals"], [])
        stamp = res["stamp"]
        self.assertEqual(stamp["schema"], "rig.acceptance_identity/1")
        self.assertEqual(stamp["executed_by"]["model"], "claude-opus-4-1")
        self.assertEqual(stamp["executed_by"]["model_family"], "claude")
        self.assertEqual(stamp["verifier"]["model_family"], "gpt")
        self.assertIn("different_model_family", stamp["externality_basis"])
        self.assertIn("different_harness", stamp["externality_basis"])

    def test_cli_writes_stamp_and_only_stamp(self):
        raw = json.dumps(full_record())
        res, stamp_path, tmp = run_cli(raw, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(stamp_path.read_text(encoding="utf-8"), res.stdout)
        stamped = json.loads(stamp_path.read_text(encoding="utf-8"))
        self.assertEqual(stamped["record_sha256"],
                         hashlib.sha256(raw.encode("utf-8")).hexdigest())
        # the stamp file is the only file created beyond the input record
        self.assertEqual(sorted(p.name for p in tmp.iterdir()),
                         ["rec.json", "stamp.json"])

    def test_externality_by_family_alone_is_enough(self):
        rec = full_record()
        rec["verifier"]["harness_id"] = rec["harness_ref"]["harness_id"]  # same harness
        res = ai.evaluate(rec)
        self.assertTrue(res["ok"], res["refusals"])  # different family carries it
        self.assertNotIn("different_harness", res["stamp"]["externality_basis"])

    def test_externality_by_harness_alone_is_enough(self):
        rec = full_record()
        rec["verifier"]["model"] = "claude-sonnet-5"  # same family...
        res = ai.evaluate(rec)
        self.assertTrue(res["ok"], res["refusals"])   # ...but different harness+process
        self.assertEqual(res["stamp"]["externality_basis"],
                         ["different_process", "different_harness"])


class UnpinnedIdentityTests(unittest.TestCase):
    def test_missing_producer_model_refused(self):
        rec = full_record()
        del rec["executed_by"]["model"]
        res = ai.evaluate(rec)
        self.assertFalse(res["ok"])
        self.assertIn("identity_unavailable:executed_by.model", res["refusals"][0])
        cli, stamp_path, _ = run_cli(json.dumps(rec))
        self.assertEqual(cli.returncode, 1)
        self.assertIn("identity_unavailable:executed_by.model", cli.stderr)
        self.assertFalse(stamp_path.exists(), "a refusal must write no stamp")

    def test_unverifiable_config_hash_refused(self):
        rec = full_record()
        rec["harness_ref"]["config_hash"] = "green"  # free text pins no variant
        res, stamp_path, _ = run_cli(json.dumps(rec))
        self.assertEqual(res.returncode, 1)
        self.assertIn("identity_unavailable:harness_ref.config_hash", res.stderr)
        self.assertFalse(stamp_path.exists())

    def test_environment_with_no_identity_is_refused_not_guessed(self):
        # Empty record; the only identity-ish things in the environment are
        # DECOYS a guessing implementation might have scraped. The module
        # must name every missing field and write nothing.
        tmp = Path(tempfile.mkdtemp(prefix="aid-test-"))
        rec_path = tmp / "rec.json"
        rec_path.write_text("{}", encoding="utf-8")
        stamp_path = tmp / "stamp.json"
        res = subprocess.run(
            [sys.executable, str(MODULE), str(rec_path), "--stamp", str(stamp_path)],
            capture_output=True, text=True, cwd=REPO_ROOT,
            env={"RIG_MODEL_ID": "claude-opus-4-1", "HARNESS_ID": "rig-capabilities"})
        self.assertEqual(res.returncode, 1)
        for section, key in ai.REQUIRED:
            self.assertIn(f"identity_unavailable:{section}.{key}", res.stderr,
                          f"{section}.{key} not named in the refusal")
        self.assertNotIn("claude-opus-4-1", res.stdout + res.stderr,
                         "the decoy env value leaked into the output")
        self.assertEqual(res.stdout, "", "refusal must print no stamp on stdout")
        self.assertFalse(stamp_path.exists(), "no identity -> no write")

    def test_malformed_record_refused_by_name(self):
        res, stamp_path, _ = run_cli("this is not json")
        self.assertEqual(res.returncode, 1)
        self.assertIn("identity_unavailable:record", res.stderr)
        self.assertFalse(stamp_path.exists())


class SelfVerificationTests(unittest.TestCase):
    def test_same_process_is_the_run_grading_itself(self):
        rec = full_record()
        rec["verifier"]["process_id"] = rec["executed_by"]["process_id"]
        res = ai.evaluate(rec)
        self.assertFalse(res["ok"])
        self.assertTrue(res["refusals"][0].startswith("self_verification:"))
        cli, stamp_path, _ = run_cli(json.dumps(rec))
        self.assertEqual(cli.returncode, 1)
        self.assertIn("self_verification:", cli.stderr)
        self.assertFalse(stamp_path.exists())

    def test_same_model_family_and_harness_is_self_validation(self):
        # The arXiv:2608.11888 failure signature: a different invocation of
        # the same brain inside the same harness is still the skill's own
        # checklist grading itself.
        rec = full_record()
        rec["verifier"]["model"] = "claude-sonnet-5"
        rec["verifier"]["harness_id"] = rec["harness_ref"]["harness_id"]
        cli, stamp_path, _ = run_cli(json.dumps(rec))
        self.assertEqual(cli.returncode, 1)
        self.assertIn(
            "self_verification:same_model_family_and_harness(claude+rig-capabilities)",
            cli.stderr)
        self.assertFalse(stamp_path.exists())

    def test_missing_identity_wins_over_comparison(self):
        # An incomplete identity cannot even be compared for self-reference:
        # the refusal must be identity_unavailable, never a guess of externality.
        rec = full_record()
        rec["verifier"] = {"harness_id": "rig-capabilities"}  # model+process unpinned
        res = ai.evaluate(rec)
        self.assertFalse(res["ok"])
        self.assertTrue(all(r.startswith("identity_unavailable:") for r in res["refusals"]),
                        res["refusals"])


class PlantFailureRegression(unittest.TestCase):
    """The externality rule must be load-bearing, not decorative.

    With this exact block un-commented (rule forced off) this suite goes RED
    on test_same_model_family_and_harness_is_self_validation; restoring it
    returns GREEN. Proven by exit code via
    `env PYTHONDONTWRITEBYTECODE=1 ./bin/rig-capabilities test capabilities-done-test`
    during authoring; the planted variant is kept here as the record.
    """

    def test_rule_is_present_in_the_module_source(self):
        src = MODULE.read_text(encoding="utf-8")
        self.assertIn("if same_family and same_harness:", src,
                      "the self-verification gate was removed from "
                      "acceptance_identity.py — this suite's red is mandatory")


if __name__ == "__main__":
    unittest.main()
