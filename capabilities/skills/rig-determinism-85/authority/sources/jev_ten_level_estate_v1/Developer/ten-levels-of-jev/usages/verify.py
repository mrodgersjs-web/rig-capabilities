#!/usr/bin/env python3
"""Live-verify every jev use case against real Jev at p>=0.9.

For each case in usages/levelNN.json: pipe the state through
`rig-s1gate check <rubric> --stdin --json` and compare every expectation
({min} / {max} / {option,min}) against the returned probabilities.
Flaky-by-nature calls get one retry; best observation wins.
Exit 0 only when every case clears its bar. Evidence: verify-results.json.
"""
import json, subprocess, sys, time, collections, concurrent.futures as cf, pathlib, os

HERE = pathlib.Path(__file__).parent
S1 = os.path.expanduser("~/.rig/bin/rig-s1gate")

def call(rubric, state):
    r = subprocess.run([S1, "check", rubric, "--stdin", "--json"],
                       input=state, capture_output=True, text=True, timeout=30)
    d = json.loads(r.stdout)
    if d.get("error"):
        raise RuntimeError(d["error"])
    return d

def check_case(c, rubric):
    """Return (ok, detail). One retry on miss (Jev is a sampler, not a hash)."""
    best = None
    for _ in range(2):
        try:
            d = call(rubric, c["state"])
        except Exception as e:
            best = (False, f"ERROR {e}")
            continue
        fails, obs = [], {}
        for qid, exp in c["expect"].items():
            ans = d["answers"].get(qid)
            if not ans:
                fails.append(f"{qid}: missing"); continue
            if "option" in exp:
                p = ans.get("probabilities", {}).get(exp["option"], 0.0)
                obs[qid] = f"p={p:.2f} pick={ans.get('choice')}"
                if p < exp["min"]:
                    fails.append(f"{qid} {exp['option']}={p:.2f}<{exp['min']}")
            elif "min" in exp:
                p = ans["noul"]
                obs[qid] = f"noul={p:.2f}"
                if p < exp["min"]:
                    fails.append(f"{qid} noul={p:.2f}<{exp['min']}")
            else:
                p = ans["noul"]
                obs[qid] = f"noul={p:.2f}"
                if p > exp["max"]:
                    fails.append(f"{qid} noul={p:.2f}>{exp['max']}")
        rec = {"id": c["id"], "level": None, "rubric": rubric, "ok": not fails,
               "obs": obs, "fails": fails, "decision_id": d.get("decision_id"),
               "state": c["state"][:160]}
        if not fails:
            return True, rec
        best = (False, rec)
    return best

def main():
    cases = []
    for f in sorted(HERE.glob("level*.json")):
        doc = json.loads(f.read_text())
        for c in doc["cases"]:
            c["level"] = doc["level"]
            cases.append((doc["rubric"], c))
    print(f"cases: {len(cases)} across {len(set(c[1]['level'] for c in cases))} levels", flush=True)
    t0 = time.time()
    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(check_case, c, rb): (rb, c) for rb, c in cases}
        for fu in cf.as_completed(futs):
            ok, rec = fu.result()
            rec["level"] = futs[fu][1]["level"]
            results.append(rec)
            mark = "." if ok else "X"
            print(mark, end="", flush=True)
    print(f"\n{time.time()-t0:.0f}s")
    by = collections.defaultdict(lambda: [0, 0])
    for r in results:
        by[r["level"]][0] += 1
        by[r["level"]][1] += r["ok"]
    print("level  total  pass  rate")
    for lvl in sorted(by):
        t, p = by[lvl]
        print(f"  L{lvl:02d}   {t:4d}  {p:4d}  {p/t*100:.0f}%")
    misses = sorted((r for r in results if not r["ok"]), key=lambda r: r["id"])
    print(f"\nMISSES ({len(misses)}):")
    for m in misses:
        print(f"  {m['id']} [{m['rubric']}] {m['fails']} :: {m['state'][:80]}")
    out = HERE / "verify-results.json"
    out.write_text(json.dumps({"at": time.strftime("%F %T"), "total": len(results),
        "pass": sum(r["ok"] for r in results), "misses": misses, "results": sorted(results, key=lambda r: r["id"])},
        indent=1))
    print(f"evidence: {out}")
    return 0 if not misses else 1

sys.exit(main())
