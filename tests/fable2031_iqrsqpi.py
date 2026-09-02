"""IQRSQPI v10 stage-contract tests: alias collapse, order, and the hermetic gate."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities.iqrsqpi_v10 import (  # noqa: E402
    ARTIFACTS, GATE_FIXTURE, STAGES, STAGE_ALIASES, StageError,
    gate_stage_order, normalize_stage, run_pass, stage_order_ok)


class _Repo:
    """Stand-in for catalog.Repo — the runtime only ever wants `.root`."""

    def __init__(self, root: Path) -> None:
        self.root = root


def _write_walk(root: Path, walk_id: str = "fable-2031", *, omit=(),
                claims: dict | None = None) -> Path:
    """Materialise a walk directory with the four v10 artifacts."""
    walk = root / ".context" / "iqrsqpi" / walk_id
    walk.mkdir(parents=True, exist_ok=True)
    bodies = {
        "00-intake": {"artifact": "00-intake", "claims": []},
        "01-reality": {"artifact": "01-reality", "claims": []},
        "02-decision": {"artifact": "02-decision", "claims": []},
        "proof": {"artifact": "proof", "claims": []},
    }
    for name, extra in (claims or {}).items():
        bodies[name]["claims"].append(extra)
    for name, body in bodies.items():
        if name in omit:
            continue
        (walk / f"{name}.json").write_text(json.dumps(body), encoding="utf-8")
    return walk


class IqrsqpiStageTests(unittest.TestCase):
    maxDiff = None

    # ------------------------------------------------------ alias collapse
    def test_every_alias_key_collapses_to_a_canonical_stage(self):
        for token, want in STAGE_ALIASES.items():
            with self.subTest(token=token):
                self.assertIn(want, STAGES)
                self.assertEqual(normalize_stage(token), want)

    def test_both_real_harness_vocabularies_collapse_to_the_canonical_seven(self):
        short = ["I", "Q", "R", "S", "Q2", "P", "I2"]          # hA/hC/hD/mh
        words = ["intake", "question", "research", "synthesize",
                 "quantify", "produce", "iterate"]              # hB
        self.assertEqual([normalize_stage(t) for t in short], list(STAGES))
        self.assertEqual([normalize_stage(t) for t in words], list(STAGES))

    def test_suffixed_rungs_never_collapse_to_their_prefix(self):
        # `I` is Intent; `I2`/`I5` are Integrate. `Q`/`Q1` are Question; `Q2` is Quality.
        self.assertEqual(normalize_stage("I"), "Intent")
        self.assertEqual(normalize_stage("I2"), "Integrate")
        self.assertEqual(normalize_stage("I5"), "Integrate")
        self.assertEqual(normalize_stage("Q"), "Question")
        self.assertEqual(normalize_stage("Q1"), "Question")
        self.assertEqual(normalize_stage("Q2"), "Quality")
        self.assertEqual(normalize_stage("I1"), "Intent")
        self.assertNotEqual(normalize_stage("I2"), normalize_stage("I"))
        self.assertNotEqual(normalize_stage("Q2"), normalize_stage("Q"))

    def test_alias_mid_sequence_is_read_as_itself_not_its_prefix(self):
        seq = ["I", "Q", "R", "S", "Q2", "P", "I2"]
        ok, detail = stage_order_ok(seq)
        self.assertTrue(ok, detail)

    def test_matching_is_case_insensitive_and_trimmed(self):
        for token, want in STAGE_ALIASES.items():
            with self.subTest(token=token):
                self.assertEqual(normalize_stage(f"  {token.upper()}\t"), want)
        self.assertEqual(normalize_stage("  iNtEnT  "), "Intent")
        self.assertEqual(normalize_stage(" i5 "), "Integrate")

    def test_canonical_names_map_to_themselves(self):
        for stage in STAGES:
            with self.subTest(stage=stage):
                self.assertEqual(normalize_stage(stage), stage)
                self.assertEqual(normalize_stage(stage.lower()), stage)

    def test_garbage_unknown_or_empty_tokens_raise(self):
        for token in ("Q3", "I3", "S1", "deliberate", "", "   ", "intent-ish",
                      "synthesise", "P2", "intgrate"):
            with self.subTest(token=token):
                with self.assertRaises(StageError) as ctx:
                    normalize_stage(token)
                self.assertTrue(str(ctx.exception))
        with self.assertRaises(StageError) as ctx:
            normalize_stage(None)
        self.assertEqual(str(ctx.exception), "stage_token_empty")

    def test_alias_table_covers_the_documented_groupings(self):
        want = {"I": "Intent", "I1": "Intent", "intake": "Intent",
                "Q": "Question", "Q1": "Question", "question": "Question",
                "R": "Research", "research": "Research",
                "S": "Solution", "synthesize": "Solution",
                "Q2": "Quality", "quantify": "Quality",
                "P": "Proof", "produce": "Proof",
                "I2": "Integrate", "I5": "Integrate", "iterate": "Integrate"}
        for token, stage in want.items():
            self.assertEqual(STAGE_ALIASES[token.lower()], stage)
        self.assertEqual(ARTIFACTS, ("00-intake", "01-reality", "02-decision",
                                     "proof"))

    # ---------------------------------------------------------- stage order
    def test_stage_order_ok_accepts_canonical_order_and_subsequences(self):
        ok, detail = stage_order_ok(STAGES)
        self.assertTrue(ok, detail)
        self.assertTrue(detail.startswith("in_order"), detail)
        self.assertTrue(stage_order_ok(["I", "Q", "S", "P"])[0])
        self.assertTrue(stage_order_ok(["intake"])[0])
        self.assertTrue(stage_order_ok(["I", "Q", "R", "S", "Q2", "P"])[0])

    def test_stage_order_ok_rejects_a_swapped_pair(self):
        for i in range(len(STAGES) - 1):
            swapped = list(STAGES)
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            with self.subTest(swap=f"{STAGES[i]}<->{STAGES[i + 1]}"):
                ok, detail = stage_order_ok(swapped)
                self.assertFalse(ok)
                self.assertIn("stage_backtrack", detail)

    def test_stage_order_ok_rejects_repeats_empties_and_bad_tokens(self):
        self.assertFalse(stage_order_ok(list(STAGES) + ["I2"])[0])
        ok, detail = stage_order_ok(["I", "Q", "R", "S", "Q2", "P", "I2", "Q"])
        self.assertFalse(ok)
        self.assertIn("stage_backtrack", detail)
        self.assertEqual(stage_order_ok([]), (False, "empty_stage_sequence"))
        self.assertEqual(stage_order_ok(None)[0], False)
        ok, detail = stage_order_ok(["I", "NONSENSE", "R"])
        self.assertFalse(ok)
        self.assertIn("unknown_stage_token", detail)

    def test_a_seven_stage_record_with_seven_aliases_is_reported_as_seven(self):
        ok, detail = stage_order_ok(["I", "question", "R", "synthesize",
                                     "Q2", "produce", "I2"])
        self.assertTrue(ok, detail)
        self.assertIn("7/7", detail)

    # ------------------------------------------------------------ run_pass
    def test_run_pass_rejects_builder_as_checker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            walk = _write_walk(root)
            with self.assertRaises(StageError) as ctx:
                run_pass(_Repo(root), walk.name, list(STAGES),
                         verifier="claude-fable-5-1", generator="claude-fable-5-1")
            self.assertEqual(str(ctx.exception), "verifier_is_generator")

    def test_run_pass_accepts_a_complete_walk_and_normalizes_its_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_walk(root, "fable-2031")
            rep = run_pass(_Repo(root), "fable-2031",
                           ["I", "question", "R", "synthesize", "Q2",
                            "produce", "I2"],
                           verifier="gpt-56", generator="claude-fable-5-1")
            self.assertEqual(rep["stages"], list(STAGES))
            self.assertEqual(rep["reached"], 7)
            self.assertTrue(rep["ok"])
            self.assertEqual(rep["walk_id"], "fable-2031")
            self.assertEqual(sorted(rep["artifacts"]["Intent"]),
                             ["00-intake.json"])
            self.assertGreaterEqual(rep["claims_checked"], 0)
            # read-only: the runner never invents artifacts or records
            self.assertEqual(sorted(p.name for p in (root / ".context" / "iqrsqpi"
                                                     / "fable-2031").iterdir()),
                             ["00-intake.json", "01-reality.json",
                              "02-decision.json", "proof.json"])

    def test_run_pass_refuses_a_walk_dir_that_does_not_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(StageError) as ctx:
                run_pass(_Repo(root), "no-such-walk", ["I"],
                         verifier="gpt-56", generator="claude-fable-5-1")
            self.assertIn("artifact_missing:", str(ctx.exception))

    def test_run_pass_names_the_missing_artifact_for_a_reached_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_walk(root, "fable-2031", omit=("02-decision",))
            with self.assertRaises(StageError) as ctx:
                run_pass(_Repo(root), "fable-2031",
                         ["I", "Q", "R", "S"], verifier="gpt-56",
                         generator="claude-fable-5-1")
            self.assertEqual(str(ctx.exception), "artifact_missing:02-decision")
            # a stage that was never reached demands nothing
            _write_walk(root, "short", omit=("02-decision",))
            rep = run_pass(_Repo(root), "short", ["I", "Q", "R"],
                           verifier="gpt-56", generator="claude-fable-5-1")
            self.assertEqual(rep["stages"], ["Intent", "Question", "Research"])

    def test_run_pass_refuses_a_number_with_no_source(self):
        for bad, name in (
            ({"claim": "compiled specs", "value": 56}, "typed value"),
            ({"claim": "compiled specs", "value": "56"}, "numeric string"),
            ({"claim": "the register holds 64 rows"}, "digits in prose"),
            ({"claim": "sealed packets", "value": 3, "source": "   "},
             "blank source"),
        ):
            with self.subTest(form=name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    _write_walk(root, "fable-2031",
                                claims={"01-reality": bad})
                    with self.assertRaises(StageError) as ctx:
                        run_pass(_Repo(root), "fable-2031",
                                 ["I", "Q", "R"], verifier="gpt-56",
                                 generator="claude-fable-5-1")
                    self.assertEqual(str(ctx.exception),
                                     "no_source_no_number:Research")

    def test_a_sourced_number_and_an_unsourced_non_number_both_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_walk(root, "fable-2031",
                        claims={"01-reality": {"claim": "compiled specs",
                                               "value": 56,
                                               "source": "out/harness-goalspecs"}})
            _write_walk(root, "quiet",
                        claims={"01-reality": {"claim": "order is canonical",
                                               "source": "STAGES"}})
            self.assertEqual(
                run_pass(_Repo(root), "fable-2031", ["I", "Q", "R"],
                         verifier="gpt-56",
                         generator="claude-fable-5-1")["claims_checked"], 1)
            self.assertEqual(
                run_pass(_Repo(root), "quiet", ["I", "Q", "R"],
                         verifier="gpt-56",
                         generator="claude-fable-5-1")["claims_checked"], 1)

    def test_run_pass_refuses_out_of_order_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_walk(root, "fable-2031")
            with self.assertRaises(StageError) as ctx:
                run_pass(_Repo(root), "fable-2031",
                         ["I", "Q", "S", "R"], verifier="gpt-56",
                         generator="claude-fable-5-1")
            self.assertIn("stage_out_of_order", str(ctx.exception))
            with self.assertRaises(StageError):
                run_pass(_Repo(root), "fable-2031", [], verifier="gpt-56",
                         generator="claude-fable-5-1")

    def test_run_pass_takes_a_bare_root_path_as_well_as_a_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_walk(root, "fable-2031")
            rep = run_pass(root, "fable-2031", ["I"], verifier="gpt-56",
                           generator="claude-fable-5-1")
            self.assertEqual(rep["stages"], ["Intent"])

    # ------------------------------------------------- hermetic stage gate
    def test_gate_is_green_on_the_committed_record(self):
        ok, detail = gate_stage_order(_Repo(REPO_ROOT))
        self.assertTrue(ok, detail)
        self.assertIn("7/7", detail)

    def test_gate_fixture_declares_the_canonical_seven_with_artifacts_and_sources(self):
        doc = json.loads((FIX / "iqrsqpi-run.json").read_text(encoding="utf-8"))
        stages = [s["stage"] for s in doc["stages"]]
        self.assertEqual([normalize_stage(s) for s in stages], list(STAGES))
        for row in doc["stages"]:
            self.assertTrue(row["artifacts"], row["stage"])
            self.assertTrue(row["claims"], row["stage"])
            for claim in row["claims"]:
                self.assertTrue(str(claim.get("source", "")).strip(),
                                f"unsourced claim in {row['stage']}")
        self.assertNotEqual(doc["generator"], doc["verifier"])

    def test_gate_goes_red_when_two_stages_are_reordered(self):
        src = REPO_ROOT / GATE_FIXTURE
        for swap in ((0, 6), (2, 3), (4, 5)):
            with self.subTest(swap=swap):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    dst = root / GATE_FIXTURE
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
                    doc = json.loads(dst.read_text(encoding="utf-8"))
                    a, b = swap
                    doc["stages"][a], doc["stages"][b] = (
                        doc["stages"][b], doc["stages"][a])
                    dst.write_text(json.dumps(doc), encoding="utf-8")
                    ok, detail = gate_stage_order(_Repo(root))
                    self.assertFalse(ok)
                    self.assertIn("stage_backtrack", detail)
                    # untouched original is still green
                    self.assertTrue(gate_stage_order(_Repo(REPO_ROOT))[0])

    def test_gate_reports_rather_than_raising_on_a_broken_fixture(self):
        for kind in ("missing", "unparseable", "no-stages", "not-an-object"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    path = root / GATE_FIXTURE
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if kind == "missing":
                        pass
                    elif kind == "unparseable":
                        path.write_text("{not json,,,", encoding="utf-8")
                    elif kind == "no-stages":
                        path.write_text(json.dumps({"walk_id": "x"}),
                                        encoding="utf-8")
                    else:
                        path.write_text("[1, 2, 3]", encoding="utf-8")
                    ok, detail = gate_stage_order(_Repo(root))
                    self.assertFalse(ok)
                    self.assertTrue(detail, "a RED must name its reason")

    def test_gate_reads_only_the_repo_root_it_is_handed(self):
        """No live-state: the same fixture under any root gives the same verdict."""
        src = REPO_ROOT / GATE_FIXTURE
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dst = root / GATE_FIXTURE
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            self.assertEqual(gate_stage_order(_Repo(root)),
                             gate_stage_order(_Repo(REPO_ROOT)))
            self.assertEqual(gate_stage_order(root),
                             gate_stage_order(_Repo(root)))


if __name__ == "__main__":
    unittest.main()
