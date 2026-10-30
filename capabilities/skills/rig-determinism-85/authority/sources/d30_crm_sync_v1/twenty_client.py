#!/usr/bin/env python3
"""Twenty CRM client for RIG agents (GTM funnel of record).

Server: Twenty v2.50.1 self-hosted on rig256gb, http://192.168.68.53:8092
Auth:   API key in macOS keychain item com.rig.env.TWENTY_API_KEY
        (fallback $TWENTY_API_KEY). Send as `Authorization: Bearer <key>`.
        NOTE: X-Api-Key header is NOT accepted by this build; Bearer only.
Rate limit: ~1 request/second per token — the server answers 429 above that.

Funnel fields on person (camelCase — Twenty rejects underscores):
  source, channel, icpScore, lastTouchAt, ownerAgent  (custom fields)
  stage  (SELECT "GTM Stage", option values:
    IDENTIFIED, ENRICHED_VERIFIED, ICP_QUALIFIED, CONTACTED, ENGAGED,
    MEETING_BOOKED, DISCOVERY_HELD, PROPOSAL_SENT, WON, LOST,
    ONBOARDING_HANDOFF)
  Lost reason: use the person's note/summary field or a tagged note (build
  records no Lost rows yet).

Usage:
    from twenty_client import TwentyClient
    t = TwentyClient()
    t.get("alice@example.com")                      # person dict or None
    t.upsert("alice@example.com", first_name="Alice", stage="CONTACTED")
    t.move_stage("alice@example.com", "MEETING_BOOKED")
"""
from __future__ import annotations
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TWENTY_URL", "http://192.168.68.53:8092")
STAGES = ["IDENTIFIED", "ENRICHED_VERIFIED", "ICP_QUALIFIED", "CONTACTED",
          "ENGAGED", "MEETING_BOOKED", "DISCOVERY_HELD", "PROPOSAL_SENT",
          "WON", "LOST", "ONBOARDING_HANDOFF"]


def _api_key() -> str:
    key = os.environ.get("TWENTY_API_KEY")
    if key:
        return key.strip()
    out = subprocess.run(
        ["security", "find-generic-password", "-a", "rig",
         "-s", "com.rig.env.TWENTY_API_KEY", "-w"],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("no TWENTY_API_KEY env and keychain lookup failed")
    return out.stdout.strip()


class TwentyClient:
    def __init__(self, base: str = BASE, key: str | None = None):
        self.base = base
        self.key = (key or _api_key()).strip()
        self._last = 0.0

    def _req(self, method: str, path: str, body=None, tries: int = 8):
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(tries):
            wait = self._last + 1.2 - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(
                self.base + path, data=data, method=method,
                headers={"Authorization": f"Bearer {self.key}",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.load(resp)
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    time.sleep(2 + attempt)
                    continue
                raise
        raise RuntimeError(f"rate-limited giving up on {method} {path}")

    def get(self, email: str):
        """Return the person with this primary email, or None."""
        # REST filter grammar (v2.50.1): field.subfield[comparator]:value
        f = urllib.parse.quote(f"emails.primaryEmail[eq]:{email.lower()}")
        res = self._req("GET", f"/rest/people?filter={f}&limit=2")
        rows = (res.get("data") or {}).get("people") or []
        for r in rows:
            em = (r.get("emails") or {}).get("primaryEmail") or r.get("email") or ""
            if em.lower() == email.lower():
                return r
        return None

    def upsert(self, email: str, *, first_name: str = "", last_name: str = "",
               stage: str | None = None, source: str | None = None,
               channel: str | None = None, owner_agent: str | None = None,
               icp_score: int | None = None, last_touch_at: str | None = None):
        """Create or update the person; returns the stored person dict."""
        email = email.lower()
        body = {}
        if first_name or last_name:
            body["name"] = {"firstName": first_name, "lastName": last_name}
        body["emails"] = {"primaryEmail": email}
        for field, val in (("stage", stage), ("source", source), ("channel", channel),
                           ("ownerAgent", owner_agent), ("icpScore", icp_score),
                           ("lastTouchAt", last_touch_at)):
            if val is not None:
                body[field] = val
        if stage is not None and stage.upper() not in STAGES:
            raise ValueError(f"unknown stage {stage!r}; allowed: {', '.join(STAGES)}")
        existing = self.get(email)
        if existing:
            res = self._req("PATCH", f"/rest/people/{existing['id']}", body)
        else:
            res = self._req("POST", "/rest/people", body)
        return res.get("data") or res

    def move_stage(self, email: str, stage: str):
        """Set person.stage to `stage` (case-insensitive name like 'Contacted')."""
        s = stage.upper().replace("+", "_").replace(" ", "_")
        if s not in STAGES:
            raise ValueError(f"unknown stage {stage!r}; allowed: {', '.join(STAGES)}")
        return self.upsert(email, stage=s)


if __name__ == "__main__":
    t = TwentyClient()
    me = t.get("crm-admin3@rig.local")
    print("keychain+REST OK; people reachable:", me is not None or "0 rows")
