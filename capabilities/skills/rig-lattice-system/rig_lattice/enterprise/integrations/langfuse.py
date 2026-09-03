"""LangFuse integration — LLM analytics + cost tracking."""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent.parent
LOCAL_LOG = AUDITS_DIR / "langfuse.jsonl"


def langfuse_available() -> bool:
    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        return False
    try:
        import langfuse  # noqa: F401
        return True
    except ImportError:
        return False


def langfuse_emit(event: str, payload: dict[str, Any],
                    cost_usd: float = 0.0,
                    latency_ms: float = 0.0) -> dict:
    """Emit a generation event with cost + latency metadata."""
    enriched = {**payload, "cost_usd": cost_usd, "latency_ms": latency_ms}
    if langfuse_available():
        try:
            from langfuse import Langfuse  # type: ignore
            client = Langfuse()
            trace = client.trace(name=event, input=enriched)
            return {"sent_to": "langfuse", "trace_id": getattr(trace, "id", None)}
        except Exception as e:
            return _local_log(f"{event}_LANGFUSE_ERROR_{type(e).__name__}", enriched)
    return _local_log(event, enriched)


def _local_log(event: str, payload: dict[str, Any]) -> dict:
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "destination": "local_fallback",
        "payload": payload,
    }
    with LOCAL_LOG.open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec
