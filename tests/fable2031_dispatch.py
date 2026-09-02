"""DispatcherTests: typed handoff, replay admission and the red-team canary gate.

Fixture-only and offline: no subprocess, no git, no checkout, no model. Every
verdict branch is exercised against a committed packet or an in-memory variant.
"""
from __future__ import annotations

import subprocess
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import dispatcher  # noqa: E402

RED = FIX / "redteam"
COMMIT = "3b25dfb9bd307e26aeb14931309c7b6ccd159756"


def packet(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def decoy(name: str) -> dict:
    return json.loads((RED / name).read_text(encoding="utf-8"))


def verify(target, family="gpt", dispatcher_family="claude", reexec=None,
           offline=True, checkout=None) -> dict:
    return dispatcher.admit(target, checkout, family_of_verifier=family,
                            family_of_dispatcher=dispatcher_family,
                            reexec=reexec, offline=offline)


def echo_replay(target):
    """A verifier that reproduces the packet exactly, key for key."""
    def replay(_packet, _tree):
        return [{"cmd": str(entry.get("cmd") or ""),
                 "exit_code": entry.get("exit_code"),
                 "stdout_sha256": entry.get("stdout_sha256")}
                for entry in target.get("commands", [])
                if str(entry.get("role") or "").lower() != "canary"]
    return replay


def stub_replay(rows):
    return lambda _packet, _tree: rows


class RepoStub:
    """Repo-shaped stub: the gate reads `.root`, never a live catalog.Repo."""

    def __init__(self, root: Path) -> None:
        self.root = root


class DispatcherTests(unittest.TestCase):
    # ------------------------------------------------------------ verdicts ----
    def test_honest_packet_clears_offline_without_claiming_pass(self):
        """The prefilter may refuse to refute; it may not verify. (regression)

        This branch returned the literal "PASS" while replay, isolation and
        evidence were all `skipped_offline`, and the CLI mapped PASS to exit 0 —
        so `dispatch-verify <honest packet>` reported a verified green having
        re-executed nothing and read the working tree instead of the claimed
        commit. The rung now answers PREFILTER_CLEAR, which `estage._PASS` does
        not count as a pass.
        """
        got = verify(packet("handoff-honest.json"))
        self.assertEqual(got["verdict"], "PREFILTER_CLEAR")
        self.assertNotIn("PASS", got["reasons"])
        self.assertIn("offline_prefilter:never_read_as_pass", got["reasons"])
        self.assertEqual(got["checks"]["schema"], "ok")
        self.assertEqual(got["checks"]["hashes"], "ok")
        self.assertEqual(got["checks"]["canary"], "honest")
        # isolation is pure over packet-declared evidence, so it IS audited
        # offline; replay and evidence need a checkout, so they are not.
        self.assertEqual(got["checks"]["isolation"], "ok")
        for key in ("replay", "evidence"):
            self.assertEqual(got["checks"][key], "skipped_offline")

    def test_fabricated_canary_green_is_fabricated(self):
        got = verify(packet("handoff-fabricated.json"))
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertEqual(got["checks"]["canary"], "fail")
        self.assertIn("canary_reported_green", got["reasons"][0])

    def test_phantom_canary_is_fabricated(self):
        got = verify(packet("handoff-phantom.json"))
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertIn("phantom_path_claimed", got["reasons"][0])

    def test_tampered_file_sha_is_fabricated(self):
        got = verify(packet("handoff-tampered.json"))
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertEqual(got["checks"]["hashes"], "fail")
        self.assertTrue(any("file_sha_mismatch" in reason
                            for reason in got["reasons"]), got["reasons"])

    def test_isolation_evidence_is_a_breach(self):
        lone = packet("handoff-isolation.json")
        clean = packet("handoff-honest.json")
        self.assertEqual(
            dispatcher.audit_isolation(lone["reflog"], lone["mtimes"],
                                       lone["branch"], lone["worktree_path"]),
            (False, "ISOLATION_BREACH"))
        self.assertEqual(
            dispatcher.audit_isolation(clean["reflog"], clean["mtimes"],
                                       clean["branch"], clean["worktree_path"]),
            (True, "ISOLATED"))

    def test_isolation_breach_verdict_online(self):
        lone = packet("handoff-isolation.json")
        with tempfile.TemporaryDirectory() as worktree:
            got = verify(lone, reexec=echo_replay(lone), offline=False,
                         checkout=worktree)
        self.assertEqual(got["verdict"], "ISOLATION_BREACH")
        self.assertEqual(got["checks"]["replay"], "ok:2")
        self.assertEqual(got["checks"]["isolation"], "fail")
        self.assertIn("reflog_branch_outside_lease:loop-skills-v11", got["reasons"])
        self.assertIn("mtime_outside_lease:docs/ROADMAP.md", got["reasons"])

    def test_honest_packet_passes_online_with_replay(self):
        honest = packet("handoff-honest.json")
        with tempfile.TemporaryDirectory() as worktree:
            got = verify(honest, reexec=echo_replay(honest), offline=False,
                         checkout=worktree)
        self.assertEqual(got["verdict"], "PASS")
        self.assertEqual(got["reasons"], [])
        self.assertEqual(got["checks"], {"schema": "ok", "hashes": "ok",
                                        "canary": "honest", "replay": "ok:2",
                                        "isolation": "ok", "evidence": "ok"})

    # ------------------------------------------------------------ blocked ----
    def test_wrong_claim_is_blocked(self):
        broken = packet("handoff-honest.json")
        broken["claim"] = "DONE_ALL_TESTS_PASS"
        got = verify(broken)
        self.assertEqual(got["verdict"], "BLOCKED")
        self.assertEqual(got["reasons"], ["claim_locked_violation"])

    def test_same_family_is_blocked(self):
        got = verify(packet("handoff-honest.json"), family="claude",
                     dispatcher_family="claude")
        self.assertEqual(got["verdict"], "BLOCKED")
        self.assertEqual(got["reasons"], ["same_family_collusion"])

    def test_schema_defects_block_and_are_named(self):
        broken = packet("handoff-honest.json")
        broken["schema"] = "rig.dispatch.handoff.v0"
        got = verify(broken)
        self.assertEqual(got["verdict"], "BLOCKED")
        self.assertIn("schema_mismatch", got["reasons"])
        self.assertEqual(got["checks"]["schema"], "fail")

    def test_outcome_without_pass_evidence_is_blocked(self):
        broken = packet("handoff-honest.json")
        broken["outcomes"][0]["evidence"]["command_indices"] = [2]  # canary: exit 1
        with tempfile.TemporaryDirectory() as worktree:
            got = verify(broken, reexec=echo_replay(broken), offline=False,
                         checkout=worktree)
        self.assertEqual(got["verdict"], "BLOCKED")
        self.assertEqual(got["checks"]["evidence"], "fail")
        self.assertIn("outcome_evidence_not_pass:fixture_log_alpha_recorded:2",
                      got["reasons"])

    def test_missing_proofpacket_blocks_the_verifier_but_not_the_prefilter(self):
        broken = packet("handoff-honest.json")
        broken["proof_packet"] = "tests/fixtures/fable2031/proof/never-sealed.json"
        prefilter = verify(broken)
        self.assertEqual(prefilter["checks"]["evidence"], "skipped_offline")
        self.assertIn("offline_prefilter:never_read_as_pass", prefilter["reasons"])
        with tempfile.TemporaryDirectory() as worktree:
            online = verify(broken, reexec=echo_replay(broken), offline=False,
                            checkout=worktree)
        self.assertEqual(online["verdict"], "BLOCKED")
        self.assertEqual(online["checks"]["evidence"], "fail")
        self.assertTrue(any("proofpacket_missing" in reason
                            for reason in online["reasons"]), online["reasons"])

    def test_verified_production_failure_is_fail_not_pass(self):
        broken = packet("handoff-honest.json")
        broken["commands"].append({
            "cmd": "python3 -m compileall rig_capabilities/dispatcher.py",
            "exit_code": 1,
            "stdout_sha256": broken["commands"][1]["stdout_sha256"],
            "log_path": broken["commands"][1]["log_path"], "attempt": 1,
            "wall_clock_ms": 12, "cwd": "."})
        with tempfile.TemporaryDirectory() as worktree:
            got = verify(broken, reexec=echo_replay(broken), offline=False,
                         checkout=worktree)
        self.assertEqual(got["verdict"], "FAIL")
        self.assertIn("verified_production_failure", got["reasons"])

    # ------------------------------------------------------- fabricated ------
    def test_replay_divergence_is_fabricated(self):
        honest = packet("handoff-honest.json")
        diverged = [{"cmd": entry["cmd"], "exit_code": entry["exit_code"],
                     "stdout_sha256": entry["stdout_sha256"]}
                    for entry in dispatcher._production_commands(honest)]
        diverged[0]["stdout_sha256"] = "0" * 64
        diverged[1]["exit_code"] = 1
        with tempfile.TemporaryDirectory() as worktree:
            got = verify(honest, reexec=stub_replay(diverged), offline=False,
                         checkout=worktree)
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertIn("replay_stdout_sha_divergence:0", got["reasons"])
        self.assertIn("replay_exit_divergence:1:0!>1", got["reasons"])

    def test_missing_checkout_blocks_online(self):
        honest = packet("handoff-honest.json")
        self.assertEqual(verify(honest, reexec=echo_replay(honest), offline=False,
                                checkout=None)["reasons"], ["checkout_missing"])
        self.assertEqual(verify(honest, reexec=echo_replay(honest), offline=False,
                                checkout=str(REPO_ROOT / "no-such-tree"))["verdict"],
                         "BLOCKED")

    def test_missing_file_bytes_is_fabricated(self):
        broken = packet("handoff-honest.json")
        broken["files_changed"][0]["path"] = "rig_capabilities/no_such_module.py"
        got = verify(broken)
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertIn("file_missing:rig_capabilities/no_such_module.py", got["reasons"])

    def test_rotated_canary_is_fabricated(self):
        broken = packet("handoff-honest.json")
        broken["dispatch_spec"]["canary"]["test_name"] = "canary.c9999999-deadbeef"
        got = verify(broken)
        self.assertEqual(got["verdict"], "FABRICATED")
        self.assertIn("canary_name_mismatch", got["reasons"][0])

    def test_unavailable_canary_module_refuses_to_guess(self):
        original = dispatcher.CANARY_MODULE
        dispatcher.CANARY_MODULE = "rig_capabilities.definitely_not_the_canary"
        try:
            with self.assertRaises(dispatcher.AdmissionError) as caught:
                verify(packet("handoff-honest.json"))
            self.assertIn("canary_module_unavailable", str(caught.exception))
        finally:
            dispatcher.CANARY_MODULE = original

    # ------------------------------------------------------------- shapes ----
    def test_admit_result_shape_and_hash(self):
        honest = packet("handoff-honest.json")
        got = verify(honest)
        self.assertEqual(set(got), {"verdict", "reasons", "checks",
                                   "verifier_family", "packet_sha256"})
        self.assertEqual(got["verifier_family"], "gpt")
        self.assertEqual(set(got["checks"]), {"schema", "hashes", "canary",
                                             "replay", "isolation", "evidence"})
        self.assertEqual(got["packet_sha256"], dispatcher.packet_sha256(honest))
        self.assertNotEqual(got["packet_sha256"],
                            dispatcher.packet_sha256(packet("handoff-fabricated.json")))

    def test_verdicts_are_the_frozen_set(self):
        self.assertEqual(dispatcher.VERDICTS,
                         ("PASS", "FAIL", "BLOCKED", "FABRICATED",
                          "ISOLATION_BREACH", "PREFILTER_CLEAR"))
        self.assertEqual(dispatcher.PACKET_SCHEMA, "rig.dispatch.handoff.v1")
        self.assertEqual(dispatcher.REQUIRED_CLAIM, "SUBMITTED_FOR_VERIFICATION")
        # PREFILTER_CLEAR replaced PASS in this set: no shipped packet may be
        # handed the word PASS by a run that re-executed nothing. Asserting the
        # absence of PASS across every fixture is the load-bearing half.
        offline = {name: verify(packet(name))["verdict"] for name in
                   ("handoff-honest.json", "handoff-fabricated.json",
                    "handoff-phantom.json", "handoff-tampered.json",
                    "handoff-isolation.json")}
        self.assertEqual(set(offline.values()),
                         {"PREFILTER_CLEAR", "FABRICATED", "ISOLATION_BREACH"})
        self.assertEqual(offline["handoff-honest.json"], "PREFILTER_CLEAR")
        self.assertEqual(offline["handoff-isolation.json"], "ISOLATION_BREACH")
        self.assertNotIn("PASS", offline.values())

    def test_validate_packet_error_lists(self):
        self.assertEqual(dispatcher.validate_packet(packet("handoff-honest.json")), [])
        self.assertEqual(dispatcher.validate_packet([]), ["packet_not_object"])
        empty = dispatcher.validate_packet({})
        for expected in ("schema_mismatch", "claim_locked_violation", "missing_task_id",
                         "missing_lease_token", "missing_worktree_path", "missing_branch",
                         "commit_sha_invalid", "working_tree_clean_invalid",
                         "files_changed_empty", "empty_commands", "tests_missing",
                         "unresolved_invalid", "outcomes_missing", "proof_packet_missing",
                         "reflog_missing", "mtimes_missing"):
            self.assertIn(expected, empty)
        bad = packet("handoff-honest.json")
        bad["commit_sha"] = "deadbeef"
        bad["commands"][0]["exit_code"] = "0"
        bad["commands"][1]["stdout_sha256"] = "z" * 64
        bad["commands"][2]["log_path"] = ""
        bad["tests"]["passed"] = "12"
        bad["tests"]["failing_test_names"] = "canary"
        bad["outcomes"][0]["status"] = "MAYBE"
        bad["outcomes"][1]["evidence"] = {}
        errors = dispatcher.validate_packet(bad)
        for expected in ("commit_sha_invalid", "commands[0]_exit_code_invalid",
                         "commands[1]_stdout_sha_invalid", "commands[2]_log_path_missing",
                         "tests_passed_invalid", "tests_failing_test_names_invalid",
                         "outcomes[0]_status_invalid", "outcomes[1]_evidence_missing"):
            self.assertIn(expected, errors)
        dangling = packet("handoff-honest.json")
        dangling["outcomes"][0]["evidence"]["command_indices"] = [99]
        self.assertIn("outcomes[0]_evidence_command_missing",
                      dispatcher.validate_packet(dangling))

    # ------------------------------------------------- tac-bound records -----
    def test_normalize_records_shape_and_rehash(self):
        got = dispatcher.normalize_records(packet("handoff-honest.json"))
        self.assertEqual(got["schema"], "tac.claim.v1")
        self.assertTrue(got["canary_records_excluded"])
        self.assertEqual(len(got["records"]), 2)
        self.assertEqual(got["dropped_canary_records"], 1)
        keys = {"cmd", "exit_code", "stdout_file", "sha256", "bytes", "captured_at",
                "attempt", "wall_clock_ms", "cwd"}
        for record in got["records"]:
            self.assertEqual(set(record), keys)
            self.assertTrue(Path(record["stdout_file"]).is_file())
            self.assertEqual(record["bytes"], Path(record["stdout_file"]).stat().st_size)
        honest = packet("handoff-honest.json")
        for entry, record in zip(honest["commands"], got["records"]):
            self.assertEqual(record["sha256"], entry["stdout_sha256"])

    def test_canary_records_are_structurally_unreachable(self):
        got = dispatcher.normalize_records(packet("handoff-phantom.json"))
        blob = json.dumps(got["records"], ensure_ascii=False).lower()
        self.assertNotIn("canary", blob)
        self.assertNotIn("observed", blob)
        self.assertNotIn("nonexistent_path_probe", blob)
        self.assertNotIn("claim", json.dumps(got["records"]))
        smuggled = packet("handoff-honest.json")
        smuggled["commands"].append(
            {"cmd": f"python3 -m unittest {smuggled['dispatch_spec']['canary']['test_name']}",
             "exit_code": 1, "stdout_sha256": "a" * 64,
             "log_path": "rig_capabilities/dispatcher.py", "attempt": 1})
        after = dispatcher.normalize_records(smuggled)
        self.assertEqual(len(after["records"]), 2)
        self.assertEqual(after["dropped_canary_records"], 2)
        self.assertNotIn("canary",
                         json.dumps(after["records"], ensure_ascii=False).lower())

    def test_normalize_records_rejects_non_packet(self):
        with self.assertRaises(dispatcher.AdmissionError):
            dispatcher.normalize_records("not a packet")

    # ------------------------------------------------------- law L2 plan -----
    def test_verifier_checkout_plan_uses_archive_only(self):
        plan = " | ".join(dispatcher.verifier_checkout_plan(
            "/Users/rig128gb/Developer/rig-capabilities", COMMIT, "/tmp/f31-verify"))
        self.assertIn("archive", plan)
        self.assertIn("tar -x -C", plan)
        self.assertNotIn("clone", plan)
        self.assertNotIn("worktree", plan)

    def test_verifier_checkout_plan_refuses_smuggling(self):
        for dest in ("/tmp/x; git clone url", "/tmp/x | git worktree add", "/tmp/$(id)"):
            with self.assertRaises(dispatcher.AdmissionError):
                dispatcher.verifier_checkout_plan("/repo", COMMIT, dest)
        with self.assertRaises(dispatcher.AdmissionError):
            dispatcher.verifier_checkout_plan("/repo", "main", "/tmp/x")
        with self.assertRaises(dispatcher.AdmissionError):
            dispatcher.verifier_checkout_plan("", COMMIT, "/tmp/x")
        with self.assertRaises(dispatcher.AdmissionError):
            dispatcher.verifier_checkout_plan("/repo", COMMIT, "")

    # ---------------------------------------------------------- isolation ----
    def test_audit_isolation_accepts_head_and_dict_entries(self):
        base = dispatcher.audit_isolation(
            [f"{COMMIT} HEAD@{{0}}: commit: x"], ["rig_capabilities/dispatcher.py"],
            "fable-2031", ".")
        self.assertEqual(base, (True, "ISOLATED"))
        self.assertEqual(dispatcher.audit_isolation(
            [{"branch": "fable-2031", "path": "rig_capabilities/dispatcher.py"}],
            [{"path": "rig_capabilities/stats.py"}], "fable-2031", ".")[0], True)
        self.assertEqual(dispatcher.audit_isolation(
            [{"branch": "elsewhere"}], [], "fable-2031", "."),
            (False, "ISOLATION_BREACH"))
        self.assertEqual(dispatcher.audit_isolation(
            [], ["../outside.file"], "fable-2031", ".")[0], False)
        self.assertEqual(dispatcher.audit_isolation([], [], "fable-2031", None)[0], False)
        self.assertEqual(dispatcher.audit_isolation(
            [], [], "", ".")[1], "ISOLATION_BREACH")

    # --------------------------------------------------------- red team ------
    def test_all_three_decoys_are_caught(self):
        ok, detail = dispatcher.gate_canary_detection(RepoStub(REPO_ROOT))
        self.assertTrue(ok, detail)
        self.assertIn("3/3 decoys fabricated", detail)
        styles = set()
        for name in ("decoy-1.json", "decoy-2.json", "decoy-3.json"):
            got = decoy(name)
            styles.add(got["decoy_style"])
            self.assertIn(f"{name}[{got['decoy_style']}]:FABRICATED(", detail)
            self.assertEqual(verify(got)["verdict"], "FABRICATED")
        self.assertEqual(detail.count(":FABRICATED("), 3)
        self.assertEqual(len(styles), 3, "each decoy is a different fabrication style")

    def test_gate_accepts_a_path_argument_not_the_filesystem_root(self):
        ok, detail = dispatcher.gate_canary_detection(REPO_ROOT)
        self.assertTrue(ok, detail)
        ok_missing, detail_missing = dispatcher.gate_canary_detection(Path("/"))
        self.assertFalse(ok_missing)
        self.assertIn("missing", detail_missing)

    def test_planted_all_green_decoy_turns_the_gate_red(self):
        with tempfile.TemporaryDirectory() as work:
            staged = Path(work) / dispatcher.CANARY_DIR
            shutil.copytree(RED, staged)
            target = staged / "decoy-2.json"
            green = decoy("decoy-2.json")
            green["canary"]["observed"] = "PASS"
            green["canary"]["nonexistent_path_probe"] = "NOT_FOUND"
            green["files_changed"] = green["files_changed"][:2]
            green["tests"] = {"passed": 12, "failed": 0, "skipped": 0,
                              "failing_test_names": []}
            target.write_text(json.dumps(green), encoding="utf-8")
            ok, detail = dispatcher.gate_canary_detection(RepoStub(Path(work)))
            self.assertFalse(ok, detail)
            self.assertIn("3/3 decoys fabricated", detail)
            self.assertIn("detection_reasons_not_distinct", detail)

            target.write_text(json.dumps(packet("handoff-honest.json")), encoding="utf-8")
            ok, detail = dispatcher.gate_canary_detection(RepoStub(Path(work)))
            self.assertFalse(ok, detail)
            self.assertIn("decoy-2.json:not_a_registered_decoy", detail)
            self.assertIn("detection_incomplete:2 of 3 caught", detail)

    def test_gate_reports_missing_decoys_without_raising(self):
        with tempfile.TemporaryDirectory() as work:
            ok, detail = dispatcher.gate_canary_detection(RepoStub(Path(work)))
            self.assertFalse(ok)
            self.assertEqual(detail.count("missing"), 3)
        ok, detail = dispatcher.gate_canary_detection(None)
        self.assertFalse(ok)
        self.assertIn("gate_error", detail)


class WorktreeDenialParityTests(unittest.TestCase):
    """Law L2 mechanical denial: gate_d and the house hook agree verdict-for-verdict."""

    HOOK = REPO_ROOT / "capabilities" / "hooks" / "guard-dangerous-commands.sh"
    RULE = "unmanaged-worktree-add"

    # (command, expected verdict). deny = the command creates an unmanaged
    # checkout, or contains a quoted occurrence a deterministic regex cannot
    # distinguish from one — `echo "git worktree add"` is denied on BOTH surfaces
    # (same trade-off the existing force-push rules already make). allow =
    # read-only worktree inspection; over-denial there would be a defect.
    CASES: list[tuple[str, str]] = [
        ("git worktree add /tmp/x -b feat", "deny"),
        ("git -C /Users/rig128gb/Developer/rig-capabilities worktree add /tmp/x -b lane", "deny"),
        ("git --git-dir=/repo/.git worktree add /tmp/x --detach", "deny"),
        ("git --git-dir /repo/.git --work-tree /repo worktree add ../sibling -b lane", "deny"),
        ("X=1 git worktree add /tmp/x", "deny"),
        ("git\tworktree\tadd /tmp/x", "deny"),
        ('echo "git worktree add /tmp/x"', "deny"),
        ('git commit -m "guard the worktree add denial rule"', "allow"),
        ("git worktree list", "allow"),
        ("git worktree list --porcelain", "allow"),
        ("git worktree status", "allow"),
        ("git worktree remove ./scratch/wt-verify", "allow"),
        ("git worktree prune -n", "allow"),
    ]

    def hook_verdict(self, command: str) -> tuple[str, str]:
        """Run the repo hook for real: exit 2 = deny, exit 0 = allow."""
        import subprocess
        payload = json.dumps({"tool_input": {"command": command}})
        proc = subprocess.run(["/bin/sh", str(self.HOOK)],
                              input=payload.encode("utf-8"),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 2:
            return "deny", proc.stderr.decode("utf-8", "replace")
        if proc.returncode == 0:
            return "allow", ""
        return self.fail(f"hook must exit 0 or 2 (fail-open contract), "
                         f"got {proc.returncode}: {proc.stderr!r}")  # unreachable return

    def test_hook_is_the_repo_copy_not_an_installed_home_copy(self):
        self.assertTrue(self.HOOK.exists(), f"missing repo hook: {self.HOOK}")
        self.assertTrue(self.HOOK.is_relative_to(REPO_ROOT))
        self.assertNotIn(".claude", str(self.HOOK))
        first = self.HOOK.read_text(encoding="utf-8").splitlines()[0]
        self.assertTrue(first.startswith("#!"), first)

    def test_rule_registered_in_gate_d_and_mirrored_verbatim_in_hook(self):
        from rig_capabilities.gate_d import DANGEROUS_COMMAND_RULES
        patterns = {rid: sweep for rid, sweep, _ in DANGEROUS_COMMAND_RULES}
        self.assertIn(self.RULE, patterns)
        hook_src = self.HOOK.read_text(encoding="utf-8")
        self.assertIn(patterns[self.RULE], hook_src,
                      "hook regex must be byte-identical to gate_d's")

    def test_surfaces_agree_on_every_case(self):
        from rig_capabilities.gate_d import evaluate
        for command, want in self.CASES:
            with self.subTest(command=command):
                gate_verdict, gate_rule = evaluate("Bash", {"command": command})
                hook_verdict, hook_err = self.hook_verdict(command)
                self.assertEqual(gate_verdict, want,
                                 f"gate_d: {command!r} -> {gate_verdict}/{gate_rule}")
                self.assertEqual(hook_verdict, want,
                                 f"hook: {command!r} -> {hook_verdict} ({hook_err.strip()})")
                # denies must be THIS rule firing, allows rule-free — no incidental collisions
                self.assertEqual(gate_rule, self.RULE if want == "deny" else "no-rule-match")

    def test_hook_fails_open_on_malformed_payload(self):
        import subprocess
        proc = subprocess.run(["/bin/sh", str(self.HOOK)], input=b"not json {{{",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))




class FixtureHygieneTests(unittest.TestCase):
    """A fixture must not borrow somebody else's history.

    The honest proof packet used to pin `d2bbec27…`, a commit that exists only on
    a sibling branch — so on this branch the fixture's own claim was false, and a
    tracked file was asserting reachability it did not have. Fixtures name their
    own bytes; where a commit is named it is an ancestor of the branch under test.
    """

    def test_honest_proof_fixture_commits_to_this_branch_ancestry(self):
        doc = json.loads((FIX / "proof" / "fable2031-honest.json").read_text())
        commit = doc["body"]["commit"]
        self.assertRegex(commit, r"^[0-9a-f]{7,40}$")
        for f in doc["body"]["evidence_logs"] + [
                doc["body"]["canary"]["test_path"],
                doc["body"]["canary"]["run_log"]]:
            self.assertTrue((REPO_ROOT / f).is_file(), f"fixture names missing {f}")
        r = subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"],
                           cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0,
                         f"{commit} is not an ancestor of HEAD — fixture history leak")


if __name__ == "__main__":
    unittest.main()
