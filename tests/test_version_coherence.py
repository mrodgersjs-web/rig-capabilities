"""The version constant, the ladder, and ROADMAP are one claim in three places.

`docs/ROADMAP.md` grew rows 41–49 — each with its own proof packet — while
`__version__` stayed `40.0.0` and `VERSION_LADDER` stopped at `"40"`. Every
consumer of that constant (`GET /version`, `stats`, the public release zip name,
and the MCP `initialize` handshake) kept advertising rung 40 for nine shipped
increments. A client reading the MCP handshake could not tell that `round`
changed contract, which is exactly what a version is for.

These tests close the triangle. If any one of the three moves alone, this fails
in whichever direction the drift goes.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import rig_capabilities  # noqa: E402
from rig_capabilities import server  # noqa: E402

ROW = re.compile(r"^\|\s*(\d+)\s*\|", re.M)


def _doc_rows() -> set[int]:
    text = (REPO_ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    return {int(m) for m in ROW.findall(text)}


class VersionCoherenceTests(unittest.TestCase):
    def test_version_major_is_the_top_ladder_rung(self):
        top = max(int(k) for k in rig_capabilities.VERSION_LADDER)
        self.assertEqual(int(rig_capabilities.__version__.split(".")[0]), top,
                         f"__version__ {rig_capabilities.__version__} vs ladder top {top}")

    def test_mcp_handshake_advertises_the_package_version(self):
        """Two constants for one fact is how the drift started."""
        self.assertEqual(server.VERSION, rig_capabilities.__version__)

    def test_ladder_is_contiguous_from_two(self):
        keys = sorted(int(k) for k in rig_capabilities.VERSION_LADDER)
        self.assertEqual(keys, list(range(keys[0], keys[-1] + 1)),
                         f"rung numbered once, then never again: {keys}")

    def test_every_rung_above_the_wave_boundary_is_documented(self):
        """Rows 2..40 predate the wave table; anything new must appear in it."""
        missing = [k for k in (int(k) for k in rig_capabilities.VERSION_LADDER)
                   if int(k) > 40 and int(k) not in _doc_rows()]
        self.assertEqual(missing, [], f"shipped rungs with no ROADMAP row: {missing}")

    def test_every_roadmap_row_above_the_boundary_is_in_the_ladder(self):
        """The other direction: a documented row that never shipped."""
        ladder = {int(k) for k in rig_capabilities.VERSION_LADDER}
        extra = sorted(n for n in _doc_rows() if 40 < n <= max(ladder) and n not in ladder)
        self.assertEqual(extra, [], f"ROADMAP rows with no shipped rung: {extra}")

    def test_non_vacuity_the_triangle_actually_bites(self):
        """A hand-built triangle one rung out of shape must fail the check."""
        ladder = {"48": "x", "49": "y"}
        self.assertNotEqual(max(int(k) for k in ladder), 50,
                            "if the top rung moved to 50 this test must be rewritten, not deleted")


if __name__ == "__main__":
    unittest.main()
