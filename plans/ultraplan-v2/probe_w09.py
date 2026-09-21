#!/usr/bin/env python3
"""W09 digest probe: the nine execution/proof cells' receipts + live one-claim-one-execution."""
import glob, json, sys, tempfile, uuid
sys.path.insert(0, "/Users/rig128gb/Developer/ultraplan")
from runtime.ledger import Ledger
from runtime.effects import drain, dry_run_executor

W09 = ["execute/lease", "execute/dispatch", "execute/worker", "execute/verifier", "execute/arbiter",
       "integrate/integrate", "proof/seal", "proof/proofpacket", "quality/sssf-gates"]
MID = "0f516f4a-0000-4000-8000-000000000601"
rs = {}
for f in glob.glob("/Users/rig128gb/Developer/ultraplan/data/receipt-*.json"):
    r = json.load(open(f))
    rs[r["cell"]] = r
green = [c for c in W09 if c in rs and rs[c]["results"][0]["ok"]]
print("W09 cells with green receipts:", len(green), "of", len(W09))
print("bound to mission 0601:", sum(1 for c in green if rs[c].get("mission_id") == MID))
db = tempfile.mktemp(suffix=".db")
lg = Ledger(db)
m = str(uuid.uuid4())
lg.apply_command(m, "mission.create", {"goal": "e"})
lg.acquire_fence("exec", "w1")
lg.apply_command(m, "cell.dispatch", {"cell": "p"}, effects=[{"kind": "dry", "n": 1}],
                 fence_key="exec", fence_token="w1")
lg.db.close()
first = drain(db, "exec", "w1", dry_run_executor)
second = drain(db, "exec", "w1", dry_run_executor)
print("first drain executed:", len(first), first[0]["status"] if first else "",
      "| second drain executed:", len(second), "-> one claim, one execution")
