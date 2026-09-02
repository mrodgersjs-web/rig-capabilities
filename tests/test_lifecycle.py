"""Tests for the asset lifecycle state machine (arXiv:2608.29596 + 2608.12851).

Four claims the harness depends on, each checked here:

  1. every legal transition has a record that actually triggers it — the edge
     set is derived from the rule table, so a rule shipped without a fixture is
     a test failure, not a comment;
  2. illegal transitions are refused structurally: `revoked` has no exit to a
     loadable state, and a verified restore archive does not reopen one;
  3. revocation overrides utility — the highest-scoring asset in the estate
     stops being loadable when its reuse attribution turns negative, and the
     utility feed alone would have kept it forever;
  4. `plan()` is write-free: `open`, `os.remove`, `mkdir` and `write_text` are
     patched to raise for the duration of the call, and a sentinel tree is
     hashed before and after.

Plus the plant suite: every named guard must flip the example estate to
INSOLVENT. A guard that cannot go RED is not a guard.
"""

import builtins
import contextlib
import hashlib
import io
import json
import os
import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

from rig_capabilities import lifecycle

NOW = "2026-09-02"
RESTORE = {"point": ".rig/prune/restore/rig-subject.tar.gz", "verified": True}
APPROVE = {"approval": "sha256:condemnation-9f", "scope": ["removal"]}


def rec(rid="rig-subject", state="active", **over):
    """A healthy asset: measured positive utility, real use, clean attribution."""
    base = {
        "id": rid, "state": state, "state_reason": "certified V52i",
        "state_at": "2026-06-01", "days_in_state": 30,
        "utility": {"counterfactual_gain": 0.9, "retrieval_latency": 0.05,
                    "token_footprint": 0.05, "execution_overhead": 0.05, "trials": 6},
        "usage": {"uses": 10, "passes": 9, "runs": 10, "window_days": 60,
                  "last_used_days_ago": 3},
        "attribution": {"negative": 0, "open_risk_flags": []},
        "done_test": {"status": "green"},
    }
    base.update(over)
    return base


NEG_QUIARANTINE = {"attribution": {"negative": 4, "open_risk_flags": []}}
NEG_REVOKE = {"attribution": {"negative": 9, "open_risk_flags": []}}
NEGATIVE_UTILITY = {"utility": {"counterfactual_gain": 0.1, "retrieval_latency": 0.3,
                                "token_footprint": 0.4, "execution_overhead": 0.2,
                                "trials": 6},
                    "usage": {"uses": 2, "passes": 1, "runs": 2, "window_days": 90,
                              "last_used_days_ago": 60}}
DECAYED = {"usage": {"uses": 0, "passes": 0, "runs": 0, "window_days": 120,
                     "last_used_days_ago": 200}}


# One record per (rule, source state) the rule table allows. `edge_cases()`
# asserts this set equals the table, so coverage cannot rot silently.
EDGE_CASES = {
    ("revocation", "active"): rec(**NEG_REVOKE),
    ("revocation", "dormant"): rec(state="dormant", **NEG_REVOKE),
    ("revocation", "deprecated"): rec(state="deprecated", **NEG_REVOKE),
    # safety outranks the return path: an evicted asset with a verified restore
    # is still pulled to `revoked` once attribution turns negative
    ("revocation", "evicted"): rec(state="evicted", restore=RESTORE, **NEG_REVOKE),
    ("attribution_quarantine", "active"): rec(**NEG_QUIARANTINE),
    ("attribution_quarantine", "deprecated"): rec(state="deprecated", **NEG_QUIARANTINE),
    ("attribution_repair", "active"): rec(attribution={"negative": 2, "open_risk_flags": []}),
    ("attribution_repair", "dormant"): rec(state="dormant",
                                           attribution={"negative": 2, "open_risk_flags": []}),
    ("utility_evict", "active"): rec(**NEGATIVE_UTILITY, restore=RESTORE, gate_d=APPROVE),
    ("utility_evict", "dormant"): rec(state="dormant", **NEGATIVE_UTILITY,
                                      restore=RESTORE, gate_d=APPROVE),
    ("utility_evict", "deprecated"): rec(state="deprecated", **NEGATIVE_UTILITY,
                                         restore=RESTORE, gate_d=APPROVE),
    ("decay_quarantine", "active"): rec(**DECAYED),
    ("decay_evict", "dormant"): rec(state="dormant", days_in_state=150,
                                    usage={"uses": 0, "passes": 0, "runs": 0,
                                           "window_days": 180, "last_used_days_ago": 240},
                                    restore=RESTORE, gate_d=APPROVE),
    ("test_repair", "active"): rec(done_test={"status": "red"}),
    ("test_repair", "dormant"): rec(state="dormant", days_in_state=5,
                                    done_test={"status": "red"}),
    ("unrepaired_evict", "deprecated"): rec(state="deprecated", days_in_state=40,
                                            done_test={"status": "red"},
                                            restore=RESTORE, gate_d=APPROVE),
    ("revival", "dormant"): rec(state="dormant", days_in_state=10,
                                usage={"uses": 5, "passes": 4, "runs": 5,
                                       "window_days": 30, "last_used_days_ago": 2}),
    ("repair", "deprecated"): rec(state="deprecated",
                                  done_test={"status": "green"},
                                  repair={"record": ".rig/prune/repairs/a.txt"}),
    ("restore", "evicted"): rec(state="evicted", restore=RESTORE),
    ("tombstone_retire", "revoked"): rec(
        state="revoked",
        tombstone={"asset": "rig-subject", "state": "revoked", "at": "2026-08-20",
                   "because": "negative reuse attribution 8", "restore_forbidden": True},
        gate_d=APPROVE),
}


def edge_cases():
    tabled = {(r, s) for r, rule in lifecycle.RULES.items() for s in rule["from"]}
    assert tabled == set(EDGE_CASES), (
        f"rule table and fixtures disagree: missing={sorted(tabled - set(EDGE_CASES))} "
        f"stale={sorted(set(EDGE_CASES) - tabled)}")
    return EDGE_CASES


def only(out):
    assert len(out["transitions"]) == 1, out["lines"]
    return out["transitions"][0]


class LegalTransitions(unittest.TestCase):
    def test_fixture_set_covers_every_rule_and_source(self):
        edge_cases()

    def test_every_legal_transition_fires_from_a_matching_record(self):
        for (rule, src), record in sorted(edge_cases().items()):
            out = lifecycle.plan([record], now=NOW)
            self.assertEqual(out["verdict"], "OK", f"{rule}/{src}: {out['lines']}")
            t = only(out)
            self.assertEqual((t["from"], t["to"], t["rule"]),
                             (src, lifecycle.RULES[rule]["to"], rule),
                             f"{rule}/{src}: {out['lines']}")

    def test_revoked_asset_proposes_nothing_without_gate_d(self):
        r = rec(state="revoked",
                tombstone={"asset": "rig-subject", "restore_forbidden": True},
                restore=RESTORE)
        out = lifecycle.plan([r], now=NOW)
        self.assertEqual(out["transitions"], [])
        self.assertEqual(out["verdict"], "OK")
        self.assertNotIn("rig-subject", out["loadable_after"])

    def test_healthy_asset_is_left_alone(self):
        out = lifecycle.plan([rec()], now=NOW)
        self.assertEqual(out["transitions"], [])
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["loadable_after"], ["rig-subject"])


class IllegalTransitions(unittest.TestCase):
    def test_no_edge_leaves_revoked_for_a_loadable_state(self):
        bad = [(s, d) for s, d in lifecycle.LEGAL if s == "revoked" and d in lifecycle.LOADABLE]
        self.assertEqual(bad, [],
                         "revocation lifted by a transition — it lifts only by "
                         "re-canonicalising the asset")

    def test_revoked_with_verified_restore_stays_revoked(self):
        # the evicted/revoked split: the same archive restores one and not the other
        out = lifecycle.plan([rec(state="revoked", restore=RESTORE,
                                  tombstone={"restore_forbidden": True})], now=NOW)
        self.assertEqual(out["transitions"], [])
        self.assertNotIn("rig-subject", out["loadable_after"])

    def test_undeclared_state_is_refused_and_reported(self):
        out = lifecycle.plan([rec(state="quantum")], now=NOW)
        self.assertEqual(out["verdict"], "INSOLVENT")
        self.assertEqual([r["rule"] for r in out["refused"]], ["declared_state"])
        self.assertIn("state_undeclared", [v["violation"] for v in out["violations"]])

    def test_eviction_without_a_restore_point_is_refused_not_silently_dropped(self):
        out = lifecycle.plan([rec(**NEGATIVE_UTILITY)], now=NOW)
        self.assertEqual(out["verdict"], "INSOLVENT")
        r = out["refused"][0]
        self.assertEqual(r["rule"], "utility_evict")
        self.assertIn("restore point", " ".join(r["missing"]))
        self.assertEqual(out["solvency"]["eviction_set"], [])
        self.assertIn("utility_threshold_breached",
                      [v["violation"] for v in out["violations"]])

    def test_eviction_without_gate_d_is_refused(self):
        out = lifecycle.plan([rec(**NEGATIVE_UTILITY, restore=RESTORE)], now=NOW)
        self.assertEqual(out["verdict"], "INSOLVENT")
        self.assertIn("Gate-D", " ".join(out["refused"][0]["missing"]))

    def test_deprecated_may_not_reenter_service_without_a_repair_record(self):
        out = lifecycle.plan([rec(state="deprecated", done_test={"status": "green"})],
                             now=NOW)
        self.assertEqual(out["transitions"], [],
                         "deprecated returns to service only on a repair record")
        self.assertIn("rig-subject", out["loadable_after"])   # routed, still flagged


class RevocationOverridesUtility(unittest.TestCase):
    HIGH = {"counterfactual_gain": 4.0, "retrieval_latency": 0.01,
            "token_footprint": 0.02, "execution_overhead": 0.01, "trials": 20}

    def test_best_scoring_asset_is_revoked_on_negative_attribution(self):
        asset = rec(rid="rig-scraper-retry-shortcut", utility=self.HIGH, **NEG_REVOKE)
        out = lifecycle.plan([asset], now=NOW)
        t = only(out)
        self.assertEqual((t["to"], t["rule"]), ("revoked", "revocation"))
        self.assertNotIn("rig-scraper-retry-shortcut", out["loadable_after"])
        self.assertEqual(out["solvency"]["revocation_set"], ["rig-scraper-retry-shortcut"])

    def test_utility_feed_alone_would_have_kept_it(self):
        # same asset, attribution clean: utility keeps it. The revocation feed is
        # orthogonal, which is the whole point of arXiv:2608.12851.
        clean = rec(rid="rig-scraper-retry-shortcut", utility=self.HIGH)
        self.assertEqual(lifecycle.plan([clean], now=NOW)["transitions"], [])

    def test_open_risk_flag_revokes_without_any_attribution_count(self):
        asset = rec(utility=self.HIGH, attribution={"negative": 0,
                                                    "open_risk_flags": ["unsafe-shortcut"]})
        out = lifecycle.plan([asset], now=NOW)
        self.assertEqual(only(out)["to"], "revoked")

    def test_revocation_beats_utility_eviction_when_both_apply(self):
        asset = rec(utility=self.HIGH, **NEG_REVOKE, restore=RESTORE, gate_d=APPROVE)
        out = lifecycle.plan([asset], now=NOW)
        self.assertEqual(only(out)["to"], "revoked")

    def test_revocation_carries_a_tombstone_that_forbids_restore(self):
        out = lifecycle.plan([rec(**NEG_REVOKE)], now=NOW)
        tom = only(out)["tombstone"]
        self.assertTrue(tom["restore_forbidden"])
        self.assertEqual(tom["at"], NOW)
        self.assertIn("negative reuse attribution", tom["because"])


class ReasonsAreRecorded(unittest.TestCase):
    def test_every_transition_carries_reason_and_timestamp(self):
        out = lifecycle.plan(lifecycle.example_assets(), now=NOW)
        self.assertTrue(out["transitions"])
        for t in out["transitions"]:
            self.assertTrue(t["reason"].strip(), t)
            self.assertEqual(t["at"], NOW, t)

    def test_utility_reason_shows_the_arithmetic(self):
        out = lifecycle.plan([rec(**NEGATIVE_UTILITY, restore=RESTORE, gate_d=APPROVE)],
                             now=NOW)
        self.assertIn("U(s)=-0.8000", only(out)["reason"])

    def test_unmeasured_asset_is_blind_not_zero(self):
        no_measure = rec(utility=None, usage={"uses": 0, "passes": 0, "runs": 0})
        out = lifecycle.plan([no_measure], now=NOW)
        self.assertEqual(out["transitions"], [])
        self.assertEqual(out["solvency"]["telemetry_blind"], ["rig-subject"])
        self.assertEqual(out["verdict"], "OK")

    def test_a_state_without_a_recorded_reason_is_a_violation(self):
        out = lifecycle.plan([rec(state_reason="", state_at="")], now=NOW)
        self.assertIn("state_unrecorded",
                      [v["violation"] for v in out["violations"]])
        self.assertEqual(out["verdict"], "INSOLVENT")


class ComputedRetention(unittest.TestCase):
    def test_utility_subtracts_every_cost_term(self):
        r = rec(utility={"counterfactual_gain": 1.0, "retrieval_latency": 0.2,
                         "token_footprint": 0.3, "execution_overhead": 0.1,
                         "trials": 5})
        self.assertAlmostEqual(lifecycle.utility(r, lifecycle.DEFAULT_CONFIG), 0.4)

    def test_a_few_trials_is_not_a_measurement(self):
        r = rec(utility={"counterfactual_gain": 0.1, "retrieval_latency": 0.9,
                         "token_footprint": 0.0, "execution_overhead": 0.0,
                         "trials": 2})
        self.assertIsNone(lifecycle.utility(r, lifecycle.DEFAULT_CONFIG))

    def test_activity_decays_exponentially_with_age_of_last_use(self):
        r = rec(usage={"uses": 8, "passes": 8, "runs": 8, "window_days": 90,
                       "last_used_days_ago": 45})
        self.assertAlmostEqual(
            lifecycle.activity(r, lifecycle.DEFAULT_CONFIG), 4.0, places=6)

    def test_threshold_is_configuration_not_a_hardcoded_opinion(self):
        keep = lifecycle.plan([rec(**NEGATIVE_UTILITY)], now=NOW,
                              config={"evict_utility_below": -1.0})
        self.assertEqual(keep["verdict"], "OK")
        self.assertEqual(keep["transitions"], [])
        purge = lifecycle.plan([rec(**NEGATIVE_UTILITY, restore=RESTORE,
                                   gate_d=APPROVE)], now=NOW)
        self.assertEqual(only(purge)["to"], "evicted")

    def test_quarantine_is_not_terminal(self):
        stale = rec(state="dormant", days_in_state=150,
                    usage={"uses": 0, "passes": 0, "runs": 0, "window_days": 180,
                           "last_used_days_ago": 240},
                    restore=RESTORE, gate_d=APPROVE)
        self.assertEqual(only(lifecycle.plan([stale], now=NOW))["to"], "evicted")
        fresh = dict(stale, days_in_state=10)
        self.assertEqual(lifecycle.plan([fresh], now=NOW)["verdict"], "OK")
        self.assertEqual(lifecycle.plan([fresh], now=NOW)["transitions"], [])


class PlanIsWriteFree(unittest.TestCase):
    def test_plan_never_touches_the_filesystem(self):
        def boom(*a, **k):
            raise AssertionError("plan() touched the filesystem")

        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for name in ("a.yaml", "b.jsonl"):
                (root / name).write_text('{"state": "active"}\n', encoding="utf-8")
            (root / "sub").mkdir()
            (root / "sub" / "c.txt").write_text("keep", encoding="utf-8")
            before = _tree_hash(root)
            cwd = os.getcwd()
            try:
                os.chdir(td)
                with mock.patch.object(builtins, "open", boom), \
                        mock.patch.object(pathlib.Path, "write_text", boom), \
                        mock.patch.object(pathlib.Path, "write_bytes", boom), \
                        mock.patch.object(pathlib.Path, "touch", boom), \
                        mock.patch.object(pathlib.Path, "unlink", boom), \
                        mock.patch.object(os, "remove", boom), \
                        mock.patch.object(os, "makedirs", boom), \
                        mock.patch.object(os, "mkdir", boom), \
                        mock.patch.object(os, "rename", boom), \
                        mock.patch.object(shutil, "rmtree", boom):
                    out = lifecycle.plan(lifecycle.example_assets(), now=NOW)
            finally:
                os.chdir(cwd)
            self.assertEqual(out["verdict"], "OK")
            self.assertTrue(out["transitions"])
            self.assertEqual(_tree_hash(root), before,
                             "plan() mutated the tree — proposing is not executing")


class PlantFailures(unittest.TestCase):
    """Every guard is proven to fire. Same state as a regression: the invariant
    must go RED, and the plant must not be inert."""

    EXPECTED = {
        "revocation": "revocation_missing",
        "utility_evict": "utility_threshold_breached",
        "decay_quarantine": "decay_floor_breached",
        "decay_evict": "park_overdue",
        "one_way_door": "revocation_revived",
        "record_reason": "transition_unexplained",
        "tombstone": "tombstone_missing",
        "state_record": "state_unrecorded",
    }

    def test_the_unplanted_estate_is_solvent(self):
        out = lifecycle.plan(lifecycle.example_assets(), now=NOW)
        self.assertEqual(out["verdict"], "OK", out["lines"])

    def test_every_plant_guard_turns_the_estate_insolvent(self):
        assets = lifecycle.example_assets()
        for plant, expected in sorted(self.EXPECTED.items()):
            out = lifecycle.plan(assets, now=NOW, plants=[plant])
            self.assertEqual(out["verdict"], "INSOLVENT", f"{plant}: {out['lines']}")
            self.assertIn(expected, [v["violation"] for v in out["violations"]],
                          f"{plant}: {out['violations']}")
            self.assertEqual(out["plants_inert"], [], f"{plant} changed nothing")

    def test_planting_unknown_rule_is_reported_inert_not_silently_green(self):
        out = lifecycle.plan(lifecycle.example_assets(), now=NOW,
                             plants=["taste_preference"])
        self.assertEqual(out["verdict"], "OK")
        self.assertEqual(out["plants_inert"], ["taste_preference"])


class CliContract(unittest.TestCase):
    def test_plan_exits_zero_when_solvent_and_two_when_not(self):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc_ok = lifecycle.main(["plan", "--example", "--now", NOW])
            rc_red = lifecycle.main(["plan", "--example", "--now", NOW,
                                     "--plant", "revocation"])
        self.assertEqual(rc_ok, 0)
        self.assertEqual(rc_red, 2)
        self.assertIn("revocation_missing", buf.getvalue())

    def test_rules_lists_the_table_without_touching_state(self):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = lifecycle.main(["rules"])
        text = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("revoked", text)
        self.assertIn("no exit from 'revoked'", text)


    def test_assets_file_is_read_only_input(self):
        with tempfile.TemporaryDirectory() as td:
            f = pathlib.Path(td) / "estate.json"
            f.write_text('["nope"]', encoding="utf-8")
            with self.assertRaises(ValueError):
                lifecycle._read_assets(str(f))
            f.write_text('[{"id": "x", "state": "active"}]', encoding="utf-8")
            self.assertEqual(lifecycle._read_assets(str(f))[0]["id"], "x")

    def test_every_accepted_input_shape_loads(self):
        """Three shapes are documented; all three have to actually parse.

        The `[`-prefix test above covers the array. A pretty-printed object was
        the shape that used to traceback: `text.startswith("[")` was false, so it
        went down the JSONL path and `json.loads` failed on line 1.
        """
        row = {"id": "x", "state": "active", "reason": "r", "state_ts": "2026-08-01"}
        shapes = {
            "array.json": json.dumps([row]),
            "doc.json": json.dumps({"as_of": "2026-09-02", "assets": [row]}),
            "single.json": json.dumps(row),
            "one.jsonl": json.dumps(row),
            "many.jsonl": "\n".join(json.dumps(dict(row, id=f"a{i}"))
                                    for i in range(3)),
        }
        with tempfile.TemporaryDirectory() as td:
            for name, body in shapes.items():
                p = pathlib.Path(td) / name
                p.write_text(body, encoding="utf-8")
                want = 3 if name == "many.jsonl" else 1
                got = lifecycle._read_assets(str(p))
                self.assertEqual(len(got), want, f"{name} -> {len(got)} records")

    def test_malformed_input_is_a_named_refusal_never_a_traceback(self):
        """Exit 2 + `assets_unreadable:` on stderr, no stack trace, no stdout."""
        cases = {
            "broken.json": '{"assets": [ {"id": "d", ',
            "notdoc.json": '{"just": "an object with no assets"}',
            "badrow.jsonl": '{"id": "e"}\nnot json at all\n',
            "scalar.json": "42",
        }
        with tempfile.TemporaryDirectory() as td:
            for name, body in cases.items():
                p = pathlib.Path(td) / name
                p.write_text(body, encoding="utf-8")
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()) as out, \
                        contextlib.redirect_stderr(err):
                    rc = lifecycle.main(["plan", "--assets", str(p),
                                         "--now", "2026-09-02"])
                self.assertEqual(rc, 2, f"{name} -> rc={rc}")
                self.assertIn("assets_unreadable:", err.getvalue(), name)
                self.assertNotIn("Traceback", err.getvalue(), name)
                self.assertEqual(out.getvalue().strip(), "", f"{name} leaked a plan")
            missing = pathlib.Path(td) / "nope.json"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = lifecycle.main(["plan", "--assets", str(missing),
                                     "--now", "2026-09-02"])
            self.assertEqual(rc, 2)
            self.assertIn("assets_unreadable:", err.getvalue())


def _tree_hash(root: pathlib.Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = str(p.relative_to(root))
        out[rel] = "d" if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest()
    return out


if __name__ == "__main__":
    unittest.main(verbosity=2)
