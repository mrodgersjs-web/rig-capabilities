"""rig_build store — Section IV durable backend (stdlib + psycopg2 only).

Trust boundary is validated here AND in the schema (CHECK/trigger/grants):
a hostile caller with direct SQL still cannot mutate, delete, fabricate a
qualification, or skip the outbox state machine. This module is the polite
door, not the lock.

Connection: build_store.connect(dsn) or env RIG_BUILD_DATABASE_URL. The DSN
must use a login role granted exactly one of rig_build_{read,worker,verifier};
service_role/postgres bypass privileges and void the isolation (documented in
0002_rig_build_roles.sql).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations" / "agentic-stack"
MIGRATIONS = ("0001_rig_build.sql", "0002_rig_build_roles.sql")

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TREE = re.compile(r"^[0-9a-f]{40,64}$")
_OUTCOMES = ("pass", "fail", "error", "timeout", "blocked")
_VERDICTS = ("PERFECT", "VERIFIED", "PARTIAL", "FEEDBACK", "FAILED")
_OUTBOX_NEXT = ("sent", "unknown", "reconciled", "pending")


class StoreError(ValueError):
    pass


def _require(pattern: re.Pattern, value: str, name: str) -> str:
    if not isinstance(value, str) or not pattern.match(value):
        raise StoreError(f"{name} must match {pattern.pattern}, got {value!r}")
    return value


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StoreError(f"{name} must be a non-empty string")
    return value


def connect(dsn: str | None = None):
    import psycopg2  # lazy; honest ImportError if driver absent
    dsn = dsn or os.environ.get("RIG_BUILD_DATABASE_URL", "").strip()
    if not dsn:
        raise StoreError("no dsn: pass one or set RIG_BUILD_DATABASE_URL")
    conn = psycopg2.connect(dsn, connect_timeout=5)
    conn.autocommit = False
    return conn


def apply_migrations(conn) -> list[str]:
    applied = []
    with conn, conn.cursor() as cur:
        for name in MIGRATIONS:
            cur.execute((MIGRATIONS_DIR / name).read_text())
            applied.append(name)
    return applied


def record_trial(conn, *, cell: str, trial_id: str, attempt_seq: int, family: str,
                 model: str, node: str, task_sha: str, outcome: str,
                 artifact_tree: str | None = None, evidence: dict | None = None,
                 durable: bool = False, started_at: _dt.datetime,
                 finished_at: _dt.datetime) -> dict:
    """Attempt key (cell, trial_id, attempt_seq); duplicate raises IntegrityError."""
    if outcome not in _OUTCOMES:
        raise StoreError(f"outcome must be one of {_OUTCOMES}")
    if not isinstance(attempt_seq, int) or attempt_seq < 1:
        raise StoreError("attempt_seq must be an integer >= 1")
    if artifact_tree is not None:
        _require(_TREE, artifact_tree, "artifact_tree")
    _require(_SHA256, task_sha, "task_sha")
    with conn, conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM rig_build.record_trial(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s)",
            (_text(cell, "cell"), _text(trial_id, "trial_id"), attempt_seq,
             _text(family, "family"), _text(model, "model"), _text(node, "node"),
             task_sha, outcome, artifact_tree,
             json.dumps(evidence or {}), bool(durable), started_at, finished_at))
        return _row(cur)


def append_event(conn, *, cell: str, trial_id: str, event: str,
                 payload: dict | None = None) -> dict:
    """Sequence-safe append: advisory xact lock per (cell, trial_id)."""
    with conn, conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s), hashtext(%s))",
                    (cell, trial_id))
        cur.execute(
            """INSERT INTO rig_build.trace (cell, trial_id, seq, event, payload)
               SELECT %s, %s, COALESCE(max(seq), 0) + 1, %s, %s::jsonb
                 FROM rig_build.trace WHERE cell = %s AND trial_id = %s
               RETURNING *""",
            (_text(cell, "cell"), _text(trial_id, "trial_id"), _text(event, "event"),
             json.dumps(payload or {}), cell, trial_id))
        return _row(cur)


def record_verdict(conn, *, cell: str, family: str, verdict: str,
                   candidate_commit: str, candidate_tree: str,
                   findings: list | None = None,
                   verdict_at: _dt.datetime) -> dict:
    if verdict not in _VERDICTS:
        raise StoreError(f"verdict must be one of {_VERDICTS}")
    _require(_TREE, candidate_commit, "candidate_commit")
    _require(_TREE, candidate_tree, "candidate_tree")
    with conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO rig_build.verdict
               (cell, family, verdict, candidate_commit, candidate_tree, findings, verdict_at)
               VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s) RETURNING *""",
            (_text(cell, "cell"), _text(family, "family"), verdict,
             candidate_commit, candidate_tree, json.dumps(findings or []), verdict_at))
        return _row(cur)


def record_quality(conn, *, cell: str, trial_id: str, attempt_seq: int,
                   rubric: str, score: float, checks: dict | None = None) -> dict:
    if not 0 <= float(score) <= 100:
        raise StoreError("score must be within 0..100")
    with conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO rig_build.quality_score
               (cell, trial_id, attempt_seq, rubric, score, checks)
               VALUES (%s,%s,%s,%s,%s,%s::jsonb) RETURNING *""",
            (cell, trial_id, attempt_seq, _text(rubric, "rubric"),
             float(score), json.dumps(checks or {})))
        return _row(cur)


def link_seal(conn, *, packet_hash: str, links: list[tuple[str, str]]) -> int:
    """links: [(target_table, target_key)] from a sealed ProofPacket."""
    _require(_SHA256, packet_hash, "packet_hash")
    rows = [(_text(t, "target_table"), str(k)) for t, k in links]
    with conn, conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO rig_build.seal_link (packet_hash, target_table, target_key) "
            "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            [(packet_hash, t, k) for t, k in rows])
        return cur.rowcount


def outbox_new(conn, *, topic: str, payload: dict) -> dict:
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO rig_build.outbox (topic, payload) VALUES (%s, %s::jsonb) "
                    "RETURNING *", (_text(topic, "topic"), json.dumps(payload)))
        return _row(cur)


def outbox_set_state(conn, *, outbox_id: int, next_state: str, note: str = "") -> dict:
    if next_state not in _OUTBOX_NEXT:
        raise StoreError(f"next_state must be one of {_OUTBOX_NEXT}")
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM rig_build.outbox_set_state(%s,%s,%s)",
                    (int(outbox_id), next_state, note))
        return _row(cur)


def assess_quorum(conn, cell: str) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM rig_build.assess_quorum(%s)", (cell,))
        return _row(cur)


def record_qualification(conn, *, cell: str, verdict_id: int) -> dict:
    with conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM rig_build.record_qualification(%s,%s)", (cell, int(verdict_id)))
        return _row(cur)


def qualification(conn, cell: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM rig_build.qualification WHERE cell = %s", (cell,))
        row = cur.fetchone()
        return dict(zip([d[0] for d in cur.description], row)) if row else None


def _row(cur) -> dict:
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, cur.fetchone()))
