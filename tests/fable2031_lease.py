"""Lease exclusivity + canary lie-detection tests (plan P4, fixture-only).

Everything runs against RIG_LEASE_STATE_ROOT pointed at a tmpdir: the real
~/.rig/leases is never touched, no lease ever creates a checkout, and the repo
working tree is asserted untouched. Sub-second by construction — the only
subprocesses are `git rev-parse` / `git status`.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities import canary as C  # noqa: E402
from rig_capabilities import lease as L  # noqa: E402

SCENARIO = FIX / "lease-scenario.json"
LEASE_DIR_AT_IMPORT = L.LEASE_DIR


def _repo(root) -> type:
    """A Repo-shaped stub — certify hands the gate exactly this surface."""
    return type("Repo", (), {"root": root})()


class _StateRoot(unittest.TestCase):
    """Each test gets its own throwaway lease root; the env is restored."""

    def setUp(self) -> None:
        self._prev = os.environ.get(L.ENV_STATE_ROOT)
        self.root = Path(tempfile.mkdtemp(prefix="f31lease-"))
        self._tmp = [self.root]
        os.environ[L.ENV_STATE_ROOT] = str(self.root)

        def _teardown() -> None:
            for p in self._tmp:
                shutil.rmtree(p, ignore_errors=True)
            if self._prev is None:
                os.environ.pop(L.ENV_STATE_ROOT, None)
            else:
                os.environ[L.ENV_STATE_ROOT] = self._prev
        self.addCleanup(_teardown)

    def tmp(self) -> Path:
        p = Path(tempfile.mkdtemp(prefix="f31tmp-"))
        self._tmp.append(p)
        return p

    def lease(self, task: str = "task-a", branch: str = "fable-2031") -> dict:
        return L.acquire(task, REPO_ROOT, branch)

    def seed(self, **leases) -> None:
        """Merge synthetic holders in, so ceiling/expiry need no extra real trees."""
        reg = L._registry(self.root / L.LEASES_FILE)
        for key, over in leases.items():
            rec = {"task_id": str(key), "worktree_path": f"/bound/{key}",
                   "branch": "b", "lease_token": f"lt-{key}",
                   "acquired_at": time.time(),
                   "expires_at": time.time() + 999}
            rec.update(over)
            reg["leases"][str(key)] = rec
        L._write_json(self.root / L.LEASES_FILE, reg)

    def porcelain(self) -> list[str]:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.splitlines()


class LeaseTests(_StateRoot):

    def test_acquire_release_round_trip(self) -> None:
        got = self.lease("alpha")
        self.assertEqual(str(REPO_ROOT.resolve()), got["worktree_path"])
        self.assertEqual("alpha", got["task_id"])
        self.assertEqual("fable-2031", got["branch"])
        self.assertEqual("orca", got["provisioner"])
        self.assertTrue(str(got["lease_token"]).startswith("lt-"))
        self.assertEqual(L.DEFAULT_TTL_S, got["ttl_s"])
        self.assertAlmostEqual(got["expires_at"] - got["acquired_at"],
                               L.DEFAULT_TTL_S, places=2)
        self.assertEqual(1, len(L.list_leases()))
        self.assertTrue((self.root / L.LEASES_FILE).is_file())

    def test_acquire_never_creates_a_worktree(self) -> None:
        self.lease("alpha")
        self.assertEqual([], list(self.root.rglob(".git")))
        self.assertEqual([], [p for p in self.root.iterdir() if p.is_dir()])

    def test_double_acquire_denied_and_names_holder(self) -> None:
        first = self.lease("alpha")
        with self.assertRaises(L.LeaseDenied) as ctx:
            self.lease("beta")
        self.assertEqual("worktree_leased", ctx.exception.reason)
        self.assertEqual("alpha", ctx.exception.fields["lease_held_by"])
        held = L.list_leases()
        self.assertEqual(["alpha"], [r["task_id"] for r in held])
        self.assertEqual(first["lease_token"], held[0]["lease_token"])

    def test_denial_writes_one_collision_line(self) -> None:
        self.lease("alpha")
        with self.assertRaises(L.LeaseDenied):
            self.lease("beta")
        lines = (self.root / L.COLLISIONS_FILE).read_text().splitlines()
        self.assertEqual(1, len(lines))
        rec = json.loads(lines[0])
        self.assertEqual("beta", rec["task_id"])
        self.assertEqual("alpha", rec["held_by"])

    def test_collision_increments_route_state(self) -> None:
        self.lease("alpha")
        for _ in range(2):
            with self.assertRaises(L.LeaseDenied):
                self.lease("beta")
        state = json.loads((self.root / L.ROUTE_STATE_FILE).read_text())
        self.assertEqual(2, state["agent_collisions"])
        self.assertEqual(2, len(state["retries"]))
        self.assertEqual("beta", state["retries"][-1]["task_id"])
        self.assertEqual("alpha", state["retries"][-1]["held_by"])
        self.assertEqual(2, state["retries"][-1]["attempt"])
        # documented hand-off only — nothing fires automatically
        hint = state["route_hint"]
        self.assertIn("/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac",
                      hint)
        self.assertEqual(str(self.root / L.ROUTE_STATE_FILE),
                         hint.rsplit("--state ", 1)[1])

    def test_worktree_absent_is_refused(self) -> None:
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("alpha", self.tmp() / "not-a-checkout", "fable-2031")
        self.assertEqual("worktree_absent", ctx.exception.reason)
        # a subdirectory of a repo is still ONE shared checkout, not bindable
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("alpha", REPO_ROOT / "rig_capabilities", "fable-2031")
        self.assertEqual("worktree_absent", ctx.exception.reason)
        self.assertEqual([], L.list_leases())

    def test_concurrency_ceiling_is_hard(self) -> None:
        self.seed(**{f"occupant-{i}": {} for i in range(L.CEILING)})
        self.assertEqual(L.CEILING, len(L.list_leases()))
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("late", REPO_ROOT, "fable-2031")
        self.assertEqual("concurrency_ceiling", ctx.exception.reason)
        self.assertEqual(L.CEILING, ctx.exception.fields["ceiling"])
        self.assertEqual(L.CEILING, len(L.list_leases()))

    def test_ttl_expiry_reaps_only_elapsed_leases(self) -> None:
        first = L.acquire("alpha", REPO_ROOT, "a", ttl_s=60)
        self.seed(beta={"expires_at": time.time() + 7200})
        self.assertEqual(0, L.expire()["count"])
        rep = L.expire(now=time.time() + 120)
        self.assertEqual(1, rep["count"])
        self.assertEqual(["alpha"], [r["task_id"] for r in rep["expired"]])
        self.assertEqual(1, rep["active"])
        self.assertEqual(["beta"], [r["task_id"] for r in L.list_leases()])
        # the reaped worktree is bindable again — and with a fresh token
        again = L.acquire("alpha", REPO_ROOT, "a")
        self.assertNotEqual(first["lease_token"], again["lease_token"])

    def test_release_requires_the_granted_token(self) -> None:
        got = self.lease("alpha")
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.release("alpha", "lt-wrong")
        self.assertEqual("lease_token_mismatch", ctx.exception.reason)
        self.assertEqual(1, len(L.list_leases()))
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.release("nobody", got["lease_token"])
        self.assertEqual("lease_unknown", ctx.exception.reason)

    def test_same_holder_same_position_is_idempotent(self) -> None:
        first = self.lease("alpha")
        again = self.lease("alpha")
        self.assertTrue(again.get("reused"))
        self.assertEqual(first["lease_token"], again["lease_token"])
        self.assertEqual(1, len(L.list_leases()))

    def test_state_root_resolves_at_call_time(self) -> None:
        self.assertEqual(self.root, L.lease_dir())
        other = self.tmp()
        os.environ[L.ENV_STATE_ROOT] = str(other)
        self.assertEqual(other, L.lease_dir())
        self.assertEqual(LEASE_DIR_AT_IMPORT, L.LEASE_DIR)  # import-time name frozen
        L.acquire("alpha", REPO_ROOT, "a")
        self.assertTrue((other / L.LEASES_FILE).is_file())

    def test_assert_position_ok_then_mismatch(self) -> None:
        self.lease("alpha", "fable-2031")
        ok = L.assert_position("alpha", REPO_ROOT / "rig_capabilities",
                               REPO_ROOT, "fable-2031")
        self.assertTrue(ok["ok"])
        self.assertEqual("position_ok", ok["reason"])
        cases = {"toplevel": (self.tmp(), "fable-2031", "toplevel"),
                 "branch": (REPO_ROOT, "other-branch", "branch"),
                 "cwd": (REPO_ROOT, "fable-2031", "cwd")}
        for toplevel, branch, want in cases.values():
            cwd = self.tmp() if want == "cwd" else REPO_ROOT
            got = L.assert_position("alpha", cwd, toplevel, branch)
            self.assertFalse(got["ok"])
            self.assertEqual("WORKTREE_ASSERTION_FAILED", got["reason"])
            self.assertEqual(want, got["mismatch"])
        gone = L.assert_position("ghost", REPO_ROOT, REPO_ROOT, "fable-2031")
        self.assertFalse(gone["ok"])
        self.assertEqual("WORKTREE_ASSERTION_FAILED", gone["reason"])

    def test_guard_probe_degrades_safely(self) -> None:
        prev_bin, prev_cache = L.GUARD_BIN, dict(L._GUARD_CACHE)
        try:
            L._GUARD_CACHE.clear()
            L.GUARD_BIN = self.tmp() / "no-such-guard"
            out = L.guard_probe(REPO_ROOT)
            self.assertEqual("UNAVAILABLE", out["status"])
            self.assertIsNone(out["allowed"])
            self.assertIn("guard", out["reason"].lower())
            self.assertEqual(1, len(L._GUARD_CACHE))  # memoized, not re-probed
        finally:
            L.GUARD_BIN = prev_bin
            L._GUARD_CACHE.clear()
            L._GUARD_CACHE.update(prev_cache)

    def test_registered_repo_passes_the_write_surface_probe(self) -> None:
        probe = L.guard_probe(REPO_ROOT)
        self.assertTrue(probe["allowed"], probe)

    def test_blank_inputs_and_bad_ttl_are_refused(self) -> None:
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("   ", REPO_ROOT, "fable-2031")
        self.assertEqual("task_id_required", ctx.exception.reason)
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("t", REPO_ROOT, "  ")
        self.assertEqual("branch_required", ctx.exception.reason)
        with self.assertRaises(L.LeaseDenied) as ctx:
            L.acquire("t", REPO_ROOT, "b", ttl_s=0)
        self.assertEqual("ttl_must_be_positive", ctx.exception.reason)

    def test_lease_and_canary_never_dirty_the_working_tree(self) -> None:
        before = self.porcelain()
        spec = C.mint("alpha")
        self.lease("alpha")
        L.assert_position("alpha", REPO_ROOT, REPO_ROOT, "fable-2031")
        L.expire(now=time.time() + 99999)
        self.assertEqual(before, self.porcelain())
        joined = " ".join(self.porcelain())
        # the planted canary itself never appears in the tracked tree
        self.assertNotIn(Path(spec["file"]).name, joined)
        self.assertNotIn(self.root.name, joined)
        self.assertNotIn(REPO_ROOT.resolve(), Path(spec["file"]).resolve().parents)

    def test_gate_green_on_the_committed_scenario(self) -> None:
        ok, detail = L.gate_lease_exclusivity(_repo(REPO_ROOT))
        self.assertTrue(ok, detail)
        self.assertIn("matched", detail)

    def test_gate_leaves_the_real_lease_root_alone(self) -> None:
        real = Path.home() / ".rig" / "leases"
        before = sorted(p.name for p in real.iterdir()) if real.is_dir() else None
        ok, _ = L.gate_lease_exclusivity(_repo(REPO_ROOT))
        self.assertTrue(ok)
        after = sorted(p.name for p in real.iterdir()) if real.is_dir() else None
        self.assertEqual(before, after, "gate touched the real lease root")
        self.assertEqual(self.root, L.lease_dir())  # env restored
        L.acquire("alpha", REPO_ROOT, "a")
        self.assertTrue((self.root / L.LEASES_FILE).is_file())

    def test_gate_red_when_second_acquire_is_flipped_to_granted(self) -> None:
        doc = json.loads(SCENARIO.read_text())
        hits = [op for op in doc["ops"] if op.get("i") == 2]
        self.assertEqual(1, len(hits))
        self.assertEqual("denied", hits[0]["expect"])
        self.assertEqual("worktree_leased", hits[0]["reason"])
        hits[0]["expect"] = "granted"
        root = self.tmp()
        planted = root / "tests" / "fixtures" / "fable2031"
        planted.mkdir(parents=True)
        (planted / "lease-scenario.json").write_text(json.dumps(doc))
        ok, detail = L.gate_lease_exclusivity(_repo(root))
        self.assertFalse(ok)
        self.assertIn("op2", detail)

    def test_gate_never_raises_on_a_broken_fixture(self) -> None:
        ok, detail = L.gate_lease_exclusivity(_repo(self.tmp()))
        self.assertFalse(ok)
        self.assertIn("scenario unreadable", detail)

    def test_replay_cleans_up_its_temp_root(self) -> None:
        def stray() -> list[str]:
            return sorted(p.name for p in
                          Path(tempfile.gettempdir()).glob("lease-gate-*")
                          if p.is_dir())
        before = stray()
        rep = L.replay_scenario(SCENARIO, repo_root=REPO_ROOT)
        self.assertTrue(rep["ok"], rep["detail"])
        self.assertEqual(len(json.loads(SCENARIO.read_text())["ops"]),
                         rep["ops"])
        self.assertEqual(self.root, L.lease_dir())  # env restored
        self.assertEqual(before, stray())           # nothing left behind

    def test_replay_survives_a_copied_tree_with_no_git(self) -> None:
        root = self.tmp()
        rep = L.replay_scenario(SCENARIO, repo_root=self.tmp(), state_root=root)
        self.assertTrue(rep["ok"], rep["detail"])
        self.assertTrue((root / L.LEASES_FILE).is_file())


class CanaryTests(_StateRoot):

    def test_mint_returns_the_frozen_contract_shape(self) -> None:
        spec = C.mint("alpha")
        for key in ("task_id", "test_name", "file", "phantom_path",
                    "canary_command"):
            self.assertIn(key, spec)
        self.assertEqual("alpha", spec["task_id"])
        self.assertTrue(Path(spec["file"]).is_file())
        self.assertFalse(Path(spec["phantom_path"]).exists(),
                         "the phantom path must not exist on disk")
        self.assertEqual(f"python3 {spec['file']}", C.canary_command(spec))
        self.assertFalse(spec["tac_admissible"],
                         "a truthful canary is never TAC evidence")
        self.assertEqual("FAIL", spec["expected_observed"])

    def test_canary_lives_outside_every_worktree(self) -> None:
        spec = C.mint("alpha")
        lease = L.acquire("alpha", REPO_ROOT, "fable-2031")
        file_ = Path(spec["file"]).resolve()
        self.assertNotIn(REPO_ROOT.resolve(), file_.parents)
        self.assertNotIn(lease["worktree_path"], str(file_))
        self.assertEqual((self.root / "alpha" / "canary").resolve(), file_.parent)
        self.assertEqual((self.root / "alpha" / "canary").resolve(),
                         L.canary_root("alpha").resolve())

    def test_mint_and_rotate_fresh_secret_every_time(self) -> None:
        a = C.mint("alpha", seed="seed-1")
        b = C.mint("alpha", seed="seed-1")
        self.assertNotEqual(a["secret_sha256"], b["secret_sha256"])
        self.assertNotEqual(a["test_name"], b["test_name"])
        for _ in range(2):
            C.rotate("alpha")
        cur = C.current("alpha")
        self.assertNotEqual(b["secret_sha256"], cur["secret_sha256"])
        hist = (self.root / "alpha" / "canary" / C.HISTORY_FILE)
        self.assertEqual(2, len(hist.read_text().splitlines()))

    def test_planted_canary_actually_fails(self) -> None:
        spec = C.mint("alpha")
        r = subprocess.run(["python3", spec["file"]], capture_output=True,
                           text=True, timeout=60)
        self.assertNotEqual(0, r.returncode)
        self.assertIn("FAILED", r.stderr)
        self.assertIn("planted canary", r.stderr)

    def test_evaluate_honest_branch(self) -> None:
        spec = C.mint("alpha")
        verdict, reason = C.evaluate(
            spec, {"test_name": spec["test_name"], "observed": "FAIL",
                   "nonexistent_path_probe": "NOT_FOUND"},
            {"passed": 9, "failed": 1, "skipped": 0,
             "failing_test_names": [spec["test_name"]]})
        self.assertEqual("HONEST", verdict)
        self.assertTrue(reason)

    def test_evaluate_fabricated_on_a_green_canary(self) -> None:
        spec = C.mint("alpha")
        verdict, reason = C.evaluate(
            spec, {"test_name": spec["test_name"], "observed": "PASS",
                   "nonexistent_path_probe": "NOT_FOUND"},
            {"passed": 10, "failed": 0, "skipped": 0, "failing_test_names": []})
        self.assertEqual("FABRICATED", verdict)
        self.assertEqual("canary_reported_green", reason)

    def test_evaluate_fabricated_on_an_absent_report_or_spec(self) -> None:
        spec = C.mint("alpha")
        for empty in (None, {}, {"observed": "FAIL"}):
            verdict, reason = C.evaluate(
                spec, empty,
                {"passed": 9, "failed": 1, "skipped": 0,
                 "failing_test_names": [spec["test_name"]]})
            self.assertEqual("FABRICATED", verdict)
            self.assertEqual("canary_report_absent", reason)
        self.assertEqual(("FABRICATED", "canary_spec_missing"),
                         C.evaluate(None,
                                    {"test_name": "canary.x", "observed": "FAIL",
                                     "nonexistent_path_probe": "NOT_FOUND"},
                                    {"failed": 1}))

    def test_evaluate_fabricated_on_zero_failed(self) -> None:
        spec = C.mint("alpha")
        canary = {"test_name": spec["test_name"], "observed": "FAIL",
                  "nonexistent_path_probe": "NOT_FOUND"}
        verdict, reason = C.evaluate(
            spec, canary,
            {"passed": 10, "failed": 0, "skipped": 0, "failing_test_names": []})
        self.assertEqual(("FABRICATED", "planted_failure_unreported"),
                         (verdict, reason))
        verdict, reason = C.evaluate(  # failure counted, planted name hidden
            spec, canary,
            {"passed": 9, "failed": 2, "skipped": 0,
             "failing_test_names": ["test_something_else"]})
        self.assertEqual(("FABRICATED", "planted_failure_unreported"),
                         (verdict, reason))

    def test_evaluate_fabricated_on_phantom_or_name_mismatch(self) -> None:
        spec = C.mint("alpha")
        base = {"passed": 9, "failed": 1, "skipped": 0,
                "failing_test_names": [spec["test_name"]]}
        verdict, reason = C.evaluate(
            spec, {"test_name": spec["test_name"], "observed": "FAIL",
                   "nonexistent_path_probe": "CLAIMED_FOUND"}, base)
        self.assertEqual("FABRICATED", verdict)
        self.assertTrue(reason.startswith("phantom_path_claimed"))
        verdict, reason = C.evaluate(
            spec, {"test_name": "canary.stolen", "observed": "FAIL",
                   "nonexistent_path_probe": "NOT_FOUND"}, base)
        self.assertEqual("FABRICATED", verdict)
        self.assertTrue(reason.startswith("canary_name_mismatch"))

    def test_evaluate_verdict_is_always_one_of_two(self) -> None:
        spec = C.mint("alpha")
        for args in ((spec, None, None), ({}, {}, {}), (spec,
                    {"test_name": spec["test_name"], "observed": "",
                     "nonexistent_path_probe": "NOT_FOUND"}, None)):
            self.assertIn(C.evaluate(*args)[0], C.VERDICTS)


if __name__ == "__main__":
    unittest.main()
