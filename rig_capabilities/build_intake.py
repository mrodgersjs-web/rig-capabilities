"""B31 intake worker (T1: pure collect -> validate -> hash -> route).

Deterministic intake against the persisted rig_build run records:
validate a closed packet schema, hash content, record the source
document (resumable, deduplicated) and the run (idempotency-keyed),
then route the work command onto the outbox for the selected owner.

Refusals are the product here:
- unknown keys, malformed cell ids, tampered content hashes  -> exit 2
- unknown or missing route: NO DEFAULT (an ambiguous packet is
  refused, never routed by convenience)
- replay of the same packet: the run replays and exactly one outbox
  command exists — a re-run cannot double-route work.

No model, no scheduler, no cadence: cadence (if ever) is T2/T3 owner's
decision; this module answers one packet at a time.

CLI: python3 -m rig_capabilities.build_intake ingest --file PACKET.json --db PATH
Exit: 0 accepted|replayed|already_accepted, 2 refused, 1 unexpected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys

from . import build_store

_CELL = re.compile(r"^L[1-7]-D[1-3]-A[1-4]-(I1|Q1|R|S|Q2|P|I2)$")
_SHA = re.compile(r"^[0-9a-f]{64}$")

# Route table: packet route -> outbox topic. An unknown route is a
# refusal, never a fallback (A51). A37: fetched bytes are payload here —
# routing never interprets them.
ROUTES = {"document": "intake.document", "corpus": "corpus.ingest"}

_REQUIRED = ("cell_id", "criteria_version", "process_key", "process_version",
             "route", "source")
_SOURCE_KEYS = {"url", "provider", "kind", "content", "content_sha256"}


class Refused(Exception):
    pass


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(packet) -> dict:
    """Closed-schema validation + hash verification. Returns the derived
    fields; raises Refused with the named reason for every gap."""
    if not isinstance(packet, dict):
        raise Refused("packet must be a JSON object")
    missing = [k for k in _REQUIRED if k not in packet]
    if missing:
        raise Refused(f"missing key(s): {', '.join(missing)}")
    extra = set(packet) - set(_REQUIRED)
    if extra:
        raise Refused(f"unknown key(s): {', '.join(sorted(extra))}")
    cell = packet["cell_id"]
    if not isinstance(cell, str) or not _CELL.match(cell):
        raise Refused(f"cell_id is not a canonical coordinate: {cell!r}")
    route = packet["route"]
    if route not in ROUTES:
        raise Refused(f"unknown route {route!r}; known routes: "
                      f"{sorted(ROUTES)} — routing has no default")
    src = packet["source"]
    if not isinstance(src, dict) or "url" not in src:
        raise Refused("source must be an object with a url")
    bad = set(src) - _SOURCE_KEYS
    if bad:
        raise Refused(f"source unknown key(s): {', '.join(sorted(bad))}")
    content = src.get("content")
    declared = src.get("content_sha256")
    raw_sha = None
    if content is not None:
        if not isinstance(content, str):
            raise Refused("source content must be a string")
        raw_sha = _sha256_hex(content.encode())
        if declared is not None and declared != raw_sha:
            raise Refused(
                "content hash mismatch: declared content_sha256 does not "
                "match the bytes — intake refuses tampered content")
    elif declared is not None and not _SHA.match(str(declared)):
        raise Refused("declared content_sha256 is not hex64")
    return {
        "dedupe_key": _sha256_hex(src["url"].encode()),
        "content_sha256": raw_sha if raw_sha is not None else declared,
        "raw_sha256": raw_sha,
        "topic": ROUTES[route],
    }


def ingest(conn, packet: dict) -> dict:
    """One packet, end to end: validate -> hash -> persist -> route.

    Routing is self-healing: the outbox id is derived from the dedupe
    key, so a replay that finds the run committed but its command
    missing (crash between start_run's commit and the add) re-adds it;
    when the row exists, nothing is ever added twice.
    """
    d = validate(packet)
    src = packet["source"]
    doc = build_store.put_source_document(
        conn, dedupe_key=d["dedupe_key"], url=src["url"],
        provider=str(src.get("provider", "unknown")),
        kind=str(src.get("kind", "document")),
        retrieval_status="FETCHED" if d["raw_sha256"] else "PENDING",
        content_sha256=d["content_sha256"], raw_sha256=d["raw_sha256"])
    started = build_store.start_run(
        conn, cell_id=packet["cell_id"],
        criteria_version=str(packet["criteria_version"]),
        process_key=str(packet["process_key"]),
        process_version=str(packet["process_version"]),
        idempotency_key=f"intake:{d['dedupe_key']}", started_by="b31-intake")
    outbox_id = "cmd-" + d["dedupe_key"][:16]
    cur = build_store._exec(
        conn, "SELECT outbox_id FROM rig_build.outbox WHERE outbox_id=%s",
        (outbox_id,))
    if build_store._fetch_rows(cur):
        effect = "already_routed"
    else:
        try:
            build_store.outbox_add(
                conn, topic=d["topic"],
                payload={"cell_id": packet["cell_id"],
                         "dedupe_key": d["dedupe_key"],
                         "content_sha256": d["content_sha256"],
                         "run_id": started["row"]["run_id"]},
                outbox_id=outbox_id)
            effect = "routed"
        except Exception:
            # A concurrent replay won the race on the derived id, or a
            # rare integrity surprise. The after-check discriminates: the
            # row exists now -> already_routed; it doesn't -> real failure.
            cur = build_store._exec(
                conn, "SELECT outbox_id FROM rig_build.outbox "
                      "WHERE outbox_id=%s", (outbox_id,))
            if not build_store._fetch_rows(cur):
                raise
            effect = "already_routed"
    return {"status": started["status"], "document": doc["status"],
            "effect": effect, "run_id": started["row"]["run_id"],
            "topic": d["topic"], "dedupe_key": d["dedupe_key"]}


def pending(conn) -> list[dict]:
    """Routing visibility (read-only): work commands awaiting the owner."""
    cur = build_store._exec(
        conn, "SELECT outbox_id, topic FROM rig_build.outbox "
              "WHERE state = 'pending' ORDER BY created_at")
    return build_store._fetch_rows(cur)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="build_intake")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ing = sub.add_parser("ingest")
    ing.add_argument("--file", required=True)
    ing.add_argument("--db", required=True, help="sqlite file (fixture lane)")
    pend = sub.add_parser("pending")
    pend.add_argument("--db", required=True)
    args = ap.parse_args(argv)

    import sqlite3
    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        if args.cmd == "pending":
            print(json.dumps(pending(conn)))
            return 0
        packet = json.loads(open(args.file).read())
        try:
            out = ingest(conn, packet)
        except Refused as exc:
            print(json.dumps({"status": "refused", "reason": str(exc)}))
            return 2
        print(json.dumps(out))
        return 0 if out["status"] in ("started", "replayed") else 2
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
