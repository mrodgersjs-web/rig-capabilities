"""A1.1 — Intent (PYTHON_ONLY).

Does: deterministic intent classification via keyword/regex maps.
Model: NONE. Cost: $0.
Doctrine: "Escalate, don't fail." On a miss, return IntentKey.UNKNOWN so
Hermes can route the cell up to A3.1.
"""
from __future__ import annotations

import re

from ._types import InboundPayload, IntentKey

# Deterministic intent map. In production this is hydrated from
# intent_maps/<studio>.yaml. Patterns are ordered; first match wins.
_INTENT_PATTERNS: list[tuple[IntentKey, re.Pattern[str]]] = [
    (IntentKey.LEAD_SCORE, re.compile(r"\b(score|qualify|rank)\b.*\blead", re.I)),
    (IntentKey.STATUS_LOOKUP, re.compile(r"\b(status|where is|track)\b", re.I)),
    (IntentKey.INVENTORY_CHECK, re.compile(r"\b(in stock|inventory|available)\b", re.I)),
    (IntentKey.SEND_FOLLOWUP, re.compile(r"\b(follow.?up|nudge|remind)\b", re.I)),
]


def _haystack(payload: InboundPayload) -> str:
    parts = [payload.source]
    for v in payload.raw.values():
        if isinstance(v, str):
            parts.append(v)
    return " ".join(parts)


def classify_intent(payload: InboundPayload) -> IntentKey:
    """Return the matched IntentKey or UNKNOWN (escalation signal)."""
    text = _haystack(payload)
    for key, pat in _INTENT_PATTERNS:
        if pat.search(text):
            return key
    return IntentKey.UNKNOWN


def run(payload: InboundPayload) -> IntentKey:
    """Archetype entrypoint. Every archetype file exposes run()."""
    return classify_intent(payload)
