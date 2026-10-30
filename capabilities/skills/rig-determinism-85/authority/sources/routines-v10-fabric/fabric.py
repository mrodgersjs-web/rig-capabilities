#!/usr/bin/env python3
"""Routine fabric for Aside routines & scheduling (routines-v10).

Live ops layer over ~/.aside/u/0/state.db:
  census        inventory + stale pins + next fires + collision summary
  collisions    co-fire collision groups over a window
  check-daemon  compare expander next_fire with the daemon's next_run_at (acceptance)
  stagger       spread colliding minute-of-hour slots (dry-run; --apply writes)
  unpause       journaled resume of paused routines (dry-run; --apply writes)
  repin         self-healing re-pin of stale/missing next_run_at
  mesh          fleet-wide routine mesh registry (local + ssh nodes, read-only)
  client-ops    client ops backbone: register/status per-client routine bundles
  loadtest      provision/run/judge 10x volume load windows
  undo          reverse the last journaled fabric write

All writes are journaled to ~/.rig/state/routine-fabric/journal.jsonl.
Nothing here sends anything outward; load-test fires are read-only sessions on
the local rig-fleet-blackwell-glm-bg model lane.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import string
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fabricdb
import metric_reader
import rrule
from rrule import TZ, UTC

DEVICE_ID = "5250853b-5823-4249-a922-efb76ff02df9"  # this laptop, per state.db
FLEET_NODES = ["rig256gb", "rig96gb", "rig48gb", "rig36gb", "rig28gb"]
STATE_DIR = fabricdb.STATE_DIR
MESH_PATH = STATE_DIR / "mesh.json"
CLIENTS_PATH = STATE_DIR / "client-ops.json"
NOW = lambda: datetime.now(TZ)


def _iso(t): return rrule.to_iso_utc(t)


def active_routines(conn):
    return fabricdb.rows(
        conn,
        "SELECT id, name, rrule, status, next_run_at, paused_at, session_config "
        "FROM routines WHERE deleted_at IS NULL AND status='active'")


# ---------------- census ----------------

def cmd_census(args):
    conn = fabricdb.connect(ro=True)
    counts = fabricdb.one(conn,
        "SELECT status, COUNT(*) c FROM routines WHERE deleted_at IS NULL GROUP BY status")
    now = NOW()
    rows = active_routines(conn)
    stale, exhausted, soon = [], [], []
    for r in rows:
        try:
            nf = rrule.next_fire(r["rrule"], now)
        except rrule.RuleError as e:
            stale.append({**r, "error": str(e)})
            continue
        if nf is None:
            exhausted.append(r)
            continue
        stored = r["next_run_at"]
        if stored is None:
            stale.append({**r, "reason": "next_run_at NULL", "expander_next": _iso(nf)})
        else:
            try:
                stored_t = rrule.from_iso_utc(stored)
            except ValueError:
                stored_t = None
            if stored_t is not None and stored_t < now.astimezone(UTC) - timedelta(seconds=120):
                stale.append({**r, "reason": f"next_run_at stale ({stored})",
                              "expander_next": _iso(nf)})
        soon.append((nf, r["id"], r["name"]))
    coll = _collisions(conn, hours=getattr(args, "hours", 24.0), rows=rows, now=now)
    out = {
        "now": now.isoformat(timespec="seconds"),
        "status_counts": counts,
        "active": len(rows),
        "stale_pins": [{"id": s["id"], "name": s["name"],
                        "reason": s.get("reason", s.get("error")),
                        "expander_next": s.get("expander_next")} for s in stale],
        "exhausted_no_future_fire": [e["id"] for e in exhausted],
        "collisions_next_24h": {"groups": len(coll),
                                "routines_involved": len({rid for g in coll for rid in g["ids"]})},
        "next_fires": [{"at": _iso(t), "id": i, "name": n} for t, i, n in sorted(soon)[:15]],
    }
    if getattr(args, "json", False):
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"active={out['active']} counts={counts}")
        print(f"stale pins: {len(stale)}  exhausted: {len(exhausted)}  "
              f"collision groups next 24h: {out['collisions_next_24h']}")
        for s in out["stale_pins"]:
            print(f"  STALE {s['id']} {s['reason']} -> expander {s['expander_next']}")
        for t, i, n in sorted(soon)[:10]:
            print(f"  next {_iso(t)} {i} {n[:50]}")
    conn.close()
    return 0


# ---------------- collisions ----------------

def _occ_map(rows, now, hours):
    end = now + timedelta(hours=hours)
    occ = {}
    for r in rows:
        times = list(rrule.between(r["rrule"], now, end))
        occ[r["id"]] = {"name": r["name"], "times": times, "rrule": r["rrule"]}
    return occ


def _collisions(conn, hours, rows=None, now=None):
    now = now or NOW()
    rows = rows if rows is not None else active_routines(conn)
    occ = _occ_map(rows, now, hours)
    by_time = defaultdict(set)
    for rid, info in occ.items():
        for t in info["times"]:
            by_time[t].add(rid)
    groups = [{"at": _iso(t), "ids": sorted(ids)} for t, ids in by_time.items() if len(ids) > 1]
    return sorted(groups, key=lambda g: g["at"])


def cmd_collisions(args):
    conn = fabricdb.connect(ro=True)
    groups = _collisions(conn, hours=args.hours)
    print(json.dumps({"window_hours": args.hours, "groups": groups}, indent=2))
    conn.close()
    return 0


# ---------------- check-daemon (expander acceptance) ----------------

def cmd_check_daemon(args):
    conn = fabricdb.connect(ro=True)
    now = NOW()
    ok = mismatch = skipped = 0
    bad = []
    for r in active_routines(conn):
        if not r["next_run_at"]:
            skipped += 1
            continue
        try:
            nf = rrule.next_fire(r["rrule"], now)
        except rrule.RuleError as e:
            bad.append({"id": r["id"], "err": str(e)})
            mismatch += 1
            continue
        stored = rrule.from_iso_utc(r["next_run_at"])
        delta = abs((nf.astimezone(UTC) - stored).total_seconds()) if nf else None
        if nf is not None and delta <= 90:
            ok += 1
        else:
            mismatch += 1
            bad.append({"id": r["id"], "name": r["name"][:40],
                        "daemon": r["next_run_at"], "expander": _iso(nf) if nf else None})
    print(json.dumps({"ok": ok, "mismatch": mismatch, "skipped_null": skipped,
                      "bad": bad}, indent=2))
    conn.close()
    return 0 if mismatch == 0 else 1


# ---------------- stagger ----------------

def _feasible_deltas(info, max_shift):
    """Deltas that keep every shifted minute inside [0,59]."""
    if "BYMINUTE=" in info["rrule"].split("RRULE:")[-1]:
        vals = [int(x) for x in
                __import__("re").search(r"BYMINUTE=([0-9,]+)", info["rrule"]).group(1).split(",")]
    else:
        _, parts = rrule.parse(info["rrule"])
        vals = [rrule.parse(info["rrule"])[0].minute]
    out = []
    for d in list(range(1, max_shift + 1)) + list(range(-1, -max_shift - 1, -1)):
        if all(0 <= v + d <= 59 for v in vals):
            out.append(d)
    return out


def cmd_stagger(args):
    conn = fabricdb.connect(ro=True)
    now = NOW()
    rows = active_routines(conn)
    conn.close()
    occ = _occ_map(rows, now, args.hours)
    taken = defaultdict(set)
    for rid, info in occ.items():
        for t in info["times"]:
            taken[t].add(rid)
    conflicts = {rid: sum(len(taken[t]) - 1 for t in info["times"])
                 for rid, info in occ.items()}
    before = sum(1 for ids in taken.values() if len(ids) > 1)
    order = sorted(occ, key=lambda rid: (-conflicts[rid], rid))
    moves = []
    for rid in order:
        actual = sum(len(taken[t]) - 1 for t in occ[rid]["times"])
        if actual == 0:
            continue
        info = occ[rid]
        deltas = _feasible_deltas(info, args.max_shift)
        placed = False
        for d in deltas:
            new_times = [t + timedelta(minutes=d) for t in info["times"]]
            if all(len(taken[t] - {rid}) == 0 for t in new_times):
                for t in info["times"]:
                    taken[t].discard(rid)
                for t in new_times:
                    taken[t].add(rid)
                info["times"] = new_times
                info["delta"] = d
                moves.append({"id": rid, "name": info["name"][:48], "delta_min": d,
                              "conflicts_before": conflicts[rid]})
                placed = True
                break
        if not placed:
            moves.append({"id": rid, "name": info["name"][:48], "delta_min": None,
                          "conflicts_before": conflicts[rid],
                          "note": "no feasible delta within cap"})
    after = sum(1 for ids in taken.values() if len(ids) > 1)
    print(json.dumps({"window_hours": args.hours,
                      "collision_groups_before": before,
                      "collision_groups_after": after,
                      "moves": moves}, indent=2))
    if args.apply:
        conn = fabricdb.connect()
        for m in moves:
            if m["delta_min"]:
                info = occ[m["id"]]
                new_rule = rrule.shift(info["rrule"], m["delta_min"])
                try:
                    nf = rrule.next_fire(new_rule, now)
                except rrule.RuleError:
                    nf = None
                fabricdb.update_routine(
                    conn, m["id"],
                    {"rrule": new_rule, "updated_at": int(time.time()),
                     **({"next_run_at": _iso(nf)} if nf else {})},
                    f"stagger {m['delta_min']}min (collision-free slot)")
        conn.close()
        print(f"applied {len([m for m in moves if m['delta_min']])} shifts (journaled)")
    return 0


# ---------------- unpause ----------------

PAUSED_REVENUE_9 = [
    ("YoLilr9eq0DnLFkC", "LI weekly review"),
    ("z8ntkEvrsySqWtPx", "GTM 24/7 war-room driver"),
    ("9Cxab7KMSYNYFWAk", "LI inbound sweep + owner analytics"),
    ("YjLMbKudbh7eBOMv", "GTM Apollo credit renewal enrich"),
    ("QKDUsQxVNCeFZdHS", "GTM Apollo enrich confirmation gate"),
    ("FPquwovjYkgtUg2i", "LI next-week batch (stage only)"),
    ("xf8GaHq3MqV5GchG", "LI weekly recommendations (drafts only)"),
    ("jx1Dl70qirjCDV52", "LI monthly profile audit (read only)"),
    ("3e9tIm4d2ttq9S2O", "OXYGEN keep-alive watchdog"),
]


def cmd_unpause(args):
    ids = args.ids.split(",") if args.ids else [i for i, _ in PAUSED_REVENUE_9]
    conn = fabricdb.connect(ro=True)
    now = NOW()
    plan = []
    for rid in ids:
        r = fabricdb.get_routine(conn, rid)
        if r is None:
            plan.append({"id": rid, "action": "MISSING"})
            continue
        if r["deleted_at"]:
            plan.append({"id": rid, "action": "SKIP deleted", "name": r["name"][:50]})
            continue
        if r["status"] == "active" and not r["paused_at"]:
            plan.append({"id": rid, "action": "already live", "name": r["name"][:50],
                         "next_run_at": r["next_run_at"]})
            continue
        try:
            nf = rrule.next_fire(r["rrule"], now)
        except rrule.RuleError as e:
            plan.append({"id": rid, "action": f"SKIP bad rrule: {e}"})
            continue
        plan.append({"id": rid, "action": "UNPAUSE", "name": r["name"][:50],
                     "from_status": r["status"],
                     "next_fire": _iso(nf) if nf else "EXHAUSTED (no future occurrence)"})
    print(json.dumps(plan, indent=2))
    if args.apply:
        conn = fabricdb.connect()
        for p in plan:
            if p["action"] != "UNPAUSE":
                continue
            r = fabricdb.get_routine(conn, p["id"])
            try:
                nf = rrule.next_fire(r["rrule"], now)
            except rrule.RuleError:
                nf = None
            fabricdb.update_routine(
                conn, p["id"],
                {"status": "active", "paused_at": None,
                 "updated_at": int(time.time()),
                 **({"next_run_at": _iso(nf)} if nf else {})},
                "unpause per routines-v10 v8 milestone (revenue routines live)")
            print(f"UNPAUSED {p['id']} {p['name']}")
        conn.close()
    return 0


# ---------------- repin (self-healing) ----------------

def cmd_repin(args):
    conn = fabricdb.connect(ro=True)
    now = NOW()
    now_utc = now.astimezone(UTC)
    healed, exhausted, healthy = [], [], 0
    for r in active_routines(conn):
        try:
            nf = rrule.next_fire(r["rrule"], now)
        except rrule.RuleError as e:
            healed.append({"id": r["id"], "error": str(e)})
            continue
        if nf is None:
            exhausted.append(r["id"])
            continue
        stored = r["next_run_at"]
        stale = stored is None
        if stored is not None:
            try:
                stale = rrule.from_iso_utc(stored) < now_utc - timedelta(seconds=120)
            except ValueError:
                stale = True
        if stale:
            healed.append({"id": r["id"], "name": r["name"][:48],
                           "was": stored, "repin": _iso(nf)})
        else:
            healthy += 1
    print(json.dumps({"healthy": healthy, "to_repin": healed,
                      "exhausted_no_future_fire": exhausted}, indent=2))
    if args.apply:
        conn = fabricdb.connect()
        for h in healed:
            if "repin" not in h:
                continue
            fabricdb.update_routine(conn, h["id"],
                                    {"next_run_at": h["repin"], "updated_at": int(time.time())},
                                    "self-healing re-pin (stale/missing next_run_at)")
        conn.close()
        print(f"repinned {len([h for h in healed if 'repin' in h])} routines (journaled)")
    return 0


# ---------------- mesh ----------------

def cmd_mesh(args):
    conn = fabricdb.connect(ro=True)
    now = NOW()
    local_rows = []
    for r in fabricdb.rows(conn,
            "SELECT id, name, status, next_run_at, paused_at FROM routines "
            "WHERE deleted_at IS NULL AND status='active'"):
        last = fabricdb.one(conn,
            "SELECT MAX(created_at) m, COUNT(*) c FROM sessions "
            "WHERE routine_id=?", (r["id"],))
        last_fire = datetime.fromtimestamp(last["m"], timezone.utc).isoformat(timespec="seconds") if last["m"] else None
        gap_min = (time.time() - last["m"]) / 60 if last["m"] else None
        local_rows.append({"id": r["id"], "name": r["name"][:60],
                           "next_run_at": r["next_run_at"], "last_fire_utc": last_fire,
                           "fires_all_time": last["c"], "minutes_since_last_fire": round(gap_min, 1) if gap_min else None})
    conn.close()
    nodes = [{"node": "rig128gb-local", "reachable": True, "aside_state": "live",
              "active_routines": len(local_rows)}]
    for host in FLEET_NODES:
        entry = {"node": host, "reachable": False}
        try:
            p = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", host,
                 "hostname; test -f ~/.aside/u/0/state.db && echo ASIDE_STATE_PRESENT || echo NO_ASIDE_STATE; uptime | tail -1"],
                capture_output=True, text=True, timeout=15)
            lines = [l.strip() for l in p.stdout.splitlines() if l.strip()]
            entry["reachable"] = p.returncode == 0
            entry["probe"] = lines
            entry["aside_state"] = ("live" if any("ASIDE_STATE_PRESENT" == l for l in lines)
                                    else "absent")
        except Exception as e:  # noqa: BLE001 - mesh must report, not crash
            entry["error"] = str(e)[:120]
        nodes.append(entry)
    out = {"collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "nodes": nodes, "local_routines": local_rows}
    if args.collect:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        MESH_PATH.write_text(json.dumps(out, indent=2, sort_keys=True))
        print(f"mesh written: {MESH_PATH}")
    print(json.dumps({"nodes": nodes}, indent=2))
    return 0


# ---------------- client-ops ----------------

def _load_clients():
    if CLIENTS_PATH.exists():
        return json.loads(CLIENTS_PATH.read_text())
    return {"clients": {}}


def cmd_client_ops(args):
    if args.action == "register":
        reg = _load_clients()
        prev_routines = (reg["clients"].get(args.client_id, {}).get("routines") or [])
        reg["clients"][args.client_id] = {
            "name": args.name or args.client_id,
            "registered_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sla": {"min_clean_rate_lcb95": args.min_clean_rate,
                    "max_gap_minutes": args.max_gap_minutes},
            "routines": prev_routines,
        }
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        CLIENTS_PATH.write_text(json.dumps(reg, indent=2, sort_keys=True))
        print(f"registered client bundle {args.client_id}")
        if args.provision:
            now = datetime.now(TZ)
            start = now + timedelta(minutes=2)
            if args.interval_min:
                rule = (f"DTSTART;TZID=America/Denver:{start.strftime('%Y%m%dT%H%M%S')}\n"
                        f"RRULE:FREQ=MINUTELY;INTERVAL={args.interval_min}")
            else:
                rule = (f"DTSTART;TZID=America/Denver:{start.strftime('%Y%m%dT%H%M%S')}\n"
                        "RRULE:FREQ=DAILY;INTERVAL=1")
            name = (f"CLIENT OPS · {reg['clients'][args.client_id]['name']} · "
                    + (f"{args.interval_min}min pilot check" if args.interval_min
                       else "daily fabric check"))
            existing = reg["clients"][args.client_id]["routines"]
            conn = fabricdb.connect()
            if existing:
                nf = rrule.next_fire(rule, datetime.now(timezone.utc))
                fabricdb.update_routine(conn, existing[0],
                    {"rrule": rule, "name": name,
                     "next_run_at": rrule.to_iso_utc(nf) if nf else None},
                    f"client-ops recadence bundle {args.client_id}")
                print(f"recadenced routine {existing[0]} for {args.client_id}")
                conn.close()
                return 0
            rid = _new_id()
            row = {
                "id": rid,
                "type": "standalone",
                "environment": "device",
                "device_id": DEVICE_ID,
                "name": name,
                "prompt": (
                    "Routine fabric client-ops check (routines-v10). Read-only pass: "
                    "1) report the current UTC time; 2) check that the client ops notes file "
                    f"~/.rig/state/routine-fabric/client-ops/{args.client_id}.md exists and "
                    "quote its last line or report MISSING; 3) reply with one status line "
                    "'CLIENT OPS <id> OK/MISSING <utc-time>'. Do not use tools that send, "
                    "post, purchase or modify anything. Do not message anyone."),
                "rrule": rule,
                "status": "active",
                "next_run_at": rrule.to_iso_utc(
                    rrule.next_fire(rule, datetime.now(timezone.utc))),
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "metadata": json.dumps({"fabric": "client-ops", "client": args.client_id,
                                        "provisioned_by": "routines-v10"}),
                "session_config": json.dumps({
                    "model": {"provider": "rig-fleet-blackwell-glm-bg",
                              "modelId": "glm-5.3-flash-uncensored",
                              "thinkingLevel": "medium", "fastMode": False},
                    "harnessId": "v1", "permissionMode": "read-only",
                    "notificationsEnabled": False, "strictModelSelection": True}),
            }
            conn = fabricdb.connect()
            fabricdb.insert_routine(conn, row, f"client-ops provision bundle {args.client_id}")
            reg["clients"][args.client_id]["routines"].append(rid)
            CLIENTS_PATH.write_text(json.dumps(reg, indent=2, sort_keys=True))
            print(f"provisioned routine {rid} for {args.client_id}")
            conn.close()
    elif args.action == "status":
        reg = _load_clients()
        out = {}
        conn = fabricdb.connect(ro=True)
        now = NOW()
        for cid, c in reg["clients"].items():
            rids = c["routines"]
            if not rids:
                out[cid] = {"verdict": "FAIL", "reason": "no routines in bundle"}
                continue
            ph = ",".join("?" for _ in rids)
            end = time.time()
            start = end - 86400
            fires = fabricdb.rows(conn,
                f"SELECT status, COUNT(*) c FROM sessions WHERE routine_id IN ({ph}) "
                "AND created_at >= ? AND created_at < ? GROUP BY status",
                (*rids, int(start), int(end)))
            total = sum(r["c"] for r in fires)
            clean = next((r["c"] for r in fires if r["status"] == "idle"), 0)
            lcb = metric_reader.clopper_pearson_lcb(clean, total) if total else 0.0
            last = fabricdb.one(conn,
                f"SELECT MAX(created_at) m FROM sessions WHERE routine_id IN ({ph})", rids)
            gap = (time.time() - last["m"]) / 60 if last["m"] else None
            sla = c["sla"]
            ok_rate = (total > 0 and lcb >= sla["min_clean_rate_lcb95"])
            ok_gap = (gap is not None and gap <= sla["max_gap_minutes"])
            out[cid] = {
                "name": c["name"], "routines": rids, "fires_24h": total, "clean_24h": clean,
                "clean_rate_lcb95": round(lcb, 4), "minutes_since_last_fire": round(gap, 1) if gap else None,
                "sla": sla,
                "verdict": "PASS" if (ok_rate and ok_gap) else "FAIL",
                "fails": ([] if ok_rate else ["clean-rate LCB below SLA or zero fires"])
                        + ([] if ok_gap else ["no fire within max_gap_minutes"]),
            }
        conn.close()
        print(json.dumps(out, indent=2, sort_keys=True))
    return 0


# ---------------- loadtest ----------------

def _new_id(n=16):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(n))


def _loadtest_ids(label: str | None = None):
    """Fabric loadtest routine ids. The daemon rewrites routine metadata on
    adoption (keeps only memoryPath), so cohorts are persisted at prepare time."""
    ids: list[str] = []
    for f in sorted(STATE_DIR.glob("loadtest-*-ids.json")):
        if label and f"loadtest-{label}-ids" not in f.name:
            continue
        ids.extend(json.loads(f.read_text()))
    if not ids:
        conn = fabricdb.connect(ro=True)
        ids = [r["id"] for r in fabricdb.rows(conn,
            "SELECT id FROM routines WHERE metadata LIKE '%\"fabric\": \"loadtest\"%'")]
        conn.close()
    return ids


def cmd_loadtest(args):
    if args.action == "prepare":
        conn = fabricdb.connect()
        start = datetime.now(TZ) + timedelta(minutes=args.start_in)
        created = []
        for i in range(args.routines):
            rid = _new_id()
            row = {
                "id": rid,
                "type": "standalone",
                "environment": "device",
                "device_id": DEVICE_ID,
                "name": f"FABRIC LOADTEST · {args.label} · {i + 1}/{args.routines}",
                "prompt": (f"Routine fabric scheduled load test ({args.label}). "
                           f"Reply with exactly: FIRE OK {rid} — then stop. "
                           "Do not use tools. Do not send or write anything anywhere."),
                "rrule": (f"DTSTART;TZID=America/Denver:{start.strftime('%Y%m%dT%H%M%S')}\n"
                          f"RRULE:FREQ=MINUTELY;INTERVAL=1;COUNT={args.fires}"),
                "status": "active",
                "next_run_at": rrule.to_iso_utc(
                    rrule.next_fire(
                        f"DTSTART;TZID=America/Denver:{start.strftime('%Y%m%dT%H%M%S')}\n"
                        f"RRULE:FREQ=MINUTELY;INTERVAL=1;COUNT={args.fires}",
                        datetime.now(timezone.utc))),
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "metadata": json.dumps({"fabric": "loadtest", "label": args.label,
                                        "provisioned_by": "routines-v10"}),
                "session_config": json.dumps({
                    "model": {"provider": "rig-fleet-blackwell-glm-bg",
                              "modelId": "glm-5.3-flash-uncensored",
                              "thinkingLevel": "medium", "fastMode": False},
                    "harnessId": "v1", "permissionMode": "read-only",
                    "notificationsEnabled": False, "strictModelSelection": True}),
            }
            fabricdb.insert_routine(conn, row, f"loadtest {args.label} provision")
            created.append(rid)
        conn.close()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / f"loadtest-{args.label}-ids.json").write_text(json.dumps(created))
        print(json.dumps({"created": created, "routines": args.routines,
                          "fires_each": args.fires,
                          "planned_total_fires": args.routines * args.fires,
                          "window": f"{start.isoformat(timespec='minutes')} .. "
                                    f"{(start + timedelta(minutes=args.fires)).isoformat(timespec='minutes')}"}))
    elif args.action == "status":
        ids = _loadtest_ids(args.label)
        conn = fabricdb.connect(ro=True)
        ph = ",".join("?" for _ in ids) or "''"
        per = fabricdb.rows(conn,
            f"SELECT routine_id, status, COUNT(*) c FROM sessions "
            f"WHERE routine_id IN ({ph}) GROUP BY routine_id, status",
            ids)
        conn.close()
        print(json.dumps({"loadtest_routines": ids, "fires": per}, indent=2))
    return 0


# ---------------- undo ----------------

def cmd_keeper(args):
    """Periodic launchd entry: self-healing re-pin, then fleet mesh collect."""
    cmd_repin(argparse.Namespace(apply=True))
    cmd_mesh(argparse.Namespace(collect=True))


def cmd_undo(args):
    conn = fabricdb.connect()
    entry = fabricdb.undo_last(conn)
    conn.close()
    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


# ---------------- main ----------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("census")
    p.add_argument("--json", action="store_true")
    p.add_argument("--hours", type=float, default=24.0)
    p.set_defaults(fn=cmd_census)

    p = sub.add_parser("collisions")
    p.add_argument("--hours", type=float, default=24.0)
    p.set_defaults(fn=cmd_collisions)

    p = sub.add_parser("check-daemon")
    p.set_defaults(fn=cmd_check_daemon)

    p = sub.add_parser("stagger")
    p.add_argument("--hours", type=float, default=24.0)
    p.add_argument("--max-shift", type=int, default=45)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_stagger)

    p = sub.add_parser("unpause")
    p.add_argument("--ids", default=None)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_unpause)

    p = sub.add_parser("repin")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(fn=cmd_repin)

    p = sub.add_parser("keeper")
    p.set_defaults(fn=cmd_keeper)

    p = sub.add_parser("mesh")
    p.add_argument("--collect", action="store_true")
    p.set_defaults(fn=cmd_mesh)

    p = sub.add_parser("client-ops")
    p.add_argument("action", choices=["register", "status"])
    p.add_argument("client_id", nargs="?")
    p.add_argument("--name", default=None)
    p.add_argument("--interval-min", type=int, default=None)
    p.add_argument("--provision", action="store_true")
    p.add_argument("--min-clean-rate", type=float, default=0.8)
    p.add_argument("--max-gap-minutes", type=float, default=36 * 60)
    p.set_defaults(fn=cmd_client_ops)

    p = sub.add_parser("loadtest")
    p.add_argument("action", choices=["prepare", "status"])
    p.add_argument("--label", default="v6")
    p.add_argument("--routines", type=int, default=25)
    p.add_argument("--fires", type=int, default=24)
    p.add_argument("--start-in", type=int, default=2)
    p.set_defaults(fn=cmd_loadtest)

    p = sub.add_parser("undo")
    p.set_defaults(fn=cmd_undo)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
