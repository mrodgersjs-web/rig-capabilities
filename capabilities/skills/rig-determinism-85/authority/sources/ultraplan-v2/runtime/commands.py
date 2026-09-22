"""W03 -- the shared, transport-neutral command handler.

CLI, MCP and the console all arrive here and nowhere else:
    execute(command, authenticated_actor) -> command_result

Authority is decided HERE, from the authenticated actor identity -- never from
what the transport claims. A node proxy or MCP client that forges a role gets
refused by the same table the console obeys. Schemas are the W01 v1 envelopes.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .ledger import Ledger, LedgerError, StaleFence, IllegalTransition, SequenceConflict

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "v1" / "command.v1.json"
DEFAULT_DB = ROOT / "data" / "ledger.db"

# actor kind -> command types it may submit. 'human' is the only actor that can
# grant approvals; deterministic workers may only report and dispatch within a fence.
AUTHORITY = {
    "human":   {"mission.create", "stage.advance", "stage.park", "stage.resume", "mission.cancel",
                "mission.abandon", "mission.retry_exhausted", "reconcile.uncertain",
                "approval.grant", "approval.deny", "receipt.attach", "forecast.register",
                "forecast.settle", "cell.dispatch", "worker.report", "mission.complete"},
    "cli":     {"mission.create", "stage.advance", "stage.park", "stage.resume", "mission.cancel",
                "receipt.attach", "forecast.register", "forecast.settle", "worker.report",
                "reconcile.uncertain"},  # operator surface: park/resume/cancel yes;
                                        # abandon/complete/retry_exhausted stay human
    "mcp":     {"mission.create", "stage.advance", "receipt.attach", "worker.report"},
    "ui":      {"receipt.attach", "worker.report"},   # the console OBSERVES, mostly
    "worker":  {"receipt.attach", "worker.report", "cell.dispatch",
                "stage.park"},  # workers may park ONLY with payload.researched (guard above the authority table)
}


def _validator():
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(schema)


def execute(command, authenticated_actor, *, ledger=None, db_path=None):
    """command: dict (v1 envelope). authenticated_actor: {'kind','id'} decided by
    the transport's authentication step -- the handler trusts ONLY this argument.
    Returns a command_result dict; never raises for expected refusals."""
    actor_kind = (authenticated_actor or {}).get("kind")
    if actor_kind not in AUTHORITY:
        return {"ok": False, "error": "unauthenticated_actor", "detail": str(actor_kind)}
    errs = sorted(_validator().iter_errors(command), key=lambda e: list(e.path))
    if errs:
        return {"ok": False, "error": "schema_invalid",
                "detail": "; ".join("%s: %s" % ("/".join(map(str, e.path)) or "$", e.message)[:200] for e in errs[:4])}
    ctype = command["type"]
    if ctype == "stage.park" and actor_kind in ("worker", "mcp"):
        pl = command.get("payload") or {}
        if not (isinstance(pl.get("researched"), list) and pl["researched"]):
            return {"ok": False, "error": "park_needs_research",
                    "detail": "researchable blockers must be researched before interrupting "
                              "the user; payload.researched must list what was attempted"}
    if ctype not in AUTHORITY[actor_kind]:
        return {"ok": False, "error": "forbidden_for_actor",
                "detail": "%s may not submit %s" % (actor_kind, ctype)}
    if ctype == "cell.dispatch":
        kind = (command.get("payload") or {}).get("slice_kind")
        if kind not in ("code", "human", "outward"):
            return {"ok": False, "error": "slice_kind_required",
                    "detail": "cell.dispatch must declare slice_kind code|human|outward"}
        if kind == "outward" and not (command.get("payload") or {}).get("approval_id"):
            return {"ok": False, "error": "outward_needs_approval",
                    "detail": "outward slices bind an approval_id (per-slice Gate-D), never blanket consent"}
        if kind == "human" and actor_kind == "worker":
            return {"ok": False, "error": "human_slice_needs_operator",
                    "detail": "workers cannot dispatch slices whose work is a human decision"}

    lg = ledger or Ledger(str(db_path or DEFAULT_DB))
    try:
        ev = lg.apply_command(
            command["mission_id"], ctype, command.get("payload", {}),
            command_id=command["command_id"], idempotency_key=command["idempotency_key"],
            expected_seq=command.get("expected_seq"),
            fence_key=(command.get("payload") or {}).get("fence_key"),
            fence_token=(command.get("payload") or {}).get("fence_token"),
            effects=(command.get("payload") or {}).get("effects", []),
        )
    except SequenceConflict as exc:
        return {"ok": False, "error": "sequence_conflict", "detail": str(exc)}
    except StaleFence as exc:
        return {"ok": False, "error": "stale_writer_fence", "detail": str(exc)}
    except IllegalTransition as exc:
        return {"ok": False, "error": "illegal_transition", "detail": str(exc)}
    except LedgerError as exc:
        return {"ok": False, "error": "ledger_error", "detail": str(exc)}
    return {"ok": True, "seq": ev["seq"], "event_id": ev["event_id"], "hash": ev["hash"],
            "command_id": ev["command_id"]}
