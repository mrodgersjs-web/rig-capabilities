"""Serve compiled goal specs to coding agents over the capability surface.

Harness YAMLs in ``capabilities/harnesses/`` are the authored source; the
engine-loadable GoalSpec JSON in ``out/harness-goalspecs/`` is what a session
actually loads. Before this module the compiled specs were reachable only by
reading the checkout, so an agent wired to this repo could pull a *skill* or a
*harness* but never the *goal* it is supposed to run.

The one thing that makes this safe to expose is staleness detection. A goalspec
is derived data: if the harness changed and nobody recompiled, serving the old
JSON is worse than serving nothing, because the agent will execute gates that no
longer exist. So every compiled spec records the sha256 of the harness it was
built from (``_meta.source_sha256``, written by scripts/compile_harnesses.py)
and every read here recomputes the live hash and reports the verdict. A spec
whose source has moved is returned flagged ``stale: true`` with the command that
would refresh it -- never silently, and never as if it were current.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SPEC_DIR_REL = "out/harness-goalspecs"
SOURCE_DIR_REL = "capabilities/harnesses"
RECOMPILE = "python3 scripts/compile_harnesses.py compile"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec_paths(repo_root: Path) -> list[Path]:
    d = Path(repo_root) / SPEC_DIR_REL
    return sorted(d.glob("*.json")) if d.is_dir() else []


def load_spec(repo_root: Path, stem: str) -> tuple[dict | None, str | None]:
    """Return (payload, None) or (None, reason). Reason is never a silent dict."""
    safe = Path(str(stem)).name
    if safe != str(stem) or not safe:
        return None, "unsafe_stem"
    path = Path(repo_root) / SPEC_DIR_REL / f"{safe}.json"
    if not path.is_file():
        return None, "no_such_spec"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "spec_unreadable"
    goals = doc.get("goals") or []
    if not goals:
        return None, "spec_has_no_goals"
    return goals[0], None


def provenance(repo_root: Path, payload: dict) -> dict:
    """How current is this compiled goal? ``stale`` is the answer an agent needs."""
    meta = payload.get("_meta") or {}
    src_rel = meta.get("source") or ""
    rec_sha = meta.get("source_sha256") or ""
    src = Path(repo_root) / src_rel if src_rel else None
    out = {"source": src_rel or None, "compiled_source_sha256": rec_sha or None,
           "source_present": bool(src and src.is_file()), "stale": False,
           "reason": "ok", "recompile": RECOMPILE}
    if not src_rel:
        # Specs compiled before source pinning existed carry no hash: they are
        # unverified rather than verified, and saying "ok" would be a lie.
        out.update(stale=True, reason="source_unpinned")
        return out
    if not out["source_present"]:
        out.update(stale=True, reason="source_missing")
        return out
    now = _sha(src)
    out["source_sha256"] = now
    if not rec_sha:
        out.update(stale=True, reason="source_unpinned")
    elif rec_sha != now:
        out.update(stale=True, reason="source_changed_since_compile")
    return out


def summaries(repo_root: Path) -> list[dict]:
    rows = []
    for path in spec_paths(repo_root):
        payload, reason = load_spec(repo_root, path.stem)
        if payload is None:
            rows.append({"stem": path.stem, "error": reason})
            continue
        meta = payload.get("_meta") or {}
        # session_type is emitted under preconditions.meta by the compiler, not
        # under _meta — reading the wrong branch returns "" for every spec and
        # resolve-by-session then silently misses everything.
        pcm = (payload.get("preconditions") or {}).get("meta") or {}
        gates = payload.get("gates") or []
        rows.append({
            "stem": path.stem,
            "goal_id": payload.get("id"),
            "name": payload.get("name"),
            "session_type": str(pcm.get("session_type") or ""),
            "anchor": payload.get("anchor"),
            "bms_mode": payload.get("bms_mode"),
            "gates": len(gates),
            "blocking": sum(1 for g in gates if g.get("required")),
            "gates_without_proof": len(meta.get("gates_without_proof") or []),
            "approval_required": bool(payload.get("approval_required")),
            "provenance": provenance(repo_root, payload),
        })
    return rows


def _stems_for(rows: list, needle: str) -> list:
    return [r["stem"] for r in rows
            if needle and needle in str(r.get("session_type", "")).lower()]



def serve(repo_root, stem: str = "", session_type: str = "") -> dict:
    """The MCP-facing answer. One shape for list, resolve-by-session, and fetch.

    Callers pass either a Repo (CLI/server) or a Path (tests). A Repo carries
    `.root`; a Path ALSO has `.root` (its "/" anchor), so a bare
    `getattr(x, "root", x)` silently retargets every relative tree onto the
    filesystem root — ask for a Repo by a name only Repo has instead.
    """
    repo_root = Path(repo_root.root if hasattr(repo_root, "cap_root") else repo_root)
    if not spec_paths(repo_root):
        return {"verdict": "NO_SPECS",
                "detail": f"nothing compiled under {SPEC_DIR_REL}/; run {RECOMPILE}"}
    if stem:
        payload, reason = load_spec(repo_root, stem)
        if payload is None:
            return {"verdict": "ERROR", "reason": reason, "stem": stem,
                    "available": [p.stem for p in spec_paths(repo_root)][:40]}
        prov = provenance(repo_root, payload)
        return {"verdict": "STALE" if prov["stale"] else "OK",
                "stem": stem, "provenance": prov, "goal": payload}
    rows = summaries(repo_root)
    # Staleness decides the verdict in every branch. An aggregate "OK" beside a
    # stale list is how a gate goes vacuous: the caller that reads only `verdict`
    # -- which is every caller that ever automated this -- would load expired
    # gates. Proven by planting an un-recompiled harness edit and watching these
    # two branches refuse to go red the first time they were written.
    stale = [r["stem"] for r in rows if (r.get("provenance") or {}).get("stale")]
    if session_type:
        hits = _stems_for(rows, str(session_type).strip().lower())
        hit_stale = [s for s in stale if s in hits]
        return {"verdict": "NO_MATCH" if not hits else ("STALE" if hit_stale else "OK"),
                "session_type": session_type, "stems": hits, "stale": hit_stale,
                "all_session_types": sorted({r.get("session_type", "")
                                             for r in rows if r.get("session_type")})}
    return {"verdict": "STALE" if stale else "OK", "specs": len(rows),
            "stale": stale, "goals": rows}
