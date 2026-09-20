#!/usr/bin/env bash
# jex.sh v3 — JEV EXEC gate (captain rules 2026-09-20).
# 1. every done-test assertion is EXECUTED by the gate itself (rig-ultra now runs them)
# 2. CERTIFIED rules decide on their measured threshold (calibration.rules in the pack)
# 3. UNCERTIFIED rules: goodness >= 0.85 required (captain interim bar), else annotate-only fail
#    goodness polarity comes from the rule's own direction (>= is bad-framed, <= good-framed)
# PASS = route cleared AND no enforced escalation AND every judged signal passes its bar.
# Usage: jex.sh <item-id> <gate> <artifact-file> <atomic-claim> <assertion-cmd...>
# JEX_RECEIPT=... required by proof gates. Exit 0 = built; 1 = NOT built.
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
OUT="$OUT" ITEM="$ITEM" python3 <<'PY'
import json, os, re, sys
out, item = os.environ["OUT"], os.environ["ITEM"]
d = json.load(open(out))
jev = d.get("jev") or {}
cleared = bool(d.get("cleared"))
verdict = (d.get("verdict") or "").upper()
pack = d.get("pack")
entries = {}; polarity = {}
if pack:
    p = os.path.expanduser("~/Developer/rig-capabilities/capabilities/harnesses/s1gate/rubrics/%s.json" % pack)
    if os.path.exists(p):
        rb = json.load(open(p))
        entries = (rb.get("calibration") or {}).get("rules") or {}
        polarity = {}
        for r in rb.get("rules", []):
            m = re.match(r"^(\w+\.\w+)\s*(>=|<=)", r.get("when", ""))
            if m:
                polarity[m.group(1)] = ("bad" if m.group(2) == ">=" else "good")
bad = []
detail = {}
for q, a in jev.items():
    vals = [x for x in (a.get("noul"), a.get("score"), a.get("confidence")) if x is not None]
    if not vals:
        continue
    v = vals[0]
    if v is None:
        continue
    pol = polarity.get(q, "good")
    goodness = (1.0 - float(v)) if pol == "bad" else float(v)
    e = entries.get("%s.%s" % (q, "noul" if "noul" in a else ("score" if "score" in a else "confidence")))
    if e:
        thr = float(e["threshold"])
        ok = (float(v) > thr) if pol == "good" else (float(v) < thr)
        detail[q] = "certified thr=%.3f val=%.2f %s" % (thr, float(v), "OK" if ok else "VIOLATED")
    else:
        ok = goodness >= 0.85
        detail[q] = "uncertified goodness=%.2f %s(0.85)" % (goodness, "OK " if ok else "BELOW")
    if not ok:
        bad.append(q)
ok = cleared and not bad and verdict not in ("BLOCK",)
print("%s jex: cleared=%s verdict=%s %s failing=%s -> %s"
      % (item, cleared, verdict or "NONE", "; ".join("%s: %s" % kv for kv in detail.items()) or "no jev answers",
         bad or "none", out))
sys.exit(0 if ok else 1)
PY
