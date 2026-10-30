#!/usr/bin/env python3
"""rig-crm-sync: every inbound reply, calculator lead and booking -> Twenty CRM deal.

Sources (read-only):
  1. Airtable "GTM · Inbound" (Command Center base, table tblYNRKlVisbYEJO8)
     - Google appointment bookings  (Zap 384480122)
     - Upwork messages              (Zap 384479423)
     - bx-* calculator captures     (d30-bx-gtm writes them into this table)
  2. Oxygen Unibox replies (`oxygen messages query --direction inbound`)

Target: Twenty v2.50.1 (http://192.168.68.53:8092) via twenty_client.TwentyClient.
Each event upserts person + company + deal (opportunity) with source and stage.
Idempotent: ledger at ~/.rig/state/crm-sync/ledger.json keys every source event;
re-runs are no-ops. Stage guards never move a person or deal backwards.

Stage map (deterministic, event kind -> person GTM stage / deal stage):
  lead    (calculator submission) -> IDENTIFIED       / NEW
  reply   (inbound message)       -> ENGAGED          / SCREENING
  booking (appointment booked)    -> MEETING_BOOKED   / MEETING
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import time
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/rig128gb/.rig/live/control-plane/agent-company")
from twenty_client import TwentyClient  # noqa: E402

HOME = os.path.expanduser("~")
STATE_DIR = f"{HOME}/.rig/state/crm-sync"
LEDGER_PATH = f"{STATE_DIR}/ledger.json"
LOG_PATH = f"{HOME}/.rig/logs/crm-sync.jsonl"
AIRTABLE_ENV = f"{HOME}/.rig/secrets/airtable-command-center.env"
AIRTABLE_TABLE = "tblYNRKlVisbYEJO8"  # "GTM · Inbound"
OXYGEN_BIN = f"{HOME}/.local/bin/oxygen"

# Same blocklist as gtm-crm-funnel: our own identities never become leads.
BLOCKLIST_SUBSTR = ("rodgemd1@gmail.com", "@rodgemd1", "mike@rodgersintelligence.com",
                    "mrodgersjs@gmail.com", "mike@rodgersintelligencegroup.com")
BLOCKLIST_PREFIX = ("jacob",)
FREE_MAIL = ("gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com",
             "yahoo.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com",
             "msn.com", "qq.com", "mail.com", "gmx.com", "yandex.com", "zoho.com")
SYNTHETIC_DOMAIN_SUFFIX = (".example", ".test", ".invalid", ".rig.local")

KIND_PERSON_STAGE = {"lead": "IDENTIFIED", "reply": "ENGAGED", "booking": "MEETING_BOOKED"}
KIND_DEAL_STAGE = {"lead": "NEW", "reply": "SCREENING", "booking": "MEETING"}
KIND_LABEL = {"lead": "Lead", "reply": "Reply", "booking": "Booking"}
PERSON_STAGE_RANK = {"IDENTIFIED": 0, "ENRICHED_VERIFIED": 1, "ICP_QUALIFIED": 2,
                     "CONTACTED": 3, "ENGAGED": 4, "MEETING_BOOKED": 5, "DISCOVERY_HELD": 6,
                     "PROPOSAL_SENT": 7, "WON": 8, "ONBOARDING_HANDOFF": 9, "LOST": 10}
DEAL_STAGE_RANK = {"NEW": 0, "SCREENING": 1, "MEETING": 2, "PROPOSAL": 3, "CUSTOMER": 4}

AMOUNT_RE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
AMOUNT_CONTEXT_RE = re.compile(
    r"(budget|price|cost|proposal|quote|not[ -]?to[ -]?exceed|retainer|per month|per year|"
    r"annual|contract value|worth|estimate)", re.I)
AMOUNT_NEGATION_RE = re.compile(r"\b(off|discount|save|coupon|refund)\b", re.I)
BOOKING_RE = re.compile(
    r"\b(booked|appointment|calendar invite|scheduled (a )?(call|meeting|demo|consult)|"
    r"confirmed (a )?(call|meeting))\b", re.I)
LEAD_RE = re.compile(
    r"\b(calculator|your result|result is in|assessment|scorecard|audit result|"
    r"trigger calculator|revenue calculator|audit calculator)\b", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_SUBJECT_RE = re.compile(r"^\s*re\s*:", re.I)
NO_REPLY_SENDERS = ("upwork@email.upwork.com", "noreply@", "no-reply@", "notifications@",
                    "calendar-notification@", "no_response@")


def parse_ts(s: str) -> float | None:
    """Epoch seconds from ISO or RFC2822-ish Airtable Received strings."""
    s = (s or "").strip().replace(" (UTC)", "")
    if not s:
        return None
    try:
        from datetime import datetime, timezone
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        pass
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(s).timestamp()
    except Exception:
        return None


def is_reply(ev: dict, outbound_contacts: set[str]) -> bool:
    """A reply is a thread reply (^Re:) or an inbound from a contact we messaged.
    Everything else in the raw mailbox (newsletters, receipts, OTPs) is noise."""
    return ev["email"] in outbound_contacts or bool(RE_SUBJECT_RE.search(ev["subject"]))


def iso_ts(s: str) -> str | None:
    """ISO-8601 Z string for Twenty DATE_TIME fields; None when unparseable."""
    t = parse_ts(s)
    if t is None:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------- pure helpers (unit-tested) -------------------------------------

def blocked(email: str) -> bool:
    e = (email or "").lower()
    return any(s in e for s in BLOCKLIST_SUBSTR) or e.startswith(BLOCKLIST_PREFIX)


def classify(event: dict) -> str:
    """Deterministic event kind: booking > lead > reply (fallback)."""
    src = (event.get("source_label") or "")
    text = " ".join(str(event.get(k) or "") for k in ("subject", "body"))
    if src.strip() == "Booking" or BOOKING_RE.search(text):
        return "booking"
    if LEAD_RE.search(text) or re.search(r"\bbx-", src, re.I):
        return "lead"
    return "reply"


def parse_amount(subject: str, body: str) -> int | None:
    """First $ figure near a budget/price keyword; never a discount figure."""
    for text in (subject or "", body or ""):
        for m in AMOUNT_RE.finditer(text):
            before = text[max(0, m.start() - 48):m.start()]
            if AMOUNT_NEGATION_RE.search(before):
                continue
            window = text[max(0, m.start() - 48):m.end() + 24]
            if AMOUNT_CONTEXT_RE.search(window):
                # half-up: money never uses banker's rounding
                return int(float(m.group(1).replace(",", "")) + 0.5)
    return None


def pick_email(*texts: str) -> str | None:
    for t in texts:
        for m in EMAIL_RE.finditer(t or ""):
            return m.group(0).lower()
    return None


def split_name(display: str, email: str) -> tuple[str, str]:
    display = (display or "").strip().strip('"')
    if "<" in display and ">" in display:
        display = display.split("<", 1)[0].strip()
    if not display or "@" in display:
        local = email.split("@", 1)[0]
        display = local.replace(".", " ").replace("_", " ").replace("-", " ").title()
    parts = display.split()
    return parts[0], " ".join(parts[1:])


def email_domain(email: str) -> str:
    return email.split("@", 1)[1].lower() if "@" in email else ""


def company_worthy(email: str) -> bool:
    d = email_domain(email)
    if not d or d in FREE_MAIL:
        return False
    return not any(d.endswith(s) for s in SYNTHETIC_DOMAIN_SUFFIX)


def event_key(system: str, native_id: str, fallback: str) -> str:
    return f"{system}:{native_id or fallback}"


def from_airtable_record(rec: dict) -> dict | None:
    f = rec.get("fields") or {}
    gmail_id = (f.get("Gmail Message ID") or "").strip()
    sender = (f.get("From") or "").strip()
    subject = (f.get("Subject") or "").strip()
    body = (f.get("Snippet") or "")
    # a platform notification's own address is never the prospect
    sender_is_notify = any(ns in sender.lower() for ns in NO_REPLY_SENDERS)
    email = None if sender_is_notify else pick_email(sender)
    if not email:
        # platform notification: try the body, else a synthetic handle (see shortcut note)
        email = pick_email(subject, body)
    synthetic = False
    if not email:
        if gmail_id:
            # shortcut: Upwork hides prospect addresses; key the person by the message id
            # and let the deal source carry the truth. Upgrade when the Zap forwards a
            # real address (parse it then; pick_email already handles that case).
            email = f"upwork-{gmail_id[:16]}@inbound.rig.local"
            synthetic = True
        else:
            return None  # unattributable row: caller logs the skip
    occurred = (f.get("Received") or rec.get("createdTime") or "").strip()
    ev = {
        "key": event_key("at", gmail_id, rec.get("id", "")),
        "system": "airtable-inbox",
        "source_label": (f.get("Source") or "").strip(),
        "channel": "upwork" if "upwork" in (sender + subject + f.get("Source", "")).lower() else "email",
        "subject": subject,
        "body": body,
        "display_name": sender,
        "email": email,
        "occurred_at": occurred,
        "synthetic_email": synthetic,
        "row_id": rec.get("id", ""),
    }
    ev["kind"] = classify(ev)
    ev["amount"] = parse_amount(subject, body)
    return ev


def from_oxygen_message(m: dict) -> dict | None:
    email = pick_email(m.get("contactHandle") or "")
    if not email:
        return None
    ev = {
        "key": event_key("ox", m.get("id", ""), m.get("conversationRef") or ""),
        "system": "oxygen-inbox",
        "source_label": f"oxygen:{m.get('channel', 'email')}",
        "channel": m.get("channel", "email"),
        "subject": m.get("subject") or "",
        "body": m.get("body") or m.get("snippet") or "",
        "display_name": m.get("contactName") or "",
        "email": email,
        "occurred_at": m.get("sentAt") or "",
        "synthetic_email": False,
        "row_id": m.get("id", ""),
    }
    ev["kind"] = classify(ev)
    ev["amount"] = parse_amount(ev["subject"], ev["body"])
    return ev


# ---------- transports ------------------------------------------------------

class AirtableInbox:
    def __init__(self):
        env = {}
        with open(AIRTABLE_ENV) as fh:
            for line in fh:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
        self.pat = env["AIRTABLE_CC_PAT"]
        self.base = env["AIRTABLE_CC_BASE"]

    def fetch_all(self) -> list[dict]:
        rows, offset = [], None
        while True:
            url = (f"https://api.airtable.com/v0/{self.base}/{AIRTABLE_TABLE}"
                   f"?pageSize=100" + (f"&offset={offset}" if offset else ""))
            req = urllib_request.Request(url, headers={"Authorization": f"Bearer {self.pat}"})
            with urllib_request.urlopen(req, timeout=30) as resp:
                d = json.load(resp)
            rows += d.get("records", [])
            offset = d.get("offset")
            if not offset:
                return rows


def oxygen_outbound_contacts() -> set[str]:
    """Contacts we have ever sent to: the deterministic 'this inbound is a reply' set."""
    out, cursor, contacts = "", None, set()
    for _ in range(20):
        cmd = [OXYGEN_BIN, "messages", "query", "--direction", "outbound",
               "--channel", "all", "--limit", "100", "--json"]
        if cursor:
            cmd += ["--cursor", cursor]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            raise RuntimeError(f"oxygen outbound query failed rc={out.returncode}: {out.stderr[:200]}")
        d = json.loads(out.stdout)
        for m in d.get("data", {}).get("messages", []):
            e = pick_email(m.get("contactHandle") or "")
            if e:
                contacts.add(e)
        cursor = d.get("data", {}).get("nextCursor") or None
        if not cursor:
            break
    return contacts


def oxygen_inbound() -> list[dict]:
    out, cursor, msgs = "", None, []
    for _ in range(20):  # bounded pagination
        cmd = [OXYGEN_BIN, "messages", "query", "--direction", "inbound",
               "--channel", "all", "--limit", "100", "--json"]
        if cursor:
            cmd += ["--cursor", cursor]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            raise RuntimeError(f"oxygen messages query failed rc={out.returncode}: {out.stderr[:200]}")
        d = json.loads(out.stdout)
        msgs += d.get("data", {}).get("messages", [])
        cursor = d.get("data", {}).get("nextCursor") or None
        if not cursor:
            break
    return msgs


class TwentyOps:
    """Person/company/deal upserts on top of twenty_client + REST."""

    def __init__(self, client: TwentyClient | None = None):
        self.c = client or TwentyClient()

    def _req(self, method, path, body=None):
        return self.c._req(method, path, body)

    # person ---------------------------------------------------------------
    def person(self, email: str) -> dict | None:
        return self.c.get(email)

    def save_person(self, ev: dict, stage: str | None, create: bool) -> str:
        first, last = split_name(ev["display_name"], ev["email"])
        touch = iso_ts(ev["occurred_at"])
        if create:
            res = self.c.upsert(ev["email"], first_name=first, last_name=last,
                                stage=stage, source=ev["system"], channel=ev["channel"],
                                owner_agent="rig-crm-sync", last_touch_at=touch)
        else:
            body = {}
            if touch:
                body["lastTouchAt"] = touch
            if stage:
                body["stage"] = stage
            res = self._req("PATCH", f"/rest/people/{ev['_person_id']}", body)
        data = res.get("data") or res
        for v in (data.values() if isinstance(data, dict) else []):
            if isinstance(v, dict) and "id" in v:
                return v["id"]
        raise RuntimeError(f"person save returned no id: {str(res)[:200]}")

    # company ---------------------------------------------------------------
    def company(self, domain: str) -> str | None:
        f = urllib_parse.quote(f"domainName.primaryLinkUrl[eq]:{domain}")
        res = self._req("GET", f"/rest/companies?filter={f}&limit=2")
        for r in (res.get("data") or {}).get("companies") or []:
            return r["id"]
        return None

    def save_company(self, domain: str) -> str:
        res = self._req("POST", "/rest/companies",
                        {"name": domain,
                         "domainName": {"primaryLinkLabel": "", "primaryLinkUrl": domain}})
        data = res.get("data") or res
        for v in (data.values() if isinstance(data, dict) else []):
            if isinstance(v, dict) and "id" in v:
                return v["id"]
        raise RuntimeError(f"company save returned no id: {str(res)[:200]}")

    # deal ------------------------------------------------------------------
    def find_deal(self, name: str, person_id: str) -> str | None:
        f = urllib_parse.quote(f"name[eq]:{name}")
        res = self._req("GET", f"/rest/opportunities?filter={f}&limit=10")
        for r in (res.get("data") or {}).get("opportunities") or []:
            if r.get("pointOfContactId") == person_id:
                return r["id"]
        return None

    def deal(self, deal_id: str) -> dict | None:
        try:
            res = self._req("GET", f"/rest/opportunities/{deal_id}")
        except urllib_error.HTTPError as e:
            if e.code == 404:
                return None
            raise
        return (res.get("data") or {}).get("opportunity")

    def save_deal(self, ev: dict, person_id: str, company_id: str | None,
                  name: str, stage: str, amount: int | None,
                  close_date: str | None, deal_id: str | None) -> str:
        body = {"name": name, "stage": stage,
                "source": f"{ev['system']}:{ev['source_label'] or ev['kind']}",
                "pointOfContactId": person_id}
        if company_id:
            body["companyId"] = company_id
        if deal_id:
            existing = self.deal(deal_id) or {}
            if existing.get("stage") and DEAL_STAGE_RANK.get(stage, -1) < DEAL_STAGE_RANK.get(existing["stage"], 99):
                body["stage"] = existing["stage"]  # never regress a deal
            if existing.get("amount") is None and amount is not None:
                body["amount"] = {"amountMicros": amount * 1_000_000, "currencyCode": "USD"}
            if close_date and not existing.get("closeDate"):
                body["closeDate"] = close_date
            self._req("PATCH", f"/rest/opportunities/{deal_id}", body)
            return deal_id
        if amount is not None:
            body["amount"] = {"amountMicros": amount * 1_000_000, "currencyCode": "USD"}
        if close_date:
            body["closeDate"] = close_date
        res = self._req("POST", "/rest/opportunities", body)
        data = res.get("data") or res
        for v in (data.values() if isinstance(data, dict) else []):
            if isinstance(v, dict) and "id" in v:
                return v["id"]
        raise RuntimeError(f"deal save returned no id: {str(res)[:200]}")


# ---------- engine ----------------------------------------------------------

def load_ledger() -> dict:
    try:
        with open(LEDGER_PATH) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def save_ledger(ledger: dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=True)
    os.replace(tmp, LEDGER_PATH)


def person_stage_for(ev: dict, existing: dict | None) -> str | None:
    """Stage to write; None when the person already sits at or past it (no regression)."""
    want = KIND_PERSON_STAGE[ev["kind"]]
    if existing and existing.get("stage"):
        if PERSON_STAGE_RANK.get(existing["stage"], -1) >= PERSON_STAGE_RANK[want]:
            return None
    return want


def process(ev: dict, ops, ledger: dict) -> dict:
    """Upsert person+company+deal for one event; idempotent via ledger."""
    if ev["key"] in ledger:
        return {"key": ev["key"], "status": "skipped_already_synced"}
    if blocked(ev["email"]):
        return {"key": ev["key"], "status": "skipped_blocklist"}

    existing = ops.person(ev["email"])
    ev["_person_id"] = existing["id"] if existing else None
    stage = person_stage_for(ev, existing)
    person_id = ops.save_person(ev, stage, create=not existing)

    company_id = None
    if company_worthy(ev["email"]):
        company_id = ops.company(email_domain(ev["email"])) or ops.save_company(email_domain(ev["email"]))

    name = f"{KIND_LABEL[ev['kind']]} — {split_name(ev['display_name'], ev['email'])[0]} {split_name(ev['display_name'], ev['email'])[1]}".strip()
    deal_id = ledger.get(ev["key"], {}).get("deal_id") or ops.find_deal(name, person_id)
    close_date = None
    if ev["kind"] == "booking":
        # shortcut: the booked moment is best approximated by the event timestamp;
        # upgrade to parsing the actual appointment slot when the Zap forwards it.
        close_date = iso_ts(ev["occurred_at"])
    deal_id = ops.save_deal(ev, person_id, company_id, name, KIND_DEAL_STAGE[ev["kind"]],
                            ev["amount"], close_date, deal_id)
    ledger[ev["key"]] = {"person_id": person_id, "company_id": company_id, "deal_id": deal_id,
                         "kind": ev["kind"], "email": ev["email"], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return {"key": ev["key"], "status": "synced", "person_id": person_id,
            "company_id": company_id, "deal_id": deal_id, "kind": ev["kind"]}


def run_once() -> dict:
    summary = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "events": 0, "synced": 0, "skipped": 0, "errors": [],
               "created_deals": [], "pipeline_usd": 0, "max_lag_seconds": None,
               "sources": {}}
    ledger = load_ledger()
    ops = TwentyOps()
    events = []

    try:
        rows = AirtableInbox().fetch_all()
        summary["sources"]["airtable_rows"] = len(rows)
        for rec in rows:
            ev = from_airtable_record(rec)
            if ev is None:
                summary["errors"].append(f"unattributable row {rec.get('id')}")
                continue
            events.append(ev)
    except Exception as e:  # one dead source must not kill the other
        summary["errors"].append(f"airtable: {e}")

    try:
        contacts = oxygen_outbound_contacts()
        msgs = oxygen_inbound()
        summary["sources"]["oxygen_messages"] = len(msgs)
        summary["sources"]["oxygen_outbound_contacts"] = len(contacts)
        for m in msgs:
            ev = from_oxygen_message(m)
            if ev is None:
                summary["errors"].append(f"unattributable oxygen msg {m.get('id')}")
                continue
            if not is_reply(ev, contacts):
                summary["skipped_noise"] = summary.get("skipped_noise", 0) + 1
                continue
            events.append(ev)
    except Exception as e:
        summary["errors"].append(f"oxygen: {e}")

    for ev in events:
        summary["events"] += 1
        try:
            r = process(ev, ops, ledger)
        except Exception as e:
            summary["errors"].append(f"{ev['key']}: {e}")
            continue
        if r["status"] == "synced":
            summary["synced"] += 1
            summary["created_deals"].append(r["deal_id"])
            lag = parse_ts(ev["occurred_at"])
            if lag is not None:
                lag = time.time() - lag
                summary["max_lag_seconds"] = max(summary["max_lag_seconds"] or 0, lag)
        else:
            summary["skipped"] += 1
    save_ledger(ledger)

    # KPI: pipeline $ across deals this tool owns (ledger), deduped per deal
    seen_deals = set()
    for rec in ledger.values():
        if rec["deal_id"] in seen_deals:
            continue
        seen_deals.add(rec["deal_id"])
        try:
            d = ops.deal(rec["deal_id"]) or {}
        except Exception:
            continue
        amt = (d.get("amount") or {}).get("amountMicros") or 0
        if d.get("stage") not in ("CUSTOMER",) and amt:
            summary["pipeline_usd"] += amt // 1_000_000

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as fh:
        fh.write(json.dumps(summary, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    s = run_once()
    print(json.dumps(s, indent=1, sort_keys=True))
    sys.exit(0 if not s["errors"] else 2)
