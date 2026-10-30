#!/usr/bin/env python3
"""Fire a canonical hook against a fixture. Exit 0 only if it actually acted."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd, input_text="", expect_rc=None, expect_text=None, expect_empty=False, env=None) -> bool:
    r = subprocess.run(cmd, input=input_text, text=True, capture_output=True,
                       cwd=str(ROOT), timeout=15, check=False, env=env)
    if expect_rc is not None and r.returncode != expect_rc:
        print(f"rc {r.returncode} != {expect_rc}\n{r.stderr[-400:]}", file=sys.stderr)
        return False
    blob = (r.stdout or "") + (r.stderr or "")
    if expect_text and expect_text not in blob:
        print(f"missing {expect_text!r} in output\n{blob[-400:]}", file=sys.stderr)
        return False
    if expect_empty and blob.strip():
        print(f"expected no output\n{blob[-400:]}", file=sys.stderr)
        return False
    return True


def isolated_loop_env(root: Path) -> dict[str, str]:
    home = root / "home"
    home.mkdir()
    d85 = home / ".rig" / "d85"
    d85.mkdir(parents=True)
    (d85 / "enforcement.json").write_text(json.dumps({"roots": [], "ttl_hours": 24}))
    env = os.environ.copy()
    env.update({
        "HOME": str(home),
        "RIG_LOOP_STATE": str(root / "state"),
        "RIG_LOOP_PROOF_DIR": str(root / "proof"),
        "RIG_LOOP_CLI": str(ROOT / "bin" / "rig-loop"),
        "PYTHONPATH": os.pathsep.join(sys.path),
        "PATH": os.pathsep.join((str(Path.home() / ".bun" / "bin"), env.get("PATH", ""))),
    })
    return env


def activate_loop(env: dict[str, str], cwd: Path) -> bool:
    cwd.mkdir()
    return run(
        [sys.executable, str(ROOT / "bin" / "rig-loop"), "activate", "iqrsqpi-v11",
         "--cwd", str(cwd), "--harness", "fixture"],
        expect_rc=0,
        env=env,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: hook_fires.py <hook-id>", file=sys.stderr)
        return 2
    hid = argv[1]
    if hid == "guard-dangerous-commands.sh":
        deny = json.dumps({"tool_input": {"command": "rm -rf /"}})
        allow = json.dumps({"tool_input": {"command": "ls"}})
        ok = (
            run(["sh", "capabilities/hooks/guard-dangerous-commands.sh"],
                input_text=deny, expect_rc=2)
            and run(["sh", "capabilities/hooks/guard-dangerous-commands.sh"],
                    input_text=allow, expect_rc=0)
        )
    elif hid == "guard-secret-write.sh":
        deny = json.dumps({"tool_input": {"content": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"}})
        allow = json.dumps({"tool_input": {"content": "hello world"}})
        ok = (
            run(["sh", "capabilities/hooks/guard-secret-write.sh"],
                input_text=deny, expect_rc=2)
            and run(["sh", "capabilities/hooks/guard-secret-write.sh"],
                    input_text=allow, expect_rc=0)
        )
    elif hid == "goal-loop-startup.sh":
        ok = run(["bash", "capabilities/hooks/goal-loop-startup.sh"],
                 expect_rc=0, expect_text="GOAL LOOP ACTIVE")
    elif hid == "jake-pushback.sh":
        deny = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/tmp/demo.env"}})
        allow = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "/tmp/demo.env"}})
        ok = (
            run(["bash", "capabilities/hooks/jake-pushback.sh"],
                input_text=deny, expect_rc=1)
            and run(["bash", "capabilities/hooks/jake-pushback.sh"],
                    input_text=allow, expect_rc=0)
        )
    elif hid == "session-size-guard.sh":
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as fh:
            fh.write(b"x" * (2 * 1048576 + 10))
            tp = fh.name
        try:
            payload = json.dumps({"transcript_path": tp})
            ok = run(["bash", "capabilities/hooks/session-size-guard.sh"],
                     input_text=payload, expect_rc=0, expect_text="systemMessage")
        finally:
            os.unlink(tp)
    elif hid == "tac-plan-gate.sh":
        with tempfile.TemporaryDirectory(prefix="tac-plan-gate-") as tmp:
            env = os.environ.copy()
            env["HOME"] = tmp
            env["PATH"] = "/usr/bin:/bin"
            env["RIG_TAC_ENFORCE"] = "1"
            denied = run(["bash", "capabilities/hooks/tac-plan-gate.sh"],
                         input_text="{}", expect_rc=2, expect_text="BLOCKED", env=env)
            env["RIG_TAC_ENFORCE"] = "0"
            allowed = run(["bash", "capabilities/hooks/tac-plan-gate.sh"],
                          input_text="{}", expect_rc=0, expect_empty=True, env=env)
            ok = denied and allowed
    elif hid in ("rig-loop-hook.sh", "rig-loop-hooks.ts"):
        with tempfile.TemporaryDirectory(prefix="rig-loop-hook-") as tmp:
            root = Path(tmp)
            cwd = root / "work"
            env = isolated_loop_env(root)
            activated = activate_loop(env, cwd)
            if hid == "rig-loop-hook.sh":
                deny = json.dumps({
                    "cwd": str(cwd),
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(cwd / "src" / "x.py")},
                })
                allow = json.dumps({
                    "cwd": str(cwd),
                    "tool_name": "Read",
                    "tool_input": {"file_path": str(cwd / "src" / "x.py")},
                })
                denied = run(["bash", "capabilities/hooks/rig-loop-hook.sh", "pre-tool", "claude"],
                             input_text=deny, expect_rc=2,
                             expect_text='"permissionDecision": "deny"', env=env)
                allowed = run(["bash", "capabilities/hooks/rig-loop-hook.sh", "pre-tool", "claude"],
                              input_text=allow, expect_rc=0, expect_empty=True, env=env)
                ok = activated and denied and allowed
            else:
                fired = run(["bun", "scripts/rig_loop_hooks_fixture.ts", str(cwd)],
                            expect_rc=0, expect_text="deny=block allow=undefined", env=env)
                ok = activated and fired
    else:
        print(f"no deny/banner fixture for {hid}", file=sys.stderr)
        return 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
