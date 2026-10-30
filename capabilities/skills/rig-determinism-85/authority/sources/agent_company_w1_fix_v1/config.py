"""GTM agent company W1 - configuration (L0 Temporal engine, L1 workers, L2 lead, L3 head)."""
from __future__ import annotations

SSH_HOST = "rig-128gb"  # rig128gb laptop: canonical .rig/live control-plane
CP = "/Users/rig128gb/.rig/live/control-plane"
AC = CP + "/agent-company"
KPI_LEDGER = AC + "/kpi/gtm.jsonl"
HB_DIR = AC + "/heartbeats"
QUEUE_DIR = AC + "/queue/gtm"
QUEUE_CLOSED = AC + "/queue/gtm-closed"
STANDUP_DIR = CP + "/gtm/standup"
REVIEW_DIR = CP + "/gtm/reviews"
COUNCIL_DIR = AC + "/council-cards"
LOG_DIR = AC + "/logs"
INCIDENTS = LOG_DIR + "/watchdog-incidents.log"
WATCHDOG_LOG = LOG_DIR + "/watchdog.log"
GTM_DIR = CP + "/gtm"
LEADS_DIR = GTM_DIR + "/leads"

TEMPORAL_ADDR = "127.0.0.1:7233"
NAMESPACE = "rig-company"
TASK_QUEUE = "gtm"

TZ = "America/Denver"
QUIET = (21, 7)  # quiet hours 21:00-06:59 Denver (messages to Mike / sends)

# role: worker|lead|head|watchdog. Workers are the only writers for their resources.
AGENTS: dict[str, dict] = {
    "upwork-bidder":   {"role": "worker", "cadence_s": 1800,  "kpi": "proposals_sent_today",    "target": 8},
    "email-outreach":  {"role": "worker", "cadence_s": 900,   "kpi": "cold_first_touches",      "target": 40},
    "lead-sourcer":    {"role": "worker", "cadence_s": 1800,  "kpi": "net_new_staged_leads_today", "target": 50},
    "enrich-verify":   {"role": "worker", "cadence_s": 1800,  "kpi": "evidence_captures_total", "target": None},
    "icp-scorer":      {"role": "worker", "cadence_s": 1800,  "kpi": "crm_icp_qualified",       "target": None},
    "reply-handler":   {"role": "worker", "cadence_s": 300,   "kpi": "gmail_unread",            "target": 0},
    "linkedin-events": {"role": "worker", "cadence_s": 1800,  "kpi": "connections",             "target": None},
    "phone-calls":     {"role": "worker", "cadence_s": 1800,  "kpi": "call_packs_present",      "target": 0},
    "web-analytics":   {"role": "worker", "cadence_s": 1800,  "kpi": "ga4_sessions_7d",         "target": None},
    "website-cro":     {"role": "worker", "cadence_s": 1800,  "kpi": "funnel_submissions_total", "target": None},
    "gtm-lead":        {"role": "lead",   "at_time": "07:30"},
    "gtm-head":        {"role": "head",   "weekly_day": 3, "weekly_time": "08:00", "monthly_day": 1, "monthly_time": "07:00"},
    "gtm-watchdog":    {"role": "watchdog", "cadence_s": 900},
}
# legacy pre-W1b id kept registered (paused lane, superseded by linkedin-events)
EXTRA_WORKFLOWS = {"linkedin-gtm": "superseded by linkedin-events (W1b); relaunch via query_status relaunch"}
GRACE_MULT = 3.0   # stale = no heartbeat for GRACE_MULT * cadence
GRACE_MIN_S = 1800
