"""mcp_wire.selftest — a dry, per-target proof that every harness could pull the
server if wired, with no write to any live config.

The question 'can cursor / gemini / opencode / goose pull rig-capabilities' is
not answered by listing targets (verify does that); it is answered by projecting
the entry into that target's own dialect and reading it back. A dialect whose
projection does not round-trip would silently drop the server. This suite pins
the green path and a plant that must flip it red.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rig_capabilities import mcp_wire as MW  # noqa: E402


class WireSelftestTests(unittest.TestCase):
    def test_all_four_targets_resolve(self):
        r = MW.selftest()
        self.assertIs(r["all_resolvable"], True, r)
        got = {t["target"] for t in r["targets"]}
        self.assertEqual(got, {"cursor", "gemini", "opencode", "goose"})
        for t in r["targets"]:
            self.assertIs(t["resolvable"], True, t)
            self.assertIs(t["round_trips"], True, t)
            self.assertEqual(t["op"], "wire", t)

    def test_json_targets_stay_valid_json_after_projection(self):
        for name in ("cursor", "gemini", "opencode"):
            after, _ = MW.project(name, MW._EMPTY[name])
            json.loads(after)          # raises if the projection broke the JSON

    def test_a_broken_launch_spec_flips_it_red(self):
        """Plant: point the server file at nothing — nothing could launch."""
        orig = MW.SERVER
        MW.SERVER = REPO / "server_DOES_NOT_EXIST.py"
        try:
            r = MW.selftest()
            self.assertIs(r["all_resolvable"], False)
            self.assertIs(r["launch"]["resolvable"], False)
        finally:
            MW.SERVER = orig
        self.assertIs(MW.selftest()["all_resolvable"], True, "restore failed")

    def test_project_still_refuses_to_invent_a_container(self):
        """Non-vacuity for the safety property the seed models around: projecting
        into a config with no container is a named refusal, not a silent write."""
        after, ops = MW.project("cursor", "{}\n")
        self.assertEqual(after, "{}\n", "must not write when the container is absent")
        self.assertEqual(ops[0]["action"], "container_missing")

    def test_selftest_writes_no_live_config(self):
        """The seeds are in-memory; a run must not create any target file."""
        before = {name: live.exists() for name, live in MW.targets()}
        MW.selftest()
        after = {name: live.exists() for name, live in MW.targets()}
        self.assertEqual(before, after, "selftest touched a live config path")


if __name__ == "__main__":
    unittest.main()
