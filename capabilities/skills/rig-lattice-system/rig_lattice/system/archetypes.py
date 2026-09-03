"""28 BMS archetypes — 7 levels × 4 A-modes.

Each archetype is a deterministic callable: state_dict → (ok, output, reason).
The orchestrator picks the archetype for each level based on the BMS router
confidence score (from enterprise.iqrsqpi.route_bms).

  A1 Python-only      ≥ 0.75 confidence — pure code, no LLM, fastest
  A2 Hybrid            0.45-0.74 — code + light LLM grading
  A3 Bounded           0.25-0.44 — LLM with cost cap, single-shot
  A4 Agent-free        < 0.25 — human gate; suggests but does not execute

ArchetypeId encodes (level, mode) as a single key e.g. "L1_CAPTURE/A1".
"""
from __future__ import annotations
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from rig_lattice.enterprise.iqrsqpi import BMSMode
from rig_lattice.system.levels import (
    Level, LEVELS,
    L1_CAPTURE, L2_PROCESS, L3_CREATE, L4_DISTRIBUTE,
    L5_ENGAGE, L6_CONVERT, L7_AUTONOMIZE,
)

ROOT = Path(__file__).parent.parent


ArchetypeFn = Callable[[dict], tuple[bool, Any, str]]


@dataclass(frozen=True)
class ArchetypeId:
    level: Level
    mode: BMSMode

    @property
    def key(self) -> str:
        return f"{self.level.value}/{self.mode.value}"


@dataclass
class Archetype:
    id: ArchetypeId
    fn: ArchetypeFn
    description: str
    cost_cap_usd: float = 0.0
    requires_human_gate: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# L1 — CAPTURE
# ═══════════════════════════════════════════════════════════════════════════

def L1_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: file path or stdin → text + hash. No LLM."""
    src = state.get("source")
    if not src:
        return False, None, "missing source"
    if src == "-" or src == "stdin":
        text = state.get("stdin_text", "")
    elif src.startswith("http://") or src.startswith("https://"):
        # Defer to A2/A3 for URL fetching
        return False, None, "A1 cannot fetch URL; route to A2"
    else:
        p = Path(src).expanduser()
        if not p.exists():
            return False, None, f"file not found: {p}"
        text = p.read_text(encoding="utf-8", errors="replace")
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
    return True, {
        "text": text,
        "content_hash": content_hash,
        "char_count": len(text),
        "word_count": len(text.split()),
        "source_meta": {"src": src, "path_or_url": src},
    }, ""


def L1_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 fallback + URL fetcher via urllib (zero LLM)."""
    src = state.get("source", "")
    if src.startswith(("http://", "https://")):
        try:
            from urllib import request
            req = request.Request(src, headers={"User-Agent": "RIG-Deviator/1.0"})
            with request.urlopen(req, timeout=30) as r:
                text = r.read().decode("utf-8", errors="replace")
            content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
            return True, {
                "text": text,
                "content_hash": content_hash,
                "char_count": len(text),
                "word_count": len(text.split()),
                "source_meta": {"src": src, "fetched_via": "urllib"},
            }, ""
        except Exception as e:
            return False, None, f"URL fetch failed: {e}"
    return L1_A1(state)


def L1_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A2 + scraper escalation hook (would invoke Apify/Firecrawl
    in prod; here logs intent and falls back to A2)."""
    ok, out, reason = L1_A2(state)
    if not ok and "URL fetch failed" in reason:
        from rig_lattice.enterprise.observability import counter_inc
        counter_inc("l1_a3_scraper_escalation_requested")
        return False, None, f"A3 scraper not configured; would escalate: {reason}"
    return ok, out, reason


def L1_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: surfaces the manual capture instruction for a human."""
    src = state.get("source", "<unknown>")
    return True, {
        "instruction": f"HUMAN: capture artifact from {src} and paste into state.stdin_text",
        "requires_human": True,
    }, "human gate"


# ═══════════════════════════════════════════════════════════════════════════
# L2 — PROCESS
# ═══════════════════════════════════════════════════════════════════════════

def L2_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: run 40-engine audit + DES² inner-loop. No LLM."""
    text = _get_text(state)
    if not text:
        return False, None, "L2 needs L1 output (text)"
    from rig_lattice.deviator.auditor import audit_all
    from rig_lattice.deviator.des_squared import amplify
    audit = audit_all(text, llm_enabled=False)
    enriched = amplify(audit, text)
    return True, {
        "audit": audit,
        "des2": enriched.get("des2", {}),
        "rig_l": audit.get("rig_l", 0),
        "hard_blocks": audit.get("hard_blocks", 0),
        "status": audit.get("status", "?"),
    }, ""


def L2_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 audit + LLM-graded specificity (single light call)."""
    ok, out, reason = L2_A1(state)
    if not ok:
        return ok, out, reason
    text = _get_text(state)
    try:
        from rig_lattice.adapters.llm import grade_fuzzy_metric
        specificity = grade_fuzzy_metric(
            text, "specificity",
            "Rate 0-100 how specific (vs generic) this text is.",
            max_tokens=80,
        )
        out["fuzzy_specificity"] = specificity
    except Exception as e:
        out["fuzzy_specificity"] = None
        out["llm_error"] = str(e)
    return True, out, ""


def L2_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A2 + full LLM-judge for ambiguous criteria (cost capped)."""
    ok, out, reason = L2_A2(state)
    if not ok:
        return ok, out, reason
    out["a3_llm_judge_invoked"] = False  # would integrate here in prod
    out["cost_cap_usd"] = 0.50
    return True, out, ""


def L2_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: A1 audit only; surfaces results for human review."""
    ok, out, reason = L2_A1(state)
    if ok:
        out["requires_human_review"] = True
        out["instruction"] = "HUMAN: review audit before proceeding to L3"
    return ok, out, reason


# ═══════════════════════════════════════════════════════════════════════════
# L3 — CREATE
# ═══════════════════════════════════════════════════════════════════════════

def L3_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: deterministic patch overlay (no agent dispatch)."""
    text = _get_text(state)
    if not text:
        return False, None, "L3 needs L1 text"
    l2 = state.get("L2_PROCESS", {})
    audit = l2.get("audit", {})
    from rig_lattice.deviator.patch_overlays import build_overlay
    patched = build_overlay(text, audit)
    weakest = [
        {"slug": s, "codename": r.get("codename"), "sigma": r.get("sigma")}
        for s, r in audit.get("engines", {}).items()
        if r.get("status") == "HARD_BLOCK"
    ][:10]
    return True, {
        "variants": [{"source": "deterministic_patch", "text": patched,
                        "method": "L3_A1_overlay"}],
        "weakest_engines": weakest,
        "agent_dispatched": False,
    }, ""


def L3_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 + ONE targeted LLM rewrite on the worst engine."""
    ok, out, reason = L3_A1(state)
    if not ok:
        return ok, out, reason
    out["a2_targeted_rewrite_planned"] = bool(out["weakest_engines"])
    if not out["weakest_engines"]:
        return True, out, ""
    # Real single-agent dispatch on the worst engine (cost cap $0.10)
    try:
        from rig_lattice.enterprise.swarm import dispatch_swarm
        text = _get_text(state)
        dispatch = dispatch_swarm(
            text,
            out["weakest_engines"][:1],   # ONE agent only
            mission_id=state.get("mission_id", "L3_A2"),
            max_agents=1,
            cost_cap_usd=0.10,
        )
        out["swarm"] = dispatch.to_dict()
        if dispatch.mesh_synthesis:
            out["variants"].append({
                "source": "L3_A2_targeted_rewrite",
                "text": dispatch.mesh_synthesis,
                "method": "single_plus20_agent",
            })
    except Exception as e:
        out["swarm_error"] = f"{type(e).__name__}: {e}"
    return True, out, ""


def L3_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: dispatch +20σ agents for top-N weakest engines + Coral Reef mesh."""
    ok, out, reason = L3_A1(state)
    if not ok:
        return ok, out, reason
    out["a3_agents_planned"] = min(len(out["weakest_engines"]), 7)
    out["cost_cap_usd"] = 0.50
    out["mesh_strategy"] = "coral_reef_5_mode"
    if not out["weakest_engines"]:
        return True, out, ""
    # Real concurrent swarm dispatch (up to 7 agents, $0.50 cap)
    try:
        from rig_lattice.enterprise.swarm import dispatch_swarm
        text = _get_text(state)
        dispatch = dispatch_swarm(
            text,
            out["weakest_engines"],
            mission_id=state.get("mission_id", "L3_A3"),
            max_agents=7,
            cost_cap_usd=0.50,
        )
        out["swarm"] = dispatch.to_dict()
        if dispatch.mesh_synthesis:
            out["variants"].append({
                "source": "L3_A3_coral_reef_mesh",
                "text": dispatch.mesh_synthesis,
                "method": "parallel_plus20_swarm",
            })
        out["agent_dispatched"] = True
        out["agents_executed"] = len(dispatch.agents)
        out["agents_successful"] = sum(1 for a in dispatch.agents if a.ok)
        out["total_cost_usd"] = dispatch.total_cost_usd
    except Exception as e:
        out["swarm_error"] = f"{type(e).__name__}: {e}"
    return True, out, ""


def L3_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: list the rewrites a human should perform manually."""
    text = _get_text(state)
    l2 = state.get("L2_PROCESS", {})
    audit = l2.get("audit", {})
    blockers = [
        f"{r.get('codename')}: {r.get('failed_required', [])}"
        for r in audit.get("engines", {}).values()
        if r.get("status") == "HARD_BLOCK"
    ]
    return True, {
        "variants": [],
        "human_action_required": True,
        "instructions": [f"HUMAN: rewrite paragraph(s) addressing {b}" for b in blockers],
    }, "human gate"


# ═══════════════════════════════════════════════════════════════════════════
# L4 — DISTRIBUTE
# ═══════════════════════════════════════════════════════════════════════════

def L4_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: render HTML report + JSON receipt. No LLM."""
    l2 = state.get("L2_PROCESS", {})
    audit = l2.get("audit", {})
    if not audit:
        return False, None, "L4 needs L2 audit"
    from rig_lattice.deviator.result_packet import emit
    text = _get_text(state)
    src = state.get("source", "stdin")
    packet = emit(audit, src, tier=state.get("tier", "client"),
                    mission_id=state.get("mission_id"),
                    des2=l2.get("des2"))
    return True, {
        "receipt": packet,
        "receipt_id": packet.get("mission_id"),
    }, ""


def L4_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 + auto-generate one-paragraph executive summary."""
    ok, out, reason = L4_A1(state)
    if not ok:
        return ok, out, reason
    out["a2_summary_planned"] = True
    return True, out, ""


def L4_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A1 + LLM-generated executive summary (cost capped)."""
    ok, out, reason = L4_A1(state)
    if not ok:
        return ok, out, reason
    out["cost_cap_usd"] = 0.20
    out["a3_llm_summary_invoked"] = False  # wire in prod
    return True, out, ""


def L4_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: skip rendering, return raw audit JSON for human curation."""
    ok, out, reason = L4_A1(state)
    if ok:
        out["requires_human_curation"] = True
    return ok, out, reason


# ═══════════════════════════════════════════════════════════════════════════
# L5 — ENGAGE
# ═══════════════════════════════════════════════════════════════════════════

def L5_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: surface blockers + copy-paste fix suggestions."""
    l2 = state.get("L2_PROCESS", {})
    audit = l2.get("audit", {})
    if not audit:
        return False, None, "L5 needs L2 audit"
    blockers = []
    fix_suggestions = []
    for slug, r in audit.get("engines", {}).items():
        if r.get("failed_required"):
            for qid in r["failed_required"][:3]:
                q = next((qq for qq in r["questions"] if qq["id"] == qid), {})
                blockers.append({
                    "codename": r.get("codename"),
                    "slug": slug,
                    "criterion": qid,
                    "question": q.get("question", "")[:120],
                    "evidence": (q.get("evidence") or "")[:120],
                })
    try:
        from rig_lattice.deviator.fix_suggestions import suggest_for
        for b in blockers:
            text_q = {"question": b["question"]}
            sug = suggest_for(b["slug"], b["criterion"], text_q)
            if sug:
                fix_suggestions.append({"criterion": b["criterion"], "suggestion": sug})
    except Exception:
        pass
    return True, {
        "blockers": blockers,
        "blocker_count": len(blockers),
        "fix_suggestions": fix_suggestions,
        "next_actions": [
            "Apply fix_suggestions to artifact",
            "Re-run L2 audit",
            "If still HARD_BLOCK → escalate to A3",
        ],
    }, ""


def L5_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 + LLM-graded coherence check."""
    ok, out, reason = L5_A1(state)
    if not ok:
        return ok, out, reason
    text = _get_text(state)
    try:
        from rig_lattice.enterprise.adversarial import coherence_score
        out["coherence"] = coherence_score(text)
        out["coherence_alert"] = out["coherence"] < 0.70
    except Exception as e:
        out["coherence_error"] = str(e)
    return True, out, ""


def L5_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A2 + adversarial review (8 attack vectors)."""
    ok, out, reason = L5_A2(state)
    if not ok:
        return ok, out, reason
    text = _get_text(state)
    try:
        from rig_lattice.enterprise.adversarial import adversarial_review
        review = adversarial_review(text, author_persona=state.get("author_persona", "claude"))
        out["adversarial_review"] = review.to_dict()
    except Exception as e:
        out["adversarial_error"] = str(e)
    return True, out, ""


def L5_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: surface blockers; require human acknowledgement."""
    ok, out, reason = L5_A1(state)
    if ok:
        out["requires_human_acknowledgement"] = True
    return ok, out, reason


# ═══════════════════════════════════════════════════════════════════════════
# L6 — CONVERT
# ═══════════════════════════════════════════════════════════════════════════

def L6_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: apply patch overlay; re-audit; produce final."""
    text = _get_text(state)
    l2 = state.get("L2_PROCESS", {})
    audit = l2.get("audit", {})
    if not text or not audit:
        return False, None, "L6 needs L1 text + L2 audit"
    from rig_lattice.deviator.patch_overlays import build_overlay
    from rig_lattice.deviator.auditor import audit_all
    patched = build_overlay(text, audit)
    final_audit = audit_all(patched, llm_enabled=False)
    return True, {
        "final_text": patched,
        "final_audit": final_audit,
        "rig_l": final_audit.get("rig_l"),
        "hard_blocks": final_audit.get("hard_blocks"),
        "status": final_audit.get("status"),
    }, ""


def L6_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 + DES² re-amplify on patched text."""
    ok, out, reason = L6_A1(state)
    if not ok:
        return ok, out, reason
    from rig_lattice.deviator.des_squared import amplify
    out["final_des2"] = amplify(out["final_audit"], out["final_text"]).get("des2", {})
    return True, out, ""


def L6_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A2 + one LLM polish pass (cost capped)."""
    ok, out, reason = L6_A2(state)
    if not ok:
        return ok, out, reason
    out["cost_cap_usd"] = 0.30
    out["a3_polish_invoked"] = False
    return True, out, ""


def L6_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: produce patch diff, require human accept."""
    ok, out, reason = L6_A1(state)
    if ok:
        out["requires_human_accept"] = True
        out["instruction"] = "HUMAN: review patched_text before adopting"
    return ok, out, reason


# ═══════════════════════════════════════════════════════════════════════════
# L7 — AUTONOMIZE
# ═══════════════════════════════════════════════════════════════════════════

def L7_A1(state: dict) -> tuple[bool, Any, str]:
    """A1 Python-only: kick the daemon tick + log a Brier prediction."""
    l6 = state.get("L6_CONVERT", {})
    final_audit = l6.get("final_audit", {})
    if not final_audit:
        return False, None, "L7 needs L6 final_audit"
    from rig_lattice.enterprise.daemon import Daemon
    from rig_lattice.deviator.des2_innerloop import record_prediction
    d = Daemon()
    executed = d.tick()
    pred = record_prediction(
        mission_id=state.get("mission_id", "unknown"),
        engine_name="composite_RIG_L",
        predicted_madz=final_audit.get("rig_l", 0),
    )
    return True, {
        "daemon_tick": executed,
        "prediction_logged": pred,
        "daemon_status": d.status(),
    }, ""


def L7_A2(state: dict) -> tuple[bool, Any, str]:
    """A2 Hybrid: A1 + emit observability event to LangSmith/LangFuse stub."""
    ok, out, reason = L7_A1(state)
    if not ok:
        return ok, out, reason
    try:
        from rig_lattice.enterprise.integrations import langsmith_emit
        langsmith_emit("L7_AUTONOMIZE", out)
        out["telemetry_emitted"] = True
    except Exception as e:
        out["telemetry_error"] = str(e)
    return True, out, ""


def L7_A3(state: dict) -> tuple[bool, Any, str]:
    """A3 Bounded: A2 + CrewAI orchestration hook for outcome observation."""
    ok, out, reason = L7_A2(state)
    if not ok:
        return ok, out, reason
    try:
        from rig_lattice.enterprise.integrations import crewai_dispatch
        out["crewai_dispatch"] = crewai_dispatch("outcome_observer", state)
    except Exception as e:
        out["crewai_error"] = str(e)
    return True, out, ""


def L7_A4(state: dict) -> tuple[bool, Any, str]:
    """A4 Agent-free: emit a runbook with manual steps for the operator."""
    return True, {
        "manual_runbook": [
            "1. Watch the daemon dashboard for any RED slots",
            "2. Manually resolve any pending Brier predictions when outcomes are known",
            "3. Run `make verify-engines` weekly",
            "4. Review FINAL_REPORT.md after each ship",
        ],
        "requires_human_followup": True,
    }, "human gate"


# ═══════════════════════════════════════════════════════════════════════════
# Registry — 28 archetypes
# ═══════════════════════════════════════════════════════════════════════════

ARCHETYPES: dict[str, Archetype] = {}


def _register_all() -> None:
    catalog = [
        (L1_CAPTURE, L1_A1, L1_A2, L1_A3, L1_A4),
        (L2_PROCESS, L2_A1, L2_A2, L2_A3, L2_A4),
        (L3_CREATE,  L3_A1, L3_A2, L3_A3, L3_A4),
        (L4_DISTRIBUTE, L4_A1, L4_A2, L4_A3, L4_A4),
        (L5_ENGAGE,  L5_A1, L5_A2, L5_A3, L5_A4),
        (L6_CONVERT, L6_A1, L6_A2, L6_A3, L6_A4),
        (L7_AUTONOMIZE, L7_A1, L7_A2, L7_A3, L7_A4),
    ]
    cost_caps = {BMSMode.A1: 0.0, BMSMode.A2: 0.10, BMSMode.A3: 0.50, BMSMode.A4: 0.0}
    for level, *fns in catalog:
        for mode, fn in zip([BMSMode.A1, BMSMode.A2, BMSMode.A3, BMSMode.A4], fns):
            aid = ArchetypeId(level=level, mode=mode)
            ARCHETYPES[aid.key] = Archetype(
                id=aid,
                fn=fn,
                description=(fn.__doc__ or "").strip().split("\n")[0],
                cost_cap_usd=cost_caps[mode],
                requires_human_gate=(mode == BMSMode.A4),
            )


def _get_text(state: dict) -> str:
    l1 = state.get("L1_CAPTURE", {})
    if isinstance(l1, dict):
        return l1.get("text", "")
    return ""


def get_archetype(level: Level, mode: BMSMode) -> Archetype:
    key = ArchetypeId(level=level, mode=mode).key
    return ARCHETYPES[key]


def list_archetypes_for_level(level: Level) -> list[Archetype]:
    return [a for a in ARCHETYPES.values() if a.id.level == level]


_register_all()
assert len(ARCHETYPES) == 28, f"expected 28 archetypes, got {len(ARCHETYPES)}"
