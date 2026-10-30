#!/usr/bin/env python3
"""Scenario-only REA capture for public web surfaces.
Usage: scen.py <name> <url1> [url2 ...]
"""
import json, shlex, subprocess, sys, os
WORK = "/Users/rig128gb/.rig/work/rea-feature-mine"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def run(cmd, timeout=300):
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

name, urls = sys.argv[1], sys.argv[2:]
actions = []
for i, u in enumerate(urls):
    if i > 0:
        actions.append({"step_id": f"go{i}", "action": "goto", "destination": {"url": u, "query": []}, "wait_until": "load"})
    actions.append({"step_id": f"w{i}", "action": "wait_for_timeout", "duration_ms": 5000})
payload = {"browser": {"mode": "launch", "executable_path": CHROME, "headless": True},
           "start_url": {"url": urls[0], "query": []}, "actions": actions,
           "capture": {"at_end": ["url", "dom", "accessibility"], "events": ["network", "console"]}}
ipath = f"{WORK}/{name}-scenario-input.json"
json.dump(payload, open(ipath, "w"))
rc, out, err = run(f"rea capture-browser-scenario {shlex.quote(ipath)} --json")
if rc != 0:
    print(f"[{name}] FAILED: {out[:300]}"); sys.exit(1)
open(f"{WORK}/{name}-scenario.json", "w").write(out)
d = json.loads(out)
nr = d.get("normalized_result", d)
print(f"[{name}] ok: {len(nr.get('steps',[]))} steps, {len(nr.get('events',{}).get('items',[]))} events, {len(out)} bytes")
