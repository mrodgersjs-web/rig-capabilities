"""rig_build data-access layer — Section IV durable backend (B14–B19).

The schema is scripts/ddl_rig_build.sql (frozen by B06); this module is the
only sanctioned writer path. Invariants, enforced fail-closed HERE and, where
marked, again by database law in the DDL:

- cell criteria and process versions are FROZEN records: a byte-identical
  replay is a no-op, a differing rewrite is refused (never overwritten);
- run creation is idempotent on the caller's idempotency key — a replay
  returns the existing run, it never forks a second one;
- run_events are append-only with sequence == max+1 and a fencing token that
  must equal the run's current token: a stale writer is rejected;
- artifacts are content-addressed: the sha256 is RECOMPUTED from the bytes
  here and a declared-hash mismatch is refused before anything is written;
- approval_refs store REFERENCES into the authoritative gate-d ledger only.
  There is deliberately NO set_qualified, NO approve_omission, and no path
  from any caller-submitted PASS/qualified flag to a stored row: this module
  cannot manufacture approval or qualification, only point at it.

Connections follow the house convention (sync.discover_dsn + RIG_CAP_DSN +
--dsn override; no secrets in source). Functions take an open connection, so
the same code runs against Postgres (psycopg2, production) and the offline
sqlite structural harness (tests only; the PG-only invariants are listed as
needs-live-proof there, never claimed as sqlite-proven).

Stdlib-only at import time; psycopg2 is imported lazily inside connect().
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

from .sync import discover_dsn

REPO = Path(__file__).resolve().parent.parent
DDL_PATH = REPO / "scripts" / "ddl_rig_build.sql"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RUN_STATES = ("requested", "running", "waiting_approval", "blocked",
               "succeeded", "failed", "cancelled")
_EVENT_KINDS = ("transition", "checkpoint", "receipt", "note")
_OUTBOX_SETTLE = ("sent", "failed", "unknown")
_OUTBOX_RECONCILE = ("sent", "failed", "pending")
_RETRIEVAL_STATES = ("PENDING", "FETCHING", "FETCHED", "TRUNCATED",
                     "MISSING", "FAILED", "REPLACED")
# T1–T8 per authority/standards/tool_selection.v2.json (single source; the
# binding records the chosen row, it never picks a default owner).
WORK_TYPES = ("T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8")
# Any of these appearing as a key or a flag value in caller-supplied detail
# is an approval/qualification in disguise — refused at the boundary.
_BANNED_MINT_TOKENS = frozenset(
    {"pass", "passed", "approve", "approved", "approval", "qualified",
     "qualification", "verdict", "admitted", "certified"})


class StoreError(ValueError):
    pass


# -- guards / primitives ------------------------------------------------------

def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _require_sha(value: str, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.match(value):
        raise StoreError(f"{name} must be 64-hex sha256, got {value!r}")
    return value


def _text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StoreError(f"{name} must be a non-empty string")
    return value.strip()


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _is_sqlite(conn) -> bool:
    return type(conn).__module__.startswith("sqlite3")


def _sql(conn, sql: str) -> str:
    """Canonical SQL is written psycopg2-style (%s, ::jsonb, rig_build.);
    the sqlite structural harness gets qmarks, no casts, no schema prefix."""
    if _is_sqlite(conn):
        return (sql.replace("%s", "?").replace("::jsonb", "")
                   .replace("rig_build.", ""))
    return sql


def _integrity(conn) -> tuple:
    if _is_sqlite(conn):
        import sqlite3
        return (sqlite3.IntegrityError,)
    import psycopg2  # already connected if we got here
    return (psycopg2.IntegrityError,)


def _exec(conn, sql: str, params: tuple = ()):
    cur = conn.cursor()
    try:
        cur.execute(_sql(conn, sql), params)
        return cur
    except Exception:
        cur.close()
        raise


def _fetch_rows(cur) -> list[dict]:
    cols = [d[0] for d in cur.description] if cur.description else []
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _commit(conn) -> None:
    conn.commit()


def _mint_id() -> str:
    return uuid.uuid4().hex


def connect(dsn: str | None = None):
    """Override -> RIG_CAP_DSN -> rig-dev-db container discovery.
    No credential hunting beyond the house convention; fail closed."""
    dsn = dsn or os.environ.get("RIG_CAP_DSN") or discover_dsn()
    if not dsn:
        raise StoreError(
            "no rig_build dsn: pass --dsn or set RIG_CAP_DSN "
            "(fail closed — no default target is invented)")
    try:
        import psycopg2
    except ImportError as exc:
        raise StoreError(f"psycopg2 unavailable: {exc}") from exc
    conn = psycopg2.connect(dsn, connect_timeout=10,
                            application_name="rig_build_store")
    return conn


# -- DDL sectioning (shared with build_migrate) -------------------------------

_SECTION = re.compile(
    r"-- >>>> ([A-Z-]+)-BEGIN.*?\n(.*?)-- <<<< \1-END", re.S)


def ddl_sections(path: Path | None = None) -> dict[str, str]:
    text = (path or DDL_PATH).read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in _SECTION.finditer(text)}


def portable_ddl_sqlite(path: Path | None = None) -> str:
    """The APPLY-PORTABLE section mechanically adapted for the sqlite
    structural harness ONLY: CREATE SCHEMA removed (tables land in main via
    prefix strip) and the rig_build. prefix dropped. The APPLY-PGONLY section
    (triggers/roles/grants/RLS) is NEVER transformed — those invariants go on
    the blocked list, not into a fake sqlite pass."""
    sec = ddl_sections(path)["APPLY-PORTABLE"]
    lines = [ln for ln in sec.splitlines()
             if not ln.strip().upper().startswith("CREATE SCHEMA")]
    return "\n".join(lines).replace("rig_build.", "")


# -- frozen records (B14) -------------------------------------------------------

def put_cell_contract(conn, *, cell_id: str, criteria_version: str,
                      contract: dict, criteria_pack_sha256: str,
                      sealed_by: str) -> dict:
    """Seal one criteria contract for (cell, criteria_version). A replay of
    identical bytes is a no-op; a differing rewrite is REFUSED — the frozen
    pack is never retrofitted in place."""
    from .build_diagnose import _cell_ids  # 588-cell authority, single source
    cid = _text(cell_id, "cell_id")
    if cid not in _cell_ids():
        raise StoreError(f"cell_id not in the 588-cell authority: {cid!r}")
    _require_sha(_text(criteria_pack_sha256, "criteria_pack_sha256"),
                 "criteria_pack_sha256")
    body = _canonical(contract)
    sha = _sha256(body.encode())
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.cell_contracts
              (cell_id, criteria_version, contract, contract_sha256,
               criteria_pack_sha256, sealed_by)
            VALUES (%s,%s,%s::jsonb,%s,%s,%s)
            ON CONFLICT (cell_id, criteria_version) DO NOTHING
            RETURNING cell_id, criteria_version, contract_sha256""",
            (cid, _text(criteria_version, "criteria_version"), body, sha,
             criteria_pack_sha256, _text(sealed_by, "sealed_by")))
        rows = _fetch_rows(cur)
    except _integrity(conn):
        rows = []
    _commit(conn)
    if rows:
        return {"status": "sealed", "row": rows[0]}
    cur = _exec(conn, """
        SELECT contract_sha256 FROM rig_build.cell_contracts
        WHERE cell_id=%s AND criteria_version=%s""",
        (cid, _text(criteria_version, "criteria_version")))
    have = _fetch_rows(cur)
    if not have:
        raise StoreError(f"contract for {cid}/{criteria_version} vanished")
    if have[0]["contract_sha256"] != sha:
        raise StoreError(
            f"frozen contract differs: {cid}/{criteria_version} is sealed at "
            f"{have[0]['contract_sha256'][:12]}; refusing an in-place rewrite "
            "(cut a new criteria_version instead)")
    return {"status": "replay_confirmed",
            "row": {"cell_id": cid, "criteria_version": criteria_version,
                    "contract_sha256": sha}}


def register_process_version(conn, *, process_key: str, version: str,
                             definition: dict, declared_owner: str,
                             resource_envelope: dict | None = None,
                             registered_by: str) -> dict:
    """Immutable process-version record: changes are NEW version rows."""
    _text(process_key, "process_key")
    _text(version, "version")
    body = _canonical(definition)
    sha = _sha256(body.encode())
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.process_versions
              (process_key, version, definition, definition_sha256,
               declared_owner, resource_envelope, registered_by)
            VALUES (%s,%s,%s::jsonb,%s,%s,%s::jsonb,%s)
            ON CONFLICT (process_key, version) DO NOTHING
            RETURNING process_key, version, definition_sha256""",
            (process_key, version, body, sha,
             _text(declared_owner, "declared_owner"),
             _canonical(resource_envelope or {}),
             _text(registered_by, "registered_by")))
        rows = _fetch_rows(cur)
    except _integrity(conn):
        rows = []
    _commit(conn)
    if rows:
        return {"status": "registered", "row": rows[0]}
    cur = _exec(conn, """
        SELECT definition_sha256 FROM rig_build.process_versions
        WHERE process_key=%s AND version=%s""", (process_key, version))
    have = _fetch_rows(cur)
    if have and have[0]["definition_sha256"] != sha:
        raise StoreError(
            f"process {process_key}@{version} is frozen at "
            f"{have[0]['definition_sha256'][:12]}; a change requires a new "
            "version, never an overwrite")
    return {"status": "replay_confirmed",
            "row": {"process_key": process_key, "version": version,
                    "definition_sha256": sha}}


def bind_cell(conn, *, cell_id: str, criteria_version: str, process_key: str,
              process_version: str, work_type: str, owner: str,
              bound_by: str, facts: dict | None = None) -> dict:
    """Record the T1–T8 owner selection for a cell. The contract and process
    rows must already exist (FK); no default owner is ever invented."""
    if work_type not in WORK_TYPES:
        raise StoreError(f"work_type must be one of {WORK_TYPES}")
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.cell_bindings
              (cell_id, criteria_version, process_key, process_version,
               work_type, owner, facts, bound_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
            ON CONFLICT (cell_id, criteria_version, process_key,
                         process_version) DO NOTHING
            RETURNING cell_id, criteria_version, process_key,
                      process_version, work_type, owner""",
            (_text(cell_id, "cell_id"),
             _text(criteria_version, "criteria_version"),
             _text(process_key, "process_key"),
             _text(process_version, "process_version"),
             work_type, _text(owner, "owner"),
             _canonical(facts or {}), _text(bound_by, "bound_by")))
        rows = _fetch_rows(cur)
    except _integrity(conn) as exc:
        _commit(conn)
        raise StoreError(
            f"binding refused — the contract/process it names must be sealed "
            f"first (foreign key): {exc}") from exc
    _commit(conn)
    return {"status": "bound" if rows else "replay_confirmed",
            "row": rows[0] if rows else {
                "cell_id": cell_id, "criteria_version": criteria_version,
                "process_key": process_key,
                "process_version": process_version}}


# -- runs and events (B15) ------------------------------------------------------

def start_run(conn, *, cell_id: str, criteria_version: str, process_key: str,
              process_version: str, idempotency_key: str, started_by: str,
              run_id: str | None = None,
              checkpoint: dict | None = None) -> dict:
    """Register a run. The idempotency key is UNIQUE: a replay returns the
    existing row with status 'replayed', never a forked second run."""
    key = _text(idempotency_key, "idempotency_key")
    cur = _exec(conn, """
        SELECT run_id, state, fencing_token FROM rig_build.runs
        WHERE idempotency_key=%s""", (key,))
    hit = _fetch_rows(cur)
    if hit:
        return {"status": "replayed", "row": hit[0]}
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.runs
              (run_id, idempotency_key, cell_id, criteria_version,
               process_key, process_version, state, started_by, checkpoint)
            VALUES (%s,%s,%s,%s,%s,%s,'requested',%s,%s::jsonb)
            RETURNING run_id, state, fencing_token""",
            (run_id or _mint_id(), key, _text(cell_id, "cell_id"),
             _text(criteria_version, "criteria_version"),
             _text(process_key, "process_key"),
             _text(process_version, "process_version"),
             _text(started_by, "started_by"),
             _canonical(checkpoint or {})))
        rows = _fetch_rows(cur)
    except _integrity(conn):
        _commit(conn)  # concurrent replay: the key won elsewhere
        cur = _exec(conn, """
            SELECT run_id, state, fencing_token FROM rig_build.runs
            WHERE idempotency_key=%s""", (key,))
        rows = _fetch_rows(cur)
        if rows:
            return {"status": "replayed", "row": rows[0]}
        raise
    _commit(conn)
    return {"status": "started", "row": rows[0]}


def append_event(conn, *, run_id: str, sequence: int, kind: str,
                 fencing_token: int, payload: dict | None = None,
                 occurred_at: str | None = None) -> dict:
    """Append-only event write. The caller's fencing token must EQUAL the
    run's current token (a stale worker cannot commit); the sequence must be
    exactly max+1 (duplicates and gaps both refused here; the PG trigger
    closes the cross-connection race)."""
    if kind not in _EVENT_KINDS:
        raise StoreError(f"event kind must be one of {_EVENT_KINDS}")
    if not isinstance(sequence, int) or sequence < 1:
        raise StoreError("sequence must be an integer >= 1")
    if not isinstance(fencing_token, int) or fencing_token < 1:
        raise StoreError("fencing_token must be >= 1")
    cur = _exec(conn, """
        SELECT fencing_token FROM rig_build.runs WHERE run_id=%s""",
        (_text(run_id, "run_id"),))
    run = _fetch_rows(cur)
    if not run:
        raise StoreError(f"unknown run: {run_id}")
    if run[0]["fencing_token"] != fencing_token:
        raise StoreError(
            f"stale fencing token rejected for run {run_id}: caller "
            f"{fencing_token} != current {run[0]['fencing_token']}")
    cur = _exec(conn, """
        SELECT COALESCE(MAX(sequence), 0) AS max_seq
        FROM rig_build.run_events WHERE run_id=%s""", (run_id,))
    max_seq = _fetch_rows(cur)[0]["max_seq"]
    if sequence <= max_seq:
        raise StoreError(
            f"duplicate/out-of-order sequence {sequence} for run {run_id} "
            f"(already appended through {max_seq}) — append-only")
    if sequence != max_seq + 1:
        raise StoreError(
            f"sequence gap for run {run_id}: got {sequence}, expected "
            f"{max_seq + 1} — append-only, never skip")
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.run_events
              (run_id, sequence, kind, payload, fencing_token, occurred_at)
            VALUES (%s,%s,%s,%s::jsonb,%s,COALESCE(%s, CURRENT_TIMESTAMP))
            RETURNING run_id, sequence, kind, fencing_token, occurred_at""",
            (run_id, sequence, kind, _canonical(payload or {}),
             fencing_token, occurred_at))
        rows = _fetch_rows(cur)
    except _integrity(conn) as exc:
        _commit(conn)
        raise StoreError(f"duplicate sequence {sequence} for run {run_id}") \
            from exc
    _commit(conn)
    return {"status": "appended", "row": rows[0]}


# -- artifacts (B16) ------------------------------------------------------------

def add_artifact(conn, *, run_id: str, uri: str, kind: str, recorded_by: str,
                 content: bytes | None = None, path: str | None = None,
                 content_sha256: str | None = None) -> dict:
    """Content-addressed artifact registration. The hash is RECOMPUTED from
    the bytes here — a declared hash that does not match the content is
    refused before insert. There is no way to register an artifact by
    declaring a hash alone."""
    if content is None:
        if not path:
            raise StoreError("add_artifact needs content or path")
        content = Path(path).read_bytes()
    actual = _sha256(content)
    if content_sha256 is not None and content_sha256 != actual:
        raise StoreError(
            f"artifact hash mismatch: declared {content_sha256[:12]} != "
            f"recomputed {actual[:12]} — refused, nothing stored")
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.artifacts
              (content_sha256, uri, run_id, kind, size_bytes, recorded_by)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (content_sha256, uri) DO NOTHING
            RETURNING content_sha256, uri, run_id, kind, size_bytes""",
            (actual, _text(uri, "uri"), _text(run_id, "run_id"),
             _text(kind, "kind"), len(content),
             _text(recorded_by, "recorded_by")))
        rows = _fetch_rows(cur)
    except _integrity(conn) as exc:
        _commit(conn)
        raise StoreError(f"artifact refused — unknown run or bad key: {exc}") \
            from exc
    _commit(conn)
    return {"status": "registered" if rows else "replay_confirmed",
            "content_sha256": actual,
            "row": rows[0] if rows else {"content_sha256": actual,
                                         "uri": uri, "run_id": run_id}}


# -- approval references (B17) --------------------------------------------------

def _reject_mint(detail, where: str) -> None:
    if detail is None:
        return
    if isinstance(detail, dict):
        for k, v in detail.items():
            if str(k).lower() in _BANNED_MINT_TOKENS:
                raise StoreError(
                    f"{where}: key {k!r} is an approval/qualification mint; "
                    "this store keeps REFERENCES only — validate through the "
                    "gate-d ledger and record its external_ref")
            _reject_mint(v, where)
    elif isinstance(detail, list):
        for v in detail:
            _reject_mint(v, where)
    elif isinstance(detail, str) and detail.strip().lower() \
            in _BANNED_MINT_TOKENS:
        raise StoreError(
            f"{where}: value {detail!r} is a mint flag; refused")


def add_approval_ref(conn, *, authority_ledger: str, external_ref: str,
                     subject_kind: str, subject_id: str, requested_by: str,
                     recorded_by: str, detail: dict | None = None) -> dict:
    """Store a POINTER to an approval held in the authoritative ledger.
    Refused: self-authority, missing external_ref, any caller-submitted
    PASS/approved/qualified flag in the detail, verdict-like subjects. This
    cannot approve anything — not with any argument combination."""
    ledger = _text(authority_ledger, "authority_ledger").lower()
    if ledger == "self":
        raise StoreError("authority_ledger 'self' is not a ledger; "
                         "self-approval has no external ref to point at")
    ref = _text(external_ref, "external_ref")
    if subject_kind == "run" and ref.startswith("caller:"):
        raise StoreError("approval ref 'caller:*' is caller-minted consent; "
                         "external ledger refs only")
    _reject_mint(detail, "approval detail")
    if subject_kind not in ("run", "cell_omission", "build"):
        raise StoreError("subject_kind must be run|cell_omission|build")
    body = _canonical(detail or {})
    if _BANNED_MINT_TOKENS & set(_canonical(detail or {}).split('"')):
        raise StoreError("approval detail carries a mint token; refused")
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.approval_refs
              (authority_ledger, external_ref, subject_kind, subject_id,
               requested_by, recorded_by)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (authority_ledger, external_ref) DO NOTHING
            RETURNING authority_ledger, external_ref, subject_kind,
                      subject_id""",
            (ledger, ref, subject_kind, _text(subject_id, "subject_id"),
             _text(requested_by, "requested_by"),
             _text(recorded_by, "recorded_by")))
        rows = _fetch_rows(cur)
    except _integrity(conn) as exc:
        _commit(conn)
        raise StoreError(f"approval ref refused: {exc}") from exc
    _commit(conn)
    del body
    return {"status": "referenced" if rows else "replay_confirmed",
            "note": "reference only — consent is validated by gate-d, "
                    "never by this row",
            "row": rows[0] if rows else {"authority_ledger": ledger,
                                         "external_ref": ref}}


# -- source documents (B18) -----------------------------------------------------

def put_source_document(conn, *, dedupe_key: str, url: str, provider: str,
                        kind: str, retrieval_status: str = "PENDING",
                        content_sha256: str | None = None,
                        raw_sha256: str | None = None,
                        expected_artifact: str = "",
                        why_version_applicable: str = "",
                        last_error: str | None = None) -> dict:
    """Resumable ingestion state keyed by a unique dedupe key: a re-accepted
    source resolves to the SAME row (attempt_count++), never a second
    accepted copy. FETCHED requires the content hash (DB CHECK + here)."""
    key = _require_sha(_text(dedupe_key, "dedupe_key"), "dedupe_key")
    if retrieval_status not in _RETRIEVAL_STATES:
        raise StoreError(f"retrieval_status must be one of {_RETRIEVAL_STATES}")
    if retrieval_status == "FETCHED" and not content_sha256:
        raise StoreError("FETCHED requires content_sha256 — a claimed fetch "
                         "without the hash is not evidence")
    for name, val in (("content_sha256", content_sha256),
                      ("raw_sha256", raw_sha256)):
        if val is not None:
            _require_sha(val, name)
    try:
        cur = _exec(conn, """
            INSERT INTO rig_build.source_documents
              (dedupe_key, url, provider, kind, retrieval_status,
               content_sha256, raw_sha256, expected_artifact,
               why_version_applicable)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (dedupe_key) DO NOTHING
            RETURNING dedupe_key, retrieval_status, attempt_count""",
            (key, _text(url, "url"), _text(provider, "provider"),
             _text(kind, "kind"), retrieval_status, content_sha256,
             raw_sha256, expected_artifact, why_version_applicable))
        rows = _fetch_rows(cur)
    except _integrity(conn) as exc:
        _commit(conn)
        raise StoreError(f"source document refused: {exc}") from exc
    if rows:
        _commit(conn)
        return {"status": "accepted", "row": rows[0]}
    cur = _exec(conn, """
        SELECT retrieval_status, attempt_count FROM rig_build.source_documents
        WHERE dedupe_key=%s""", (key,))
    have = _fetch_rows(cur)
    if have and have[0]["retrieval_status"] in ("FETCHED", "REPLACED"):
        _commit(conn)
        return {"status": "already_accepted", "row": have[0]}
    cur = _exec(conn, """
        UPDATE rig_build.source_documents
           SET retrieval_status=%s, attempt_count=attempt_count+1,
               content_sha256=COALESCE(%s, content_sha256),
               raw_sha256=COALESCE(%s, raw_sha256),
               last_error=%s, updated_at=CURRENT_TIMESTAMP
         WHERE dedupe_key=%s
        RETURNING dedupe_key, retrieval_status, attempt_count""",
        (retrieval_status, content_sha256, raw_sha256, last_error, key))
    rows = _fetch_rows(cur)
    _commit(conn)
    return {"status": "advanced", "row": rows[0]}


# -- outbox (B19) ---------------------------------------------------------------

def outbox_add(conn, *, topic: str, payload: dict,
               outbox_id: str | None = None) -> dict:
    cur = _exec(conn, """
        INSERT INTO rig_build.outbox (outbox_id, topic, payload)
        VALUES (%s,%s,%s::jsonb)
        RETURNING outbox_id, state""",
        (outbox_id or _mint_id(), _text(topic, "topic"),
         _canonical(payload)))
    rows = _fetch_rows(cur)
    _commit(conn)
    return {"status": "queued", "row": rows[0]}


def claim_outbox(conn, *, outbox_id: str, claim_owner: str,
                 lease_seconds: int = 120, now: str | None = None) -> dict:
    """Take (or RE-take after expiry) a one-item lease. Reclaiming a live
    lease returns status 'not_claimable' — the previous holder's lease is
    honoured. Every successful claim BUMPS claim_fence: the old holder's
    settle with the old fence is refused from then on (B47)."""
    if lease_seconds < 1:
        raise StoreError("lease_seconds must be >= 1")
    t = now or _now()
    expiry = (dt := _dt.datetime.fromisoformat(t)).replace(
        microsecond=0) + _dt.timedelta(seconds=int(lease_seconds))
    cur = _exec(conn, """
        UPDATE rig_build.outbox
           SET state='claimed', claim_owner=%s, claim_fence=claim_fence+1,
               lease_expires_at=%s, attempt_count=attempt_count+1,
               updated_at=%s
         WHERE outbox_id=%s
           AND (state='pending'
                OR (state='claimed' AND lease_expires_at < %s))
        RETURNING outbox_id, claim_owner, claim_fence, lease_expires_at""",
        (_text(claim_owner, "claim_owner"), expiry.isoformat(), t,
         _text(outbox_id, "outbox_id"), t))
    rows = _fetch_rows(cur)
    _commit(conn)
    return ({"status": "claimed", "row": rows[0]} if rows
            else {"status": "not_claimable",
                  "reason": "live lease held, already settled, or unknown — "
                            "unknown requires reconcile_unknown, never a "
                            "re-claim"})


def settle_outbox(conn, *, outbox_id: str, claim_owner: str, claim_fence: int,
                  state: str, receipt: str | None = None,
                  error: str | None = None,
                  now: str | None = None) -> dict:
    """Resolve a claim to sent | failed | unknown. `sent` requires the
    provider receipt. A fence that is not the CURRENT claim fence (a worker
    whose lease was reclaimed, or a replayed commit) is REFUSED — stale
    workers cannot commit. `unknown` is honest bookkeeping for ambiguous
    acks and is the only state that then needs reconciliation."""
    if state not in _OUTBOX_SETTLE:
        raise StoreError(f"settle state must be one of {_OUTBOX_SETTLE}; "
                         "in particular: never 'pending' — a blind resend "
                         "is not a settlement")
    if state == "sent" and not (receipt and receipt.strip()):
        raise StoreError("sent requires the provider receipt (read-back id)")
    t = now or _now()
    cur = _exec(conn, """
        UPDATE rig_build.outbox
           SET state=%s, last_error=%s, lease_expires_at=NULL, updated_at=%s
         WHERE outbox_id=%s AND claim_owner=%s AND claim_fence=%s
           AND state='claimed'
        RETURNING outbox_id, state, claim_fence""",
        (state, error, t, _text(outbox_id, "outbox_id"),
         _text(claim_owner, "claim_owner"), int(claim_fence)))
    rows = _fetch_rows(cur)
    if not rows:
        _commit(conn)
        raise StoreError(
            f"settlement refused for {outbox_id}: claim_fence {claim_fence} "
            "is stale (lease reclaimed) or the row is not claimed — a stale "
            "worker cannot commit")
    _commit(conn)
    return {"status": "settled", "row": rows[0]}


def reconcile_unknown(conn, *, outbox_id: str, resolution: str,
                      expected_fence: int, evidence: str,
                      now: str | None = None) -> dict:
    """The ONLY exit from 'unknown', and it is evidence-gated: name the
    remote read-back that proves what actually happened. Without evidence
    the row stays unknown — no amount of retrying here resends anything.
    resolution 'pending' means PROVEN-not-delivered and re-queues under a
    NEW fence; it is a decision, not a blind resend."""
    if resolution not in _OUTBOX_RECONCILE:
        raise StoreError(f"resolution must be one of {_OUTBOX_RECONCILE}")
    ev = _text(evidence, "evidence")
    t = now or _now()
    cur = _exec(conn, """
        UPDATE rig_build.outbox
           SET state=%s, claim_owner=NULL, lease_expires_at=NULL,
               last_error=%s, updated_at=%s
         WHERE outbox_id=%s AND state='unknown' AND claim_fence=%s
        RETURNING outbox_id, state, claim_fence""",
        (resolution, f"reconciled: {ev}", t,
         _text(outbox_id, "outbox_id"), int(expected_fence)))
    rows = _fetch_rows(cur)
    if not rows:
        _commit(conn)
        raise StoreError(
            f"reconciliation refused for {outbox_id}: not in unknown at "
            f"fence {expected_fence} — never a blind transition")
    _commit(conn)
    return {"status": "reconciled", "evidence": ev, "row": rows[0]}


# Deliberately absent: set_qualified, approve_omission, mark_pass, or any
# other verb that could turn a caller's wish into stored consent. tests/
# test_build_store.py asserts their non-existence as a standing guard.


def status(dsn: str | None = None) -> dict:
    """Read-only plane probe for MCP status. configured=false is honest
    UNCONFIGURED (no DSN discovered), never a fabricated pass. A denied read
    aborts the transaction: every count comes back None with the detail, never
    a partial fake."""
    out = {"plane": "record", "configured": False}
    try:
        conn = connect(dsn)
    except Exception as exc:  # noqa: BLE001 — unconfigured/unreachable, honest
        out["detail"] = str(exc)[:160]
        return out
    out["configured"] = True
    tables = ("cell_contracts", "process_versions", "cell_bindings", "runs",
              "run_events", "artifacts", "approval_refs", "source_documents", "outbox")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user")
            out["role"] = cur.fetchone()[0]
            counts = {}
            for table in tables:
                cur.execute(f"SELECT count(*) FROM rig_build.{table}")
                counts[table] = cur.fetchone()[0]
            out["counts"] = counts
            out["ok"] = True
    except Exception as exc:  # noqa: BLE001 — unreadable, report not swallow
        out["ok"] = False
        out["counts"] = dict.fromkeys(tables)
        out["detail"] = str(exc)[:160]
    finally:
        conn.close()
    return out


def _dicts(cur) -> list[dict]:
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_run(conn, *, run_id: str | None = None,
            idempotency_key: str | None = None) -> dict | None:
    """One run record by run_id or idempotency_key (B24, read-only)."""
    if run_id:
        cur = _exec(conn, "SELECT * FROM rig_build.runs WHERE run_id = %s", (run_id,))
    elif idempotency_key:
        cur = _exec(conn, "SELECT * FROM rig_build.runs WHERE idempotency_key = %s",
                    (idempotency_key,))
    else:
        raise StoreError("run_id or idempotency_key required")
    rows = _dicts(cur)
    return rows[0] if rows else None


def cell_contract(conn, *, cell_id: str,
                  criteria_version: str | None = None) -> list[dict]:
    """Sealed criteria contracts for one cell (B24, read-only), newest version first."""
    if criteria_version:
        cur = _exec(conn, "SELECT * FROM rig_build.cell_contracts "
                          "WHERE cell_id = %s AND criteria_version = %s",
                    (cell_id, criteria_version))
        return _dicts(cur)
    cur = _exec(conn, "SELECT * FROM rig_build.cell_contracts WHERE cell_id = %s "
                      "ORDER BY criteria_version DESC", (cell_id,))
    return _dicts(cur)
