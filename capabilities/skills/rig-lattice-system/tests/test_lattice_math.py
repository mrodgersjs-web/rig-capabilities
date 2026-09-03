"""Lattice math — the assertions carried over from strategy_studio's suites.

Ported from ``tests/test_lattice.py``, ``tests/test_lattice_sio.py`` and
``tests/test_geometry_sio.py`` in strategy-studio-pro. Those files could not
be vendored as-is: they import ``strategy_studio.hermes.*``,
``strategy_studio.session`` and ``strategy_studio.core.types`` (none of which
are part of this bundle) and they assert on the dropped
``D1_STRATEGY``/``D2_INTELLIGENCE``/``D3_OPERATIONS`` diamond dialect. What
survives is what was actually being tested: the geometry, the BMS formula, and
both cell-id shapes.
"""

from __future__ import annotations

import unittest

from rig_lattice.lattice import (
    ALTITUDE_BONUS,
    N_ARCHETYPES,
    N_CELLS,
    N_PRIMARY_COORDS,
    BMSMode,
    Diamond,
    IQRSQPIStep,
    Level,
    all_cells,
    archetypes,
    compute_bms,
    parse_cell_id,
    primary_coordinates,
)
from rig_lattice.lattice.schema import LatticeCoordinate
from rig_lattice.lattice.validator import (
    generate_all_cell_ids,
    generate_primary_coordinates,
    is_old_format,
    is_valid_cell_id,
)
from rig_lattice.lattice.wire import (
    LatticeCell,
    generate_all_build_cards,
    get_all_588_cells,
    get_all_cells,
)


class TestGeometry(unittest.TestCase):
    def test_axis_cardinality(self):
        self.assertEqual(len(Level), 7)
        self.assertEqual(len(Diamond), 3)
        self.assertEqual(len(BMSMode), 4)
        self.assertEqual(len(IQRSQPIStep), 7)

    def test_588_cells_unique(self):
        cells = all_cells()
        self.assertEqual(len(cells), 588)
        self.assertEqual(len(cells), N_CELLS)
        self.assertEqual(len(set(cells)), 588)

    def test_84_primary_coordinates(self):
        self.assertEqual(len(primary_coordinates()), 84)
        self.assertEqual(len(primary_coordinates()), N_PRIMARY_COORDS)

    def test_28_archetypes(self):
        self.assertEqual(len(set(archetypes())), 28)
        self.assertEqual(N_ARCHETYPES, 28)

    def test_147_legacy_shape_cells(self):
        """7 levels x 3 diamonds x 7 steps, BMS axis implicit."""
        cells = get_all_cells()
        self.assertEqual(len(cells), 147)
        self.assertEqual(len({c.cell_id for c in cells}), 147)

    def test_147_build_cards(self):
        self.assertEqual(len(generate_all_build_cards()), 147)

    def test_588_cells_via_wire(self):
        cells = get_all_588_cells()
        self.assertEqual(len(cells), 588)
        self.assertEqual(len({c.full_cell_id for c in cells}), 588)

    def test_validator_enumerations_agree(self):
        self.assertEqual(len(generate_all_cell_ids()), 588)
        self.assertEqual(len(generate_primary_coordinates()), 84)
        self.assertEqual(set(generate_all_cell_ids()), set(all_cells()))

    def test_all_588_ids_parse(self):
        for cid in all_cells():
            self.assertEqual(parse_cell_id(cid).cell_id, cid)


class TestCellIdFormats(unittest.TestCase):
    def test_canonical_shape(self):
        coord = parse_cell_id("L2-D1-A1-I1")
        self.assertEqual(coord.cell_id, "L2-D1-A1-I1")
        self.assertEqual(coord.primary_coordinate, "L2-D1-A1")

    def test_primary_coordinate_property(self):
        coord = LatticeCoordinate(
            level=Level.L1,
            diamond=Diamond.D1,
            bms_mode=BMSMode.A1,
            step=IQRSQPIStep.I1,
        )
        self.assertEqual(coord.primary_coordinate, "L1-D1-A1")
        self.assertTrue(coord.is_a1)
        self.assertFalse(coord.requires_approval)

    def test_bare_digit_dialect_normalizes(self):
        self.assertEqual(parse_cell_id("L3-2-A2-R").cell_id, "L3-D2-A2-R")

    def test_dotted_dialect_normalizes(self):
        coord = parse_cell_id("intent.D1_physical.A1.intent")
        self.assertEqual(coord.cell_id, "L1-D1-A1-I1")

    def test_old_format_rejected(self):
        self.assertTrue(is_old_format("L2-D1-Intent"))
        self.assertFalse(is_valid_cell_id("L2-D1-Intent"))
        with self.assertRaises(ValueError):
            parse_cell_id("L2-D1-Intent")

    def test_out_of_range_level_rejected(self):
        with self.assertRaises(ValueError):
            parse_cell_id("L8-D1-A1-I1")

    def test_error_names_the_three_shapes(self):
        with self.assertRaises(ValueError) as ctx:
            parse_cell_id("nonsense")
        message = str(ctx.exception)
        for shape in ("canonical", "bare-digit", "dotted"):
            self.assertIn(shape, message)

    def test_wire_parses_both_shapes(self):
        self.assertEqual(LatticeCell.parse("L2-D1-A1-S").full_cell_id, "L2-D1-A1-S")
        self.assertEqual(LatticeCell.parse("L2-D1-S").cell_id, "L2-D1-S")
        with self.assertRaises(ValueError):
            LatticeCell.parse("L2-A1-S")


class TestBMSSelection(unittest.TestCase):
    def test_from_score_bands(self):
        self.assertIs(BMSMode.from_score(0.9), BMSMode.A1)
        self.assertIs(BMSMode.from_score(0.75), BMSMode.A1)
        self.assertIs(BMSMode.from_score(0.5), BMSMode.A2)
        self.assertIs(BMSMode.from_score(0.45), BMSMode.A2)
        self.assertIs(BMSMode.from_score(0.3), BMSMode.A3)
        self.assertIs(BMSMode.from_score(0.25), BMSMode.A3)
        self.assertIs(BMSMode.from_score(0.1), BMSMode.A4)

    def test_only_a1_is_deterministic(self):
        self.assertTrue(BMSMode.A1.deterministic)
        self.assertFalse(BMSMode.A1.model_in_decision_path)
        for mode in (BMSMode.A2, BMSMode.A3, BMSMode.A4):
            self.assertFalse(mode.deterministic)
            self.assertTrue(mode.model_in_decision_path)

    def test_a3_a4_require_approval(self):
        self.assertFalse(BMSMode.A1.approval_required)
        self.assertFalse(BMSMode.A2.approval_required)
        self.assertTrue(BMSMode.A3.approval_required)
        self.assertTrue(BMSMode.A4.approval_required)

    def test_raw_score_weights(self):
        """raw = failure_cost*0.4 + reversibility*0.3 + mechanism_clarity*0.3."""
        result = compute_bms(
            failure_cost=1.0, reversibility=0.0, mechanism_clarity=0.0,
            level=Level.L4,  # altitude bonus 0.0
        )
        self.assertAlmostEqual(result.raw, 0.4, places=9)
        result = compute_bms(
            failure_cost=0.0, reversibility=1.0, mechanism_clarity=0.0,
            level=Level.L4,
        )
        self.assertAlmostEqual(result.raw, 0.3, places=9)
        result = compute_bms(
            failure_cost=0.0, reversibility=0.0, mechanism_clarity=1.0,
            level=Level.L4,
        )
        self.assertAlmostEqual(result.raw, 0.3, places=9)

    def test_altitude_penalty_lowers_the_band(self):
        low = compute_bms(0.2, 0.8, 0.8, level=Level.L1)
        high = compute_bms(0.2, 0.8, 0.8, level=Level.L7)
        self.assertGreater(low.confidence, high.confidence)
        self.assertAlmostEqual(
            low.adj_altitude - high.adj_altitude, 0.70, places=9
        )

    def test_altitude_bonus_table(self):
        self.assertEqual(ALTITUDE_BONUS["L1"], 0.35)
        self.assertEqual(ALTITUDE_BONUS["L4"], 0.0)
        self.assertEqual(ALTITUDE_BONUS["L7"], -0.35)

    def test_past_failure_and_volume_adjustments(self):
        base = compute_bms(0.5, 0.5, 0.5, level=Level.L4)
        penalised = compute_bms(
            0.5, 0.5, 0.5, past_failure_rate=1.0, level=Level.L4
        )
        self.assertAlmostEqual(penalised.adj_failure, -0.2, places=9)
        self.assertLess(penalised.confidence, base.confidence)

        volume = compute_bms(0.5, 0.5, 0.5, data_volume=1.0, level=Level.L4)
        self.assertAlmostEqual(volume.adj_volume, 0.05, places=9)

    def test_score_clamped_to_unit_interval(self):
        top = compute_bms(1.0, 1.0, 1.0, data_volume=1.0, level=Level.L1)
        self.assertLessEqual(top.confidence, 1.0)
        self.assertIs(top.mode, BMSMode.A1)
        bottom = compute_bms(
            0.0, 0.0, 0.0, past_failure_rate=1.0, data_volume=0.0, level=Level.L7
        )
        self.assertGreaterEqual(bottom.confidence, 0.0)
        self.assertIs(bottom.mode, BMSMode.A4)

    def test_inputs_out_of_range_rejected(self):
        for kwargs in (
            {"failure_cost": 1.5},
            {"reversibility": -0.1},
            {"mechanism_clarity": 2.0},
            {"past_failure_rate": 1.1},
            {"data_volume": -1.0},
        ):
            with self.assertRaises(ValueError):
                compute_bms(**kwargs)

    def test_same_input_same_mode(self):
        a = compute_bms(0.7, 0.6, 0.65, level=Level.L3)
        b = compute_bms(0.7, 0.6, 0.65, level=Level.L3)
        self.assertEqual(a.to_dict(), b.to_dict())


if __name__ == "__main__":
    unittest.main()
