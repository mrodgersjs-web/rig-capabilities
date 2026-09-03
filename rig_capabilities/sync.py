"""V14: sync the capability index (+ packs/ratings) into Postgres.

psycopg2 is imported lazily; this module imports cleanly without it.
DSN is never hardcoded: RIG_CAP_DSN env wins, else docker inspect rig-dev-db.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def discover_dsn() -> str | None:
    """Env override, then the rig-dev-db container env. No credential hunting."""
    env = os.environ.get("RIG_CAP_DSN")
    if env:
        return env
    try:
        out = subprocess.run(
            ["docker", "inspect", "rig-dev-db", "--format", "{{json .Config.Env}}"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        pairs = json.loads(out)
        kv = dict(p.split("=", 1) for p in pairs if "=" in p)
        pw, user, db = (kv.get("POSTGRES_PASSWORD"), kv.get("POSTGRES_USER", "postgres"),
                        kv.get("POSTGRES_DB", "postgres"))
        if pw:
            return f"postgresql://{user}:{pw}@127.0.0.1:5433/{db}"
    except Exception:
        pass
    return None


def apply_ddl(repo, conn) -> None:
    ddl = (Path(repo.root) / "scripts" / "ddl_capabilities.sql")
    if not ddl.exists():
        ddl = Path(__file__).resolve().parent.parent / "scripts" / "ddl_capabilities.sql"
    with conn.cursor() as cur:
        cur.execute(ddl.read_text())
    conn.commit()



def asset_rows(doc: dict, overlay: dict) -> list:
    from .taxonomy import classify
    rows = []
    for a in doc["assets"]:
        lane = overlay.get(a["id"]) or classify(a)
        rows.append((a["id"], a["kind"], a["source"], a.get("sha"),
                     a.get("description"), json.dumps(a.get("tags") or []),
                     json.dumps(a.get("okf") or {}), json.dumps(a.get("quality") or {}),
                     lane))
    return rows


def pack_rows(repo) -> list:
    rows = []
    for p in sorted(Path(repo.root).glob(".context/pack-*.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        rows.append((d.get("id") or p.stem, d.get("requester") or "",
                     d.get("intent") or "", json.dumps(d)))
    return rows


def rating_rows(repo) -> list:
    f = Path(repo.root) / ".context" / "ratings.jsonl"
    rows = []
    if f.exists():
        for ln in f.read_text().splitlines():
            try:
                d = json.loads(ln)
            except Exception:
                continue
            rows.append((d.get("pack", ""), d.get("verdict", ""),
                         json.dumps(d.get("ids") or [])))
    return rows


def _upsert_many(cur, sql: str, rows: list, batch: int = 500) -> int:
    n = 0
    for i in range(0, len(rows), batch):
        cur.executemany(sql, rows[i:i + batch])
        n += len(rows[i:i + batch])
    return n


SQL_ASSET = """INSERT INTO capabilities.assets
 (id, kind, source, sha, description, tags, okf, quality, lane)
 VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s)
 ON CONFLICT (id, kind, source) DO UPDATE SET
   sha=EXCLUDED.sha, description=EXCLUDED.description, tags=EXCLUDED.tags,
   okf=EXCLUDED.okf, quality=EXCLUDED.quality, lane=EXCLUDED.lane,
   updated_at=now()"""

SQL_PACK = """INSERT INTO capabilities.packs (id, requester, intent, artifact)
 VALUES (%s,%s,%s,%s::jsonb)
 ON CONFLICT (id) DO UPDATE SET requester=EXCLUDED.requester,
   intent=EXCLUDED.intent, artifact=EXCLUDED.artifact"""

SQL_RATING = "INSERT INTO capabilities.ratings (pack, verdict, ids) VALUES (%s,%s,%s::jsonb)"


def sync(repo, dsn: str | None = None) -> dict:
    try:
        import psycopg2
    except ImportError:
        raise RuntimeError("psycopg2 not installed — db-sync unavailable")
    dsn = dsn or discover_dsn()
    if not dsn:
        raise RuntimeError("no DSN: set RIG_CAP_DSN or run rig-dev-db")
    doc = repo.load_index()
    from .lanes import load_overlay
    overlay = load_overlay(repo)
    conn = psycopg2.connect(dsn, connect_timeout=5)
    try:
        apply_ddl(repo, conn)
        with conn.cursor() as cur:
            # sync owns the mirror: rebuild so repo-side deletions disappear
            # (ponytail: full reload each sync; incremental prune if volume matters)
            cur.execute("truncate capabilities.assets, capabilities.packs, capabilities.ratings")
            assets = _upsert_many(cur, SQL_ASSET, asset_rows(doc, overlay))
            packs = _upsert_many(cur, SQL_PACK, pack_rows(repo))
            ratings = _upsert_many(cur, SQL_RATING, rating_rows(repo))
        conn.commit()
    finally:
        conn.close()
    return {"assets": assets, "packs": packs, "ratings": ratings}
