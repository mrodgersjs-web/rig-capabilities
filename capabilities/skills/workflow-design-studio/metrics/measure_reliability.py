#!/usr/bin/env python3
"""measure_reliability.py — measured reliability metrics for the Workflow Design Studio
before/after table (mandate: stuck-relays count, watchdog false-RED count, relay round-trip seconds).

Sources (read-only, live):
  ~/.rig/live/prime-aside-driver/watchdog-log.jsonl   (Temporal watchdog sweeps)
  ~/.rig/live/prime-aside-driver/ledger.jsonl         (bridge send/reply rows)
  ~/.rig/live/prime-aside-driver/prime-chat/jobs/*/meta.json
Output: metrics/reliability.json + stdout summary.
"""
import json, glob, os, statistics, time

HOME = os.path.expanduser("~")
BASE = f"{HOME}/.rig/live/prime-aside-driver"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reliability.json")

sweeps = [json.loads(l) for l in open(f"{BASE}/watchdog-log.jsonl") if l.strip()]
stuck_ids, stuck_red_sweeps = set(), 0
false_red = 0
red_by_check = {}
for s in sweeps:
    for c in s.get("checks", []):
        red_by_check.setdefault(c["check"], 0)
        if c.get("red"):
            red_by_check[c["check"]] += 1
            if c["check"] == "stuck-relays":
                stuck_red_sweeps += 1
                d = c.get("detail")
                if isinstance(d, list):
                    stuck_ids |= {x.get("job") for x in d if x.get("job")}
            if c["check"] == "jake-alive":
                d = json.dumps(c.get("detail"))
                if "ENOENT /tmp/prime-agent-rust-501" in d:
                    false_red += 1

# relay round-trip: ledger prime_say -> prime_reply for the same job (true polled replies only)
rows = [json.loads(l) for l in open(f"{BASE}/ledger.jsonl") if l.strip()]
say_at, rtt = {}, []
backfilled = 0
for r in rows:
    t, j = r.get("tool"), r.get("job")
    if t == "prime_say" and j:
        say_at[j] = r.get("epoch")
    elif t == "prime_reply" and j and j in say_at:
        rtt.append(r["epoch"] - say_at[j])
    elif t == "prime_reply_backfill":
        backfilled += 1

# current unpaired set (jobs aged 30min..24h with no transcript reply is what the watchdog flags;
# here we report the watchdog's own last verdict plus the job population)
jobs = sorted(glob.glob(f"{BASE}/prime-chat/jobs/*/meta.json"))
last = sweeps[-1]
last_stuck = next((c for c in last.get("checks", []) if c["check"] == "stuck-relays"), {})
current_stuck = last_stuck.get("detail") if last_stuck.get("red") else []

res = {
    "source": "watchdog-log.jsonl + ledger.jsonl + prime-chat/jobs (live, read-only)",
    "sweeps_measured": len(sweeps),
    "stuck_relays": {
        "distinct_job_ids_ever_flagged": sorted(x for x in stuck_ids if x),
        "distinct_count": len([x for x in stuck_ids if x]),
        "red_sweeps": stuck_red_sweeps,
        "current_stuck_at_last_sweep": current_stuck if isinstance(current_stuck, list) else str(current_stuck),
        "jobs_on_disk": len(jobs),
    },
    "watchdog_false_red": {
        "jake_alive_enoent_tmp_probe_reds": false_red,
        "red_sweeps_per_check": red_by_check,
    },
    "relay_round_trip_seconds": {
        "samples_polled": len(rtt),
        "median": round(statistics.median(rtt), 1) if rtt else None,
        "mean": round(statistics.mean(rtt), 1) if rtt else None,
        "max": max(rtt) if rtt else None,
        "ledger_reply_rows_backfilled_not_timed": backfilled,
    },
}
json.dump(res, open(OUT, "w"), indent=2)
print(json.dumps(res, indent=2))
