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
from unittest.mock import patch

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


class BuildCertificationGateTests(TempState):
    def build_run(self):
        run = L.activate('iqrsqpi-v11', cwd=str(self.cwd), harness='ut')
        spec = dict(L.load_spec('iqrsqpi-v11'))
        spec['stages'] = [{'id': 'F', 'gate': [{'type': 'd85_certified', 'root': '.',
                                              'build': 'build.json', 'certificate': 'certificate.json',
                                              'failure_tier': 'degrade'}]}]
        return run, spec

    def test_build_failure_cannot_force_or_degrade_to_pass(self):
        run, spec = self.build_run()
        with patch.dict(L.GATE_TYPES, {'d85_certified': lambda *args: (False, 'D85 ratio failure')}):
            with self.assertRaisesRegex(L.SpecError, 'refusing pass'):
                L.mark_stage(run, spec, 'F', 'pass', force=True)
        self.assertNotEqual(run['stage_status'].get('F'), 'pass')

    def test_final_stage_rechecks_stale_build_even_with_force(self):
        run, spec = self.build_run()
        with patch.dict(L.GATE_TYPES, {'d85_certified': lambda *args: (True, 'initial pass')}), \
             patch.object(L, '_gate_d85_certified', return_value=(False, 'source changed')):
            with self.assertRaisesRegex(L.SpecError, 'blocks completion'):
                L.mark_stage(run, spec, 'F', 'pass', force=True)

    def test_seal_rechecks_build_and_records_passing_evidence(self):
        run, spec = self.build_run()
        run['stage_status']['F'] = 'pass'
        with patch.object(L, '_gate_d85_certified', return_value=(False, 'stale certificate')):
            with self.assertRaisesRegex(L.SpecError, 'blocks completion'):
                L.seal(run, spec)
        with patch.object(L, '_gate_d85_certified', return_value=(True, 'verified build certificate')):
            packet = L.seal(run, spec)
        self.assertEqual(packet['verdict'], 'GO')
        self.assertEqual(packet['build_certifications'], ['verified build certificate'])

    def test_missing_declared_build_certificate_blocks(self):
        run, spec = self.build_run()
        with self.assertRaises(L.SpecError):
            L.mark_stage(run, spec, 'F', 'pass')

    def test_certificate_change_during_verification_blocks(self):
        run, spec = self.build_run()
        (self.cwd / 'build.json').write_text('{}')
        certificate = self.cwd / 'certificate.json'
        certificate.write_text('{}')
        def change_during_verify(*args, **kwargs):
            certificate.write_text('{"changed": true}')
            return subprocess.CompletedProcess(args, 0, '{"verdict": "CERTIFICATION_VERIFIED"}', '')
        with patch.object(L.subprocess, 'run', side_effect=change_during_verify):
            ok, detail = L._gate_d85_certified(run, spec, spec['stages'][0], spec['stages'][0]['gate'][0])
        self.assertFalse(ok)
        self.assertEqual(detail, 'build or certificate changed during verification')

    def test_real_declared_certificate_passes_and_tampering_blocks(self):
        run, spec = self.build_run()
        source = REPO_ROOT / 'capabilities/skills/rig-determinism-85/authority/reference/julie_synthetic'
        (self.cwd / 'build.json').write_bytes((source / 'build.json').read_bytes())
        (self.cwd / 'diagram.json').write_bytes((source / 'root/diagram.json').read_bytes())
        cli = REPO_ROOT / 'capabilities/skills/rig-determinism-85/bin/rig-determinism-85'
        result = subprocess.run([sys.executable, str(cli), 'checklist', str(self.cwd / 'build.json'),
                                 '--root', str(self.cwd), '--process-id', 'julie_synthetic'],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        certificate = self.cwd / 'certificate.json'
        certificate.write_text(result.stdout)
        gate = spec['stages'][0]['gate'][0]
        self.assertTrue(L._gate_d85_certified(run, spec, spec['stages'][0], gate)[0])
        packet = json.loads(certificate.read_text())
        packet['checks'] = []
        certificate.write_text(json.dumps(packet))
        self.assertFalse(L._gate_d85_certified(run, spec, spec['stages'][0], gate)[0])


class BuildDiagnosisGateTests(TempState):
    """A13/A53/A54: the build_diagnosis gate is halt-tier and non-forceable,
    re-checked at the final stage and at seal, while fail/park and reads stay
    usable when it is red."""

    GOOD_DIAG = {
        'goal': 'ship the criteria pack',
        'cell_id': 'L1-D1-A1-I1',
        'done_test': ['python3 rig_capabilities/criteria_pack.py generate --verify '
                      'runs/agentic-stack-buildout/packs/criteria-v1.jsonl'],
        'out_of_scope': ['push'],
        'effort_budget': {'cpu_minutes': 30, 'usd': 0.01, 'wallclock_seconds': 900},
        'evidence_refs': ['receipt:s4-manifest-gate-fires'],
    }

    def diag_run(self, seed_index=True):
        run = L.activate('iqrsqpi-v11', cwd=str(self.cwd), harness='ut')
        spec = dict(L.load_spec('iqrsqpi-v11'))
        spec['stages'] = [{'id': 'F', 'gate': [{'type': 'build_diagnosis',
                                                'diagnosis': 'diagnosis.json',
                                                'index': 'build-index.jsonl'}]}]
        (self.cwd / 'diagnosis.json').write_text(json.dumps(self.GOOD_DIAG))
        if seed_index:
            from rig_capabilities import build_index
            idx = build_index.open_live(REPO_ROOT, str(self.cwd / 'build-index.jsonl'))
            idx.insert('L1-D1-A1-I1', 'builds/l1-d1-a1-i1.json')
        return run, spec

    def gate(self, run, spec):
        return L._gate_build_diagnosis(run, spec, spec['stages'][0],
                                       spec['stages'][0]['gate'][0])

    def test_real_diagnosis_and_index_row_pass(self):
        run, spec = self.diag_run()
        ok, detail = self.gate(run, spec)
        self.assertTrue(ok, detail)
        self.assertIn('L1-D1-A1-I1', detail)

    def test_missing_diagnosis_packet_blocks(self):
        run, spec = self.diag_run()
        (self.cwd / 'diagnosis.json').unlink()
        ok, detail = self.gate(run, spec)
        self.assertFalse(ok)
        self.assertIn('unreadable', detail)

    def test_diagnosis_without_executable_acceptance_blocks(self):
        run, spec = self.diag_run()
        bad = dict(self.GOOD_DIAG)
        del bad['done_test']
        (self.cwd / 'diagnosis.json').write_text(json.dumps(bad))
        ok, detail = self.gate(run, spec)
        self.assertFalse(ok)
        self.assertIn('diagnosis refused', detail)

    def test_diagnosis_without_provenance_refs_blocks(self):
        run, spec = self.diag_run()
        bad = dict(self.GOOD_DIAG)
        bad['evidence_refs'] = []
        (self.cwd / 'diagnosis.json').write_text(json.dumps(bad))
        ok, detail = self.gate(run, spec)
        self.assertFalse(ok)
        self.assertIn('diagnosis refused', detail)

    def test_missing_index_row_blocks(self):
        run, spec = self.diag_run(seed_index=False)
        ok, detail = self.gate(run, spec)
        self.assertFalse(ok)
        self.assertIn('no row', detail)

    def test_row_bound_to_other_pack_blocks(self):
        run, spec = self.diag_run()
        index = self.cwd / 'build-index.jsonl'
        lines = []
        for ln in index.read_text().splitlines():
            rec = json.loads(ln)
            if 'cell_id' in rec:
                rec['pack_sha'] = '0' * 64
            lines.append(json.dumps(rec, sort_keys=True))
        index.write_text('\n'.join(lines) + '\n')
        ok, detail = self.gate(run, spec)
        self.assertFalse(ok)  # rejected either as stale row or corrupt index

    def test_red_diagnosis_cannot_be_forced_past_stage_pass(self):
        run, spec = self.diag_run()
        with patch.dict(L.GATE_TYPES, {'build_diagnosis': lambda *a: (False, 'stale pack')}):
            with self.assertRaisesRegex(L.SpecError, 'refusing pass'):
                L.mark_stage(run, spec, 'F', 'pass', force=True)
        self.assertNotEqual(run['stage_status'].get('F'), 'pass')

    def test_final_stage_rechecks_diagnosis_even_with_force(self):
        run, spec = self.diag_run()
        with patch.dict(L.GATE_TYPES, {'build_diagnosis': lambda *a: (True, 'initial pass')}), \
             patch.object(L, '_gate_build_diagnosis', return_value=(False, 'diagnosis stale')):
            with self.assertRaisesRegex(L.SpecError, 'blocks completion'):
                L.mark_stage(run, spec, 'F', 'pass', force=True)

    def test_seal_refuses_red_diagnosis_and_binds_green_evidence(self):
        run, spec = self.diag_run()
        run['stage_status']['F'] = 'pass'
        with patch.object(L, '_gate_build_diagnosis', return_value=(False, 'diagnosis stale')):
            with self.assertRaisesRegex(L.SpecError, 'blocks completion'):
                L.seal(run, spec)
        with patch.object(L, '_gate_build_diagnosis', return_value=(True, 'diagnosis bound')):
            packet = L.seal(run, spec)
        self.assertIn('diagnosis bound', packet['build_certifications'])

    def test_park_and_reads_stay_usable_while_diagnosis_is_red(self):
        run, spec = self.diag_run()
        with patch.dict(L.GATE_TYPES, {'build_diagnosis': lambda *a: (False, 'stale pack')}):
            L.mark_stage(run, spec, 'F', 'park', note='diagnosis red — parked for repair')
        reloaded = L.load_run(run['run_id'])
        self.assertEqual(reloaded['stage_status']['F'], 'park')


class GateDActionBindingTests(TempState):
    """A50 (loops side): an APPROVE authorizes exactly the action it was
    issued against; a later action cannot replay the earlier approval."""

    def _run(self):
        return L.activate('iqrsqpi-v11', cwd=str(self.cwd), harness='ut')

    def test_approval_does_not_replay_onto_a_new_action(self):
        run = self._run()
        L.gate_d_request(run, 'publish post #1 to LinkedIn')
        L.gate_d_approve(run, f"APPROVE {run['run_id']}")
        self.assertTrue(run['gate_d']['approved'])
        L.gate_d_request(run, 'deploy the landing page')
        self.assertFalse(run['gate_d']['approved'])
        L.gate_d_approve(run, f"APPROVE {run['run_id']}")
        self.assertTrue(run['gate_d']['approved'])

    def test_identical_re_request_keeps_its_approval(self):
        run = self._run()
        L.gate_d_request(run, 'publish post #1')
        L.gate_d_approve(run, f"APPROVE {run['run_id']}")
        L.gate_d_request(run, 'publish post #1')
        self.assertTrue(run['gate_d']['approved'])

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
        (art / "intent.md").write_text(f"## GOAL\ng\n## METRIC\nm\n## DONE-TEST\n- cmd:test -f {out}\n## OUT-OF-SCOPE\no\n## COORDINATE\nL3\n## UNCERTAINTY-LEVEL\n1\n## CONFIDENCE\n0.6\n")
        run = L.mark_stage(run, spec, "I1", "pass")
        (art / "questions.md").write_text(
        "## Panel\n- [lens:a]\n- [lens:b]\n- [lens:c]\n## Questions\n"
        + "\n".join(f"- [ASSUMED] What happens to the corpus index if assumption {i} about shard rotation is wrong? (assumption: rotation is stable)" for i in range(1, 286))
        + "\n" + "\n".join(f"- [BLOCKING] Which agent owns the research wave schedule for topic area {i} this quarter? -> ANSWER: the orchestrating agent owns it" for i in range(1, 17)) + "\n")
        run = L.mark_stage(run, spec, "Q1", "pass")
        (art / "research.md").write_text("## Findings\n- f\n## Sources\n- s (HIGH)\n## Corpus\n" + "\n".join(f'- corpus:rig_brain "t{i}" -> hits: {i}' for i in range(1, 11)) + "\n## Gaps\n- none\n")
        res = art.parent / "research"; res.mkdir(exist_ok=True)
        for w in ("wave-a", "wave-b"):
            (res / f"{w}.md").write_text("\n".join(f"F{i}. t (https://example.com/{w}{i})" for i in range(1, 7)) + "\n")
        (res / "questions-ut.md").write_text("\n".join(f"Q{i}. ut probe {i} about the corpus index shard rotation" for i in range(1, 301)) + "\n")
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
        tpl = L.verify(L.load_run(run["run_id"]), spec, "omp",
                       cmd_override="printf 'Output exactly: a line `VERDICT: "
                                    "PERFECT|VERIFIED|PARTIAL|FEEDBACK|FAILED`, then GAPS:\\n'")
        self.assertEqual(tpl["verdict"], "NO_VERDICT",
                         "the prompt template echoed in a transcript is not a verdict")
        real = L.verify(L.load_run(run["run_id"]), spec, "prime-agent",
                        cmd_override="printf 'thinking VERDICT: PARTIAL noise\\n"
                                     "final answer\\nVERDICT: VERIFIED\\n'")
        self.assertEqual(real["verdict"], "VERIFIED", "the last real verdict wins")
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
    def test_doctor_diagnoses_loop_without_selftest_cases(self):
        # A13: a declared loop missing tests/cases.json must be named, and must
        # make the diagnosis NOT OK — a loop whose gates can never be proven RED
        # is a diagnosis hole, not a green.
        import shutil
        import tempfile
        old = dict(L.SKILL_ROOTS)
        # a hand-written mini-spec would fail load_spec validation and land in
        # spec_errors instead of the diagnosis under test — clone a real spec
        src = Path(old["canonical"]) / "gate-d-loop" / "loop.yaml"
        fake = Path(tempfile.mkdtemp(prefix="rig-loop-nocases-"))
        (fake / "bare-loop").mkdir()
        (fake / "bare-loop" / "loop.yaml").write_text(
            src.read_text().replace("gate-d-loop", "bare-loop"))
        try:
            L.SKILL_ROOTS["canonical"] = fake
            rep = L.doctor()
            self.assertIn("bare-loop", rep["loops_missing_selftest"])
            self.assertFalse(rep["ok"])
            # plant-restore: cases present -> loop drops out of the red list
            cases = fake / "bare-loop" / "tests"
            cases.mkdir()
            shutil.copy(Path(old["canonical"]) / "gate-d-loop" / "tests" / "cases.json",
                        cases / "cases.json")
            rep2 = L.doctor()
            self.assertNotIn("bare-loop", rep2["loops_missing_selftest"])
        finally:
            L.SKILL_ROOTS.clear()
            L.SKILL_ROOTS.update(old)
            shutil.rmtree(fake, ignore_errors=True)

    def test_doctor_all_canonical_loops_carry_case_packs(self):
        rep = L.doctor()
        self.assertEqual(rep["loops_missing_selftest"], [],
                         f"loops without plant-case packs: {rep['loops_missing_selftest']}")

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
        home = patch.object(L, "HOME", self.root)
        home.start()
        self.addCleanup(home.stop)

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

    def test_wiring_rejects_drift_even_when_markers_survive(self):
        L.wire(apply=True)
        for harness in ("omp", "prime-agent"):
            path = L.HOOK_CONFIG[harness]
            path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        handler = L.HOOK_CONFIG["hermes"] / "handler.py"
        handler.write_text(handler.read_text() + "\n# drift\n")
        for harness in ("claude", "codex"):
            path = L.HOOK_CONFIG[harness]
            data = json.loads(path.read_text())
            data["hooks"]["PreToolUse"][0]["matcher"] = "Write"
            path.write_text(json.dumps(data))
        verdicts = L.verify_wiring()
        self.assertTrue(all(v["wired"] is False for v in verdicts.values()), verdicts)
        L.wire(apply=True)
        self.assertTrue(all(v["wired"] for v in L.verify_wiring().values()))

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
