#!/usr/bin/env python3
"""Licence ledger for every blob in docs/skillos/warehouse.

Ownership is not licence evidence, so each blob gets a basis: the licence the asset
itself declares (frontmatter `license:`), the licence file shipped beside it, or — only
when nothing upstream is marked anywhere near it — the repository's own MIT grant,
asserted because the repo is the author of record. Anything that looks vendored but
carries no licence lands in `needs_review` instead of being waved through.
"""
from __future__ import annotations
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rig_capabilities.catalog import Repo
from rig_capabilities.skillos import (UNIVERSE, _content_digest, _payload_path,
                                      restore_blob)

OUT = ROOT / "docs/skillos/blob-license-ledger.json"
SPDX = (("Apache License", "Apache-2.0"),
        ("Permission is hereby granted", "MIT"),
        ("MIT License", "MIT"),
        ("BSD", "BSD (uncatalogued)"),
        ("ISC", "ISC"),
        ("CC0", "CC0-1.0"))
PERMISSIVE = {"MIT", "Apache-2.0", "ISC", "CC0-1.0", "0BSD"}
UPSTREAM = re.compile(r"https?://\S+")


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def frontmatter_license(descriptor: Path | None) -> str | None:
    if descriptor is None or not descriptor.is_file():
        return None
    lines = descriptor.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:40]:
        if line.strip() == "---":
            break
        m = re.match(r"^\s*license:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip("'\"")
    return None


def sibling_license(payload: Path) -> tuple[str | None, Path | None]:
    base = payload.parent if payload.is_file() else payload
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENCE.txt",
                 "COPYING", "COPYING.txt", "NOTICE"):
        for cand in (base / name, base / name.lower()):
            if cand.is_file():
                text = cand.read_text(encoding="utf-8", errors="replace")[:4000]
                for needle, spdx in SPDX:
                    if needle in text:
                        return spdx, cand
                return "unrecognised licence text", cand
    return None, None


def upstream_marked(payload: Path) -> str | None:
    """An asset that names an upstream URL is a vendoring signal, not our authorship."""
    base = payload.parent if payload.is_file() else payload
    for cand in (base / "PROVENANCE.md", base / "PROVENANCE",):
        if cand.is_file():
            hit = UPSTREAM.search(cand.read_text(encoding="utf-8", errors="replace"))
            return hit.group(0).rstrip(").,") if hit else str(cand)
    return None


def classify(payload: Path) -> dict:
    desc = payload if payload.is_file() else next(
        (p for p in (payload / "SKILL.md", payload / "index.md") if p.is_file()), None)
    licence, file_ = sibling_license(payload)
    marked = upstream_marked(payload)
    if licence:
        return {"license": licence, "basis": f"asset licence file {file_.name}",
                "archive_allowed": licence in PERMISSIVE}
    fm = frontmatter_license(desc)
    if fm:
        return {"license": fm, "basis": "frontmatter license:",
                "archive_allowed": fm in PERMISSIVE}
    if marked:
        return {"license": None, "basis": f"upstream marked ({marked}), no licence found",
                "archive_allowed": False}
    return {"license": "MIT", "basis": "repo LICENSE (MIT, RIG / mrodgersjs-web); "
                                       "no upstream marker in or beside the asset",
            "archive_allowed": True}


def main() -> int:
    """Classify every LIVE canonical asset by prospective digest.

    Inventory comes from the index, not from what happens to be filed in the warehouse:
    `dump`/`restock` only write a blob after this ledger clears its digest, so a generator
    that read only stored blobs could never licence anything new. Nothing here writes to
    the warehouse — the digest is what `_store_for` WOULD file.
    """
    repo = Repo(ROOT)
    canonical = [a for a in (repo.load_index().get("assets") or [])
                 if (a.get("source") or "") == "canonical"]
    pinned: dict[str, dict] = {}
    row_paths: dict[str, str] = {}
    stored = 0
    for line in (ROOT / UNIVERSE).read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        store = row.get("store") or {}
        if store.get("status") == "blob":
            stored += 1
            key = f"{row['kind']}/{row['id']}"
            pinned[key] = store
            row_paths[key] = row.get("path") or ""
    entries, needs_review, drift = [], [], []
    for a in sorted(canonical, key=lambda x: (x.get("kind") or "", x.get("id") or "")):
        key = f"{a.get('kind') or ''}/{a.get('id') or ''}"
        payload = _payload_path(a)
        digest = _content_digest(payload)
        scope = None if payload is None else ("bundle" if payload.is_dir() else "file")
        if payload is None:
            verdict = {"license": None, "basis": "payload not resolvable",
                       "archive_allowed": False}
        else:
            verdict = classify(payload)
        entries.append({
            "kind": a.get("kind"), "id": a.get("id"), "catalog_sha": a.get("sha"),
            "blob_sha256": digest, "payload_scope": scope, "path": _rel(payload),
            **verdict,
        })
        if not verdict["archive_allowed"]:
            needs_review.append(key)          # denied even with nothing archived
        elif pinned.get(key, {}).get("blob_sha256") not in (None, digest):
            drift.append(key)                 # warehouse holds other content for this id

    # A pinned blob whose content has since drifted is a different artifact: classify the
    # bytes actually filed, not today's payload, or the ledger would clear content it never
    # looked at (and the row would read as unlicensed forever).
    cleared = {e["blob_sha256"] for e in entries if e["archive_allowed"]}
    for key, store in sorted(pinned.items()):
        digest = store.get("blob_sha256") or ""
        if not digest or digest in cleared:
            continue
        kind, _, aid = key.partition("/")
        with tempfile.TemporaryDirectory() as td:
            got = restore_blob(Repo(ROOT), digest, Path(td))
            if not got.get("ok"):
                verdict = {"license": None,
                           "basis": f"stored blob unrestorable: {got.get('error')}",
                           "archive_allowed": False}
            else:
                # bundle unpacks into the dir; a file lands at <tmp>/payload — classify the
                # bytes themselves, or a vendored file's frontmatter is never read.
                verdict = classify(Path(td) if got.get("kind") == "bundle"
                                   else Path(td) / "payload")
        entries.append({
            "kind": kind, "id": aid, "catalog_sha": store.get("catalog_sha"),
            "blob_sha256": digest, "payload_scope": store.get("payload_scope"),
            "path": row_paths.get(key, ""),
            "content": "stored_snapshot",
            **verdict,
        })
        if not verdict["archive_allowed"]:
            needs_review.append(key)
    doc = {
        "generated_by": "scripts/blob_license_ledger.py",
        "doctrine": "docs/SOURCE-LICENSE.md",
        "repo_license": "MIT (LICENSE, Copyright (c) 2026 RIG / mrodgersjs-web)",
        "canonical_assets": len(canonical),
        "stored_blobs": stored,
        "archive_allowed": sum(1 for e in entries if e["archive_allowed"]),
        "needs_review": sorted(needs_review),
        "stored_content_drift": sorted(drift),
        "entries": entries,
    }
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "canonical_assets": doc["canonical_assets"],
        "stored_blobs": doc["stored_blobs"],
        "archive_allowed": doc["archive_allowed"],
        "needs_review_count": len(needs_review),
        "needs_review": doc["needs_review"][:10],
        "stored_content_drift": drift[:10],
        "out": str(OUT),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
