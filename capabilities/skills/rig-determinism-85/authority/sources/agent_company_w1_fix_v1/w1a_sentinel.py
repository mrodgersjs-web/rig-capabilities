"""W1a Sentinel: the verifier workflow (workers cannot mark done) + Gate 11 seam report.

Judge verdicts are REAL rig-judge output run on the laptop; never fabricated, never
defaulted. On judge unavailability the row records status=judge_unavailable.
"""
from __future__ import annotations
import asyncio
import json
import re
import shlex
import time
from datetime import datetime, timedelta
from temporalio import activity, workflow
with workflow.unsafe.imports_passed_through():
    from temporalio.common import RetryPolicy
    from . import config, sshio

CAN_S = 20 * 3600  # continue-as-new after ~20h (same convention as workflows.py)
SEAM_EVERY_S = 1800
STATE_CAP = 12000  # chars of (claim + evidence) handed to the judges
JUDGE_BIN = "/Users/rig128gb/.rig/bin/rig-judge"
VERDICTS_LEDGER = config.AC + "/verdicts.jsonl"
VERDICTS_DIR = config.AC + "/verdicts"
JUDGE_LINE = re.compile(r"^JUDGE jev=([0-9.]+|UNAVAILABLE\S*(?:\s*\([^)]*\))?) "
                        r"clef=([0-9.]+|UNAVAILABLE\S*(?:\s*\([^)]*\))?) -> (DONE|NOT DONE)", re.M)

# Gate 11 seams: origin stage(s) -> target stage, with the owning agent's heartbeat.
SEAMS = [
    {"seam": "Identified->Verified", "origin": "IDENTIFIED", "sla_h": 24, "agent": "enrich-verify"},
    {"seam": "Verified->Contacted", "origin": "ENRICHED_VERIFIED", "sla_h": 24, "agent": "email-outreach"},
    {"seam": "Reply->Meeting", "origin": "ENGAGED", "sla_h": 120, "agent": "reply-handler"},
    {"seam": "Meeting->Proposal", "origin": "DISCOVERY_HELD", "sla_h": 120, "agent": "phone-calls"},
    {"seam": "Won->Onboarding", "origin": "WON", "sla_h": 48, "agent": "gtm-lead"},
]

SEAM_REMOTE = r'''
import json, os, time
from datetime import datetime, timedelta, timezone
p = json.loads(os.environ["PAYLOAD"]); today = p["today"]; seams = p["seams"]
CP = "/Users/rig128gb/.rig/live/control-plane"; AC = CP + "/agent-company"
GQL = "http://192.168.68.53:8092/graphql"
def _key():
    try:
        for ln in open(os.path.expanduser("~/.rig/secrets/twenty-crm.env")):
            if ln.startswith("TWENTY_API_KEY="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return os.popen("security find-generic-password -s com.rig.env.TWENTY_API_KEY -w").read().strip()
key = _key()
_last = [0.0]
def gql(q):
    w = _last[0] + 1.2 - time.monotonic()
    if w > 0: time.sleep(w)
    _last[0] = time.monotonic()
    import urllib.request
    req = urllib.request.Request(GQL, data=json.dumps({"query": q}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    return json.load(urllib.request.urlopen(req, timeout=30))
now = datetime.now(timezone.utc)
rows = []
stage_counts = {}
for s in seams:
    cutoff = (now - timedelta(hours=s["sla_h"])).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    stuck = total = None
    try:
        d = gql('query { people(filter: {stage: {eq: %s}}, first: 1000) { edges { node { id } } } }' % s["origin"])
        total = len(d["data"]["people"]["edges"])
        d2 = gql('query { people(filter: {stage: {eq: %s}, updatedAt: {lt: "%s"}}, first: 1000) { edges { node { id } } } }'
                 % (s["origin"], cutoff))
        stuck = len(d2["data"]["people"]["edges"])
    except Exception as e:
        stuck = None
    hb_age = None
    try:
        hb = json.load(open(AC + "/heartbeats/" + s["agent"] + "/latest.json"))
        ts = datetime.fromisoformat(hb["ts"])
        if ts.tzinfo is None: ts = ts.replace(tzinfo=timezone.utc)
        hb_age = int((now - ts).total_seconds())
    except Exception:
        pass
    ok = (stuck == 0) if stuck is not None else None
    rows.append({"seam": s["seam"], "origin": s["origin"], "sla_h": s["sla_h"], "agent": s["agent"],
                 "in_stage": total, "stuck": stuck, "heartbeat_age_s": hb_age,
                 "status": ("ok" if ok else ("STUCK" if ok is False else "UNKNOWN"))})
# three SLA lines
def latest_daily(cols):
    try:
        lines = open(CP + "/gtm/kpi-daily.csv").read().splitlines()
        hdr = lines[0].split(",")
        import csv as _csv
        row = next(_csv.reader([lines[-1]]))
        return {c: (row[hdr.index(c)] if c in hdr else "") for c in cols}
    except Exception:
        return {}
reply_age = next((r["heartbeat_age_s"] for r in rows if r["agent"] == "reply-handler"), None)
daily = latest_daily(["median_response_min", "bounce_pct", "bounce_count"])
sla = {
    "speed_to_lead": {"rule": "inbound reply drafted < 15 min",
                      "reply_handler_heartbeat_age_s": reply_age,
                      "latest_median_response_min": daily.get("median_response_min") or "n/a",
                      "status": ("ok" if reply_age is not None and reply_age < 900 else "AT RISK")},
    "deliverability": {"rule": "bounce < 3 percent",
                       "latest_bounce_pct": daily.get("bounce_pct") or "n/a",
                       "status": ("ok" if daily.get("bounce_pct","1") not in ("", None) and float(daily.get("bounce_pct") or 0) < 3.0 else "check")},
    "onboarding": {"rule": "kickoff < 48 h",
                   "won_stuck_over_48h": next((r["stuck"] for r in rows if r["origin"] == "WON"), None),
                   "status": ("ok" if next((r["stuck"] for r in rows if r["origin"] == "WON"), None) == 0 else "STUCK")},
}
L = ["# Gate 11 seam report " + today, "",
     "Source: Twenty GraphQL people counts per stage (192.168.68.53:8092/graphql) + "
     "agent-company/heartbeats/<agent>/latest.json + gtm/kpi-daily.csv latest row.", "",
     "| seam | origin stage | SLA | stuck beyond SLA | in stage | owner heartbeat age | status |",
     "|---|---|---|---|---|---|---|"]
for r in rows:
    L.append("| %s | %s | %s h | %s | %s | %s | %s |" % (r["seam"], r["origin"], r["sla_h"],
             r["stuck"], r["in_stage"],
             (str(r["heartbeat_age_s"]) + " s") if r["heartbeat_age_s"] is not None else "no heartbeat",
             r["status"]))
L += ["", "## SLA lines",
      "- Speed-to-Lead (inbound reply drafted < 15 min): %s (reply-handler heartbeat %s s old; latest median_response_min %s)"
        % (sla["speed_to_lead"]["status"], reply_age, sla["speed_to_lead"]["latest_median_response_min"]),
      "- Deliverability (bounce < 3%%): %s (latest bounce_pct %s)" % (sla["deliverability"]["status"], sla["deliverability"]["latest_bounce_pct"]),
      "- Onboarding (kickoff < 48 h): %s (WON stuck > 48 h: %s)" % (sla["onboarding"]["status"], sla["onboarding"]["won_stuck_over_48h"]),
      ""]
path = AC + "/logs/seam-report-" + today + ".md"
os.makedirs(os.path.dirname(path), exist_ok=True)
open(path, "w").write("\n".join(L))
print(json.dumps({"ok": True, "path": path, "seams": rows, "sla": sla}))
'''


@activity.defn(name="judge_claim")
async def judge_claim(claim: dict) -> dict:
    """Run one done-claim through rig-judge on the laptop; ledger the real verdict."""
    worker = re.sub(r"[^A-Za-z0-9._-]", "-", str(claim.get("worker", "unknown")))[:64] or "unknown"
    text = str(claim.get("text", ""))[:STATE_CAP]
    ev_path = str(claim.get("evidence_path", ""))
    ev = ""
    if ev_path:
        ev = await sshio.read(ev_path, timeout=30) or ""
    state = "CLAIM: " + text + "\n\nEVIDENCE (verbatim, bounded):\n" + ev
    state = state[:STATE_CAP]
    ts = int(time.time())
    state_path = f"{config.LOG_DIR}/judge/{ts}-{worker}.state.txt"
    await sshio.write(state_path, state)
    cmd = (f"env -u PYTHONHOME -u PYTHONPATH {shlex.quote(JUDGE_BIN)} "
           f"'Does the evidence support that the claim is fully met?' {shlex.quote(state_path)}")
    p = await sshio.run(cmd, timeout=240)
    out = (p.stdout or "") + (("\n" + p.stderr[-400:]) if p.returncode != 0 else "")
    m = None
    for m in JUDGE_LINE.finditer(out):
        pass  # last JUDGE line wins
    if m:
        jev = float(m.group(1))
        clef_raw = m.group(2)
        verdict = m.group(3)
        if clef_raw.startswith("UNAVAILABLE"):
            row = {"worker": worker, "claim": text[:300], "jev": jev, "clef": None,
                   "verdict": "judge_unavailable", "status": "judge_unavailable",
                   "ts": datetime_iso(ts)}
        else:
            row = {"worker": worker, "claim": text[:300], "jev": jev, "clef": float(clef_raw),
                   "verdict": verdict, "status": "judged", "ts": datetime_iso(ts)}
    else:
        row = {"worker": worker, "claim": text[:300], "jev": None, "clef": None,
               "verdict": "judge_unavailable", "status": "judge_unavailable",
               "error": out[-300:], "ts": datetime_iso(ts)}
    await sshio.append(VERDICTS_LEDGER, json.dumps(row, sort_keys=True) + "\n")
    await sshio.write(f"{VERDICTS_DIR}/{ts}-{worker}.md",
                      f"# verdict {ts} {worker}\n\nstatus: {row['status']}\n\n```\n{out}\n```\n")
    return row


def datetime_iso(ts: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


@activity.defn(name="seam_check")
async def seam_check() -> dict:
    today = time.strftime("%Y-%m-%d")
    res = await sshio.run_py(SEAM_REMOTE, {"today": today, "seams": SEAMS}, timeout=180)
    return res if isinstance(res, dict) else {"ok": False, "error": str(res)[:300]}


@workflow.defn(name="SentinelVerifier")
class SentinelVerifier:
    """One verifier for every worker: claims are judged by rig-judge, never self-marked.
    Also emits the Gate 11 seam report every 30 min."""

    def __init__(self):
        self._wake = False
        self._claims: list[dict] = []
        self.beat: dict = {"agent": "sentinel", "state": "init"}
        self.judged = 0
        self.last_verdict: dict | None = None
        self.last_seam: dict | None = None
        self._seam_due = 0.0

    @workflow.signal
    def wake(self): self._wake = True

    @workflow.signal
    def claim(self, payload: dict):
        self._claims.append(payload)
        self._wake = True

    @workflow.query
    def status(self) -> dict:
        return {"beat": self.beat, "judged": self.judged, "pending": len(self._claims),
                "last_verdict": self.last_verdict, "last_seam": self.last_seam, "last": _now()}

    @workflow.run
    async def run(self):
        while True:
            try:
                await workflow.wait_condition(
                    lambda: self._wake or bool(self._claims),
                    timeout=timedelta(seconds=SEAM_EVERY_S))
            except asyncio.TimeoutError:
                pass
            self._wake = False
            while self._claims:
                payload = self._claims.pop(0)
                row = await workflow.execute_activity(
                    "judge_claim", payload,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=1))  # never retry: one real call
                self.judged += 1
                self.last_verdict = row
            if workflow.now().timestamp() >= self._seam_due:
                self._seam_due = workflow.now().timestamp() + SEAM_EVERY_S
                self.last_seam = await workflow.execute_activity(
                    "seam_check",
                    start_to_close_timeout=timedelta(minutes=4),
                    retry_policy=RetryPolicy(maximum_attempts=2,
                                             initial_interval=timedelta(seconds=15)))
            self.beat = {"agent": "sentinel", "state": "ok", "ts": workflow.now().isoformat()}
            if (workflow.now() - workflow.info().start_time).total_seconds() > CAN_S:
                workflow.continue_as_new()


def _now() -> float:
    return workflow.now().timestamp()


SENTINEL_ACTIVITIES = [judge_claim, seam_check]
