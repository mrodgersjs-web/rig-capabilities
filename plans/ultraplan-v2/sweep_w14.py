#!/usr/bin/env python3
"""W14 re-sweep at tree=100: plant full-cycles (categorized), OpenSpec formation,
manifest traceability against the resolved audit queue."""
import json, sys, glob, re
sys.path.insert(0, "/Users/rig128gb/Developer/rig-capabilities")
sys.path.insert(0, "/Users/rig128gb/Developer/ultraplan")
from rig_capabilities.ultra_cell import discover_cells, plant_failure
import yaml

ROOT = "/Users/rig128gb/Developer/ultraplan"
HERE = "/Users/rig128gb/Developer/rig-capabilities/plans/ultraplan-v2"

disc = discover_cells(ROOT)
cells = [str(c) for c in (disc[0] if isinstance(disc, tuple) else disc)]
ok = skip = 0
skips = []
for c in cells:
    r = plant_failure(c)
    if r.get("ok"):
        ok += 1
    else:
        reason = r.get("reason") or "not-green-or-not-red"
        if "is not a file" in reason:
            skip += 1  # designed: parent/studio cell with no routes.yaml slot
            skips.append((c.split("/")[-1], "no-slot"))
        else:
            skips.append((c.split("/")[-1], reason[:70]))
plant = {"cells_total": len(cells), "full_cycle": ok, "designed_skip_no_slot": skip,
         "true_fails": [s for s in skips if s[1] != "no-slot"], "evidence": "green->planted-red->byte-restored"}

feats = sorted(glob.glob(ROOT + "/features/**/*.feature", recursive=True))
malformed = [f for f in feats if "Feature:" not in open(f).read() or not re.search(r"^\s*Scenario", open(f).read(), re.M)]
openspec = {"files": len(feats), "malformed": len(malformed), "malformed_list": malformed[:5]}

d = yaml.safe_load(open(HERE + "/BUILD-MANIFEST.yaml"))
non_inv = {it["id"] for it in d["items"] if it["status"] != "inventoried"}
queue = {row["id"] for row in json.load(open(HERE + "/audit-queue.json"))}
unreproducible = json.load(open(HERE + "/audit-queue.json"))
no_repro = {row["id"] for row in unreproducible if not row.get("repro_cmd")}
trace = {"non_inventoried_rows": len(non_inv),
         "rows_in_queue": len(non_inv & queue),
         "rows_executable": len(non_inv & queue) - len(no_repro),
         "rows_without_executable_repro": sorted(non_inv - queue | no_repro)[:10]}

json.dump(plant, open(HERE + "/evidence/w14-plant-sweep.json", "w"), indent=1)
json.dump(openspec, open(HERE + "/evidence/w14-openspec.json", "w"), indent=1)
json.dump(trace, open(HERE + "/evidence/w14-traceability.json", "w"), indent=1)
print("plant full-cycle", ok, "designed-skip", skip, "true-fails", len(plant["true_fails"]), "of", len(cells))
print("openspec", len(feats), "files,", len(malformed), "malformed")
print("trace", trace["rows_executable"], "of", trace["non_inventoried_rows"],
      "rows executable;", trace["rows_without_executable_repro"])
