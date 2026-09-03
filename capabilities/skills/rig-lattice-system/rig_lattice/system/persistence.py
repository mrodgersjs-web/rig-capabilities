"""system.persistence — write every SystemRun into the canonical SQLite DB.

Bridges the in-memory `SystemRun` dataclass into the schema defined by
`enterprise.database`. Called by the orchestrator after every run.

Tables touched per run:
  - mission            — one row per run
  - engine_score       — one row per engine result (when L2 audit present)
  - audit_chain        — one event row per run + one per HARD_BLOCK
  - brier              — one row per Brier prediction logged in L7
"""
from __future__ import annotations
import time
import uuid
from typing import Any

from rig_lattice.enterprise.database import (
    connection, insert_mission, insert_engine_score,
    insert_audit_entry, get_last_audit_hash,
)


def _layer_for(engine_id: int) -> str:
    """Map 1-40 → cognitive/nature/physics."""
    if engine_id <= 20:
        return "cognitive"
    if engine_id <= 30:
        return "nature"
    return "physics"


def persist_system_run(run: Any, state: dict) -> dict:
    """Persist a `SystemRun` to the DB. Returns counts of rows written.

    Idempotent on (mission_id) — repeated calls UPSERT the mission row but
    only append engine_score rows once per mission (we guard with the
    score_id derivation which is deterministic).
    """
    l2 = state.get("L2_PROCESS") or {}
    audit = l2.get("audit") if isinstance(l2, dict) else None
    l6 = state.get("L6_CONVERT") or {}
    final_audit = l6.get("final_audit") if isinstance(l6, dict) else None

    # Prefer final_audit if L6 ran successfully; else use L2 audit
    pri_audit = final_audit or audit or {}
    rig_l = pri_audit.get("rig_l", 0)
    hard_blocks = pri_audit.get("hard_blocks", 0)
    status = pri_audit.get("status", "?")
    bdf = pri_audit.get("bdf")
    weakest_gate = _weakest_gate(pri_audit)

    # ── 1. mission row ────────────────────────────────────────────────
    mission_row = {
        "mission_id": run.mission_id,
        "tier": state.get("tier", "client"),
        "bms_mode": run.bms_mode.value,
        "intent": state.get("intent", ""),
        "confidence": run.confidence,
        "artifact_hash": _artifact_hash(state),
        "rig_l": float(rig_l) if rig_l is not None else None,
        "bdf": float(bdf) if bdf is not None else None,
        "status": status,
        "short_circuit": int(bool(run.short_circuited_at)),
        "weakest_gate": weakest_gate,
        "escalation_cost": _escalation_cost(pri_audit),
    }
    insert_mission(mission_row)

    # ── 2. engine_score rows ──────────────────────────────────────────
    engines_written = 0
    if pri_audit:
        engines = pri_audit.get("engines", {}) or {}
        # Build slug → engine_id map from the canonical registry. The exported
        # name is ENGINE_REGISTRY; the old `from ... import REGISTRY` inside a
        # bare `except Exception` always failed and silently zeroed this map,
        # so every engine_score row fell back to a positional index. A missing
        # registry is not a degradable condition — let it propagate.
        from rig_lattice.core.registry import ENGINE_REGISTRY as REGISTRY

        slug_to_id = {e.slug: e.id for e in REGISTRY}
        for idx, (slug, r) in enumerate(engines.items()):
            if not isinstance(r, dict):
                continue
            engine_id = r.get("engine_id") or slug_to_id.get(slug) or (idx + 1)
            engine_name = r.get("codename") or slug
            score_id = f"{run.mission_id}-{slug}"  # unique per slug
            try:
                insert_engine_score({
                    "score_id": score_id,
                    "mission_id": run.mission_id,
                    "engine_id": engine_id,
                    "engine_name": engine_name,
                    "engine_slug": slug,
                    "layer": r.get("layer") or _layer_for(engine_id),
                    "raw_score": r.get("raw_score") or r.get("score"),
                    "madz": r.get("sigma") or r.get("madz"),
                    "status": r.get("status"),
                    "is_gate": r.get("is_gate", False),
                })
                engines_written += 1
            except Exception:
                # PRIMARY KEY collision = already persisted; skip silently
                pass

    # ── 3. audit_chain event ──────────────────────────────────────────
    prev = get_last_audit_hash()
    chain_payload = {
        "mission_id": run.mission_id,
        "bms_mode": run.bms_mode.value,
        "tier": state.get("tier", "client"),
        "rig_l": float(rig_l) if rig_l is not None else None,
        "hard_blocks": int(hard_blocks or 0),
        "status": status,
        "short_circuited_at": run.short_circuited_at.value if run.short_circuited_at else None,
        "elapsed_ms": run.total_elapsed_ms,
    }
    entry_hash = insert_audit_entry("system_run", chain_payload, prev)

    # ── 4. brier row (if L7 logged a prediction) ──────────────────────
    l7 = state.get("L7_AUTONOMIZE") or {}
    pred = l7.get("prediction_logged") if isinstance(l7, dict) else None
    brier_written = 0
    if pred and isinstance(pred, dict):
        try:
            with connection() as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO brier
                        (log_id, mission_id, engine_name, predicted,
                         expected_resolution, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pred.get("log_id") or f"brier-{run.mission_id}",
                    run.mission_id,
                    pred.get("engine_name", "composite_RIG_L"),
                    float(pred.get("predicted_madz", 0)),
                    pred.get("expected_resolution"),
                    pred.get("content_hash"),
                ))
                brier_written = 1
        except Exception:
            pass

    return {
        "mission_id": run.mission_id,
        "missions_written": 1,
        "engine_scores_written": engines_written,
        "audit_chain_entry_hash": entry_hash,
        "brier_rows_written": brier_written,
    }


def _artifact_hash(state: dict) -> str | None:
    l1 = state.get("L1_CAPTURE") or {}
    if isinstance(l1, dict):
        return l1.get("content_hash")
    return None


def _weakest_gate(audit: dict) -> str | None:
    """Identify the worst-status engine name."""
    if not audit:
        return None
    engines = audit.get("engines", {}) or {}
    hard = [(slug, r) for slug, r in engines.items()
             if isinstance(r, dict) and r.get("status") == "HARD_BLOCK"]
    if hard:
        return hard[0][1].get("codename") or hard[0][0]
    # else: pick the lowest sigma engine
    worst = None
    worst_sigma = float("inf")
    for slug, r in engines.items():
        if not isinstance(r, dict):
            continue
        sig = r.get("sigma")
        if sig is not None and sig < worst_sigma:
            worst_sigma = sig
            worst = r.get("codename") or slug
    return worst


def _escalation_cost(audit: dict) -> int | None:
    """Sum escalation cost for HARD_BLOCK engines per DOCTRINE §6."""
    if not audit:
        return None
    engines = audit.get("engines", {}) or {}
    hard_count = sum(1 for r in engines.values()
                      if isinstance(r, dict) and r.get("status") == "HARD_BLOCK")
    if hard_count == 0:
        return 0
    # cost ladder: 2^n for n=1..10, escalates after that
    return min(2 ** hard_count, 1024)


def recent_missions(limit: int = 20) -> list[dict]:
    """Read the N most recent mission rows from the DB."""
    with connection() as conn:
        rows = conn.execute("""
            SELECT mission_id, tier, bms_mode, confidence, rig_l, status,
                   short_circuit, weakest_gate, created_at
            FROM mission
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def mission_detail(mission_id: str) -> dict | None:
    """Return mission row + all engine scores for a given mission."""
    with connection() as conn:
        m = conn.execute(
            "SELECT * FROM mission WHERE mission_id = ?", (mission_id,)
        ).fetchone()
        if not m:
            return None
        scores = conn.execute("""
            SELECT engine_id, engine_name, layer, raw_score, madz, status, is_gate
            FROM engine_score
            WHERE mission_id = ?
            ORDER BY engine_id ASC
        """, (mission_id,)).fetchall()
    return {
        "mission": dict(m),
        "engine_scores": [dict(s) for s in scores],
    }
