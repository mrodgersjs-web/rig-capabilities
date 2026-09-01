"""OKF (Open Knowledge Format) bundle contract for capability assets.

Every indexed asset carries an `okf` block derived from frontmatter:

  type, domain, owner, status, verified_by, verified_on, version, acl, relates_to

plus two computed fields:

  trust     — [0..1] confidence from source, status, and verification age
  freshness — Stable | Aging | Stale | Deprecated | Unknown

Trust formula (documented, deterministic):
  base: canonical 0.9 | harness-root install 0.7 | external root 0.6
  status: Stable +0.1 | Draft -0.3 | Deprecated -> 0.2 (floor rule)
  verified_on within 180 days +0.1; older than 365 days -0.2
  floor 0.1, ceiling 1.0.

`acl` (list of scopes) is single-user here; filters honor `requester_acl`
when a caller supplies one — a list intersection check, org-mode ready.
"""
from __future__ import annotations

from datetime import date, datetime

OKF_KEYS = ("type", "domain", "owner", "status", "verified_by",
            "verified_on", "version", "acl", "relates_to")

_BASE = {"canonical": 0.9, "installed": 0.7, "great": 0.8}
_EXT_BASE = 0.6
_PREFIX_BASE = (("fed:", 0.5), ("sql:", 0.55), ("api:", 0.55))

def _as_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        return [t.strip().strip("[]") for t in v.replace(";", ",").split(",")
                if t.strip().strip("[]")]
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return []


def _as_date(v) -> date | None:
    if not isinstance(v, str) or not v.strip():
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(v.strip()[:10], fmt).date()
        except ValueError:
            continue
    return None


def trust(source: str, status: str, verified_on: date | None,
          today: date | None = None) -> float:
    t = _BASE.get(source)
    if t is None:
        t = next((b for p, b in _PREFIX_BASE if source.startswith(p)), _EXT_BASE)
    s = (status or "").strip().lower()
    if s == "stable":
        t += 0.1
    elif s == "draft":
        t -= 0.3
    elif s == "deprecated":
        return 0.2
    if verified_on is not None:
        age = ((today or date.today()) - verified_on).days
        if age <= 180:
            t += 0.1
        elif age > 365:
            t -= 0.2
    return max(0.1, min(1.0, round(t, 2)))


def freshness(status: str, verified_on: date | None,
              today: date | None = None) -> str:
    s = (status or "").strip().lower()
    if s == "deprecated":
        return "Deprecated"
    if s not in ("stable", "draft", "active", "current") and verified_on is None:
        return "Unknown"
    if verified_on is None:
        return "Stable" if s in ("stable", "active", "current") else "Unknown"
    age = ((today or date.today()) - verified_on).days
    if age > 365:
        return "Stale"
    if age > 180:
        return "Aging"
    return "Stable"


def meta(fm: dict, source: str, today: date | None = None,
         kind: str | None = None) -> dict:
    """Derive the okf block for one asset from its parsed frontmatter."""
    v_on = _as_date(fm.get("verified_on") or fm.get("verified-on"))
    status = str(fm.get("status") or "")
    d = today or date.today()
    acl = _as_list(fm.get("acl") or fm.get("visibility"))
    # installer-delivered commands/hooks are the public contract of this repo
    if not acl and source == "canonical" and kind in ("command", "hook"):
        acl = ["public"]
    return {
        "type": str(fm.get("type") or ""),
        "domain": str(fm.get("domain") or ""),
        "owner": str(fm.get("owner") or ""),
        "status": status,
        "verified_by": str(fm.get("verified_by") or ""),
        "verified_on": v_on.isoformat() if v_on else "",
        "version": str(fm.get("version") or ""),
        "acl": acl,
        "relates_to": _as_list(fm.get("relates_to") or fm.get("relates-to")),
        "trust": trust(source, status, v_on, d),
        "freshness": freshness(status, v_on, d),
    }


REQUIRED_CANONICAL = ("status",)  # only hard expectation for now


def check(repo) -> dict:
    """Report OKF completeness across canonical assets."""
    doc = repo.load_index()
    rows = {"canonical_total": 0, "with_status": 0, "with_owner": 0,
            "with_domain": 0, "with_verified_on": 0, "with_relates_to": 0,
            "missing_status": []}
    dist: dict = {}
    for a in doc["assets"]:
        if a["source"] != "canonical":
            continue
        rows["canonical_total"] += 1
        o = a.get("okf") or {}
        for key, field in (("with_status", "status"), ("with_owner", "owner"),
                           ("with_domain", "domain"),
                           ("with_verified_on", "verified_on"),
                           ("with_relates_to", "relates_to")):
            if o.get(field):
                rows[key] += 1
        if not o.get("status"):
            rows["missing_status"].append(a["id"])
        f = o.get("freshness", "Unknown")
        dist[f] = dist.get(f, 0) + 1
    rows["freshness_distribution"] = dist
    return rows
