"""v3/v4 policy: ACL enforcement, observation-decay, ratings→trust.

ACL
  acl_policy.json maps agent id → permitted scopes. `*` = unrestricted.
  No requester (operator CLI) = unrestricted. Unknown agent uses `default`.
  Asset with empty acl = unrestricted. Else require intersection.

Decay (v3)
  Unseen assets are not punished (multiplier 1.0). Observed assets stay at
  1.0 for HALF_LIFE_DAYS, then linear to FLOOR at 2× half-life.

Ratings trust (v4)
  useful +0.05, partial 0, wasted −0.10 per rating, clamped ±0.30.
  Applied as additive delta on (base × decay).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HALF_LIFE_DAYS = 90
DECAY_FLOOR = 0.85
RATING_CLAMP = 0.30
RATING_USEFUL = 0.05
RATING_WASTED = -0.10


def load_policy(repo) -> dict:
    p = Path(repo.root) / "acl_policy.json"
    if not p.exists():
        return {"agents": {}}
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {"agents": {}}
    return d if isinstance(d, dict) else {"agents": {}}


def permitted_scopes(repo, agent: str | None) -> set | None:
    """None = unrestricted caller. set() = deny-all (no scopes). set('*') = all."""
    if not agent:
        return None
    agents = (load_policy(repo).get("agents") or {})
    scopes = agents.get(agent)
    if scopes is None:
        scopes = agents.get("default")
    if scopes is None:
        return None
    if not isinstance(scopes, list):
        return None
    return set(str(s) for s in scopes)


def acl_allows(asset_acl, caller_scopes: set | None) -> bool:
    if caller_scopes is None:
        return True
    if "*" in caller_scopes:
        return True
    if not asset_acl:
        return True
    return bool(set(asset_acl) & caller_scopes)


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def last_observed(repo) -> dict:
    """id → latest ISO timestamp from observations.jsonl."""
    p = Path(repo.root) / ".context" / "observations.jsonl"
    out: dict = {}
    if not p.exists():
        return out
    try:
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = rec.get("ts") or ""
            for i in rec.get("ids") or []:
                prev = out.get(i)
                if prev is None or ts > prev:
                    out[i] = ts
    except OSError:
        return out
    return out


def record_observation(repo, pack_id: str, ids: list, agent: str | None = None) -> None:
    d = Path(repo.root) / ".context"
    d.mkdir(exist_ok=True)
    rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "pack": pack_id, "ids": list(ids), "agent": agent or ""}
    with (d / "observations.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")


def decay_multiplier(last_iso: str | None, now: datetime | None = None) -> float:
    if not last_iso:
        return 1.0
    dt = _parse_ts(last_iso)
    if dt is None:
        return 1.0
    now = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    days = max(0.0, (now - dt).total_seconds() / 86400.0)
    if days <= HALF_LIFE_DAYS:
        return 1.0
    span = float(HALF_LIFE_DAYS)
    t = min(1.0, (days - span) / span)
    return round(1.0 - t * (1.0 - DECAY_FLOOR), 4)


def ratings_delta(repo) -> dict:
    p = Path(repo.root) / ".context" / "ratings.jsonl"
    acc: dict = {}
    if not p.exists():
        return acc
    try:
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            v = rec.get("verdict")
            delta = RATING_USEFUL if v == "useful" else (
                RATING_WASTED if v == "wasted" else 0.0)
            if delta == 0.0:
                continue
            for i in rec.get("ids") or []:
                acc[i] = acc.get(i, 0.0) + delta
    except OSError:
        return acc
    for k, v in list(acc.items()):
        acc[k] = max(-RATING_CLAMP, min(RATING_CLAMP, round(v, 4)))
    return acc


def effective_trust(base: float, aid: str, obs: dict, deltas: dict) -> float:
    t = float(base) * decay_multiplier(obs.get(aid)) + float(deltas.get(aid, 0.0))
    return max(0.1, min(1.0, round(t, 2)))


def trust_tables(repo) -> tuple[dict, dict]:
    return last_observed(repo), ratings_delta(repo)
