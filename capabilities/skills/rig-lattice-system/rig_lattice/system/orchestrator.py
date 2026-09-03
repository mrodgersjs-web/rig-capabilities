"""System orchestrator — runs L1 → L7 with BMS-routed archetype selection per level.

Per the RIG Lattice + LinkedIn Studio template.

Usage:
    from rig_lattice.system import run_system
    result = run_system(source="my_proposal.md", confidence=0.85)
    # → SystemRun with per-level results + final artifact + receipts
"""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from rig_lattice.enterprise.iqrsqpi import BMSMode, route_bms
from rig_lattice.system.archetypes import get_archetype, ARCHETYPES
from rig_lattice.system.levels import Level, LEVELS


@dataclass
class LevelRun:
    level: Level
    mode: BMSMode
    ok: bool
    output: Any
    reason: str
    elapsed_ms: float

    def to_dict(self) -> dict:
        # Don't try to serialize full text in output — truncate large keys
        safe_output = {}
        if isinstance(self.output, dict):
            for k, v in self.output.items():
                if isinstance(v, str) and len(v) > 200:
                    safe_output[k] = v[:200] + f"... ({len(v):,} chars total)"
                elif isinstance(v, (dict, list)):
                    safe_output[k] = f"<{type(v).__name__} with {len(v)} items>"
                else:
                    safe_output[k] = v
        else:
            safe_output = str(self.output)[:200]
        return {
            "level": self.level.value,
            "mode": self.mode.value,
            "ok": self.ok,
            "reason": self.reason,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "output_preview": safe_output,
        }


@dataclass
class SystemRun:
    mission_id: str
    confidence: float
    bms_mode: BMSMode
    source: str
    levels: list[LevelRun] = field(default_factory=list)
    ok: bool = True
    short_circuited_at: Level | None = None
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    @property
    def total_elapsed_ms(self) -> float:
        end = self.completed_at if self.completed_at else time.time()
        return (end - self.started_at) * 1000

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "confidence": self.confidence,
            "bms_mode": self.bms_mode.value,
            "source": self.source,
            "ok": self.ok,
            "short_circuited_at": self.short_circuited_at.value if self.short_circuited_at else None,
            "total_elapsed_ms": round(self.total_elapsed_ms, 2),
            "levels_completed": len([l for l in self.levels if l.ok]),
            "levels_total": len(self.levels),
            "level_runs": [l.to_dict() for l in self.levels],
        }


def run_level(level: Level, state: dict, mode: BMSMode) -> LevelRun:
    """Execute one level with the chosen BMS archetype."""
    archetype = get_archetype(level, mode)
    t0 = time.time()
    try:
        ok, output, reason = archetype.fn(state)
    except Exception as e:
        ok, output, reason = False, None, f"{type(e).__name__}: {e}"
    elapsed_ms = (time.time() - t0) * 1000
    return LevelRun(level=level, mode=mode, ok=ok, output=output,
                     reason=reason, elapsed_ms=elapsed_ms)


def run_system(*,
                source: str,
                stdin_text: str = "",
                confidence: float = 0.75,
                force_a4: bool = False,
                tier: str = "client",
                author_persona: str = "claude",
                mission_id: str | None = None,
                mode_override: BMSMode | None = None) -> SystemRun:
    """Execute the full 7-level RIG Deviator System.

    Args:
        source: file path / URL / '-' for stdin
        stdin_text: text to use when source='-'
        confidence: 0-1; routes to BMS A1-A4
        force_a4: bypass router → A4 (human gate mandatory)
        tier: artifact tier (internal_note → civilization)
        author_persona: required for L5 adversarial review independence
        mission_id: optional ID; auto-generated if omitted
        mode_override: force a specific BMS mode for all levels

    Returns:
        SystemRun with per-level results.
    """
    mid = mission_id or f"sys-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
    bms_mode = mode_override or route_bms(confidence, force_a4)

    # ── Per-mission budget enforcement ──────────────────────────────
    # A1: $0.00 (no LLM), A2: $0.10, A3: $0.50, A4: $0.00 (human gate)
    try:
        from rig_lattice.enterprise.cost_ledger import set_budget
        budget_map = {
            BMSMode.A1: 0.0,
            BMSMode.A2: 0.10,
            BMSMode.A3: 0.50,
            BMSMode.A4: 0.0,
        }
        set_budget(mid, budget_map.get(bms_mode, 0.0))
    except Exception:
        pass

    run = SystemRun(
        mission_id=mid,
        confidence=confidence,
        bms_mode=bms_mode,
        source=source,
    )
    state: dict = {
        "mission_id": mid,
        "source": source,
        "stdin_text": stdin_text,
        "tier": tier,
        "author_persona": author_persona,
        "confidence": confidence,
        "bms_mode": bms_mode.value,
    }

    for level in LEVELS:
        result = run_level(level, state, bms_mode)
        run.levels.append(result)
        state[level.value] = result.output if result.ok else None

        if not result.ok:
            run.ok = False
            run.short_circuited_at = level
            break

    run.completed_at = time.time()

    # ── Persist to canonical SQLite DB ─────────────────────────────────
    # Best-effort: never let a DB write failure poison the run result.
    try:
        from rig_lattice.system.persistence import persist_system_run
        run.persistence = persist_system_run(run, state)  # type: ignore[attr-defined]
    except Exception as e:
        run.persistence = {"error": f"{type(e).__name__}: {e}"}  # type: ignore[attr-defined]

    return run
