#!/usr/bin/env bash
# FINAL verification chain: full 671-row audit @0.85 -> GLM 5-sample sweep -> summary
cd "$(dirname "$0")"
./jev-audit.py audit-queue.json > audit-final.log 2>&1
./glm_verify.py > glm-final-sweep.log 2>&1
python3 - <<'PY'
import json
q=json.load(open("audit-queue.json"))
res=[]
import os
for x in q:
    f="audit/%s.json"%x["id"]
    if os.path.exists(f): res.append(json.load(open(f)))
green=[r for r in res if r.get("pass")]; red=[r for r in res if not r.get("pass")]
json.dump({"rows":len(q),"audited":len(res),"green":len(green),
           "red":[{"id":r["id"],"reasons":r["reasons"]} for r in red]},
          open("evidence/audit-final-summary.json","w"), indent=1)
print("final:", len(green),"green of",len(res),"audited")
PY
echo FINAL-DONE
