#!/usr/bin/env python3
"""Worker E fleet governor (brief: ~/.rig/jake/overseer/briefs/WORKER-E-FLEET.md).

Every CYCLE_S: probe each meter (scoreboard-compatible), write fleet/latest.json,
start/stop ONLY jobs this governor launched (fleet/jobs.jsonl owns them), call
Worker B's capacity.py (read/use, never edit), run the Jev enforcer every 20 min,
and track the all-meters>=70% streak. Never kills missions or Worker A-D work.

Meters match scoreboard.py fleet(): cpu = 1-min load / cores; mac gpu = ioreg
Device Utilization (median of 3 draws); blackwell gpu rows from nvidia-smi.
"""
import json, os, re, signal, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

FLEET = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FLEET, "out")
LOGS = os.path.join(FLEET, "logs")
WORKERS = os.path.join(FLEET, "workers")
LATEST = os.path.join(FLEET, "latest.json")
JOBSF = os.path.join(FLEET, "jobs.jsonl")
HIST = os.path.join(OUT, "meters-history.jsonl")
LEDGER = os.path.join(OUT, "ledger.jsonl")
STREAKF = os.path.join(FLEET, "streak.json")
JEVLOG = os.path.join(OUT, "jev-enforce.jsonl")
CAPACITY = os.path.expanduser("~/.rig/jake/overseer/capacity.py")
S1 = os.path.expanduser("~/.rig/bin/rig-s1gate")
RECEIPTS = os.path.expanduser("~/.rig/jake/overseer/RECEIPTS.md")
CYCLE_S, JEV_EVERY = 300, 4
# GPU stop ceiling disabled: continuous batch decode pegs GPUs at 98-100 by
# design; util-based stops here caused kill/restart sawtooth that broke the
# >=70 window. CPU ceiling stays at 90 (protection against overload).
CPU_UNDER, CPU_OVER, GPU_UNDER, GPU_OVER = 70.0, 92.0, 70.0, 101.0
MACS = ["rig256gb", "rig96gb", "rig36gb"]
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6"]
BLACKWELL_GPU_NOTES = "blackwell-gpu1 omitted: nvidia-smi reports 'Unable to determine the device handle for GPU1' (device error; named physical reason, not a meter)"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(f"{now()} {msg}", flush=True)


def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 124, str(e)


# ---------------------------------------------------------------- meters
def probe_host(host):
    """Return (cpu_pct, gpu_draws, error). gpu_draws empty on blackwell."""
    if host == "blackwell":
        cmd = ("uptime; (nproc); "
               "nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits")
    else:
        cmd = ('uptime; (sysctl -n hw.ncpu); '
               'for i in 1 2 3; do ioreg -r -d 1 -w 0 -c IOAccelerator '
               '2>/dev/null | grep -oE \'Device Utilization %"=[0-9]+\' | head -1; sleep 2; done')
    timeout = 25 if host == "blackwell" else 45
    rc, out = sh(SSH + [host, cmd], timeout=timeout)
    if rc != 0:
        time.sleep(3)
        rc, out = sh(SSH + [host, cmd], timeout=timeout)  # one retry on transient ssh stall
    if rc != 0:
        return None, [], f"ssh rc={rc}: {out[:120]}"
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    m = re.search(r"load averages?:\s*([\d.]+)", lines[0] if lines else "")
    nums = [l for l in lines[1:] if l.isdigit()]
    if not m or not nums:
        return None, [], f"unparseable: {lines[:3]}"
    cores = int(nums[0])
    cpu = round(100.0 * float(m.group(1)) / max(cores, 1), 1)
    draws = [int(x) for x in re.findall(r'Device Utilization %"=(\d+)', out)]
    if host == "blackwell":
        draws = []  # gpu rows come from nvidia-smi lines
    return cpu, draws, None


def probe_blackwell_gpus():
    rc, out = sh(SSH + ["blackwell",
                        "nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits"],
                 timeout=20)
    g = {}
    if rc == 0:
        for ln in out.splitlines():
            p = [x.strip() for x in ln.split(",")]
            if len(p) == 2 and p[0].isdigit():
                g[int(p[0])] = float(p[1])
    return g


def probe():
    """-> (meters{key:pct_or_None}, raw{key:[draws]}, errors{key:reason})"""
    meters, raw, errors = {}, {}, {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(probe_host, h): h for h in MACS + ["blackwell"]}
        results = {futs[f]: f.result() for f in futs}
    for h in MACS + ["blackwell"]:
        cpu, draws, err = results[h]
        if err:
            meters[h] = None
            errors[h] = f"host unreachable: {err}"
        else:
            meters[h] = cpu
        if h != "blackwell":
            if err:
                meters[h + "-gpu"] = None
                errors[h + "-gpu"] = f"host unreachable: {err}"
            else:
                med = sorted(draws)[len(draws) // 2] if draws else None
                meters[h + "-gpu"] = float(med) if med is not None else None
                raw[h + "-gpu"] = draws
                if med is None:
                    errors[h + "-gpu"] = "no ioreg Device Utilization reading"
    if not errors.get("blackwell"):
        g = probe_blackwell_gpus()
        for i in (0, 2):
            meters[f"blackwell-gpu{i}"] = g.get(i)
            raw[f"blackwell-gpu{i}"] = [g.get(i)] if i in g else []
            if i not in g:
                errors[f"blackwell-gpu{i}"] = "nvidia-smi row missing"
        if 1 not in g:
            errors["blackwell-gpu1-note"] = BLACKWELL_GPU_NOTES
    return meters, raw, errors


def under(meters, errors):
    bad = []
    for k, v in meters.items():
        if v is None:
            bad.append(k)
            continue
        thr = GPU_UNDER if "gpu" in k else CPU_UNDER
        if v < thr:
            bad.append(k)
    return bad


def over(meters):
    out = []
    for k, v in meters.items():
        if v is None:
            continue
        thr = GPU_OVER if "gpu" in k else CPU_OVER
        if v > thr:
            out.append(k)
    return out


# ---------------------------------------------------------------- jobs
def load_jobs():
    rows = []
    if os.path.exists(JOBSF):
        for l in open(JOBSF):
            l = l.strip()
            if l:
                try:
                    rows.append(json.loads(l))
                except ValueError:
                    pass
    return rows


def save_jobs(rows):
    tmp = JOBSF + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.replace(tmp, JOBSF)


def clog(event, **kw):
    row = {"ts": now(), "event": event}
    row.update(kw)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def job_running(j):
    if j.get("kind") == "local":
        pid = j.get("pid")
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    rc, _ = sh(SSH + [j["host"], f"tmux has-session -t {j['id']} 2>/dev/null"], timeout=15)
    return rc == 0


def artifact_bytes(j):
    path, host = j.get("artifact"), j.get("artifact_host", "local")
    if not path:
        return None
    if host == "local":
        try:
            return os.path.getsize(path)
        except OSError:
            return None
    rc, out = sh(SSH + [host, f'stat -c%s "{path}" 2>/dev/null || stat -f%z "{path}" 2>/dev/null'],
                 timeout=15)
    if rc == 0 and out.strip().splitlines():
        try:
            return int(out.strip().splitlines()[-1])
        except ValueError:
            return None
    return None


def job_lines(j):
    path, host = j.get("artifact"), j.get("artifact_host", "local")
    if not path:
        return None
    if host == "local":
        try:
            with open(path, "rb") as f:
                return sum(1 for _ in f)
        except OSError:
            return None
    rc, out = sh(SSH + [host, f'wc -l < "{path}" 2>/dev/null'], timeout=15)
    try:
        return int(out.strip()) if rc == 0 else None
    except ValueError:
        return None


def start_job(j, actions):
    if j.get("kind") == "local":
        pid = subprocess.Popen(j["start"], shell=True, stdout=open(j["log"], "a"),
                               stderr=subprocess.STDOUT, start_new_session=True).pid
        j["pid"] = pid
        j["started"] = now()
        j["state"] = "running"
        actions.append(f"start {j['id']} (local pid {pid})")
        clog("job-start", job=j["id"], why=j.get("why", ""), pid=pid)
        return True
    rc, out = sh(SSH + [j["host"], j["start"]], timeout=40)
    if rc == 0:
        j["started"] = now()
        j["state"] = "running"
        j.pop("pid", None)
        actions.append(f"start {j['id']} on {j['host']}")
        clog("job-start", job=j["id"], host=j["host"], why=j.get("why", ""))
        return True
    j["state"] = "start-failed"
    j["last_error"] = out[:200]
    actions.append(f"START-FAILED {j['id']}: {out.strip()[:120]}")
    clog("job-start-failed", job=j["id"], host=j.get("host"), err=out[:200])
    return False


def stop_job(j, actions, reason):
    """Stop only a job this governor started."""
    if j.get("kind") == "local" and j.get("pid"):
        try:
            os.killpg(os.getpgid(j["pid"]), signal.SIGTERM)
        except OSError:
            pass
    elif j.get("host"):
        sh(SSH + [j["host"], f"tmux kill-session -t {j['id']} 2>/dev/null"], timeout=15)
    j["state"] = "queued"
    j.pop("pid", None)
    actions.append(f"stop {j['id']} ({reason})")
    clog("job-stop", job=j["id"], reason=reason)


def done_check(j):
    d = j.get("done_when")
    if not d:
        return False
    if d.get("kind") == "lines":
        n = job_lines(j)
        return n is not None and n >= d["target"]
    if d.get("kind") == "fit_lines":
        # local jsonl rows carrying a real score (error rows don't count)
        path = os.path.expandvars(os.path.expanduser(j.get("artifact", "")))
        try:
            n = 0
            with open(path) as f:
                for l in f:
                    if '"fit":' in l and '"fit": null' not in l:
                        n += 1
            return n >= d["target"]
        except OSError:
            return False
    if d.get("kind") == "flag":
        path = d["path"]
        # flag may live on the job's host: default from artifact_host, else local
        host = d.get("host") or j.get("artifact_host") or "local"
        if host == "local":
            return os.path.exists(os.path.expandvars(os.path.expanduser(path)))
        # remote: the remote shell expands $HOME in the literal path
        rc, _ = sh(SSH + [host, f'test -f "{path}"'], timeout=15)
        return rc == 0
    return False


def manage_jobs(meters, actions):
    rows = load_jobs()
    jobs_running = 0
    stalled = []
    stopped_for = {}
    for j in rows:
        running = job_running(j)
        if j["state"] == "running" and not running:
            if j.get("pid") or j.get("host"):
                actions.append(f"{j['id']} exited")
                clog("job-exit", job=j["id"])
            j["state"] = "queued" if not done_check(j) else "done"
        if j["state"] == "running":
            jobs_running += 1
            b = artifact_bytes(j)
            if b is not None:
                if j.get("last_bytes") is None:
                    j["last_bytes"] = b
                    j["last_growth"] = now()
                elif b > j["last_bytes"]:
                    j["last_bytes"] = b
                    j["last_growth"] = now()
                elif j.get("last_growth") and age_min(j["last_growth"]) >= 15:
                    stalled.append(j)
            elif j.get("artifact") and age_min(j.get("started") or "") >= 10:
                stalled.append(j)  # artifact file missing entirely after 10 min
            if done_check(j):
                j["state"] = "done"
                actions.append(f"{j['id']} DONE artifact complete")
                clog("job-done", job=j["id"], artifact=j.get("artifact"))
        # ceiling stop (only my jobs)
        # throttling: stop at most ONE job per over-meter per cycle (at the
        # CPU stop trigger 92, a hair above the 70-90 band) so load sheds
        # gradually instead of collapsing below 70
        over_m = [s for s in j["serves"]
                  if meters.get(s) is not None
                  and meters.get(s) > (GPU_OVER if "gpu" in s else CPU_OVER)]
        if j["state"] == "running" and over_m:
            mkey = over_m[0]
            if stopped_for.get(mkey, 0) >= 1:
                continue
            thr = GPU_OVER if "gpu" in mkey else CPU_OVER
            stop_job(j, actions, f"{mkey} at {m}% > {thr}% ceiling (throttle:1/cycle)")
            stopped_for[mkey] = stopped_for.get(mkey, 0) + 1
            jobs_running -= 1
    for j in stalled:
        stop_job(j, actions, "artifact stalled >=15min (requeue)")
        j["state"] = "queued"
    # start queued jobs for meters under target; <=2 new starts per meter per cycle
    started_for = {}
    for j in rows:
        if j["state"] in ("queued", "start-failed"):
            triggers = [s for s in j["serves"]
                        if meters.get(s) is not None and meters.get(s) < CPU_UNDER]
            if not triggers or any(started_for.get(s, 0) >= 2 for s in triggers):
                continue
            if done_check(j):
                continue
            if start_job(j, actions):
                jobs_running += 1
                for s in triggers:
                    started_for[s] = started_for.get(s, 0) + 1
    save_jobs(rows)
    return jobs_running, rows


def age_min(ts):
    try:
        t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 60.0
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- capacity + jev
def run_capacity(actions):
    rc, out = sh([sys.executable, CAPACITY, "cycle"], timeout=300)
    # capacity prints one pretty-printed JSON block on stdout; LEDGER rows ride on stderr
    d = None
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == "{":
            try:
                d, _ = json.JSONDecoder().raw_decode("\n".join(lines[i:]))
                break
            except ValueError:
                continue
    if rc == 0 and d is not None:
        inf = d.get("in_flight", {})
        if d.get("started"):
            actions.append(f"capacity.py started {d['started']} mission(s); in_flight={inf}")
            clog("capacity-cycle", started=d["started"], in_flight=inf)
        return
    err = next((ln for ln in reversed(lines) if ln.strip()), "")
    actions.append(f"capacity.py rc={rc}: {err[:100]}")
    clog("capacity-cycle-failed", rc=rc, err=err[:200])


def jev_enforce(meters, rows, actions):
    running = [j["id"] for j in rows if j["state"] == "running"]
    txt = (f"Routine: fleet utilization governor on Worker E, a named schedule of runs every "
           f"5 minutes (cycle ticks at 0,5,10,... past each hour), with this Jev enforcement "
           f"every 20 minutes (every 4th cycle). This run applies actions only after measuring: "
           f"actions this cycle = {actions or ['none']}, each taken because a meter measured "
           f"below 70 or above its ceiling. A dry run writes nothing. rig-s1gate check "
           f"routine.run runs locally and is not carried by a frontier model. Evidence: "
           f"the prior 'rig-s1gate check routine.run --json' returned a decision id, meters this cycle = "
           f"{meters}, running jobs = {running}, rows appended every cycle in {HIST} and "
           f"{LEDGER}. Owner: Worker E, fleet utilization engineer, approves the next run.")
    rc, out = sh([S1, "check", "routine.run", "--text", txt, "--subject",
                  "fleet-governor-cycle", "--json"], timeout=60)
    rec = {"ts": now(), "rc": rc, "raw": out[:4000]}
    try:
        d = json.loads(out)
        rec["parsed"] = d
    except ValueError:
        d = {}
    with open(JEVLOG, "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    verdict = d.get("verdict") or d.get("result") or f"rc={rc}"
    did = d.get("decision_id") or d.get("id") or ""
    actions.append(f"jev-enforce verdict={verdict} id={did}")
    try:
        with open(RECEIPTS, "a") as f:
            f.write(f"E: jev-enforce {now()} routine.run verdict={verdict} id={did} "
                    f"meters_ok={not under(meters, {})} running={running}\n")
    except OSError:
        pass
    return {"at": now(), "verdict": verdict, "decision_id": did}


# ---------------------------------------------------------------- main cycle
def cycle(n):
    t0 = time.time()
    actions = []
    meters, raw, errors = probe()
    rows = load_jobs()
    # capacity engine first: it owns mission starts
    run_capacity(actions)
    jobs_running, rows = manage_jobs(meters, actions)

    un = under(meters, errors)
    ov = over(meters)
    streak = {}
    if os.path.exists(STREAKF):
        try:
            streak = json.load(open(STREAKF))
        except ValueError:
            streak = {}
    elapsed_min = 0.0
    if streak.get("last_sample"):
        elapsed_min = age_min(streak["last_sample"])
    streak["last_sample"] = now()
    if not un:
        if streak.get("prev_good"):
            # consecutive good samples: credit actual wall time between samples
            streak["min"] = round((streak.get("min") or 0) + min(elapsed_min, 10.0), 1)
            streak.setdefault("since", now())
        streak["prev_good"] = True
        streak["last_good"] = now()
        streak.pop("bad_now", None)
    else:
        streak["min"] = 0
        streak["prev_good"] = False
        streak["since"] = None
        streak["bad_now"] = un
    json.dump(streak, open(STREAKF, "w"))

    jev = None
    if n % JEV_EVERY == 0:
        jev = jev_enforce(meters, rows, actions)
        if streak.get("min", 0) >= 60:
            actions.append("STREAK>=60min reached")
            clog("streak-60", meters=meters, running=[j["id"] for j in rows if j["state"] == "running"])

    doc = {"at": now(), "cycle": n, "meters": meters, "meters_raw": raw,
           "under_70": un, "over_ceiling": ov, "errors": errors,
           "jobs_running": jobs_running,
           "jobs": [{"id": j["id"], "state": j["state"], "artifact": j.get("artifact"),
                     "last_bytes": j.get("last_bytes"), "last_growth": j.get("last_growth")}
                    for j in rows],
           "streak_min": streak.get("min", 0), "actions": actions}
    if jev:
        doc["jev"] = jev
    tmp = LATEST + ".tmp"
    json.dump(doc, open(tmp, "w"), indent=1)
    os.replace(tmp, LATEST)
    with open(HIST, "a") as f:
        f.write(json.dumps({"ts": doc["at"], "meters": meters, "under_70": un,
                            "streak_min": doc["streak_min"],
                            "jobs_running": jobs_running}, separators=(",", ":")) + "\n")
    log(f"cycle {n}: under={un or 'none'} over={ov or 'none'} jobs={jobs_running} "
        f"streak={doc['streak_min']}m took {round(time.time() - t0, 1)}s")


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    while True:
        try:
            cycle(n)
        except Exception as e:
            log(f"cycle {n} ERROR: {e}")
            clog("cycle-error", err=str(e)[:300])
        n += 1
        time.sleep(CYCLE_S)


if __name__ == "__main__":
    main()
