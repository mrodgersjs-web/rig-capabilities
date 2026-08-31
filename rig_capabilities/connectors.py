"""SQL/API bundle connectors (stdlib).

config.json `connectors`:

  {"label": "kb", "type": "sqlite", "path": "data/kb.sqlite",
   "query": "SELECT id, name, description, tags FROM docs", "kind": "skill"}

  {"label": "docs", "type": "http", "url": "https://host/api/docs",
   "items": "data", "id_field": "slug", "name_field": "title",
   "description_field": "summary", "kind": "skill"}

A missing file, failed HTTP, or unknown type is skipped and recorded in
`.context/connector-last-error.json` — never invented as assets.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .okf import meta as _okf_meta

_HTTP_TIMEOUT = 8


def _sha(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update((p or "").encode())
    return h.hexdigest()[:12]


def _row_asset(label: str, source_kind: str, kind: str, rec: dict) -> dict | None:
    aid = str(rec.get("id") or rec.get("slug") or rec.get("name") or "").strip()
    if not aid:
        return None
    name = str(rec.get("name") or rec.get("title") or aid)
    desc = str(rec.get("description") or rec.get("summary") or rec.get("body") or "")[:400]
    tags = rec.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.replace(";", ",").split(",") if t.strip()]
    status = str(rec.get("status") or "")
    fm = {"name": name, "description": desc, "status": status,
          "acl": rec.get("acl") or rec.get("visibility") or "",
          "owner": rec.get("owner") or "", "domain": rec.get("domain") or ""}
    src = f"{source_kind}:{label}"
    return {
        "id": aid,
        "kind": str(rec.get("kind") or kind),
        "source": src,
        "path": f"connector://{label}/{aid}",
        "abs_path": "",
        "name": name,
        "description": desc,
        "tags": [str(t) for t in tags][:8],
        "sha": _sha(aid, desc, src),
        "installable": False,
        "okf": _okf_meta(fm, src),
        "connector": label,
    }


def _record_error(repo, label: str, error: str) -> None:
    d = Path(repo.root) / ".context"
    d.mkdir(exist_ok=True)
    rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "label": label, "error": error}
    (d / "connector-last-error.json").write_text(json.dumps(rec, indent=1))
    with (d / "connector-errors.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")


def ingest_sqlite(repo, spec: dict) -> list:
    label = spec["label"]
    path = Path(spec.get("path") or "").expanduser()
    if not path.is_absolute():
        path = Path(repo.root) / path
    if not path.exists():
        _record_error(repo, label, f"sqlite missing: {path}")
        return []
    query = spec.get("query") or "SELECT * FROM capabilities"
    kind = spec.get("kind") or "skill"
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=3)
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(query).fetchall()
        finally:
            con.close()
    except sqlite3.Error as exc:
        _record_error(repo, label, f"sqlite: {exc}")
        return []
    out = []
    for row in rows:
        rec = {k: row[k] for k in row.keys()}
        a = _row_asset(label, "sql", kind, rec)
        if a:
            out.append(a)
    return out


def ingest_http(repo, spec: dict) -> list:
    label = spec["label"]
    url = spec.get("url") or ""
    if not url:
        _record_error(repo, label, "http: no url")
        return []
    kind = spec.get("kind") or "skill"
    try:
        req = urllib.request.Request(
            url, headers={"Accept": "application/json",
                          "User-Agent": "rig-capabilities-connector/5"})
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
            raw = r.read()
        data = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        _record_error(repo, label, f"http: {type(exc).__name__}: {exc}")
        return []
    items_key = spec.get("items")
    if items_key and isinstance(data, dict):
        items = data.get(items_key) or []
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items") or data.get("data") or data.get("assets") or []
    else:
        items = []
    if not isinstance(items, list):
        _record_error(repo, label, "http: items is not a list")
        return []
    id_f = spec.get("id_field") or "id"
    name_f = spec.get("name_field") or "name"
    desc_f = spec.get("description_field") or "description"
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rec = {
            "id": item.get(id_f),
            "name": item.get(name_f),
            "description": item.get(desc_f),
            "tags": item.get("tags") or [],
            "kind": item.get("kind") or kind,
            "status": item.get("status") or "",
            "acl": item.get("acl") or "",
        }
        a = _row_asset(label, "api", kind, rec)
        if a:
            out.append(a)
    return out


def ingest_postgres(repo, spec: dict) -> list:
    """Optional: requires psycopg2. Honest skip if the driver is absent."""
    label = spec["label"]
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        _record_error(repo, label, "postgres: psycopg2 not installed")
        return []
    dsn = spec.get("dsn") or ""
    if not dsn:
        _record_error(repo, label, "postgres: no dsn")
        return []
    query = spec.get("query") or "SELECT id, name, description FROM capabilities"
    kind = spec.get("kind") or "skill"
    try:
        con = psycopg2.connect(dsn, connect_timeout=3)
        try:
            with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
        finally:
            con.close()
    except Exception as exc:
        _record_error(repo, label, f"postgres: {type(exc).__name__}: {exc}")
        return []
    out = []
    for row in rows:
        a = _row_asset(label, "sql", kind, dict(row))
        if a:
            out.append(a)
    return out


_INGEST = {
    "sqlite": ingest_sqlite,
    "http": ingest_http,
    "api": ingest_http,
    "postgres": ingest_postgres,
    "postgresql": ingest_postgres,
}


def connector_assets(repo) -> list:
    out = []
    for spec in repo.config().get("connectors") or []:
        if not isinstance(spec, dict) or not spec.get("label"):
            continue
        fn = _INGEST.get(str(spec.get("type") or "").lower())
        if fn is None:
            _record_error(repo, spec.get("label", "?"),
                          f"unknown type: {spec.get('type')}")
            continue
        out.extend(fn(repo, spec))
    return out


def connector_status(repo) -> dict:
    specs = repo.config().get("connectors") or []
    err_p = Path(repo.root) / ".context" / "connector-last-error.json"
    last = None
    if err_p.exists():
        try:
            last = json.loads(err_p.read_text())
        except json.JSONDecodeError:
            last = None
    return {
        "configured": len(specs),
        "labels": [s.get("label") for s in specs if isinstance(s, dict)],
        "types": [s.get("type") for s in specs if isinstance(s, dict)],
        "last_error": last,
    }
