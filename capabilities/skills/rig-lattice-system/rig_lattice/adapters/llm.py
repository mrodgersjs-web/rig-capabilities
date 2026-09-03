"""DOCTRINE.md §5 — LLM adapter for fuzzy metrics.

Wraps any OpenAI-compatible chat-completions endpoint via a simple HTTP call.
Defaults to llama3.3:70b on rig-256gb (Tailscale + Ollama). Falls back to
OFFLINE_MODE which returns deterministic-but-conservative pseudo-scores when
the LLM is unavailable.

Used for fuzzy metrics that can't be regex'd:
  - Mechanism clarity     (FORGE / MechanismFurnace)
  - Memory residue        (ECHO / MemoryResidue)
  - Causal completeness   (FORGE inner amplifier)
  - Specificity grading   (SpecificityGate)

This is a thin adapter. The full per-engine prompts live in each engine module.
"""
from __future__ import annotations
import json
import os
import re
import time
from dataclasses import dataclass
from urllib import request as ur

DEFAULT_URL = (
    os.environ.get("RIG_DV_LLM_URL")            # deprecated alias, read first
    or os.environ.get("RIG_LATTICE_LLM_URL")
    or "http://127.0.0.1:11434/v1/chat/completions"
)
DEFAULT_MODEL = (
    os.environ.get("RIG_DV_LLM_MODEL")
    or os.environ.get("RIG_LATTICE_LLM_MODEL")
    or "llama3.3:70b"
)
DEFAULT_TIMEOUT = int(os.environ.get("RIG_DV_LLM_TIMEOUT", "120"))
def offline_mode() -> bool:
    """True when RIG_DV_OFFLINE=1, read live on every call.

    This used to be a module-level constant evaluated at import time, which
    silently ignored any process that set RIG_DV_OFFLINE after the first
    import of this module — the documented env switch did not work once
    anything else had imported the adapter. Callers must call this function.
    """
    return os.environ.get("RIG_DV_OFFLINE", "0") == "1"


# Back-compat name. Deliberately a snapshot of the value at import time; new
# code calls offline_mode() instead.
OFFLINE_MODE = offline_mode()


@dataclass(frozen=True)
class LLMResponse:
    ok: bool
    content: str
    score: float | None  # parsed numeric score if extractable
    elapsed_s: float
    reason: str = ""    # error reason if !ok


def _parse_score(text: str) -> float | None:
    """Extract a numeric score from LLM response. Looks for 'SCORE: NN' first,
    then any number 0–100 at the start of a line."""
    m = re.search(r"SCORE:\s*([+-]?\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    m = re.search(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(?:/100)?\s*$", text, re.MULTILINE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def llm_score(prompt: str,
                model: str | None = None,
                url: str | None = None,
                timeout: int | None = None,
                temperature: float = 0.0,
                max_tokens: int = 200,
                mission_id: str | None = None,
                purpose: str = "") -> LLMResponse:
    """Call the LLM, parse a 0-100 score from the response.

    When `mission_id` is provided, the call is recorded to the cost
    ledger (`enterprise.cost_ledger.record_llm_cost`). If the mission has
    a budget set and this call would exceed it, BudgetExceededError is
    raised BEFORE the LLM is contacted.
    """
    used_model = model or DEFAULT_MODEL

    # ── Pre-flight budget check ──────────────────────────────────────
    if mission_id:
        try:
            from rig_lattice.enterprise.cost_ledger import estimate_cost, mission_remaining
            est_in_tokens = max(1, len(prompt) // 4)  # ~4 chars/token rough
            _, _, est_total = estimate_cost(used_model, est_in_tokens, max_tokens)
            remaining = mission_remaining(mission_id)
            if remaining is not None and est_total > remaining:
                # Would blow the budget — short-circuit to median.
                return LLMResponse(
                    ok=False,
                    content=f"BUDGET: ${est_total:.4f} > remaining ${remaining:.4f}",
                    score=50.0, elapsed_s=0.0,
                    reason="budget_would_exceed",
                )
        except Exception:
            # Cost ledger optional — don't crash the call
            pass

    if offline_mode():
        # Record zero-cost offline entry so call counts are still tracked
        if mission_id:
            try:
                from rig_lattice.enterprise.cost_ledger import record_llm_cost
                record_llm_cost(mission_id, used_model, in_tokens=0,
                                out_tokens=0, purpose=purpose or "offline",
                                enforce_budget=False)
            except Exception:
                pass
        return LLMResponse(ok=True, content="OFFLINE_MODE: returning median 50",
                            score=50.0, elapsed_s=0.0)

    t0 = time.time()
    payload = {
        "model": used_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        req = ur.Request(url or DEFAULT_URL,
                         data=json.dumps(payload).encode("utf-8"),
                         headers={"Content-Type": "application/json"},
                         method="POST")
        with ur.urlopen(req, timeout=timeout or DEFAULT_TIMEOUT) as r:
            body = json.loads(r.read().decode("utf-8"))
        msg = body["choices"][0]["message"]
        content = (msg.get("content") or msg.get("reasoning") or "").strip()
        elapsed = time.time() - t0

        # ── Cost ledger ──────────────────────────────────────────────
        usage = body.get("usage", {}) or {}
        in_tokens = int(usage.get("prompt_tokens") or len(prompt) // 4)
        out_tokens = int(usage.get("completion_tokens") or len(content) // 4)
        if mission_id:
            try:
                from rig_lattice.enterprise.cost_ledger import record_llm_cost
                record_llm_cost(mission_id, used_model,
                                in_tokens=in_tokens, out_tokens=out_tokens,
                                purpose=purpose or "llm_score",
                                enforce_budget=False)  # post-hoc record
            except Exception:
                pass

        return LLMResponse(ok=True, content=content,
                            score=_parse_score(content), elapsed_s=round(elapsed, 1))
    except Exception as e:
        elapsed = time.time() - t0
        # On any error, degrade to neutral median rather than fail the audit.
        return LLMResponse(ok=False,
                            content=f"LLM error: {type(e).__name__}: {e}",
                            score=50.0, elapsed_s=round(elapsed, 1),
                            reason=str(e))


def grade_fuzzy_metric(text: str, metric_name: str,
                        rubric: str, max_tokens: int = 100) -> float:
    """Convenience: grade `text` on a single fuzzy metric.

    Returns a 0-100 score. Used by engines that need beyond-regex judgment
    (mechanism clarity, memory residue, specificity grade).
    """
    prompt = (
        f"You are a strict doctrine auditor scoring text on ONE metric.\n\n"
        f"METRIC: {metric_name}\n"
        f"RUBRIC:\n{rubric}\n\n"
        f"TEXT TO SCORE (first 6000 chars):\n---\n{text[:6000]}\n---\n\n"
        "Respond with EXACTLY this format on TWO lines:\n"
        "SCORE: <0-100>\n"
        "WHY: <one sentence>\n\n"
        "Be strict. Score 0-30 if the metric is absent, 30-60 if partial, "
        "60-80 if good, 80-100 only if exemplary."
    )
    resp = llm_score(prompt, max_tokens=max_tokens)
    return resp.score if resp.score is not None else 50.0
