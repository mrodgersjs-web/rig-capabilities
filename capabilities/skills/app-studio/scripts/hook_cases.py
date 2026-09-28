#!/usr/bin/env python3
"""Fire an App Studio hook against its fixture cases. Exit 0 only if every case behaved.

Cases live at capabilities/hooks/fixtures/<hook-stem>/cases.json: a list of
  {"name", "payload": {...tool call payload...}, "files": {"rel/path": "body"},
   "git_init": bool, "env": {...}, "expect_rc": 0|2, "expect_text": "..."}
Each case runs in a fresh temp directory used as the payload cwd, so a case can
build an App Studio project (.app-studio/), a package.json, a build lock, or a git
repo with untracked env files. A hook that allows what it should block, or blocks
what it should allow, fails its case.

Usage:
  hook_cases.py <hook-file-name> [--hook-file PATH]
    --hook-file  run the cases against another copy of the hook (planted-failure proofs)
Exit 0 all cases pass, 1 a case failed, 2 usage or missing fixtures. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HOOKS = REPO / "capabilities" / "hooks"


def run_case(hook: Path, case: dict) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        if case.get("git_init"):
            subprocess.run(["git", "init", "-q", str(root)], capture_output=True, check=False)
        for rel, body in (case.get("files") or {}).items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        payload = dict(case["payload"])
        payload.setdefault("cwd", str(root))
        env = os.environ.copy()
        env.update(case.get("env") or {})
        r = subprocess.run(["sh", str(hook)], input=json.dumps(payload), text=True,
                           capture_output=True, cwd=str(root), timeout=20, env=env)
        blob = (r.stdout or "") + (r.stderr or "")
        ok = r.returncode == case["expect_rc"] and (not case.get("expect_text") or case["expect_text"] in blob)
        return ok, f"rc={r.returncode} want={case['expect_rc']} out={blob.strip()[-240:]!r}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("hook")
    ap.add_argument("--hook-file")
    a = ap.parse_args(argv)
    hook = Path(a.hook_file) if a.hook_file else HOOKS / a.hook
    stem = a.hook.rsplit(".", 1)[0]
    cases_file = HOOKS / "fixtures" / stem / "cases.json"
    if not hook.is_file() or not cases_file.is_file():
        print(f"missing hook or fixtures: {hook} / {cases_file}", file=sys.stderr)
        return 2
    cases = json.loads(cases_file.read_text())
    failed = 0
    for c in cases:
        ok, detail = run_case(hook, c)
        print(f"{'PASS' if ok else 'FAIL'} {c['name']}: {detail}")
        failed += 0 if ok else 1
    print(f"{a.hook}: {len(cases) - failed}/{len(cases)} case(s) behaved")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
