"""KPI measurement: one script, executed on the laptop via sshio.run_py.
Every KPI row carries the real source query. Payload:
{"agents": [...], "today": "YYYY-MM-DD", "now": iso}
"""
from __future__ import annotations

REMOTE = r'''
import csv, glob, json, os, re
from datetime import datetime
p = json.loads(os.environ["PAYLOAD"]); today = p["today"]; agents = set(p["agents"])
CP = "/Users/rig128gb/.rig/live/control-plane"; GTM = CP + "/gtm"; AC = CP + "/agent-company"
rows = []
def emit(agent, kpi, value, unit, target, source):
    rows.append({"agent": agent, "kpi": kpi, "value": value, "unit": unit,
                 "target": target, "source": source, "date": today,
                 "ts": datetime.now().astimezone().isoformat(timespec="seconds")})
def missing(agent, kpi, reason):
    """Always-emit row: missing/unreadable source -> value None + reason, never silence."""
    emit(agent, kpi or p.get("kpi") or "measure_error", None, "error", None, "reason: " + str(reason)[:220])
def err(agent, src, e):
    missing(agent, None, "unreadable source " + src + ", " + repr(e)[:120])
def mday(f):
    return datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d")
def read(path):
    try:
        return open(path).read()
    except Exception:
        return ""
def num(v):
    m = re.search(r"\d[\d,]*", str(v).replace("_", ""))
    return int(m.group(0).replace(",", "")) if m else None
WAR = read(GTM + "/GTM-WAR-ROOM.md")

if "upwork-bidder" in agents:
    try:
        sent = won = 0
        with open(GTM + "/FREELANCE-PIPELINE.csv") as f:
            for r in csv.DictReader(f):
                st = (r.get("status") or "").strip().upper()
                # fix: compare the date part only (quoted fields and 'T' separators made
                # startswith(today) miss rows); status must be an exact SENT/SUBMITTED/WON
                dmdt = (r.get("date_mdt") or "").strip().replace("T", " ")
                if dmdt[:10] == today and st in ("SENT", "SUBMITTED"):
                    sent += 1
                if st == "WON":
                    won += 1
        m = re.findall(r"budget ([0-9.]+)/300", WAR)  # latest line wins
        emit("upwork-bidder", "proposals_sent_today", sent, "count", 8,
             "count date_mdt[:10]==today status in {SENT,SUBMITTED} gtm/FREELANCE-PIPELINE.csv")
        emit("upwork-bidder", "wins_total", won, "count", None,
             "count status==WON gtm/FREELANCE-PIPELINE.csv")
        emit("upwork-bidder", "connects_balance",
             round(300 - float(m[-1]), 3) if m else None, "connects", None,
             "300 minus latest regex 'budget X/300' gtm/GTM-WAR-ROOM.md")
    except Exception as e:
        err("upwork-bidder", "gtm/FREELANCE-PIPELINE.csv", e)

def daily_row(today):
    """Newest gtm/kpi-daily.csv row with date <= today (None if none)."""
    try:
        lines = read(GTM + "/kpi-daily.csv").splitlines()
        hdr = lines[0].split(",")
        best = None
        for line in lines[1:]:
            try: r = next(csv.reader([line]))
            except Exception: continue
            if r and r[0] <= today and (best is None or r[0] > best[0]):
                best = r
        return hdr, best
    except Exception:
        return [], None

def sends_ledger_today():
    """(count, source) for today from the REAL sends ledger, else (None, reason).
    Preference: (a) per-send Oxygen/outbox/sent ledger files in gtm/ with today-dated
    rows; (b) day-total counters dated today in gtm/GTM-WAR-ROOM.md ('day totals ... = N
    email-channel', 'day <today> counter N'); (c) per-send entries ('#k' cohort sends) on
    'Window send log' lines of today's gtm/driver-run-<today>-*.md (latest = max). The
    platform 14d funnel counter is cumulative, so only its same-line per-send log counts
    as today. kpi-daily.csv rows lag and are never used here.
    shortcut: (c) counts '#n' markers on send-log lines; upgrade to a structured Oxygen
    events ledger file when the CLI starts writing one."""
    for pat in ("OXYGEN*sends*", "oxygen*sends*", "*send-ledger*", "*outbox*.jsonl", "*sent*.jsonl"):
        for f in sorted(glob.glob(GTM + "/" + pat)):
            if not os.path.isfile(f):
                continue
            try:
                n = sum(1 for l in open(f) if today in l)
            except Exception:
                continue
            if n:
                return n, "count rows dated " + today + " gtm/" + os.path.basename(f)
    srcs = [("gtm/GTM-WAR-ROOM.md", WAR)]
    for f in sorted(glob.glob(GTM + "/driver-run-" + today + "-*.md")):
        srcs.append(("gtm/" + os.path.basename(f), read(f)))
    cands = []
    for fname, txt in srcs:
        for line in txt.splitlines():
            if today not in line:
                continue
            for pat in (r"day totals [^=)]*=\s*(\d+)\s+email-channel",
                        r"day " + today + r" counter (\d+)"):
                m = re.search(pat, line)
                if m:
                    cands.append((int(m.group(1)), fname, line.strip()[:160]))
            if "send log" in line.lower():
                n = len(re.findall(r"#\d", line))
                if n:
                    cands.append((n, fname, line.strip()[:160]))
    if cands:
        v, fname, line = max(cands)
        return v, "count today send entries " + fname + " line: " + line
    return None, "reason: no per-send ledger file and no day-total counter dated " + today + " in gtm/"

if "email-outreach" in agents:
    try:
        hdr, row = daily_row(today)
        def ecol(name):
            try:
                i = hdr.index(name); return int(float(row[i]))
            except Exception: return None
        d = row[0] if row else "no-row"
        n, src = sends_ledger_today()
        if n is None and row:  # explicitly labeled secondary, only when the real ledger is absent
            n = ecol("cold_first_touches")
            if n is not None:
                src = ("SECONDARY gtm/kpi-daily.csv row date=" + d +
                       " col cold_first_touches (no real sends ledger: " + src[8:] + ")")
        emit("email-outreach", "cold_first_touches", n, "count" if n is not None else "error", 40, src)
        emit("email-outreach", "replies_inbound_today", ecol("replies_inbound"), "count", None,
             "gtm/kpi-daily.csv row date=" + d + " col replies_inbound")
        emit("email-outreach", "meetings_booked_today", ecol("meetings_booked"), "count", None,
             "gtm/kpi-daily.csv row date=" + d + " col meetings_booked")
        paused = os.path.exists(AC + "/deliverability/PAUSED")
        emit("email-outreach", "deliverability_paused", int(paused), "flag", 0,
             "exists agent-company/deliverability/PAUSED")
    except Exception as e:
        err("email-outreach", "gtm/kpi-daily.csv", e)


if "lead-sourcer" in agents:
    try:
        staged = sum(1 for f in glob.glob(GTM + "/leads/*") if mday(f) == today)
        emit("lead-sourcer", "net_new_staged_leads_today", staged, "count", 50,
             "count mtime==today gtm/leads/*")
    except Exception as e:
        err("lead-sourcer", "gtm/leads/", e)

def crm_counts():
    import urllib.request
    key = os.popen("security find-generic-password -s com.rig.env.TWENTY_API_KEY -w").read().strip()
    q = ("query { persons(first: 1000) { edges { node { id } } } }")
    req = urllib.request.Request("http://192.168.68.53:8092/api/graphql",
        data=json.dumps({"query": q}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    total = len(d["data"]["persons"]["edges"])
    stages = {}
    for st in ("IDENTIFIED","ENRICHED_VERIFIED","ICP_QUALIFIED","CONTACTED","ENGAGED",
               "MEETING_BOOKED","DISCOVERY_HELD","PROPOSAL_SENT","WON","LOST","ONBOARDING_HANDOFF"):
        body = {"query": "query($w: PersonWhereInput!) { persons(filter: $w, first: 1000) "
                "{ edges { node { id } } } }", "variables": {"w": {"stage": {"eq": st}}}}
        r2 = urllib.request.Request("http://192.168.68.53:8092/api/graphql",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        stages[st] = len(json.load(urllib.request.urlopen(r2, timeout=30))["data"]["persons"]["edges"])
    return total, stages

try:  # funnel-of-record read shared by enrich/icp/reply + funnel_depth (lead agent uses it in standup)
    total, stages = crm_counts()
except Exception:
    total, stages = None, {}

if "enrich-verify" in agents:
    try:
        n = len(glob.glob(AC + "/seo-alternatives/captures/*.sha256"))
        emit("enrich-verify", "evidence_captures_total", n, "count", None,
             "ls agent-company/seo-alternatives/captures/*.sha256")
        if total is not None:
            emit("enrich-verify", "crm_enriched_verified", stages.get("ENRICHED_VERIFIED"), "count", None,
                 "graphql persons filter stage=ENRICHED_VERIFIED (Twenty 192.168.68.53:8092)")
    except Exception as e:
        err("enrich-verify", "agent-company/seo-alternatives/captures", e)

if "icp-scorer" in agents:
    try:
        scored = {}
        for f in sorted(glob.glob(AC + "/seo-alternatives/scores.jsonl")):
            for line in open(f):
                try:
                    r = json.loads(line)
                    if (r.get("date") or r.get("ts", ""))[:10] == today:
                        scored[str(r.get("score"))] = scored.get(str(r.get("score")), 0) + 1
                except Exception:
                    pass
        emit("icp-scorer", "score_distribution_today", json.dumps(scored, sort_keys=True), "json", None,
             "count score by value ts[:10]==today agent-company/seo-alternatives/scores.jsonl")
        if total is not None:
            emit("icp-scorer", "crm_icp_qualified", stages.get("ICP_QUALIFIED"), "count", None,
                 "graphql persons filter stage=ICP_QUALIFIED (Twenty 192.168.68.53:8092)")
            emit("icp-scorer", "crm_persons_total", total, "count", None,
                 "graphql persons first:1000 (Twenty 192.168.68.53:8092)")
    except Exception as e:
        err("icp-scorer", "agent-company/seo-alternatives/scores.jsonl", e)


if "reply-handler" in agents:
    try:
        hdr, row = daily_row(today)
        def dcol(name):
            try:
                i = hdr.index(name); return int(float(row[i]))
            except Exception: return None
        d = row[0] if row else "no-row"
        emit("reply-handler", "gmail_unread", dcol("replies_inbound"), "count", 0,
             "gtm/kpi-daily.csv row date=" + d + " col replies_inbound (proxy: inbound replies pending)")
        emit("reply-handler", "prospect_replies", dcol("prospect_replies"), "count", None,
             "gtm/kpi-daily.csv row date=" + d + " col prospect_replies")
    except Exception as e:
        err("reply-handler", "gtm/kpi-daily.csv", e)

if "linkedin-events" in agents:
    try:
        hdr, row = daily_row(today)
        def lcol(name):
            try:
                i = hdr.index(name); return int(float(row[i]))
            except Exception: return None
        d = row[0] if row else "no-row"
        emit("linkedin-events", "invites_gtm", lcol("linkedin_invites_gtm"), "count", None,
             "gtm/kpi-daily.csv row date=" + d + " col linkedin_invites_gtm")
        emit("linkedin-events", "messages_gtm", lcol("linkedin_messages_gtm"), "count", None,
             "gtm/kpi-daily.csv row date=" + d + " col linkedin_messages_gtm")
    except Exception as e:
        err("linkedin-events", "gtm/kpi-daily.csv", e)

if "phone-calls" in agents:
    try:
        lines = [l for l in read(GTM + "/CALL-LOG-2026-10-15.csv").splitlines()[1:] if l.strip()]
        emit("phone-calls", "call_log_lines", len(lines), "count", None,
             "count data rows gtm/CALL-LOG-2026-10-15.csv")
        m = re.findall(r"MONDAY-CALL-LIST\s+[0-9]+->(\d+)", WAR)
        n = len([l for l in read(GTM + "/MONDAY-CALL-LIST.csv").splitlines()[1:] if l.strip()]) if not m else None
        emit("phone-calls", "call_list_rows", int(m[-1]) if m else n, "count", None,
             "regex 'MONDAY-CALL-LIST N->M' gtm/GTM-WAR-ROOM.md / rows gtm/MONDAY-CALL-LIST.csv")
    except Exception as e:
        err("phone-calls", "gtm/MONDAY-CALL-LIST.csv", e)

if "web-analytics" in agents:
    try:
        days = sess_t = imps_t = clicks_t = seen_q = 0
        for line in read(AC + "/kpi/inbound.jsonl").splitlines():
            try: r = json.loads(line)
            except Exception: continue
            if r.get("source") == "ga4" and r.get("kind") == "daily":
                sess_t += int(r.get("sessions") or 0); days += 1
            if r.get("source") == "search-console" and r.get("kind") == "top_queries":
                qs = r.get("queries") or []
                if qs:
                    clicks_t = sum(int(q.get("clicks") or 0) for q in qs)
                    imps_t = sum(int(q.get("impressions") or 0) for q in qs)
                    seen_q = 1
        emit("web-analytics", "ga4_sessions_7d", sess_t if days else None, "count", None,
             "sum ga4/daily sessions agent-company/kpi/inbound.jsonl (" + str(days) + " days; refresh: ~/rig-builds/gtm-inbound/tools/web_analytics.py)")
        emit("web-analytics", "gsc_impressions_7d", imps_t if seen_q else None, "count", None,
             "sum latest search-console top_queries impressions agent-company/kpi/inbound.jsonl")
        emit("web-analytics", "gsc_clicks_7d", clicks_t if seen_q else None, "count", None,
             "sum latest search-console top_queries clicks agent-company/kpi/inbound.jsonl")
    except Exception as e:
        err("web-analytics", "agent-company/kpi/inbound.jsonl", e)

if "website-cro" in agents:
    try:
        subs = len(re.findall(r"\|\s*\d{4}-\d{2}-\d{2}", read(AC + "/funnel-submissions.md")))
        emit("website-cro", "funnel_submissions_total", subs, "count", None,
             "count dated rows agent-company/funnel-submissions.md")
        alt = os.path.exists(os.path.expanduser("~/Developer/rig-website/alternatives-2026"))
        emit("website-cro", "alt_pages_built", int(alt), "flag", 1,
             "exists ~/Developer/rig-website/alternatives-2026")
    except Exception as e:
        err("website-cro", "agent-company/funnel-submissions.md", e)

# Always-emit catch-all (fixes 'linkedin-gtm: no rows' crash): every requested agent
# gets >=1 row; an agent with no dedicated block emits None + reason, never silence.
seen = {r["agent"] for r in rows}
for a in p["agents"]:
    if a not in seen:
        missing(a, p.get("kpi"), "no measure block for agent " + str(a))
print(json.dumps({"rows": rows}))
'''
