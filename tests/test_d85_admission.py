"""D85 admission gate: fail-closed check + typed approve + OS-sandboxed launcher.

RED cases must be denied by the gate (no admission, cross-target, expiry,
session mismatch, malformed/tampered ledger, build drift, shell bypass vectors,
ungated outside-root launch, unavailable sandbox). GREEN cases cover the full
admit ceremony against the Julie synthetic fixture and the sandboxed launcher.
"""

import json
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import d85_admission as d85  # noqa: E402

AUTHORITY = (
    REPO_ROOT / "capabilities/skills/rig-determinism-85/authority/reference/julie_synthetic"
)
SANDBOX_EXEC = "/usr/bin/sandbox-exec"


def sh(cmd, **kw):
    env = dict(kw.pop("env", os.environ))
    env.pop("RIG_D85_DISABLE", None)
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=120, env=env, **kw
    )


class D85Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        test_mode = patch.dict(os.environ, {"RIG_D85_TEST_PHRASE": "1"})
        test_mode.start()
        self.addCleanup(test_mode.stop)
        self._prev_env = os.environ.get("RIG_D85_HOME")
        os.environ["RIG_D85_HOME"] = str(self.home)
        self.root = self.home / "protected"
        self.root.mkdir()
        self.fixture = self.home / "fixture"
        shutil.copytree(AUTHORITY, self.fixture, ignore=shutil.ignore_patterns("certificate.json", "__pycache__"))
        self.build = self.fixture / "build.json"
        self.target = self.root / "d85-test-target.json"

    def tearDown(self):
        if self._prev_env is None:
            os.environ.pop("RIG_D85_HOME", None)
        else:
            os.environ["RIG_D85_HOME"] = self._prev_env
        self._tmp.cleanup()

    # -- helpers ---------------------------------------------------------

    def write_config(self, roots=None, ttl=24):
        cfg = {"roots": [str(self.root)] if roots is None else roots, "ttl_hours": ttl}
        (self.home / "enforcement.json").write_text(json.dumps(cfg))
        return cfg

    def admit(self, paths, session="sess-a", build_file=None, process_id=None):
        build = build_file or self.build
        req = d85.admit_request(build, process_id, paths, "sid:" + session)
        return d85.admit_approve(f"APPROVE {req['admission_id']}")

    def check(self, tool, paths=(), command=None, cwd=None, session="sess-a", now=None):
        return d85.hook_check(
            {
                "tool": tool,
                "paths": [str(p) for p in paths],
                "command": command,
                "cwd": str(cwd) if cwd else None,
                "session_id": session,
            }, now=now,
        )

    def deny(self, verdict, why=""):
        self.assertIsNotNone(verdict, f"expected deny {why}, got allow")
        self.assertEqual(verdict.get("action"), "deny")


class TestGateRed(D85Case):
    @unittest.skipUnless(Path('/Users/rig128gb/.rig/bin/jake-greet').is_file(), 'local greeter absent')
    def test_live_reviewed_greeter_ignores_cwd_and_path_python_overrides(self):
        greeter = Path('/Users/rig128gb/.rig/bin/jake-greet')
        self.assertEqual(hashlib.sha256(greeter.read_bytes()).hexdigest(), d85._JAKE_GREET_SHA256)
        (self.home / 'json.py').write_text("raise RuntimeError('cwd module executed')\n")
        fake_python = self.home / 'python3'
        fake_python.write_text("#!/bin/sh\nprintf 'PATH override executed'\nexit 99\n")
        fake_python.chmod(0o700)
        env = dict(os.environ, PATH=str(self.home), PYTHONPATH=str(self.home))
        run = subprocess.run([str(greeter), '--agent', 'codex', '--json'], cwd=self.home,
                             env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['agent'], 'codex')
        self.assertNotIn('override executed', run.stdout + run.stderr)

    def test_reviewed_jake_greeting_allows_only_exact_read_command(self):
        greeter = Path('/Users/rig128gb/.rig/bin/jake-greet')
        self.write_config(roots=[str(greeter.parent)])
        command = str(greeter) + ' --agent codex'
        reviewed = b"#!/bin/sh\nprintf 'hello'\n"
        pinned_hash = patch.object(d85, '_JAKE_GREET_SHA256', hashlib.sha256(reviewed).hexdigest())
        read_bytes = patch.object(Path, 'read_bytes', return_value=reviewed)
        pinned_hash.start()
        read_bytes.start()
        self.addCleanup(pinned_hash.stop)
        self.addCleanup(read_bytes.stop)
        for suffix in ('', ' --json'):
            self.assertIsNone(self.check('bash', command=command + suffix, cwd='/tmp'))
        for changed in (
            command + ' > ' + str(greeter.parent / 'output'),
            command + '; touch ' + str(greeter.parent / 'output'),
            command + '\ntouch ' + str(greeter.parent / 'output'),
            'PATH=/tmp ' + command,
            command + ' --write',
            str(greeter.parent / 'other' / 'jake-greet') + ' --agent codex',
        ):
            self.deny(self.check('bash', command=changed, cwd='/tmp'))
        with patch.object(Path, 'read_bytes', return_value=reviewed + b'changed'):
            self.deny(self.check('bash', command=command, cwd='/tmp'))
        with patch.object(Path, 'read_bytes', side_effect=OSError('unreadable')):
            self.deny(self.check('bash', command=command, cwd='/tmp'))

    def test_no_admission_denies_root_write(self):
        self.write_config()
        self.deny(self.check("write", [self.target]), "no admission")

    def test_outside_root_paths_pass_without_admission(self):
        self.write_config()
        with tempfile.TemporaryDirectory() as t:
            self.assertIsNone(self.check("write", [Path(t) / "x.py"]))

    def test_missing_config_fails_closed(self):
        self.deny(self.check("write", [self.target]), "no config")

    def test_malformed_config_fails_closed(self):
        (self.home / "enforcement.json").write_text("{not json")
        self.deny(self.check("write", [self.target]), "bad config")

    def test_cross_target_denied(self):
        self.write_config()
        self.admit([self.target])
        self.deny(self.check("write", [self.root / "other.json"]), "cross-target")

    def test_expired_admission_denied(self):
        self.write_config(ttl=1)
        rec = self.admit([self.target])
        self.assertIsNone(self.check("write", [self.target], now=rec["expires_at"] - 1))
        self.deny(self.check("write", [self.target], now=rec["expires_at"]), "expiry boundary")
        self.deny(self.check("write", [self.target], now=rec["expires_at"] + 1), "expired")

    def test_fractional_expiry_boundary_does_not_truncate_the_clock(self):
        self.write_config(ttl=0.0005)
        req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
        rec = d85.admit_approve(f"APPROVE {req['admission_id']}", now=1000.25)
        self.assertIsNone(self.check("write", [self.target], now=rec["expires_at"] - 0.1))
        self.deny(self.check("write", [self.target], now=rec["expires_at"]), "fractional expiry")
        self.deny(self.check("write", [self.target], now=rec["issued_at"] - 0.1), "before issuance")

    def test_invalid_ttl_never_mints_an_approval(self):
        for ttl in (0, -1, 24.1, float("nan"), float("inf"), float("-inf")):
            with self.subTest(ttl=ttl):
                self.write_config(ttl=ttl)
                req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
                with self.assertRaises(d85.AdmissionDenied):
                    d85.admit_approve(f"APPROVE {req['admission_id']}")
                self.deny(self.check("write", [self.target]))
                self.assertFalse((self.home / "admissions/approvals.jsonl").exists())

    def test_empty_admission_scope_is_rejected(self):
        self.write_config()
        for paths, launchers in (([], []), ([""], []), ([], [" "])):
            with self.subTest(paths=paths, launchers=launchers):
                with self.assertRaises(d85.AdmissionDenied):
                    d85.admit_request(self.build, None, paths, "sid:sess-a", launchers=launchers)
        self.assertFalse((self.home / "admissions/requests.jsonl").exists())

    def test_arbitrary_code_stays_denied_even_with_path_admission(self):
        self.write_config()
        self.admit([self.target])
        self.deny(self.check("eval", [self.target], command="print(1)"))

    def test_session_mismatch_denied(self):
        self.write_config()
        self.admit([self.target], session="sess-a")
        self.deny(
            self.check("write", [self.target], session="sess-b"), "session mismatch"
        )

    def test_tampered_signature_denied(self):
        self.write_config()
        self.admit([self.target])
        ledger = self.home / "admissions" / "approvals.jsonl"
        lines = ledger.read_text().splitlines()
        rec = json.loads(lines[-1])
        rec["paths"].append(str(self.root / "extra.json"))  # forge wider grant
        lines[-1] = json.dumps(rec)  # signature no longer matches payload
        ledger.write_text("\n".join(lines) + "\n")
        self.deny(self.check("write", [self.root / "extra.json"]), "forged record")

    def test_build_changed_after_approval_denied(self):
        self.write_config()
        with tempfile.TemporaryDirectory() as bd:
            build = Path(bd) / "build.json"
            build.write_text((AUTHORITY / "build.json").read_text())
            shutil.copytree(AUTHORITY / "root", Path(bd) / "root")  # bound inventory
            self.admit([self.target], build_file=build)
            build.write_text(build.read_text() + "\n")  # drift
            self.deny(self.check("write", [self.target]), "build drift")

    def test_unknown_verb_touching_root_denied(self):
        self.write_config()
        self.deny(
            self.check("bash", command=f"python {self.root}/helper.py"),
            "unknown verb names root path",
        )

    def test_cwd_under_root_unproven_denied(self):
        self.write_config()
        self.deny(self.check("bash", command="make all", cwd=self.root), "cwd in root")

    def test_symlink_alias_denied(self):
        self.write_config()
        with tempfile.TemporaryDirectory() as t:
            link = Path(t) / "alias.json"
            link.symlink_to(self.target)
            self.deny(self.check("write", [link]), "symlink alias")

    def test_redirect_into_root_denied(self):
        self.write_config()
        self.deny(
            self.check("bash", command=f"cat /etc/hosts > {self.target}"),
            "readonly verb + redirect",
        )

    def test_mutation_verb_relative_operand_denied(self):
        self.write_config()
        self.deny(
            self.check(
                "bash", command=f"cd {self.root} && rm jobs.json", cwd=self.root
            ),
            "relative rm operand",
        )


class TestGateGreen(D85Case):
    def test_admit_roundtrip_allows_exact_target(self):
        self.write_config()
        self.admit([self.target])
        self.assertIsNone(self.check("write", [self.target]))
        self.assertIsNone(self.check("bash", command=f"cp a {self.target}"))
        self.assertIsNone(self.check("bash", command=f"touch {self.target}"))

    def test_readonly_ops_pass_unadmitted(self):
        self.write_config()
        self.assertIsNone(self.check("bash", command="cat /etc/hosts"))
        self.assertIsNone(self.check("bash", command="git status"))
        self.assertIsNone(self.check("read", [self.target]))


class TestMutationTargets(unittest.TestCase):
    def test_extracts_operands(self):
        t, unk, unprov = d85.mutation_targets_ex(
            {"tool": "Bash", "command": "rm -f /a/b.json && cat x > /c/d.txt"}
        )
        self.assertIn("/a/b.json", [str(x) for x in t])
        self.assertIn("/c/d.txt", [str(x) for x in t])
        self.assertFalse(unprov)

    def test_sed_inplace_and_tee(self):
        t, _, _ = d85.mutation_targets_ex(
            {"tool": "Bash", "command": "sed -i s/a/b/ /e/f.txt; tee /g/h.txt"}
        )
        got = {str(x) for x in t}
        self.assertTrue({"/e/f.txt", "/g/h.txt"} <= got)

    def test_unknown_verb_flagged(self):
        _, unk, unprov = d85.mutation_targets_ex(
            {"tool": "Bash", "command": "python /opt/root/tool.py"}
        )
        self.assertTrue(unprov)



class TestLauncherModels(D85Case):
    def make_job(self, body):
        job = self.home / "job.py"
        job.write_text(body)
        return job
    def test_launcher_rewritten_after_approval_denied(self):
        self.write_config()
        job = self.make_job("print('RAN')\n")
        build = self.build
        req = d85.admit_request(build, None, [self.target],
                                "sid:" + str(self.home), launchers=[str(job)])
        d85.admit_approve(f"APPROVE {req['admission_id']}")
        job.write_text("print('REWRITTEN')\n")  # drift after approval
        try:
            d85._launcher_authorized(job)
            self.fail("rewritten launcher must not authorize")
        except d85.AdmissionDenied:
            pass

    def test_missing_launcher_at_request_denied(self):
        self.write_config()
        try:
            d85.admit_request(self.build, None, [self.target],
                              "sid:t", launchers=[str(self.home / "nope.py")])
            self.fail("non-file launcher must be rejected at request time")
        except d85.AdmissionDenied:
            pass

    def test_forged_launcher_digest_denied(self):
        """Mutate a pending request's launcher_digests without recomputing ID."""
        self.write_config()
        req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
        rp = d85._requests_path()
        lines = rp.read_text().splitlines()
        rec = json.loads(lines[-1])
        rec["launcher_digests"] = {"/tmp/evil.py": "0" * 64}
        lines[-1] = json.dumps(rec)
        rp.write_text("\n".join(lines) + "\n")
        try:
            d85.admit_approve(f"APPROVE {req['admission_id']}")
            self.fail("forged launcher_digests must fail ID recomputation")
        except d85.AdmissionDenied:
            pass


@unittest.skipIf(not os.path.exists(SANDBOX_EXEC), "sandbox-exec missing")
class TestLauncher(D85Case):
    def make_job(self, body):
        job = self.home / "job.py"
        job.write_text(body)
        return job

    def test_outside_root_ungated_script_denied(self):
        """Advisory: script location must not weaken the boundary."""
        self.write_config()
        job = self.make_job(
            "from pathlib import Path\n"
            f"Path({str(self.target)!r}).write_text('pwn')\n"
            "print('BYPASS_WRITE_SUCCEEDED')\n"
        )
        r = sh(
            f'{sys.executable} -c "import sys; sys.path.insert(0, {str(REPO_ROOT)!r}); '
            f'from rig_capabilities import d85_admission as d; '
            f'sys.exit(d.run_launcher([{str(job)!r}]))"',
            env={**os.environ, "RIG_D85_HOME": str(self.home)},
        )
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertNotIn("BYPASS_WRITE_SUCCEEDED", r.stdout + r.stderr)
        self.assertFalse(self.target.exists())

    def test_admitted_literal_writable_sibling_denied(self):
        self.write_config()
        sibling = self.root / "d85-test-sibling.json"
        job = self.make_job(
            "from pathlib import Path\n"
            f"Path({str(self.target)!r}).write_text('ok'); print('ADMITTED_OK')\n"
            "try:\n"
            f"    Path({str(sibling)!r}).write_text('x')\n"
            "    print('SIBBY_BYPASS')\n"
            "except PermissionError:\n"
            "    print('SIBLING_DENIED')\n"
        )
        req = d85.admit_request(self.build, None, [self.target],
                                "sid:" + str(self.home), launchers=[str(job)])
        d85.admit_approve(f"APPROVE {req['admission_id']}")
        r = sh(
            f'{sys.executable} -c "import sys; sys.path.insert(0, {str(REPO_ROOT)!r}); '
            f'from rig_capabilities import d85_admission as d; '
            f'sys.exit(d.run_launcher([{str(job)!r}]))"',
            env={**os.environ, "RIG_D85_HOME": str(self.home)},
        )
        out = r.stdout + r.stderr
        self.assertIn("ADMITTED_OK", out, out)
        self.assertIn("SIBLING_DENIED", out, out)
        self.assertNotIn("SIBBY_BYPASS", out)
        self.assertEqual(self.target.read_text(), "ok")

    def test_missing_sandbox_binary_fails_closed(self):
        self.write_config()
        job = self.make_job("print('RAN')\n")
        req = d85.admit_request(self.build, None, [], "sid:sess-a", launchers=[str(job)])
        d85.admit_approve(f"APPROVE {req['admission_id']}")
        prev = d85._SANDBOX_EXEC
        d85._SANDBOX_EXEC = None
        try:
            rc = d85.run_launcher([str(job)])
        finally:
            d85._SANDBOX_EXEC = prev
        self.assertEqual(rc, 2)

    def test_bad_literal_charset_rejected(self):
        self.write_config()
        job = self.make_job("print('RAN')\n")
        with self.assertRaises(d85.AdmissionDenied):
            d85._sandbox_argv(self.write_config(), {"paths": [str(self.root / 'bad\"name')]}, job, [str(job)])

    def test_directory_output_does_not_admit_descendant_writes(self):
        self.write_config()
        directory = self.root / "output"
        directory.mkdir()
        child = directory / "child.txt"
        job = self.make_job(
            "from pathlib import Path\n"
            "try:\n"
            f"    Path({str(child)!r}).write_text('not admitted')\n"
            "except PermissionError:\n"
            "    print('CHILD_DENIED')\n"
            "else:\n"
            "    raise AssertionError('directory grant became recursive')\n"
        )
        req = d85.admit_request(self.build, None, [directory], "sid:sess-a", launchers=[str(job)])
        d85.admit_approve(f"APPROVE {req['admission_id']}")
        env = {k: v for k, v in os.environ.items() if k != "RIG_D85_DISABLE"}
        result = subprocess.run([sys.executable, str(d85.D85_CLI), "d85-run", str(job)],
                                capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "CHILD_DENIED")
        self.assertFalse(child.exists())

    def test_launcher_only_cli_grant_never_makes_launcher_writable(self):
        self.write_config()
        job = self.root / "job.py"
        body = (
            "from pathlib import Path\n"
            "try:\n"
            "    Path(__file__).write_text('tampered')\n"
            "except PermissionError:\n"
            "    print('SELF_WRITE_DENIED')\n"
            "else:\n"
            "    raise AssertionError('launcher implicitly writable')\n"
        )
        job.write_text(body)
        cli = str(d85.D85_CLI)
        env = {k: v for k, v in os.environ.items() if k not in ("RIG_D85_DISABLE", "RIG_D85_TEST_PHRASE")}
        request = subprocess.run(
            [sys.executable, cli, "admit-request", str(self.build), "--launcher", str(job), "--session-key", "sid:sess-a"],
            capture_output=True, text=True, env=env, timeout=30,
        )
        self.assertEqual(request.returncode, 0, request.stderr)
        req = json.loads(request.stdout)
        self.assertEqual(d85.admit_status()["requests"][-1]["launchers"], [str(job.resolve())])
        refused = subprocess.run(
            [sys.executable, cli, "admit-approve", "--phrase", f"APPROVE {req['admission_id']}"],
            capture_output=True, text=True, env=env, timeout=30,
        )
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertFalse((self.home / "admissions/approvals.jsonl").exists())
        d85.admit_approve(f"APPROVE {req['admission_id']}")
        self.assertEqual(d85.admit_status()["approvals"][-1]["launchers"], [str(job.resolve())])
        self.deny(self.check("write", [job]))
        executed = subprocess.run(
            [sys.executable, cli, "d85-run", str(job)],
            capture_output=True, text=True, env=env, cwd=self.home, timeout=30,
        )
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertEqual(executed.stdout.strip(), "SELF_WRITE_DENIED")
        self.assertEqual(job.read_text(), body)


class TestApprovalBoundary(D85Case):
    def test_api_supplied_phrase_requires_explicit_isolated_test_mode(self):
        self.write_config()
        req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
        with patch.dict(os.environ, {"RIG_D85_TEST_PHRASE": ""}):
            with self.assertRaises(d85.AdmissionDenied):
                d85.admit_approve(f"APPROVE {req['admission_id']}")
        self.assertFalse((self.home / "admissions/approvals.jsonl").exists())

    def test_test_flag_cannot_target_production_home(self):
        operator = self.home / "operator"
        production = operator / ".rig/d85"
        production.mkdir(parents=True)
        (production / "enforcement.json").write_text(json.dumps({"roots": [str(self.root)], "ttl_hours": 24}))
        with patch.object(Path, "home", return_value=operator), \
             patch.dict(os.environ, {"RIG_D85_HOME": str(production)}):
            req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
            with self.assertRaises(d85.AdmissionDenied):
                d85.admit_approve(f"APPROVE {req['admission_id']}")
        self.assertFalse((production / "admissions/approvals.jsonl").exists())

    def test_test_ledger_symlink_cannot_escape_isolated_home(self):
        self.write_config()
        req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
        with tempfile.TemporaryDirectory() as outside:
            ledger = Path(outside) / "approvals.jsonl"
            ledger.write_text("unchanged")
            (self.home / "admissions/approvals.jsonl").symlink_to(ledger)
            with self.assertRaises(d85.AdmissionDenied):
                d85.admit_approve(f"APPROVE {req['admission_id']}")
            self.assertEqual(ledger.read_text(), "unchanged")

    def test_api_acquires_tty_before_minting(self):
        self.write_config()
        req = d85.admit_request(self.build, None, [self.target], "sid:sess-a")
        with patch("builtins.open", side_effect=OSError("no controlling terminal")):
            with self.assertRaises(d85.AdmissionDenied):
                d85.admit_approve()
        self.assertFalse((self.home / "admissions/approvals.jsonl").exists())
        terminal = io.StringIO(f"APPROVE {req['admission_id']}\n")
        with patch("builtins.open", return_value=terminal), patch.object(terminal, "isatty", return_value=True):
            record = d85.admit_approve()
        self.assertEqual(record["how"], "typed-approve")
        self.assertIsNone(self.check("write", [self.target]))


class TestEnforcementPath(D85Case):
    def run_hook(self, tool, inputs, cli=None):
        env = {k: v for k, v in os.environ.items() if k != "RIG_D85_DISABLE"}
        env["RIG_LOOP_STATE"] = str(self.home / "loop-state")
        result = subprocess.run(
            [sys.executable, "-B", str(cli or REPO_ROOT / "bin/rig-loop"), "hook", "pre-tool", "--format", "pi"],
            input=json.dumps({"tool_name": tool, "tool_input": inputs, "cwd": str(self.home)}),
            capture_output=True, text=True, env=env, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["block"]

    def test_real_hook_does_not_apply_build_admission_to_ordinary_tools(self):
        self.write_config()
        self.assertIs(self.run_hook("read", {"path": str(self.target)}), False)
        for tool in ("write", "MultiEdit", " Multi-Edit ", "Notebook-Edit", "applypatch",
                     "create-file", "apply-patch", "str_replace_editor"):
            with self.subTest(tool=tool):
                self.assertIs(self.run_hook(tool, {"path": str(self.target)}), False)
        for tool in ("bash", "shell", "run-command", "exec", "terminal", "execute_command"):
            with self.subTest(tool=tool):
                self.assertIs(self.run_hook(tool, {"cmd": f"touch {self.target}"}), False)
        self.assertIs(self.run_hook("eval", {"code": "print(1)"}), False)
        self.assertIs(self.run_hook(" Python-Repl ", {"code": "print(1)"}), False)

    def test_missing_and_broken_build_gate_does_not_stop_ordinary_tools(self):
        replica = self.home / "replica"
        package = replica / "rig_capabilities"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
        shutil.copy2(REPO_ROOT / "rig_capabilities/loops.py", package / "loops.py")
        cli = replica / "bin/rig-loop"
        cli.parent.mkdir()
        shutil.copy2(REPO_ROOT / "bin/rig-loop", cli)
        for defect in ("missing", "syntax_error"):
            with self.subTest(defect=defect):
                if defect == "syntax_error":
                    (package / "d85_admission.py").write_text("def broken(:\n")
                self.assertIs(self.run_hook("write", {"path": str(self.target)}, cli), False)
                self.assertIs(self.run_hook("eval", {"code": "print(1)"}, cli), False)
                self.assertIs(self.run_hook("read", {"path": str(self.target)}, cli), False)


if __name__ == "__main__":
    unittest.main()
