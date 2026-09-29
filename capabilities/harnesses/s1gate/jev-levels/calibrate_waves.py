#!/usr/bin/env python3
"""Calibrate the ten-level jev.* rubrics from the 300 suite cases, in gentle waves.

One level per wave, 3 concurrent Jev calls, and a load/memory check between
waves (waits while the 1-min load average is above LOAD_MAX or free memory is
low). Each wave: fresh live decisions (subject calib:<id>) -> signal labels
from the case's expected option (labelled_by suite:ten-levels-v1) ->
s1gate_calibrate on the rubric's RISK rule. Dry run unless --write.
"""
import json, os, pathlib, subprocess, sys, time, concurrent.futures as cf
REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from rig_capabilities.s1gate import DecisionLog
from rig_capabilities.s1gate_calibrate import calibrate_rubric
HERE = pathlib.Path(__file__).parent
S1 = os.path.expanduser("~/.rig/bin/rig-s1gate")
BY = "suite:ten-levels-v1"
LOAD_MAX = float(os.environ.get("LOAD_MAX", "24"))
# rubric -> (question, attr, direction, which expected options are BAD)
PLAN = {
 "jev.escalation":       ("needs_reasoning", "p.yes", "above", {"yes"}),
 "jev.triage":           ("lane", "confidence", "below", set()),
 "jev.scrape-classify":  ("category", "confidence", "below", set()),
 "jev.auto-approve":     ("risk", "p.yes", "above", {"yes"}),
 "jev.skill-router":     ("skill", "confidence", "below", set()),
 "jev.bash-gate":        ("destructive_irreversible", "p.yes", "above", {"yes"}),
 "jev.file-triage":      ("credential_bearing", "p.yes", "above", {"cred"}),
 "jev.compact-read":     ("compact_is_safe", "p.no", "above", {"no"}),
 "jev.injection-screen": ("instruction_override", "p.yes", "above", {"yes"}),
 "jev.gate-d":           ("outward_or_irreversible", "p.yes", "above", {"yes"}),
}
def free_gb():
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    pages = {l.split(":")[0].strip(): int(l.split(":")[1].strip().rstrip(".")) for l in out.splitlines()[1:] if ":" in l and l.split(":")[1].strip().rstrip(".").isdigit()}
    return (pages.get("Pages free", 0) + pages.get("Pages inactive", 0)) * 16384 / 1e9
def breathe():
    for _ in range(12):
        la = os.getloadavg()[0]; fg = free_gb()
        if la <= LOAD_MAX and fg >= 4: return la, fg
        print(f"   waiting: load {la:.1f} free {fg:.1f}GB", flush=True); time.sleep(10)
    return os.getloadavg()[0], free_gb()
def call(rubric, c):
    r = subprocess.run([S1, "check", rubric, "--stdin", "--json", "--subject", f"calib:{c['id']}"],
                       input=c["state"], capture_output=True, text=True, timeout=45)
    return c, json.loads(r.stdout)
def main(write):
    log = DecisionLog(); summary = []
    only = [x for x in os.environ.get("RUBRICS", "").split(",") if x]
    relabel = os.environ.get("RELABEL", "1") == "1"
    for f in sorted(HERE.glob("level*.json")):
        doc = json.loads(f.read_text()); rb = doc["rubric"]; q, attr, direction, bad = PLAN[rb]
        amb = HERE / f"ambiguous{doc['level']:02d}.json"
        if amb.exists():   # routing: ambiguous items are the BAD class for the confidence rule
            doc["cases"] = doc["cases"] + json.loads(amb.read_text())["cases"]
        if only and rb not in only: continue
        la, fg = breathe()
        print(f"WAVE L{doc['level']:02d} {rb}  (load {la:.1f}, free {fg:.1f}GB)", flush=True)
        got = []
        if relabel:
            with cf.ThreadPoolExecutor(max_workers=3) as ex:
                got = list(ex.map(lambda c: call(rb, c), doc["cases"]))
        n = 0
        for c, d in got:
            if d.get("error") or not d.get("decision_id"): continue
            opt = c.get("expect", {}).get(q, {}).get("option")
            if c.get("expect_escalate"):
                lab = "bad"
            elif rb == "jev.file-triage":
                lab = "bad" if "credential_bearing" in c["expect"] else "good"
            else:
                lab = "bad" if opt in bad else "good"
            log.label_signal(d["decision_id"], f"{q}.{attr}", lab,
                             by=BY if c["id"].startswith("l") else "agent-review:ambiguous-v1"); n += 1
        res = calibrate_rubric(rb, (q, attr), direction=direction, tie=("declared" if attr == "confidence" else "middle"), write=write)
        op = res.get("operating_point") or {}
        row = {"rubric": rb, "signal": f"{q}.{attr}", "labelled_now": n, "n_labelled": res["n_labelled"],
               "good": res["n_good"], "bad": res["n_bad"], "certified": res["certified"],
               "threshold": op.get("threshold"), "holdout": res.get("holdout"), "reason": res["reason"]}
        summary.append(row)
        print(f"   labelled {n}, total {res['n_labelled']} (good {res['n_good']} / bad {res['n_bad']}) "
              f"-> certified={res['certified']} t={op.get('threshold')} :: {res['reason'][:120]}", flush=True)
        time.sleep(5)
    log.close()
    out = pathlib.Path(os.environ.get("JEV_EVIDENCE_DIR", "/tmp")) / f"calibrate-waves-{time.strftime('%Y%m%dT%H%M%S')}{'-write' if write else '-dry'}.json"
    out.write_text(json.dumps(summary, indent=1)); print("evidence:", out)
if __name__ == "__main__":
    main("--write" in sys.argv)
