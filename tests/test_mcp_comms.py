"""Communications OS riding the capability MCP server.

Pinned contract: the comms loop is reachable through MCP tools, resources and
prompts — and the private lane is a lock that fires BEFORE any drafting or
scoring, not a filter after. These handlers are the same ones a harness calls
over stdio; driving them directly is the shortest check that fails if the
wiring or the lock breaks.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import server  # noqa: E402
from rig_capabilities.mcp_stdio import ToolError  # noqa: E402

COMMS_TOOLS = ("capabilities_comms_surfaces", "capabilities_comms_route",
               "capabilities_comms_packet", "capabilities_comms_score",
               "capabilities_comms_voice_check",
               "capabilities_comms_ledger_report", "capabilities_comms_doctor")

WEAK = ("Unlock the potential of your practice. Empower your team to delve "
        "into seamless AI. Learn more and get started today.")


class CommsToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = server.build_server()

    def test_every_comms_tool_has_a_handler(self):
        names = {t["name"] for t in server.TOOLS}
        for t in COMMS_TOOLS:
            self.assertIn(t, names)
            self.assertIn(t, self.srv.handlers)

    def test_route_ranks_the_email_surface_for_an_email_intent(self):
        out = self.srv.handlers["capabilities_comms_route"](
            {"intent": "write a cold email to a dental practice owner"})
        self.assertTrue(out["route"], "route must not come back empty")

    def test_weak_artifact_does_not_clear_can_ship(self):
        out = self.srv.handlers["capabilities_comms_score"](
            {"surface": "emails", "artifact": WEAK})
        self.assertFalse(out["can_ship"])
        self.assertTrue(out["blocks"])
        self.assertEqual(out["exit"], 2)

    def test_unknown_surface_is_named_not_mocked(self):
        with self.assertRaises(ToolError) as cm:
            self.srv.handlers["capabilities_comms_score"](
                {"surface": "tiktok", "artifact": "x"})
        self.assertIn("unknown surface", str(cm.exception))

    def test_doctor_reports_against_canonical_hashes(self):
        out = self.srv.handlers["capabilities_comms_doctor"]({})
        self.assertIn("drift", out)
        self.assertIn("exit", out)


class PrivacyLockTests(unittest.TestCase):
    """Private lane: lock first, content never."""

    @classmethod
    def setUpClass(cls):
        cls.srv = server.build_server()

    def test_machine_scoring_private_is_refused(self):
        with self.assertRaises(ToolError) as cm:
            self.srv.handlers["capabilities_comms_score"](
                {"surface": "love-notes", "artifact": "any text at all"})
        self.assertIn("PRIVACY_LOCK", str(cm.exception))

    def test_private_draft_requires_human(self):
        with self.assertRaises(ToolError) as cm:
            self.srv.handlers["capabilities_comms_packet"](
                {"surface": "love-notes", "brief": "something"})
        self.assertIn("PRIVACY_LOCK", str(cm.exception))

    def test_write_prompt_private_is_refused(self):
        with self.assertRaises(ToolError) as cm:
            self.srv.get_prompt("write", {"surface": "love-notes", "brief": "x"})
        self.assertIn("PRIVACY_LOCK", str(cm.exception))

    def test_no_private_uri_and_no_traversal(self):
        for r in self.srv.resources:
            self.assertNotIn("james", r["uri"].lower())
        with self.assertRaises(ToolError):
            self.srv.read_resource("comms://doctrine/../../server.py")


class ResourcePromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = server.build_server()

    def test_surfaces_resource_is_live_json(self):
        self.assertIsInstance(
            json.loads(self.srv.read_resource("comms://surfaces")), dict)

    def test_stats_resource_serves_the_estate(self):
        stats = json.loads(self.srv.read_resource("capabilities://stats"))
        self.assertTrue(stats.get("total", 0) > 1000)

    def test_write_prompt_assembles_packet_and_brief(self):
        brief = ("A note about shipping the gate stack after 40 engines "
                 "told us it was generic.")
        out = self.srv.get_prompt("write", {"surface": "linkedin", "brief": brief})
        roles = [m["role"] for m in out["messages"]]
        self.assertEqual(roles, ["system", "user"])
        self.assertIn("capabilities_comms_score", out["messages"][0]["content"])
        self.assertEqual(out["messages"][1]["content"], brief)

    def test_unknown_prompt_is_named(self):
        with self.assertRaises(ToolError):
            self.srv.get_prompt("summarize", {})


class HandshakeTests(unittest.TestCase):
    def _call(self, srv, msg):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            srv.handle_request(msg)
        return json.loads(buf.getvalue()) if buf.getvalue() else None

    def test_initialize_advertises_resources_prompts_and_instructions(self):
        srv = server.build_server()
        r = self._call(srv, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {"protocolVersion": "2025-06-18",
                                        "capabilities": {}}})
        caps = r["result"]["capabilities"]
        self.assertIn("resources", caps)
        self.assertIn("prompts", caps)
        self.assertIn("PRIVACY_LOCK", r["result"]["instructions"])
        self.assertEqual(r["result"]["serverInfo"]["name"], "rig-capabilities")

    def test_resources_and_prompts_lists_round_trip(self):
        srv = server.build_server()
        rl = self._call(srv, {"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        pl = self._call(srv, {"jsonrpc": "2.0", "id": 3, "method": "prompts/list"})
        self.assertEqual({r["uri"] for r in rl["result"]["resources"]},
                         {r["uri"] for r in srv.resources})
        self.assertEqual({p["name"] for p in pl["result"]["prompts"]},
                         {"write", "review"})

    def test_privacy_lock_survives_the_wire(self):
        """isError semantics: the client sees the lock in the tool result."""
        srv = server.build_server()
        r = self._call(srv, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                             "params": {"name": "capabilities_comms_score",
                                        "arguments": {"surface": "love-notes",
                                                      "artifact": "text"}}})
        self.assertTrue(r["result"]["isError"])
        self.assertIn("PRIVACY_LOCK", r["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
