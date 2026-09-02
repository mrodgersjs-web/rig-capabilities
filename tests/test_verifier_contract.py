"""The validator output contract must LOAD, must hold, and must be able to fail.

Two separate failures are guarded here, because the second one hid the first:

1. VISIBILITY — `catalog._pick_main_text` reads HEAD_BYTES (4096). This asset's
   gates once lived as ~8.6 KB of inline programs inside frontmatter, so the
   catalog parsed an empty quality block and `test` reported pass=false with
   zero results. A contract no agent can load is not a contract, so the byte
   budget is asserted before anything else.
2. NON-VACUITY — every guard here is shown RED on a planted defect, including
   the checker itself: weakening a rule is proven to change the verdict.

Run: python3 -m unittest tests.test_verifier_contract -v
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rig_capabilities import catalog  # noqa: E402

DOC_REL = "capabilities/loops/doer-checker-validator.md"
CHECKER = REPO / "capabilities" / "loops" / "verifier_contract_check.py"
FIX = REPO / "tests" / "fixtures" / "fable2031"


def checker():
    spec = importlib.util.spec_from_file_location("verifier_contract_check", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CK = checker()
DOC = (REPO / DOC_REL).read_text()
FX = {"clean": "verifier-report-clean.json", "looks_good": "verifier-report-looks-good.json",
      "same_family": "verifier-report-same-family.json",
      "single_run": "verifier-report-single-run.json"}


class Visibility(unittest.TestCase):
    """The gate that failed first: bytes the loader can actually see."""

    def test_frontmatter_fits_the_head_the_loader_reads(self):
        self.assertTrue(DOC.startswith("---"), "asset must open with a fence")
        fm_end = DOC.find("\n---", 3)
        self.assertGreater(fm_end, 0, "frontmatter fence never closes")
        self.assertLess(fm_end, catalog.HEAD_BYTES,
                        f"frontmatter ends at byte {fm_end}, past HEAD_BYTES="
                        f"{catalog.HEAD_BYTES}; the quality block is truncated away. "
                        "Move programs into the checker the cmd: lines invoke.")

    def test_quality_block_loads_through_the_real_loader(self):
        """Not a copy of the parse — the parse `_pick_main_text` feeds it."""
        q = catalog._quality_block(catalog._pick_main_text(REPO / DOC_REL))
        for field in ("outcome", "done_when", "great_example", "quality_floor"):
            self.assertTrue(q.get(field), f"{field} invisible to the catalog")
        self.assertGreaterEqual(len(q["done_when"]), 12,
                                "guards disappeared from the loaded block")
        self.assertEqual(CK.visibility(REPO / DOC_REL), [],
                         "the checker reports its own host asset unloadable")

    def test_visibility_rule_fires_when_the_head_is_too_short(self):
        """The visibility rule must be able to go RED, not just sit green."""
        saved = catalog.HEAD_BYTES
        try:
            catalog.HEAD_BYTES = 64          # every real frontmatter is longer
            self.assertTrue([f for f in ("outcome", "done_when", "great_example",
                                         "quality_floor")
                             if not catalog._quality_block(
                                 catalog._pick_main_text(REPO / DOC_REL)).get(f)],
                            "with a 64-byte head the loader must lose the block; "
                            "if it doesn't, this guard can never fire")
        finally:
            catalog.HEAD_BYTES = saved


class ContractHolds(unittest.TestCase):
    def test_the_document_satisfies_its_own_contract(self):
        self.assertEqual(CK.check_contract(DOC, str(REPO / DOC_REL)), [])

    def test_every_declared_slot_is_a_schema_key(self):
        L = DOC.splitlines()
        keys = {l.strip().strip('"').split('"')[0] for l in L
                if l.lstrip().startswith('"')}
        self.assertEqual([s for s in CK.SLOTS if s not in keys], [])

    def test_every_label_has_its_own_router_row_with_a_consumer(self):
        for lab in CK.LABELS:
            own = [l for l in DOC.splitlines() if l.startswith(f"| `{lab}`")]
            self.assertTrue(own, f"{lab} has no router row")
            self.assertTrue(any("route:" in r for r in own), f"{lab} routes nowhere")


class DocumentPlants(unittest.TestCase):
    """Each mutation removes exactly one thing and must be caught."""

    def test_all_eight_doc_plants_are_caught(self):
        escaped = [n for n in sorted(CK.DOC_PLANTS)
                   if not CK.check_contract("\n".join(CK.mutate(DOC.splitlines(), n)))]
        self.assertEqual(escaped, [])
        self.assertEqual(len(CK.DOC_PLANTS), 8, "a doc plant disappeared")

    def test_each_plant_names_the_rule_it_breaks(self):
        expect = {
            "schema_key": "what_would_change_verdict@schema",
            "router_row": "evaluator-gap@route",
            "law_line": "NOT-A-VERDICT@rule",
            "marker_renamed": "NOT-A-VERDICT@rule",
            "slots_declaration": "slots@declaration",
            "labels_declaration": "labels@declaration",
            "negative_declaration": "negative@declaration",
        }
        for name, reason in expect.items():
            missing = CK.check_contract("\n".join(CK.mutate(DOC.splitlines(), name)))
            self.assertIn(reason, missing, f"{name} escaped or misreported: {missing}")


class ReportRules(unittest.TestCase):
    def test_clean_reports_count_as_verdicts(self):
        for i, rep in enumerate(CK.CLEAN):
            self.assertEqual(CK.check_report(rep), [], f"clean report {i} refused")

    def test_all_ten_report_plants_refused_for_exactly_one_reason(self):
        for name, (patch, reason) in sorted(CK.PLANTED.items()):
            bad = CK.check_report(dict(CK.CLEAN[0], **patch))
            self.assertEqual(bad, [reason], f"report plant {name} misjudged")
        self.assertEqual(len(CK.PLANTED), 10)

    def test_shipped_fixtures_match_the_rules(self):
        import json
        expect = {"clean": [], "looks_good": ["outcome_label_outside_vocabulary"],
                  "same_family": ["same_family_collusion"],
                  "single_run": ["attempts_below_declared_k"]}
        for name, want in expect.items():
            rep = json.loads((FIX / FX[name]).read_text())
            self.assertEqual(CK.check_report(rep), want, f"fixture {name} disagrees")


class CheckerIsNotTheater(unittest.TestCase):
    """A checker that cannot be weakened cannot be trusted. Weaken it on purpose."""

    def test_off_vocabulary_label_passes_when_the_vocabulary_is_widened(self):
        saved = CK.LABELS
        try:
            CK.LABELS = saved + ("looks_good",)
            self.assertEqual(CK.check_report(dict(CK.CLEAN[0], verdict="looks_good")), [],
                            "the label rule is not actually reading LABELS")
        finally:
            CK.LABELS = saved

    def test_law_rule_misses_a_marker_the_document_does_not_use(self):
        saved = CK.MARKER
        try:
            CK.MARKER = "NOT-A-VERDICT-TOMORROW"
            missing = CK.check_contract(DOC)
            self.assertIn("NOT-A-VERDICT-TOMORROW@rule", missing)
        finally:
            CK.MARKER = saved


class SelfTest(unittest.TestCase):
    def test_self_test_returns_zero(self):
        self.assertEqual(CK.self_test(DOC, str(REPO / DOC_REL)), 0)

    def test_self_test_catches_a_gutted_rule_table(self):
        saved = dict(CK.PLANTED)
        try:
            CK.PLANTED.clear()
            self.assertEqual(CK.self_test(DOC, str(REPO / DOC_REL)), 2,
                             "an empty plant table must not pass self-test")
        finally:
            CK.PLANTED.update(saved)


class LoadedGuardsAreRunnable(unittest.TestCase):
    """Every loaded guard must be a real form, not prose that reads like one."""

    def test_no_loaded_guard_is_unrunnable(self):
        from rig_capabilities.done_tests import parse_form
        q = catalog._quality_block(catalog._pick_main_text(REPO / DOC_REL))
        unknown = [e for e in q["done_when"] if parse_form(str(e))[0] == "unknown"]
        self.assertEqual(unknown, [])


if __name__ == "__main__":
    unittest.main()
