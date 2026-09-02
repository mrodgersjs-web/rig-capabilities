"""immutable-surface-guard: the mutable allowlist is enforced state, not a comment.

A self-improving harness that can edit its own gate has not improved — it has
redefined improvement. This asset (hook `immutable-surface-guard.sh` + checker
`capabilities/hooks/fixtures/immutable-surface/check_surface.py`) enforces the
declaration: writes land inside `mutable_surface` or they exit 2, and the
checker's own machinery is immutable even under a widened allowlist.

These tests run the checker and the hook as shipped (subprocesses, cwd at the
repo root — the same way `done_tests` runs `cmd:` forms) and pin:
* every GREEN fixture exits 0 and every planted violation exits 2;
* each RED names ITS clause (SURFACE_MISSING vs SURFACE_EMPTY vs
  MANIFEST_MALFORMED vs WRITE_MALFORMED vs OUTSIDE_SURFACE vs PATH_ESCAPE vs
  SELF_TOUCH) — a guard that blurs them cannot tell a drift from an attack;
* missing files are refusals (exit 1), never verdicts;
* the hook fails CLOSED when configured-but-unjudgeable and stays silent when
  nothing was proposed;
* the checker writes nothing: fixture bytes are identical after every verdict.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIX = REPO_ROOT / "capabilities" / "hooks" / "fixtures" / "immutable-surface"
CHECKER = FIX / "check_surface.py"
HOOK = REPO_ROOT / "capabilities" / "hooks" / "immutable-surface-guard.sh"


def _check(manifest: Path, writes: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(manifest), str(writes)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)


def _hook(payload: str, env: dict | None = None) -> subprocess.CompletedProcess:
    import os
    e = os.environ.copy()
    e.update(env or {})
    return subprocess.run(["/bin/bash", str(HOOK)], input=payload, cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=30, env=e)


def _digest() -> str:
    h = hashlib.sha256()
    for f in sorted(FIX.rglob("*")):
        if f.is_file():
            h.update(f.name.encode())
            h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


class CheckerGreenTests(unittest.TestCase):
    def test_writes_inside_the_declared_surface_are_clean(self):
        p = _check(FIX / "surface_valid.yaml", FIX / "writes_in.jsonl")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stdout.count("ALLOW "), 4, p.stdout)

    def test_root_prefixed_paths_judge_identically(self):
        p = _check(FIX / "surface_valid.yaml", FIX / "writes_root.jsonl")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(p.stdout.count("ALLOW "), 3, p.stdout)

    def test_no_writes_proposed_is_clean_not_a_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "writes_empty.jsonl"
            empty.write_text("\n\n", encoding="utf-8")
            p = _check(FIX / "surface_valid.yaml", empty)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


class CheckerRedTests(unittest.TestCase):
    def _assert_red(self, manifest: Path, writes: Path, tag: str) -> str:
        p = _check(manifest, writes)
        self.assertEqual(p.returncode, 2,
                         f"{tag}: expected exit 2, got {p.returncode}\n{p.stdout}")
        self.assertIn(f"VIOLATION {tag}:", p.stdout, p.stdout)
        return p.stdout

    def test_path_outside_every_glob_is_outside_surface(self):
        self._assert_red(FIX / "surface_valid.yaml", FIX / "writes_outside.jsonl",
                         "OUTSIDE_SURFACE")

    def test_empty_allowlist_denies_instead_of_permitting(self):
        self._assert_red(FIX / "surface_empty.yaml", FIX / "writes_in.jsonl",
                         "SURFACE_EMPTY")

    def test_missing_allowlist_key_is_denial_not_licence(self):
        self._assert_red(FIX / "surface_nokey.yaml", FIX / "writes_in.jsonl",
                         "SURFACE_MISSING")

    def test_scalar_surface_is_malformed_not_coerced(self):
        self._assert_red(FIX / "surface_malformed.yaml", FIX / "writes_in.jsonl",
                         "MANIFEST_MALFORMED")

    def test_gate_edit_wins_over_a_widened_allowlist(self):
        """The plant-failure: the improver widens its surface over its own gate.
        SELF_TOUCH must name itself — OUTSIDE_SURFACE would blur attack drift."""
        out = self._assert_red(FIX / "surface_widened.yaml",
                               FIX / "writes_gate_touch.jsonl", "SELF_TOUCH")
        self.assertNotIn("VIOLATION OUTSIDE_SURFACE", out,
                         "only the SELF_TOUCH line may be violated here")
        self.assertIn("ALLOW memory/lesson_044.md", out,
                      "the memory write in the same run stays allowed")

    def test_traversal_side_door_is_path_escape(self):
        out = self._assert_red(FIX / "surface_valid.yaml", FIX / "writes_escape.jsonl",
                               "PATH_ESCAPE")
        self.assertIn("ALLOW runs/2026-09/../2026-08/notes.jsonl", out,
                      "a benign traversal that lands inside must not be blocked")

    def test_write_rows_without_a_path_are_malformed(self):
        self._assert_red(FIX / "surface_valid.yaml", FIX / "writes_malformed.jsonl",
                         "WRITE_MALFORMED")

    def test_absolute_path_outside_the_root_is_outside_surface(self):
        with tempfile.TemporaryDirectory() as td:
            w = Path(td) / "writes_abs.jsonl"
            w.write_text('{"path": "/etc/passwd"}\n', encoding="utf-8")
            p = _check(FIX / "surface_valid.yaml", w)
            self.assertEqual(p.returncode, 2)
            self.assertIn("OUTSIDE_SURFACE", p.stdout)


class CheckerRefusalTests(unittest.TestCase):
    def test_missing_manifest_is_a_refusal_not_a_verdict(self):
        p = _check(FIX / "no_such_surface.yaml", FIX / "writes_in.jsonl")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_missing_writes_file_is_a_refusal(self):
        p = _check(FIX / "surface_valid.yaml", FIX / "no_such_writes.jsonl")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_usage_error_is_a_refusal(self):
        p = subprocess.run([sys.executable, str(CHECKER)], cwd=REPO_ROOT,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_checker_writes_nothing(self):
        before = _digest()
        _check(FIX / "surface_valid.yaml", FIX / "writes_in.jsonl")
        _check(FIX / "surface_widened.yaml", FIX / "writes_gate_touch.jsonl")
        self.assertEqual(_digest(), before, "the checker mutated a fixture")


class HookTests(unittest.TestCase):
    def test_hook_allows_an_in_surface_write(self):
        p = _hook('{"tool_input":{"file_path":"harness/memory/lesson_001.md"}}',
                  {"SURFACE_MANIFEST": str(FIX / "surface_valid.yaml")})
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_hook_blocks_a_gate_edit_with_exit_2(self):
        p = _hook('{"tool_input":{"file_path":"harness/machine/check_gate.py"}}',
                  {"SURFACE_MANIFEST": str(FIX / "surface_valid.yaml")})
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("SELF_TOUCH", p.stderr, "the denial must name its clause")

    def test_hook_blocks_an_out_of_surface_write(self):
        p = _hook('{"tool_input":{"file_path":"src/policy/patcher.py"}}',
                  {"SURFACE_MANIFEST": str(FIX / "surface_valid.yaml")})
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("OUTSIDE_SURFACE", p.stderr)

    def test_payload_without_a_path_is_not_a_verdict(self):
        env = {"SURFACE_MANIFEST": str(FIX / "surface_valid.yaml")}
        for payload in ('', '{"tool_input":{"command":"echo hi"}}', 'not json'):
            p = _hook(payload, env)
            self.assertEqual(p.returncode, 0, f"{payload!r}: {p.stdout}{p.stderr}")

    def test_guard_inactive_without_a_manifest(self):
        p = _hook('{"tool_input":{"file_path":"any/path.py"}}',
                  {"SURFACE_MANIFEST": ""})
        self.assertEqual(p.returncode, 0)

    def test_configured_but_unjudgeable_fails_closed(self):
        p = _hook('{"tool_input":{"file_path":"harness/memory/x.md"}}',
                  {"SURFACE_MANIFEST": "/nonexistent/surface.yaml"})
        self.assertEqual(p.returncode, 2, "a configured guard MUST fail closed")
        self.assertIn("BLOCKED", p.stderr)

    def test_missing_checker_fails_closed_with_a_named_reason(self):
        p = _hook('{"tool_input":{"file_path":"harness/memory/x.md"}}',
                  {"SURFACE_MANIFEST": str(FIX / "surface_valid.yaml"),
                   "SURFACE_CHECKER": "/nonexistent/check_surface.py"})
        self.assertEqual(p.returncode, 2)
        self.assertIn("checker missing", p.stderr)


if __name__ == "__main__":
    unittest.main()
