"""The ULTRA cell contract validator.

Every test builds its own cell in a temp dir, so the suite does not depend on
the ultraplan checkout. Each refusal is asserted by its finding code, not by
prose, because the codes are what a board or CI reads.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rig_capabilities.ultra_cell import (  # noqa: E402
    SLOTS,
    discover_cells,
    find_cycles,
    plant_failure,
    validate_cell,
    validate_tree,
)

BIN = ROOT / "bin" / "rig-ultra"
GATES = {"plan.dq_before_build", "outward.gate_d"}

STOP = "#!/bin/sh\n[ -e out.md ] || { echo BLOCKED >&2; exit 2; }\nexit 0\n"
STOP_VACUOUS = "#!/bin/sh\nexit 0\n"


def write_cell(d: Path, *, level="L2", children=(), routes=None, gates=None, stop=STOP,
               ladder=("local/a", "paid/b"), tier=1, budget=None, kill=("k",)):
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        "---\nname: x\noutcome: o\ndone_when:\n  - 'file:out.md'\nquality_floor: 0.8\n---\n# x\n", encoding="utf-8")
    (d / "agent.md").write_text(
        "---\nname: x-agent\nmodel_ladder:\n" + "".join(f"  - {r}\n" for r in ladder)
        + f"autonomy_tier: {tier}\nverifier_family_differs: true\n---\n# agent\n", encoding="utf-8")
    gates = gates if gates is not None else [dict(name="g", code="c", jev="plan.dq_before_build")]
    b = budget or dict(usd=1, wallclock_seconds=10, mike_decisions=0)
    gtxt = "".join(
        f"  - name: {g['name']}\n    code: {g['code']}\n    jev: {g['jev']}\n"
        + (f"    why: {g['why']}\n" if g.get("why") else "") for g in gates)
    (d / "harness.yaml").write_text(
        f"level: {level}\ninputs: [a]\noutputs: [out.md]\ngates:\n{gtxt}"
        f"red_path:\n  plant: remove routes.yaml\n  expect: slot_missing\n"
        f"effort_budget:\n  usd: {b['usd']}\n  wallclock_seconds: {b['wallclock_seconds']}\n  mike_decisions: {b['mike_decisions']}\n"
        f"kill_criteria:\n" + "".join(f"  - {k}\n" for k in kill), encoding="utf-8")
    (d / "loop.yaml").write_text(
        "entry: e\nbody: b\nexit_gate: x\nmax_iterations: 3\npark: p\nclose: c\n", encoding="utf-8")
    (d / "hooks").mkdir(exist_ok=True)
    s = d / "hooks" / "stop"
    s.write_text(stop, encoding="utf-8")
    s.chmod(s.stat().st_mode | stat.S_IXUSR)
    (d / "context").mkdir(exist_ok=True)
    (d / "context" / "hydrate.yaml").write_text("sources:\n  - kind: artifact\n    items: [a]\n", encoding="utf-8")
    (d / "prompts").mkdir(exist_ok=True)
    (d / "prompts" / "leaf.md").write_text("# leaf\n", encoding="utf-8")
    routes = routes if routes is not None else [dict(when="always", call=children[0] if children else "self")]
    rtxt = "".join(f"  - when: {r['when']}\n    call: {r['call']}\n" for r in routes)
    (d / "routes.yaml").write_text(
        "children:\n" + ("".join(f"  - {c}\n" for c in children) or "  []\n") + f"routes:\n{rtxt}", encoding="utf-8")
    return d


def codes(rep):
    return {f["code"] for f in rep["findings"]}


class TestValidCell(unittest.TestCase):
    def test_complete_cell_is_valid(self):
        with tempfile.TemporaryDirectory() as td:
            rep = validate_cell(write_cell(Path(td) / "c"), known_gates=GATES)
            self.assertTrue(rep["ok"], rep["findings"])
            self.assertEqual(rep["level"], "L2")

    def test_all_eight_slots_are_required(self):
        for slot in SLOTS:
            with tempfile.TemporaryDirectory() as td:
                d = write_cell(Path(td) / "c")
                p = d / slot
                if p.is_dir():
                    for f in p.iterdir():
                        f.unlink()
                    p.rmdir()
                else:
                    p.unlink()
                rep = validate_cell(d, known_gates=GATES)
                self.assertFalse(rep["ok"], slot)
                self.assertIn("slot_missing", codes(rep), slot)


class TestRefusals(unittest.TestCase):
    def test_unknown_jev_gate_is_a_defect(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", gates=[dict(name="g", code="c", jev="plan.made_up")])
            self.assertIn("harness_gate_jev_unknown", codes(validate_cell(d, known_gates=GATES)))

    def test_jev_none_needs_a_why(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", gates=[dict(name="g", code="c", jev="none")])
            self.assertIn("harness_gate_jev_none_unjustified", codes(validate_cell(d, known_gates=GATES)))
            d2 = write_cell(Path(td) / "c2", gates=[dict(name="g", code="c", jev="none", why="graph property")])
            self.assertTrue(validate_cell(d2, known_gates=GATES)["ok"])

    def test_gate_without_code_check_is_a_defect(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", gates=[dict(name="g", code="", jev="plan.dq_before_build")])
            self.assertIn("harness_gate_code", codes(validate_cell(d, known_gates=GATES)))

    def test_budget_must_count_mike_decisions(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c")
            h = d / "harness.yaml"
            h.write_text(h.read_text().replace("  mike_decisions: 0\n", ""), encoding="utf-8")
            self.assertIn("harness_budget_key", codes(validate_cell(d, known_gates=GATES)))

    def test_red_path_required(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c")
            h = d / "harness.yaml"
            h.write_text(h.read_text().replace("  expect: slot_missing\n", ""), encoding="utf-8")
            self.assertIn("harness_red_path", codes(validate_cell(d, known_gates=GATES)))

    def test_ladder_must_be_local_first_with_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", ladder=("paid/x", "local/y"))
            self.assertIn("agent_ladder_not_local_first", codes(validate_cell(d, known_gates=GATES)))
            d2 = write_cell(Path(td) / "c2", ladder=("local/only",))
            self.assertIn("agent_ladder", codes(validate_cell(d2, known_gates=GATES)))

    def test_autonomy_tier_domain(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", tier=7)
            self.assertIn("agent_autonomy_tier", codes(validate_cell(d, known_gates=GATES)))

    def test_vacuous_stop_hook_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", stop=STOP_VACUOUS)
            self.assertIn("hooks_stop_vacuous", codes(validate_cell(d, known_gates=GATES)))

    def test_sibling_call_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_cell(root / "a", children=(), routes=[dict(when="x", call="../b")])
            write_cell(root / "b")
            rep = validate_cell(root / "a", known_gates=GATES)
            self.assertIn("routes_sibling_call", codes(rep))

    def test_studio_calls_must_resolve(self):
        """W01: `studio:` used to `continue` unchecked -- the 26/26 blind spot.
        Now the target must be a cell-shaped studio under the tree root."""
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", routes=[dict(when="x", call="studio:forecasting"),
                                                   dict(when="y", call="self"), dict(when="z", call="close")])
            self.assertIn("studio_target_unresolved", codes(validate_cell(d, known_gates=GATES)))
            (d / "studios" / "forecasting").mkdir(parents=True)
            (d / "studios" / "forecasting" / "agent.md").write_text("# f\n", encoding="utf-8")
            self.assertTrue(validate_cell(d, known_gates=GATES)["ok"])

    def test_studio_not_in_allowed_list_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", routes=[dict(when="x", call="studio:forecasting")])
            (d / "studios" / "forecasting").mkdir(parents=True)
            (d / "studios" / "forecasting" / "agent.md").write_text("# f\n", encoding="utf-8")
            rtxt = d / "routes.yaml"
            rtxt.write_text(rtxt.read_text() + "studios_allowed:\n  - studio:questioning\n", encoding="utf-8")
            self.assertIn("studio_not_allowed", codes(validate_cell(d, known_gates=GATES)))

    def test_declared_child_must_exist(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", children=("ghost",))
            self.assertIn("routes_child_absent", codes(validate_cell(d, known_gates=GATES)))

    def test_bad_level_refused(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c", level="L9")
            self.assertIn("harness_level", codes(validate_cell(d, known_gates=GATES)))


class TestTree(unittest.TestCase):
    def test_route_cycle_is_a_reported_defect(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_cell(root, level="L0", children=("p",))
            write_cell(root / "p", level="L1", children=("../",))  # edge back to ancestor
            cyc = find_cycles(root)
            self.assertTrue(cyc, "a cycle must be reported, not quietly survived")
            rep = validate_tree(root)
            self.assertFalse(rep["ok"], "a cyclic tree cannot pass")

    def test_tree_walks_declared_children_reports_leaves_and_orphans(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_cell(root, level="L0", children=("p",), routes=[dict(when="x", call="p")])
            write_cell(root / "p", level="L1", children=("../s", "../leaf"),
                       routes=[dict(when="x", call="../s"), dict(when="y", call="../leaf")])
            write_cell(root / "s", level="L2")
            (root / "leaf").mkdir()
            (root / "leaf" / "SKILL.md").write_text("---\nname: leaf\n---\n", encoding="utf-8")
            write_cell(root / "orphan", level="L2")
            order, orphans, leaves = discover_cells(root)
            self.assertEqual(len(order), 3)  # root, p, s; the orphan is deliberately not walked
            self.assertEqual(orphans, ["orphan"])
            self.assertEqual(leaves, ["leaf"])
            rep = validate_tree(root)
            self.assertFalse(rep["ok"], "an orphan must fail the tree")
            self.assertEqual(rep["valid"], 3)
            self.assertEqual(sorted(rep["by_level"]), ["L0", "L1", "L2"])

    def test_plant_goes_red_and_restores(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c")
            before = (d / "routes.yaml").read_bytes()
            res = plant_failure(d)
            self.assertTrue(res["ok"], res)
            self.assertTrue(res["restored_byte_identical"])
            self.assertEqual((d / "routes.yaml").read_bytes(), before)

    def test_plant_refuses_when_nothing_to_plant(self):
        with tempfile.TemporaryDirectory() as td:
            d = write_cell(Path(td) / "c")
            res = plant_failure(d, slot="nope.yaml")
            self.assertFalse(res["ok"])
            self.assertIn("not a file", res["reason"])


class TestCLI(unittest.TestCase):
    def run_cli(self, *argv):
        return subprocess.run([sys.executable, str(BIN), *argv], cwd=ROOT, capture_output=True, text=True)

    def test_validate_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_cell(root, level="L0")
            r = self.run_cli("cell", "validate", str(root), "--json")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rep = json.loads(r.stdout)
            self.assertTrue(rep["ok"])
            self.assertTrue(rep["declared_gates_seen"], "validator must read the live gate table")
            (root / "routes.yaml").unlink()
            r2 = self.run_cli("cell", "validate", str(root))
            self.assertEqual(r2.returncode, 1)
            self.assertIn("slot_missing", r2.stdout)

    def test_tree_and_plant_commands(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_cell(root, level="L0")
            r = self.run_cli("cell", "tree", str(root))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("L0", r.stdout)
            p = self.run_cli("cell", "plant", str(root))
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            self.assertIn("RED as required", p.stdout)


if __name__ == "__main__":
    unittest.main()
