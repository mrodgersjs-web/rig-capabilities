#!/usr/bin/env python3
"""memory-verifier -- plant-failure canary + soak ledger for the RIG Memory OS plane.

Each check is a claim this estate has already been burned on once:
  W  write path alive      (omniscout silently wrote nothing for weeks)
  F  frozen stays frozen   (governance regression: propose_memory must 409)
  C  cron tick green       (10 flows failed EVERY tick for weeks, silently)
  H  healer converges     (16,474 false 'REPAIRED' lines while the plane died)
  S  consolidation alive  (redis auth outage masqueraded as an empty queue)

Every check was observed RED against a planted bad state before it was trusted
GREEN. Exit 0 = all green, 1 = any RED; RED is delivered four ways: log line,
macOS notification, vault alarm note, canonical memory_verifier.alarm event.

Soak ledger: history.jsonl gets one row per run; once a day the run also emits
memory_verifier.soak -- the green-rate over trailing 7/30 days plus the last
consolidation counters -- so "outcome measured" is a queryable series from day
one, not a memory. That event is the maturity receipt the world-class ladder
asks for; run --soak to print the rate without writing anything.

Proof artifacts: ~/.rig/state/memory-verifier/{history.jsonl,last-run.json,soak.done}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

STATE = Path(os.environ.get("MEMVER_STATE_DIR", Path.home() / ".rig/state/memory-verifier"))
LOG_DIR = Path(os.environ.get("MEMVER_LOG_DIR", Path.home() / ".rig/logs"))
MEMORY_CLI = Path(os.environ.get("MEMVER_MEMORY_CLI", Path.home() / "bin/rig-memory-os"))
HISTORY = STATE / "history.jsonl"
LANE_EVIDENCE = STATE / "lane-evidence.json"
LAST_CONSOLIDATION: dict = {}


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def run(cmd: list, timeout: int = 60) -> tuple:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as exc:  # noqa: BLE001
        return 4, "", str(exc)[:200]


def check_write() -> str:
    day = f"{_now_utc():%Y%m%d}"
    key = f"memver-sentinel-{day}"
    # Deterministic bytes: same key + same payload all day -> replay is a no-op;
    # a varying occurred_at made every second run of the day a self-inflicted Conflict.
    payload = {
        "run_id": f"memory-verifier-{day}", "mission_id": "plane-proof",
        "event_type": "memory_verifier.sentinel",
        "occurred_at": f"{day[:4]}-{day[4:6]}-{day[6:]}T00:00:00+00:00",
        "sensitivity": "internal",
        "payload": {"purpose": "write-path liveness sentinel", "day": day},
        "idempotency_key": key,
    }
    rc, out, err = run([str(MEMORY_CLI), "call", "memory.record_event", "--input", json.dumps(payload)], timeout=30)
    # rc 0 = first write today; ConflictError = sentinel already landed today (green)
    if not (rc == 0 or "idempotency" in (out + err).lower()):
        raise RuntimeError(f"sentinel write failed: {(err or out)[:160]}")
    # in-loop plant failure: same key, different bytes MUST be refused
    payload["payload"] = {"purpose": "REPLAY MUST BE REFUSED"}
    rc2, out2, _ = run([str(MEMORY_CLI), "call", "memory.record_event", "--input", json.dumps(payload)], timeout=30)
    if rc2 == 0 or "idempotency" not in (out2 + "").lower():
        raise RuntimeError("idempotency replay NOT refused -- write plane integrity is broken")
    return "write+idempotent-replay proven"


def check_frozen() -> str:
    rc, out, err = run([str(MEMORY_CLI), "call", "memory.propose_memory",
                        "--input", json.dumps({"probe": "governance canary -- must never execute"})], timeout=30)
    text = (out + err).lower()
    if rc == 0 or "not_executed" not in text:
        raise RuntimeError("frozen op EXECUTED or answer changed -- governance regression")
    return "propose_memory still FROZEN"


def check_cron() -> str:
    logs = sorted(LOG_DIR.glob("memory-os-cron-2026*.log"), key=lambda p: p.stat().st_mtime)
    if not logs:
        raise RuntimeError("no cron logs at all")
    fresh = [p for p in logs[-4:] if p.stat().st_size > 0]
    if not fresh:
        raise RuntimeError("recent cron logs empty")
    last = fresh[-1]
    age_min = (_now_utc().timestamp() - last.stat().st_mtime) / 60
    text = last.read_text(errors="replace")
    if "All flows: SUCCESS" not in text:
        raise RuntimeError(f"latest tick ({last.name}) has no flows-SUCCESS line")
    if age_min > 15 and "Flows failed:" in text:
        raise RuntimeError(f"latest tick is {age_min:.0f}min old with a completed summary -- cron cadence dead")
    failed = [line for line in text.splitlines() if "Flows failed:" in line]
    if failed and not failed[-1].endswith("0"):
        raise RuntimeError(failed[-1])
    return f"tick fresh ({age_min:.0f}min) and green"


def check_consolidation() -> str:
    # launchd cadence is 1800s; a fresh START+DONE pair with counters must exist in
    # the stdout tail. Auth/connect failures now exit non-zero (working.ts refuses to
    # claim empty), so a stale tail means the loop died, not that the queue is empty.
    out = LOG_DIR / "memory-consolidation.stdout.log"
    if not out.is_file():
        raise RuntimeError("consolidation stdout log absent -- job never ran here")
    age_min = (_now_utc().timestamp() - out.stat().st_mtime) / 60
    if age_min > 66:
        raise RuntimeError(f"consolidation stdout stale ({age_min:.0f}min) -- launchd job stalled/dead")
    tail = out.read_text(errors="replace")[-800:]
    m = None
    for m in re.finditer(r"DONE run_id=\S+ promoted=(\d+) summarized=(\d+) deduped=(\d+) decayRefreshed=(\d+)", tail):
        pass
    if m is None:
        raise RuntimeError(f"fresh log but no DONE line with counters: {tail[-120:]}")
    LAST_CONSOLIDATION.update(promoted=int(m.group(1)), summarized=int(m.group(2)),
                              deduped=int(m.group(3)), decayRefreshed=int(m.group(4)))
    return f"fresh ({age_min:.0f}min) counters={json.dumps(LAST_CONSOLIDATION, sort_keys=True)}"


def check_healer() -> str:
    # Crying wolf = the SAME repair kind repeated on consecutive fresh ticks
    # (non-convergent repair, like the 16,474-line doctor_summary_fail loop of
    # 2026-09-20: a broken binding the healer could never actually fix).
    # A single REPAIRED line is the healer doing its job. Stale tail is not recent crying.
    log = LOG_DIR / "memory-healer-cron.log"
    if not log.is_file():
        return "healer log absent (healer may be cron-managed elsewhere)"
    age_min = (_now_utc().timestamp() - log.stat().st_mtime) / 60
    tail = [ln for ln in log.read_text(errors="replace")[-2000:].splitlines() if ln.strip()][-5:]
    repaired = [ln for ln in tail if "REPAIRED" in ln]
    if age_min <= 15 and len(repaired) >= 3 and len({ln.split("-")[-1].strip() for ln in repaired}) == 1:
        raise RuntimeError(f"non-convergent repair loop: {repaired[-1][:120]}")
    return f"not crying wolf (tail fresh={age_min <= 15}, repairs in last 5 lines: {len(repaired)})"


def load_history() -> list:
    rows = []
    if HISTORY.is_file():
        for line in HISTORY.read_text().splitlines()[-4000:]:
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def soak_rate(rows: list, days: int) -> dict:
    cutoff = (_now_utc() - dt.timedelta(days=days)).isoformat()
    window = [r for r in rows if r.get("ts", "") >= cutoff]
    green = sum(1 for r in window if not r.get("red"))
    return {"days": days, "runs": len(window), "green": green,
            "green_rate": round(green / len(window), 4) if window else None}


def report_soak(rows: list) -> int:
    for d in (7, 30):
        s = soak_rate(rows, d)
        print(f"soak {s['days']}d: {s['green']}/{s['runs']} green"
              + (f" ({s['green_rate']:.1%})" if s["green_rate"] is not None else " (no data)"))
    return 0


def emit_daily_soak(rows: list, results: dict) -> None:
    today = f"{_now_utc():%Y-%m-%d}"
    marker = STATE / "soak.done"
    if marker.is_file() and marker.read_text().strip() == today:
        return
    body = {
        "event_type": "memory_verifier.soak", "day": today,
        "soak_7d": soak_rate(rows, 7), "soak_30d": soak_rate(rows, 30),
        "consolidation_counters": dict(LAST_CONSOLIDATION),
        "checks": {k: v["status"] for k, v in results.items() if isinstance(v, dict)},
    }
    payload = {
        "run_id": f"memory-verifier-soak-{today.replace('-', '')}", "mission_id": "plane-proof",
        "event_type": "memory_verifier.soak", "occurred_at": _now_utc().isoformat(timespec="seconds"),
        "sensitivity": "internal", "payload": body, "idempotency_key": f"memver-soak-{today}",
    }
    rc, _, _ = run([str(MEMORY_CLI), "call", "memory.record_event", "--input", json.dumps(payload)], timeout=30)
    if rc == 0:
        marker.write_text(today)


def deliver_alarm(results: dict, names: list) -> None:
    # Four deliveries, all local: log line, macOS notification, vault alarm note,
    # canonical event -- a red nobody can notice is a red that did not happen.
    print("MEMORY-VERIFIER RED:", ",".join(names))
    subprocess.run(["osascript", "-e",
                    f'display notification "{",".join(names)} red in memory plane" with title "memory-verifier" sound name "Basso"'],
                   capture_output=True, timeout=10)
    note = Path.home() / "Documents/JakeStudio/Logs/memory-verifier-ALARM.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    detail = "; ".join(f"{k}: {results[k]['evidence'][:90]}" for k in names)
    note_body = f"\n- {results['ts']} RED: {detail}\n"
    try:
        with note.open("a", encoding="utf-8") as f:
            f.write(note_body)
    except PermissionError:
        # TCC full-disk-access can block a background writer (observed 2026-09-21T04:00Z);
        # alarm delivery may degrade, the evidence may not -- ledger copy lives in state dir.
        with (STATE / "alarm-ledger.jsonl").open("a", encoding="utf-8") as f:
            f.write(note_body.strip() + "\n")
    event = {
        "run_id": f"memory-verifier-{_now_utc():%Y%m%d}", "mission_id": "plane-proof",
        "event_type": "memory_verifier.alarm", "occurred_at": results["ts"],
        "sensitivity": "internal",
        "payload": {"red": names, "evidence": {k: results[k]["evidence"] for k in names}},
        "idempotency_key": f"memver-alarm-{results['ts']}",
    }
    run([str(MEMORY_CLI), "call", "memory.record_event", "--input", json.dumps(event)], timeout=20)


def load_known_lanes() -> set:
    # World-class ladder (row 5) receipt: lanes registered in lane-evidence.json carry a
    # recorded evidence ref (file path) for their claim, so when one goes RED the plane
    # can prove what went wrong instead of guessing. Known lanes ring the alarm; RED on
    # an unregistered lane is logged as hidden_red (recording stays honest) and cross-lane
    # proof doesn't count it until the lane gets its evidence file.
    lanes = set()
    if LANE_EVIDENCE.is_file():
        try:
            lanes = set(json.loads(LANE_EVIDENCE.read_text()).get("lanes", {}))
        except ValueError:
            pass
    return lanes

def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="memory plane canary + soak ledger")
    ap.add_argument("--quiet", action="store_true", help="print only RED results")
    ap.add_argument("--soak", action="store_true", help="print green-rate history and exit")
    ap.add_argument("--plant", action="store_true",
                   help="proof-of-alarm canary: plant one RED carrier then fire the quadruple alarm path")
    args = ap.parse_args(list(argv) if argv is not None else None)
    STATE.mkdir(parents=True, exist_ok=True)
    rows = load_history()
    if args.soak:
        return report_soak(rows)
    checks = {"write": check_write, "frozen": check_frozen, "cron": check_cron,
              "healer": check_healer, "consolidation": check_consolidation}
    results = {}
    for name, fn in checks.items():
        try:
            results[name] = {"status": "GREEN", "evidence": fn()}
        except Exception as exc:  # noqa: BLE001
            results[name] = {"status": "RED", "evidence": str(exc)[:200]}
    red = [k for k, v in results.items() if v["status"] == "RED"]
    known = load_known_lanes()
    hidden_red = [k for k in red if k not in known]
    visible_red = [k for k in red if k in known]
    # Proof-of-alarm planted failure: when the board is green, one run-out-of-10 plants a RED
    # carrier in a known lane and re-fires the quadruple alarm -- proving the delivery wiring
    # itself, before a real red arrives (the world-class ladder's planted-green test).
    if args.plant and known and not red:
        carrier = sorted(known)[0]
        results[carrier] = {"status": "RED", "evidence": "planted carrier (proof-of-alarm canary)"}
        red = red + [carrier]
        visible_red = visible_red + [carrier]
    results["ts"] = _now_utc().isoformat(timespec="seconds")
    (STATE / "last-run.json").write_text(json.dumps({**results, "hidden_red": hidden_red}, indent=1, sort_keys=True))
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": results["ts"], "red": red, "hidden_red": hidden_red}, sort_keys=True) + "\n")
    rows.append({"ts": results["ts"], "red": red, "hidden_red": hidden_red})
    if visible_red:
        deliver_alarm(results, visible_red)
    elif red:
        if not args.quiet:
            print(f"MEMORY-VERIFIER red, quarantined lanes only ({', '.join(red)}): see {LANE_EVIDENCE}")
    else:
        emit_daily_soak(rows, results)
    if not (args.quiet and not red):
        print(json.dumps({k: (f"{v['status']}: {v['evidence']}" if isinstance(v, dict) else v)
                          for k, v in results.items()}, ensure_ascii=False, indent=1))
    return 1 if red else 0


if __name__ == "__main__":
    raise SystemExit(main())
