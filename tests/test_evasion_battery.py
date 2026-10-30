"""Evasion battery — seven planted attacks against the tool-selection gates.

Every attack MUST fail closed: either a typed TOOL_SELECTION_MALFORMED block
or a CHECKLIST_BLOCK verdict. A planted attack that passes is a gate hole,
not a test failure to relax.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "capabilities/skills/rig-determinism-85"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tool_selection import (  # noqa: E402
    ToolSelectionBlock,
    certify_build,
    check_build_checklist,
    select_framework,
)
from test_tool_selection import SCHEDULE, _live_inventory_sha256  # noqa: E402

CLOCK = {
    "clock_critical": {
        "consumer": "live pricing dashboard",
        "start_latency_ms": 30000,
        "catch_up_policy": "catch_up",
        "mechanism": "Temporal workflow with durable timer",
        "deployment_evidence": "authority/evidence/temporal-pricing.json",
    }
}


def _green_build(testcase, tmp, **overrides):
    diagram = Path(tmp) / "diagram.json"
    diagram.write_text(
        json.dumps({"schema_version": 2, "diagram_type": "workflow"}),
        encoding="utf-8",
    )
    build = {
        "properties": {"ordinary_schedule": SCHEDULE},
        "process_id": "julie_synthetic",
        "inventory_sha256": _live_inventory_sha256(),
        "framework": "kestra",
        "durable_system": True,
        "pydantic_models": ["In", "Out"],
        "model_necessity_claims": ["classify: deterministic sort failed"],
        "archify_diagram_path": "diagram.json",
        "d85_realized_pass": True,
        "orchestration_is_code": True,
        "lattice": {'cell_id': 'L3-D2-A1-I1', 'bms': {'failure_cost': 0.5, 'reversibility': 0.95, 'mechanism_clarity': 0.95, 'past_failure_rate': 0.0, 'data_volume': 0.5, 'level': 'L3'}, 'a1_failure': None},
    }
    build.update(overrides)
    return build


import json  # noqa: E402  (used by _green_build)


class EvasionBattery(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _fails(self, name):
        return [c for c in self.checks if c["check"] == name and not c["pass"]]

    # 1. Lying properties: a well-formed record whose evidence contradicts the
    #    claim (SLA too loose) must BLOCK, never read as absent/FALSE.
    def test_attack_lying_properties_blocks(self) -> None:
        lying = {"clock_critical": dict(CLOCK["clock_critical"], start_latency_ms=60001)}
        with self.assertRaises(ToolSelectionBlock) as caught:
            select_framework(lying)
        self.assertIn("contradicted", caught.exception.detail)

    # 2. Framework swap: declare the cheaper framework the decision table
    #    does not require for these properties.
    def test_attack_framework_swap_blocks(self) -> None:
        build = _green_build(self, self.tmp, properties=CLOCK, framework="kestra")
        result = check_build_checklist(build, root=Path(self.tmp))
        self.checks = result["checks"]
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertTrue(self._fails("framework_matches_standard"))

    # 3. Diagram forgery: an absolute path to a perfectly-shaped diagram that
    #    lives outside the declared root.
    def test_attack_diagram_forgery_outside_root_blocks(self) -> None:
        outside = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        forged = Path(outside) / "forged.json"
        forged.write_text(json.dumps({"diagram_type": "workflow"}), encoding="utf-8")
        build = _green_build(self, self.tmp, archify_diagram_path=str(forged))
        result = check_build_checklist(build, root=Path(self.tmp))
        self.checks = result["checks"]
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertTrue(self._fails("archify_diagram_present"))

    # 4. Necessity forgery: a model build whose necessity "claims" are empty
    #    strings — presence without substance.
    def test_attack_necessity_forgery_blocks(self) -> None:
        build = _green_build(self, self.tmp, model_necessity_claims=[""])
        with self.assertRaises(ToolSelectionBlock) as caught:
            check_build_checklist(build, root=Path(self.tmp))
        self.assertEqual(caught.exception.code, "TOOL_SELECTION_MALFORMED")

    # 5. Schema smuggling: an unknown top-level field trying to ride along.
    def test_attack_schema_smuggling_blocks(self) -> None:
        build = _green_build(self, self.tmp)
        build["framework_override"] = "temporal"
        with self.assertRaises(ToolSelectionBlock) as caught:
            check_build_checklist(build, root=Path(self.tmp))
        self.assertIn("unknown checklist fields", caught.exception.detail)

    # 6. Path traversal: a relative diagram path that climbs out of root.
    def test_attack_path_traversal_blocks(self) -> None:
        build = _green_build(self, self.tmp, archify_diagram_path="../../etc/passwd")
        result = check_build_checklist(build, root=Path(self.tmp))
        self.checks = result["checks"]
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertTrue(self._fails("archify_diagram_present"))
        self.assertIn("escapes the declared root", self._fails("archify_diagram_present")[0]["detail"])

    # 7. Stale-hash replay: an old checklist re-submitted after code drift.
    def test_attack_stale_hash_replay_blocks(self) -> None:
        build = _green_build(self, self.tmp, inventory_sha256="0" * 64)
        result = certify_build(build, "julie_synthetic", root=Path(self.tmp))
        self.assertEqual(result["verdict"], "CHECKLIST_BLOCK")
        self.assertEqual(result["inventory_binding"], "stale")


if __name__ == "__main__":
    unittest.main()
