#!/usr/bin/env python3
"""C3 capacity engine (Worker B) -- deterministic stdlib, no model call in the decision path."""
import json, os, re, subprocess, sys, time, urllib.request
from datetime import datetime, timezone

JAKE = os.path.expanduser("~/.rig/jake")
QUEUE = os.path.join(JAKE, "missions", "queue.jsonl")
LEDGER = os.path.join(JAKE, "missions", "ledger.jsonl")
STATE = os.path.join(JAKE, "overseer", "capacity-state.json")
FLEET = os.path.join(JAKE, "overseer", "fleet.py")
OMPPATH = "/Users/rig128gb/bin/omp"   # 18.3.2 (PATH-front shadows 17.3.1 — learnings)
# JAKE 22:10 takeover: missions run as LOCAL Orca terminals (remote tmux kept dying
# because the briefs need this Mac's files). Mac-local model servers first,
# Blackwell :8201 last; GPU1 (B2/8111) is in device error and never used.
LOCAL_LANES = ["rig-256gb-ollama/qwen3.6:35b-a3b",
               "rig-36gb-lan/qwen3.8:27b",
               "blackwell-mimo-v26/mimo-v2.6-flash"]
ORCA_WORKTREE = "path:/Users/rig128gb/Developer/rig-intelligence"
EXTERNAL_OWNED = {"M01", "M02", "M03", "M04", "M05", "M08"}  # JAKE 22:10 launches these

SLOTS = {"rig256gb": 2, "rig96gb": 1, "rig36gb": 1}
UNDER, CPU_STOP, GPU_STOP, TIMEOUT_S = 70.0, 90.0, 95.0, 8 * 3600
TERMINAL = {"done", "fail", "gate-failed", "receipt", "mission-orderly", "cut-off"}

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ledger(event, host=None, mission=None, **kw):
    row = {"ts": now(), "event": event}
    if host:
        row["host"] = host
    if mission:
        row["mission"] = mission
    row.update(kw)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")
    print("LEDGER " + json.dumps(row, separators=(",", ":")), file=sys.stderr, flush=True)

# ------------------------------------------------------------------ fleet read
def _gpu_tags(grid):
    """nvidia index -> util map into lane tags:
    b1 = mimo lanes (gpu0+gpu2), b2 = qwen lane (gpu1); missing gpu1 -> b2_down."""
    if not grid:
        return {}
    out = {"b1": round((grid.get(0, 0.0) + grid.get(2, 0.0)) / 2, 1),
           "b2": float(grid.get(1, 0.0))}
    if 1 not in grid:
        out["b2_down"] = 1
    return out


def _parse_fleet(d):
    """Worker A's fleet.py --json schema -> (hosts, gpus).

    hosts.<h>.busy_pct; gpus = [{index, util_pct, ...}]. Returns ({}, {}) when
    neither side parses, so read_fleet can fall back to ssh probes."""
    hosts = {}
    for k, v in (d.get("hosts") or {}).items():
        if isinstance(v, dict) and v.get("busy_pct") is not None:
            try:
                hosts[k] = float(v["busy_pct"])
            except (TypeError, ValueError):
                pass
    grid = {}
    for g in (d.get("gpus") or []):
        if (isinstance(g, dict) and g.get("index") is not None
                and g.get("util_pct") is not None):
            grid[int(g["index"])] = float(g["util_pct"])
    return hosts, _gpu_tags(grid)


def _parse_nvidia_csv(text):
    """nvidia-smi csv,noheader,nounits rows -> {index: util}.

    Rows are `0, 86`; split() would yield ['0,', '86'] and drop every row, so
    split on comma. The GPU1 device-error line has no digit,digit shape."""
    grid = {}
    for ln in text.splitlines():
        seg = [s.strip() for s in ln.split(",")]
        if len(seg) >= 2 and seg[0].isdigit() and seg[1].isdigit():
            grid[int(seg[0])] = int(seg[1])
    return grid


def read_fleet():
    """Return (host_busy_pct, gpu_pct_dict, source_tag).

    Primary source is Worker A's `fleet.py --json` (hosts.<h>.busy_pct,
    gpus = [{index, util_pct}]); ssh fallback probes otherwise."""
    note = ""
    if os.path.exists(FLEET):
        try:
            r = subprocess.run([sys.executable, FLEET, "--json"],
                               capture_output=True, text=True, timeout=90)
            if r.returncode == 0:
                hosts, gpus = _parse_fleet(json.loads(r.stdout))
                if hosts and gpus:
                    return hosts, gpus, "fleet.py --json"
                note = "fleet.py gave incomplete data"
        except Exception as e:
            note = "fleet.py error " + str(e)[:60]
    hosts, unreach = {}, []
    for h in SLOTS:
        try:
            r = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", h,
                 "sysctl -n vm.loadavg; sysctl -n hw.ncpu"],
                capture_output=True, text=True, timeout=20)
            lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
            l5 = float(re.match(r"[\(\{]\s*(\d[\d.]*)", lines[0]).group(1))
            cores = int(lines[1].strip())
            hosts[h] = round(l5 / max(cores, 1) * 100.0, 1)
        except Exception:
            hosts[h] = 0.0
            unreach.append(h)
    gpus, gnotes = {}, []
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
             "root@192.168.68.90",
             "nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20)
        if r.returncode != 0 or not r.stdout.strip():
            gnotes.append("blackwell")
        else:
            grid = _parse_nvidia_csv(r.stdout)
            gpus.update(_gpu_tags(grid))
            # GPU1 device error -> nvidia-smi omits its row; 0.0 would read as healthy
            if grid and 1 not in grid:
                gnotes.append("gpu1-down")
    except Exception:
        gnotes.append("blackwell")
    for tag in ("b1", "b2"):
        gpus.setdefault(tag, 0.0)
    src = "fallback probes" + (" | " + note if note else "") \
        + (" | unreachable:" + ",".join(unreach + gnotes)
           if unreach + gnotes else "")
    return hosts, gpus, src

# ------------------------------------------------------------------ state
def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"under": {}, "in_flight": {}}

def save_state(st):
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)

def under_two_consecutive(h, st, busy):
    win = st.setdefault("under", {})
    win[h] = list(win.get(h, [])[-7:]) + [busy]
    st["under"][h] = win[h]
    w2 = win[h][-2:]
    return len(w2) == 2 and w2[0] < UNDER and w2[1] < UNDER

# ------------------------------------------------------------------ queue
def finished_ids():
    done = set()
    try:
        for l in open(LEDGER):
            try:
                r = json.loads(l)
                if r.get("event") in TERMINAL and r.get("mission"):
                    done.add(r["mission"])
            except Exception:
                pass
    except Exception:
        pass
    return done

# spec C3: "stop starting above 90% CPU / 95% GPU" -- gate scoped to the GPU
# that the lane launch() would pick (Blackwell b1/b2); Mac lanes have no
# Blackwell GPU dependency and are gated by the CPU ceiling above.
LANE_GPU = {"blackwell-mimo-v26": "b1", "blackwell-uncensored": "b2"}


def _next_lane():
    """The lane launch() will pick next (same round-robin read, no mutation)."""
    return LOCAL_LANES[int(_lane_state().get("launch_seq", 0)) % len(LOCAL_LANES)]


def _lane_gpu(lane):
    for pre, tag in LANE_GPU.items():
        if lane.startswith(pre):
            return tag
    return None


def pick_next(rows, done, inflight_ids_by_host, h=None):
    """Queue-row rank; skip DONE, in-flight, and hosts whose slots are full or OVER."""
    # GPU ceiling: refuse to start when the would-be lane's GPU is OVER.
    gtag = _lane_gpu(_next_lane())
    if gtag:
        if gpus_snapshot.get(str(gtag) + "_down"):
            return None
        try:
            if float(gpus_snapshot.get(gtag, 0.0)) > GPU_STOP:
                return None
        except (TypeError, ValueError):
            return None
    for m in rows:
        bid = m.get("id", "")
        host = m.get("host", "")
        if not bid or not host or (h and host != h):
            continue
        if bid in done or bid in EXTERNAL_OWNED or any(bid in v for v in state.get("in_flight_ids", {}).values()):
            continue
        deps = m.get("depends", [])
        if deps and any(d not in done for d in deps):
            continue
        if len(inflight_ids_by_host.get(host, [])) >= SLOTS[host]:
            continue
        busy = hosts_snapshot.get(host, 0.0)
        if busy > CPU_STOP:
            continue
        if not under_two_consecutive(host, state, busy):
            continue
        return m
    return None

def _orca_live(handle):
    """True when the Orca terminal handle still exists."""
    if not handle:
        return False
    r = subprocess.run(["orca", "terminal", "show", "--terminal", handle, "--json"],
                       capture_output=True, text=True, timeout=20)
    try:
        return bool(json.loads(r.stdout or "").get("ok"))
    except Exception:
        return False

def _orca_close(handle):
    """Best-effort close of one of our own mission terminals."""
    if not handle:
        return
    try:
        subprocess.run(["orca", "terminal", "close", "--terminal", handle],
                       capture_output=True, timeout=20)
    except Exception:
        pass

_LS = ""
def _lane_state():
    global _LS
    try:
        _LS = json.load(open(STATE + "-lane.json"))
    except (FileNotFoundError, ValueError):
        _LS = {}
    return _LS

def _lane_save(st):
    global _LS
    _LS = st
    json.dump(st, open(STATE + "-lane.json", "w"))


# ------------------------------------------------------------------ launch + reap
def launch(m, host):
    # JAKE 22:10 takeover: LOCAL Orca terminal, in_flight tracked by handle.
    bid = m["id"]
    bidl = bid.lower()
    st = _lane_state()
    seq = int(st.get("launch_seq", 0))
    st["launch_seq"] = seq + 1
    _lane_save(st)
    lane = LOCAL_LANES[seq % len(LOCAL_LANES)]  # Mac-local first, Blackwell last
    brief = os.path.join(JAKE, "missions", "briefs", bid + ".md")
    out = os.path.join(JAKE, "missions", "out", bidl + ".log")
    donf = os.path.join(JAKE, "missions", "receipts", bidl + ".done")
    falf = os.path.join(JAKE, "missions", "receipts", bidl + ".failed")
    if not os.path.isfile(brief):
        ledger("launch-brief-missing", host, bid)
        return False
    # rc+size gate + typo-text guard (error runs exit rc=0, so text must be checked);
    # TERM=dumb keeps the PTY from injecting ANSI that would pollute the log/grep
    cmd = ("rm -f " + donf + " " + falf + "; "
           + "TERM=dumb " + OMPPATH + " --model " + lane + " @" + brief + " > " + out + " 2>&1; rc=$?; "
           + "if [ $rc -eq 0 ] && [ -s " + out + " ] "
           + "&& ! grep -q \"Was there a typo in the url or port\" " + out + "; "
           + "then echo done > " + donf + "; else echo FAILED-rc=$rc > " + falf + "; fi")
    r = subprocess.run(["orca", "terminal", "create", "--worktree", ORCA_WORKTREE,
                        "--title", "om-" + bidl, "--command", cmd, "--json"],
                       capture_output=True, text=True, timeout=60)
    handle = None
    try:
        d = json.loads(r.stdout or "")
        if d.get("ok"):
            handle = d["result"]["terminal"]["handle"]
    except Exception:
        pass
    if not handle:
        ledger("launch-failed", host, bid, lane=lane,
               stderr=((r.stderr or "") + (r.stdout or ""))[:300])
        return False
    # JAKE P0: 62s steady-state verify — .failed, or terminal gone with no flags
    # => mark FAILED (with log tail), do NOT enter in_flight; next cycle rotates lane.
    time.sleep(62)
    fl, dn = os.path.isfile(falf), os.path.isfile(donf)
    live = _orca_live(handle)
    if fl:
        tail = ""
        if os.path.isfile(out):
            with open(out, errors="replace") as f:
                tail = f.read()[-300:]
        ledger("launch-verify-failed", host, bid, lane=lane, handle=handle, err=tail)
        _orca_close(handle)
        return False
    if not (dn or live):
        ledger("launch-verify-failed", host, bid, lane=lane, handle=handle,
               err="terminal gone, no .done/.failed")
        return False
    ledger("launch", host, bid, lane=lane, handle=handle)
    state.setdefault("in_flight", {}).setdefault(host, [])
    state["in_flight"][host].append({"id": bid, "ts": now(), "lane": lane, "handle": handle})
    state.setdefault("in_flight_ids", {}).setdefault(host, [])
    if bid not in state["in_flight_ids"][host]:
        state["in_flight_ids"][host].append(bid)
    return True

def reap(host, s):
    """Close missions on receipt/.failed flags; dead-handle fallback after 5 min."""
    for e in list(s):
        bid, bidl = e["id"], e["id"].lower()
        donf = os.path.join(JAKE, "missions", "receipts", bidl + ".done")
        falf = os.path.join(JAKE, "missions", "receipts", bidl + ".failed")
        out = os.path.join(JAKE, "missions", "out", bidl + ".log")
        fl, dn = os.path.isfile(falf), os.path.isfile(donf)
        age_h = (datetime.now(timezone.utc) -
                 datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))).total_seconds() / 3600.0
        handle = e.get("handle")
        if dn:
            ledger("receipt", host, bid, age_h=round(age_h, 2), handle=handle)
            _orca_close(handle)
            s.remove(e)
        elif fl:
            tail = ""
            if os.path.isfile(out):
                with open(out, errors="replace") as f:
                    tail = f.read()[-300:]
            ledger("mission-failed", host, bid, age_h=round(age_h, 2),
                   handle=handle, err=tail)
            _orca_close(handle)
            s.remove(e)
        elif age_h > 5.0 / 60.0 and not _orca_live(handle):
            ledger("launch-session-dead", host, bid, age_h=round(age_h, 2), handle=handle)
            s.remove(e)
        elif age_h > TIMEOUT_S / 3600.0 and not _orca_live(handle):
            ledger("mission-orderly", host, bid, age_h=round(age_h, 1), handle=handle)
            s.remove(e)

# ------------------------------------------------------------------ main cycle
_hosts_snapshot, _gpus_snapshot = {}, {}
def cycle():
    global hosts_snapshot, gpus_snapshot, state
    hosts, gpus, source = read_fleet()
    hosts_snapshot, gpus_snapshot = hosts, gpus
    st = load_state()
    state = st
    st.setdefault("in_flight_ids", {})
    st["external_owned"] = sorted(EXTERNAL_OWNED)
    rows = [json.loads(l) for l in open(QUEUE) if l.strip()]
    done = finished_ids()
    started = 0
    for h in list(SLOTS):
        # one mission start per host per cycle (ponytail: conservative; the 2-read gate owns pace)
        m = pick_next(rows, done, st.get("in_flight_ids", {}), h)
        if m and launch(m, h):
            started += 1
    # reap finished, then sync id bookkeeping with survivors
    for h, lst in st.get("in_flight", {}).items():
        if lst:
            reap(h, lst)
        survivors = list(lst)
        st.setdefault("in_flight_ids", {}).setdefault(h, [])
        still = [i for i in st["in_flight_ids"][h] if i in [e["id"] for e in survivors]]
        st["in_flight_ids"][h] = still
    save_state(st)
    print(json.dumps({"ok": True, "hosts": hosts, "gpu": gpus, "source": source,
                      "started": started, "in_flight": {k: len(v) for k, v in st.get("in_flight_ids", {}).items()},
                      "under_windows": {k: v[-2:] for k, v in st.get("under", {}).items()}},
                     indent=1))
    return 0

def status():
    st = load_state()
    hosts, gpus, source = read_fleet()
    print(json.dumps({"hosts": hosts, "gpu": gpus, "source": source,
                      "in_flight": st.get("in_flight", {}),
                      "under_windows": {k: v[-4:] for k, v in st.get("under", {}).items()}},
                     indent=1))
    return 0

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            return status()
        if cmd == "fleet":
            hosts, gpus, source = read_fleet()
            print(json.dumps({"hosts": hosts, "gpu": gpus, "source": source}, indent=1))
            return 0
        if cmd == "cycle":
            return cycle()
    print("usage: capacity.py {cycle|status|fleet}")
    return 2

if __name__ == "__main__":
    sys.exit(main())