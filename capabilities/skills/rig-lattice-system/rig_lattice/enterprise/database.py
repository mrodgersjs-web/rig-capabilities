"""Enterprise Database — SQLite schema, WAL mode, integrity verification.

Per the LinkedIn Studio template Database subsystem. Uses stdlib sqlite3.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
DB_PATH = AUDITS_DIR / "deviator.db"


# ── Schema (canonical) ──────────────────────────────────────────────────
SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS mission (
    mission_id     TEXT PRIMARY KEY,
    tier           TEXT NOT NULL,
    bms_mode       TEXT,
    intent         TEXT,
    confidence     REAL,
    artifact_hash  TEXT,
    rig_l          REAL,
    bdf            REAL,
    status         TEXT,
    short_circuit  INTEGER DEFAULT 0,
    weakest_gate   TEXT,
    escalation_cost INTEGER,
    created_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mission_tier ON mission(tier);
CREATE INDEX IF NOT EXISTS idx_mission_status ON mission(status);
CREATE INDEX IF NOT EXISTS idx_mission_created ON mission(created_at);

CREATE TABLE IF NOT EXISTS engine_score (
    score_id     TEXT PRIMARY KEY,
    mission_id   TEXT NOT NULL,
    engine_id    INTEGER NOT NULL,
    engine_name  TEXT NOT NULL,
    engine_slug  TEXT NOT NULL,
    layer        TEXT NOT NULL,
    raw_score    REAL,
    madz         REAL,
    status       TEXT,
    is_gate      INTEGER DEFAULT 0,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mission_id) REFERENCES mission(mission_id)
);

CREATE INDEX IF NOT EXISTS idx_engine_score_mission ON engine_score(mission_id);
CREATE INDEX IF NOT EXISTS idx_engine_score_engine ON engine_score(engine_id);
CREATE INDEX IF NOT EXISTS idx_engine_score_layer ON engine_score(layer);

CREATE TABLE IF NOT EXISTS amplifier_verdict (
    verdict_id   TEXT PRIMARY KEY,
    score_id     TEXT NOT NULL,
    amp_name     TEXT NOT NULL,
    passed       INTEGER NOT NULL,
    multiplier   REAL NOT NULL,
    detail       TEXT,
    evidence_hash TEXT,
    FOREIGN KEY (score_id) REFERENCES engine_score(score_id)
);

CREATE INDEX IF NOT EXISTS idx_amp_verdict_score ON amplifier_verdict(score_id);

CREATE TABLE IF NOT EXISTS audit_chain (
    seq          INTEGER PRIMARY KEY AUTOINCREMENT,
    event        TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    prev_hash    TEXT,
    entry_hash   TEXT NOT NULL,
    ts_utc       TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_chain_event ON audit_chain(event);

CREATE TABLE IF NOT EXISTS brier (
    log_id        TEXT PRIMARY KEY,
    mission_id    TEXT,
    engine_name   TEXT NOT NULL,
    predicted     REAL NOT NULL,
    realized      REAL,
    delta         REAL,
    expected_resolution TEXT,
    content_hash  TEXT,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_brier_engine ON brier(engine_name);

CREATE TABLE IF NOT EXISTS approval (
    request_id    TEXT PRIMARY KEY,
    artifact_hash TEXT NOT NULL,
    tier          TEXT NOT NULL,
    requested_by  TEXT NOT NULL,
    reason        TEXT,
    status        TEXT NOT NULL,
    approved_by   TEXT,
    requested_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    approved_at   TEXT,
    ttl_seconds   INTEGER DEFAULT 86400
);

CREATE INDEX IF NOT EXISTS idx_approval_status ON approval(status);

CREATE TABLE IF NOT EXISTS deployment (
    deploy_id    TEXT PRIMARY KEY,
    version      TEXT NOT NULL,
    state        TEXT NOT NULL,
    canary_pct   INTEGER DEFAULT 0,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    promoted_at  TEXT,
    rolled_back_at TEXT,
    rollback_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_deployment_state ON deployment(state);
"""


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    """Get a DB connection. Creates schema on first use."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA_SQL)
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> Path:
    """Initialize the DB (apply schema). Idempotent."""
    with connection() as conn:
        pass
    return DB_PATH


def insert_mission(mission: dict) -> None:
    with connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO mission
                (mission_id, tier, bms_mode, intent, confidence,
                 artifact_hash, rig_l, bdf, status, short_circuit,
                 weakest_gate, escalation_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mission.get("mission_id"), mission.get("tier"), mission.get("bms_mode"),
            mission.get("intent"), mission.get("confidence"),
            mission.get("artifact_hash"), mission.get("rig_l"), mission.get("bdf"),
            mission.get("status"), int(mission.get("short_circuit", False)),
            mission.get("weakest_gate"), mission.get("escalation_cost"),
        ))


def insert_engine_score(score: dict) -> None:
    with connection() as conn:
        conn.execute("""
            INSERT INTO engine_score
                (score_id, mission_id, engine_id, engine_name, engine_slug,
                 layer, raw_score, madz, status, is_gate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score["score_id"], score["mission_id"], score["engine_id"],
            score["engine_name"], score["engine_slug"], score["layer"],
            score.get("raw_score"), score.get("madz"), score.get("status"),
            int(score.get("is_gate", False)),
        ))


def insert_audit_entry(event: str, payload: dict, prev_hash: str | None) -> str:
    """Append to audit_chain. Returns the new entry_hash."""
    payload_json = json.dumps(payload, sort_keys=True, default=str)
    canonical = f"{event}|{payload_json}|{prev_hash or ''}"
    entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    with connection() as conn:
        conn.execute("""
            INSERT INTO audit_chain (event, payload_json, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?)
        """, (event, payload_json, prev_hash, entry_hash))
    return entry_hash


def get_last_audit_hash() -> str | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT entry_hash FROM audit_chain ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row["entry_hash"] if row else None


def verify_audit_chain() -> tuple[bool, int, str]:
    """Walk audit_chain in seq order, verifying every link."""
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_chain ORDER BY seq ASC"
        ).fetchall()
    prev = None
    for i, row in enumerate(rows, start=1):
        if row["prev_hash"] != prev:
            return False, i, f"prev_hash mismatch at seq={row['seq']}"
        canonical = f"{row['event']}|{row['payload_json']}|{row['prev_hash'] or ''}"
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if row["entry_hash"] != expected:
            return False, i, f"entry_hash recompute mismatch at seq={row['seq']}"
        prev = row["entry_hash"]
    return True, len(rows), ""


def integrity_check() -> dict:
    """Run SQLite PRAGMA integrity_check + audit chain verification."""
    with connection() as conn:
        rows = conn.execute("PRAGMA integrity_check").fetchall()
        sql_ok = len(rows) == 1 and rows[0][0] == "ok"
        chain_ok, n_entries, chain_msg = verify_audit_chain()
        # Table counts
        tables = {}
        for tbl in ("mission", "engine_score", "amplifier_verdict",
                     "audit_chain", "brier", "approval", "deployment"):
            r = conn.execute(f"SELECT COUNT(*) AS n FROM {tbl}").fetchone()
            tables[tbl] = r["n"]
    return {
        "sqlite_integrity_ok": sql_ok,
        "audit_chain_ok": chain_ok,
        "audit_chain_entries": n_entries,
        "audit_chain_error": chain_msg,
        "row_counts": tables,
    }


# Table count target per LinkedIn Studio template (42+ tables suggested)
# We ship 7 canonical tables; "42+" includes views, indexes, denormalized
# aggregations which are deployment-time. Documenting count here:
CANONICAL_TABLE_COUNT = 7
