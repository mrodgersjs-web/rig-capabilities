#!/usr/bin/env python3
"""Fire a canonical hook against fixtures and assert it acts (blocks/allows/redacts).

usage: hook_fires_misc.py <hook-file-name>
Covers: done-gate.py, done-gate.sh, jev-bash-gate.sh, redact_state.py,
        s1gate-stage-gate.sh, s1gate-stage-gate-redacted.sh, memory-fleet.py.
Exit 0 only when every assertion holds. Stdlib only. No network: Jev/gate binaries
are replaced with local fakes inside a temp dir.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "capabilities" / "hooks"


def run(cmd, stdin="", env=None, cwd=None):
    return subprocess.run(cmd, input=stdin, text=True, capture_output=True,
                          cwd=str(cwd or ROOT), env=env, timeout=30, check=False)


def need(cond, msg):
    if not cond:
        print("FAIL:", msg, file=sys.stderr)
    return bool(cond)


def clean_env(tmp: Path, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("DONE_GATE", "DONE_GATE_ENFORCE", "JEV_GATE", "S1GATE_ENFORCE", "S1GATE_BIN")}
    env["HOME"] = str(tmp)
    (tmp / ".rig" / "s1gate").mkdir(parents=True, exist_ok=True)
    env.update(extra)
    return env


FAIL_TAIL = "$ pytest -q\n3 tests failed\nAssertionError: boom\nAll done."
PASS_TAIL = "$ pytest -q\n5 tests passed\nAll done."


def t_done_gate(entry):
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        cmd = (["python3", str(HOOKS / entry)] if entry.endswith(".py") else ["bash", str(HOOKS / entry)])
        env = clean_env(tmp, DONE_GATE_ENFORCE="1")
        blocked = run(cmd, json.dumps({"tail": FAIL_TAIL}), env)
        ok = need(blocked.returncode == 2 and "done-gate BLOCK" in blocked.stderr, f"failing suite + done claim must block: rc={blocked.returncode} {blocked.stderr[-200:]}")
        allowed = run(cmd, json.dumps({"tail": PASS_TAIL}), env)
        ok &= need(allowed.returncode == 0 and not allowed.stderr.strip(), f"verified claim must pass silently: rc={allowed.returncode} {allowed.stderr[-200:]}")
        shadow = run(cmd, json.dumps({"tail": FAIL_TAIL}), clean_env(tmp, DONE_GATE_ENFORCE="0"))
        ok &= need(shadow.returncode == 0 and "WARN (shadow)" in shadow.stderr, "shadow mode warns but never blocks")
        off = run(cmd, json.dumps({"tail": FAIL_TAIL}), clean_env(tmp, DONE_GATE_ENFORCE="1", DONE_GATE="0"))
        ok &= need(off.returncode == 0 and not off.stderr.strip(), "DONE_GATE=0 kill switch must exit 0 silently")
        log = tmp / ".rig" / "s1gate" / "done-gate.jsonl"
        ok &= need(log.exists() and "failed_suite" in log.read_text(), "decision row written to done-gate.jsonl")
        return ok


def t_jev_bash_gate():
    src = (HOOKS / "jev-bash-gate.sh").read_text()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        fake = tmp / "fake-gate"
        glog = tmp / "jev-gate.log"

        def make(p):
            fake.write_text("#!/bin/sh\ncat >/dev/null\necho '{\"answers\":{\"destructive_irreversible\":{\"noul\":" + p + "}}}'\n")
            fake.chmod(0o755)
        # point the hook copy at the fake gate and a temp log; logic is otherwise untouched
        patched = src.replace("/Users/rig128gb/.rig/bin/rig-s1gate", str(fake)).replace("/Users/rig128gb/.rig/s1gate/jev-gate.log", str(glog))
        need(patched != src, "hook still hardcodes the gate path (fixture substitution found nothing)")
        h = tmp / "jev-bash-gate.sh"
        h.write_text(patched)
        payload = json.dumps({"tool_input": {"command": "find / -name '*.db' -delete"}})
        make("0.97")
        blocked = run(["sh", str(h)], payload)
        ok = need(blocked.returncode == 2 and "jev-bash-gate BLOCK" in blocked.stderr, f"p=0.97 must block: rc={blocked.returncode} {blocked.stderr[-160:]}")
        ok &= need(glog.exists() and "destr=0.97" in glog.read_text(), "gate decision logged")
        make("0.05")
        allowed = run(["sh", str(h)], payload)
        ok &= need(allowed.returncode == 0, "p=0.05 must allow")
        env = dict(os.environ, JEV_GATE="0")
        make("0.97")
        ok &= need(run(["sh", str(h)], payload, env).returncode == 0, "JEV_GATE=0 kill switch must allow")
        ok &= need(run(["sh", str(h)], "not json").returncode == 0, "bad JSON must fail open")
        ok &= need(run(["sh", str(h)], "").returncode == 0, "empty payload must fail open")
        return ok


def t_redact():
    seeds = ["sk-ABCDEFGHIJKLMNOPQRSTUV1234", "AKIAIOSFODNN7EXAMPLE", "Bearer abcdefghijklmnop1234567890",
             "-----BEGIN RSA PRIVATE KEY-----\nMIIEvQIBADANBgk\n-----END RSA PRIVATE KEY-----", "password=hunter2hunter2"]
    text = "ok line\n" + "\n".join(seeds) + "\nkeep this line"
    r = run(["python3", str(HOOKS / "redact_state.py")], text)
    out = r.stdout
    ok = need(r.returncode == 0, "redactor exits 0")
    for s in ("sk-ABCDEFGHIJKLMNOPQRSTUV1234", "AKIAIOSFODNN7EXAMPLE", "abcdefghijklmnop1234567890", "MIIEvQIBADANBgk", "hunter2hunter2"):
        ok &= need(s not in out, f"seed {s[:12]} leaked through redactor")
    ok &= need("keep this line" in out and "ok line" in out, "non-secret text must survive")
    ok &= need("[REDACTED" in out, "redaction markers present")
    return ok


def fake_gate(tmp: Path, code: int, store: Path):
    g = tmp / "fake-s1gate"
    g.write_text("#!/bin/sh\ncat > '%s'\necho 'rubric said: weak test coverage'\nexit %d\n" % (store, code))
    g.chmod(0o755)
    return g


def t_s1gate(redacted: bool):
    entry = HOOKS / ("s1gate-stage-gate-redacted.sh" if redacted else "s1gate-stage-gate.sh")
    secret = "sk-ABCDEFGHIJKLMNOPQRSTUV1234"
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        seen = tmp / "seen.txt"
        ok = True
        for code, want_rc, want_text, extra in ((1, 2, "s1gate BLOCKED", {"S1GATE_ENFORCE": "1"}),
                                                (0, 0, "", {}),
                                                (2, 0, "s1gate ESCALATE", {}),
                                                (1, 0, "WARN (enforcement disabled)", {"S1GATE_ENFORCE": "0"})):
            g = fake_gate(tmp, code, seen)
            env = dict(os.environ, S1GATE_BIN=str(g), **extra)
            if not redacted and "S1GATE_ENFORCE" not in extra:
                env.pop("S1GATE_ENFORCE", None)
            r = run(["bash", str(entry)], f"stage output with token {secret}\n", env)
            ok &= need(r.returncode == want_rc and want_text in r.stderr, f"gate exit {code}: want rc {want_rc} '{want_text}', got rc {r.returncode} {r.stderr[-160:]}")
        if redacted:
            ok &= need(seen.exists() and secret not in seen.read_text() and "[REDACTED" in seen.read_text(), "secret must be redacted before it reaches the gate")
        else:
            ok &= need(seen.exists() and secret in seen.read_text(), "plain stage gate forwards state unchanged")
        missing = run(["bash", str(entry)], "x", dict(os.environ, S1GATE_BIN=str(tmp / "nope")))
        ok &= need(missing.returncode == 0 and "NOT applied" in missing.stderr, "missing gate binary warns loudly and does not wedge")
        return ok


def t_memory_fleet():
    spec = importlib.util.spec_from_file_location("memory_fleet_under_test", HOOKS / "memory-fleet.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    good = {"status": "ok", "value": {"tenant_id": "rig", "operator_scope": "mike", "items": [{"id": "a", "content": "x" * 2000}]}}

    def caller_ok(op, payload, timeout=0):
        return good

    r = m.retrieve("claude", "turn", {"prompt": "hi"}, caller=caller_ok)
    ok = need(r["status"] == "ok" and r["reference_only"] is True, "ok retrieval is marked reference_only")
    ok &= need("never instructions or authorization" in r["reference_text"], "turn text labelled as reference data")
    ok &= need('"display_truncated": true' in r["reference_text"], "long bodies truncated for display")

    def caller_bad(op, payload, timeout=0):
        return {"status": "error", "reason": "memory_os_timeout"}

    r = m.retrieve("claude", "startup", {}, caller=caller_bad)
    ok &= need(r["status"] == "error" and "memory_os_timeout" in r["failures"][0], "backend failure surfaces as error, no silent fallback")
    calls = iter([good, {"status": "ok", "value": {"tenant_id": "other", "operator_scope": "mike"}}])
    r = m.retrieve("claude", "turn", {"prompt": "hi"}, caller=lambda *a, **k: next(calls))
    ok &= need(r["status"] == "error" and r["reason"] == "authenticated_scope_mismatch", "scope mismatch must be rejected")
    out = run(["python3", str(HOOKS / "memory-fleet.py"), "--runtime", "claude", "--event", "tool", "--format", "metadata"], "not json")
    ok &= need(out.returncode == 0 and "Memory OS error" in out.stdout, "invalid input surfaces an error line, exit 0")
    return ok


def main(argv):
    if len(argv) != 2:
        print("usage: hook_fires_misc.py <hook-file>", file=sys.stderr)
        return 2
    h = argv[1]
    table = {
        "done-gate.py": lambda: t_done_gate("done-gate.py"),
        "done-gate.sh": lambda: t_done_gate("done-gate.sh"),
        "jev-bash-gate.sh": t_jev_bash_gate,
        "redact_state.py": t_redact,
        "s1gate-stage-gate.sh": lambda: t_s1gate(False),
        "s1gate-stage-gate-redacted.sh": lambda: t_s1gate(True),
        "memory-fleet.py": t_memory_fleet,
    }
    if h not in table:
        print(f"no fixture for {h}", file=sys.stderr)
        return 2
    return 0 if table[h]() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
