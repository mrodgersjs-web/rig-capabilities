"""E_stage promotion-gate tests: arithmetic, golden-set integrity, verdicts."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities.estage import (  # noqa: E402
    AUTO_FALLBACK_TO_EARLIER_FAMILY, E_STAGE_WEIGHTS, GOLDEN_ROOT,
    GOLDEN_STATUSES, GOLDEN_STUDIOS, MANIFEST_SCHEMA, REVOKE_REMEDY,
    GoldenSetInvalid, compare, e_stage, fail_loss, family_of, input_hash,
    load_manifest, manifest_signature, promotion_verdict, rebaseline_required,
    revocation_check, verify_manifest)

M1 = "strategy-2031-capability-map"
M2 = "strategy-realign-week"
M3 = "strategy-known-expert-os-phase"
M1_E_OPUS = 0.6 * 0.35 + 0.25 * 0.75 + 0.15 * 0.80          # 0.5175
M1_E_FABLE = 0.6 * 0.125 + 0.25 * 0.875 + 0.15 * 0.75        # 0.40625
M2_E_OPUS = 0.6 * 0.25 + 0.25 * 0.50 + 0.15 * 0.50           # 0.35
M2_E_FABLE = 0.6 * 0.075 + 0.25 * 0.80 + 0.15 * (13 / 24)    # 0.32625
M3_E_OPUS = 0.6 * 0.175 + 0.25 * 0.40 + 0.15 * 0.50          # 0.28
M3_E_FABLE = 0.6 * 0.065 + 0.25 * 0.45 + 0.15 * 0.60         # 0.2415


def _replay(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def _run(**over) -> dict:
    """Self-describing single run — budgets inline, so e_stage needs no manifest."""
    run = {"mission_id": "m-hand", "cost_usd": 6.0, "turns": 32,
           "cost_budget_usd": 8.0, "turn_budget": 40,
           "gates": [{"id": "register", "blocking": True, "status": "PASS"},
                     {"id": "index_fresh", "blocking": True, "status": "PASS"},
                     {"id": "quality_contract", "blocking": False,
                      "scored": True, "score": 0.70},
                     {"id": "okf_trust", "blocking": False,
                      "scored": True, "score": 0.60}]}
    run.update(over)
    return run


def _score_candidate_below(deny: dict, mission_id: str, scores) -> dict:
    """Rewrite one candidate mission's scored gates in memory."""
    doc = copy.deepcopy(deny)
    for run in doc["runs"]:
        if run["mission_id"] != mission_id:
            continue
        scored = [g for g in run["gates"] if g.get("scored")]
        for gate, score in zip(scored, scores):
            gate["score"] = score
    return doc


def _spend(**over) -> dict:
    packet = {"candidate_family": "fable", "verifier_family": "opus",
              "manifest_signature": "sig-a", "replay_signature": "sig-a"}
    packet.update(over)
    return packet


class EStageTests(unittest.TestCase):
    maxDiff = None

    # ---------------------------------------------------------- e_stage math
    def test_weights_are_pinned_and_total_one(self):
        self.assertEqual(E_STAGE_WEIGHTS, {"fail": 0.6, "cost": 0.25,
                                           "turns": 0.15})
        self.assertEqual(list(E_STAGE_WEIGHTS), ["fail", "cost", "turns"])
        self.assertAlmostEqual(sum(E_STAGE_WEIGHTS.values()), 1.0, places=12)
        self.assertFalse(AUTO_FALLBACK_TO_EARLIER_FAMILY)

    def test_e_stage_hand_computed(self):
        run = _run()
        self.assertAlmostEqual(fail_loss(run), 0.35, places=12)
        self.assertAlmostEqual(e_stage(run), M1_E_OPUS, places=12)
        self.assertAlmostEqual(e_stage(run), 0.5175, places=12)

    def test_scored_gates_average_into_the_fail_term(self):
        # two scored gates at 0.90/0.85 -> mean(1-score) = 0.125
        run = _run(gates=[{"id": "register", "blocking": True, "status": "PASS"},
                          {"id": "quality_contract", "scored": True, "score": 0.90},
                          {"id": "okf_trust", "scored": True, "score": 0.85}])
        self.assertAlmostEqual(fail_loss(run), 0.125, places=12)
        # same run ceilings as _run(): 0.6*0.125 + 0.25*(6/8) + 0.15*(32/40)
        self.assertAlmostEqual(e_stage(run), 0.075 + 0.1875 + 0.12, places=12)

    def test_blocking_failure_short_circuits_the_fail_term_to_one(self):
        run = _run(gates=[{"id": "register", "blocking": True, "status": "PASS"},
                          {"id": "index_fresh", "blocking": True,
                           "status": "FAILED"},
                          {"id": "quality_contract", "scored": True,
                           "score": 1.0}])
        self.assertAlmostEqual(fail_loss(run), 1.0, places=12)
        # 0.6*1 + 0.25*0.75 + 0.15*0.8
        self.assertAlmostEqual(e_stage(run), 0.6 + 0.1875 + 0.12, places=12)

    def test_no_scored_gates_and_no_failure_means_zero_fail_loss(self):
        run = _run(gates=[{"id": "register", "blocking": True, "status": "pass"}])
        self.assertEqual(fail_loss(run), 0.0)
        self.assertAlmostEqual(e_stage(run), 0.25 * 0.75 + 0.15 * 0.8, places=12)

    def test_losses_clamp_at_one_and_zero(self):
        over = _run(cost_usd=99.0, turns=1000,
                    gates=[{"id": "register", "blocking": True, "status": "PASS"}])
        self.assertAlmostEqual(e_stage(over), 0.25 + 0.15, places=12)
        under = _run(cost_usd=-5, turns=-1,
                     gates=[{"id": "q", "scored": True, "score": 9.0}])
        # fail term clamps to 1-1 = 0, cost/turns clamp to 0
        self.assertAlmostEqual(e_stage(under), 0.0, places=12)

    def test_zero_or_missing_budget_raises_never_divides(self):
        for over in ({"cost_budget_usd": 0}, {"turn_budget": 0},
                     {"cost_budget_usd": None}, {"turn_budget": ""},
                     {"cost_budget_usd": "8"}, {"turn_budget": -40}):
            with self.assertRaises(GoldenSetInvalid, msg=str(over)):
                e_stage(_run(**over))

    def test_budget_absent_entirely_raises(self):
        for key in ("cost_budget_usd", "turn_budget"):
            bare = {k: v for k, v in _run().items() if k != key}
            with self.assertRaises(GoldenSetInvalid, msg=key):
                e_stage(bare)

    def test_run_without_budget_keys_anywhere_raises(self):
        bare = {"mission_id": "m", "cost_usd": 1.0, "turns": 2,
                "gates": [{"id": "a", "blocking": True, "status": "PASS"}]}
        with self.assertRaises(GoldenSetInvalid):
            e_stage(bare)

    def test_missing_measurement_or_gates_raises(self):
        no_cost = {k: v for k, v in _run().items() if k != "cost_usd"}
        with self.assertRaises(GoldenSetInvalid):
            e_stage(no_cost)
        no_turns = {k: v for k, v in _run().items() if k != "turns"}
        with self.assertRaises(GoldenSetInvalid):
            e_stage(no_turns)
        no_gates = {k: v for k, v in _run().items() if k != "gates"}
        with self.assertRaises(GoldenSetInvalid):
            e_stage(no_gates)

    def test_blocking_gate_without_status_raises(self):
        run = _run(gates=[{"id": "register", "blocking": True}])
        with self.assertRaises(GoldenSetInvalid):
            e_stage(run)

    # ------------------------------------------------------------- compare
    def test_compare_over_the_replay_fixtures(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        self.assertEqual(cmp_["n"], 3)
        self.assertEqual([r["mission_id"] for r in cmp_["per_mission"]],
                         sorted([M1, M2, M3]))
        got = {r["mission_id"]: r for r in cmp_["per_mission"]}
        for mid, base, cand in ((M1, M1_E_OPUS, M1_E_FABLE),
                                (M2, M2_E_OPUS, M2_E_FABLE),
                                (M3, M3_E_OPUS, M3_E_FABLE)):
            self.assertAlmostEqual(got[mid]["e_baseline"], base, places=12)
            self.assertAlmostEqual(got[mid]["e_candidate"], cand, places=12)
            self.assertTrue(got[mid]["strictly_lower"], mid)
        self.assertAlmostEqual(cmp_["mean_baseline"],
                               (M1_E_OPUS + M2_E_OPUS + M3_E_OPUS) / 3,
                               places=12)
        self.assertAlmostEqual(cmp_["mean_candidate"],
                               (M1_E_FABLE + M2_E_FABLE + M3_E_FABLE) / 3,
                               places=12)
        self.assertTrue(cmp_["strictly_lower_everywhere"])

    def test_strictly_lower_everywhere_flips_when_roles_reverse(self):
        fable, opus = _replay("replay-fable.json"), _replay("replay-opus.json")
        self.assertTrue(compare(opus, fable)["strictly_lower_everywhere"])
        rev = compare(fable, opus)
        self.assertFalse(rev["strictly_lower_everywhere"])
        self.assertFalse(any(r["strictly_lower"] for r in rev["per_mission"]))

    def test_compare_rejects_mismatched_mission_sets(self):
        fable = _replay("replay-fable.json")
        short = copy.deepcopy(fable)
        short["runs"] = short["runs"][:2]
        with self.assertRaises(GoldenSetInvalid) as ctx:
            compare(_replay("replay-opus.json"), short)
        self.assertIn("missing_in_candidate", str(ctx.exception))
        extra = copy.deepcopy(fable)
        extra["runs"].append(copy.deepcopy(extra["runs"][0]))
        extra["runs"][-1]["mission_id"] = "strategy-invented"
        with self.assertRaises(GoldenSetInvalid) as ctx:
            compare(_replay("replay-opus.json"), extra)
        self.assertIn("extra_in_candidate", str(ctx.exception))
        self.assertIn("strategy-invented", str(ctx.exception))

    def test_compare_rejects_duplicate_empty_and_budget_drift(self):
        fable = _replay("replay-fable.json")
        dup = copy.deepcopy(fable)
        dup["runs"].append(copy.deepcopy(dup["runs"][0]))
        with self.assertRaises(GoldenSetInvalid):
            compare(_replay("replay-opus.json"), dup)
        with self.assertRaises(GoldenSetInvalid):
            compare([], [])
        drift = copy.deepcopy(fable)
        drift["missions"][M1]["cost_budget_usd"] = 9.0
        with self.assertRaises(GoldenSetInvalid) as ctx:
            compare(_replay("replay-opus.json"), drift)
        self.assertIn("budget_mismatch", str(ctx.exception))

    def test_compare_accepts_bare_run_lists(self):
        runs = [{"mission_id": "a", "cost_usd": 1.0, "turns": 5,
                 "cost_budget_usd": 4.0, "turn_budget": 10,
                 "gates": [{"id": "g", "blocking": True, "status": "PASS"}]},
                {"mission_id": "b", "cost_usd": 2.0, "turns": 5,
                 "cost_budget_usd": 4.0, "turn_budget": 10,
                 "gates": [{"id": "g", "blocking": True, "status": "PASS"}]}]
        better = copy.deepcopy(runs)
        for run in better:
            run["cost_usd"] = 0.5
        cmp_ = compare(runs, better)
        self.assertTrue(cmp_["strictly_lower_everywhere"])
        self.assertEqual(cmp_["n"], 2)

    # ------------------------------------------------------ promotion verdict
    def test_promotion_verdict_promotes_a_clean_sweep(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        sig = _replay("replay-fable.json")["manifest_signature"]
        verdict = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig))
        self.assertEqual(verdict, {"promote": True, "reasons": []})

    def test_promotion_refuses_same_family_verifier(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        sig = _replay("replay-fable.json")["manifest_signature"]
        verdict = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig,
            verifier_family="claude-fable-5-1"))
        self.assertFalse(verdict["promote"])
        self.assertIn("same_family_collusion", verdict["reasons"])

    def test_promotion_refuses_one_mission_not_strictly_lower(self):
        opus = _replay("replay-opus.json")
        fable = _score_candidate_below(_replay("replay-fable.json"), M1,
                                       (0.62, 0.58))
        cmp_ = compare(opus, fable)
        # the mutation makes M1 the only non-lower mission while the mean still
        # improves, so the refusal must be attributable to that one mission.
        worse = [r["mission_id"] for r in cmp_["per_mission"]
                 if not r["strictly_lower"]]
        self.assertEqual(worse, [M1])
        self.assertLess(cmp_["mean_candidate"], cmp_["mean_baseline"])
        sig = _replay("replay-fable.json")["manifest_signature"]
        verdict = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig))
        self.assertFalse(verdict["promote"])
        self.assertEqual(verdict["reasons"], [f"not_strictly_lower:{M1}"])

    def test_any_mission_at_or_above_baseline_blocks_promotion(self):
        opus = _replay("replay-opus.json")
        # tie on M2: candidate equal to baseline is not "strictly lower"
        fable = _score_candidate_below(_replay("replay-fable.json"), M2,
                                       (0.80, 0.70))
        fable["runs"][1]["cost_usd"] = 2.0
        fable["runs"][1]["turns"] = 12
        cmp_ = compare(opus, fable)
        row = {r["mission_id"]: r for r in cmp_["per_mission"]}[M2]
        self.assertAlmostEqual(row["e_candidate"], row["e_baseline"], places=12)
        self.assertFalse(row["strictly_lower"])
        verdict = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature="s", replay_signature="s"))
        self.assertFalse(verdict["promote"])
        self.assertIn(f"not_strictly_lower:{M2}", verdict["reasons"])
        self.assertNotIn("mean_not_improved", verdict["reasons"])
        # the mean still improves; the tie alone is enough to refuse promotion
        self.assertLess(cmp_["mean_candidate"], cmp_["mean_baseline"])

    def test_promotion_refuses_signature_mismatch_and_missing_signature(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        bad = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature="sha256:aaa", replay_signature="sha256:bbb"))
        self.assertFalse(bad["promote"])
        self.assertIn("manifest_signature_mismatch", bad["reasons"])
        missing = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature="sha256:aaa", replay_signature=""))
        self.assertIn("manifest_signature_missing", missing["reasons"])

    def test_promotion_refuses_forced_tool_choice_and_gate_regression(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        sig = _replay("replay-fable.json")["manifest_signature"]
        forced = promotion_verdict("GTM", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig,
            forced_tool_choice=["capabilities/harnesses/hD-01-outbound-sequence.yaml"]))
        self.assertFalse(forced["promote"])
        self.assertIn("forced_tool_choice_harness", forced["reasons"])
        regressed = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig,
            blocking_gate_regression=[M1]))
        self.assertIn("blocking_gate_regression", regressed["reasons"])
        mismatched = promotion_verdict("Strategy", cmp_, _spend(
            manifest_signature=sig, replay_signature=sig, studio="App"))
        self.assertIn("studio_mismatch", mismatched["reasons"])

    def test_promotion_rejects_a_fabricated_compare_result(self):
        cmp_ = compare(_replay("replay-opus.json"), _replay("replay-fable.json"))
        lie = copy.deepcopy(cmp_)
        for row in lie["per_mission"]:
            row["e_candidate"] = row["e_baseline"] / 100.0
        with self.assertRaises(GoldenSetInvalid):
            promotion_verdict("Strategy", lie, _spend())
        flipped = copy.deepcopy(cmp_)
        flipped["strictly_lower_everywhere"] = True
        for row in flipped["per_mission"]:
            row["e_candidate"] = row["e_baseline"] + 1.0
        with self.assertRaises(GoldenSetInvalid):
            promotion_verdict("Strategy", flipped, _spend())
        with self.assertRaises(GoldenSetInvalid):
            promotion_verdict("", cmp_, _spend())
        with self.assertRaises(GoldenSetInvalid):
            promotion_verdict("Strategy", {"per_mission": []}, _spend())

    # ----------------------------------------------------- revocation / rerun
    def test_revocation_fires_on_spend_growth_without_ct_movement(self):
        out = revocation_check("Strategy", [40.0, 48.0, 56.0],
                               [0.62, 0.62, 0.61])
        self.assertTrue(out["revoked"])
        self.assertEqual(out["remedy"], REVOKE_REMEDY)
        self.assertEqual(out["remedy"], "revert to Opus 5")
        self.assertAlmostEqual(out["spend_growth"], 0.40, places=12)
        self.assertLessEqual(out["delta_c_t"], 0)

    def test_revocation_holds_when_ct_moves_or_growth_is_mild(self):
        moving = revocation_check("Strategy", [40.0, 48.0, 56.0],
                                  [0.62, 0.63, 0.65])
        self.assertFalse(moving["revoked"])
        self.assertIsNone(moving["remedy"])
        mild = revocation_check("Strategy", [40.0, 44.0, 48.0],
                                [0.62, 0.62, 0.62])
        self.assertFalse(mild["revoked"])
        self.assertAlmostEqual(mild["spend_growth"], 0.20, places=12)
        flat_at_threshold = revocation_check("Strategy", [40.0, 46.0, 52.0],
                                            [0.62, 0.62, 0.62])
        self.assertAlmostEqual(flat_at_threshold["spend_growth"], 0.30,
                               places=12)
        self.assertFalse(flat_at_threshold["revoked"],
                         "exactly 30% is not more than 30%")

    def test_revocation_refuses_to_conclude_without_history(self):
        thin = revocation_check("Strategy", [40.0, 56.0], [0.62, 0.61])
        self.assertFalse(thin["revoked"])
        self.assertEqual(thin["reasons"], ["insufficient_history"])
        zero = revocation_check("Strategy", [0.0, 0.0, 56.0], [0.62, 0.62, 0.61])
        self.assertFalse(zero["revoked"])
        self.assertEqual(zero["reasons"], ["spend_baseline_non_positive"])
        with self.assertRaises(ValueError):
            revocation_check("Strategy", [1.0, 2.0, 3.0], [0.1, 0.2])

    def test_rebaseline_required_across_families(self):
        self.assertTrue(rebaseline_required("opus", "fable"))
        self.assertTrue(rebaseline_required("Opus 5 (high effort)",
                                            "claude-fable-5-1"))
        self.assertTrue(rebaseline_required(None, "fable"))
        self.assertTrue(rebaseline_required("", "fable"))
        self.assertFalse(rebaseline_required("fable", "claude-fable-5-1"))
        self.assertFalse(rebaseline_required("claude-opus-5", "Opus 5"))
        self.assertEqual(family_of("claude-fable-5-1"), "fable")
        self.assertEqual(family_of("Opus 5 (high effort)"), "opus")

    def test_callers_raise_golden_set_invalid_when_rebaseline_is_required(self):
        # A golden set recorded under another family cannot certify a candidate:
        # the documented caller raises before compare() is trusted.
        manifest = load_manifest(FIX / "golden-strategy.json")
        candidate = _replay("replay-fable.json")["family"]
        if rebaseline_required(manifest["recorded_under"], candidate):
            with self.assertRaises(GoldenSetInvalid):
                raise GoldenSetInvalid(
                    f"golden_set_recorded_under:{manifest['recorded_under']}")
        with self.assertRaises(GoldenSetInvalid):
            raise GoldenSetInvalid("golden_set_recorded_under:None")

    # ------------------------------------------------------ committed artifacts
    def test_all_six_golden_manifests_are_dormant_and_intact(self):
        seen = {}
        for studio in GOLDEN_STUDIOS:
            path = REPO_ROOT / GOLDEN_ROOT / studio / "missions.json"
            self.assertTrue(path.is_file(), str(path))
            man = load_manifest(path)          # raises unless signature holds
            self.assertEqual(man["schema"], MANIFEST_SCHEMA)
            self.assertEqual(man["studio"], studio)
            self.assertEqual(man["status"], "DORMANT", studio)
            self.assertIn(man["status"], GOLDEN_STATUSES)
            self.assertEqual(man["model_id"], "claude-fable-5-1")
            self.assertNotEqual(man["candidate_family"],
                                man["verifier_family"])
            self.assertFalse(man["auto_fallback_to_earlier_family"])
            self.assertEqual(man["e_stage_weights"], E_STAGE_WEIGHTS)
            self.assertEqual(man["promotion_gate"],
                             "DORMANT_PER_STUDIO_UNTIL_E_STAGE_LOWER_THAN_OPUS5")
            self.assertFalse(man["baseline_recorded"])
            self.assertIsNone(man["recorded_under"])
            ok, reason = verify_manifest(man)
            self.assertTrue(ok, reason)
            seen[studio] = len(man["missions"])
            for m in man["missions"]:
                self.assertGreater(m["cost_budget_usd"], 0, m["id"])
                self.assertGreater(m["turn_budget"], 0, m["id"])
                self.assertEqual(m["input_sha256"], input_hash(m), m["id"])
                self.assertEqual(round(sum(g["weight"] for g in m["gates"]), 6),
                                 1.0, m["id"])
                blocking = [g for g in m["gates"] if g["blocking"]]
                scored = [g for g in m["gates"] if g.get("scored")]
                self.assertTrue(blocking and scored, m["id"])
                if m["origin_kind"] == "harness":
                    self.assertTrue((REPO_ROOT / m["origin"]).is_file(),
                                    m["origin"])
        self.assertEqual(sorted(seen), sorted(GOLDEN_STUDIOS))
        self.assertEqual(set(seen.values()), {3})

    def test_tampering_with_a_manifest_breaks_its_signature(self):
        man = load_manifest(REPO_ROOT / GOLDEN_ROOT / "Strategy" /
                            "missions.json")
        man["missions"][0]["cost_budget_usd"] = 99.0
        self.assertEqual(verify_manifest(man), (False, "signature_mismatch"))
        del man["missions"][0]["input_sha256"]
        self.assertEqual(
            verify_manifest(man),
            (False, f"input_hash_mismatch:{man['missions'][0]['id']}"))
        self.assertEqual(verify_manifest({"schema": "other"}),
                         (False, "schema_unsupported"))
        self.assertEqual(verify_manifest({**man, "status": "PROMOTED"}),
                         (False, "status_unknown"))

    def test_replay_fixtures_carry_the_frozen_manifest_signature(self):
        manifest = load_manifest(FIX / "golden-strategy.json")
        self.assertEqual(manifest["studio"], "Strategy")
        self.assertEqual(manifest["status"], "DORMANT")
        self.assertTrue(manifest["synthetic"])
        self.assertEqual(manifest_signature(manifest),
                         manifest["manifest_signature"])
        for name in ("replay-fable.json", "replay-opus.json"):
            doc = _replay(name)
            self.assertEqual(doc["manifest_signature"],
                             manifest["manifest_signature"], name)
            self.assertEqual(doc["e_stage_weights"], E_STAGE_WEIGHTS, name)
            self.assertEqual([r["mission_id"] for r in doc["runs"]],
                             [M1, M2, M3], name)
            self.assertTrue(doc["synthetic"], name)
            self.assertEqual(doc["provenance"],
                             "fixture_only_not_a_recorded_run", name)
            for run in doc["runs"]:
                mission = {m["id"]: m for m in manifest["missions"]}[
                    run["mission_id"]]
                self.assertEqual(
                    doc["missions"][run["mission_id"]],
                    {"cost_budget_usd": mission["cost_budget_usd"],
                     "turn_budget": mission["turn_budget"]}, run["mission_id"])
                declared = [g["id"] for g in mission["gates"]]
                reported = [g["id"] for g in run["gates"]]
                self.assertEqual(sorted(reported), sorted(declared),
                                 run["mission_id"])

    def test_load_manifest_refuses_a_replay_document(self):
        with self.assertRaises(GoldenSetInvalid):
            load_manifest(FIX / "replay-fable.json")


if __name__ == "__main__":
    unittest.main()
