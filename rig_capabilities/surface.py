"""v5 — public catalog, HMAC pack signing, per-asset analytics.

Signing
  HMAC-SHA256 over the pack artifact minus markdown/signature. Key from
  RIG_CAPABILITIES_SIGNING_KEY or `.signing.key` (gitignored). No key →
  `signed: false` in-band; nothing is faked.

Public catalog
  Assets whose okf.acl contains `public`. Generated `.public-catalog.json`.

Analytics
  Aggregates `.context/pack-*.json` + ratings.jsonl into per-asset counts
  and a rolling useful-rate. Written to `.context/analytics.json`.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _key_path(repo) -> Path:
    return Path(repo.root) / ".signing.key"


def load_key(repo) -> bytes | None:
    env = os.environ.get("RIG_CAPABILITIES_SIGNING_KEY")
    if env:
        return env.encode()
    p = _key_path(repo)
    if p.exists():
        try:
            raw = p.read_bytes().strip()
        except OSError:
            return None
        return raw or None
    return None


def generate_key(repo) -> Path:
    p = _key_path(repo)
    if not p.exists():
        p.write_bytes(os.urandom(32).hex().encode())
        try:
            p.chmod(0o600)
        except OSError:
            pass
    return p


def canonical_bytes(artifact: dict) -> bytes:
    skip = {"markdown", "signature", "artifact"}
    body = {k: artifact[k] for k in sorted(artifact) if k not in skip}
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


def sign_artifact(artifact: dict, key: bytes) -> dict:
    sig = hmac.new(key, canonical_bytes(artifact), hashlib.sha256).hexdigest()
    return {"alg": "hmac-sha256", "sig": sig}


def verify_artifact(artifact: dict, key: bytes) -> bool:
    sig = (artifact.get("signature") or {}).get("sig")
    if not sig:
        return False
    expect = hmac.new(key, canonical_bytes(artifact), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expect)


def public_assets(repo) -> list:
    doc = repo.load_index()
    rows = []
    for a in doc.get("assets") or []:
        acl = (a.get("okf") or {}).get("acl") or []
        if "public" in {str(x).lower() for x in acl}:
            rows.append({
                "id": a["id"], "kind": a["kind"], "source": a["source"],
                "sha": a.get("sha"), "name": a.get("name"),
                "description": (a.get("description") or "")[:240],
                "trust": (a.get("okf") or {}).get("trust"),
                "freshness": (a.get("okf") or {}).get("freshness"),
                "path": a.get("path"),
            })
    return rows


def write_public_catalog(repo) -> dict:
    rows = public_assets(repo)
    doc = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "count": len(rows), "assets": rows}
    p = Path(repo.root) / ".public-catalog.json"
    p.write_text(json.dumps(doc, indent=1))
    return {"path": str(p), "count": len(rows)}


def collect_analytics(repo) -> dict:
    ctx = Path(repo.root) / ".context"
    packs = []
    if ctx.exists():
        for f in sorted(ctx.glob("pack-*.json")):
            try:
                packs.append(json.loads(f.read_text()))
            except (json.JSONDecodeError, OSError):
                continue
    per: dict = {}
    for p in packs:
        for n in p.get("nodes") or []:
            aid = n.get("id")
            if not aid:
                continue
            rec = per.setdefault(aid, {"packs": 0, "useful": 0, "partial": 0,
                                       "wasted": 0, "kind": n.get("kind"),
                                       "source": n.get("source")})
            rec["packs"] += 1
    ratings_p = ctx / "ratings.jsonl"
    if ratings_p.exists():
        try:
            for line in ratings_p.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                v = rec.get("verdict")
                if v not in ("useful", "partial", "wasted"):
                    continue
                for i in rec.get("ids") or []:
                    row = per.setdefault(i, {"packs": 0, "useful": 0,
                                             "partial": 0, "wasted": 0})
                    row[v] = row.get(v, 0) + 1
        except OSError:
            pass
    for row in per.values():
        judged = row.get("useful", 0) + row.get("partial", 0) + row.get("wasted", 0)
        row["judged"] = judged
        row["useful_rate"] = round(row.get("useful", 0) / judged, 3) if judged else None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "packs": len(packs),
        "assets": len(per),
        "per_asset": per,
    }


def write_analytics(repo) -> dict:
    doc = collect_analytics(repo)
    p = Path(repo.root) / ".context" / "analytics.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(doc, indent=1))
    return {"path": str(p), "packs": doc["packs"], "assets": doc["assets"]}
