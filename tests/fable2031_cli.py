"""The fable-2031 operator surface: 14 CLI verbs, their exit codes, their output keys.

Every case runs the real `bin/rig-capabilities` in a subprocess against either the
committed register/ledger or the hermetic fable2031 fixtures — no live corpus walk,
no route writes, no certify/self-test (the suite copies are the orchestrator's).
"""
from __future__ import annotations

import hashlib
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

FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"
CLI = REPO_ROOT / "bin" / "rig-capabilities"
CORPUS_FIXTURE = "tests/fixtures/fable2031/corpus"
WEEK = "2026-W36"

VERBS = ("corpus", "register", "converge", "realign", "expert-os", "evidence",
         "lease", "canary", "dispatch-verify", "estage", "model-route",
         "fabrication", "certify", "self-test")

# The three route targets must be byte-identical before and after every
# read-only/refusal call: dormant-by-default is the thing under test.
ROUTE_TARGETS = (
    Path.home() / ".rig/agent-doctrine/registries/model_registry.yaml",
    Path.home() / ".hermes/config.yaml",
    Path.home() / ".rig/grokbot-router/litellm.yaml",
)


def _route_hashes() -> dict:
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in ROUTE_TARGETS if p.is_file()}


class CliVerbTests(unittest.TestCase):
    """Exit codes and payload keys for every verb this slice adds."""

    @classmethod
    def setUpClass(cls):
        # canary/lease state goes to a throwaway root: ~/.rig/leases stays untouched.
        cls.state_root = tempfile.mkdtemp(prefix="fable2031-cli-")
        cls.env = dict(os.environ, RIG_LEASE_STATE_ROOT=cls.state_root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.state_root, ignore_errors=True)

    # ------------------------------------------------------------------ helpers
    def _run(self, *argv, env=None):
        proc = subprocess.run([sys.executable, str(CLI), *[str(a) for a in argv]],
                              capture_output=True, text=True, cwd=str(REPO_ROOT),
                              env=env or self.env)
        return proc.returncode, proc.stdout, proc.stderr

    def _json(self, *argv, env=None):
        rc, out, err = self._run(*argv, env=env)
        try:
            return rc, json.loads(out)
        except json.JSONDecodeError:  # keep the failure readable
            self.fail(f"{argv[0]}: stdout is not JSON (exit {rc})\n{out[:400]}\n{err[:400]}")

    def _context_week(self, week=WEEK) -> Path:
        return REPO_ROOT / ".context" / "realign" / week

    # ---------------------------------------------------------------- the surface
    def test_every_verb_advertising_itself(self):
        for verb in VERBS:
            rc, out, err = self._run(verb, "--help")
            self.assertEqual(rc, 0, f"{verb} --help exited {rc}: {err[:200]}")
            self.assertIn("usage:", out)
        # one root help proves wiring for the two verbs this file never invokes.
        rc, out, _ = self._run("--help")
        self.assertEqual(rc, 0)
        for verb in VERBS:
            self.assertIn(verb, out, f"{verb} missing from the root verb list")

    def test_docstring_documents_each_new_verb(self):
        head = CLI.read_text(encoding="utf-8").split('"""')[1]
        for verb in VERBS:
            self.assertIn(f"\n  {verb} ", head, f"{verb} has no docstring command line")

    # --------------------------------------------------------------------- corpus
    def test_corpus_scan_scores_the_fixture_corpus(self):
        rc, rep = self._json("corpus", "scan", "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, rep)
        self.assertTrue(rep["ok"], rep)
        self.assertEqual(rep["raw"], 22)
        self.assertEqual(rep["unique"], 20)
        self.assertLessEqual(rep["unclassified_rate"], 0.10)
        # one duplicate pair, one contradiction variant, one truncated card
        self.assertEqual(rep["duplicates"], 1)
        self.assertEqual(rep["contradiction_variants"], 1)
        self.assertEqual(rep["truncated"], 1)
        self.assertNotIn("roots_missing", rep)

    def test_corpus_scan_default_subcommand_is_scan(self):
        rc, rep = self._json("corpus", "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, rep)
        self.assertEqual(rep["unique"], 20)

    def test_corpus_scan_of_an_absent_root_is_red_not_empty_but_fine(self):
        rc, rep = self._json("corpus", "scan", "--root", "tests/fixtures/nope")
        self.assertEqual(rc, 1)
        self.assertFalse(rep["ok"])
        self.assertEqual(rep["reason"], "empty_corpus")
        self.assertEqual(rep["roots"][0]["present"], False)

    def test_corpus_classify_and_truncation(self):
        rc, out = self._json("corpus", "classify",
                             f"{CORPUS_FIXTURE}/01-corpus-scanner-build-card.md")
        self.assertEqual(rc, 0, out)
        self.assertFalse(out["unclassified"])
        self.assertTrue(out["subsystem"] and out["studio"] and out["type"])

        rc, out = self._json("corpus", "classify",
                             f"{CORPUS_FIXTURE}/18-sourdough-hydration-log.md")
        self.assertEqual(rc, 1, "an unclassifiable card must not exit green")
        self.assertTrue(out["unclassified"])
        self.assertEqual(out["reason"], "no_rule_matched")

        rc, out = self._json("corpus", "truncation",
                             f"{CORPUS_FIXTURE}/17-fuel-budget-sweep.md")
        self.assertEqual(rc, 0)
        self.assertTrue(out["truncated"])
        self.assertTrue(out["end_anchor"])

        rc, out = self._json("corpus", "classify")
        self.assertEqual(rc, 2, "a missing card path is a usage error")
        self.assertIn("card_missing", out["error"])

    # ------------------------------------------------------------------- register
    def test_register_validate_is_clean(self):
        rc, out = self._json("register", "validate")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["row_errors"], [])
        self.assertEqual(out["flagged_owners"], [])
        self.assertTrue(out["booked_qualified_conversation"]["ok"])
        self.assertTrue(out["ok"])
        self.assertEqual(out["rows"], 21)

    def test_register_diff_and_flags(self):
        rc, out = self._json("register", "diff",
                             str(FIX / "register-previous.csv"),
                             str(FIX / "register-current.csv"))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["counts"]["changed"], 3)
        self.assertEqual(out["counts"]["added"], 0)
        self.assertTrue(any(m["id"] == "capability_catalog_index"
                            for m in out["maturity_moves"]))

        rc, short = self._json("register", "diff", str(FIX / "register-current.csv"))
        self.assertEqual(rc, 2, "a one-argument diff is a usage error")
        self.assertEqual(short["error"], "diff_requires_two_csvs")

        rc, out = self._json("register", "flags")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["flagged_owners"], [])

    # ------------------------------------------------------------------- converge
    def test_converge_metrics_without_a_week(self):
        rc, out = self._json("converge")
        self.assertEqual(rc, 0, out)
        for key in ("c_t", "a_t", "e_cap", "rows_scored", "degenerate_targets"):
            self.assertIn(key, out)
        self.assertEqual(out["degenerate_targets"], [])

    def test_converge_week_without_a_prior_seals_nothing_but_passes(self):
        rc, out = self._json("converge", "--week", WEEK, "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, out["gate"])
        self.assertEqual(out["gate"]["verdict"], "BASELINE_ONLY")
        self.assertIn("booked_qualified_conversations", out["gate"]["causes"])
        self.assertEqual(out["bookings"]["count"], 0)
        self.assertFalse(self._context_week().exists(),
                         "converge must never write the week's artifacts")

    def test_converge_flags_a_failing_week(self):
        # A prior week + zero qualifying bookings is a real FAIL, not a baseline.
        rc, out = self._json("converge", "--week", WEEK, "--root", CORPUS_FIXTURE,
                             "--previous", str(FIX / "register-previous.csv"))
        self.assertEqual(rc, 1, out["gate"])
        self.assertEqual(out["gate"]["verdict"], "FAIL")
        self.assertIn("booked_qualified_conversations", out["gate"]["causes"])

    # -------------------------------------------------------------------- realign
    def test_realign_is_dry_by_default_and_prints_the_baseline_verdict(self):
        rc, out = self._json("realign", "--week", WEEK, "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, out)
        self.assertTrue(out["dry_run"])
        self.assertFalse(out["apply"])
        self.assertFalse(out["wrote"])
        self.assertFalse(out["sealed"], out["seal_reason"])
        self.assertEqual(out["verdict"], "BASELINE_ONLY")
        self.assertEqual(out["row_errors"], [])
        self.assertFalse(self._context_week().exists(),
                         "dry realign wrote .context/realign — it may only read")

    def test_realign_dry_flag_is_a_noop_alias(self):
        rc, out = self._json("realign", "--dry", "--week", WEEK, "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, out)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["verdict"], "BASELINE_ONLY")

    def test_realign_dry_writes_nothing_even_named_for_another_week(self):
        rc, out = self._json("realign", "--week", "2026-W35", "--root", CORPUS_FIXTURE)
        self.assertEqual(rc, 0, out)
        self.assertFalse((REPO_ROOT / ".context" / "realign" / "2026-W35").exists())

    # ------------------------------------------------------------------ expert-os
    def test_expert_os_phases_is_a_flat_status_map(self):
        rc, out = self._json("expert-os", "phases")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(out), 12, "phases 1-10 gated, 11 truncated, 12 absent")
        self.assertEqual(out["1"], "gated")
        self.assertEqual(out["10"], "gated")
        self.assertEqual(out["11"], "objective_only_truncated")
        self.assertEqual(out["12"], "absent_at_source")

    def test_expert_os_truncated_phases_can_never_pass(self):
        for phase, status in ((11, "objective_only_truncated"),
                              (12, "absent_at_source")):
            rc, out = self._json("expert-os", "advance", "--phase", phase,
                                 "--evidence", str(FIX / "iqrsqpi-run.json"))
            self.assertEqual(rc, 1, f"phase {phase} reported ok")
            self.assertFalse(out["ok"])
            self.assertEqual(out["status"], status)

        rc, out = self._json("expert-os", "advance", "--phase", 99)
        self.assertEqual(rc, 2, "an unknown phase is a usage error, not a failed gate")
        self.assertFalse(out["ok"])
        self.assertTrue(out["error"])

        rc, out = self._json("expert-os", "advance")
        self.assertEqual(rc, 2, "--phase is required; that is a usage error")
        self.assertEqual(out["error"], "phase_required")

    def test_expert_os_advance_reports_missing_then_satisfied(self):
        rc, out = self._json("expert-os", "advance", "--phase", 1)
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["title"], "Select the problem to own")
        self.assertEqual(len(out["missing"]), len(out["deliverables"]))

        filled = {slug: f"docs/ASSUMPTIONS.md#{slug}"
                  for slug in out["deliverables"]}
        handle, evidence = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w") as fh:
            json.dump(filled, fh)
        try:
            rc, out = self._json("expert-os", "advance", "--phase", 1,
                                 "--evidence", evidence)
            self.assertEqual(rc, 0, out)
            self.assertTrue(out["ok"])
            self.assertEqual(out["missing"], [])
            self.assertTrue(out["gate"])
        finally:
            os.unlink(evidence)

        rc, out = self._json("expert-os", "advance", "--phase", 1,
                             "--evidence", "tests/fixtures/nope.json")
        self.assertEqual(rc, 2, "an unreadable evidence file is a usage error")
        self.assertIn("evidence_file_missing", out["error"])

    # ------------------------------------------------------------------- evidence
    def test_evidence_validate_is_clean_on_the_committed_ledger(self):
        rc, out = self._json("evidence", "validate")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["invalid"], [])
        self.assertEqual(out["rows"], 6)
        self.assertTrue(out["ok"])

    def test_evidence_rule_three_rejects_an_unverified_resume_claim(self):
        rc, out = self._json("evidence", "validate", "--ledger",
                             str(FIX / "evidence-ledger-unverified-resume.csv"))
        self.assertEqual(rc, 1, out)
        self.assertFalse(out["ok"])
        reasons = {e for row in out["invalid"] for e in row["errors"]}
        self.assertIn("unverified_claim_on_resume", reasons)
        for trap in ("evidence_missing", "unknown_claim_type:asserted",
                     "unknown_allowed_use:investor", "confidence_out_of_range:1.4",
                     "confidence_not_numeric:high", "missing_field:evidence"):
            self.assertIn(trap, reasons)

    def test_evidence_resume_lists_only_rule_three_clean_claims(self):
        rc, out = self._json("evidence", "resume")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["resume_eligible"], 3)
        self.assertEqual(len(out["ids"]), 3)

        rc, out = self._json("evidence", "validate", "--ledger", "nope.csv")
        self.assertEqual(rc, 1)
        self.assertEqual(out["error"], "ledger_empty_or_missing")

    # ---------------------------------------------------------------------- lease
    def test_lease_list_reports_the_state_root_it_was_told_to_use(self):
        rc, out = self._json("lease", "list")
        self.assertEqual(rc, 0, out)
        self.assertEqual(Path(out["state_root"]).resolve(), Path(self.state_root).resolve())
        self.assertEqual(out["ceiling"], 16)
        self.assertEqual(out["leases"], [])

    def test_lease_passthrough_preserves_the_denial_exit_and_the_reason(self):
        rc, out, _ = self._run("lease", "acquire", "--task", "",
                               "--worktree", "/tmp", "--branch", "x")
        self.assertEqual(rc, 2, "lease denial must surface as exit 2")
        self.assertIn("task_id_required", out)

        rc, out = self._json("lease", "assert", "--task", "nope",
                             "--cwd", str(REPO_ROOT), "--toplevel", str(REPO_ROOT),
                             "--branch", "fable-2031")
        self.assertEqual(rc, 2, out)
        self.assertEqual(out["reason"], "WORKTREE_ASSERTION_FAILED")
        self.assertEqual(out["mismatch"], "no_active_lease")

    # --------------------------------------------------------------------- canary
    def test_canary_mint_current_rotate(self):
        rc, out = self._json("canary", "current", "--task", "cli-canary")
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["reason"], "canary_never_minted")

        rc, minted = self._json("canary", "mint", "--task", "cli-canary")
        self.assertEqual(rc, 0, minted)
        self.assertTrue(minted["canary_id"])

        rc, seen = self._json("canary", "current", "--task", "cli-canary")
        self.assertEqual(rc, 0, seen)
        self.assertEqual(seen["canary_id"], minted["canary_id"])

        rc, rotated = self._json("canary", "rotate", "--task", "cli-canary")
        self.assertEqual(rc, 0, rotated)
        self.assertNotEqual(rotated["canary_id"], minted["canary_id"],
                            "a canary that never rotates detects nothing")

    # ------------------------------------------------------------- dispatch-verify
    def test_dispatch_verify_offline_prefilter_passes_the_honest_packet(self):
        rc, out = self._json("dispatch-verify",
                             "tests/fixtures/fable2031/handoff-honest.json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["mode"], "offline_prefilter")
        self.assertTrue(out["tac_bound"]["canary_records_excluded"])
        self.assertGreaterEqual(out["tac_bound"]["dropped_canary_records"], 1)

    def test_dispatch_verify_exits_two_for_every_fabrication_shape(self):
        for name in ("fabricated", "phantom", "tampered"):
            rc, out = self._json("dispatch-verify",
                                 f"tests/fixtures/fable2031/handoff-{name}.json",
                                 "--offline")
            self.assertEqual(rc, 2, f"{name}: {out}")
            self.assertEqual(out["verdict"], "FABRICATED")
            self.assertTrue(out["reasons"])

    def test_dispatch_verify_cannot_emit_a_pass_it_has_not_earned(self):
        rc, out = self._json("dispatch-verify",
                             "tests/fixtures/fable2031/handoff-honest.json", "--verify")
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["verdict"], "BLOCKED")
        self.assertEqual(out["reasons"], ["checkout_missing"])
        self.assertEqual(out["mode"], "full_ladder")

        rc, out, _ = self._run("dispatch-verify",
                               "tests/fixtures/fable2031/handoff-honest.json",
                               "--verify", "--offline")
        self.assertEqual(rc, 2)
        self.assertIn("offline_and_verify_conflict", out)

        rc, out = self._json("dispatch-verify", "tests/fixtures/nope.json")
        self.assertEqual(rc, 2)
        self.assertIn("packet_missing", out["error"])

    # ---------------------------------------------------------------------- estage
    def test_estage_score_compare_verdict(self):
        rc, out = self._json("estage", "score",
                             "tests/fixtures/fable2031/replay-opus.json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(out["runs"]), 3)
        self.assertEqual(out["weights"], {"fail": 0.6, "cost": 0.25, "turns": 0.15})
        self.assertAlmostEqual(out["mean_e_stage"], 0.3825, places=6)

        rc, out = self._json("estage", "compare",
                             "tests/fixtures/fable2031/replay-opus.json",
                             "tests/fixtures/fable2031/replay-fable.json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["n"], 3)
        self.assertTrue(out["strictly_lower_everywhere"])

        rc, out = self._json("estage", "verdict",
                             "--manifest", str(FIX / "golden-strategy.json"),
                             "--baseline", str(FIX / "replay-opus.json"),
                             "--candidate", str(FIX / "replay-fable.json"))
        self.assertEqual(rc, 0, out)
        self.assertTrue(out["promote"], out["reasons"])
        self.assertEqual(out["status"], "DORMANT")
        # a synthetic fixture replay is never presented as a recorded run
        self.assertEqual(out["candidate_provenance"], "fixture_only_not_a_recorded_run")

        rc, out = self._json("estage", "verdict",
                             "--manifest", str(FIX / "golden-strategy.json"),
                             "--baseline", str(FIX / "replay-opus.json"),
                             "--candidate", str(FIX / "replay-fable.json"),
                             "--forced-tool-choice")
        self.assertEqual(rc, 1, out)
        self.assertFalse(out["promote"])
        self.assertEqual(out["reasons"], ["forced_tool_choice_harness"])

        rc, out = self._json("estage", "verdict",
                             "--manifest", str(FIX / "golden-strategy.json"))
        self.assertEqual(rc, 2)
        self.assertIn("replays", out["error"])

    # ----------------------------------------------------------------- model-route
    def test_model_route_reads_and_refuses_without_writing(self):
        before = _route_hashes()
        self.assertEqual(len(before), 3, "a route target vanished mid-test")

        rc, plan = self._json("model-route")
        self.assertEqual(rc, 0, plan)
        self.assertTrue(plan["dry_run"])
        self.assertIs(plan["writes"], False)
        self.assertTrue(plan["ungoverned_route_detected"]["detected"],
                        "the ungoverned OMP designer binding must be disclosed")

        rc, audit = self._json("model-route", "audit-fallbacks")
        self.assertEqual(rc, 0, audit)
        self.assertTrue(audit["ok"])
        self.assertFalse(audit["governance_incident"])

        rc, tool = self._json("model-route", "audit-tool-choice")
        self.assertEqual(rc, 0, tool)
        self.assertTrue(tool["ok"])

        # Refusal must happen before the route module is reachable: zero writes.
        rc, out, _ = self._run("model-route", "--apply")
        self.assertEqual(rc, 2, out)
        self.assertEqual(json.loads(out)["reason"], "gate_d_required")

        rc, out, _ = self._run("model-route", "--apply", "--gate-d", "APPROVE nope")
        self.assertEqual(rc, 2, out)
        self.assertEqual(json.loads(out)["reason"], "max_budget_required")

        # An unapproved run id is refused by Gate-D itself, still before any write.
        rc, out = self._json("model-route", "--apply", "--gate-d",
                             "no-such-gate-d-run", "--max-budget-usd", "20")
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["reason"], "gate_d_required")
        self.assertEqual(out["writes"], 0)

        self.assertEqual(_route_hashes(), before,
                         "model-route wrote a route target without an approved Gate-D run")

    # ----------------------------------------------------------------- fabrication
    def test_fabrication_reports_the_ledger_it_actually_has(self):
        rc, out = self._json("fabrication")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["ladder"]["schema"], "rig.verdict-ladder.v1")
        self.assertGreaterEqual(len(out["ladder"]["rungs"]), 3)
        rates = out["rates"]
        self.assertEqual(rates["window_days"], 30)
        if not rates["ledger_present"]:
            self.assertEqual(rates["total"], 0)
            self.assertIn("no rate fabricated from nothing", rates["note"])

    def test_fabrication_window_flag_reaches_the_report(self):
        rc, out = self._json("fabrication", "--since-days", "7")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["rates"]["window_days"], 7)

    # ------------------------------------------------ documented script spellings
    def test_documented_script_spellings_all_parse(self):
        # The plan and the canonical assets spell these with `--json` and the long
        # flag names; a form that argparse rejects is a broken operator surface.
        rc, out = self._json("corpus", "--roots", CORPUS_FIXTURE, "--json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["unique"], 20)

        rc, out = self._json("register", "--validate", "--json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["row_errors"], [])

        rc, out = self._json("evidence", "--validate", "--json")
        self.assertEqual(rc, 0, out)

        rc, out = self._json("expert-os", "phases", "--json")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["12"], "absent_at_source")

        rc, out = self._json("fabrication", "--json")
        self.assertEqual(rc, 0, out)

    def test_realign_bookings_override_scores_without_writing(self):
        # run_week has no bookings override, so the override path goes through the
        # weekly gate and must say plainly that it wrote nothing.
        rc, out = self._json("realign", "--week", WEEK, "--root", CORPUS_FIXTURE,
                             "--bookings", str(FIX / "bookings-valid.json"))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["bookings"]["count"], 2)
        self.assertFalse(out["wrote"])
        self.assertTrue(out["note"])
        self.assertFalse(self._context_week().exists())

    def test_model_route_run_id_alias_still_refuses_and_writes_nothing(self):
        before = _route_hashes()
        rc, out = self._json("model-route", "--apply", "--gate-d-run-id",
                             "no-such-gate-d-run", "--max-budget-usd", "20")
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["reason"], "gate_d_required")
        self.assertEqual(out["writes"], 0)
        self.assertEqual(_route_hashes(), before,
                         "an unapproved Gate-D run id must not move a route target")

    def test_estage_studio_override_must_match_the_manifest(self):
        rc, out = self._json("estage", "verdict",
                             "--manifest", str(FIX / "golden-strategy.json"),
                             "--baseline", str(FIX / "replay-opus.json"),
                             "--candidate", str(FIX / "replay-fable.json"),
                             "--studio", "GTM")
        self.assertEqual(rc, 1, out)
        self.assertFalse(out["promote"])
        self.assertEqual(out["reasons"], ["studio_mismatch"])
        self.assertEqual(out["manifest_studio"], "Strategy")


    # ------------------------------------------------------- certify / self-test
    def test_certify_accepts_a_gate_filter_without_running_the_suite(self):
        # `--only` on an unknown gate must return red-fast: proves the verb is
        # wired and that it never falls through to the 300 s suite gate.
        rc, out = self._json("certify", "--only", "no_such_gate")
        self.assertEqual(rc, 1, out)
        self.assertEqual(out["gates"], {})
        self.assertFalse(out["verdict"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
