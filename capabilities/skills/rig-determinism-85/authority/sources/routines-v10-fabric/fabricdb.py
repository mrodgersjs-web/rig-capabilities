"""Journaled access to the Aside routines store (~/.aside/u/0/state.db).

Every mutation goes through update_routine/insert_routine and is appended to
~/.rig/state/routine-fabric/journal.jsonl with full before/after rows, so any
fabric write is reversible (`fabric.py undo`). Reads use plain SELECTs. The
state.db itself is never copied; evidence dumps are per-table SELECTs only.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.environ.get("RIG_ROUTINE_DB", os.path.expanduser("~/.aside/u/0/state.db")))
STATE_DIR = Path(os.environ.get("RIG_FABRIC_STATE", os.path.expanduser("~/.rig/state/routine-fabric")))
JOURNAL_PATH = STATE_DIR / "journal.jsonl"

# Columns the fabric may write; undo restores exactly these.
WRITABLE = ("status", "paused_at", "next_run_at", "rrule", "updated_at", "name", "prompt",
            "session_config", "metadata", "type", "environment", "device_id", "created_at")


def connect(db: str | Path | None = None, ro: bool = False) -> sqlite3.Connection:
    path = Path(db) if db else DB_PATH
    uri = f"file:{path}?mode={'ro' if ro else 'rw'}"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    return conn


def rows(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def one(conn, sql, args=()):
    r = conn.execute(sql, args).fetchone()
    return dict(r) if r else None


def get_routine(conn, rid: str):
    return one(conn, "SELECT * FROM routines WHERE id=?", (rid,))


def _journal(entry: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entry}
    with open(JOURNAL_PATH, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def update_routine(conn, rid: str, sets: dict, reason: str):
    """Journaled UPDATE on one routine. `sets` keys must be in WRITABLE."""
    bad = set(sets) - set(WRITABLE)
    if bad:
        raise ValueError(f"non-writable columns: {sorted(bad)}")
    before = get_routine(conn, rid)
    if before is None:
        raise KeyError(f"routine {rid} not found")
    cols = ", ".join(f"{k}=?" for k in sets)
    conn.execute(f"UPDATE routines SET {cols} WHERE id=?", (*sets.values(), rid))
    conn.commit()
    after = get_routine(conn, rid)
    return _journal({"op": "update", "table": "routines", "id": rid, "reason": reason,
                     "before": before, "after": after,
                     "changed": {k: sets[k] for k in sets}})


def insert_routine(conn, row: dict, reason: str):
    """Journaled INSERT of a new routine row (fabric-provisioned routines)."""
    cols = ", ".join(row)
    ph = ", ".join("?" for _ in row)
    conn.execute(f"INSERT INTO routines ({cols}) VALUES ({ph})", tuple(row.values()))
    conn.commit()
    after = get_routine(conn, row["id"])
    return _journal({"op": "insert", "table": "routines", "id": row["id"],
                     "reason": reason, "before": None, "after": after})


def journal_lines() -> list[dict]:
    if not JOURNAL_PATH.exists():
        return []
    out = []
    with open(JOURNAL_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def undo_last(conn) -> dict:
    """Reverse the most recent reversible journal entry."""
    lines = journal_lines()
    for entry in reversed(lines):
        if entry.get("op") == "update" and entry.get("undone_by") is None:
            before = entry["before"]
            changed = entry["changed"]
            sets = {k: before[k] for k in changed if k in WRITABLE}
            cols = ", ".join(f"{k}=?" for k in sets)
            conn.execute(f"UPDATE routines SET {cols} WHERE id=?", (*sets.values(), entry["id"]))
            conn.commit()
            mark = _journal({"op": "undo", "table": "routines", "id": entry["id"],
                             "reason": f"undo of {entry['ts']}",
                             "restored": sets})
            return mark
        if entry.get("op") == "insert" and entry.get("undone_by") is None:
            # never delete rows: retire fabric-provisioned routines instead
            conn.execute("UPDATE routines SET status='completed', deleted_at=?, updated_at=? WHERE id=?",
                         (int(time.time()), int(time.time()), entry["id"]))
            conn.commit()
            return _journal({"op": "undo", "table": "routines", "id": entry["id"],
                             "reason": f"retire inserted routine ({entry['ts']})"})
    raise LookupError("no reversible journal entry")
