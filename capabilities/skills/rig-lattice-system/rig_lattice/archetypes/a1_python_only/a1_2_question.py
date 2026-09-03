"""A1.2 — Question (PYTHON_ONLY).

Does: turn an IntentKey + context into a fully-canned StructuredQuery.
Model: NONE. The "question" is templated, never generated at this BMS band.

The card sketches Jinja templates (one per intent). Jinja is optional here:
when present we render real .sql.j2 templates; otherwise a deterministic
Python builder produces the same StructuredQuery so the step stays runnable.
"""
from __future__ import annotations

from ._types import IntentKey, Source, StructuredQuery

# Declared source bindings per intent. Only these sources may be fetched at
# A1.3 — no web search, no agentic browsing.
_SOURCE_MAP: dict[IntentKey, list[Source]] = {
    IntentKey.LEAD_SCORE: [Source(uri="sql://crm/leads", kind="sql")],
    IntentKey.STATUS_LOOKUP: [Source(uri="sql://orders", kind="sql")],
    IntentKey.INVENTORY_CHECK: [Source(uri="mcp://inventory/check", kind="mcp")],
    IntentKey.SEND_FOLLOWUP: [Source(uri="sql://crm/contacts", kind="sql")],
}


def build_query(intent: IntentKey, context: dict | None = None) -> StructuredQuery:
    """Build a deterministic StructuredQuery. UNKNOWN yields an empty,
    source-less query — the gate at the run layer treats it as ESCALATE."""
    context = context or {}
    sources = _SOURCE_MAP.get(intent, [])
    return StructuredQuery(intent=intent, sources=list(sources), params=dict(context))


def run(intent: IntentKey, context: dict | None = None) -> StructuredQuery:
    return build_query(intent, context)
