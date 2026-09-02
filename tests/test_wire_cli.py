"""CLI-surface tests for `rig-capabilities wire-mcp`.

These drive bin/rig-capabilities as a subprocess — the byte-for-byte contract a
coding agent actually gets — with RIG_MCP_WIRE_TARGETS + RIG_PROOF_ROOT pointed
into a tmpdir so nothing near a real harness config is touched. The load-bearing
claims: dormant by default (zero writes on plan and on every refusal path), the
Gate-D file is really consulted, and an approved apply writes all four targets
and is then idempotent.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
CLI = ROOT / "bin" / "rig-capabilities"

from test_mcp_wire import CURSOR, GEMINI, OPENCODE, GOOSE  # noqa: E402
from rig_capabilities import mcp_wire as W  # noqa: E402

NAMES = ("cursor", "gemini", "opencode", "goose")
SEEDED = {"cursor": CURSOR, "gemini": GEMINI, "opencode": OPENCODE, "goose": GOOSE}


class WireCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "targets").mkdir()
        (self.root / "proof").mkdir()
        for name, text in SEEDED.items():
            (self.root / "targets" / name).write_text(text, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        env = dict(os.environ)
        env["RIG_MCP_WIRE_TARGETS"] = str(self.root / "targets")
        env["RIG_PROOF_ROOT"] = str(self.root / "proof")
        proc = subprocess.run([sys.executable, str(CLI), *argv],
                              capture_output=True, text=True, env=env, timeout=60)
        return proc.returncode, proc.stdout, proc.stderr

    def disk(self):
        return {name: (self.root / "targets" / name).read_text(encoding="utf-8")
                for name in NAMES}

    def stamps(self):
        return {(name, (self.root / "targets" / name).stat().st_mtime_ns)
                for name in NAMES}

    def approve(self, run_id="mw-cli-1"):
        rec = {"schema": "rig.gate-d-approval.v1", "status": "APPROVED",
               "action": W.GATE_D_ACTION, "targets": list(NAMES)}
        (self.root / "proof" / f"gate-d-{run_id}.json").write_text(
            json.dumps(rec), encoding="utf-8")
        return run_id

    def test_plan_writes_nothing(self):
        was, was_stamps = self.disk(), self.stamps()
        rc, out, err = self.run_cli("wire-mcp")
        self.assertEqual(rc, 0, err)
        plan = json.loads(out)
        self.assertEqual(plan["schema"], "rig.mcp-wire-plan.v1")
        self.assertEqual(sorted(t["target"] for t in plan["targets"]), sorted(NAMES))
        self.assertEqual(len(plan["targets"]), 4)
        # pristine fixtures are all pending, so "wrote nothing" is byte identity,
        # not "the plan wanted nothing".
        self.assertEqual(self.disk(), was)
        self.assertEqual(self.stamps(), was_stamps)

    def test_apply_without_token_exits_two(self):
        was, was_stamps = self.disk(), self.stamps()
        rc, out, err = self.run_cli("wire-mcp", "--apply")
        self.assertEqual(rc, 2, err)
        body = json.loads(out)
        self.assertFalse(body["ok"])
        self.assertEqual(body["reason"], "gate_d_required")
        self.assertIn("hint", body)
        self.assertEqual(self.disk(), was)
        self.assertEqual(self.stamps(), was_stamps)

    def test_apply_with_unapproved_token_exits_two(self):
        # The named run has no file under RIG_PROOF_ROOT: the refusal must name
        # the missing gate-d file, which proves the file is really consulted.
        was, was_stamps = self.disk(), self.stamps()
        rc, out, err = self.run_cli("wire-mcp", "--apply", "--gate-d", "nope")
        self.assertEqual(rc, 2, err)
        body = json.loads(out)
        self.assertFalse(body["ok"])
        self.assertIn("gate_d_missing", body["reason"])
        self.assertIn("gate-d-nope.json", body["reason"])
        self.assertEqual(self.disk(), was)
        self.assertEqual(self.stamps(), was_stamps)

    def test_apply_with_approved_token_writes_all_four_and_is_idempotent(self):
        run_id = self.approve()
        # the literal approval phrase must resolve to the same run_id
        rc, out, err = self.run_cli("wire-mcp", "--apply",
                                    "--gate-d", f"APPROVE {run_id}")
        self.assertEqual(rc, 0, err)
        res = json.loads(out)
        self.assertEqual(res["schema"], "rig.mcp-wire-apply.v1")
        self.assertEqual(sorted(w["target"] for w in res["written"]), sorted(NAMES))
        self.assertTrue(res["all_wired"])
        for name in NAMES:
            self.assertTrue(W.has_entry(name, self.disk()[name]), name)
        # idempotent: verify reports nothing left to write, and a second plan
        # finds every target already wired.
        rc, out, err = self.run_cli("wire-mcp", "verify")
        self.assertEqual(rc, 0, err)
        self.assertTrue(json.loads(out)["idempotent"])
        rc, out, err = self.run_cli("wire-mcp")
        self.assertEqual(rc, 0, err)
        self.assertEqual(json.loads(out)["writable"], [])

    def test_two_token_approve_spelling_is_not_a_usage_error(self):
        # The hint once told operators to re-run `--gate-d APPROVE <run_id>`.
        # That spelling arrives as three argv tokens; it must reach Gate-D and
        # come back as a JSON refusal, never an argparse "invalid choice"
        # usage error on the subcommand positional.
        was, was_stamps = self.disk(), self.stamps()
        rc, out, err = self.run_cli("wire-mcp", "--apply",
                                    "--gate-d", "APPROVE", "nope")
        self.assertNotIn("usage:", err)
        self.assertEqual(rc, 2, err)
        body = json.loads(out)  # a usage error prints no JSON at all
        self.assertIn("gate_d_missing", body["reason"])
        self.assertIn("gate-d-nope.json", body["reason"],
                      "the phrase must resolve to the bare run id, not 'APPROVE nope'")
        self.assertEqual(self.disk(), was)
        self.assertEqual(self.stamps(), was_stamps)


if __name__ == "__main__":
    unittest.main()
