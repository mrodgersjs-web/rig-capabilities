"""chunk_agent.py — the Pydantic AI lane for fanned-out chunks.

Two facts this module is built around, both verified 2026-09-15:

  * PAIR speaks Chat Completions, NOT the OpenAI Responses API. `GET /v1/responses` with
    `qwen3:4b` returned 404 even though the model is in the cluster inventory. Pydantic AI
    defaults to a Responses-API model for OpenAI, so the lane MUST pin `OpenAIChatModel`
    (pydantic.dev/docs/ai/models/openai: select OpenAIChatModel for Chat Completions-compatible
    servers). Using the default class silently targets an endpoint PAIR does not serve.
  * PAIR is loopback-only. A worker on another machine cannot reach this Mac's :11435; it must
    call its OWN local PAIR, which then places the request on an eligible node. `base_url` is
    therefore a parameter, defaulted to loopback, never a hardcoded LAN address.

The model proposes through a typed boundary and deterministic code accepts or rejects the
result (D85: a decision may be model-proposed but the verdict stays in code). `run_typed`
returns the validated object or raises — it never returns an unvalidated blob.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

PAIR_OPENAI_BASE = "http://127.0.0.1:11435/v1"
# PAIR performs no auth on the loopback proxy; the OpenAI client still requires a non-empty
# key, so this is a placeholder, not a credential. Never read a real secret here.
PAIR_PLACEHOLDER_KEY = "pair-local-no-auth"

T = TypeVar("T")


class AgentLaneError(Exception):
    """The lane could not run: missing dependency, unreachable PAIR, or invalid model output."""


@dataclass(frozen=True)
class LaneConfig:
    model: str
    base_url: str = PAIR_OPENAI_BASE
    retries: int = 2


def pair_model(config: LaneConfig):
    """Build a Pydantic AI model bound to PAIR. Import is local so that merely importing this
    module does not require pydantic-ai to be installed in the caller's environment."""
    try:
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.openai import OpenAIProvider
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise AgentLaneError(
            "pydantic-ai is not installed in this interpreter. Verified 2026-09-15: "
            "~/.hermes/hermes-agent/venv has pydantic_ai; ~/.rig/meta-harness/.venv has "
            "temporalio but NOT pydantic_ai. No environment currently has both."
        ) from exc
    return OpenAIChatModel(
        config.model,
        provider=OpenAIProvider(base_url=config.base_url, api_key=PAIR_PLACEHOLDER_KEY),
    )


def run_typed(prompt: str, output_type: type[T], config: LaneConfig, *, instructions: str = "") -> T:
    """Run one chunk and return a VALIDATED `output_type`. Schema violations raise rather than
    degrade into free text, so a caller can never mistake a malformed answer for a result."""
    try:
        from pydantic_ai import Agent
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise AgentLaneError("pydantic-ai is not installed in this interpreter") from exc
    agent = Agent(
        pair_model(config),
        output_type=output_type,
        instructions=instructions or "Answer exactly what is asked. No preamble, no explanation.",
        retries=config.retries,
    )
    try:
        return agent.run_sync(prompt).output
    except AgentLaneError:
        raise
    except Exception as exc:  # pydantic-ai raises validation/transport errors of many types
        raise AgentLaneError(f"{type(exc).__name__}: {exc}") from exc
