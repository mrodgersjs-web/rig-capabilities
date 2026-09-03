"""A1.4 — Solution (PYTHON_ONLY).

Does: assemble a Draft from a templated artifact body plus an OPTIONAL
<=60-word personalization shim. This is the ONLY place A1 may touch an LLM
(a Haiku shim with max_tokens enforced). The shim is injected, never inline,
so the decision path stays model-free.

Doctrine:
  - No model in the decision path. The shim only personalizes a fixed slot.
  - Source-per-claim: the Draft carries the sources it was built from.
"""
from __future__ import annotations

from typing import Callable, Optional

from ._types import Draft, ResearchPack

# Hard cap on the personalization shim per A1 doctrine (<=60 words).
SHIM_WORD_LIMIT = 60

# Deterministic artifact body template. In production this is a Jinja
# template under templates/artifacts/. Kept inline here for runnability.
_ARTIFACT_TEMPLATE = (
    "Summary based on {n} sourced record(s): {headline}"
)

# A shim function takes the research rows and returns a short personalization
# string. Signature kept narrow so a Haiku wrapper can drop in unchanged.
ShimFn = Callable[[ResearchPack], str]


def _clamp_shim(text: str) -> str:
    words = text.split()
    if len(words) <= SHIM_WORD_LIMIT:
        return text.strip()
    return " ".join(words[:SHIM_WORD_LIMIT]).strip()


def _default_headline(pack: ResearchPack) -> str:
    if not pack.rows:
        return "no records found"
    first = pack.rows[0]
    # Deterministic: pick the first non-underscore string field.
    for k, v in first.items():
        if not k.startswith("_") and isinstance(v, str):
            return v
    return "record available"


def build_solution(pack: ResearchPack, shim: Optional[ShimFn] = None) -> Draft:
    body = _ARTIFACT_TEMPLATE.format(
        n=len(pack.rows), headline=_default_headline(pack)
    )
    personalization = ""
    if shim is not None:
        personalization = _clamp_shim(shim(pack))
    return Draft(body=body, personalization=personalization, sources=list(pack.sources))


def run(pack: ResearchPack, shim: Optional[ShimFn] = None) -> Draft:
    return build_solution(pack, shim)
