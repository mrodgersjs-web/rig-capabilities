"""Enterprise +20σ Swarm — concurrent LLM-backed agent dispatch for L3 A3.

Per DOCTRINE.md §3 — the L3 CREATE layer with BMS A3 dispatches N parallel
+20σ agents, each tasked with rewriting the artifact to clear ONE specific
weak engine. Results are merged via Coral Reef synthesis (5 reproduction
modes from `nature` layer).

Key contracts:
  - max_agents: caller-controlled cap (default 7 per DOCTRINE)
  - cost_cap_usd: hard ceiling enforced per dispatch
  - concurrent execution via ThreadPoolExecutor (LLM calls are I/O bound)
  - every dispatch writes to audits/swarm.jsonl for forensics
  - offline mode → deterministic per-engine rewrite templates

In `RIG_DV_OFFLINE=1` mode (or when LLM is unreachable), the swarm produces
deterministic rewrites using the per-engine patch overlays already shipped
under `patch_overlays.py`. This keeps L3 A3 productive even without LLM
access.
"""
from __future__ import annotations
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
SWARM_LOG = AUDITS_DIR / "swarm.jsonl"

# ── Per-engine +20σ agent prompts (cognitive layer, top-7) ────────────────
# Each prompt asks the LLM to rewrite the artifact such that the named engine
# would score in the +20σ band. Real rewrites swap entire paragraphs.
_AGENT_PROMPTS: dict[str, dict] = {
    # ── Cognitive (1-20) ──
    "gravity_escape": {
        "role": "Forge — Mechanism-First Author",
        "prompt": (
            "Rewrite the artifact so that EVERY claim names an explicit "
            "mechanism, named system, or measured cause. Eliminate any "
            "abstract benefit-language not backed by HOW it happens."
        ),
        "target_engine": "Gravity Escape (Mechanism Furnace)",
    },
    "anti_slop_auditor": {
        "role": "Anchor — Specificity Surgeon",
        "prompt": (
            "Rewrite the artifact so every paragraph names: a real person, "
            "team, or system; a measurable threshold; a date or window; an "
            "evidence pointer. Strip every adjective that survives without "
            "a measurement."
        ),
        "target_engine": "Anti-Slop Auditor",
    },
    "structural_purifier": {
        "role": "Horizon — Structural Editor",
        "prompt": (
            "Rewrite so every section enforces parallel structure: one "
            "claim per paragraph, one mechanism per claim, one proof per "
            "mechanism. Delete fillers, hedges, and meta-commentary."
        ),
        "target_engine": "Structural Purifier",
    },
    "absolute_zero": {
        "role": "Breaker — Banned-Phrase Sweeper",
        "prompt": (
            "Rewrite to eliminate every banned absolute: 'always', 'never', "
            "'all', 'every', 'guaranteed', 'undefeated', 'first-ever'. "
            "Replace with measured, bounded claims with sample sizes."
        ),
        "target_engine": "Absolute Zero",
    },
    "specificity_gate": {
        "role": "Bayes — Number-First Author",
        "prompt": (
            "Rewrite so every paragraph contains at least one specific "
            "number, threshold, date, or named entity. Replace all vague "
            "quantifiers ('many', 'most', 'significant') with measurements."
        ),
        "target_engine": "Specificity Gate",
    },
    "evidence_anchor": {
        "role": "Collider — Evidence Cross-Linker",
        "prompt": (
            "Rewrite so every load-bearing claim names: the evidence "
            "type (study, log, internal data, A/B test), the source, and "
            "the recency. Add inline references where missing."
        ),
        "target_engine": "Evidence Anchor",
    },
    "compounding_edge": {
        "role": "Shield — Compounding-Loop Author",
        "prompt": (
            "Rewrite so the artifact explicitly identifies the compounding "
            "loop: input → flywheel mechanism → output → reinforcement → "
            "input. Show how the loop accelerates with scale."
        ),
        "target_engine": "Compounding Edge",
    },
    # ── Nature (21-30) ──
    "coral_reef": {
        "role": "Synthesizer — Coral Reef Mesh",
        "prompt": (
            "Rewrite to encode 5 reproduction modes: broadcast (mass "
            "distribution channel), brood (internal nurturing), bud "
            "(extension), fragment (resilience under stress), deprecate "
            "(graceful sunset)."
        ),
        "target_engine": "Coral Reef Synthesis",
    },
}

# Fallback prompt for any engine slug not explicitly named above
_GENERIC_PROMPT = {
    "role": "Generic +20σ Agent",
    "prompt": (
        "Rewrite the artifact so it would score in the top +20σ band on "
        "the named engine. Preserve all factual claims; replace generic "
        "language with measurable, mechanism-backed, evidence-anchored "
        "language."
    ),
    "target_engine": "<unspecified>",
}


@dataclass
class AgentResult:
    slug: str
    engine_name: str
    role: str
    ok: bool
    elapsed_s: float
    proposed_text: str
    score: float | None = None
    cost_usd: float = 0.0
    reason: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        # truncate text
        if len(d["proposed_text"]) > 800:
            d["proposed_text"] = d["proposed_text"][:800] + f"... ({len(self.proposed_text):,} chars)"
        return d


@dataclass
class SwarmDispatch:
    mission_id: str
    weak_engines: list[dict] = field(default_factory=list)
    agents: list[AgentResult] = field(default_factory=list)
    cost_cap_usd: float = 0.50
    total_cost_usd: float = 0.0
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    mesh_strategy: str = "coral_reef_5_mode"
    mesh_synthesis: str = ""           # final merged rewrite

    @property
    def elapsed_s(self) -> float:
        end = self.completed_at if self.completed_at else time.time()
        return end - self.started_at

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "weak_engines": self.weak_engines,
            "agent_count": len(self.agents),
            "successful_agents": sum(1 for a in self.agents if a.ok),
            "elapsed_s": round(self.elapsed_s, 2),
            "cost_cap_usd": self.cost_cap_usd,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "mesh_strategy": self.mesh_strategy,
            "mesh_synthesis_chars": len(self.mesh_synthesis),
            "mesh_synthesis_preview": self.mesh_synthesis[:400],
            "agents": [a.to_dict() for a in self.agents],
        }


def _agent_prompt_for(slug: str, codename: str) -> dict:
    if slug in _AGENT_PROMPTS:
        return _AGENT_PROMPTS[slug]
    p = dict(_GENERIC_PROMPT)
    p["target_engine"] = codename or slug
    return p


def _build_full_prompt(text: str, agent_def: dict) -> str:
    """Construct the rewrite prompt for a single +20σ agent."""
    return (
        f"You are {agent_def['role']}.\n"
        f"Target engine: {agent_def['target_engine']}\n\n"
        f"TASK: {agent_def['prompt']}\n\n"
        f"ARTIFACT TO REWRITE (first 6000 chars):\n---\n{text[:6000]}\n---\n\n"
        f"OUTPUT FORMAT:\n"
        f"PROPOSED_REWRITE:\n<the full rewritten artifact>\n\n"
        f"CONFIDENCE: <0-100>\n\n"
        f"Be terse. No commentary. Just the rewrite."
    )


def _deterministic_rewrite(text: str, slug: str) -> str:
    """Offline mode fallback — apply existing patch overlay for this engine."""
    try:
        from rig_lattice.deviator.patch_overlays import build_overlay
        # Build a minimal audit fragment that triggers the slug's overlay
        fake_audit = {
            "engines": {
                slug: {
                    "slug": slug,
                    "codename": slug.replace("_", " ").title(),
                    "status": "HARD_BLOCK",
                    "failed_required": ["all"],
                }
            }
        }
        return build_overlay(text, fake_audit)
    except Exception:
        return text


def dispatch_swarm(text: str,
                    weak_engines: list[dict],
                    *,
                    mission_id: str = "swarm-adhoc",
                    max_agents: int = 7,
                    cost_cap_usd: float = 0.50,
                    cost_per_call_usd: float = 0.07,
                    timeout_s: int = 60) -> SwarmDispatch:
    """Dispatch up to `max_agents` concurrent +20σ rewrite agents.

    Args:
        text: the artifact to rewrite
        weak_engines: list of {slug, codename, sigma} from L2 audit
        mission_id: parent mission for forensics
        max_agents: hard cap on parallel agents (default 7 per DOCTRINE)
        cost_cap_usd: hard total-cost ceiling
        cost_per_call_usd: estimated per-call cost (default $0.07)
        timeout_s: per-agent timeout

    Returns:
        SwarmDispatch with .agents list + .mesh_synthesis merged rewrite.
    """
    from rig_lattice.adapters.llm import llm_score, offline_mode

    targets = weak_engines[:max_agents]
    # Budget: max agents we can afford
    affordable = int(cost_cap_usd / max(cost_per_call_usd, 0.001))
    targets = targets[:affordable]

    dispatch = SwarmDispatch(
        mission_id=mission_id,
        weak_engines=[
            {"slug": t.get("slug"), "codename": t.get("codename"), "sigma": t.get("sigma")}
            for t in targets
        ],
        cost_cap_usd=cost_cap_usd,
    )

    def _run_agent(target: dict) -> AgentResult:
        slug = target.get("slug") or "?"
        codename = target.get("codename") or slug
        agent_def = _agent_prompt_for(slug, codename)
        t0 = time.time()

        if offline_mode():
            # Deterministic offline rewrite — record zero-cost call for telemetry
            try:
                from rig_lattice.enterprise.cost_ledger import record_llm_cost
                record_llm_cost(mission_id, "offline", in_tokens=0,
                                out_tokens=0, purpose=f"swarm_offline_{slug}",
                                enforce_budget=False)
            except Exception:
                pass
            rewrite = _deterministic_rewrite(text, slug)
            return AgentResult(
                slug=slug, engine_name=codename, role=agent_def["role"],
                ok=True, elapsed_s=time.time() - t0,
                proposed_text=rewrite, score=None, cost_usd=0.0,
                reason="offline_mode_deterministic",
            )

        prompt = _build_full_prompt(text, agent_def)
        resp = llm_score(prompt, max_tokens=2000, timeout=timeout_s,
                         mission_id=mission_id,
                         purpose=f"swarm_agent_{slug}")
        elapsed = time.time() - t0
        if resp.ok:
            # Extract the PROPOSED_REWRITE section
            content = resp.content
            if "PROPOSED_REWRITE:" in content:
                rewrite = content.split("PROPOSED_REWRITE:", 1)[1]
                # Strip trailing CONFIDENCE line if present
                rewrite = rewrite.split("\nCONFIDENCE:", 1)[0].strip()
            else:
                rewrite = content.strip()
            return AgentResult(
                slug=slug, engine_name=codename, role=agent_def["role"],
                ok=True, elapsed_s=elapsed, proposed_text=rewrite,
                score=resp.score, cost_usd=cost_per_call_usd,
                reason="",
            )
        return AgentResult(
            slug=slug, engine_name=codename, role=agent_def["role"],
            ok=False, elapsed_s=elapsed, proposed_text="",
            score=None, cost_usd=0.0, reason=resp.reason,
        )

    # Parallel dispatch
    with ThreadPoolExecutor(max_workers=min(len(targets), max_agents) or 1) as ex:
        futures = {ex.submit(_run_agent, t): t for t in targets}
        for fut in as_completed(futures, timeout=timeout_s * 2 + 10):
            try:
                result = fut.result()
                dispatch.agents.append(result)
                dispatch.total_cost_usd += result.cost_usd
            except Exception as e:
                dispatch.agents.append(AgentResult(
                    slug=futures[fut].get("slug", "?"),
                    engine_name=futures[fut].get("codename", "?"),
                    role="?", ok=False, elapsed_s=0.0,
                    proposed_text="", reason=f"{type(e).__name__}: {e}",
                ))

    # ── Coral Reef mesh synthesis ─────────────────────────────────────
    dispatch.mesh_synthesis = _coral_reef_synthesize(text, dispatch.agents)
    dispatch.completed_at = time.time()

    # Forensics log
    _log_dispatch(dispatch)
    return dispatch


def _coral_reef_synthesize(original: str, agents: list[AgentResult]) -> str:
    """Merge agent rewrites via Coral Reef 5-mode reproduction.

    Modes:
      - broadcast: union of all successful rewrites (largest variation)
      - brood:     pick highest-confidence rewrite (focused inheritance)
      - bud:       extend original with appendix of best rewrites
      - fragment:  pick the most-changed paragraphs across all rewrites
      - deprecate: filter out lowest-scoring rewrites

    Production version uses an LLM judge to pick the winning paragraph
    per section. Default deterministic mesh: pick the highest-confidence
    successful rewrite (brood mode).
    """
    successful = [a for a in agents if a.ok and a.proposed_text]
    if not successful:
        return original

    # Brood: highest confidence (or first if all None)
    best = max(
        successful,
        key=lambda a: a.score if a.score is not None else 50.0,
    )
    return best.proposed_text


def _log_dispatch(dispatch: SwarmDispatch) -> None:
    SWARM_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": dispatch.to_dict(),
    }
    with SWARM_LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def swarm_status() -> dict:
    """Read summary of recent swarm dispatches."""
    if not SWARM_LOG.exists():
        return {"total": 0, "recent": []}
    lines = SWARM_LOG.read_text().splitlines()
    recent = []
    for line in lines[-10:]:
        try:
            recent.append(json.loads(line))
        except Exception:
            pass
    return {"total": len(lines), "recent": recent}
