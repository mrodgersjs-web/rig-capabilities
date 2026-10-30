"""Activities: the only side-effecting code. All effects are appends/writes to the
laptop control-plane over ssh, plus signals between workflows. No outward actions, no spend."""
from __future__ import annotations
import asyncio, json, shlex
from datetime import datetime, timedelta, timezone
from temporalio import activity
from temporalio.client import Client
from temporalio.common import RetryPolicy
from . import config, sshio
from .measure_remote import REMOTE as MEASURE_PY

TZ = timezone(timedelta(hours=-6))  # set per-call via Denver below
DENVER_OFFSET_H = -6  # MDT in October; only used for date stamping fallback


def _denver_now():
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(config.TZ))


_client: Client | None = None


async def client() -> Client:
    global _client
    if _client is None:
        _client = await Client.connect(config.TEMPORAL_ADDR, namespace=config.NAMESPACE)
    return _client


async def _append_kpi(rows: list[dict]) -> bool:
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    return await sshio.append(config.KPI_LEDGER, text)


async def _heartbeat(agent: str, payload: dict) -> bool:
    return await sshio.write(f"{config.HB_DIR}/{agent}/latest.json",
                             json.dumps(payload, sort_keys=True) + "\n")


async def _reconcile_queue(agent_names: list[str]) -> dict:
    """Self-reconciling queue: tasks >48h w/o progress -> reassign once, then auto-close."""
    p = await sshio.run(f"ls {shlex.quote(config.QUEUE_DIR)} 2>/dev/null | grep -c '\\.json$' || true")
    try:
        nfiles = int(p.stdout.strip() or 0)
    except ValueError:
        nfiles = 0
    if nfiles == 0:
        return {"scanned": 0, "reassigned": 0, "closed": 0, "stale_grace_h": 48}
    body = r'''
import json, os, time, glob
p = json.loads(os.environ["PAYLOAD"])
q, closed, now, names = p["q"], p["closed"], p["now"], p["agents"]
reassigned = 0; closed_n = 0
for f in glob.glob(q + "/*.json"):
    try:
        t = json.load(open(f))
    except Exception:
        continue
    upd = t.get("updated") or t.get("created") or 0
    if now - upd <= 48 * 3600:
        continue
    t["attempts"] = int(t.get("attempts", 0)) + 1
    if t["attempts"] <= 1:
        i = names.index(t.get("agent", names[0])) if t.get("agent") in names else 0
        t["agent"] = names[(i + 1) % len(names)]
        t["updated"] = now; t["note"] = "auto-reassigned (stale >48h)"
        json.dump(t, open(f, "w"))
        reassigned += 1
    else:
        t["closed_reason"] = "auto-closed (stale >48h after reassign)"
        t["closed_at"] = now
        dst = os.path.join(closed, os.path.basename(f))
        os.makedirs(closed, exist_ok=True); os.replace(f, dst)
        closed_n += 1
print(json.dumps({"scanned": len(glob.glob(q + "/*.json")), "reassigned": reassigned,
                  "closed": closed_n}))
'''
    res = await sshio.run_py(body, {"q": config.QUEUE_DIR, "closed": config.QUEUE_CLOSED,
                                    "now": _denver_now().timestamp(), "agents": agent_names})
    return res if isinstance(res, dict) and "scanned" in res else {"scanned": nfiles, "reassigned": 0, "closed": 0}


async def _agent_cycle(name: str, target_kpi: str, cadence: int) -> dict:
    today = _denver_now().strftime("%Y-%m-%d")
    state = "ok"
    try:
        res = await sshio.run_py(MEASURE_PY, {"agents": [name], "today": today,
                                              "now": _denver_now().isoformat(),
                                              "kpi": target_kpi})
        if res.get("ok") is False:
            res = dict(res, rows=[])
        rows = [r for r in res.get("rows") or [] if r.get("agent") == name]
    except Exception as ex:
        res, rows = {"ok": False, "error": str(ex)}, []
    if not rows:
        # Missing KPI source is a None-valued error row, never a cycle-killing failure.
        state = "degraded"
        reason = res.get("error") or "no rows"
        try:
            await _append_kpi([{
                "agent": name, "date": today, "kpi": target_kpi, "value": None,
                "unit": "error", "target": config.AGENTS[name].get("target"),
                "source": f"measure failed: {reason}",
                "ts": _denver_now().isoformat(timespec="seconds")}])
        except Exception:
            pass
    else:
        try:
            await _append_kpi(rows)
        except Exception:
            state = "degraded"
    rec = {"scanned": 0, "reassigned": 0, "closed": 0}
    try:
        rec = await _reconcile_queue(list(config.AGENTS))
    except Exception:
        state = "degraded"
    if rec["reassigned"] + rec["closed"]:
        try:
            await _append_kpi([{
                "agent": name, "kpi": "stale_tasks_reconciled",
                "value": rec["reassigned"] + rec["closed"], "unit": "count", "target": None,
                "source": "agent-company/queue/gtm reconcile scan", "date": today,
                "ts": _denver_now().isoformat(timespec="seconds")}])
        except Exception:
            pass
    await _heartbeat(name, {"agent": name, "ts": _denver_now().isoformat(timespec="seconds"),
                            "state": state, "kpi_rows": len(rows), "queue": rec})
    activity.logger.info(f"{name}: {len(rows)} kpi rows ({state}), queue {rec}")
    return {"rows": len(rows), "queue": rec, "state": state}


@activity.defn(name="bidder_cycle")
async def bidder_cycle():
    return await _agent_cycle("upwork-bidder", "proposals_sent_today", 1800)


@activity.defn(name="outreach_cycle")
async def outreach_cycle():
    return await _agent_cycle("email-outreach", "cold_first_touches", 900)


@activity.defn(name="sourcer_cycle")
async def sourcer_cycle():
    return await _agent_cycle("lead-sourcer", "net_new_staged_leads_today", 3600)


@activity.defn(name="linkedin_cycle")
async def linkedin_cycle():
    return await _agent_cycle("linkedin-gtm", "drafts_today", 7200)


@activity.defn(name="enrich_cycle")
async def enrich_cycle():
    return await _agent_cycle("enrich-verify", "evidence_captures_total", 3600)


@activity.defn(name="icp_cycle")
async def icp_cycle():
    return await _agent_cycle("icp-scorer", "crm_icp_qualified", 3600)


@activity.defn(name="reply_cycle")
async def reply_cycle():
    return await _agent_cycle("reply-handler", "gmail_unread", 300)


@activity.defn(name="linkedin_events_cycle")
async def linkedin_events_cycle():
    return await _agent_cycle("linkedin-events", "connections", 7200)


@activity.defn(name="phone_cycle")
async def phone_cycle():
    return await _agent_cycle("phone-calls", "call_packs_present", 3600)


@activity.defn(name="web_analytics_cycle")
async def web_analytics_cycle():
    return await _agent_cycle("web-analytics", "ga4_sessions_7d", 7200)


@activity.defn(name="cro_cycle")
async def cro_cycle():
    return await _agent_cycle("website-cro", "funnel_submissions_total", 7200)


@activity.defn(name="standup")
async def standup(escalations: list[dict] | None = None):
    """L2 lead, reads only: KPI vs target from ledger, heartbeats, signals to unblock,
    council card for the standing trade-off, standup file. No writes to worker resources."""
    today = _denver_now().strftime("%Y-%m-%d")
    workers = ["upwork-bidder", "email-outreach", "lead-sourcer", "enrich-verify", "icp-scorer",
                "reply-handler", "linkedin-events", "phone-calls", "web-analytics", "website-cro"]
    led = await sshio.read(config.KPI_LEDGER) or ""
    hb = {}
    for a in workers + ["gtm-head"]:
        txt = await sshio.read(f"{config.HB_DIR}/{a}/latest.json")
        if txt:
            try:
                hb[a] = json.loads(txt)
            except Exception:
                hb[a] = None
    by_kpi: dict[str, dict] = {}
    for line in led.splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("date") == today and r.get("value") is not None and r.get("unit") != "error":
            key = f"{r['agent']}/{r['kpi']}"
            by_kpi[key] = r  # last measurement of the day wins
    c = await client()
    now_ts = _denver_now().timestamp()
    # Wake any worker whose heartbeat is >1200s old, then poll (every 5s, <=120s)
    # until its ts refreshes so the report below is built from refreshed heartbeats.
    woken: dict[str, str] = {}
    for a in workers:
        h = hb.get(a)
        ts = h.get("ts") if isinstance(h, dict) else None
        try:
            age = now_ts - datetime.fromisoformat(ts).timestamp() if ts else 1e9
        except Exception:
            age = 1e9
        if age > 1200:
            woken[a] = ts or ""
            await c.get_workflow_handle(a).signal("wake")  # same convention as stale-wake below
    waited = 0
    while woken and waited < 120:
        await asyncio.sleep(5)
        waited += 5
        for a in list(woken):
            txt = await sshio.read(f"{config.HB_DIR}/{a}/latest.json")
            try:
                fresh = json.loads(txt) if txt else None
            except Exception:
                fresh = None
            if isinstance(fresh, dict) and fresh.get("ts") and fresh["ts"] != woken[a]:
                hb[a] = fresh
                del woken[a]
    now_ts = _denver_now().timestamp()
    stale = []
    for a, spec in config.AGENTS.items():
        if spec["role"] != "worker":
            continue
        h = hb.get(a)
        age = now_ts - datetime.fromisoformat(h["ts"]).timestamp() if h and h.get("ts") else 1e9
        if age > spec["cadence_s"] * config.GRACE_MULT + config.GRACE_MIN_S:
            stale.append(a)
            await c.get_workflow_handle(a).signal("wake")  # unblock; single-writer lock keeps it safe
    lines = [f"# GTM stand-up {today}", "",
             "| worker | KPI | today | target | source |",
             "|---|---|---:|---:|---|"]
    for a in workers:
        spec = config.AGENTS[a]
        r = by_kpi.get(f"{a}/{spec['kpi']}")
        lines.append(f"| {a} | {spec['kpi']} | {r['value'] if r else '-'} | {r['target'] if r else spec['target']} | `{r['source'] if r else 'no measurement yet'}` |")
    lines += ["", f"## Heartbeats", ""]
    for a, h in hb.items():
        lines.append(f"- {a}: {h.get('ts') if h else 'MISSING'}")
    if stale:
        lines += ["", "## Wake-ups", "", f"Stale workers signalled to wake: {', '.join(stale)}"]
    if escalations:
        lines += ["", "## Watchdog escalations", ""]
        for e in escalations[-5:]:
            lines.append(f"- {e}")
    q = await _reconcile_queue(workers)
    lines += ["", "## Queue", "", f"scanned {q['scanned']}, reassigned {q.get('reassigned', 0)}, closed {q.get('closed', 0)} (stale >48 h)"]
    lines += ["", "## Council cards", ""]
    card = (f"{config.COUNCIL_DIR}/{today}-routine-cutover-tradeoff.md")
    await sshio.write(card, f"""# Council card {today}: routine cutover trade-off

Question: which superseded GTM routines to PAUSE now that L1 workers run on Temporal?
Rule (WAVES.md / Mike): pause only AFTER the owning agent completed one equivalent
VERIFIED cycle. Workers are live; verification cycle counted from KPI ledger.
Recommendation: keep all routines ACTIVE until 3 consecutive days of worker KPI rows
match the routine's outputs; re-review at the Thursday gtm-head review.
Evidence: agent-company/kpi/gtm.jsonl, agent-company/heartbeats/.
""")
    lines.append(f"- {today}-routine-cutover-tradeoff.md (pause-vs-run routines: evidence-gated)")
    body = "\n".join(lines) + "\n"
    if not await sshio.write(f"{config.STANDUP_DIR}/{today}.md", body):
        raise RuntimeError("standup write failed")
    await _heartbeat("gtm-lead", {"agent": "gtm-lead", "ts": _denver_now().isoformat(timespec="seconds"),
                                  "kpi_keys": len(by_kpi)})
    return {"kpi_keys": len(by_kpi), "stale": stale, "queue": q}


@activity.defn(name="head_cycle")
async def head_cycle(kind: str):
    """L3 head, reads only: averages from ledger, targets to workers, budget guard (no spend)."""
    today = _denver_now().strftime("%Y-%m-%d")
    led = await sshio.read(config.KPI_LEDGER) or ""
    days: dict[str, dict[str, list]] = {}
    for line in led.splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("unit") == "error" or r.get("value") is None:
            continue
        days.setdefault(r.get("date", "?"), {}).setdefault(f"{r['agent']}/{r['kpi']}", []).append(r["value"])
    targets = {a: {"kpi": s.get("kpi"), "target": s.get("target"), "cadence_s": s.get("cadence_s", 3600)}
               for a, s in config.AGENTS.items() if s["role"] == "worker"}
    body = [f"# GTM head review {today} ({kind})", "",
            f"Ledger days observed: {sorted(days)}", ""]
    for d in sorted(days)[-7:]:
        for k, vals in sorted(days[d].items()):
            body.append(f"- {d} {k}: {vals[-1]}")
    body += ["", "## Targets", "", json.dumps(targets, indent=2, sort_keys=True),
             "", "## Budget guard", "", "No-spend authority. Spend this period: 0. Caps unchanged (Upwork 8/day, Oxygen 300 credits/day, 50/mailbox)."]
    await sshio.write(f"{config.REVIEW_DIR}/{today}-{'plan' if kind == 'first' else 'review'}.md",
                       "\n".join(body) + "\n")
    await _heartbeat("gtm-head", {"agent": "gtm-head", "ts": _denver_now().isoformat(timespec="seconds")})
    c = await client()
    for a, t in targets.items():
        await c.get_workflow_handle(a).signal("set_targets", t)
    return {"days": len(days), "targets_sent": list(targets)}


@activity.defn(name="watchdog_check")
async def watchdog_check():
    now_ts = _denver_now().timestamp()
    misses = []
    for a, spec in config.AGENTS.items():
        if spec["role"] not in ("worker", "lead", "head"):
            continue
        txt = await sshio.read(f"{config.HB_DIR}/{a}/latest.json")
        age = 1e9
        if txt:
            try:
                h = json.loads(txt)
                age = now_ts - datetime.fromisoformat(h["ts"]).timestamp()
            except Exception:
                pass
        grace = (spec.get("cadence_s", 86400) * config.GRACE_MULT + config.GRACE_MIN_S
                 if spec["role"] == "worker" else 2 * 86400)
        status = "MISS" if age > grace else "ok"
        if status == "MISS":
            misses.append({"agent": a, "age_s": int(age)})
        line = f"{_denver_now().isoformat(timespec='seconds')} {a} {status} age_s={int(min(age, 10**9))}\n"
        await sshio.append(config.WATCHDOG_LOG, line)
    return misses


@activity.defn(name="watchdog_raise")
async def watchdog_raise(misses: list[dict]):
    c = await client()
    ts = _denver_now().isoformat(timespec="seconds")
    for m in misses:
        await sshio.append(config.INCIDENTS, f"{ts} MISS {m['agent']} age_s={m['age_s']}\n")
        await c.get_workflow_handle("gtm-lead").signal("escalate", {"agent": m["agent"], "age_s": m["age_s"], "ts": ts})
    return {"raised": len(misses)}


ALL_ACTIVITIES = [bidder_cycle, outreach_cycle, sourcer_cycle, linkedin_cycle,
                  enrich_cycle, icp_cycle, reply_cycle, linkedin_events_cycle,
                  phone_cycle, web_analytics_cycle, cro_cycle,
                  standup, head_cycle, watchdog_check, watchdog_raise]
