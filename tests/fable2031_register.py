"""P3 tests: the capability register, convergence math, and the Realign driver.

Fixture-only, stdlib-only, no subprocess: the whole module must run in well
under a second because `certify`'s suite gate replays it inside a copied tree.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys
from unittest import mock
import hashlib
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import convergence as CV  # noqa: E402
from rig_capabilities import realign, register as R  # noqa: E402
from rig_capabilities import afproof  # noqa: E402

PREV_CSV = FIX / "register-previous.csv"
CUR_CSV = FIX / "register-current.csv"
BOOKINGS_VALID = FIX / "bookings-valid.json"
BOOKINGS_ZERO = FIX / "bookings-zero.json"
CORPUS_CLEAN = {"raw": 20, "unique": 20, "classified": 19, "unclassified": 1,
                "unclassified_rate": 0.05, "truncated": 1, "ok": True}


def row(**over):
    """One sound register row; override any cell to test one rule at a time."""
    base = {"id": "capability_catalog_index",
            "name": "Repo-rooted capability catalog scan and index",
            "subsystem": "chassis", "studio": "CompanyOSFactory", "type": "tool",
            "maturity_M0_5": 2, "automation_band": "A2", "weight_w": 3,
            "evidence_paths": ["rig_capabilities/catalog.py"],
            "harness_signed": False, "verifier_named": None,
            "proof_status": "golden_run", "target_M_2031": 4,
            "target_band_2031": "A1", "blocking_deps": [],
            "enables_product_classes": ["capability_card"], "duplicate_of": None,
            "contradicts": [], "last_touched": "2026-09-01",
            "owner": "otto-operations", "source_document_ids": [],
            "contradiction_group": None}
    base.update(over)
    return base


def booked(**over):
    base = row(id="booked_qualified_conversations",
               name="Booked qualified conversations (the appointment KPI)",
               subsystem="steering", studio="GTM", type="offer",
               maturity_M0_5=0, automation_band="manual", weight_w=5,
               evidence_paths=["data/fable2031/bookings-2026-W36.json"],
               proof_status="none", target_M_2031=1, owner="Mike")
    base.update(over)
    return base


def tmp_repo(rows=None, bookings=None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="f31-reg-"))
    if rows is not None:
        R.write_register(None, rows, path=root / R.REGISTER_STORE)
    if bookings is not None:
        target = root / R.BOOKINGS_ROOT
        target.mkdir(parents=True, exist_ok=True)
        (target / R.BOOKINGS_FILE.format(week=bookings["week"])).write_text(
            json.dumps(bookings), encoding="utf-8")
    return root


def load(path):
    return R.load_register(None, path=path)


class RegisterTests(unittest.TestCase):
    # -- schema -------------------------------------------------------------

    def test_field_order_is_the_criteria_card_order(self):
        self.assertEqual(R.REGISTER_FIELDS[:20], (
            "id", "name", "subsystem", "studio", "type", "maturity_M0_5",
            "automation_band", "weight_w", "evidence_paths", "harness_signed",
            "verifier_named", "proof_status", "target_M_2031",
            "target_band_2031", "blocking_deps", "enables_product_classes",
            "duplicate_of", "contradicts", "last_touched", "owner"))
        self.assertEqual(R.REGISTER_FIELDS[20:],
                         ("source_document_ids", "contradiction_group"))
        self.assertEqual(len(R.REGISTER_FIELDS), 22)

    def test_vocabularies(self):
        self.assertEqual(len(R.SUBSYSTEMS), 14)
        self.assertEqual(R.SUBSYSTEMS[:3], ("chassis", "powertrain", "transmission"))
        self.assertIn("scrutineering", R.SUBSYSTEMS)
        self.assertEqual(R.STUDIOS, ("Design", "App", "GTM", "LinkedIn",
                                     "Strategy", "CompanyOSFactory"))
        self.assertEqual(R.TYPES, ("workflow", "harness", "doctrine", "tool",
                                   "repo", "dataset", "asset", "offer"))
        self.assertEqual(R.BANDS, ("A1", "A2", "A3", "A4", "manual"))
        self.assertEqual(R.PROOF_STATUS, ("none", "golden_run",
                                          "proofpacket_sealed", "replay_passing"))
        # a 2031 target is always an automation band, never `manual`
        self.assertEqual(R.TARGET_BANDS, ("A1", "A2", "A3", "A4"))

    def test_clean_row_validates(self):
        self.assertEqual(R.validate_row(row()), [])
        self.assertEqual(R.validate_row(booked()), [])

    def test_no_evidence_path_no_row(self):
        self.assertIn("evidence_paths_empty",
                      R.validate_row(row(evidence_paths=[])))
        self.assertIn("evidence_paths_empty",
                      R.validate_row(row(evidence_paths="")))

    def test_no_mesh_edge_no_row(self):
        self.assertIn("enables_product_classes_empty",
                      R.validate_row(row(enables_product_classes=[])))

    def test_M4_without_named_verifier_is_rejected(self):
        errs = R.validate_row(row(maturity_M0_5=4, verifier_named=None))
        self.assertIn("verifier_named_missing_for_M4plus", errs)
        self.assertIn("verifier_named_missing_for_M4plus",
                      R.validate_row(row(maturity_M0_5=5, verifier_named="  ")))
        self.assertEqual(R.flagged_owners([row(owner="otto-operations",
                                               maturity_M0_5=4,
                                               verifier_named=None)]),
                         ["otto-operations"])
        # M3 needs no verifier; the law binds at M4+
        self.assertEqual(R.validate_row(row(maturity_M0_5=3, verifier_named=None)), [])

    def test_unknown_vocabulary_is_rejected(self):
        for field, junk in (("subsystem", "drivetrain"), ("studio", "Sales"),
                            ("type", "skill"), ("automation_band", "A5"),
                            ("proof_status", "vibes"),
                            ("target_band_2031", "manual")):
            with self.subTest(field=field):
                self.assertIn(f"{field}_unknown",
                              R.validate_row(row(**{field: junk})))

    def test_ranges_and_types(self):
        self.assertIn("maturity_M0_5_out_of_range",
                      R.validate_row(row(maturity_M0_5=6)))
        self.assertIn("weight_w_out_of_range", R.validate_row(row(weight_w=0)))
        self.assertIn("target_M_2031_out_of_range",
                      R.validate_row(row(target_M_2031=9)))
        self.assertIn("weight_w_not_integer",
                      R.validate_row(row(weight_w="heavy")))
        self.assertIn("maturity_M0_5_not_integer",
                      R.validate_row(row(maturity_M0_5=None)))
        self.assertIn("harness_signed_not_boolean",
                      R.validate_row(row(harness_signed="maybe")))
        self.assertIn("last_touched_not_iso_date",
                      R.validate_row(row(last_touched="09/01/2026")))
        self.assertIn("owner_missing", R.validate_row(row(owner="")))
        self.assertIn("id_missing", R.validate_row(row(id="")))
        self.assertIn("name_missing", R.validate_row(row(name="")))
        self.assertIn("duplicate_of_self",
                      R.validate_row(row(duplicate_of="capability_catalog_index")))
        self.assertEqual(R.validate_row("not a mapping"), ["row_not_mapping"])

    def test_multiple_rules_reported_together(self):
        errs = R.validate_row(row(evidence_paths=[], enables_product_classes=[],
                                  studio="Sales", maturity_M0_5=4))
        self.assertEqual(set(errs), {"evidence_paths_empty",
                                     "enables_product_classes_empty",
                                     "studio_unknown",
                                     "verifier_named_missing_for_M4plus"})

    # -- the mandatory revenue row -----------------------------------------

    def test_require_booked_row_accepts_weighted_gtm_row(self):
        rows = [row(), booked()]
        self.assertIsNone(R.require_booked_row(rows))

    def test_require_booked_row_rejects_missing_or_underweighted(self):
        for rows in ([row()],
                     [],
                     [booked(weight_w=3)],
                     [booked(weight_w=4)],
                     [booked(studio="Strategy")],
                     [row(id="booked_call", weight_w=5, studio="GTM")]):
            with self.subTest(count=len(rows)):
                with self.assertRaises(R.RegisterError) as ctx:
                    R.require_booked_row(rows)
                self.assertEqual(
                    str(ctx.exception),
                    "booked_qualified_conversations_missing_or_underweighted")

    # -- the store ---------------------------------------------------------

    def test_write_then_load_round_trip_is_stable(self):
        root = tmp_repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        rows = [booked(),
                row(id="aaa_first", name="First",
                    evidence_paths=["rig_capabilities/catalog.py"],
                    enables_product_classes=["session_harness",
                                             "capability_card"],
                    source_document_ids=["zeta-card", "alpha-card"]),
                row()]
        dest = R.write_register(root, rows)
        text = dest.read_text(encoding="utf-8")
        raw = text.splitlines()
        self.assertEqual(raw[0], ",".join(R.REGISTER_FIELDS))
        ids = [line.split(",")[0] for line in raw[1:]]
        self.assertEqual(ids, sorted(ids))                      # sorted by id
        self.assertIn('[""capability_card"",""session_harness""]', text)
        # list cells are compact AND sorted, so re-writes are stable
        self.assertIn('[""alpha-card"",""zeta-card""]', text)
        self.assertEqual(list(root.glob(".register-*.tmp")), [])  # nothing left behind
        again = R.load_register(root)
        self.assertEqual(len(again), 3)
        second = R.write_register(None, again, path=root / "second.csv")
        self.assertEqual(second.read_bytes(), dest.read_bytes())
        by_id = {r["id"]: r for r in again}
        self.assertIsInstance(by_id["aaa_first"]["harness_signed"], bool)
        self.assertEqual(by_id["aaa_first"]["weight_w"], 3)
        self.assertIsNone(by_id["aaa_first"]["verifier_named"])

    def test_load_register_missing_file_is_empty(self):
        root = tmp_repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        self.assertEqual(R.load_register(root), [])

    def test_diff_register_reports_added_removed_changed(self):
        prev = [booked(), row(maturity_M0_5=1, automation_band="A3"),
                row(id="gone", name="Gone",
                    evidence_paths=["rig_capabilities/catalog.py"],
                    enables_product_classes=["capability_card"])]
        cur = [booked(maturity_M0_5=0), row(maturity_M0_5=2, automation_band="A2"),
               row(id="born", name="Born",
                   evidence_paths=["rig_capabilities/catalog.py"],
                   enables_product_classes=["session_harness"])]
        diff = R.diff_register(prev, cur)
        self.assertEqual(diff["added"], ["born"])
        self.assertEqual(diff["removed"], ["gone"])
        self.assertEqual([c["id"] for c in diff["changed"]],
                         ["capability_catalog_index"])
        changed = diff["changed"][0]["fields"]
        self.assertEqual(changed["maturity_M0_5"], {"from": "1", "to": "2"})
        self.assertEqual(changed["automation_band"], {"from": "A3", "to": "A2"})
        self.assertEqual(diff["counts"], {"added": 1, "removed": 1, "changed": 1,
                                          "unchanged": 1})
        self.assertEqual(R.diff_register([], [])["counts"]["changed"], 0)

    # -- bookings ----------------------------------------------------------

    def test_load_bookings_counts_only_qualifying_records(self):
        doc = R.load_bookings(BOOKINGS_VALID, root=REPO_ROOT)
        self.assertEqual(doc["week"], "2026-W36")
        self.assertEqual(doc["count"], 2)
        self.assertEqual(len(doc["records"]), doc["count"])
        self.assertEqual(doc["invalid"], [])
        for rec in doc["records"]:
            self.assertTrue(Path(REPO_ROOT / rec["qualification_evidence_resolved"]).is_file()
                            or Path(rec["qualification_evidence_resolved"]).is_file())

    def test_load_bookings_zero_when_evidence_does_not_resolve(self):
        doc = R.load_bookings(BOOKINGS_ZERO, root=REPO_ROOT)
        self.assertEqual(doc["count"], 0)
        self.assertEqual(doc["records"], [])
        self.assertEqual(doc["total"], 1)
        self.assertIn("qualification_evidence_unresolved",
                      doc["invalid"][0]["reason"])

    def test_load_bookings_rejects_malformed_and_missing(self):
        root = tmp_repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with self.assertRaises(R.RegisterError) as ctx:
            R.load_bookings(root / "nope.json")
        self.assertIn("bookings_artifact_missing", str(ctx.exception))
        bad = root / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with self.assertRaises(R.RegisterError):
            R.load_bookings(bad)
        wrong = root / "wrong.json"
        wrong.write_text('{"week": "2026-W36"}', encoding="utf-8")
        with self.assertRaises(R.RegisterError):
            R.load_bookings(wrong)

    def test_bookings_record_without_fields_or_bad_date_is_dropped(self):
        root = tmp_repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "b.json").write_text(json.dumps({
            "week": "2026-W36", "records": [
                {"id": "x", "date": "2026-09-01", "account": "a",
                 "source_record_id": "s"},
                {"id": "y", "date": "09/01/2026", "account": "a",
                 "source_record_id": "s",
                 "qualification_evidence_path": "rig_capabilities/catalog.py"},
            ]}), encoding="utf-8")
        doc = R.load_bookings(root / "b.json", root=REPO_ROOT)
        self.assertEqual(doc["count"], 0)
        self.assertEqual([r["reason"].split(":")[0] for r in doc["invalid"]],
                         ["fields_missing", "date_not_iso"])

    # -- the gate ----------------------------------------------------------

    def test_gate_register_green_on_committed_csv(self):
        ok, detail = R.gate_register(REPO_ROOT)
        self.assertTrue(ok, detail)
        self.assertIn("register_ok", detail)

    def test_gate_register_red_when_evidence_blanked(self):
        root = tmp_repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        rows = R.load_register(REPO_ROOT)
        victim = next(r["id"] for r in rows if r["id"] != R.BOOKED_ID)
        R.write_register(root, [{**r, "evidence_paths": []} if r["id"] == victim
                                else r for r in rows])
        ok, detail = R.gate_register(root)
        self.assertFalse(ok)
        self.assertIn("evidence_paths_empty", detail)

    def test_gate_register_red_on_missing_or_header_only(self):
        bare = tmp_repo(rows=None)
        self.addCleanup(shutil.rmtree, bare, ignore_errors=True)
        self.assertEqual(R.gate_register(bare),
                         (False, "register_missing:capability_register.csv"))
        header_only = tmp_repo(rows=[])
        self.addCleanup(shutil.rmtree, header_only, ignore_errors=True)
        self.assertEqual(R.gate_register(header_only), (False, "register_empty"))
        root = tmp_repo(rows=[row()])
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        ok, detail = R.gate_register(root)
        self.assertFalse(ok)
        self.assertIn("booked_qualified_conversations_missing_or_underweighted",
                      detail)

    def test_gate_register_red_on_unresolvable_evidence(self):
        root = tmp_repo(rows=[booked(evidence_paths=[
            "data/fable2031/bookings-2026-W36.json"]),
            row(evidence_paths=["rig_capabilities/definitely_not_here.py"])])
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        ok, detail = R.gate_register(root)
        self.assertFalse(ok)
        self.assertIn("evidence_path_unresolved", detail)

    def test_gate_register_red_on_duplicate_row_ids(self):
        root = self.evidenced_repo([booked(), row(), row()])
        ok, detail = R.gate_register(root)
        self.assertFalse(ok)
        self.assertIn("duplicate_row_id", detail)

    def evidenced_repo(self, rows):
        """A tmp repo where every evidence path in `rows` really exists."""
        root = tmp_repo(rows=rows)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "rig_capabilities").mkdir()
        (root / "rig_capabilities" / "catalog.py").write_text("# fixture\n")
        (root / "data" / "fable2031").mkdir(parents=True)
        (root / "data" / "fable2031" / "bookings-2026-W36.json").write_text("{}")
        return root


    def test_gate_register_never_raises(self):
        ok, detail = R.gate_register(Path("/proc/definitely-not-a-repo"))
        self.assertFalse(ok)
        self.assertTrue(detail)


class ConvergenceTests(unittest.TestCase):
    def setUp(self):
        self.prev = load(PREV_CSV)
        self.cur = load(CUR_CSV)
        self.bookings = R.load_bookings(BOOKINGS_VALID, root=REPO_ROOT)
        self.zero = R.load_bookings(BOOKINGS_ZERO, root=REPO_ROOT)

    # -- hand-computed table ----------------------------------------------

    def test_e_cap_c_t_a_t_exact_on_a_hand_table(self):
        # one row: w=10, M=2 of T=4 -> 10 * (1 - 2/4) = 5 ; C_t = 1 - 5/10 = 0.5
        rows = [row(id="one", weight_w=10, maturity_M0_5=2, target_M_2031=4,
                    automation_band="A1")]
        self.assertEqual(CV.e_cap(rows), Decimal("5"))
        self.assertEqual(CV.c_t(rows), Decimal("0.5"))
        self.assertEqual(CV.a_t(rows), Decimal("1"))
        # A3/A4/manual earn no automation credit
        self.assertEqual(CV.a_t([row(automation_band="A3"),
                                 row(id="two", automation_band="A4"),
                                 row(id="three", automation_band="manual"),
                                 row(id="four", automation_band="A2")]),
                         Decimal("0.25"))

    def test_fixture_values_and_week_over_week_delta(self):
        self.assertEqual(CV.e_cap(self.prev), Decimal("9"))
        self.assertEqual(CV.c_t(self.prev), Decimal("0.1"))
        self.assertEqual(CV.a_t(self.prev), Decimal("0.1"))
        self.assertEqual(CV.e_cap(self.cur), Decimal("7"))
        self.assertEqual(CV.c_t(self.cur), Decimal("0.3"))
        self.assertEqual(CV.a_t(self.cur), Decimal("0.5"))
        self.assertGreater(CV.c_t(self.cur) - CV.c_t(self.prev), 0)
        self.assertGreaterEqual(CV.a_t(self.cur) - CV.a_t(self.prev), 0)

    def test_maturity_never_exceeds_target(self):
        # over-built row (M=5 vs T=2) contributes 0, not negative debt
        rows = [row(weight_w=5, maturity_M0_5=5, target_M_2031=2)]
        self.assertEqual(CV.e_cap(rows), Decimal("0"))
        self.assertEqual(CV.c_t(rows), Decimal("1"))

    def test_degenerate_targets_contribute_zero_and_are_listed(self):
        rows = [row(id="scored", weight_w=6, maturity_M0_5=2, target_M_2031=4),
                row(id="no_target", weight_w=4, maturity_M0_5=1, target_M_2031=0)]
        degenerate = CV.degenerate_targets(rows)
        self.assertEqual([d["id"] for d in degenerate], ["no_target"])
        self.assertEqual(degenerate[0]["weight_w"], 4)
        # Σw over scored rows only = 6 -> e_cap 3, C_t 0.5; the 4-weight row
        # neither adds debt nor inflates the denominator silently
        self.assertEqual(CV.e_cap(rows), Decimal("3"))
        self.assertEqual(CV.c_t(rows), Decimal("0.5"))
        self.assertEqual(CV.metrics(rows)["rows_scored"], 1)
        self.assertEqual(CV.metrics(rows)["weight_scored"], "6")

    def test_duplicates_are_not_scored_twice(self):
        rows = [row(id="orig", weight_w=4, maturity_M0_5=2, target_M_2031=4),
                row(id="shadow", weight_w=4, maturity_M0_5=2, target_M_2031=4,
                    duplicate_of="orig")]
        self.assertEqual(CV.metrics(rows)["rows_active"], 1)
        self.assertEqual(CV.c_t(rows), CV.c_t(rows[:1]))
        self.assertEqual(CV.a_t(rows), CV.a_t(rows[:1]))

    def test_empty_register_scores_zero_never_divides(self):
        self.assertEqual(CV.e_cap([]), Decimal("0"))
        self.assertEqual(CV.c_t([]), Decimal("0"))
        self.assertEqual(CV.a_t([]), Decimal("0"))
        self.assertEqual(CV.metrics([])["rows_scored"], 0)

    # -- RobustMADZ --------------------------------------------------------

    def test_robust_madz_known_value(self):
        z, flag = CV.robust_madz(4, [1, 2, 3, 4, 5], crosscheck=False)
        self.assertAlmostEqual(z, 0.6745, places=9)
        self.assertEqual(flag, "ok")
        z2, flag2 = CV.robust_madz(12, [1, 2, 3, 4, 5], crosscheck=False)
        self.assertAlmostEqual(z2, 0.6745 * 9, places=8)
        self.assertEqual(flag2, "deep_review")
        self.assertGreaterEqual(abs(z2), CV.MADZ_DEEP_REVIEW_SIGMA)

    def test_robust_madz_zero_mad_and_no_baseline(self):
        self.assertEqual(CV.robust_madz(9, [2, 2, 2], crosscheck=False),
                         (0.0, "mad_zero"))
        self.assertEqual(CV.robust_madz(9, [], crosscheck=False),
                         (0.0, "no_baseline"))

    def test_robust_madz_crosscheck_is_advisory_only(self):
        with mock.patch("rig_capabilities.convergence.shutil.which",
                        return_value=None):
            self.assertEqual(CV.robust_madz(4, [1, 2, 3, 4, 5])[1], "ok")
        with mock.patch("rig_capabilities.convergence._rig_math_exec",
                        return_value=99.0):
            z, flag = CV.robust_madz(4, [1, 2, 3, 4, 5])
        self.assertAlmostEqual(z, 0.6745, places=9)   # local value kept
        self.assertEqual(flag, "BLOCKED_DEEP_REVIEW")
        with mock.patch("rig_capabilities.convergence._rig_math_exec",
                        return_value=0.6745):
            self.assertEqual(CV.robust_madz(4, [1, 2, 3, 4, 5])[1], "ok")

    def test_maturity_jump_and_c_t_flags(self):
        prev = [row(id="cap", maturity_M0_5=1)]
        cur = [row(id="cap", maturity_M0_5=4)]
        flags = CV.maturity_jump_flags(prev, cur)
        self.assertEqual(flags[0]["capability"], "cap")
        self.assertEqual(flags[0]["levels"], 3)
        self.assertEqual(CV.maturity_jump_flags([row(id="cap", maturity_M0_5=1)],
                                                [row(id="cap", maturity_M0_5=2)]),
                         [])
        self.assertEqual(CV.c_t_madz_flags(["1", "2", "1", "2"], "99")[0]["flag"],
                         "deep_review")
        self.assertEqual(CV.c_t_madz_flags(["1"], "99"), [])

    # -- weekly gate -------------------------------------------------------

    def test_weekly_gate_pass(self):
        gate = CV.weekly_gate(self.prev, self.cur, [], self.bookings,
                              unclassified_rate="0.05", week="2026-W36")
        self.assertEqual(gate["verdict"], "PASS")
        self.assertEqual(gate["causes"], [])
        self.assertEqual(gate["d_c_t"], "0.20")
        self.assertEqual(gate["d_a_t"], "0.4")
        self.assertEqual(gate["bookings"], 2)
        self.assertTrue(all(gate["checks"].values()))

    def test_weekly_gate_accepts_precomputed_metrics(self):
        gate = CV.weekly_gate({"c_t": "0.1", "a_t": "0.1"},
                              {"c_t": "0.3", "a_t": "0.5"}, [],
                              {"count": 1}, unclassified_rate=Decimal("0.05"))
        self.assertEqual(gate["verdict"], "PASS")

    def test_no_prior_sealed_week_is_baseline_only(self):
        gate = CV.weekly_gate(None, self.cur, [], self.bookings,
                              unclassified_rate="0.05")
        self.assertEqual(gate["verdict"], "BASELINE_ONLY")
        self.assertFalse(gate["checks"]["prior_sealed_week"])
        self.assertIsNone(gate["d_c_t"])
        # a baseline is never a dC PASS, even with everything else green
        self.assertNotEqual(gate["verdict"], "PASS")

    def test_zero_booking_week_fails_naming_the_row(self):
        gate = CV.weekly_gate(self.prev, self.cur, [], self.zero,
                              unclassified_rate="0.05")
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("booked_qualified_conversations", gate["causes"])
        self.assertEqual(gate["bookings"], 0)

    def test_regressing_a_t_fails(self):
        cur = [row(maturity_M0_5=2, automation_band="A3", weight_w=4),
              row(id="done_test_executor", weight_w=1, maturity_M0_5=2,
                  target_M_2031=2, automation_band="A4"),
              booked()]
        gate = CV.weekly_gate(self.prev, cur, [], self.bookings,
                              unclassified_rate="0.05")
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("a_t_regressing", gate["causes"])

    def test_flat_c_t_fails(self):
        gate = CV.weekly_gate(self.cur, self.cur, [], self.bookings,
                              unclassified_rate="0.05")
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("c_t_not_improving", gate["causes"])

    def test_unclassified_rate_blocks_and_unreported_never_passes(self):
        over = CV.weekly_gate(self.prev, self.cur, [], self.bookings,
                              unclassified_rate="0.15")
        self.assertEqual(over["verdict"], "FAIL")
        self.assertIn("unclassified_rate_above_halt", over["causes"])
        unknown = CV.weekly_gate(self.prev, self.cur, [], self.bookings)
        self.assertEqual(unknown["verdict"], "FAIL")
        self.assertIn("unclassified_rate_unreported", unknown["causes"])

    def test_unresolved_deep_review_flag_blocks_pass(self):
        flags = [{"capability": "capability_catalog_index", "z": "6.2",
                  "flag": "deep_review", "resolved": False}]
        gate = CV.weekly_gate(self.prev, self.cur, flags, self.bookings,
                              unclassified_rate="0.05")
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("madz_deep_review:capability_catalog_index", gate["causes"])
        # resolved, or below 5 sigma, does not
        flags[0]["resolved"] = True
        self.assertEqual(CV.weekly_gate(self.prev, self.cur, flags,
                                        self.bookings,
                                        unclassified_rate="0.05")["verdict"],
                         "PASS")
        flags[0].update(resolved=False, z="4.9", flag="ok")
        self.assertEqual(CV.weekly_gate(self.prev, self.cur, flags,
                                        self.bookings,
                                        unclassified_rate="0.05")["verdict"],
                         "PASS")

    def test_three_consecutive_fails_rebuild_the_loop(self):
        history = [{"week": "2026-W34", "verdict": "FAIL", "c_t": "0.05",
                    "bookings": 1},
                   {"week": "2026-W35", "verdict": "FAIL", "c_t": "0.08",
                    "bookings": 1}]
        gate = CV.weekly_gate(self.prev, self.cur, [], self.zero,
                              unclassified_rate="0.05", history=history)
        self.assertEqual(gate["verdict"], "LOOP_REBUILD_REQUIRED")
        self.assertIn("LOOP_REBUILD_REQUIRED", gate["escalations"])
        self.assertEqual(gate["fail_streak"], 3)
        two = CV.weekly_gate(self.prev, self.cur, [], self.zero,
                             unclassified_rate="0.05", history=history[:1])
        self.assertEqual(two["verdict"], "FAIL")
        self.assertEqual(two["fail_streak"], 2)

    def test_three_c_t_rises_with_zero_bookings_invalidates_weights(self):
        history = [{"verdict": "PASS", "c_t": c, "bookings": 0}
                   for c in ("0.05", "0.08", "0.10")]
        gate = CV.weekly_gate(self.prev, self.cur, [], self.zero,
                              unclassified_rate="0.05", history=history)
        self.assertEqual(gate["verdict"], "WEIGHTS_INVALID")
        self.assertIn("WEIGHTS_INVALID", gate["escalations"])
        self.assertEqual(gate["zero_booking_rise_streak"], 3)

    # -- score_week (corpus seam is always stubbed) ------------------------

    def test_score_week_refuses_to_score_past_the_halt(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        refusal = CV._corpus_refusal()
        with mock.patch.object(CV, "corpus_report",
                               return_value={"unclassified_rate": 0.5,
                                             "unique": 20, "ok": False}):
            with self.assertRaises(refusal) as ctx:
                CV.score_week(root)
        self.assertIn("unclassified_rate_above_halt", str(ctx.exception))

    def test_score_week_scores_a_clean_corpus(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT),
                        bookings={"week": "2026-W36", "records": []})
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            scored = CV.score_week(root, week="2026-W36")
        self.assertEqual(scored["corpus"]["unclassified_rate"], "0.05")
        self.assertEqual(scored["gate"]["verdict"], "BASELINE_ONLY")
        self.assertEqual(scored["gate"]["bookings"], 0)
        self.assertEqual(scored["metrics"]["c_t"],
                         str(CV.c_t(R.load_register(REPO_ROOT))))
        self.assertEqual(scored["previous_metrics"], None)
        json.dumps(scored)                      # the whole packet is JSON-safe

    def test_score_week_uses_the_bookings_artifact_for_the_week(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT),
                        bookings={"week": "2026-W36", "records": [
                            {"id": "b1", "date": "2026-09-01",
                             "account": "fixture", "source_record_id": "s1",
                             "qualification_evidence_path":
                                 "capability_register.csv"}]})
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            scored = CV.score_week(root, week="2026-W36")
        self.assertEqual(scored["bookings"]["count"], 1)

    # -- the weekly driver -------------------------------------------------

    def test_week_id_is_iso(self):
        self.assertEqual(realign.week_id(date(2026, 9, 1)), "2026-W36")
        self.assertEqual(realign.week_id(datetime(2026, 9, 1, 23, 59)),
                         "2026-W36")
        self.assertEqual(realign.week_id("2026-09-01"), "2026-W36")
        self.assertRegex(realign.week_id(), r"^\d{4}-W\d{2}$")

    def test_dry_run_writes_nothing(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            res = realign.run_week(root, "2026-W36", apply=False)
        self.assertTrue(res["dry_run"])
        self.assertFalse(res["wrote"])
        self.assertFalse(res["sealed"])
        self.assertEqual(list((root / ".context").rglob("*")), [])
        self.assertEqual(len(res["would_write"]), 5)

    def test_run_week_writes_the_five_artifacts_unsealed(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            res = realign.run_week(root, "2026-W36", apply=True)
        base = root / ".context" / "realign" / "2026-W36"
        self.assertFalse(res["sealed"])
        self.assertEqual(res["verdict"], "BASELINE_ONLY")
        self.assertEqual(sorted(res["artifacts"]), sorted([
            ".context/realign/2026-W36/convergence_report.md",
            ".context/realign/2026-W36/doctrine-update-phrase.md",
            ".context/realign/2026-W36/operators-weekly.md",
            ".context/realign/2026-W36/proof",
            ".context/realign/2026-W36/register-diff.json"]))
        for name in ("convergence_report.md", "doctrine-update-phrase.md",
                     "operators-weekly.md"):
            self.assertGreater(len((base / name).read_text()), 120)
        proofs = sorted(p.name for p in (base / "proof").glob("*.json"))
        self.assertEqual(proofs, ["bookings.json", "convergence.json",
                                  "register-rows.json", "register-validation.json",
                                  "weekly-gate.json"])
        for name in proofs:
            json.loads((base / "proof" / name).read_text())
        exact = json.loads((base / "proof" / "convergence.json").read_text())["exact"]
        self.assertEqual(Decimal(exact["c_t"]), CV.c_t(R.load_register(REPO_ROOT)))
        report = (base / "convergence_report.md").read_text()
        self.assertIn("BASELINE_ONLY", report)
        self.assertIn("sealed: false", report.lower())
        self.assertIn("booked_qualified_conversations",
                      (base / "doctrine-update-phrase.md").read_text()
                      + report)   # the zero-booking cause is named, not hidden

    def test_second_week_is_not_a_baseline_anymore(self):
        root = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            realign.run_week(root, "2026-W36", apply=True)
            later = realign.run_week(root, "2026-W37", apply=True)
        self.assertNotEqual(later["verdict"], "BASELINE_ONLY")
        self.assertEqual(later["prior_weeks"], ["2026-W36"])
        self.assertIn("c_t_not_improving", later["causes"])   # same register

    def test_run_week_refuses_an_invalid_register(self):
        rows = R.load_register(REPO_ROOT)
        victim = next(r["id"] for r in rows if r["id"] != R.BOOKED_ID)
        root = tmp_repo(rows=[{**r, "evidence_paths": []} if r["id"] == victim
                              else r for r in rows])
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            res = realign.run_week(root, "2026-W36", apply=True)
        self.assertEqual(res["verdict"], "REGISTER_INVALID")
        self.assertFalse(res.get("wrote", False))
        self.assertEqual(list((root / ".context").rglob("*")), [])

    def test_run_week_without_the_booked_row_is_invalid(self):
        root = tmp_repo(rows=[row()])
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        res = realign.run_week(root, "2026-W36", apply=True)
        self.assertEqual(res["verdict"], "REGISTER_INVALID")
        self.assertIn("booked_qualified_conversations", res["reason"])

    def test_run_week_survives_a_dying_corpus(self):
        """A corpus scan that dies on a mounted root must not take the driver
        down: the rate reads as unreported, which never PASSes."""
        root = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            realign.run_week(root, "2026-W36", apply=True)      # the baseline
        with mock.patch.object(CV, "corpus_report",
                               side_effect=TimeoutError("mount went away")):
            res = realign.run_week(root, "2026-W37", apply=True)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertIn("unclassified_rate_unreported", res["causes"])
        self.assertTrue((root / ".context/realign/2026-W37/"
                         "convergence_report.md").is_file())
        # with no baseline yet, the same failure is honestly BASELINE_ONLY
        fresh = tmp_repo(rows=R.load_register(REPO_ROOT))
        self.addCleanup(shutil.rmtree, fresh, ignore_errors=True)
        with mock.patch.object(CV, "corpus_report",
                               side_effect=OSError("no such root")):
            first = realign.run_week(fresh, "2026-W36", apply=True)
        self.assertEqual(first["verdict"], "BASELINE_ONLY")
        self.assertIn("unclassified_rate_unreported", first["causes"])





class SealingTests(unittest.TestCase):
    """V52: a week is sealed with a recomputable hash, or it is honestly unsealed.

    `sealed: false` used to carry the reason "afproof_not_landed (P7)". V48 landed
    `afproof`, which turned that sentence into a false claim sitting inside the week's
    own artifacts. Sealing is now real and explicit, and every rung of it is checked
    against bytes on disk — including the rung that says a seal must survive tampering.
    """

    def setUp(self):
        self.root = tmp_repo(rows=[row(), booked()])
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.proof_root = Path(tempfile.mkdtemp(prefix="f31-proof-"))
        self.addCleanup(shutil.rmtree, self.proof_root, ignore_errors=True)
        os.environ["RIG_PROOF_ROOT"] = str(self.proof_root)
        self.addCleanup(os.environ.pop, "RIG_PROOF_ROOT", None)
        self.base = self.root / ".context" / "realign" / "2026-W36"

    def _run(self, **over):
        with mock.patch.object(CV, "corpus_report", return_value=dict(CORPUS_CLEAN)):
            return realign.run_week(self.root, "2026-W36", apply=True, **over)

    def test_unsealed_run_names_the_step_not_the_missing_module(self):
        res = self._run()
        self.assertFalse(res["sealed"])
        self.assertEqual(res["seal_reason"], realign.SEAL_PENDING)
        self.assertNotIn("P7", res["seal_reason"])
        prose = (self.base / "operators-weekly.md").read_text(encoding="utf-8")
        self.assertIn("sealed: false", prose)
        self.assertNotIn("P7 pending", prose)
        for doc in self.base.rglob("*.json"):
            self.assertNotIn('"sealed": true', doc.read_text(encoding="utf-8"))

    def test_seal_lands_a_hash_the_chain_recomputes(self):
        res = self._run(seal=True)
        self.assertTrue(res["sealed"], res.get("seal_reason"))
        self.assertEqual(res["seal_reason"], "sealed")
        receipt = json.loads((self.base / "proof" / "sealing.json")
                             .read_text(encoding="utf-8"))
        self.assertTrue(receipt["sealed"])
        self.assertEqual(receipt["proof_hash"], res["proof_hash"])
        self.assertGreaterEqual(len(receipt["artifacts"]), 5)
        for entry in receipt["artifacts"]:
            path = self.base / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             entry["sha256"], entry["path"])
        packets = list((self.proof_root / "fable2031").glob("realign-2026-W36__*.json"))
        self.assertEqual(len(packets), 1)
        ok, why = afproof.verify_seal(json.loads(packets[0].read_text()))
        self.assertTrue(ok, why)

    def test_the_receipt_binds_the_artifact_bytes(self):
        """Tamper an artifact after sealing: the recorded hash stops matching."""
        self._run(seal=True)
        report = self.base / "convergence_report.md"
        receipt = json.loads((self.base / "proof" / "sealing.json")
                             .read_text(encoding="utf-8"))
        entry = [a for a in receipt["artifacts"]
                 if a["path"] == "convergence_report.md"][0]
        report.write_text(report.read_text(encoding="utf-8") + "\nREWRITTEN\n",
                          encoding="utf-8")
        self.assertNotEqual(hashlib.sha256(report.read_bytes()).hexdigest(),
                            entry["sha256"])

    def test_seal_failure_writes_no_receipt_and_says_so(self):
        with mock.patch.object(afproof, "seal_packet",
                               side_effect=RuntimeError("proof root read-only")):
            res = self._run(seal=True)
        self.assertFalse(res["sealed"])
        self.assertIn("seal_failed:RuntimeError", res["seal_reason"])
        self.assertNotIn("proof_hash", res)
        self.assertFalse((self.base / "proof" / "sealing.json").exists())
        self.assertTrue(res["wrote"])
        self.assertTrue((self.base / "convergence_report.md").is_file())


if __name__ == "__main__":
    unittest.main()