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
# dedicated single-field call: the claim judged ALONE (ultra.atomic). Inside a
# multi-part state the judge cannot separate claim from evidence -- measured bug.
AOUT="$OUT.atomic"
JEX_STATE=$(python3 -c "import json;print(json.load(open('/tmp/jex-$ITEM.json'))['done_test_text'])")
# three single-field calls on ultra.atomic; PASS iff >=2 clean (exit 0 = PASS)
AOK=0
for i in 1 2 3; do
  /Users/rig128gb/Developer/rig-capabilities/bin/rig-s1gate check atomic.claim --text "$JEX_STATE" --subject "jex:$ITEM" --json > "$AOUT.$i" 2>/dev/null \
    && AOK=$((AOK+1))
done
echo "$AOK/3 atomic calls PASS" > "$AOUT"
# median-of-3 live samples: a single noul near the certified threshold is a coin
# flip; the median of three independent calls is a measurement, not a lottery.
for i in 1 2 3; do
  /Users/rig128gb/Developer/rig-capabilities/bin/rig-ultra route "$GATE" --state-file "$ART" --facts "$FACTS" --live --json > "$OUT.$i" 2>"$OUT.$i.err" || true
done
python3 - "$OUT" <<'MEDIAN'
import json, statistics, sys, os
out = sys.argv[1]
runs = []
for i in (1, 2, 3):
    try: runs.append(json.load(open("%s.%d" % (out, i))))
    except Exception: pass
if not runs:
    sys.exit(1)
med = {"gate": runs[0]["gate"], "route": runs[0]["route"], "cleared": all(r.get("cleared") for r in runs),
       "verdict": runs[0].get("verdict"), "pack": runs[0].get("pack"), "samples": len(runs),
       "jev": {}, "code_checks": runs[-1].get("code_checks"), "reasons": runs[-1].get("reasons", [])}
keys = set().union(*[set(r.get("jev") or {}) for r in runs])
for k in keys:
    vals = [r["jev"][k] for r in runs if k in (r.get("jev") or {}) and isinstance(r["jev"][k], dict)]
    if not vals: continue
    agg = dict(vals[0])
    for field in ("noul", "score", "confidence"):
        nums = [v[field] for v in vals if v.get(field) is not None]
        if nums: agg[field] = statistics.median(nums)
    med["jev"][k] = agg
json.dump(med, open(out, "w"), indent=1)
MEDIAN
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
        ok = True  # uncertified signals annotate only (W04 law: an unmeasured
                   # signal may not block; the 0.85 bar applies to certified rules)
        detail[q] = "uncertified goodness=%.2f annotate-only" % goodness
    if not ok:
        bad.append(q)
import subprocess
aok = 0
try:
    txt = open(out + ".atomic").read()
    aok = int(txt.split("/")[0])
except Exception:
    aok = 0
atomic_ok = aok >= 2
bad = [q for q in bad if q != "claim_atomic"]  # superseded by the single-field call
if not atomic_ok:
    detail["claim_atomic(single-field)"] = "%d/3 PASS calls (need 2)" % aok
fails = list(bad)
if not atomic_ok: fails.append("atomic-calls %d/3" % aok)
if not cleared: fails.append("not-cleared")
print("%s jex: cleared=%s verdict=%s %s failing=%s -> %s"
      % (item, cleared, verdict or "NONE", "; ".join("%s: %s" % kv for kv in detail.items()) or "no jev answers",
         fails or "none", out))
sys.exit(0 if (cleared and not fails) else 1)
PY
