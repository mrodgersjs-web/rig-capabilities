#!/usr/bin/env bash
# jex.sh v2 — JEV EXEC gate (captain rule 2026-09-20): run at the END of every test.
# PASS = code checks cleared AND every JEV question's rule-derived goodness >= 0.85.
# Polarity is read from the pack's own rules (q.noul >= X -> bad-framed; <= X -> good-framed),
# never guessed from names.
# Usage: jex.sh <item-id> <gate> <artifact-file> <done_test_text> <assertion-cmd...>
# JEX_RECEIPT=required for proof gates. Exit 0 = built; 1 = NOT built.
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
/Users/rig128gb/Developer/rig-capabilities/bin/rig-ultra route "$GATE" --state-file "$ART" --facts "$FACTS" --live --json > "$OUT" 2>"$OUT.err" || true
if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$OUT" 2>/dev/null; then
  echo "$ITEM jex: route produced no valid verdict JSON (fail closed): $(head -c 200 "$OUT.err")"; exit 1
fi
OUT="$OUT" ITEM="$ITEM" D="$D" python3 <<'PY'
import json, os, re, sys
out, item = os.environ["OUT"], os.environ["ITEM"]
d = json.load(open(out))
jev = d.get("jev") or {}
cleared = bool(d.get("cleared"))
verdict = (d.get("verdict") or "").upper()
if not cleared:
    print("%s jex: code checks not cleared route=%s -> %s" % (item, d.get("route"), out)); sys.exit(1)
# derive polarity from the pack rules
good = {}
pack = d.get("pack")
if pack:
    p = os.path.expanduser("~/Developer/rig-capabilities/capabilities/harnesses/s1gate/rubrics/%s.json" % pack)
    if os.path.exists(p):
        rb = json.load(open(p))
        for r in rb.get("rules", []):
            m = re.match(r"^(\w+)\.noul\s*(>=|<=)\s*([\d.]+)", r.get("when",""))
            if m:
                qname, op, thr = m.group(1), m.group(2), float(m.group(3))
                good[qname] = "bad" if op == ">=" else "good"
scores = {}
for q, a in jev.items():
    if isinstance(a, dict) and a.get("noul") is not None:
        v = float(a["noul"])
        pol = good.get(q, "good")   # unknown rule: default good-framed
        scores[q] = (1.0 - v) if pol == "bad" else v
    elif isinstance(a, dict) and a.get("score") is not None and a.get("probabilities"):
        probs = {int(k): float(x) for k, x in a["probabilities"].items()}
        mx = max(probs)
        scores[q] = probs[mx] / mx if mx else 0.0   # normalized expected grade
worst = min(scores.values()) if scores else None
worst_q = min(scores, key=scores.get) if scores else None
ok = worst is not None and worst >= 0.85
print("%s jex: cleared=%s verdict=%s goodness=%s worst=%.2f(%s) threshold=0.85 -> %s"
      % (item, cleared, verdict or "NONE", {k: round(v,2) for k,v in scores.items()},
         worst if worst is not None else -1, worst_q, out))
sys.exit(0 if ok else 1)
PY
