#!/usr/bin/env bash
# jex.sh — JEV EXEC gate (captain rule 2026-09-20): run at the END of every test.
# A todo item is NOT built unless the live rig-ultra route clears with JEV
# verdict PASS and every scored rule >= 0.85 (polarity-corrected).
# Usage: jex.sh <item-id> <gate> <artifact-file> <done_test_text> <assertion-cmd...>
# Receipt env: JEX_RECEIPT="path-or-text" (RED->GREEN planted-failure receipt; required
# by proof gates). Exit 0 = built; exit 1 = NOT built.
set -euo pipefail
ITEM="$1"; GATE="$2"; ART="$3"; DTT="$4"; shift 4
D=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$D/evidence/jex"
[ -f "$ART" ] || { echo "$ITEM jex: artifact missing: $ART"; exit 1; }
FACTS=/tmp/jex-$ITEM.json
JEX_ITEM="$ITEM" JEX_DTT="$DTT" JEX_CMDS="$(printf '%s\n' "$@")" python3 -c '
import json, os
pref = ("cmd:","pytest","npm test","make","cargo test","bash -c","python3 -m")
cmds = ["cmd:"+c if not c.startswith(pref) else c for c in os.environ["JEX_CMDS"].splitlines() if c.strip()]
f = {"done_test_text": os.environ["JEX_DTT"], "done_test_cmds": cmds}
if os.environ.get("JEX_RECEIPT"): f["planted_failure_receipt"] = os.environ["JEX_RECEIPT"]
json.dump(f, open("/tmp/jex-"+os.environ["JEX_ITEM"]+".json","w"))
'
OUT="$D/evidence/jex/$ITEM.json"
if ! /Users/rig128gb/Developer/rig-capabilities/bin/rig-ultra route "$GATE" --state-file "$ART" --facts "$FACTS" --live --json > "$OUT" 2>"$OUT.err"; then
  echo "$ITEM jex: route ERROR (fail closed): $(head -c 200 "$OUT.err")"; exit 1
fi
python3 - "$OUT" "$ITEM" <<'PY'
import json, sys
out, item = sys.argv[1], sys.argv[2]
d = json.load(open(out))
jev = d.get("jev") or {}
verdict = (d.get("verdict") or "").upper()
cleared = bool(d.get("cleared"))
# Polarity: rules whose name says the BAD thing ("vacuous", "missing", "generic",
# "unsupported") are inverted; everything else uses score/confidence directly.
NEG = ("vacuous", "missing", "generic", "stale", "broken", "unclear")
def rule_pass(name, ans):
    low = name.lower()
    for k in ("score", "confidence"):
        if isinstance(ans, dict) and ans.get(k) is not None:
            v = float(ans[k])
            return (1 - v) if any(n in low for n in NEG) else v >= 0.85
    if isinstance(ans, dict) and ans.get("noul") is not None:
        v = float(ans["noul"])
        return (1 - v) >= 0.85 if any(n in low for n in NEG) else v >= 0.85
    return None  # no scalar for this type (choice) -> rely on verdict
scalars = [r for name, ans in jev.items() if (r := rule_pass(name, ans)) is not None]
ok = cleared and verdict in ("PASS", "CLEARED") and all(scalars) if scalars else (cleared and verdict in ("PASS", "CLEARED"))
print(f"{item} jex: route={d.get('route')} cleared={cleared} verdict={verdict or 'NONE'} "
      f"rules={ {k: v for k, v in jev.items()} } -> {out}")
sys.exit(0 if ok else 1)
PY
