"""An asset whose gates cannot be loaded is worse than an asset with no gates.

Discovered 2026-09-02 while verifying a rewritten loop: `catalog._pick_main_text`
reads only `HEAD_BYTES` (4096), so a YAML frontmatter longer than that is parsed
from a truncated buffer, `_quality_block` returns {} and every field the file
declares reads as absent. `./bin/rig-capabilities test <id>` then answers
`pass=false` with ZERO results — indistinguishable from "this asset has no
checks" unless you know to look, and an agent that queries the catalog for the
gate simply finds nothing.

The failure is caused by putting executable programs *inside* frontmatter. The
house pattern that does not have this problem is the validator script:
`capabilities/skills/gamma-trace-record-and-failure-attribution/validate_gamma.py`
with one-line `cmd:` invocations. Long programs belong there.

Run the detector directly for the per-file verdict:
    python3 scripts/frontmatter_visibility.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _detector():
    path = REPO / "scripts" / "frontmatter_visibility.py"
    spec = importlib.util.spec_from_file_location("frontmatter_visibility", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FrontmatterVisibility(unittest.TestCase):
    def test_no_canonical_asset_is_invisible_to_the_catalog(self):
        mod = _detector()
        hidden, other, clean = mod.scan()
        detail = "; ".join(f"{rel} (fm_end={end}, bytes={size}, lost={','.join(lost)})"
                           for rel, end, size, lost in hidden)
        self.assertTrue(clean > 50, f"detector scanned only {clean} assets — it is broken")
        self.assertEqual(other, 0, f"assets declare quality fields the loader drops: "
                                   f"see detector output")
        self.assertEqual(hidden, [],
                         "frontmatter exceeds HEAD_BYTES and was truncated to nothing; "
                         "move the programs into a script the cmd: lines invoke. " + detail)

    def test_the_detector_actually_detects(self):
        """A guard that cannot fire is theater: shrink HEAD_BYTES and it must report."""
        from rig_capabilities import catalog
        mod = _detector()
        saved = catalog.HEAD_BYTES
        try:
            catalog.HEAD_BYTES = 64          # every real frontmatter is longer than this
            hidden, other, clean = mod.scan()
            self.assertTrue(hidden or other,
                            "with a 64-byte head the detector must find victims; "
                            "a detector that reports clean under a known-bad head "
                            "would report clean forever")
        finally:
            catalog.HEAD_BYTES = saved


if __name__ == "__main__":
    unittest.main()
