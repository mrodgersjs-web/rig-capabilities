#!/usr/bin/env python3
"""W07 digest probe: exactly the 19 named cells, their receipts, mission binding, live tree."""
import glob, json, sys
sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
from rig_capabilities.ultra_cell import validate_tree

W07 = ["question/persona-panel", "question/bank-quality", "question/coverage-meter",
       "question/cross-bank-dedup", "question/liveness-probe", "question/sufficiency-bar",
       "question/tag-and-route", "question/value-rank",
       "research/corpus-waves", "research/gap-mining", "research/landscape-wave", "research/source-grade",
       "forecast/aggregate", "forecast/base-rate-scout", "forecast/dry-check", "forecast/forecast-brief",
       "forecast/ledger-register", "forecast/premortem", "forecast/resolve-and-score"]
MID = "0f516f4a-0000-4000-8000-000000000601"

rs = {}
for f in glob.glob("/Users/rig128gb/Developer/ultraplan/data/receipt-*.json"):
    r = json.load(open(f))
    rs[r["cell"]] = r
green = [c for c in W07 if c in rs and rs[c]["results"][0]["ok"]]
print("W07 cells with green receipts:", len(green), "of", len(W07))
print("missing:", [c for c in W07 if c not in rs])
print("bound to mission 0601:", sum(1 for c in green if rs[c].get("mission_id") == MID), "of", len(green))
v = validate_tree("/Users/rig128gb/Developer/ultraplan")
print("tree valid", v["valid"], "of", v["total"], "orphans", v["orphans"], "cycles", v["cycles"])
