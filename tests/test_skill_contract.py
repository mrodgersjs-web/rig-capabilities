"""Tests for the six-slot skill contract (rig_capabilities.skill_contract).

The claim under test: a SKILL.md contract violation is reported with the RIGHT
one of three verdicts — ABSENT (never written), EMPTY (written, no value),
MALFORMED (wrong shape) — and the three are mutually distinguishable. An
implementation that collapses any pair passes every descriptive reading of the
contract and fails these tests, which is the point: the EMPTY case ("key typed,
value never filled in") is the most common authoring bug and must not be
mislabelled as ABSENT, and a malformed slot must not read as an absent one.

Fixtures under examples/fixtures/skill-contract/ are the fixtures under test —
one complete (exit 0), one per bad case (exit 1). Tests address the fixtures by
verdict, not by line count.
"""

import contextlib
import io
import unittest
from pathlib import Path

from rig_capabilities import skill_contract as sc

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "examples" / "fixtures" / "skill-contract"

SLOT_NAMES = [s[0] for s in sc.SLOTS]


def _verdicts(path: Path) -> dict:
    return {r["slot"]: r["verdict"]
            for r in sc.slot_verdicts(
                sc.parse_doc(path.read_text(encoding="utf-8"), path.name))}


def _rows(text: str) -> dict:
    return {r["slot"]: r for r in sc.slot_verdicts(sc.parse_doc(text, "t.md"))}


def _findings(path: Path) -> list:
    return sc.findings_for_text(str(path), path.read_text(encoding="utf-8"))


def _main(argv: list) -> tuple:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sc.main(argv)
    return rc, out.getvalue(), err.getvalue()


class CleanCase(unittest.TestCase):
    def test_complete_fixture_has_no_findings(self):
        self.assertEqual(_findings(FIX / "complete.md"), [])

    def test_complete_fixture_exit_zero(self):
        rc, out, _ = _main([str(FIX / "complete.md")])
        self.assertEqual(rc, 0)
        self.assertIn("0 finding(s)", out)

    def test_every_slot_ok_on_complete(self):
        text = (FIX / "complete.md").read_text(encoding="utf-8")
        rows = _rows(text)
        self.assertEqual(sorted(rows), sorted(SLOT_NAMES))
        for slot, row in rows.items():
            self.assertEqual(row["verdict"], sc.OK, slot)


class VerdictClasses(unittest.TestCase):
    """Each of the three verdict classes, proven on its own fixture."""

    def test_absent_verdict(self):
        rows = _verdicts(FIX / "bad" / "activation_absent.md")
        self.assertEqual(rows["activation"], sc.ABSENT)
        self.assertEqual([s for s, v in rows.items() if v != sc.OK],
                         ["activation"])

    def test_empty_verdict(self):
        rows = _verdicts(FIX / "bad" / "activation_empty.md")
        self.assertEqual(rows["activation"], sc.EMPTY)
        self.assertEqual([s for s, v in rows.items() if v != sc.OK],
                         ["activation"])

    def test_malformed_verdicts(self):
        self.assertEqual(
            _verdicts(FIX / "bad" / "permissions_scalar.md")["permissions"],
            sc.MALFORMED)
        self.assertEqual(
            _verdicts(FIX / "bad" / "applies_when_partial.md")["applies_when"],
            sc.MALFORMED)
        self.assertEqual(
            _verdicts(FIX / "bad" / "flow_single_step.md")["flow"],
            sc.MALFORMED)

    def test_all_three_classes_present_in_bad_corpus(self):
        verdicts = {f["verdict"] for f in sc.findings_for_tree(FIX / "bad")}
        self.assertEqual(verdicts, {sc.ABSENT, sc.EMPTY, sc.MALFORMED})


class VerdictsDoNotCollapse(unittest.TestCase):
    """The guard the plant-failure targets: three verdicts, not one."""

    def test_absent_and_empty_are_different_verdicts(self):
        a = _verdicts(FIX / "bad" / "activation_absent.md")["activation"]
        e = _verdicts(FIX / "bad" / "activation_empty.md")["activation"]
        self.assertNotEqual(a, e)
        self.assertEqual({a, e}, {sc.ABSENT, sc.EMPTY})

    def test_malformed_is_neither_absent_nor_empty(self):
        rows = _verdicts(FIX / "bad" / "permissions_scalar.md")
        self.assertEqual(rows["permissions"], sc.MALFORMED)
        # the slot was WRITTEN with content — reporting it ABSENT or EMPTY
        # would misdirect the fix from "reshape" to "write it"
        text = (FIX / "bad" / "permissions_scalar.md").read_text("utf-8")
        self.assertIn("permissions: Read", text)

    def test_details_differ_between_absent_and_empty(self):
        a = _rows((FIX / "bad" / "activation_absent.md").read_text("utf-8"))
        e = _rows((FIX / "bad" / "activation_empty.md").read_text("utf-8"))
        self.assertNotEqual(a["activation"]["detail"],
                            e["activation"]["detail"])


class SlotRules(unittest.TestCase):
    def test_no_frontmatter_is_every_slot_absent(self):
        findings = _findings(FIX / "bad" / "no_frontmatter.md")
        self.assertEqual(len(findings), len(SLOT_NAMES))
        self.assertEqual({f["verdict"] for f in findings}, {sc.ABSENT})

    def test_done_when_scalar_is_malformed(self):
        text = (FIX / "complete.md").read_text(encoding="utf-8")
        text = text.replace(
            "done_when:\n  - cmd:test -f "
            "examples/fixtures/skill-contract/complete.md\n",
            "done_when: it works when it works\n")
        rows = _rows(text)
        self.assertEqual(rows["done_when"]["verdict"], sc.MALFORMED)

    def test_applies_when_scalar_is_malformed(self):
        text = (FIX / "complete.md").read_text(encoding="utf-8")
        start = text.index("applies_when:")
        end = text.index("permissions:")
        text = text[:start] + "applies_when: only when it applies\n" + text[end:]
        rows = _rows(text)
        self.assertEqual(rows["applies_when"]["verdict"], sc.MALFORMED)

    def test_missing_boundary_fields_are_named(self):
        finding = _findings(FIX / "bad" / "applies_when_partial.md")[0]
        self.assertIn("runtime", finding["detail"])
        self.assertIn("budget", finding["detail"])

    def test_activation_as_list_is_malformed(self):
        text = (FIX / "complete.md").read_text(encoding="utf-8")
        start = text.index("activation:")
        end = text.index("instruction:")
        text = (text[:start] + "activation:\n  - when the build fails\n"
                + text[end:])
        rows = _rows(text)
        self.assertEqual(rows["activation"]["verdict"], sc.MALFORMED)


class ExitCodes(unittest.TestCase):
    def test_bad_dir_exits_one_and_names_the_three_missing_keys(self):
        rc, out, _ = _main([str(FIX / "bad" / "missing_three.md")])
        self.assertEqual(rc, 1)
        for key in ("activation", "applies_when", "permissions"):
            self.assertIn(key, out)

    def test_bad_corpus_exits_one(self):
        rc, out, _ = _main([str(FIX / "bad")])
        self.assertEqual(rc, 1)
        self.assertGreaterEqual(len([ln for ln in out.splitlines()
                                     if ": " in ln]), 8)

    def test_missing_path_exits_two(self):
        rc, _, err = _main([str(FIX / "nope.md")])
        self.assertEqual(rc, 2)
        self.assertIn("no such path", err)

    def test_unsupported_kind_exits_two(self):
        p = FIX / "bad" / "no_frontmatter.md"
        rc, _, err = _main([str(p)[:-3] + ".xyz"])
        self.assertEqual(rc, 2)


class LoaderGate(unittest.TestCase):
    """The loader may only load assets whose A and C are complete."""

    def test_complete_asset_is_loadable(self):
        ok, blockers = sc.loadable(FIX / "complete.md")
        self.assertTrue(ok)
        self.assertEqual(blockers, [])

    def test_missing_activation_blocks_loading(self):
        ok, blockers = sc.loadable(FIX / "bad" / "activation_absent.md")
        self.assertFalse(ok)
        self.assertIn("activation:ABSENT", blockers)

    def test_malformed_applicability_blocks_loading(self):
        ok, blockers = sc.loadable(FIX / "bad" / "applies_when_partial.md")
        self.assertFalse(ok)
        self.assertIn("applies_when:MALFORMED", blockers)

    def test_other_slot_failures_do_not_block_loading(self):
        # permissions is malformed but A and C are complete: not loadable is
        # a policy elsewhere; the A+C gate itself must not name P.
        ok, blockers = sc.loadable(FIX / "bad" / "permissions_scalar.md")
        self.assertTrue(ok)
        self.assertEqual(blockers, [])


if __name__ == "__main__":
    unittest.main()
