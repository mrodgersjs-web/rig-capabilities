"""ExpertOsTests + EvidenceLedgerTests: the Known Expert OS harness and its Evidence Ledger."""
from __future__ import annotations

import csv
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import evidence_ledger as el
from rig_capabilities import expert_os as eo

# Pinned verbatim from the card — a transcription regression must fail here.
TITLES = (
    "Select the problem to own",
    "Reverse-engineer the market and target roles",
    "Mine scars, decisions, and proof",
    "Construct the category point of view",
    "Create signature intellectual property",
    "Build the guinea-pig reference implementation",
    "Convert positioning into résumé evidence",
    "Engineer the interview system",
    "Build the searchable expertise architecture",
    "Run the 90-day MAP deployment",
    "Turn the system into the RIG offering",
)
GATE_1 = ("Advance only with an identifiable economic buyer, costly status quo, observable "
          "transformed state, credible evidence alignment, and a path to demonstration.")
GATE_10 = ("Do not increase volume below the quality threshold, and do not abandon the system "
           "because early audience numbers are small. Optimize for the right 30 people, not "
           "the wrong 30,000.")
VALID_LEDGER = FIX / "evidence-ledger-valid.csv"
BAD_LEDGER = FIX / "evidence-ledger-unverified-resume.csv"


def _row(**over) -> dict:
    row = {"id": "T-1", "claim": "a claim", "evidence": "rig_capabilities/expert_os.py",
           "type": "direct", "confidence": "0.9", "allowed_use": "internal"}
    row.update(over)
    return row


class _Repo:
    """Repo-shaped stand-in: the catalogue hands gates an object with .root."""

    def __init__(self, root):
        self.root = Path(root)


class ExpertOsTests(unittest.TestCase):
    def test_eleven_phases_verbatim(self):
        self.assertEqual(tuple(n for n, _ in eo.PHASES), tuple(range(1, 12)))
        self.assertEqual(tuple(t for _, t in eo.PHASES), TITLES)
        self.assertEqual(len(eo.PHASE_HEADINGS), 11)
        self.assertEqual(eo.PHASE_HEADINGS[0], "# Phase 1 — Select the problem to own")

    def test_phase_status_truncation_honesty(self):
        for n in range(1, 11):
            self.assertEqual(eo.PHASE_STATUS[n], "gated")
        self.assertEqual(eo.PHASE_STATUS[11], "objective_only_truncated")
        self.assertEqual(eo.PHASE_STATUS[12], "absent_at_source")
        self.assertEqual(sorted(eo.PHASE_STATUS), list(range(1, 13)))

    def test_gates_only_one_to_ten(self):
        self.assertEqual(sorted(eo.GATES), list(range(1, 11)))
        with self.assertRaises(KeyError):
            eo.GATES[11]
        with self.assertRaises(KeyError):
            eo.GATES[12]
        self.assertEqual(eo.GATES[1], GATE_1)
        self.assertEqual(eo.GATES[10], GATE_10)
        for n, gate in eo.GATES.items():
            self.assertTrue(gate.strip(), f"gate {n} is empty")

    def test_phase_11_objective_is_all_the_card_has(self):
        self.assertEqual(eo.PHASE_11_OBJECTIVE,
                         "Translate the validated expertise into a bounded offer.")

    def test_depth_ladder(self):
        self.assertEqual(eo.DEPTH_LEVELS,
                         ("L1_surface", "L2_synthesis", "L3_scar", "L4_judgment", "L5_procedure"))
        self.assertEqual(eo.MIN_PUBLISHABLE_DEPTH, "L3_scar")
        self.assertIn(eo.MIN_PUBLISHABLE_DEPTH, eo.DEPTH_LEVELS)
        self.assertEqual(len(eo.DEPTH_TEXT), 5)

    def test_rules_horizons_cadence(self):
        self.assertEqual(len(eo.NON_NEGOTIABLE_RULES), 15)
        self.assertEqual(eo.NON_NEGOTIABLE_RULES[2],
                         "Never place an unverified claim on a résumé.")
        self.assertEqual(eo.NON_NEGOTIABLE_RULES[-1], "Maintain an Evidence Ledger:")
        self.assertEqual(len(eo.HORIZONS), 3)
        self.assertEqual([h for h, _ in eo.HORIZONS],
                         ["Horizon 1 — Career proof", "Horizon 2 — RIG offering",
                          "Horizon 3 — RIG 2031"])
        self.assertEqual([w for w, _, _ in eo.MAP_CADENCE], ["Weeks 1–2", "Weeks 3–8", "Weeks 9–12"])
        self.assertEqual(eo.MAP_PHASES, ("Mine", "Accelerate", "Position"))

    def test_title_and_slugs(self):
        self.assertEqual(eo.title(7), "Convert positioning into résumé evidence")
        with self.assertRaises(ValueError):
            eo.title(12)
        self.assertEqual(len(eo.deliverable_slugs(1)), 7)
        self.assertEqual(eo.deliverable_slugs(11), ())

    def test_advance_passing_phase(self):
        verdict = eo.advance(1, {s: f"artifacts/{s}.md" for s in eo.deliverable_slugs(1)})
        self.assertTrue(verdict["ok"])
        self.assertEqual(verdict["missing"], [])
        self.assertEqual(verdict["gate"], GATE_1)
        self.assertEqual(verdict["status"], "gated")

    def test_advance_missing_deliverables(self):
        verdict = eo.advance(1, {})
        self.assertFalse(verdict["ok"])
        self.assertEqual(verdict["missing"], list(eo.deliverable_slugs(1)))
        partial = eo.advance(1, {"market_narrative": "n.md"})
        self.assertFalse(partial["ok"])
        self.assertNotIn("market_narrative", partial["missing"])
        self.assertIn("evidence_table", partial["missing"])
        self.assertEqual(partial["gate"], GATE_1)

    def test_advance_every_gated_phase_round_trips(self):
        for n in range(1, 11):
            self.assertTrue(eo.advance(n, {s: 1 for s in eo.deliverable_slugs(n)})["ok"], n)

    def test_advance_never_passes_truncated_or_absent(self):
        for phase, status in ((11, "objective_only_truncated"), (12, "absent_at_source")):
            verdict = eo.advance(phase, {"anything": "x"})
            self.assertFalse(verdict["ok"], phase)
            self.assertEqual(verdict["status"], status)
            self.assertEqual(verdict["gate"], "")
            self.assertEqual(verdict["missing"], [])
        self.assertFalse(eo.advance(11)["ok"])
        self.assertFalse(eo.advance(12)["ok"])

    def test_advance_unknown_phase(self):
        for bad in (0, 13, -1, "nine"):
            with self.assertRaises(ValueError):
                eo.advance(bad, {})

    def test_advance_rejects_non_mapping(self):
        with self.assertRaises(TypeError):
            eo.advance(1, ["market_narrative"])


class EvidenceLedgerTests(unittest.TestCase):
    def test_constants_match_the_card(self):
        self.assertEqual(el.LEDGER_PATH, "evidence_ledger.csv")
        self.assertEqual(el.LEDGER_COLUMNS,
                         ("id", "claim", "evidence", "type", "confidence", "allowed_use"))
        self.assertEqual(el.CLAIM_TYPES, ("direct", "inferred", "planned"))
        self.assertEqual(el.ALLOWED_USES, ("resume", "interview", "content", "internal"))
        self.assertEqual(el.RESUME_MIN_CONFIDENCE, 0.8)

    def test_clean_row_has_no_errors(self):
        self.assertEqual(el.validate_claim(_row(), root=REPO_ROOT), [])
        self.assertEqual(el.validate_claim(_row(type="planned"), root=REPO_ROOT), [])
        self.assertEqual(el.validate_claim(_row(type="inferred", confidence="0.6"), root=REPO_ROOT), [])

    def test_every_missing_field(self):
        for col in el.LEDGER_COLUMNS:
            errors = el.validate_claim(_row(**{col: ""}), root=REPO_ROOT)
            self.assertEqual(errors, [f"missing_field:{col}"], col)

    def test_unknown_type(self):
        self.assertEqual(el.validate_claim(_row(type="asserted"), root=REPO_ROOT),
                         ["unknown_claim_type:asserted"])

    def test_unknown_allowed_use(self):
        self.assertEqual(el.validate_claim(_row(allowed_use="internal;investor;bogus"), root=REPO_ROOT),
                         ["unknown_allowed_use:bogus", "unknown_allowed_use:investor"])
        for use in el.ALLOWED_USES:
            self.assertEqual(el.validate_claim(_row(allowed_use=use), root=REPO_ROOT), [], use)

    def test_confidence_branches(self):
        self.assertEqual(el.validate_claim(_row(confidence="high"), root=REPO_ROOT),
                         ["confidence_not_numeric:high"])
        self.assertEqual(el.validate_claim(_row(confidence="1.4"), root=REPO_ROOT),
                         ["confidence_out_of_range:1.4"])
        self.assertEqual(el.validate_claim(_row(confidence="-0.1"), root=REPO_ROOT),
                         ["confidence_out_of_range:-0.1"])
        for edge in ("0", "1", "0.8"):
            self.assertEqual(el.validate_claim(_row(confidence=edge), root=REPO_ROOT), [], edge)

    def test_rule_3_blocks_resume(self):
        for bad in (_row(type="planned", allowed_use="resume"),
                    _row(type="inferred", allowed_use="resume;interview"),
                    _row(confidence="0.4", allowed_use="resume"),
                    _row(confidence="0.79", allowed_use="resume"),
                    _row(allowed_use="resume", confidence="0.95",
                         evidence="tests/fixtures/fable2031/does-not-exist.md")):
            self.assertEqual(el.validate_claim(bad, root=REPO_ROOT), ["unverified_claim_on_resume"])
        ok = _row(allowed_use="resume", confidence="0.8")
        self.assertEqual(el.validate_claim(ok, root=REPO_ROOT), [])

    def test_evidence_missing_for_non_resume_lane(self):
        self.assertEqual(
            el.validate_claim(_row(evidence="tests/fixtures/fable2031/does-not-exist.md"),
                              root=REPO_ROOT),
            ["evidence_missing"])
        self.assertEqual(el.validate_claim(_row(evidence="rig_capabilities/expert_os.py"),
                                           root=REPO_ROOT), [])

    def test_resume_claims_filters(self):
        rows = el.load_ledger(REPO_ROOT, BAD_LEDGER)
        self.assertEqual([r["id"] for r in el.resume_claims(rows, root=REPO_ROOT)], ["E-203"])
        clean = el.load_ledger(REPO_ROOT, VALID_LEDGER)
        self.assertEqual([r["id"] for r in el.resume_claims(clean, root=REPO_ROOT)], ["E-101"])

    def test_write_load_roundtrip_sorted_and_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [_row(id="E-9", claim="later"), _row(id="E-1", claim="first"),
                    _row(id="E-5", claim="middle", type="planned")]
            el.write_ledger(root, rows)
            raw = (root / el.LEDGER_PATH).read_text(encoding="utf-8").splitlines()
            self.assertEqual(raw[0], ",".join(el.LEDGER_COLUMNS))
            self.assertEqual([r["id"] for r in el.load_ledger(root)], ["E-1", "E-5", "E-9"])
            self.assertEqual(el.load_ledger(root)[1]["claim"], "middle")
            self.assertEqual(el.load_ledger(root)[1]["type"], "planned")
            el.write_ledger(root, [rows[1]])
            self.assertEqual([r["id"] for r in el.load_ledger(root)], ["E-1"])
            self.assertEqual(list(root.glob(f".{el.LEDGER_PATH}.*")), [])
            target = root / el.LEDGER_PATH
            target.chmod(0o640)
            el.write_ledger(root, [rows[0], rows[1]])
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)
            fresh = root / "fresh.csv"
            el.write_ledger(root, rows, fresh)
            self.assertTrue(fresh.is_file())
            mask = os.umask(0)
            os.umask(mask)
            self.assertEqual(stat.S_IMODE(fresh.stat().st_mode), 0o666 & ~mask)

    def test_write_ledger_accepts_repo_object_and_explicit_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "ledger.csv"
            el.write_ledger(_Repo(tmp), [_row(id="E-2"), _row(id="E-1")], target)
            self.assertEqual([r["id"] for r in el.load_ledger(_Repo(tmp), target)], ["E-1", "E-2"])

    def test_load_missing_or_headerless(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(el.load_ledger(root), [])
            (root / el.LEDGER_PATH).write_text("claim,evidence\n", encoding="utf-8")
            rows = el.load_ledger(root)
            self.assertEqual(rows, [])

    def test_card_header_spelling_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "card-shaped.csv"
            path.write_text(
                "ID,Claim,Evidence,Type,Confidence,Allowed use\n"
                "E-1,a direct thing,rig_capabilities/expert_os.py,direct,0.9,résumé\n",
                encoding="utf-8")
            rows = el.load_ledger(REPO_ROOT, path)
            self.assertEqual(len(rows), 1)
            # the card writes the lane as "résumé"; our declared lane is ASCII "resume"
            self.assertEqual(el.validate_claim(rows[0], root=REPO_ROOT),
                             ["unknown_allowed_use:résumé"])

    def test_committed_valid_fixture_is_clean(self):
        rows = el.load_ledger(REPO_ROOT, VALID_LEDGER)
        self.assertGreaterEqual(len(rows), 3)
        for r in rows:
            self.assertEqual(el.validate_claim(r, root=REPO_ROOT), [], r["id"])
        self.assertTrue(all(Path(REPO_ROOT / r["evidence"]).exists() for r in rows))
        self.assertTrue(any("planned" == r["type"] for r in rows),
                        "valid fixture needs a planned row for the plant")

    def test_committed_unverified_fixture_names_rule_3(self):
        rows = el.load_ledger(REPO_ROOT, BAD_LEDGER)
        by_id = {r["id"]: el.validate_claim(r, root=REPO_ROOT) for r in rows}
        self.assertEqual(by_id["E-201"], ["unverified_claim_on_resume"])
        self.assertEqual(by_id["E-202"], ["unverified_claim_on_resume"])
        self.assertEqual(by_id["E-203"], [])
        self.assertEqual(by_id["E-204"], ["unverified_claim_on_resume"])
        self.assertEqual(by_id["E-205"], ["evidence_missing"])
        self.assertEqual(by_id["E-206"], ["unknown_claim_type:asserted"])
        self.assertEqual(by_id["E-207"], ["unknown_allowed_use:investor"])
        self.assertEqual(by_id["E-208"], ["confidence_out_of_range:1.4"])
        self.assertEqual(by_id["E-209"], ["confidence_not_numeric:high"])
        self.assertEqual(by_id["E-210"], ["missing_field:evidence"])

    def test_committed_root_ledger_clears_every_row(self):
        rows = el.load_ledger(REPO_ROOT)
        self.assertGreaterEqual(len(rows), 1)
        for r in rows:
            self.assertEqual(el.validate_claim(r, root=REPO_ROOT), [], r["id"])

    def test_gate_green_on_committed_repo(self):
        ok, detail = el.gate_evidence_ledger(_Repo(REPO_ROOT))
        self.assertTrue(ok, detail)
        self.assertNotIn("unverified_claim_on_resume", detail)

    def test_gate_red_when_planted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / el.FIXTURE_LEDGER.parent).mkdir(parents=True)
            shutil.copy(VALID_LEDGER, root / el.FIXTURE_LEDGER)
            # materialise the evidence targets so the plant is the only possible failure
            for r in el.load_ledger(root, root / el.FIXTURE_LEDGER):
                target = root / r["evidence"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
            self.assertTrue(el.gate_evidence_ledger(root)[0])
            text = (root / el.FIXTURE_LEDGER).read_text(encoding="utf-8")
            (root / el.FIXTURE_LEDGER).write_text(
                text.replace("planned,0.5,internal", "planned,0.5,resume;internal"),
                encoding="utf-8")
            ok, detail = el.gate_evidence_ledger(root)
            self.assertFalse(ok)
            self.assertIn("unverified_claim_on_resume", detail)

    def test_gate_reports_missing_or_unparsable_fixture_without_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, detail = el.gate_evidence_ledger(tmp)
            self.assertFalse(ok)
            self.assertIn("fixture_missing", detail)
            (Path(tmp) / el.FIXTURE_LEDGER.parent).mkdir(parents=True)
            (Path(tmp) / el.FIXTURE_LEDGER).write_text("nope\n", encoding="utf-8")
            ok, detail = el.gate_evidence_ledger(tmp)
            self.assertFalse(ok)
            self.assertIn("header_missing", detail)
            (Path(tmp) / el.FIXTURE_LEDGER).write_text("id,claim,evidence,type,confidence,allowed_use\n",
                                                       encoding="utf-8")
            self.assertEqual(el.gate_evidence_ledger(tmp), (False, "empty_ledger"))


if __name__ == "__main__":
    unittest.main()
