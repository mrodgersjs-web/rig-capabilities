"""LiteLLM integration — multi-provider LLM router with cost cap.

Wraps adapters/llm.py with provider-agnostic routing. If `litellm` package
is installed, routes through it (which handles 100+ providers). Otherwise
falls back to the existing adapters/llm.py path (Ollama on rig-256gb).
"""
from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Any


def litellm_available() -> bool:
    try:
        import litellm  # noqa: F401
        return True
    except ImportError:
        return False


@dataclass
class LLMCall:
    provider: str
    model: str
    prompt: str
    max_tokens: int
    temperature: float
    cost_cap_usd: float


@dataclass
class LLMResult:
    ok: bool
    content: str
    elapsed_s: float
    est_cost_usd: float
    provider: str
    reason: str = ""


def litellm_route(prompt: str,
                    model: str | None = None,
                    max_tokens: int = 500,
                    temperature: float = 0.0,
                    cost_cap_usd: float = 0.10) -> LLMResult:
    """Route a prompt to the best available LLM provider.

    Provider preference order:
      1. LiteLLM (if installed) → any provider
      2. Local Ollama (rig-256gb) via adapters/llm.py
      3. Offline median fallback (score=50)
    """
    t0 = time.time()
    m = model or os.environ.get("RIG_DV_DEFAULT_MODEL", "llama3.3:70b")

    # RIG_DV_OFFLINE=1 means "make no outbound model call". Check it before
    # reaching for litellm, not after: the vendored order called the network
    # first and only degraded on the resulting exception.
    from rig_lattice.adapters.llm import offline_mode

    if offline_mode():
        return _fallback_local(prompt, m, max_tokens, temperature, t0,
                                 reason="offline_mode")

    if litellm_available():
        try:
            import litellm  # type: ignore
            resp = litellm.completion(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = resp.choices[0].message.content
            est_cost = float(resp.get("response_cost", 0.0)) if hasattr(resp, "get") else 0.0
            elapsed = time.time() - t0
            return LLMResult(ok=True, content=content, elapsed_s=elapsed,
                              est_cost_usd=est_cost, provider="litellm")
        except Exception as e:
            return _fallback_local(prompt, m, max_tokens, temperature, t0,
                                     reason=f"litellm error: {e}")

    return _fallback_local(prompt, m, max_tokens, temperature, t0)


def _fallback_local(prompt: str, model: str, max_tokens: int,
                      temperature: float, t0: float, reason: str = "") -> LLMResult:
    from rig_lattice.adapters.llm import llm_score
    resp = llm_score(prompt, model=model, max_tokens=max_tokens,
                       temperature=temperature)
    elapsed = time.time() - t0
    return LLMResult(
        ok=resp.ok,
        content=resp.content,
        elapsed_s=elapsed,
        est_cost_usd=0.0,   # local model
        provider="local_ollama",
        reason=reason or resp.reason,
    )
