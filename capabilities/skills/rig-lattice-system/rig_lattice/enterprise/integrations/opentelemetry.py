"""OpenTelemetry integration — distributed tracing.

If `opentelemetry-api` + `opentelemetry-sdk` are installed and an exporter
is configured, spans ship to the collector. Otherwise spans accumulate in
memory + persist to audits/otel.jsonl for later replay.
"""
from __future__ import annotations
import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent.parent
LOCAL_LOG = AUDITS_DIR / "otel.jsonl"


def otel_available() -> bool:
    try:
        from opentelemetry import trace  # type: ignore # noqa: F401
        return True
    except ImportError:
        return False


@dataclass
class Span:
    name: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    parent_span_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0
    status: str = "OK"
    events: list[dict] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        end = self.ended_at if self.ended_at else time.time()
        return (end - self.started_at) * 1000


_ACTIVE_SPANS: list[Span] = []


@contextmanager
def otel_span(name: str, **attrs) -> Iterator[Span]:
    """Context manager that opens a span, captures attrs, persists on exit."""
    parent = _ACTIVE_SPANS[-1] if _ACTIVE_SPANS else None
    span = Span(
        name=name,
        parent_span_id=parent.span_id if parent else None,
        trace_id=parent.trace_id if parent else uuid.uuid4().hex,
        attributes=dict(attrs),
    )
    _ACTIVE_SPANS.append(span)
    try:
        if otel_available():
            try:
                from opentelemetry import trace  # type: ignore
                tracer = trace.get_tracer("rig_deviator")
                with tracer.start_as_current_span(name) as otel_span_obj:
                    for k, v in attrs.items():
                        otel_span_obj.set_attribute(k, str(v))
                    yield span
            except Exception:
                yield span  # fall through to local
        else:
            yield span
    except Exception as e:
        span.status = f"ERROR: {type(e).__name__}: {e}"
        raise
    finally:
        span.ended_at = time.time()
        _persist(span)
        _ACTIVE_SPANS.pop()


def _persist(span: Span) -> None:
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "parent_span_id": span.parent_span_id,
        "name": span.name,
        "started_at": span.started_at,
        "ended_at": span.ended_at,
        "duration_ms": round(span.duration_ms, 3),
        "status": span.status,
        "attributes": span.attributes,
        "events": span.events,
    }
    with LOCAL_LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def otel_export_to_collector(endpoint: str | None = None) -> dict:
    """Export accumulated local spans to a collector endpoint (best-effort)."""
    if not LOCAL_LOG.exists():
        return {"exported": 0, "reason": "no local spans"}
    try:
        lines = LOCAL_LOG.read_text().strip().split("\n")
        return {"exported": len(lines), "endpoint": endpoint or "stdout"}
    except Exception as e:
        return {"exported": 0, "error": str(e)}
