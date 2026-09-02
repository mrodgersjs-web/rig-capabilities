"""Wiring the same MCP server into four harness dialects, without ever guessing.

Fixtures are small synthetic configs shaped exactly like the live ones (verified
against ~/.cursor/mcp.json, ~/.gemini/settings.json,
~/.config/opencode/opencode.json and ~/.config/goose/config.yaml on 2026-09-02).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rig_capabilities import mcp_wire as W  # noqa: E402

CURSOR = """{
  "mcpServers": {
    "codegraph": {
      "args": ["serve", "--mcp"],
      "command": "codegraph",
      "type": "stdio"
    }
  }
}
"""
CURSOR_EMPTY = '{\n  "mcpServers": {}\n}\n'
GEMINI = """{
  "mcpServers": {
    "pencil": {
      "command": "/Applications/pencil/mcp-server",
      "args": ["--stdio"]
    }
  },
  "selectedModel": "gemini-pro"
}
"""
OPENCODE = """{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "stripe": {
      "command": ["/Users/rig128gb/.rig/bin/stripe-mcp"],
      "enabled": false,
      "type": "local"
    }
  },
  "model": "rig-blackwell"
}
"""
GOOSE = """extensions:
  developer:
    bundled: true
    enabled: true
    name: developer
    timeout: 300
    type: builtin
  tutorial:
    enabled: true
    name: tutorial
    type: builtin
"""


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["RIG_MCP_WIRE_TARGETS"] = str(self.root)
        os.environ["RIG_PROOF_ROOT"] = str(self.root / "proof")

    def tearDown(self):
        os.environ.pop("RIG_MCP_WIRE_TARGETS", None)
        os.environ.pop("RIG_PROOF_ROOT", None)
        self.tmp.cleanup()

    def seed(self, name: str, text: str) -> Path:
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    # ---- dialect correctness -------------------------------------------
    def test_cursor_entry_is_valid_json_and_separable(self):
        after, acts = W.project("cursor", CURSOR)
        self.assertEqual(acts[0]["action"], "wire")
        self.assertTrue(acts[0]["trailing_comma"],
                        "a comma is mandatory after a first child in a non-empty object")
        doc = json.loads(after)                      # raises if the comma is wrong
        self.assertIn("rig-capabilities", doc["mcpServers"])
        self.assertIn("codegraph", doc["mcpServers"], "existing servers survive")
        self.assertEqual(doc["mcpServers"]["rig-capabilities"]["command"], W.PYTHON)
        self.assertEqual(doc["mcpServers"]["rig-capabilities"]["args"], [str(W.SERVER)])

    def test_empty_inline_container_gets_no_trailing_comma(self):
        after, acts = W.project("cursor", CURSOR_EMPTY)
        self.assertFalse(acts[0]["trailing_comma"],
                         "an inline {} has no sibling to separate; a comma is invalid JSON")
        doc = json.loads(after)
        self.assertIn("rig-capabilities", doc["mcpServers"])

    def test_gemini_keeps_its_own_key_order_and_other_keys(self):
        after, _ = W.project("gemini", GEMINI)
        doc = json.loads(after)
        self.assertEqual(doc["selectedModel"], "gemini-pro")
        entry = doc["mcpServers"]["rig-capabilities"]
        self.assertEqual(list(entry), ["command", "args"])
        self.assertIn("pencil", doc["mcpServers"])

    def test_opencode_wants_an_array_command_and_local_type(self):
        after, _ = W.project("opencode", OPENCODE)
        doc = json.loads(after)
        entry = doc["mcp"]["rig-capabilities"]
        self.assertEqual(entry["type"], "local")
        self.assertIs(entry["enabled"], True)
        self.assertEqual(entry["command"], [W.PYTHON, str(W.SERVER)],
                         "opencode takes command as an argv array, not command+args")
        self.assertEqual(doc["model"], "rig-blackwell")

    def test_goose_block_matches_the_documented_stdio_shape(self):
        after, acts = W.project("goose", GOOSE)
        self.assertEqual(acts[0]["action"], "wire")
        lines = after.splitlines()
        i = next(n for n, ln in enumerate(lines) if ln.startswith("  rig-capabilities:"))
        block = "\n".join(lines[i:i + 9])
        for needle in ("type: stdio", "name: rig-capabilities", "enabled: true",
                       f"cmd: {W.PYTHON}", f'args: ["{W.SERVER}"]', "timeout: 300"):
            self.assertIn(needle, block)
        self.assertIn("  developer:", after, "existing extensions untouched")
        self.assertTrue(W.has_entry("goose", after))

    # ---- idempotence / refusal ------------------------------------------
    def test_second_projection_is_already_wired(self):
        once, a1 = W.project("cursor", CURSOR)
        twice, a2 = W.project("cursor", once)
        self.assertEqual(a1[0]["action"], "wire")
        self.assertEqual(a2[0]["action"], "already_wired")
        self.assertEqual(once, twice, "running the wiring twice must be a no-op")
        for target, text in (("gemini", GEMINI), ("opencode", OPENCODE), ("goose", GOOSE)):
            one, _ = W.project(target, text)
            self.assertEqual(W.project(target, one)[1][0]["action"], "already_wired",
                             f"{target} is not idempotent")

    def test_missing_container_is_reported_not_guessed(self):
        text = '{\n  "workspaces": {}\n}\n'
        after, acts = W.project("cursor", text)
        self.assertEqual(after, text, "no container means no write, not an invented one")
        self.assertEqual(acts[0]["action"], "container_missing")

    def test_unknown_target_raises(self):
        with self.assertRaises(W.WireGateError):
            W.project("cursor-mobile", CURSOR)

    def test_corrupt_config_is_never_written(self):
        broken = '{\n  "mcpServers": {\n    "x": { "command": "y" }\n}\n'  # unclosed root
        self.seed("cursor", broken)
        row = next(r for r in W.plan()["targets"] if r["target"] == "cursor")
        self.assertEqual(row["state"], "invalid_json_refused")
        self.assertFalse(row["changes"], "an unparseable config must not be rewritten")


class GateDTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "targets").mkdir()
        (self.root / "proof").mkdir()
        os.environ["RIG_MCP_WIRE_TARGETS"] = str(self.root / "targets")
        os.environ["RIG_PROOF_ROOT"] = str(self.root / "proof")
        for name, text in (("cursor", CURSOR), ("gemini", GEMINI),
                           ("opencode", OPENCODE), ("goose", GOOSE)):
            (self.root / "targets" / name).write_text(text, encoding="utf-8")
    def tearDown(self):
        os.environ.pop("RIG_MCP_WIRE_TARGETS", None)
        os.environ.pop("RIG_PROOF_ROOT", None)
        self.tmp.cleanup()

    def approve(self, run_id="mw-1", action=W.GATE_D_ACTION, targets=None):
        rec = {"schema": "rig.gate-d-approval.v1", "status": "APPROVED",
               "action": action,
               "targets": ["cursor", "gemini", "opencode", "goose"]
               if targets is None else targets}
        (self.root / "proof" / f"gate-d-{run_id}.json").write_text(
            json.dumps(rec), encoding="utf-8")
        return run_id

    def test_apply_without_approval_writes_nothing(self):
        # Pristine fixtures are all *pending* (a write would change them), so the
        # isolation claim is byte identity on disk, not "the plan wanted nothing".
        was = {name: (self.root / "targets" / name).read_text(encoding="utf-8")
               for name in ("cursor", "gemini", "opencode", "goose")}
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply("")
        self.assertIn("gate_d_required", str(ctx.exception))
        now = {name: (self.root / "targets" / name).read_text(encoding="utf-8")
               for name in was}
        self.assertEqual(now, was,
                         "a refused apply must leave every config byte-identical")
        with self.assertRaises(W.WireGateError) as ctx2:
            W.apply("never-issued")
        self.assertIn("gate_d_missing", str(ctx2.exception))
        self.assertEqual({name: (self.root / "targets" / name)
                          .read_text(encoding="utf-8") for name in was}, was)

    def test_wrong_action_is_refused(self):
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply(self.approve(run_id="mw-bad", action="something-else"))
        self.assertIn("gate_d_action_mismatch", str(ctx.exception))

    def _raw_approval(self, run_id, body):
        (self.root / "proof" / f"gate-d-{run_id}.json").write_text(body, encoding="utf-8")
        return run_id

    def test_approval_file_that_is_not_approved_is_refused(self):
        """A Gate-D record that exists but says PENDING/DENIED is not a pass.

        Without this case, deleting the status check would keep the suite green:
        every other refusal in this file fires before the record is even opened.
        """
        was = (self.root / "targets" / "cursor").read_text(encoding="utf-8")
        for status in ("PENDING", "DENIED", ""):
            rid = self._raw_approval(
                "mw-pending", json.dumps({"status": status,
                                          "action": W.GATE_D_ACTION,
                                          "targets": ["cursor", "gemini",
                                                      "opencode", "goose"]}))
            with self.assertRaises(W.WireGateError) as ctx:
                W.apply(rid)
            self.assertIn("gate_d_not_approved", str(ctx.exception), status)
        self.assertEqual((self.root / "targets" / "cursor")
                         .read_text(encoding="utf-8"), was)

    def test_unreadable_approval_is_refused_not_treated_as_absent(self):
        rid = self._raw_approval("mw-junk", "{not json")
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply(rid)
        self.assertIn("gate_d_unreadable", str(ctx.exception))

    def test_wrong_run_id_is_not_a_blanket_approval(self):
        self.approve(run_id="mw-other")
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply("mw-1")          # approved under a different id
        self.assertIn("gate_d_missing", str(ctx.exception))

    def test_approval_does_not_extend_to_unnamed_targets(self):
        """The scope of a config-write approval is its target list, not its existence."""
        rid = self.approve(run_id="mw-part", targets=["cursor"])
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply(rid, ["cursor", "goose"])
        self.assertIn("gate_d_target_not_approved:goose", str(ctx.exception))
        self.assertFalse(W.has_entry("goose",
                                     (self.root / "targets" / "goose")
                                     .read_text(encoding="utf-8")))
        # Refusal is atomic: an approval that covers cursor does not buy a partial
        # write of cursor while goose is still unauthorised. Nothing moved.
        self.assertFalse(W.has_entry("cursor",
                                     (self.root / "targets" / "cursor")
                                     .read_text(encoding="utf-8")),
                        "an over-scoped request must write nothing at all")
        res = W.apply(rid, ["cursor"])      # same approval, honest scope
        self.assertEqual([r["target"] for r in res["written"]], ["cursor"])
        self.assertTrue(W.has_entry("cursor",
                                    (self.root / "targets" / "cursor")
                                    .read_text(encoding="utf-8")))
        self.assertFalse(W.has_entry("goose",
                                     (self.root / "targets" / "goose")
                                     .read_text(encoding="utf-8")))

    def test_apply_writes_all_four_then_is_idempotent(self):
        res = W.apply(self.approve(run_id="mw-ok"))
        self.assertEqual(len(res["written"]), 4)
        self.assertTrue(res["all_wired"])
        for row in res["written"]:
            self.assertEqual(row["state_after"], "already_wired")
            self.assertTrue(Path(row["backup"]).is_file(),
                            "every config write keeps a pre-write copy")
            text = Path(row["path"]).read_text(encoding="utf-8")
            self.assertTrue(W.has_entry(row["target"], text))
            if W.DIALECT[row["target"]] != "yaml":
                json.loads(text)
        again = W.apply(self.approve(run_id="mw-ok"))
        self.assertEqual(again["written"], [], "second apply has nothing to write")
        self.assertTrue(again.get("all_wired"),
                        "an already-wired fleet is the healthy steady state and must "
                        "report all_wired so the caller exits 0, not a permanent red")
        self.assertTrue(W.verify()["idempotent"])

    def test_steady_state_is_not_reported_when_a_target_is_blocked(self):
        """all_wired=true must be earned, not defaulted: a target whose config cannot
        be parsed stays visible as blocked, so the steady-state claim is false."""
        W.apply(self.approve(run_id="mw-part2"))
        (self.root / "targets" / "goose").write_text("not: [yaml\n", encoding="utf-8")
        res = W.apply(self.approve(run_id="mw-part2"))
        self.assertEqual(res["written"], [])
        self.assertFalse(res.get("all_wired", True))
        self.assertIn("goose", res["skipped"])

    def test_apply_refuses_a_target_the_plan_cannot_change(self):
        rid = self.approve(run_id="mw-noop")
        W.apply(rid)
        with self.assertRaises(W.WireGateError) as ctx:
            W.apply(rid, ["cursor"])          # already wired -> not writable
        self.assertIn("not_writable:cursor", str(ctx.exception))


class RealConfigTests(unittest.TestCase):
    """Read-only against the live machine: the parsers must survive real files."""

    def setUp(self):
        self._saved = os.environ.pop("RIG_MCP_WIRE_TARGETS", None)

    def tearDown(self):
        if self._saved is not None:
            os.environ["RIG_MCP_WIRE_TARGETS"] = self._saved

    def test_plan_reads_real_configs_without_writing(self):
        before = {str(path): path.stat().st_mtime_ns
                  for _, path in W.targets() if path.is_file()}
        plan = W.plan()
        self.assertEqual([r["target"] for r in plan["targets"]],
                         ["cursor", "gemini", "opencode", "goose"])
        legal = {"wire", "already_wired", "container_missing", "invalid_json_refused",
                 "missing_file", "cannot_read"}
        for r in plan["targets"]:
            self.assertIn(r["state"], legal, r)
        for _, path in W.targets():
            if str(path) in before:
                self.assertEqual(path.stat().st_mtime_ns, before[str(path)],
                                 f"plan() must not touch {path}")

    def test_launch_spec_matches_a_server_that_already_works(self):
        """What we propose must be what the working harnesses already run."""
        omp = Path.home() / ".omp" / "agent" / "mcp.json"
        if not omp.is_file():
            self.skipTest("no omp config on this machine")
        srv = (json.loads(omp.read_text(encoding="utf-8"))
               .get("mcpServers") or {}).get(W.ENTRY_NAME)
        if not srv:
            self.skipTest("rig-capabilities not wired in omp")
        self.assertEqual(srv.get("command"), W.PYTHON)
        self.assertEqual(srv.get("args"), [str(W.SERVER)])


class ShapePinTests(unittest.TestCase):
    def test_entry_bodies_are_pinned(self):
        """These bodies will be edited; the dialects are what makes them loadable."""
        cur = "\n".join(W.entry_json("cursor", 4))
        self.assertIn('    "rig-capabilities": {', cur)
        self.assertIn('"command":', cur)
        self.assertNotIn('"type"', cur, "the cursor entry stays minimal")
        oc = "\n".join(W.entry_json("opencode", 4))
        self.assertIn('"type": "local"', oc)
        self.assertIn('"enabled": true', oc)
        gy = "\n".join(W.entry_yaml(4))
        self.assertIn("  cmd: ", gy)
        self.assertIn("env_keys: []", gy)

    def test_module_compiles(self):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(Path(W.__file__))],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
