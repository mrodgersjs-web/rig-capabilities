"""Enterprise integrations — CrewAI, LangSmith, LangFuse, OpenTelemetry.

These are registered adapters. If the corresponding package is installed,
the adapter wires through to the real client; otherwise it logs the
intent + falls back to local observability so the system never breaks.
"""
from rig_lattice.enterprise.integrations.langsmith import langsmith_emit, langsmith_available
from rig_lattice.enterprise.integrations.langfuse import langfuse_emit, langfuse_available
from rig_lattice.enterprise.integrations.crewai import (
    crewai_dispatch, crewai_available, register_crew, list_crews,
)
from rig_lattice.enterprise.integrations.litellm import litellm_route, litellm_available
from rig_lattice.enterprise.integrations.opentelemetry import (
    otel_span, otel_available, otel_export_to_collector,
)

__all__ = [
    "langsmith_emit", "langsmith_available",
    "langfuse_emit", "langfuse_available",
    "crewai_dispatch", "crewai_available", "register_crew", "list_crews",
    "litellm_route", "litellm_available",
    "otel_span", "otel_available", "otel_export_to_collector",
]


def integrations_status() -> dict:
    """Snapshot of which integrations are wired."""
    return {
        "langsmith":     {"available": langsmith_available()},
        "langfuse":      {"available": langfuse_available()},
        "crewai":        {"available": crewai_available(), "crews": list_crews()},
        "litellm":       {"available": litellm_available()},
        "opentelemetry": {"available": otel_available()},
    }
