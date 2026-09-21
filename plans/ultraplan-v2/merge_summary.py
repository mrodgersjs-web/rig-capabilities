#!/usr/bin/env python3
"""Merge the final pass (656 green rows, judged on current queue+disk) with the
targeted re-audit of the 24 probe-enrichment reds (judged after the fix) into the
authoritative audit-final-summary.json. Honest composition: every row judged by
its CURRENT repro against CURRENT disk; no row inherits a verdict from stale state."""
import json, re, datetime

HERE = "/Users/rig128gb/Developer/rig-capabilities/plans/ultraplan-v2"
q = {row["id"] for row in json.load(open(HERE + "/audit-queue.json"))}

judged = {}
for log in ("/tmp/audit-clean2.log", "/tmp/reaudit-final24.log"):
    for line in open(log):
        m = re.match(r"(PASS|RED)\s+(\S+)", line)
        if m:
            judged.setdefault(m.group(2), []).append(m.group(1))

# precedence: the re-audit (later log) overrides the first pass
final = {iid: v[-1] for iid, v in judged.items()}
missing = sorted(q - set(final))
reds = sorted(i for i, v in final.items() if v == "RED")
summary = {
    "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
    "queue_rows": len(q), "pass": sum(1 for v in final.values() if v == "PASS"),
    "red": len(reds), "red_ids": reds, "never_judged": missing,
    "bar": "evidence_median >= 0.85, atomic >= 2/3 (captain 2026-09-20)",
    "composition": {
        "full pass": "/tmp/audit-clean2.log (live-probe queue, judged against final disk)",
        "targeted re-audit": "/tmp/reaudit-final24.log (24 probe-output-enrichment rows, overrides pass rows)",
    },
    "note": "every row's verdict comes from its current repro command executed against current disk state",
}
print("pass", summary["pass"], "red", summary["red"], "never_judged", len(missing))
if missing or summary["red"]:
    print("REFUSING to write authoritative summary until green+complete")
    print("missing sample:", missing[:5], "reds:", reds[:5])
    raise SystemExit(1)
json.dump(summary, open(HERE + "/evidence/audit-final-summary.json", "w"), indent=1)
print("authoritative summary written")
