"""LangSmith integration — LLM trace observability.

If `langsmith` package is installed and LANGSMITH_API_KEY is set, traces ship
to LangSmith. Otherwise events are logged locally to audits/langsmith.jsonl.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent.parent
LOCAL_LOG = AUDITS_DIR / "langsmith.jsonl"


def langsmith_available() -> bool:
    if not os.environ.get("LANGSMITH_API_KEY"):
        return False
    try:
        import langsmith  # noqa: F401
        return True
    except ImportError:
        return False


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


def langsmith_emit(event: str, payload: dict[str, Any]) -> dict:
    """Emit a trace event. Routes to LangSmith if available, else local log."""
    if langsmith_available():
        try:
            from langsmith import Client  # type: ignore
            client = Client()
            run = client.create_run(
                name=event,
                run_type="chain",
                inputs={"event": event},
                outputs=payload,
            )
            return {"sent_to": "langsmith", "run_id": getattr(run, "id", None)}
        except Exception as e:
            return _local_log(f"{event}_LANGSMITH_ERROR_{type(e).__name__}", payload)
    return _local_log(event, payload)
