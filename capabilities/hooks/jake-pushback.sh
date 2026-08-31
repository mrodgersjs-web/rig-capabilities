#!/bin/bash
# outcome: agent-engineering:
# done_when: file:capabilities/hooks/jake-pushback.sh || hook is registered and fires on its trigger fixture
# great_example: examples/great/agent-engineering/jake-pushback.sh.md
# quality_floor: 0.6
# jake-pushback.sh — PreToolUse hook: Jake's in-session enforcement.
#
# Three enforcement layers, fastest first:
#   1. SECRET FILE GUARD (Juno/council): hard BLOCK on edits to secret-bearing
#      paths (.env, .pem, credentials.json, .ssh/, .aws/, keys) — one write,
#      one approval. Irreversible-class edits.
#   2. TESTLESS STREAK GATE (8-member council convergence): per-session counter;
#      warn at 4 files/0 tests, BLOCK at 7 until a test runs.
#   3. HARNESS STATE: reads ~/.rig/state/jake-harness.json (5-min cron cycle)
#      and injects active blocking interventions as warnings.
#
# Exit 0 = allow, exit 1 = block (message on stderr).

set -uo pipefail

payload="$(cat)"

tool_name="$(printf '%s' "$payload" | python3 -c "
import json,sys
try: print(json.load(sys.stdin).get('tool_name',''))
except: print('')
" 2>/dev/null || echo '')"
[ -z "$tool_name" ] && exit 0

# Only file-mutating tools are gated
case "$tool_name" in
  Write|Edit|MultiEdit|NotebookEdit) ;;
  *) exit 0 ;;
esac

target_path="$(printf '%s' "$payload" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    ti=d.get('tool_input',{}) or {}
    print(ti.get('file_path') or ti.get('path') or '')
except: print('')
" 2>/dev/null || echo '')"

session_id="$(printf '%s' "$payload" | python3 -c "
import json,sys
try: print(json.load(sys.stdin).get('session_id','default')[:16])
except: print('default')
" 2>/dev/null || echo 'default')"

# ---------- Layer 1: SECRET FILE GUARD (hard block) ----------
if [ -n "$target_path" ] && printf '%s' "$target_path" | grep -qiE '(\.env($|\.)|\.pem$|_rsa$|credentials\.json|secrets?/|\.aws/|\.ssh/|id_ed25519|\.keystore|\.p12$|\.key$|token\.json)'; then
    # Approval token: Mike approves ONE write, optionally reason-coded:
    #   touch /tmp/jake-secret-approve-<md5>.wrong_rule   (detector was wrong)
    #   touch /tmp/jake-secret-approve-<md5>.expedient    (right rule, in a hurry)
    #   touch /tmp/jake-secret-approve-<md5>              (unknown)
    # The reason turns overrides into a labeled correction dataset.
    hash="$(printf '%s' "$target_path" | md5 -q)"
    approval="/tmp/jake-secret-approve-$hash"
    logdir="$HOME/.rig/state"
    mkdir -p "$logdir"
    for suffix in wrong_rule expedient unknown; do
        if [ -f "$approval.$suffix" ]; then
            rm -f "$approval.$suffix"
            printf '{"ts":"%s","target_path":"%s","session_id":"%s","reason":"%s","detector_id":"secret_file_guard","outcome":"override"}\n' \
                "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$target_path" "$session_id" "$suffix" >> "$logdir/jake-overrides.jsonl"
            echo "JAKE: secret-file write approved [$suffix] (one-time token consumed): $target_path" >&2
            exit 0
        fi
    done
    if [ -f "$approval" ]; then
        rm -f "$approval"
        printf '{"ts":"%s","target_path":"%s","session_id":"%s","reason":"unknown","detector_id":"secret_file_guard","outcome":"override"}\n' \
            "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$target_path" "$session_id" >> "$logdir/jake-overrides.jsonl"
        echo "JAKE: secret-file write approved [unknown] (one-time token consumed): $target_path" >&2
        exit 0
    fi
    # Log the block itself (no approval) — blocks are data too
    printf '{"ts":"%s","target_path":"%s","session_id":"%s","reason":null,"detector_id":"secret_file_guard","outcome":"blocked"}\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$target_path" "$session_id" >> "$logdir/jake-overrides.jsonl"
    cat >&2 <<EOF
🛑 JAKE HARD BLOCK — secret_file_guard (Juno/security council)

Target: $target_path

Agent-authored edits to secret-bearing files are irreversible at commit.
To approve this ONE write (reason-coded — feeds Jake's detector learning):
  touch $approval.wrong_rule   # the detector was wrong
  touch $approval.expedient    # rule was right, you're in a hurry
  touch $approval              # unlabeled

Then retry. This is the one pattern class where advisory is insufficient.
EOF
    exit 1
fi

# ---------- Layer 2: TESTLESS STREAK GATE ----------
COUNTER_DIR="/tmp/jake-hook-counters"
mkdir -p "$COUNTER_DIR"
COUNTER="$COUNTER_DIR/$session_id.json"
export JAKE_TARGET_PATH="$target_path"

python3 - "$COUNTER" "$tool_name" <<'PYEOF'
import json, sys, os

counter_path, tool_name = sys.argv[1], sys.argv[2]
state = {"files": [], "tests": 0}
if os.path.exists(counter_path):
    try:
        state = json.load(open(counter_path))
    except Exception:
        pass

if tool_name in ("Bash",):
    state["tests"] = state.get("tests", 0) + 1  # any bash may be a test; conservative reset
    state["files"] = []
else:
    fp = os.environ.get("JAKE_TARGET_PATH", "")
    files = state.get("files", [])
    if fp and fp not in files:
        files.append(fp)
    state["files"] = files

json.dump(state, open(counter_path, "w"))

n_files = len(state.get("files", []))
n_tests = state.get("tests", 0)

if n_tests == 0 and n_files >= 7:
    print(f"🛑 JAKE BLOCK — testless_multifile (8-member council convergence)\n"
          f"This session has touched {n_files} files with ZERO test runs.\n"
          f"Measured fleet data: this exact shape (4-10 files, 0 tests) shipped broken 9 times in one project.\n"
          f"Run the project test suite (any Bash test command clears this), then continue.", file=sys.stderr)
    sys.exit(1)
elif n_tests == 0 and n_files >= 4:
    print(f"⚠️ JAKE WARN — {n_files} files touched, 0 tests. Block at 7. Verify before the streak compounds.", file=sys.stderr)

sys.exit(0)
PYEOF
streak_exit=$?
[ $streak_exit -ne 0 ] && exit 1

# ---------- Layer 3: HARNESS STATE (cron-computed blocking interventions) ----------
HARNESS_JSON="$HOME/.rig/state/jake-harness.json"
if [ -f "$HARNESS_JSON" ]; then
    python3 - "$HARNESS_JSON" <<'PYEOF'
import json, sys
try:
    h = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
blocking = [i for i in h.get("interventions", []) if i.get("severity") == "blocking"]
if blocking:
    ids = ", ".join(i["id"] for i in blocking[:4])
    print(f"⚠️ JAKE HARNESS — {len(blocking)} blocking interventions active: {ids}. "
          f"See ~/.rig/state/jake-harness.json or ask memory_get_guidance.", file=sys.stderr)
sys.exit(0)  # advisory only — hook never hard-blocks on fleet-level state
PYEOF
fi

exit 0
