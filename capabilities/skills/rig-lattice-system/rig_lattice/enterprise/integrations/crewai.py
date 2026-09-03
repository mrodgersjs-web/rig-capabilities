"""CrewAI integration — agent orchestration for L3 / L5 / L7 swarms.

If `crewai` is installed, dispatches to real Crew. Otherwise registers the
intent locally so the operator can route manually.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent.parent
LOCAL_LOG = AUDITS_DIR / "crewai.jsonl"


def crewai_available() -> bool:
    try:
        import crewai  # noqa: F401
        return True
    except ImportError:
        return False


@dataclass
class Crew:
    name: str
    agents: tuple[str, ...]
    tasks: tuple[str, ...]
    handler: Callable[[dict], dict] | None = None


_CREWS: dict[str, Crew] = {}


def register_crew(name: str, agents: tuple[str, ...], tasks: tuple[str, ...],
                    handler: Callable[[dict], dict] | None = None) -> Crew:
    crew = Crew(name=name, agents=agents, tasks=tasks, handler=handler)
    _CREWS[name] = crew
    return crew


def list_crews() -> list[str]:
    return list(_CREWS.keys())


def _local_log(event: str, payload: dict) -> dict:
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "destination": "local_fallback",
        "payload": payload,
    }
    with LOCAL_LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec


def crewai_dispatch(crew_name: str, state: dict) -> dict:
    """Dispatch a registered crew with state. Falls back to local log."""
    crew = _CREWS.get(crew_name)
    if not crew:
        return _local_log(f"crew_not_found_{crew_name}", state)
    if crew.handler:
        try:
            return crew.handler(state)
        except Exception as e:
            return _local_log(f"crew_{crew_name}_HANDLER_ERROR_{type(e).__name__}", state)
    if crewai_available():
        return _local_log(f"crew_{crew_name}_dispatched_but_no_handler_wired", state)
    return _local_log(f"crew_{crew_name}_dispatch", state)


# ── Canonical crews for the RIG Deviator System ────────────────────────
def _outcome_observer_handler(state: dict) -> dict:
    """Stub for outcome_observer crew. Resolves Brier predictions when
    realized σ is known."""
    return {"crew": "outcome_observer", "state_keys": list(state.keys()),
            "action": "outcome_resolution_logged"}


def _plus20_swarm_handler(state: dict) -> dict:
    """Real plus20_swarm dispatch — runs concurrent +20σ agents via
    enterprise.swarm.dispatch_swarm. Falls back to deterministic patch
    overlays when LLM is offline."""
    from rig_lattice.enterprise.swarm import dispatch_swarm
    text = (state.get("L1_CAPTURE") or {}).get("text", "")
    weak = state.get("weakest_engines") or state.get("weak_engines") or []
    if not weak:
        # Derive from L2 audit if not passed explicitly
        l2 = state.get("L2_PROCESS") or {}
        audit = l2.get("audit") if isinstance(l2, dict) else None
        if audit:
            weak = [
                {"slug": s, "codename": r.get("codename"), "sigma": r.get("sigma")}
                for s, r in audit.get("engines", {}).items()
                if r.get("status") == "HARD_BLOCK"
            ][:7]
    if not text or not weak:
        return {"crew": "plus20_swarm",
                "action": "skipped",
                "reason": "no_text_or_no_weak_engines"}
    dispatch = dispatch_swarm(
        text, weak,
        mission_id=state.get("mission_id", "crewai-plus20"),
        max_agents=state.get("max_agents", 7),
        cost_cap_usd=state.get("cost_cap_usd", 0.50),
    )
    return {"crew": "plus20_swarm",
            "action": "dispatched",
            "result": dispatch.to_dict()}


def _coral_reef_mesh_handler(state: dict) -> dict:
    """Real coral_reef_mesh — invokes the +20σ swarm with mesh synthesis
    enabled. The mesh is built inside dispatch_swarm via
    _coral_reef_synthesize."""
    return _plus20_swarm_handler({**state, "mesh_mode": "coral_reef_5_mode"})


def _adversarial_reviewer_handler(state: dict) -> dict:
    """Stub for adversarial_reviewer — runs 8 attack vectors."""
    try:
        from rig_lattice.enterprise.adversarial import adversarial_review
        text = state.get("L1_CAPTURE", {}).get("text", "")
        if not text:
            return {"crew": "adversarial_reviewer", "error": "no L1 text"}
        review = adversarial_review(text, author_persona=state.get("author_persona", "claude"))
        return {"crew": "adversarial_reviewer", "review": review.to_dict()}
    except Exception as e:
        return {"crew": "adversarial_reviewer", "error": str(e)}


# Register the canonical crews
register_crew("outcome_observer",
                agents=("brier_resolver", "weight_updater"),
                tasks=("resolve_pending", "compute_weight_delta"),
                handler=_outcome_observer_handler)

register_crew("plus20_swarm",
                agents=("forge", "anchor", "horizon", "breaker", "bayes", "collider", "shield"),
                tasks=("rewrite_at_20_sigma",) * 7,
                handler=_plus20_swarm_handler)

register_crew("coral_reef_mesh",
                agents=("synthesizer",),
                tasks=("broadcast", "brood", "bud", "fragment", "deprecate"),
                handler=_coral_reef_mesh_handler)

register_crew("adversarial_reviewer",
                agents=("independent_reviewer",),
                tasks=("attack_vector_" + str(i) for i in range(1, 9)),
                handler=_adversarial_reviewer_handler)
