"""Behavioral regressions for D85 boundary failures found after release 096d2ce."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_d85_admission import D85Case
from rig_capabilities import d85_admission as d85
from rig_capabilities import loops


class AuthorizationBoundaries(D85Case):
    def setUp(self):
        super().setUp()
        isolation = patch.dict(os.environ, {"RIG_LOOP_STATE": str(self.home / "loops")})
        isolation.start()
        self.addCleanup(isolation.stop)
        disabled = os.environ.pop("RIG_D85_DISABLE", None)
        if disabled is not None:
            self.addCleanup(os.environ.__setitem__, "RIG_D85_DISABLE", disabled)
        self.write_config()

    def dispatch(self, tool, inputs, session="sess-a"):
        return loops.dispatch_hook("pre-tool", {
            "tool_name": tool, "tool_input": inputs,
            "cwd": str(self.home), "session_id": session,
        })

    def test_malformed_root_schema_cannot_disable_enforcement(self):
        for roots in ([42], [""], "not-a-list", {}, [str(self.root), None], ["relative/path"]):
            with self.subTest(roots=roots):
                self.write_config(roots=roots)
                with self.assertRaises(d85.AdmissionDenied):
                    d85.load_config()
                self.deny(self.check("write", [self.target]))
        self.write_config(roots=[])
        with self.assertRaises(d85.AdmissionDenied):
            d85.load_config()
        self.deny(self.check("write", [self.target]))

    def test_duplicate_config_keys_are_not_an_operator_disable(self):
        config = self.home / "enforcement.json"
        config.write_text('{"roots":' + json.dumps([str(self.root)]) + ',"roots":[],"ttl_hours":24}')
        self.deny(self.check("write", [self.target]))

    def test_native_hashline_writes_require_admission(self):
        for operation in ("PUT 1.=1:\n+changed", "REM", "MV " + str(self.home / "moved.txt")):
            for wrapped in (False, True):
                with self.subTest(operation=operation, wrapped=wrapped):
                    text = f"[{self.target}#A1B2]\n{operation}\n"
                    if wrapped:
                        text = "*** Begin Patch\n" + text + "*** End Patch\n"
                    self.deny(self.dispatch("edit", {"input": text}))
        outside = self.home / "outside.txt"
        move_into_root = f"[{outside}#A1B2]\nMV {self.target}\n"
        self.deny(self.dispatch("edit", {"input": move_into_root}))
        self.admit([self.target])
        allowed = self.dispatch("edit", {"input": f"[{self.target}#A1B2]\nPUT 1.=1:\n+approved\n"})
        self.assertEqual(allowed.get("action"), "allow")

    def test_unresolved_mutation_targets_fail_closed(self):
        self.deny(self.dispatch("edit", {"input": "unrecognized edit format"}))
        self.deny(self.dispatch("write", {"content": "no target"}))
        self.assertEqual(self.dispatch("read", {"path": str(self.target)})["action"], "allow")

    def test_unknown_mcp_mutator_is_not_treated_as_read_only(self):
        self.deny(self.dispatch("mcp__filesystem__write_file", {"path": str(self.target), "content": "blocked"}))
        self.deny(self.dispatch("unregistered_tool", {"annotations": {"readOnlyHint": True}}))

    def test_host_owned_tool_policy_is_required_for_custom_reads(self):
        cfg = self.write_config()
        cfg["tool_capabilities"] = {"mcp__inventory__get_status": "read", "mcp__filesystem__write_file": "write"}
        (self.home / "enforcement.json").write_text(json.dumps(cfg))
        self.assertEqual(self.dispatch("mcp__inventory__get_status", {})["action"], "allow")
        self.deny(self.dispatch("mcp__filesystem__write_file", {"path": str(self.target), "content": "blocked"}))
    def test_custom_shell_capability_preserves_command_for_target_analysis(self):
        cfg = self.write_config()
        cfg["tool_capabilities"] = {"mcp__runner__shell": "shell"}
        (self.home / "enforcement.json").write_text(json.dumps(cfg))
        self.deny(self.dispatch(
            "mcp__runner__shell",
            {"command": f"/bin/rm -- {self.target}"},
        ))
        self.deny(self.dispatch(
            "mcp__runner__shell",
            {"script": f"/bin/rm -- {self.target}"},
        ))


    def test_missing_session_identity_cannot_reuse_a_cwd_grant(self):
        self.admit([self.target], session="sess-a")
        self.deny(self.dispatch("write", {"path": str(self.target), "content": "blocked"}, session=""))
        self.deny(self.dispatch("write", {"path": str(self.target), "content": "blocked"}, session="sess-b"))
        self.assertEqual(self.dispatch("write", {"path": str(self.target), "content": "approved"}, session="sess-a")["action"], "allow")
        with self.assertRaises(d85.AdmissionDenied):
            d85.session_key({"cwd": str(self.home)})

    def test_malformed_internal_verdicts_cannot_authorize(self):
        for verdict in ({}, "allow", True, [], {"action": "error"}, {"action": "allow"}):
            with self.subTest(verdict=verdict), patch.object(d85, "hook_check", return_value=verdict):
                self.deny(self.dispatch("write", {"path": str(self.target)}))

    def test_malformed_tool_identity_denies_instead_of_crashing(self):
        result = loops.dispatch_hook("pre-tool", {"tool_name": {"unexpected": "object"}, "tool_input": {"path": str(self.target)}, "cwd": str(self.home)})
        self.deny(result)

    def test_real_extension_separates_sessions_in_one_directory(self):
        import subprocess
        self.admit([self.target], session="sess-a")
        repo = Path(__file__).resolve().parent.parent
        shim = self.workspace / "rig-loop-test.py"
        shim.write_text(
            "import runpy, sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, {str(repo)!r})\n"
            "from rig_capabilities import d85_admission as d85\n"
            f"d85._TEST_HOME = Path({str(self.home)!r})\n"
            f"runpy.run_path({str(repo / 'bin/rig-loop')!r}, run_name='__main__')\n"
        )
        env = {
            key: value
            for key, value in os.environ.items()
            if key
            not in {
                "RIG_D85_DISABLE",
                "RIG_D85_TEST_PHRASE",
                "RIG_LOOP_CLI",
                "RIG_D85_HOME",
                "RIG_D85_CLI",
                "PYTHONPATH",
                "PYTHONSTARTUP",
                "BASH_ENV",
                "ENV",
            }
        }
        result = subprocess.run(
            [
                "bun",
                str(repo / "scripts/rig_loop_hooks_fixture.ts"),
                str(self.workspace),
                "session-isolation",
                str(self.target),
                str(shim),
            ],
            env=env,
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("session-a=allowed session-b=blocked missing-session=blocked", result.stdout)
