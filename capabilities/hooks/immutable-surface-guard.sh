#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when:
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_valid.yaml $D/writes_in.jsonl; test $? -eq 0
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_valid.yaml $D/writes_root.jsonl; test $? -eq 0
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_valid.yaml $D/writes_outside.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_empty.yaml $D/writes_in.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_nokey.yaml $D/writes_in.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_malformed.yaml $D/writes_in.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_widened.yaml $D/writes_gate_touch.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_valid.yaml $D/writes_escape.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; python3 $D/check_surface.py $D/surface_valid.yaml $D/writes_malformed.jsonl; rc=$?; test $rc -eq 2
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; printf '{"tool_input":{"file_path":"harness/memory/lesson_001.md"}}' | SURFACE_MANIFEST=$D/surface_valid.yaml /bin/bash capabilities/hooks/immutable-surface-guard.sh; test $? -eq 0
#   - cmd:D=capabilities/hooks/fixtures/immutable-surface; printf '{"tool_input":{"file_path":"harness/machine/check_gate.py"}}' | SURFACE_MANIFEST=$D/surface_valid.yaml /bin/bash capabilities/hooks/immutable-surface-guard.sh; rc=$?; test $rc -eq 2
#   - file:capabilities/hooks/fixtures/immutable-surface/check_surface.py
# great_example: examples/great/agent-engineering/immutable-surface-guard.md
# quality_floor: 0.6
# immutable-surface-guard — pre-write guard for self-improving harnesses.
# Canonical source: rig-capabilities repo.
#
# A self-improving harness declares the exact surface an optimizer may mutate
# (mutable_surface: its memory/config files) and the machinery fixed by
# declaration (immutable: its own checker/gate/patcher/validator) in a YAML
# manifest. Any score delta is attributable to the mutable layer only if
# nothing outside it moved. This guard denies any proposed write outside the
# declared allowlist, and denies writes to the declared-immutable machinery
# even when a widened allowlist would cover them.
#
# Contract: PreToolUse-style JSON payload on stdin (house convention:
# guard-secret-write.sh, working-memory-commit-gate.sh). The proposed write
# path is taken from tool_input.{file_path,path,target_file,notebook_path}.
# The surface manifest lives at $SURFACE_MANIFEST; the checker is
# $SURFACE_CHECKER, defaulting to the canonical
# fixtures/immutable-surface/check_surface.py next to this hook — when
# installing this hook alone, point one of the two env vars at a checkout or
# the guard fails CLOSED with a named reason.
#
# Exit codes: 0 every proposed write is inside the declared mutable surface;
# 2 denied — a path outside the allowlist (OUTSIDE_SURFACE), a traversal that
# only matches before normalization (PATH_ESCAPE), a write onto immutable
# machinery (SELF_TOUCH), an empty/missing/malformed allowlist
# (SURFACE_EMPTY/SURFACE_MISSING/MANIFEST_MALFORMED), or a configured guard
# that cannot be judged (fail closed). Empty stdin or a payload carrying no
# file path exits 0: nothing was proposed. The checker itself refuses to
# judge (exit 1) on missing files; at RUNTIME that refusal becomes denial.
set -uo pipefail
payload=$(cat 2>/dev/null || true)
[ -n "$payload" ] || exit 0
[ -n "${SURFACE_MANIFEST:-}" ] || exit 0   # no surface declared: guard inactive

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CHECKER="${SURFACE_CHECKER:-$HERE/fixtures/immutable-surface/check_surface.py}"
if [ ! -f "$CHECKER" ]; then
  echo "rig-guard: BLOCKED — surface checker missing at $CHECKER; a configured guard never runs unchecked" >&2
  exit 2
fi

tmp=$(mktemp) || { echo "rig-guard: BLOCKED — cannot stage the proposed write path" >&2; exit 2; }
trap 'rm -f "$tmp"' EXIT

printf '%s' "$payload" | /usr/bin/python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
ti = d.get("tool_input")
if not isinstance(ti, dict):
    ti = d.get("input") if isinstance(d.get("input"), dict) else {}
path = None
for k in ("file_path", "path", "target_file", "notebook_path"):
    v = ti.get(k)
    if isinstance(v, str) and v.strip():
        path = v.strip()
        break
if path is None:
    sys.exit(1)
sys.stdout.write(json.dumps({"path": path}) + "\n")
' > "$tmp" 2>/dev/null || exit 0   # no writable path in the payload: nothing to judge
[ -s "$tmp" ] || exit 0

out=$(/usr/bin/python3 "$CHECKER" "$SURFACE_MANIFEST" "$tmp" 2>&1); rc=$?
case "$rc" in
  0) exit 0 ;;
  2) printf '%s\n' "$out" >&2
     echo "rig-guard: BLOCKED — proposed write violates the declared mutable surface (immutable-surface-guard)" >&2
     exit 2 ;;
  *) printf '%s\n' "$out" >&2
     echo "rig-guard: BLOCKED — SURFACE_MANIFEST is configured but cannot be judged; failing closed" >&2
     exit 2 ;;
esac
