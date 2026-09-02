"""Stdlib unittests for the rig-loop engine (Loop-Skill Contract v11).

Every test runs against a temporary state root (RIG_LOOP_STATE) and a temporary
proof dir, never the live ~/.rig/state. Wiring tests patch the harness config
paths to files inside the temp dir.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import loops as L  # noqa: E402

CANONICAL = ["iqrsqpi-v11", "gate-d-loop", "proof-loop", "adversarial-verification-loop",
             "north-star-lock-loop", "phase-discipline-loop", "git-push-safety-loop",
             "iqrsqpi-v20", "iqrsqpi-v20-slice"]


class TempState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rigloop-ut-")
        self.root = Path(self.tmp.name)
        self._env = {k: os.environ.get(k) for k in ("RIG_LOOP_STATE", "RIG_LOOP_PROOF_DIR")}
        os.environ["RIG_LOOP_STATE"] = str(self.root / "state")
        os.environ["RIG_LOOP_PROOF_DIR"] = str(self.root / "proof")
        self.cwd = self.root / "work"
        self.cwd.mkdir()

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()


class SpecTests(TempState):
    def test_all_canonical_specs_load_and_validate(self):
        for sid in CANONICAL:
            spec = L.load_spec(sid)
            self.assertEqual(spec["schema"], L.SCHEMA, sid)
            self.assertTrue(spec["stages"], sid)
            self.assertTrue(spec.get("kill_switch", {}).get("max_iterations"), sid)
            self.assertTrue((Path(spec["_dir"]) / "SKILL.md").exists(), sid)
            self.assertTrue((Path(spec["_dir"]) / "tests" / "cases.json").exists(), sid)

    def test_validate_rejects_missing_kill_switch_and_unknown_gate(self):
        bad = {"schema": L.SCHEMA, "id": "x", "stages": [{"id": "A", "gate": [{"type": "nope"}]}]}
        errs = L.validate_spec(bad)
        self.assertTrue(any("kill_switch" in e for e in errs))
        self.assertTrue(any("unknown gate type" in e for e in errs))

    def test_skill_frontmatter_declares_hooks_for_claude(self):
        for sid in CANONICAL:
            text = (L.SKILL_ROOTS["canonical"] / sid / "SKILL.md").read_text()
            self.assertIn("\nhooks:\n", text, sid)
            self.assertIn("PreToolUse", text, sid)
            self.assertIn("rig-loop hook stop", text, sid)


class HookMetadataTests(unittest.TestCase):
    def test_comment_metadata_parses_for_ts_and_yaml_hooks(self):
        from rig_capabilities.catalog import _quality_block
        ts = (REPO_ROOT / "capabilities" / "hooks" / "rig-loop-hooks.ts").read_text()
        yml = (REPO_ROOT / "capabilities" / "hooks" / "rig-loop-gate" / "HOOK.yaml").read_text()
        sh = (REPO_ROOT / "capabilities" / "hooks" / "rig-loop-hook.sh").read_text()
        for text in (ts, yml, sh):
            q = _quality_block(text)
            self.assertEqual(q.get("outcome"), "agent-engineering:", text[:60])
            self.assertTrue(q.get("done_when"), text[:60])
            self.assertEqual(q.get("quality_floor"), "0.7", text[:60])


class RunTests(TempState):
    def test_activate_then_out_of_order_refused(self):
        run = L.activate("iqrsqpi-v11", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("iqrsqpi-v11")
        with self.assertRaises(L.SpecError):
            L.mark_stage(run, spec, "S", "pass")
        self.assertEqual(L.find_active(str(self.cwd))["run_id"], run["run_id"])
        self.assertEqual(L.find_active(str(self.cwd / "sub" / "dir"))["run_id"], run["run_id"], "parent lookup")

    def test_unrelated_cwd_does_not_attach_to_latest_run(self):
        L.activate("iqrsqpi-v11", cwd=str(self.cwd), harness="ut")
        other = self.root / "elsewhere"
        other.mkdir()
        self.assertIsNone(L.find_active(str(other)))
        res = L.dispatch_hook("pre-tool", {"cwd": str(other), "tool_name": "Write", "tool_input": {"file_path": str(other / "x.py")}})
        self.assertEqual(res["action"], "allow")

    def test_gate_refuses_pass_and_records_gate_red_event(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("proof-loop")
        (L.artifacts_dir(run) / "claim.md").write_text("## Claim\nx\n## Done-test\n- cmd:true\n## Artifacts\n- a\n")
        with self.assertRaises(L.SpecError) as cm:
            L.mark_stage(run, spec, "C", "pass")
        self.assertIn("refusing pass", str(cm.exception))
        events = (L._run_dir(run["run_id"]) / "events.jsonl").read_text()
        self.assertIn('"kind": "gate_red"', events)

    def test_force_pass_is_recorded_as_forced(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("proof-loop")
        run = L.mark_stage(run, spec, "C", "pass", force=True)
        self.assertTrue(run["history"][-1]["forced"])
        self.assertIn("FORCED", run["stage_notes"]["C"])

    def test_kill_switch_wall_clock_parks_on_prompt(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        run["started_at"] = "2020-01-01T00:00:00Z"
        L.save_run(run)
        res = L.dispatch_hook("prompt", {"cwd": str(self.cwd), "prompt": "hi"})
        self.assertEqual(res["action"], "inject")
        self.assertIn("KILL SWITCH", res["text"])
        self.assertEqual(L.load_run(run["run_id"])["status"], "parked")

    def test_park_resume_close(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        L.park(run, "waiting on Mike")
        self.assertIsNone(L.find_active(str(self.cwd)))
        run = L.resume(run["run_id"])
        self.assertEqual(run["status"], "active")
        L.close(run, "done for now")
        self.assertIsNone(L.find_active(str(self.cwd)))

    def test_seal_writes_proofpacket_with_matching_hash(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("proof-loop")
        a = self.cwd / "a.txt"
        a.write_text("x")
        art = L.artifacts_dir(run)
        (art / "claim.md").write_text(f"## Claim\nx\n## Done-test\n- cmd:test -f {a}\n## Artifacts\n- a\n")
        run = L.mark_stage(run, spec, "C", "pass")
        (art / "evidence.md").write_text("## Commands\n- t\n## Output\n- 0\n")
        L.add_check(run, f"test -f {a}", str(self.cwd))
        run = L.mark_stage(L.load_run(run["run_id"]), spec, "E", "pass")
        (art / "planted.md").write_text("## Planted-defect\nd\n## Red\nr\n## Green\ng\n")
        L.plant(run, "p", f"test -f {a}.missing", f"test -f {a}", str(self.cwd))
        run = L.mark_stage(L.load_run(run["run_id"]), spec, "N", "pass")
        (art / "verify.md").write_text("## Verifier\n- family: codex\n## Verdict\nVERIFIED\n## Gaps\n- none\n")
        run = L.mark_stage(run, spec, "V", "pass")
        packet = L.seal(run, spec, signer="ut")
        run = L.load_run(run["run_id"])
        p = Path(run["proof"]["path"])
        self.assertTrue(p.exists())
        self.assertEqual(run["proof"]["hash"], L.sha256_file(p))
        self.assertEqual(packet["schema_version"], "rig.proofpacket.v1")
        self.assertEqual(packet["stages"]["V"], "pass")
        self.assertTrue((art / "proof.json").exists())
        run = L.mark_stage(run, spec, "P", "pass")
        self.assertEqual(run["status"], "done")


class VerifierFindingsTests(TempState):
    """Regressions for the independent (Codex) verification findings on 3a87acc."""

    def test_degrade_gate_failure_is_recorded_not_silent(self):
        run = L.activate("iqrsqpi-v11", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("iqrsqpi-v11")
        st = {"id": "X", "gate": [{"type": "min_counter", "counter": "nope", "min": 1, "failure_tier": "degrade"}]}
        spec2 = dict(spec)
        spec2["stages"] = [st]
        run = L.mark_stage(run, spec2, "X", "pass")
        self.assertEqual(run["stage_status"]["X"], "pass")
        self.assertTrue(run["history"][-1]["degraded"])
        self.assertIn("DEGRADED", run["stage_notes"]["X"])

    def test_explicit_run_id_cannot_attach_to_foreign_cwd(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        other = self.root / "other"
        other.mkdir()
        self.assertIsNone(L.find_active(str(other), run["run_id"]))
        self.assertIsNotNone(L.find_active(str(self.cwd / "deeper"), run["run_id"]))
        res = L.dispatch_hook("stop", {"cwd": str(other)}, run_id=run["run_id"])
        self.assertEqual(res["action"], "allow")

    def test_write_paths_cover_multiedit_and_apply_patch(self):
        paths = L._write_paths({"edits": [{"file_path": "a.py"}, {"file_path": "b.py"}]}, {})
        self.assertEqual(paths, ["a.py", "b.py"])
        patch = "*** Begin Patch\n*** Update File: src/x.py\n@@\n*** Add File: y.md\n*** End Patch\n"
        self.assertEqual(L._write_paths({"patch": patch}, {}), ["src/x.py", "y.md"])
        self.assertEqual(L._write_paths({"content": "x"}, {}), [])

    def test_outward_patterns_tolerate_git_global_options(self):
        pats = L.DEFAULT_OUTWARD_PATTERNS
        import re as _re
        hit = lambda cmd: any(_re.search(p, cmd, _re.I) for p in pats)  # noqa: E731
        for cmd in ("git push", "git -C . push origin main", "git -c a=b --no-pager push",
                    "/usr/bin/git push --force", "gh --repo o/r pr merge 1", "GIT_DIR=x git push"):
            self.assertTrue(hit(cmd), cmd)
        for cmd in ("git status", "git log --oneline", "echo pushed", "gh pr view 1"):
            self.assertFalse(hit(cmd), cmd)

    def test_closing_loop_resets_iteration_evidence(self):
        run = L.activate("proof-loop", cwd=str(self.cwd), harness="ut")
        spec = L.load_spec("proof-loop")
        run = L.mark_stage(run, spec, "C", "pass", force=True)
        L.plant(run, "p", "false", "true", str(self.cwd))
        run["proof"] = {"path": "old", "hash": "x", "iteration": 1}
        L.save_run(run)
        run = L.mark_stage(L.load_run(run["run_id"]), spec, "E", "fail")
        self.assertEqual(run["iteration"], 2)
        self.assertEqual(run["planted"], [])
        self.assertIsNone(run["proof"])


class V20Tests(TempState):
    def _through_s(self):
        run = L.activate("iqrsqpi-v20", cwd=str(self.cwd), harness="claude")
        spec = L.load_spec("iqrsqpi-v20")
        art = L.artifacts_dir(run)
        out = self.cwd / "out.txt"
        (art / "intent.md").write_text(f"## GOAL\ng\n## METRIC\nm\n## DONE-TEST\n- cmd:test -f {out}\n## OUT-OF-SCOPE\no\n## COORDINATE\nL3\n## CONFIDENCE\n0.6\n")
        run = L.mark_stage(run, spec, "I1", "pass")
        (art / "questions.md").write_text("## Panel\n- [lens:a]\n- [lens:b]\n- [lens:c]\n## Questions\n- [ASSUMED] x (assumption: y)\n")
        run = L.mark_stage(run, spec, "Q1", "pass")
        (art / "research.md").write_text("## Findings\n- f\n## Sources\n- s (HIGH)\n## Gaps\n- none\n")
        L.qr_pass(run, 2); L.qr_pass(run, 0)
        run = L.mark_stage(L.load_run(run["run_id"]), spec, "R", "pass")
        (art / "spec.md").write_text(f"## Approach\nAUTO\n## Acceptance\nGiven a When b Then c\n## Files\n- {self.cwd}/src/*\n## Slices\n- s1 — done: test -f out.txt\n## Det-vs-Prob\n- AUTO\n## Test-plan\n- t\n## Rollback\n- r\n")
        run = L.mark_stage(run, spec, "S", "pass")
        return run, spec, out

    def test_done_tests_are_registered_and_executed_with_calibration(self):
        run, spec, out = self._through_s()
        self.assertEqual([c for c in run["checks"] if c.get("done_test")][0]["cmd"], f"test -f {out}")
        self.assertEqual(run["predicted"], 0.6)
        results = L.run_checks(run)
        self.assertEqual(results[0]["exit"], 1, "done-test red before the work exists")
        out.write_text("x")
        results = L.run_checks(L.load_run(run["run_id"]))
        self.assertEqual(results[0]["exit"], 0)
        run = L.load_run(run["run_id"])
        run["stage_status"].update({"B": "pass", "Q2": "pass"})
        L.save_run(run)
        packet = L.seal(run, spec, signer="ut")
        self.assertEqual(packet["calibration"]["actual"], 1.0)
        self.assertAlmostEqual(packet["calibration"]["brier"], 0.16)
        summ = L.calibration_summary("iqrsqpi-v20")
        self.assertEqual(summ["runs"], 1)

    def test_slice_child_becomes_active_then_parent_restored_and_evidence_rolls_up(self):
        run, spec, out = self._through_s()
        child = L.slice_start(run, "s1")
        self.assertEqual(L.find_active(str(self.cwd))["run_id"], child["run_id"])
        cspec = L.load_spec(child["loop_id"])
        res = L.dispatch_hook("pre-tool", {"cwd": str(self.cwd), "tool_name": "Write", "tool_input": {"file_path": str(out)}})
        self.assertEqual(res["action"], "allow")
        out.write_text("x")
        (L.artifacts_dir(child) / "slice.md").write_text("## Slice\ns1\n## Changed\n- out.txt\n")
        child = L.mark_stage(L.load_run(child["run_id"]), cspec, "B", "pass")
        L.add_check(child, f"test -f {out}", str(self.cwd))
        L.plant(child, "p", f"test -f {out}.zz", f"test -f {out}", str(self.cwd))
        (L.artifacts_dir(child) / "verify.md").write_text("## Checks\n- c\n## Planted-failure\n- p\n")
        child = L.mark_stage(L.load_run(child["run_id"]), cspec, "V", "pass")
        (L.artifacts_dir(child) / "commit.md").write_text("## Commit\nabc1234 s1\n")
        child = L.mark_stage(child, cspec, "C", "pass")
        self.assertEqual(child["status"], "done")
        self.assertEqual(L.find_active(str(self.cwd))["run_id"], run["run_id"], "parent restored")
        parent = L.load_run(run["run_id"])
        self.assertEqual(len(L.all_planted(parent)), 1)
        self.assertIn(str(out), L.all_files_written(parent))
        ok, _ = L._gate_children_done(parent, spec, {}, {"min": 1})
        self.assertTrue(ok)

    def test_verify_dispatch_parses_verdict_and_refuses_same_family(self):
        run, spec, out = self._through_s()
        with self.assertRaises(L.SpecError):
            L.verify(run, spec, "claude", cmd_override="echo VERDICT: VERIFIED")
        rec = L.verify(run, spec, "codex", cmd_override="printf 'VERDICT: PARTIAL\\nGAPS:\\n- a.py:3 unchecked input\\n'")
        self.assertEqual(rec["verdict"], "PARTIAL")
        self.assertEqual(rec["gaps"], ["a.py:3 unchecked input"])
        self.assertTrue(Path(rec["output"]).exists())
        rec2 = L.verify(L.load_run(run["run_id"]), spec, "hermes", cmd_override="echo nothing useful")
        self.assertEqual(rec2["verdict"], "NO_VERDICT")
        ok, detail = L._gate_independent_verdict(L.load_run(run["run_id"]), spec, {}, {"min": 1})
        self.assertTrue(ok, detail)
        prompt = L.build_verifier_prompt(run, spec)
        self.assertIn("VERDICT:", prompt)
        self.assertIn("intent.md", prompt)

    def test_handoff_renders_structured_document(self):
        run, spec, out = self._through_s()
        p = L.handoff(run, spec)
        text = p.read_text()
        for h in ("# Session Handoff", "## Completed", "## In Progress", "## Not Started", "## Decisions Made",
                  "## Context for Next Session", "## Build Health"):
            self.assertIn(h, text)
        self.assertIn("- [x] S Solution", text)
        self.assertIn("rig-loop resume", text)

    def test_tool_call_budget_parks_and_denies(self):
        run = L.activate("iqrsqpi-v20-slice", cwd=str(self.cwd), harness="ut")
        run["tool_calls"] = 300
        L.save_run(run)
        res = L.dispatch_hook("pre-tool", {"cwd": str(self.cwd), "tool_name": "Bash", "tool_input": {"command": "ls"}})
        self.assertEqual(res["action"], "deny")
        self.assertEqual(L.load_run(run["run_id"])["status"], "parked")

    def test_doctor_not_ok_when_a_loop_skill_is_missing_from_a_harness(self):
        old_roots = dict(L.SKILL_ROOTS)
        try:
            for h in L.HARNESSES:
                L.SKILL_ROOTS[h] = self.root / "empty" / h
            rep = L.doctor()
            self.assertFalse(rep["ok"])
            self.assertIn("iqrsqpi-v20@claude", rep["missing_installs"])
        finally:
            L.SKILL_ROOTS.clear()
            L.SKILL_ROOTS.update(old_roots)

    def test_detect_harness_from_env(self):
        old = dict(os.environ)
        try:
            for k in list(os.environ):
                if k.startswith(("CLAUDE", "CODEX", "HERMES", "PRIME", "OMP", "PI_", "RIG_AGENT")):
                    os.environ.pop(k)
            os.environ["CODEX_HOME"] = "/x"
            self.assertEqual(L.detect_harness(), "codex")
            os.environ["RIG_AGENT"] = "hermes"
            self.assertEqual(L.detect_harness(), "hermes")
        finally:
            os.environ.clear()
            os.environ.update(old)


class HookRenderTests(TempState):
    def test_render_formats(self):
        deny = {"action": "deny", "reason": "no"}
        out, err, code = L.render_hook("pre-tool", deny, "claude")
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")
        out, err, code = L.render_hook("stop", {"action": "block", "reason": "not done"}, "codex")
        self.assertEqual((out, code), ("", 2))
        self.assertIn("not done", err)
        out, _, code = L.render_hook("pre-tool", deny, "pi")
        self.assertTrue(json.loads(out)["block"])
        out, _, code = L.render_hook("prompt", {"action": "inject", "text": "banner"}, "claude")
        self.assertEqual((out, code), ("banner", 0))
        out, err, code = L.render_hook("pre-tool", {"action": "allow"}, "claude")
        self.assertEqual((out, err, code), ("", "", 0))

    def test_cli_hook_is_silent_noop_without_active_run(self):
        r = subprocess.run([sys.executable, str(L.CLI), "hook", "pre-tool", "--format", "claude"],
                           input=json.dumps({"cwd": str(self.cwd), "tool_name": "Write",
                                             "tool_input": {"file_path": str(self.cwd / "x.py")}}),
                           capture_output=True, text=True, env={**os.environ}, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_cli_hook_denies_write_before_intent_with_claude_json(self):
        L.activate("iqrsqpi-v11", cwd=str(self.cwd), harness="ut")
        r = subprocess.run([sys.executable, str(L.CLI), "hook", "pre-tool", "--format", "claude"],
                           input=json.dumps({"cwd": str(self.cwd), "tool_name": "Write",
                                             "tool_input": {"file_path": str(self.cwd / "src" / "x.py")}}),
                           capture_output=True, text=True, env={**os.environ}, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_cli_hook_never_crashes_on_garbage_stdin(self):
        r = subprocess.run([sys.executable, str(L.CLI), "hook", "stop", "--format", "claude"],
                           input="not json", capture_output=True, text=True, env={**os.environ}, timeout=30)
        self.assertEqual(r.returncode, 0)


class WiringTests(TempState):
    def setUp(self):
        super().setUp()
        self._cfg = dict(L.HOOK_CONFIG)
        self._omp = L.OMP_CONFIG
        L.HOOK_CONFIG.update({
            "claude": self.root / "claude-settings.json",
            "codex": self.root / "codex-hooks.json",
            "hermes": self.root / "hermes" / "rig-loop-gate",
            "omp": self.root / "omp" / "extensions" / "rig-loop-hooks.ts",
            "prime-agent": self.root / "prime" / "extensions" / "rig-loop-hooks.ts",
        })
        L.OMP_CONFIG = self.root / "omp-config.yml"
        L.OMP_CONFIG.write_text("skills:\n  includeSkills:\n    - alfred*\n    - iqrsqpi-v11\n")
        L.HOOK_CONFIG["claude"].write_text(json.dumps({"hooks": {"Stop": [{"matcher": "*", "hooks": [{"type": "command", "command": "echo keep"}]}]}}))

    def tearDown(self):
        L.HOOK_CONFIG.clear()
        L.HOOK_CONFIG.update(self._cfg)
        L.OMP_CONFIG = self._omp
        super().tearDown()

    def test_wire_is_idempotent_and_preserves_existing_hooks(self):
        rep1 = L.wire(apply=True)
        self.assertTrue(rep1["results"]["claude"]["changed"])
        data = json.loads(L.HOOK_CONFIG["claude"].read_text())
        cmds = [h["command"] for arr in data["hooks"].values() for m in arr for h in m["hooks"]]
        self.assertIn("echo keep", cmds)
        self.assertEqual(sum(L.MARKER in c for c in cmds), 4)
        rep2 = L.wire(apply=True)
        self.assertFalse(rep2["results"]["claude"]["changed"])
        data2 = json.loads(L.HOOK_CONFIG["claude"].read_text())
        self.assertEqual(data, data2)
        self.assertTrue(L.HOOK_CONFIG["omp"].exists() and L.MARKER in L.HOOK_CONFIG["omp"].read_text())
        self.assertTrue((L.HOOK_CONFIG["hermes"] / "handler.py").exists())
        omp = L.OMP_CONFIG.read_text()
        self.assertIn("    - proof-loop\n", omp)
        self.assertEqual(omp.count("    - iqrsqpi-v11\n"), 1)
        ver = L.verify_wiring()
        self.assertTrue(all(v["wired"] for v in ver.values()), ver)

    def test_wire_remove_strips_only_managed_entries(self):
        L.wire(apply=True)
        L.wire(apply=True, remove=True)
        data = json.loads(L.HOOK_CONFIG["claude"].read_text())
        cmds = [h["command"] for arr in data["hooks"].values() for m in arr for h in m["hooks"]]
        self.assertEqual(cmds, ["echo keep"])
        self.assertFalse(L.HOOK_CONFIG["omp"].exists())


class LoopCaseTests(TempState):
    def test_every_canonical_loop_passes_its_planted_failure_cases(self):
        for sid in CANONICAL:
            rep = L.run_loop_tests(sid)
            self.assertTrue(rep["ok"], f"{sid}: {json.dumps(rep, indent=1)[:1500]}")


if __name__ == "__main__":
    unittest.main()
