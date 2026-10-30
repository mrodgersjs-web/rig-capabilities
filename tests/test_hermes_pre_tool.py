from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPTER = REPO_ROOT / "capabilities/hooks/rig-hermes-pre-tool.py"
OUTER_GUARD = REPO_ROOT / "capabilities/hooks/rig-pre-tool-guard.py"


class HermesPreToolAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        hook = self.root / "capabilities/hooks/rig-hermes-pre-tool.py"
        hook.parent.mkdir(parents=True)
        shutil.copy2(ADAPTER, hook)
        self.adapter = hook
        self.engine = self.root / "bin/rig-loop"
        self.engine.parent.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_adapter(self, payload: object, *, engine: str, env: dict[str, str] | None = None):
        self.engine.write_text(engine, encoding="utf-8")
        return subprocess.run(
            ["/Users/rig128gb/.homebrew/Cellar/python@3.14/3.14.7/bin/python3", "-I", "-B", "-S", str(self.adapter)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, **(env or {})},
        )

    def test_valid_allow_and_deny_translate_to_hermes_contract(self) -> None:
        allow = self.run_adapter(
            {"tool_name": "read", "tool_input": {}, "session_id": "s", "cwd": str(self.root)},
            engine="import json\nprint(json.dumps({'block': False}))\n",
        )
        self.assertEqual(allow.returncode, 0, allow.stderr)
        self.assertEqual(json.loads(allow.stdout), {})

        deny = self.run_adapter(
            {"tool_name": "write_file", "tool_input": {}, "session_id": "s", "cwd": str(self.root)},
            engine="import json\nprint(json.dumps({'block': True, 'reason': 'exact denial'}))\n",
        )
        self.assertEqual(deny.returncode, 2)
        self.assertEqual(
            json.loads(deny.stdout),
            {"action": "block", "message": "exact denial"},
        )

    def test_invalid_or_failed_engine_denies_mutation_but_preserves_read_recovery(self) -> None:
        for engine in ("print('not-json')\n", "raise SystemExit(1)\n"):
            with self.subTest(engine=engine):
                denied = self.run_adapter(
                    {"tool_name": "terminal", "tool_input": {}, "session_id": "s", "cwd": str(self.root)},
                    engine=engine,
                )
                self.assertEqual(denied.returncode, 2)
                self.assertEqual(json.loads(denied.stdout)["action"], "block")
                allowed = self.run_adapter(
                    {"tool_name": "read", "tool_input": {}, "session_id": "s", "cwd": str(self.root)},
                    engine=engine,
                )
                self.assertEqual(allowed.returncode, 0)
                self.assertEqual(json.loads(allowed.stdout), {})

    def test_effective_workdir_and_clean_environment_reach_gate(self) -> None:
        marker = self.root / "observed.json"
        workdir = self.root / "workspace"
        workdir.mkdir()
        engine = (
            "import json, os, pathlib, sys\n"
            "payload = json.load(sys.stdin)\n"
            f"pathlib.Path({str(marker)!r}).write_text(json.dumps({{'cwd': payload['cwd'], 'clean': all(key not in os.environ for key in ('PYTHONPATH', 'BASH_ENV', 'ENV', 'RIG_D85_DISABLE'))}}))\n"
            "print(json.dumps({'block': False}))\n"
        )
        result = self.run_adapter(
            {
                "tool_name": "read",
                "tool_input": {"workdir": "workspace"},
                "session_id": "session-1",
                "cwd": str(self.root),
            },
            engine=engine,
            env={"PYTHONPATH": "/tmp/evil", "BASH_ENV": "/tmp/evil", "ENV": "/tmp/evil"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(marker.read_text()),
            {"cwd": str(workdir.resolve()), "clean": True},
        )

class ClaudeCodexPreToolGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        hook = self.root / "capabilities/hooks/rig-pre-tool-guard.py"
        hook.parent.mkdir(parents=True)
        shutil.copy2(OUTER_GUARD, hook)
        self.adapter = hook
        self.engine = self.root / "bin/rig-loop"
        self.engine.parent.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_adapter(self, tool: str, engine: str) -> subprocess.CompletedProcess:
        self.engine.write_text(engine, encoding="utf-8")
        return subprocess.run(
            [
                "/Users/rig128gb/.homebrew/Cellar/python@3.14/3.14.7/bin/python3",
                "-I", "-B", "-S", str(self.adapter),
            ],
            input=json.dumps({
                "tool_name": tool,
                "tool_input": {},
                "session_id": "session",
                "cwd": str(self.root),
            }),
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_valid_engine_translates_block_to_exit_two(self) -> None:
        denied = self.run_adapter(
            "write",
            "import json\nprint(json.dumps({'block': True, 'reason': 'blocked'}))\n",
        )
        self.assertEqual(denied.returncode, 2)
        self.assertIn("blocked", denied.stderr)
        allowed = self.run_adapter(
            "write",
            "import json\nprint(json.dumps({'block': False}))\n",
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_engine_failure_denies_mutation_but_preserves_read_recovery(self) -> None:
        engine = "raise SystemExit(1)\n"
        self.assertEqual(self.run_adapter("write", engine).returncode, 2)
        self.assertEqual(self.run_adapter("read", engine).returncode, 0)

class WrapperEnvironmentForwardingTests(unittest.TestCase):
    def load_wrapper(self, path: Path, name: str):
        spec = importlib.util.spec_from_file_location(name, path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_present_flag_is_forwarded_verbatim_and_hostile_env_stays_scrubbed(self) -> None:
        for index, path in enumerate((ADAPTER, OUTER_GUARD)):
            module = self.load_wrapper(path, f"d85_wrapper_{index}")
            for flag in ("yes", "1"):
                with self.subTest(path=path.name, flag=flag), patch.dict(
                    os.environ,
                    {
                        "RIG_D85_DISABLE": flag,
                        "PATH": "/tmp/hostile",
                        "IFS": "hostile",
                    },
                    clear=False,
                ):
                    environment = module._clean_environment()
                    self.assertEqual(environment["RIG_D85_DISABLE"], flag)
                    self.assertEqual(
                        environment["PATH"], "/usr/bin:/bin:/usr/sbin:/sbin")
                    self.assertNotIn("IFS", environment)

            with self.subTest(path=path.name, flag="absent"), patch.dict(
                os.environ, {}, clear=True
            ):
                self.assertNotIn(
                    "RIG_D85_DISABLE", module._clean_environment())




if __name__ == "__main__":
    unittest.main()
