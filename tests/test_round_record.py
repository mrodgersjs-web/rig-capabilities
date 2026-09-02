"""V54: the round must carry a memory.

A round that picks candidates, patches frontmatter and scores the result is only
half of an optimizer. The other half is the record: previous hypotheses, diffs,
scores and verdicts, loaded back BEFORE the next proposal, so a diff the evidence
already refuted is not re-proposed again and again. These tests pin three things:

  * the two missing stage artifacts exist and say what they claim — a failure
    analysis over the recorded rollouts, and a hypothesis that cites it;
  * the persistent record lives under .context/rounds/, round-trips, and is read
    before proposing — never under ~/.rig;
  * a REJECTED diff-hash is refused on replay, and the refusal is a real process
    exit code (1), proven by subprocess returncode, then restored to green.

The fixture is deliberate. `weak-skill` carries one always-red check (the recurring
failure the analysis must name) plus a byte-budget check sized to size+1 that any
inserted line flips RED while the recorded history says it was always green — a
real held-out regression, so the honest verdict on that hypothesis is REJECTED.
`novel-skill` needs one field filled and its only check is a `file:` that stays
green: the ACCEPTED control.
"""
from __future__ import annotations

import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import rounds  # noqa: E402
from rig_capabilities.catalog import Repo  # noqa: E402

V53_KEYS = ("ts", "lane", "dry", "strategy", "selection_fallback",
            "uncertain_candidates", "eval_budget", "eval_budget_effective",
            "eval_spent", "candidates", "deferred", "actions", "unevaluated",
            "regressed", "graduated")
REL = "capabilities/skills/weak-skill/SKILL.md"
NOVEL = "capabilities/skills/novel-skill/SKILL.md"
FAILING = "cmd:false"


class _Fixture:
    """A two-asset misc-lane estate with one recurring failure and one green."""

    def __init__(self, tmp: str):
        self.root = Path(tmp) / "repo"
        self.root.mkdir(parents=True, exist_ok=True)
        self.repo = Repo(self.root)
        (self.root / ".lanes.json").write_text(json.dumps(
            {"weak-skill": "misc", "novel-skill": "misc"}))
        self.repo.config_path.write_text(json.dumps(
            {"defaults": False, "external_roots": [], "install_roots": {}}))

        d = self.root / "capabilities" / "skills" / "weak-skill"
        d.mkdir(parents=True)
        head = ("---\nname: weak-skill\ndescription: weak-skill contract is thin\n"
                "done_when:\n  - " + FAILING + "\n")
        tail = "---\n# weak-skill\nThe asset body.\n"
        # fixed point: the byte budget is the size of the file that contains it, so
        # the check is GREEN now and RED after any upgrade line is inserted
        body, threshold = rounds._sized_check(head, tail, REL)
        self.check = f"cmd:test $(wc -c < {REL}) -lt {threshold}"
        (d / "SKILL.md").write_text(body)
        n = self.root / "capabilities" / "skills" / "novel-skill"
        n.mkdir(parents=True)
        (n / "SKILL.md").write_text(
            "---\nname: novel-skill\ndescription: novel-skill needs one field\n"
            "outcome: misc: prove the round carries a memory\n"
            f"done_when:\n  - file:{NOVEL}\nquality_floor: 0.6\n"
            "---\n# novel-skill\nThe asset body.\n")
        self.repo.build_index()
        self.original = (self.root / REL).read_text()
        self.seed_history()

    def seed_history(self):
        """Two recorded runs: weak-skill's cmd:false always red, its byte budget
        always green (the held-out set); novel-skill all green."""
        d = self.root / ".context" / "quality-runs"
        d.mkdir(parents=True, exist_ok=True)
        for day in ("2026-09-01T000000", "2026-09-02T000000"):
            (d / f"{day}.json").write_text(json.dumps({"rows": [
                {"id": "weak-skill", "pass": False, "results": [
                    {"form": FAILING, "ok": False},
                    {"form": self.check, "ok": True}]},
                {"id": "novel-skill", "pass": True, "results": [
                    {"form": f"file:{NOVEL}", "ok": True}]}]}))

    def keep_only(self, asset_id: str):
        shutil.rmtree(self.root / "capabilities" / "skills" / "weak-skill")
        self.repo.build_index()

    def knobs(self, doc: dict):
        d = self.root / ".context" / "rounds"
        d.mkdir(parents=True, exist_ok=True)
        (d / "knobs.json").write_text(json.dumps(doc))

    def record(self) -> list:
        return rounds.load_record(self.repo)

    def acts(self, rep: dict) -> dict:
        return {a["id"]: a for a in rep["actions"]}


class Record(unittest.TestCase):
    """The record is a file: it round-trips, tolerates damage, lives in .context."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.fx = _Fixture(self._tmp.name)

    def test_missing_record_is_empty_history_not_a_zero_claim(self):
        self.assertEqual(rounds.load_record(self.fx.repo), [])

    def test_record_path_is_under_context_never_home_rig(self):
        p = rounds.record_path(self.fx.repo)
        self.assertEqual(p, self.fx.root / ".context" / "rounds" / "record.jsonl")
        self.assertTrue(p.resolve().is_relative_to(self.fx.root.resolve()))
        self.assertNotIn(".rig", str(p))

    def test_unreadable_line_is_skipped_not_fatal(self):
        p = rounds.record_path(self.fx.repo)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"asset":"a","verdict":"ACCEPTED"}\n{oops\n')
        rows = rounds.load_record(self.fx.repo)
        self.assertEqual([r["asset"] for r in rows], ["a"])

    def test_append_round_trips_every_field_the_next_round_needs(self):
        entry = {"lane": "misc", "asset": "weak-skill", "kind": "skill",
                 "source": "canonical", "hypothesis": "H", "diff_hash": "abc123",
                 "before": 60, "after": 100, "done_tests": False,
                 "verdict": rounds.REJECTED, "action": "applied-regressed"}
        self.assertEqual(rounds.append_record(self.fx.repo, [entry]), 1)
        got = rounds.load_record(self.fx.repo)
        self.assertEqual(len(got), 1)
        for k in ("ts", "lane", "asset", "diff_hash", "verdict", "before", "after"):
            self.assertIn(k, got[0])
        self.assertEqual(got[0]["verdict"], "REJECTED")
        rounds.append_record(self.fx.repo, [dict(entry, diff_hash="def456")])
        self.assertEqual(len(rounds.load_record(self.fx.repo)), 2)  # append-only

    def test_verdict_vocabulary_is_closed(self):
        self.assertEqual(set(rounds.VERDICTS),
                         {"ACCEPTED", "REJECTED", "UNEVALUATED", "BLOCKED-REPLAY"})

    def test_diff_hash_is_stable_and_diff_specific(self):
        a = rounds.diff_hash("weak-skill", "skill", "canonical",
                             {"quality_floor": 0.6})
        b = rounds.diff_hash("weak-skill", "skill", "canonical",
                             {"quality_floor": 0.6})
        c = rounds.diff_hash("weak-skill", "skill", "canonical",
                             {"quality_floor": 0.7})
        d = rounds.diff_hash("other-skill", "skill", "canonical",
                             {"quality_floor": 0.6})
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertEqual(len(a), 16)


class Artifacts(unittest.TestCase):
    """Five stages, and the two that never existed now write real artifacts."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.fx = _Fixture(self._tmp.name)

    def test_round_writes_every_stage_artifact(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        self.assertIn("stages", rep)
        for key in ("rollouts", "failure_analysis", "hypothesis",
                    "modification", "score_select"):
            self.assertIn(key, rep["stages"], f"stage artifact {key} missing")
            p = Path(rep["stages"][key])
            self.assertTrue(str(p).startswith(str(self.fx.root / ".context")),
                            f"{key} escaped .context/rounds: {p}")
            self.assertTrue(p.is_file(), f"stage artifact not written: {p}")
            self.assertIn("ts", json.loads(p.read_text()))

    def test_failure_analysis_names_the_recurring_failure_with_evidence(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        doc = json.loads(Path(rep["stages"]["failure_analysis"]).read_text())
        self.assertEqual(doc["lane"], "misc")
        self.assertEqual(doc["source"], ".context/quality-runs")
        self.assertTrue(doc["failing"], "no recurring failure in recorded rollouts")
        by_form = {f["check"]: f for f in doc["failing"]}
        self.assertIn(FAILING, by_form)
        self.assertEqual(by_form[FAILING]["fails"], 2)
        self.assertEqual(by_form[FAILING]["runs"], 2)
        self.assertIn("weak-skill", by_form[FAILING]["assets"])
        self.assertTrue(by_form[FAILING]["recurring"])
        # the always-green held-out check belongs here, not in the failure list
        self.assertIn(self.fx.check, {h["check"] for h in doc["held_out_green"]})

    def test_rollouts_artifact_carries_what_the_round_read(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        doc = json.loads(Path(rep["stages"]["rollouts"]).read_text())
        self.assertEqual({r["id"] for r in doc["rows"]},
                         {"weak-skill", "novel-skill"})
        wk = next(r for r in doc["rows"] if r["id"] == "weak-skill")
        self.assertEqual((wk["runs"], wk["passes"]), (2, 0))

    def test_hypothesis_cites_the_failure_and_carries_a_diff_hash(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        doc = json.loads(Path(rep["stages"]["hypothesis"]).read_text())
        self.assertTrue(doc["hypotheses"], "no hypothesis for a patchable asset")
        h = next(x for x in doc["hypotheses"] if x["asset"] == "weak-skill")
        self.assertEqual(len(h["diff_hash"]), 16)
        self.assertTrue(h["statement"].strip())
        self.assertIn(FAILING, h["cited_failures"])
        self.assertEqual(h["version"], rounds.KNOB_VERSION)
        self.assertEqual(h["prior_verdicts"], [])  # first proposal has no history

    def test_dry_writes_analysis_but_no_verdicts(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, dry=True,
                               strategy="weakest")
        self.assertTrue(Path(rep["stages"]["hypothesis"]).is_file())
        self.assertEqual(rep["record"]["appended"], 0)
        self.assertEqual(rounds.load_record(self.fx.repo), [])
        self.assertEqual((self.fx.root / REL).read_text(), self.fx.original)


class ReadBack(unittest.TestCase):
    """The next round must load previous hypotheses/diffs/scores/verdicts."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.fx = _Fixture(self._tmp.name)

    def test_both_verdicts_land_in_the_record(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=2, budget=2,
                               strategy="weakest")
        rec = self.fx.record()
        self.assertEqual([(r["asset"], r["verdict"]) for r in rec],
                         [("weak-skill", "REJECTED"), ("novel-skill", "ACCEPTED")])
        self.assertEqual(rep["record"]["appended"], 2)
        self.assertTrue(all(r["diff_hash"] for r in rec))
        self.assertTrue(all(isinstance(r["before"], int)
                            and isinstance(r["after"], int) for r in rec))
        self.assertEqual(rep["exit_code"], 0)

    def test_a_regression_rolls_the_asset_back(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=1, budget=1,
                               strategy="weakest")
        wk = self.fx.acts(rep)["weak-skill"]
        self.assertEqual(wk["action"], "applied-regressed")
        self.assertTrue(wk["rolled_back"])
        self.assertFalse(wk["graduated"])
        self.assertIn(self.fx.check, wk["regressed_checks"])
        # the command's own promise: a candidate that fails stays untouched
        self.assertEqual((self.fx.root / REL).read_text(), self.fx.original)
        self.assertEqual([(r["asset"], r["verdict"]) for r in self.fx.record()],
                         [("weak-skill", "REJECTED")])
        self.assertEqual(rep["rejected"], 1)
        self.assertEqual(rep["exit_code"], 0)

    def test_a_green_patch_graduates_and_is_recorded_accepted(self):
        self.fx.keep_only("novel-skill")
        rep = rounds.run_round(self.fx.repo, "misc", n=1, budget=1)
        nv = self.fx.acts(rep)["novel-skill"]
        self.assertEqual(nv["action"], "applied")
        self.assertTrue(nv["graduated"])
        self.assertGreater(nv["after"], nv["before"])
        self.assertEqual([(r["asset"], r["verdict"]) for r in self.fx.record()],
                         [("novel-skill", "ACCEPTED")])
        self.assertEqual(rep["exit_code"], 0)

    def test_second_round_loads_the_record_before_proposing(self):
        rounds.run_round(self.fx.repo, "misc", n=1, budget=1, strategy="weakest")
        rep2 = rounds.run_round(self.fx.repo, "misc", n=1, budget=1,
                                strategy="weakest")
        self.assertGreaterEqual(rep2["record"]["loaded"], 1)
        self.assertGreaterEqual(rep2["record"]["rejected_known"], 1)

    def test_rejected_diff_is_not_re_proposed_and_the_round_refuses(self):
        first = rounds.run_round(self.fx.repo, "misc", n=1, budget=1,
                                 strategy="weakest")
        h1 = self.fx.acts(first)["weak-skill"]
        rep2 = rounds.run_round(self.fx.repo, "misc", n=1, budget=1,
                                strategy="weakest")
        wk = self.fx.acts(rep2)["weak-skill"]
        self.assertEqual(wk["action"], "rejected-repeat")
        self.assertIsNone(wk["plan"])            # nothing proposed, nothing applied
        self.assertEqual(wk["diff_hash"], h1["diff_hash"])
        self.assertEqual(rep2["replay_rejected"], 1)
        self.assertEqual(rep2["exit_code"], 1)
        self.assertEqual(rep2["eval_spent"], 0)   # a refusal costs no evaluation
        self.assertEqual((self.fx.root / REL).read_text(), self.fx.original)
        # the refusal is recorded too, so the re-patch symptom stays countable
        self.assertEqual([r["verdict"] for r in self.fx.record()],
                         ["REJECTED", "BLOCKED-REPLAY"])

    def test_the_guard_fires_only_on_a_recorded_rejection(self):
        rounds.run_round(self.fx.repo, "misc", n=1, budget=1, strategy="weakest")
        rounds.record_path(self.fx.repo).write_text("")  # named human override
        rep = rounds.run_round(self.fx.repo, "misc", n=1, budget=1,
                               strategy="weakest")
        self.assertEqual(rep["replay_rejected"], 0)
        self.assertEqual(rep["exit_code"], 0)
        self.assertEqual(self.fx.acts(rep)["weak-skill"]["action"],
                         "applied-regressed")

    def test_a_rejection_on_one_asset_does_not_block_another(self):
        rounds.run_round(self.fx.repo, "misc", n=1, budget=1, strategy="weakest")
        rep = rounds.run_round(self.fx.repo, "misc", n=2, budget=2,
                               strategy="weakest")
        acts = self.fx.acts(rep)
        self.assertEqual(acts["weak-skill"]["action"], "rejected-repeat")
        self.assertEqual(acts["novel-skill"]["action"], "applied")
        self.assertTrue(acts["novel-skill"]["graduated"])
        self.assertEqual(rep["replay_rejected"], 1)
        self.assertEqual(rep["exit_code"], 1)


class Knobs(unittest.TestCase):
    """Attempt budget, routing and the stopping rule are declared versioned knobs."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.fx = _Fixture(self._tmp.name)

    def test_declared_knobs_are_reported(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=1, dry=True)
        self.assertEqual(rep["knobs"]["version"], rounds.KNOB_VERSION)
        self.assertEqual(rep["knobs"]["source"], "declared")
        self.assertEqual(rep["knobs"]["unknown"], [])

    def test_knobs_file_overrides_without_editing_code(self):
        """A declared attempt budget routes the round with no code edit."""
        self.fx.knobs({"version": rounds.KNOB_VERSION, "eval_budget_default": 1})
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        self.assertEqual(rep["knobs"]["source"], "file")
        self.assertEqual(rep["eval_budget"], 1)
        self.assertEqual(rep["eval_budget_effective"], 1)
        self.assertEqual(rep["eval_spent"], 1)
        self.assertEqual(rep["candidates"], 1)
        # the budget buys ONE attempt, so the second candidate is deferred by name —
        # "we ran a round" cannot quietly mean "we ran everything"
        self.assertEqual([d["id"] for d in rep["deferred"]], ["novel-skill"])
        self.assertEqual(self.fx.acts(rep)["weak-skill"]["action"],
                         "applied-regressed")
        self.assertNotIn("novel-skill", self.fx.acts(rep))
        self.assertEqual([(r["asset"], r["verdict"]) for r in self.fx.record()],
                         [("weak-skill", "REJECTED")])

    def test_unevaluated_is_reported_and_still_unreachable(self):
        """Honesty check on a V53 key. The selector caps candidate COUNT at the
        evaluation budget, so a round can never apply more edits than it can run and
        `applied-unevaluated` cannot occur today. The branch stays (an unrun edit must
        be named, never counted as graduated, if that coupling changes) and the key
        stays (callers read it) — but the report must not imply the state was seen."""
        rep = rounds.run_round(self.fx.repo, "misc", n=2, budget=2,
                               strategy="weakest")
        self.assertIn("unevaluated", rep)
        self.assertEqual(rep["unevaluated"], 0)
        self.assertEqual(rep["eval_spent"], rep["candidates"])

    def test_first_reject_stops_the_round_before_spending_on_the_rest(self):
        self.fx.knobs({"version": rounds.KNOB_VERSION,
                       "stopping_rule": "first-reject"})
        rep = rounds.run_round(self.fx.repo, "misc", n=2, strategy="weakest")
        self.assertEqual(rep["stopped_reason"], "first-reject")
        acts = self.fx.acts(rep)
        self.assertEqual(acts["weak-skill"]["action"], "applied-regressed")
        self.assertEqual(acts["novel-skill"]["action"], "stopped-by-rule")
        self.assertEqual(len(self.fx.record()), 1)

    def test_unknown_knob_is_named_not_silently_ignored(self):
        self.fx.knobs({"version": 99, "bogus": True})
        rep = rounds.run_round(self.fx.repo, "misc", n=1, dry=True)
        self.assertEqual(rep["knobs"]["unknown"], ["bogus"])
        self.assertTrue(rep["knobs"]["version_mismatch"])


class BackwardContract(unittest.TestCase):
    """Callers today: bin/rig-capabilities, the MCP handler, test_catalog."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.fx = _Fixture(self._tmp.name)

    def test_run_round_keywords_and_defaults_are_unchanged(self):
        p = inspect.signature(rounds.run_round).parameters
        self.assertEqual(list(p)[:5], ["repo", "lane", "n", "dry", "budget"])
        self.assertEqual(p["n"].default, 5)
        self.assertIs(p["dry"].default, False)
        self.assertIsNone(p["budget"].default)
        self.assertEqual(p["strategy"].default, "informative")

    def test_report_is_a_superset_of_the_v53_keys(self):
        rep = rounds.run_round(self.fx.repo, "misc", n=1, dry=True)
        for k in V53_KEYS:
            self.assertIn(k, rep, f"report lost v53 key {k}")

    def test_selection_module_is_untouched_and_still_used(self):
        from rig_capabilities import selection
        self.assertTrue(hasattr(selection, "select"))
        rep = rounds.run_round(self.fx.repo, "misc", n=1, dry=True)
        self.assertEqual(rep["strategy"], "informative-first")

    def test_pick_candidates_shape_is_unchanged(self):
        rows = rounds.pick_candidates(self.fx.repo, "misc", 2)
        self.assertTrue(rows)
        self.assertEqual(sorted(rows[0]), ["id", "kind", "score", "source"])


class PlantFailureSubprocess(unittest.TestCase):
    """The refusal is a process exit code, not an adjective.

    PYTHONDONTWRITEBYTECODE=1 so a stale .pyc can never make a restored tree look
    green, and HOME points into the sandbox so any escape to ~/.rig is visible.
    """

    def _run(self, root: Path, *extra: str) -> subprocess.CompletedProcess:
        (root / "fakehome").mkdir(exist_ok=True)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=str(REPO_ROOT), HOME=str(root / "fakehome"))
        return subprocess.run(
            [sys.executable, "-m", "rig_capabilities.rounds", "misc",
             "--root", str(root), "--n", "1", "--budget", "1",
             "--strategy", "weakest", *extra],
            cwd=str(root), env=env, capture_output=True, text=True, timeout=120)

    def _fixture(self) -> _Fixture:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return _Fixture(tmp.name)

    def test_plant_rejected_replay_goes_red_then_restore_goes_green(self):
        fx = self._fixture()
        first = self._run(fx.root)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertTrue([r for r in fx.record() if r["verdict"] == "REJECTED"],
                        "first round recorded no REJECTED hypothesis")

        # PLANT: same evidence, same diff — the guard must refuse, exit 1
        second = self._run(fx.root)
        self.assertEqual(second.returncode, 1,
                         "re-proposing a REJECTED diff exited green: " + second.stdout)
        self.assertEqual(json.loads(second.stdout)["replay_rejected"], 1)

        # RESTORE: the rejected verdict is removed by a named override -> green
        rounds.record_path(fx.repo).write_text("")
        third = self._run(fx.root)
        self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
        self.assertEqual(json.loads(third.stdout)["replay_rejected"], 0)

    def test_round_state_never_lands_in_home_rig(self):
        fx = self._fixture()
        for _ in range(2):
            self._run(fx.root)
        self.assertFalse((fx.root / "fakehome" / ".rig").exists(),
                         "round state escaped to ~/.rig")
        self.assertTrue((fx.root / ".context" / "rounds"
                         / "record.jsonl").is_file())

    def test_plant_fixture_rejected_exits_one_and_novel_exits_zero(self):
        """The two cmd: fixtures written in the command asset, driven identically."""
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=str(REPO_ROOT))
        for mode, want in (("rejected", 1), ("novel", 0)):
            r = subprocess.run(
                [sys.executable, "-m", "rig_capabilities.rounds", "--plant", mode],
                cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
                timeout=180)
            self.assertEqual(r.returncode, want,
                             f"--plant {mode} -> {r.returncode}\n{r.stdout}{r.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
