"""AfProofTests: seal determinism, per-task chains, ledger honesty, ladder."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import afproof

TAC_ABS = "/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac"


class AfProofTests(unittest.TestCase):
    """Every write goes under tmpdirs via RIG_PROOF_ROOT / RIG_LEASE_STATE_ROOT."""

    def setUp(self):
        self._home_proof = str(afproof.PROOF_DIR)
        self._home_conv = str(afproof.SENTINEL_DIR.parent.parent)
        tmp = tempfile.TemporaryDirectory(prefix="afproof-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        before = {k: os.environ.get(k)
                  for k in ("RIG_PROOF_ROOT", "RIG_LEASE_STATE_ROOT")}

        def restore():
            for k, v in before.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.addCleanup(restore)
        os.environ["RIG_PROOF_ROOT"] = str(root / "rig-proof")
        os.environ["RIG_LEASE_STATE_ROOT"] = str(root / "rig-leases")
        # Guard: nothing this test class writes may land in the real home tree.
        self.assertNotIn(str(afproof.packet_dir()), self._home_proof)
        self.assertNotIn(str(afproof.sentinel_dir()), self._home_conv)
        self.assertNotIn(str(afproof.ledger_path()), str(Path.home() / ".rig"))

    # ---- sealing --------------------------------------------------------

    def test_seal_is_deterministic(self):
        body = {"claim": "corpus scan ran", "count": 20}
        a = afproof.seal_packet("corpus", body)
        b = afproof.seal_packet("corpus", dict(body))
        self.assertEqual(a["proof_hash"], b["proof_hash"])
        self.assertEqual(len(a["proof_hash"]), 64)
        self.assertTrue((afproof.packet_dir()
                         / f"standalone__{a['proof_hash'][:16]}.json").is_file())

    def test_pre_existing_proof_hash_is_stripped_before_hashing(self):
        clean = {"a": 1}
        dirty = {"a": 1, "proof_hash": "0" * 64}
        sealed = afproof.seal_packet("x", dirty)
        self.assertEqual(sealed["proof_hash"],
                         afproof.seal_packet("x", clean)["proof_hash"])
        self.assertNotEqual(sealed["proof_hash"], "0" * 64)
        self.assertNotIn("proof_hash", sealed["payload"])

    def test_chain_links_within_task_and_not_across_tasks(self):
        p1 = afproof.seal_packet("step", {"n": 1}, task_id="t1")
        self.assertEqual(p1["previous_hash"], "genesis")
        p2 = afproof.seal_packet("step", {"n": 2}, task_id="t1")
        self.assertEqual(p2["previous_hash"], p1["proof_hash"])
        other = afproof.seal_packet("step", {"n": 1}, task_id="t2")
        self.assertEqual(other["previous_hash"], "genesis")
        p3 = afproof.seal_packet("step", {"n": 3}, task_id="t1")
        self.assertEqual(p3["previous_hash"], p2["proof_hash"])

    def test_packet_without_task_id_is_standalone_genesis(self):
        afproof.seal_packet("step", {"n": 1}, task_id="t1")
        s1 = afproof.seal_packet("note", {"a": 1})
        s2 = afproof.seal_packet("note", {"a": 2})
        self.assertEqual(s1["previous_hash"], "genesis")
        self.assertEqual(s2["previous_hash"], "genesis")
        self.assertIsNone(s1["task_id"])

    def test_verify_seal_roundtrip_then_one_byte_mutation(self):
        pkt = afproof.seal_packet("seal", {"quote": "no proof, no confidence"})
        on_disk = json.loads((afproof.packet_dir()
                              / f"standalone__{pkt['proof_hash'][:16]}.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(afproof.verify_seal(on_disk), (True, "ok"))
        on_disk["payload"]["quote"] = "no proof, no confidence."
        self.assertEqual(afproof.verify_seal(on_disk), (False, "seal_mismatch"))
        self.assertEqual(afproof.verify_seal({"payload": {}}),
                         (False, "seal_mismatch"))

    def test_verify_seal_separates_wrong_type_from_tampering(self):
        """A Path passed by mistake must not be reported as tampered evidence.

        seal_mismatch on a non-dict accuses real evidence of being forged when the
        caller simply handed over the wrong object; the two verdicts send the reader
        to different repairs.
        """
        pkt = afproof.seal_packet("wrongtype", {"a": 1}, task_id="wt")
        path = (afproof.packet_dir()
                / f"wt__{pkt['proof_hash'][:16]}.json")
        self.assertEqual(afproof.verify_seal(path), (False, "seal_unreadable"))
        self.assertEqual(afproof.verify_seal(None), (False, "seal_unreadable"))
        self.assertEqual(afproof.verify_seal("not a packet"),
                         (False, "seal_unreadable"))
        # the same file read as a dict still verifies, so nothing about the packet
        # itself changed — only the caller's mistake is being named
        self.assertEqual(afproof.verify_seal(json.loads(
            path.read_text(encoding="utf-8"))), (True, "ok"))

    # ---- sentinel -------------------------------------------------------

    def test_write_sentinel_evidence_stamps_honesty(self):
        pkt = afproof.seal_packet("task", {"done": True}, task_id="s1")
        ev = afproof.write_sentinel_evidence("s1", pkt)
        self.assertEqual(ev["sentinel_prime_status"], "SPECIFICATION_ONLY")
        self.assertEqual(ev["gauntlet_phases_executed"], [])
        self.assertEqual(ev["termination_authority"], "UNIMPLEMENTED")
        self.assertTrue(ev["seal_verified"])
        f = afproof.sentinel_dir() / f"s1__{pkt['proof_hash'][:16]}.json"
        self.assertTrue(f.is_file())
        disk = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(disk["sentinel_prime_status"], "SPECIFICATION_ONLY")
        self.assertEqual(disk["gauntlet_phases_executed"], [])
        self.assertEqual(disk["termination_authority"], "UNIMPLEMENTED")

    # ---- fabrication ledger ----------------------------------------------

    def test_log_fabrication_appends_exactly_one_line_per_call(self):
        afproof.log_fabrication("grok", "FABRICATED", "t1", "phantom stdout")
        afproof.log_fabrication("grok", "ISOLATION_BREACH", "t2")
        lines = afproof.ledger_path().read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        rec = json.loads(lines[0])
        for key in ("ts", "epoch", "event", "pattern", "verdict", "session",
                    "agent_id", "detail"):
            self.assertIn(key, rec)
        self.assertEqual(rec["verdict"], "FABRICATED")
        self.assertEqual(rec["session"], "t1")

    def test_log_fabrication_raises_on_unwritable_ledger(self):
        blocker = Path(os.environ["RIG_LEASE_STATE_ROOT"])
        os.environ["RIG_LEASE_STATE_ROOT"] = str(blocker) + "-blocked"
        Path(os.environ["RIG_LEASE_STATE_ROOT"]).write_text("not a dir",
                                                            encoding="utf-8")
        with self.assertRaises(RuntimeError) as cm:
            afproof.log_fabrication("grok", "FABRICATED", "t9")
        self.assertIn("fabrication_ledger_write_failed", str(cm.exception))

    def test_fabrication_rates_absent_ledger_is_zeroed_not_fabricated(self):
        rep = afproof.fabrication_rates()
        self.assertFalse(rep["ledger_present"])
        self.assertEqual(rep["total"], 0)
        self.assertEqual(rep["by_verdict"], {})
        self.assertIsNone(rep["fabrication_rate"])
        self.assertIn("ledger_absent", rep["note"])

    def test_fabrication_rates_populated(self):
        afproof.log_fabrication("grok", "FABRICATED", "t1")
        afproof.log_fabrication("grok", "FABRICATED", "t2")
        afproof.log_fabrication("fable", "ISOLATION_BREACH", "t3")
        rep = afproof.fabrication_rates(since_days=30)
        self.assertTrue(rep["ledger_present"])
        self.assertEqual(rep["total"], 3)
        self.assertEqual(rep["fabricated"], 2)
        self.assertEqual(rep["by_verdict"]["FABRICATED"], 2)
        self.assertEqual(rep["by_agent"], {"grok": 2, "fable": 1})
        self.assertAlmostEqual(rep["fabrication_rate"], 2 / 3)

    # ---- verdict ladder ----------------------------------------------------

    def test_verdict_ladder_rung_one_tac_never_emits_pass(self):
        ladder = afproof.verdict_ladder()
        self.assertEqual(len(ladder["rungs"]), 3)
        rung1 = ladder["rungs"][0]
        self.assertIn(TAC_ABS, rung1["command"])
        self.assertEqual(sorted(rung1["emits"]), ["GREEN", "RED"])
        self.assertNotIn("PASS", rung1["emits"])
        self.assertIn("PASS", rung1["never_emits"])

    def test_verdict_ladder_pass_and_sentinel_rungs(self):
        ladder = afproof.verdict_ladder()
        rung2, rung3 = ladder["rungs"][1], ladder["rungs"][2]
        self.assertIn("dispatcher", rung2["callable"])
        self.assertIn("PASS", rung2["emits"])
        self.assertNotIn("PASS", rung3["emits"])
        self.assertIn("BLOCKED_PENDING_SENTINEL", rung3["emits"])
        self.assertEqual(rung3["status"], "SPECIFICATION_ONLY")
        self.assertEqual(rung3["termination_authority"], "UNIMPLEMENTED")
        self.assertTrue(any("never PASS" in inv or "never emits PASS" in inv
                            for inv in ladder["invariants"]))

    def test_real_home_tree_untouched_by_writes(self):
        home_rig = (Path.home() / ".rig").resolve()
        real_ledger = home_rig / "leases" / afproof.LEDGER.name
        # Snapshot first: the real ledger legitimately holds entries once the
        # pipeline catches a fabricated citation, and doctrine says that append must
        # never be dropped. Asserting the file does not exist would fail every run
        # from the first honest log onward. The isolation property is that THIS test
        # adds nothing to it.
        before = real_ledger.stat().st_size if real_ledger.exists() else None
        pkt = afproof.seal_packet("probe", {"x": 1}, task_id="probe-task")
        afproof.log_fabrication("probe", "FABRICATED", "probe-task")
        afproof.write_sentinel_evidence("probe-task", pkt)
        packet_file = (afproof.packet_dir()
                       / f"probe-task__{pkt['proof_hash'][:16]}.json")
        self.assertTrue(packet_file.is_file())
        for p in (packet_file.resolve(), afproof.ledger_path().resolve(),
                  afproof.sentinel_dir().resolve()):
            self.assertNotIn(home_rig, p.parents)
        self.assertFalse((Path(self._home_proof) / afproof.PACKET_SUBDIR
                          / packet_file.name).exists())
        after = real_ledger.stat().st_size if real_ledger.exists() else None
        self.assertEqual(before, after,
                         "probe write leaked into the real ~/.rig fabrication ledger")
        # and the probe landed where the override pointed, so the equality above is
        # not vacuous through a silently shared path
        self.assertIn("probe-task", afproof.ledger_path().read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
