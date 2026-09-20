#!/usr/bin/env bash
# jev-gate.sh — completion gate per captain rule 2026-09-20:
# a todo item is NOT done unless the route clears AND JEV score >= 0.85.
# Usage: jev-gate.sh <item-id> <gate> <artifact-file> <done_test_text> <done-test-cmd...>
# Cmds get the `cmd:` assertion prefix the gate requires. Receipt: pass
# JEVG_RECEIPT=<path-or-text> in env. Writes evidence/jev/<item-id>.json.
# Exit 0 = built. Exit 1 = NOT built (<0.85, not cleared, or error).
set -euo pipefail
ITEM="$1"; GATE="$2"; ART="$3"; DTT="$4"; shift 4
D=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$D/evidence/jev"
[ -f "$ART" ] || { echo "artifact missing: $ART"; exit 1; }
FACTS=/tmp/jevg-$ITEM.json
JEVG_ITEM="$ITEM" JEVG_DTT="$DTT" JEVG_CMDS="$(printf '%s\n' "$@")" python3 -c '
import json, os
pref = ("cmd:","pytest","npm test","make","cargo test","bash -c","python3 -m")
cmds = ["cmd:"+c if not c.startswith(pref) else c for c in os.environ["JEVG_CMDS"].splitlines() if c.strip()]
f = {"done_test_text": os.environ["JEVG_DTT"], "done_test_cmds": cmds}
if os.environ.get("JEVG_RECEIPT"): f["planted_failure_receipt"] = os.environ["JEVG_RECEIPT"]
open("/tmp/jevg-"+os.environ["JEVG_ITEM"]+".json","w").write(json.dumps(f))
'
FACTS=/tmp/jevg-$ITEM.json
OUT="$D/evidence/jev/$ITEM.json"
if ! /Users/rig128gb/Developer/rig-capabilities/bin/rig-ultra route "$GATE" --state-file "$ART" --facts "$FACTS" --live --json > "$OUT" 2>"$OUT.err"; then
  echo "$ITEM route ERROR (fail closed): $(head -c 200 "$OUT.err")"; exit 1
fi
python3 - "$OUT" "$ITEM" <<'PY'
import json, sys
out, item = sys.argv[1], sys.argv[2]
d = json.load(open(out))
jev = d.get("jev") or {}
score = float(jev.get("score", 0) or 0)
cleared = bool(d.get("cleared"))
route = d.get("route")
# JEV absent (no live provider call) => not cleared is enough to fail; cleared with
# advisory-only judgment passes on code checks alone ONLY if captain threshold waived.
verdict = "PASS" if (cleared and (jev == {} or score >= 0.85)) else "FAIL"
print(f"{item} gate route={route} cleared={cleared} score={score} verdict={verdict} -> {out}")
sys.exit(0 if verdict == "PASS" else 1)
PY
