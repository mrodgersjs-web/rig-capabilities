"""V23: agent packs.

`agents/<id>/pack.json` names the skills/harnesses an agent runs on. This
module resolves those names against the live index, detects agent-shaped
queries, and builds a boot pack — the resolved entries WITH runtime evidence
(live state + done-test verdict), so an agent boots knowing what it can
actually run, not just what it is supposed to have.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def load_packs(repo) -> dict:
    out = {}
    d = Path(repo.root) / "agents"
    if not d.exists():
        return out
    for p in sorted(d.glob("*/pack.json")):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        agent = doc.get("agent") or p.parent.name
        out[agent] = doc
    return out


def _index_ids(repo) -> dict:
    from .taxonomy import dedupe
    return {(a["id"], a.get("kind")): a for a in dedupe(repo.load_index()["assets"])}


def resolve_pack(repo, agent: str) -> dict:
    """Pack with every entry resolved against the index; unresolved flagged."""
    packs = load_packs(repo)
    pack = packs.get(agent)
    if pack is None:
        return {"ok": False, "error": f"no pack for agent '{agent}'",
                "known": sorted(packs)}
    idx = _index_ids(repo)
    entries, unresolved = [], []
    for e in pack.get("skills", []):
        a = idx.get((e["id"], e.get("kind")))
        if a is None:  # kind drift: any-kind lookup
            a = next((v for (i, _k), v in idx.items() if i == e["id"]), None)
        if a is None:
            entries.append({**e, "resolved": False})
            unresolved.append(e["id"])
        else:
            entries.append({**e, "resolved": True,
                            "source": a.get("source"),
                            "summary": (a.get("summary") or "")[:140]})
    return {"ok": True, "agent": agent, "lanes": pack.get("lanes", []),
            "entries": entries, "unresolved": unresolved}


_STOP = {"the", "a", "an", "to", "for", "run", "use", "with", "and", "wire",
         "agent", "pack", "boot", "give", "set", "up", "of", "in", "on", "my"}


def match_agent(repo, intent: str, limit: int = 3) -> list:
    """Rank agents whose id parts appear as (sub)tokens of the query."""
    toks = [t for t in re.split(r"[^a-z0-9]+", intent.lower())
            if t and t not in _STOP and len(t) > 2]
    rows = []
    for agent in load_packs(repo):
        parts = [p for p in agent.split("-") if p not in _STOP and len(p) > 2]
        if not parts:
            continue
        hit = sum(1 for p in parts
                  if any(p == t or p in t or t in p for t in toks))
        if hit:
            rows.append({"agent": agent, "score": round(hit / len(parts), 3),
                         "matched": hit, "of": len(parts)})
    rows.sort(key=lambda r: (-r["score"], r["agent"]))
    return rows[:limit]


def boot_pack(repo, agent: str) -> dict:
    """Resolved pack + per-entry runtime evidence (live state, done-test)."""
    from .done_tests import run_asset
    from .live import live_status
    rp = resolve_pack(repo, agent)
    if not rp.get("ok"):
        return rp
    for e in rp["entries"]:
        if not e.get("resolved"):
            e["live"] = {"live": False, "state": "unresolved"}
            continue
        ls = live_status(repo, id=e["id"], services=False)
        e["live"] = ls.get("summary", {"live": False, "state": "unknown"})
        if e.get("source") == "canonical":
            ra = run_asset(repo, e["id"], "canonical")
            e["done_test"] = {"pass": ra["pass"],
                              "checks": len(ra["results"])}
    rp["ready"] = sum(1 for e in rp["entries"]
                      if e.get("live", {}).get("live") and
                      e.get("done_test", {}).get("pass", True))
    rp["total"] = len(rp["entries"])
    return rp
