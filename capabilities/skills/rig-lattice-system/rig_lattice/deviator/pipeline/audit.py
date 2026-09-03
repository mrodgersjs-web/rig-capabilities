"""DOCTRINE.md §8 Day 2 — append-only audit substrate.

UPDATE and DELETE are not exposed. Records are immutable once written.
The append-only contract is enforced at the Python API surface; the SQL
migration in migrations/001_audit_substrate.sql REVOKEs UPDATE/DELETE
at the database level for full enforcement.
"""
from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

# Default log location — switch to Supabase via env when ready
AUDIT_LOG_DIR = AUDITS_DIR / "log"
AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class AuditRecord:
    """Single immutable audit entry.

    Once written, never updated. Compose new records to supersede; never edit.
    """
    record_id: str
    timestamp_utc: str
    mission_id: str
    artifact_hash: str
    tier: str
    event_type: str           # gate | hook | review | mutation | promotion
    payload: dict             # the actual data (gate verdict, scorecard, etc.)
    actor: str = "system"     # who/what produced this record
    parent_record_id: str | None = None  # for chained records

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def content_hash(self) -> str:
        """Hash the record content (for tamper detection)."""
        payload_str = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:24]


class AppendOnlyAuditLog:
    """Append-only writer. NO update_record(), NO delete_record() — by design."""

    def __init__(self, log_dir: Path = AUDIT_LOG_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def append(self, record: AuditRecord) -> str:
        """Write a record. Returns the record_id. Cannot be undone."""
        # Sharded by date for log rotation
        date_shard = time.strftime("%Y%m%d", time.gmtime())
        log_path = self.log_dir / f"audit-{date_shard}.jsonl"
        with log_path.open("a") as f:
            line = json.dumps(record.to_dict(), default=str)
            f.write(line + "\n")
        return record.record_id

    def read_mission(self, mission_id: str) -> list[AuditRecord]:
        """Read all records for a given mission_id, chronologically."""
        records: list[AuditRecord] = []
        for log_path in sorted(self.log_dir.glob("audit-*.jsonl")):
            for line in log_path.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    if d.get("mission_id") == mission_id:
                        records.append(AuditRecord(**d))
                except (json.JSONDecodeError, TypeError):
                    continue
        return records

    def read_recent(self, limit: int = 100) -> list[AuditRecord]:
        """Read most recent N records across all shards."""
        records: list[AuditRecord] = []
        for log_path in sorted(self.log_dir.glob("audit-*.jsonl"), reverse=True):
            for line in reversed(log_path.read_text().splitlines()):
                if not line.strip():
                    continue
                try:
                    records.append(AuditRecord(**json.loads(line)))
                    if len(records) >= limit:
                        return records
                except (json.JSONDecodeError, TypeError):
                    continue
        return records


# Module-level singleton
_log = AppendOnlyAuditLog()


def audit_log(event_type: str,
               mission_id: str,
               artifact_hash: str,
               payload: dict,
               tier: str = "client",
               actor: str = "system",
               parent_record_id: str | None = None) -> str:
    """Write an append-only audit record. Returns the record_id."""
    record = AuditRecord(
        record_id=f"audit-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        mission_id=mission_id,
        artifact_hash=artifact_hash,
        tier=tier,
        event_type=event_type,
        payload=payload,
        actor=actor,
        parent_record_id=parent_record_id,
    )
    return _log.append(record)


def hash_artifact(text: str) -> str:
    """Standardized artifact hashing for audit linkage."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
