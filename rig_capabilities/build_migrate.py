"""rig_build migration runner (B12/B13): plan / apply / verify — never auto.

plan    offline: reads scripts/ddl_rig_build.sql, prints the entity inventory,
        DDL sha256, rollback section, and writes a timestamped receipt under
        runs/agentic-stack-buildout/backend/. No connection needed.
apply   --dsn ... --confirm <exact-token>: refuses without the exact token
        (shown by plan), PROVES TARGET IDENTITY first with
        `select current_database(), current_user`, echoes the probe into the
        receipt, then applies the portable section followed by the
        Postgres-only section, one transaction per section.
verify  --dsn ...: re-reads the LIVE catalog (schema/table/constraint/trigger/
        role/policy presence). A PASS is this fresh read, never a stored
        receipt.

Nothing in this module runs on import, from a hook, or from a scheduler.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):  # direct `python3 rig_capabilities/build_migrate.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rig_capabilities import build_store

CONFIRM_TOKEN = "rig_build__ddl_v1__"
RECEIPT_DIR = (build_store.REPO / "runs" / "agentic-stack-buildout" / "backend")

_TABLES = ("cell_contracts", "process_versions", "cell_bindings", "runs",
           "run_events", "artifacts", "approval_refs", "source_documents",
           "outbox")
_TRIGGERS = ("run_events_append_only", "run_events_next_sequence",
             "cell_contracts_immutable", "process_versions_immutable",
             "approval_refs_immutable", "runs_fencing_monotonic")
_ROLES = ("rig_build_data_plane", "rig_build_operator")


def ddl_text() -> str:
    return build_store.DDL_PATH.read_text(encoding="utf-8")


def plan(receipt_path: Path | None = None) -> dict:
    """Offline plan: derived ONLY from the committed DDL bytes. Proves
    shape, not application — application status is `verify`'s job."""
    text = ddl_text()
    sha = hashlib.sha256(text.encode()).hexdigest()
    sections = build_store.ddl_sections(build_store.DDL_PATH)
    portable = sections["APPLY-PORTABLE"].lower()
    missing = [t for t in _TABLES if f"rig_build.{t}" not in
               sections["APPLY-PORTABLE"]]
    out = {
        "action": "plan",
        "ddl": str(build_store.DDL_PATH.relative_to(build_store.REPO)),
        "ddl_sha256": sha,
        "confirm_token": CONFIRM_TOKEN + sha[:12],
        "schema": "rig_build",
        "entities": list(_TABLES),
        "entities_missing_from_portable": missing,
        "pg_only_law": {
            "triggers": list(_TRIGGERS),
            "roles": list(_ROLES),
            "rls_enabled_on": ["runs", "run_events", "artifacts", "outbox",
                               "approval_refs"],
        },
        "rollback_available": "ROLLBACK" in sections,
        "rollback_statement_count": sum(
            1 for ln in sections.get("ROLLBACK", "").splitlines()
            if ln.startswith("-- DROP")),
        "catalog_sync_law": "capabilities sync must NEVER truncate rig_build",
        "connection": "NONE — plan proves shape only; a stored plan is "
                      "never evidence the schema is live (that is verify)",
    }
    if receipt_path is not None:
        _write_receipt(receipt_path, out)
    return out


def _write_receipt(path: Path, doc: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def _stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _identity_probe(conn) -> dict:
    cur = conn.cursor()
    cur.execute("select current_database(), current_user")
    db, user = cur.fetchone()
    return {"current_database": db, "current_user": user}


def apply(dsn: str, confirm: str) -> dict:
    """Applies to a proven target. Order is law: identity probe FIRST, then
    portable, then PG-only, each committed separately; any failure rolls the
    transaction back and reports the rollback command."""
    expected = CONFIRM_TOKEN + hashlib.sha256(
        ddl_text().encode()).hexdigest()[:12]
    if confirm != expected:
        return {"action": "apply", "status": "refused",
                "reason": f"missing/wrong confirmation token; the exact "
                          f"token for the CURRENT ddl bytes is {expected}",
                "applied": False}
    conn = build_store.connect(dsn)
    try:
        probe = _identity_probe(conn)  # B12: prove the target before touching it
        sections = build_store.ddl_sections(build_store.DDL_PATH)
        applied = []
        for name in ("APPLY-PORTABLE", "APPLY-PGONLY"):
            cur = conn.cursor()
            cur.execute(sections[name])
            conn.commit()
            applied.append(name)
    except Exception as exc:
        conn.rollback()
        return {"action": "apply", "status": "failed", "error": str(exc),
                "rollback": "extract the ROLLBACK section of "
                            "scripts/ddl_rig_build.sql (drop-order is "
                            "already reversed)", "applied": False}
    finally:
        conn.close()
    doc = {"action": "apply", "status": "applied",
           "identity_probe": probe, "sections_applied": applied,
           "ddl_sha256": hashlib.sha256(ddl_text().encode()).hexdigest(),
           "note": "run `verify` against the same target — this receipt is "
                   "not the proof"}
    _write_receipt(RECEIPT_DIR / f"apply-{_stamp()}.json", doc)
    return doc


def verify(dsn: str) -> dict:
    """Fresh catalog read. Every check is a live query; nothing is inferred
    from receipts or from the DDL file."""
    conn = build_store.connect(dsn)
    try:
        probe = _identity_probe(conn)
        cur = conn.cursor()
        cur.execute("select nspname from pg_namespace where nspname='rig_build'")
        schema_ok = bool(cur.fetchone())
        cur.execute("""select tablename from pg_tables where schemaname='rig_build'""")
        tables = sorted(r[0] for r in cur.fetchall())
        cur.execute("""select tgname from pg_trigger t
                       join pg_class c on c.oid=t.tgrelid
                       join pg_namespace n on n.oid=c.relnamespace
                       where n.nspname='rig_build' and not t.tgisinternal""")
        triggers = sorted(r[0] for r in cur.fetchall())
        cur.execute("""select count(*) from pg_constraint
                       where connamespace='rig_build'::regnamespace""")
        constraints = cur.fetchone()[0]
        cur.execute("""select polname from pg_policy p
                       join pg_class c on c.oid=p.polrelid
                       join pg_namespace n on n.oid=c.relnamespace
                       where n.nspname='rig_build'""")
        policies = sorted(r[0] for r in cur.fetchall())
        cur.execute("""select rolname from pg_roles
                       where rolname in ('rig_build_data_plane','rig_build_operator')""")
        roles = sorted(r[0] for r in cur.fetchall())
    finally:
        conn.close()
    missing_tables = [t for t in _TABLES if t not in tables]
    missing_triggers = [t for t in _TRIGGERS if t not in triggers]
    missing_roles = [r for r in _ROLES if r not in roles]
    ok = (schema_ok and not missing_tables and not missing_triggers
          and not missing_roles and len(policies) >= 7)
    return {"action": "verify", "identity_probe": probe,
            "verdict": "PASS" if ok else "FAIL",
            "schema_present": schema_ok, "tables": tables,
            "missing_tables": missing_tables,
            "triggers": triggers, "missing_triggers": missing_triggers,
            "constraint_count": constraints, "policies": policies,
            "roles": roles, "missing_roles": missing_roles}


def rollback_plan() -> dict:
    sections = build_store.ddl_sections(build_store.DDL_PATH)
    stmts = [ln[3:] for ln in sections.get("ROLLBACK", "").splitlines()
             if ln.startswith("-- DROP")]
    return {"action": "rollback-plan", "statements": stmts,
            "warning": "DESTROYS run state; execute manually, not via apply"}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    def flag(name):
        return argv[argv.index(name) + 1] if name in argv else None
    if cmd == "plan":
        out = plan(RECEIPT_DIR / f"plan-{_stamp()}.json")
        print(json.dumps(out, indent=1))
        return 0
    if cmd == "rollback-plan":
        print(json.dumps(rollback_plan(), indent=1))
        return 0
    if cmd == "apply":
        out = apply(flag("--dsn") or "", flag("--confirm") or "")
        print(json.dumps(out, indent=1))
        return 0 if out.get("status") == "applied" else 2
    if cmd == "verify":
        try:
            out = verify(flag("--dsn") or "")
        except Exception as exc:  # fail closed, named
            print(json.dumps({"action": "verify", "verdict": "BLOCKED",
                              "reason": str(exc)}))
            return 2
        print(json.dumps(out, indent=1))
        return 0 if out["verdict"] == "PASS" else 2
    print(f"unknown command: {cmd} (plan|apply|verify|rollback-plan)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
