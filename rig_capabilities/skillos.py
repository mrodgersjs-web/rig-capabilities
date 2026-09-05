"""SkillOS v4–v5: universe snapshot, restorable store, witnesses, orphan plant.

Fail closed on store: never invent git URL+commit recipes. Canonical bundles
are blobbed. Clean external descriptors may advertise immutable git recipes;
unlicensed or unproven external payloads remain unresolved and cannot retire.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from .catalog import DIR_DESCRIPTOR, Repo

SKILLOS = Path("docs/skillos")
UNIVERSE = SKILLOS / "universe.jsonl"
RECEIPTS = SKILLOS / "receipts.jsonl"
BLOB_LEDGER = SKILLOS / "blob-license-ledger.json"
WAREHOUSE = SKILLOS / "warehouse"
WITNESS_DIR = SKILLOS / "witness" / "canonical"
ORPHAN_DIR = SKILLOS / "orphan"
TOP50 = SKILLOS / "04-TOP-50-JTBD.md"

_SHA12 = re.compile(r"^[0-9a-f]{12}$")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HTTPS_GIT = re.compile(r"^https://[^\s]+$")


def _key(kind: str, aid: str) -> str:
    return f"{kind}/{aid}"


def _payload_path(asset: dict) -> Path | None:
    raw = asset.get("abs_path") or asset.get("path") or ""
    p = Path(raw)
    if p.is_file():
        return p
    if p.is_dir():
        desc = DIR_DESCRIPTOR.get(asset.get("kind") or "")
        if desc and (p / desc).is_file():
            return p
    return None


def _bundle_bytes(dirpath: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for f in sorted(x for x in dirpath.rglob("*") if x.is_file()):
            data = f.read_bytes()
            info = tarfile.TarInfo(name=str(f.relative_to(dirpath)).replace("\\", "/"))
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()

def _tree_manifest(dirpath: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in dirpath.rglob("*") if p.is_file()):
        rel = str(f.relative_to(dirpath)).replace("\\", "/")
        h.update(rel.encode())
        h.update(b"\0")
        h.update(f.read_bytes())
    return h.hexdigest()


def _payload_tree_manifest(payload: Path) -> str:
    if payload.is_dir():
        return _tree_manifest(payload)
    h = hashlib.sha256()
    h.update(payload.name.encode())
    h.update(b"\0")
    h.update(payload.read_bytes())
    return h.hexdigest()

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def _content_digest(payload: Path | None) -> str:
    """The digest `_store_for` would file a payload under — without filing it."""
    if payload is None:
        return ""
    return _sha256(_bundle_bytes(payload) if payload.is_dir() else payload.read_bytes())

def _blob_path(root: Path, digest: str) -> Path:
    return root / WAREHOUSE / digest[:2] / digest


def _git_top(path: Path) -> Path | None:
    cur = path if path.is_dir() else path.parent
    chain: list[str] = []
    while True:
        key = str(cur)
        if key in _GIT_TOP:
            top = _GIT_TOP[key]
            for c in chain:
                _GIT_TOP[c] = top
            return Path(top) if top else None
        chain.append(key)
        if (cur / ".git").exists():
            for c in chain:
                _GIT_TOP[c] = str(cur)
            return cur
        if cur.parent == cur:
            for c in chain:
                _GIT_TOP[c] = None
            return None
        cur = cur.parent


_GIT_TOP: dict[str, str | None] = {}
_GIT_META: dict[str, dict | None] = {}


def _git_meta(top: Path) -> dict | None:
    k = str(top)
    if k in _GIT_META:
        return _GIT_META[k]
    try:
        commit = subprocess.check_output(
            ["git", "-C", k, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=8, text=True).strip()
        url = subprocess.check_output(
            ["git", "-C", k, "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, timeout=8, text=True).strip()
        if not commit or not url:
            _GIT_META[k] = None
            return None
        names = set(subprocess.check_output(
            ["git", "-C", k, "ls-tree", "-r", "--name-only", "-z", commit],
            stderr=subprocess.DEVNULL, timeout=60).decode().split("\0"))
        names.discard("")
        dirty: set[str] = set()
        porc = subprocess.check_output(
            ["git", "-C", k, "status", "--porcelain", "-z"],
            stderr=subprocess.DEVNULL, timeout=30)
        for part in porc.decode().split("\0"):
            if len(part) > 3:
                dirty.add(part[3:])
        meta = {"url": url, "commit": commit, "names": names, "dirty": dirty}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        meta = None
    _GIT_META[k] = meta
    return meta


def _git_recipe_for(payload: Path, asset: dict) -> dict | None:
    """Return a recipe only for a clean path at an immutable HTTPS origin."""
    if "tesslio/cli" in str(payload).replace("\\", "/"):
        return None
    top = _git_top(payload)
    if top is None:
        return None
    meta = _git_meta(top)
    if (not meta or not _HTTPS_GIT.fullmatch(meta["url"])
            or not _SHA40.fullmatch(meta["commit"])):
        return None
    try:
        rel = str(payload.resolve().relative_to(top.resolve())).replace("\\", "/")
    except ValueError:
        return None
    names, dirty = meta["names"], meta["dirty"]
    snapshot_sha = asset.get("sha") or ""
    kind = asset.get("kind") or ""
    if payload.is_file():
        if rel not in names or rel in dirty:
            return None
        if snapshot_sha and Repo._sha_file(payload) != snapshot_sha:
            return None
        recipe = {
            "status": "recipe",
            "type": "git",
            "kind": kind,
            "url": meta["url"],
            "commit": meta["commit"],
            "path": rel,
            "payload_scope": "file",
            "snapshot_sha": snapshot_sha,
            "catalog_sha": snapshot_sha,
            "n_files": 1,
            "tree_manifest": _payload_tree_manifest(payload),
        }
        return recipe if _recipe_descriptor_error(recipe) is None else None
    if not payload.is_dir():
        return None
    prefix = rel.rstrip("/") + "/"
    members = [n for n in names if n == rel or n.startswith(prefix)]
    if not members:
        return None
    if any(m in dirty for m in members):
        return None
    disk = sorted(str(f.relative_to(payload)).replace("\\", "/")
                  for f in payload.rglob("*") if f.is_file())
    git_files = sorted(n[len(prefix):] for n in members if n.startswith(prefix))
    if disk != git_files:
        return None
    desc = DIR_DESCRIPTOR.get(kind)
    if not desc:
        return None
    fp = payload / desc
    if not fp.is_file():
        return None
    if prefix + desc not in names:
        return None
    recipe = {
        "status": "recipe",
        "type": "git",
        "kind": kind,
        "url": meta["url"],
        "commit": meta["commit"],
        "path": rel,
        "payload_scope": "tree",
        "n_files": len(git_files),
        "tree_manifest": _payload_tree_manifest(payload),
        "catalog_sha": Repo._sha_file(fp),
        "snapshot_sha": snapshot_sha,
    }
    return recipe if _recipe_descriptor_error(recipe) is None else None


def _store_for(root: Path, asset: dict, licence: dict | None = None) -> dict:
    """Canonical → blob. External → verified git recipe or unresolved. Never invent recipes.

    `licence` maps ledger-cleared `blob_sha256` → `catalog_sha`. Archival IS the write, so
    an asset whose content is not cleared for that content is never filed — the row falls
    back to `unresolved` and nothing lands in the warehouse. `None` means the caller has
    already applied its own licence check (restock).
    """
    catalog_sha = asset.get("sha") or ""
    source = asset.get("source") or ""
    kind = asset.get("kind") or ""
    payload = _payload_path(asset)
    if source == "canonical" and payload is not None:
        if payload.is_dir():
            data = _bundle_bytes(payload)
            scope = "bundle"
        else:
            data = payload.read_bytes()
            scope = "file"
        digest = _sha256(data)
        if licence is not None and licence.get(digest) != catalog_sha:
            return {
                "status": "unresolved",
                "payload_scope": scope,
                "catalog_sha": catalog_sha,
                "reason": "licence ledger does not clear this content for archiving",
            }
        dest = _blob_path(root, digest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_bytes(data)
        return {
            "status": "blob",
            "payload_scope": scope,
            "catalog_sha": catalog_sha,
            "blob_sha256": digest,
            "blob": str(dest.relative_to(root)),
        }
    if payload is not None:
        rec = _git_recipe_for(payload, asset)
        if rec:
            return rec
    if kind == "skill" and source != "canonical":
        return {
            "status": "unresolved_bundle",
            "payload_scope": "descriptor_only",
            "catalog_sha": catalog_sha,
            "reason": "external skill not in a clean origin-backed git tree",
        }
    return {
        "status": "unresolved",
        "payload_scope": "unknown",
        "catalog_sha": catalog_sha,
        "reason": "no license-cleared blob and no verified immutable retrieval",
    }


def dump_universe(repo: Repo) -> dict:
    doc = repo.load_index()
    assets = doc.get("assets") or []
    rows = []
    counts: dict[str, int] = {}
    root = Path(repo.root)
    licence, licence_problems = _licence_map(root)
    for a in assets:
        kind, aid = a.get("kind") or "", a.get("id") or ""
        store = _store_for(root, a, licence=licence)
        counts[store["status"]] = counts.get(store["status"], 0) + 1
        rows.append({
            "kind": kind,
            "id": aid,
            "source": a.get("source"),
            "path": a.get("path"),
            "sha": a.get("sha"),
            "store": store,
        })
    dest = root / UNIVERSE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))
    restorable = counts.get("blob", 0)
    unresolved = counts.get("unresolved", 0) + counts.get("unresolved_bundle", 0)
    return {
        "n": len(rows),
        "path": str(dest),
        "store_counts": counts,
        "licence_problems": licence_problems,
        "restorable": restorable,
        "recipe_rows": counts.get("recipe", 0),
        "v5_all_stores_restorable": False,
        "note": "recipe rows are advertised with bounded evidence; run check --stores to fetch and verify",
        "ok": True,
        "exit_code": 0,
    }


def _load_jsonl(path: Path) -> list:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _licence_map(root: Path) -> tuple[dict, list[str]]:
    """`blob_sha256 -> catalog_sha` that the ledger clears for local archive.

    Keyed by content, never by `(kind,id)`: an older 'allowed' entry must not bless a
    different blob filed under the same asset id, so an entry only counts when the
    stored blob's sha256 AND its catalog_sha line up with the ledger row. Malformed,
    duplicated or unreadable entries deny (fail-closed) and are named in the second
    return value. Ledger absent → nothing is cleared.
    """
    path = root / BLOB_LEDGER
    if not path.is_file():
        return {}, ["licence ledger absent — run scripts/blob_license_ledger.py"]
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        return {}, [f"licence ledger unreadable: {type(e).__name__}"]
    if not isinstance(doc, dict):
        return {}, ["licence ledger document is not an object"]
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return {}, ["licence ledger entries is not a list"]

    allowed: dict[str, str] = {}
    problems: list[str] = []
    seen: set[str] = set()
    conflicted: set[str] = set()
    invalid_shape = False
    for entry in entries:
        if not isinstance(entry, dict):
            problems.append("entry is not an object")
            invalid_shape = True
            continue
        digest = entry.get("blob_sha256") or ""
        catalog = entry.get("catalog_sha") or ""
        if (not isinstance(digest, str) or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)):
            problems.append(
                f"malformed blob_sha256 for "
                f"{_key(entry.get('kind') or '?', entry.get('id') or '?')}")
            continue
        if digest in seen:
            conflicted.add(digest)
            allowed.pop(digest, None)
            problems.append(f"duplicate blob_sha256 {digest[:12]}")
        else:
            seen.add(digest)
        if (not isinstance(catalog, str) or len(catalog) != 12
                or any(c not in "0123456789abcdef" for c in catalog)):
            problems.append(f"malformed catalog_sha for {digest[:12]}")
            continue
        if entry.get("archive_allowed") is not True:
            if ("archive_allowed" in entry
                    and not isinstance(entry["archive_allowed"], bool)):
                problems.append(
                    f"non-boolean archive_allowed for "
                    f"{_key(entry.get('kind') or '?', entry.get('id') or '?')}")
            continue
        if digest not in conflicted:
            allowed[digest] = catalog
    return ({}, problems) if invalid_shape else (allowed, problems)


def _universe_store_valid(root: Path, row: dict, licence: dict | None = None) -> bool:
    store = row.get("store") or {}
    if store.get("status") != "blob":
        return False
    if licence is not None and licence.get(store.get("blob_sha256") or "") != row.get("sha"):
        return False                      # restores, but not licensed as THIS content
    rec = {
        "kind": row.get("kind"),
        "id": row.get("id"),
        "snapshot_sha": row.get("sha"),
        "store": store,
    }
    return _receipt_restores(root, rec, row)


def _receipt_restores(root: Path, rec: dict, uni_row: dict | None) -> bool:
    """Receipt authorizes disappearance only if it restores THIS snapshot row."""
    if not uni_row or not rec.get("kind") or not rec.get("id"):
        return False
    if rec.get("snapshot_sha") != uni_row.get("sha"):
        return False
    store = rec.get("store") or {}
    if store.get("status") != "blob":
        return False
    digest = store.get("blob_sha256") or ""
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return False
    src = _blob_path(root, digest)
    if not src.is_file() or _sha256(src.read_bytes()) != digest:
        return False
    base = root / ".codex-tmp"
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(base), prefix="receipt-") as td:
        tmp = Path(td)
        restored = restore_blob(Repo(root), digest, tmp)
        if not restored.get("ok"):
            return False
        if restored.get("kind") == "bundle":
            got = Repo._sha_dir(tmp)
        else:
            payload = tmp / "payload"
            if not payload.is_file():
                return False
            got = Repo._sha_file(payload)
        return got == uni_row.get("sha")


def _missing_evidence(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], int] = {}
    for row in rows:
        store = row.get("store") or {}
        status = store.get("status") or "missing_store"
        if status not in {"unresolved", "unresolved_bundle", "missing_store"}:
            continue
        key = (status, store.get("payload_scope") or "unknown",
               store.get("reason") or "store metadata absent")
        groups[key] = groups.get(key, 0) + 1
    required = [
        "a license-cleared content-addressed blob that restores the snapshot SHA12",
        "an HTTPS git URL, 40-hex commit, safe path, SHA12 descriptor, "
        "snapshot SHA12, n_files, and tree_manifest whose fetched archive verifies",
    ]
    return [
        {
            "status": status,
            "payload_scope": scope,
            "reason": reason,
            "count": count,
            "required_evidence": required,
        }
        for (status, scope, reason), count in sorted(groups.items())
    ]


def _verify_recipe_rows(rows: list[dict]) -> dict:
    groups: dict[tuple[str, str], list[dict]] = {}
    failures = []
    for row in rows:
        store = row.get("store") or {}
        error = _recipe_descriptor_error(store)
        if error is None and store.get("kind") != row.get("kind"):
            error = "recipe kind does not match snapshot kind"
        if error is None and store.get("snapshot_sha") != row.get("sha"):
            error = "recipe snapshot_sha does not match snapshot sha"
        if error:
            failures.append({"key": _key(row.get("kind") or "?",
                                         row.get("id") or "?"),
                             "error": error})
            continue
        groups.setdefault((store["url"], store["commit"]), []).append(row)

    valid = set()
    fetches = 0
    with tempfile.TemporaryDirectory(prefix="skillos-store-check-") as td:
        base = Path(td)
        for group_no, ((url, commit), members) in enumerate(groups.items()):
            work = base / f"source-{group_no}"
            fetches += 1
            fetched = _fetch_git_recipe(url, commit, work)
            if not fetched.get("ok"):
                failures.append({
                    "url": url,
                    "commit": commit,
                    "keys": [_key(row["kind"], row["id"]) for row in members],
                    "error": fetched.get("error") or "fetch failed",
                    "stderr": fetched.get("stderr"),
                })
                continue
            for row_no, row in enumerate(members):
                dest = base / f"restore-{group_no}-{row_no}"
                restored = _restore_recipe_from_checkout(
                    row["store"], dest, work)
                key = _key(row["kind"], row["id"])
                if restored.get("ok"):
                    valid.add(key)
                else:
                    failures.append({
                        "key": key,
                        "url": url,
                        "commit": commit,
                        "path": row["store"].get("path"),
                        "error": restored.get("error") or "restore failed",
                        "got": restored.get("got"),
                        "expect": restored.get("expect"),
                    })
    return {
        "valid_keys": valid,
        "recipe_group_count": len(groups),
        "recipe_fetch_count": fetches,
        "recipe_verified_count": len(valid),
        "recipe_failures": failures,
    }


def restock_stores(repo: Repo) -> dict:
    """Attach proven stores to the frozen snapshot without touching identity.

    Only rows with no store evidence (`unresolved`, `unresolved_bundle`, `missing_store`)
    are candidates. Already-pinned `recipe` and warehouse `blob` rows are historical
    evidence and are never re-derived — a recipe that has since gone unfetchable stays
    pinned exactly as recorded and is reported red by `check --stores`, not quietly
    re-pointed at today's tree. `(kind,id,sha)` is never rewritten; a `store` is written
    only when it is proven RIGHT NOW to restore the snapshot SHA12 (blob restored from the
    warehouse, or recipe fetched over HTTPS and verified).
    """
    root = Path(repo.root)
    dest = root / UNIVERSE
    if not dest.is_file():
        return {"ok": False, "error": "universe.jsonl missing — run skillos dump",
                "exit_code": 1}
    try:
        original = dest.read_bytes()
        physical_lines = original.splitlines(keepends=True)
        row_lines = []
        uni = []
        for line_no, line in enumerate(physical_lines):
            if not line.strip():
                continue
            row = json.loads(line.decode("utf-8"))
            if not isinstance(row, dict):
                raise ValueError(f"universe row {len(uni) + 1} is not an object")
            row_lines.append(line_no)
            uni.append(row)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {"ok": False, "error": f"universe.jsonl unreadable: {exc}",
                "exit_code": 1}
    if not uni:
        return {"ok": False, "error": "universe.jsonl missing — run skillos dump",
                "exit_code": 1}

    def frozen_bytes(rows: list[dict], identity_only: bool = False) -> bytes:
        if identity_only:
            values = ([row.get("kind"), row.get("id"), row.get("sha")]
                      for row in rows)
        else:
            values = ({key: value for key, value in row.items() if key != "store"}
                      for row in rows)
        return b"".join(
            json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8") + b"\n"
            for value in values
        )

    identity_before = frozen_bytes(uni, identity_only=True)
    rows_before = frozen_bytes(uni)
    OPEN = {"unresolved", "unresolved_bundle", "missing_store", ""}
    live = {_key(a.get("kind") or "", a.get("id") or ""): a
            for a in (repo.load_index().get("assets") or [])}
    licence, licence_problems = _licence_map(root)
    pending: list[tuple[int, dict]] = []
    changed: set[int] = set()
    blobbed = 0
    licence_skipped = 0
    for i, row in enumerate(uni):
        if ((row.get("store") or {}).get("status") or "") not in OPEN:
            continue                          # pinned receipts are immutable
        key = _key(row.get("kind") or "", row.get("id") or "")
        asset = live.get(key)
        if asset is None or (asset.get("sha") or "") != row.get("sha"):
            continue                          # identity must match the frozen snapshot
        derived = _store_for(root, asset, licence=licence)
        if (asset.get("source") == "canonical"
                and "licence ledger" in (derived.get("reason") or "")):
            licence_skipped += 1               # declined THIS content, on licence
        if derived.get("status") == "blob":
            if _universe_store_valid(root, {**row, "store": derived}, licence=licence):
                row["store"] = derived
                changed.add(i)
                blobbed += 1
        elif derived.get("status") == "recipe":
            pending.append((i, derived))

    recipe_verified = 0
    failures: list[dict] = []
    if pending:
        probe = [{**uni[i], "store": store} for i, store in pending]
        try:
            report = _verify_recipe_rows(probe)
        except Exception as exc:
            return {
                "ok": False,
                "n": len(uni),
                "error": f"recipe verification failed; universe unchanged: {exc}",
                "identity_unchanged": True,
                "exit_code": 1,
            }
        valid = report.get("valid_keys") or set()
        failures = list(report.get("recipe_failures") or [])
        fetch_failures = [failure for failure in failures if "keys" in failure]
        if fetch_failures:
            return {
                "ok": False,
                "n": len(uni),
                "error": "recipe fetch failed; universe unchanged",
                "recipe_refusals": fetch_failures[:20],
                "identity_unchanged": True,
                "exit_code": 1,
            }
        for (i, store), row in zip(pending, probe):
            if _key(row.get("kind") or "", row.get("id") or "") in valid:
                uni[i]["store"] = store
                changed.add(i)
                recipe_verified += 1

    identity_after = frozen_bytes(uni, identity_only=True)
    rows_after = frozen_bytes(uni)
    if (len(uni) != len(row_lines) or identity_after != identity_before
            or rows_after != rows_before):
        return {
            "ok": False,
            "n": len(uni),
            "error": "restock invariant failed; universe unchanged",
            "identity_unchanged": identity_after == identity_before,
            "exit_code": 1,
        }

    output_lines = list(physical_lines)
    for row_no in changed:
        original_line = output_lines[row_lines[row_no]]
        if original_line.endswith(b"\r\n"):
            ending = b"\r\n"
        elif original_line.endswith(b"\n"):
            ending = b"\n"
        elif original_line.endswith(b"\r"):
            ending = b"\r"
        else:
            ending = b""
        output_lines[row_lines[row_no]] = (
            json.dumps(uni[row_no], separators=(",", ":")).encode("ascii") + ending
        )
    output = b"".join(output_lines)
    if output != original:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="wb", dir=dest.parent, prefix=f".{dest.name}.",
                    suffix=".tmp", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(output)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.chmod(tmp_path, dest.stat().st_mode & 0o777)
            os.replace(tmp_path, dest)
        except OSError as exc:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
            return {
                "ok": False,
                "n": len(uni),
                "error": f"atomic universe write failed: {exc}",
                "identity_unchanged": True,
                "exit_code": 1,
            }

    counts: dict[str, int] = {}
    for row in uni:
        status = (row.get("store") or {}).get("status") or "missing_store"
        counts[status] = counts.get(status, 0) + 1
    return {
        "ok": True,
        "n": len(uni),
        "blobbed": blobbed,
        "licence_skipped": licence_skipped,
        "licence_problems": licence_problems,
        "recipe_verified": recipe_verified,
        "recipe_refused": len(pending) - recipe_verified,
        "recipe_refusals": failures[:20],
        "store_counts": counts,
        "identity_unchanged": True,
        "exit_code": 0,
    }


def check_universe(repo: Repo, plant_drop: str | None = None,
                   stores: bool = False) -> dict:
    root = Path(repo.root)
    uni = _load_jsonl(root / UNIVERSE)
    if not uni:
        return {"ok": False, "error": "universe.jsonl missing — run skillos dump",
                "exit_code": 1}
    uni_by = {}
    dupes = []
    for r in uni:
        k = _key(r["kind"], r["id"])
        if k in uni_by:
            dupes.append(k)
        else:
            uni_by[k] = r
    if dupes:
        return {"ok": False, "duplicate_universe_keys": sorted(set(dupes)),
                "exit_code": 1}
    verified_receipts = set()
    bad_receipts = []
    seen_receipts = set()
    for rec in _load_jsonl(root / RECEIPTS):
        k = _key(rec.get("kind") or "?", rec.get("id") or "?")
        if k in seen_receipts:
            return {"ok": False, "duplicate_receipt_keys": [k], "exit_code": 1}
        seen_receipts.add(k)
        if _receipt_restores(root, rec, uni_by.get(k)):
            verified_receipts.add(k)
        else:
            bad_receipts.append(k)
    live_assets = {_key(a.get("kind") or "", a.get("id") or ""): a
                   for a in (repo.load_index().get("assets") or [])}
    live = set(live_assets)
    if plant_drop:
        live.discard(plant_drop)
    missing = []
    for row in uni:
        k = _key(row["kind"], row["id"])
        if k not in live and k not in verified_receipts:
            missing.append(k)
    store_counts: dict[str, int] = {}
    valid = 0
    recipes = []
    licence, licence_problems = _licence_map(root)
    licence_denied = []
    unrestorable_blobs = []
    for row in uni:
        st = (row.get("store") or {}).get("status") or "missing_store"
        store_counts[st] = store_counts.get(st, 0) + 1
        if st == "recipe":
            recipes.append(row)
        elif _universe_store_valid(root, row, licence=licence):
            valid += 1
        elif st == "blob":
            key = _key(row.get("kind") or "", row.get("id") or "")
            store = row.get("store") or {}
            # Two different faults: the ledger refuses these bytes, versus bytes that are
            # cleared but absent/corrupt in the warehouse. Editing the ledger fixes the first
            # and must not be the response to the second.
            if licence.get(store.get("blob_sha256") or "") != row.get("sha"):
                licence_denied.append(key)
            else:
                unrestorable_blobs.append(key)
    recipe_report = {
        "recipe_group_count": 0,
        "recipe_fetch_count": 0,
        "recipe_verified_count": 0,
        "recipe_failures": [],
    }
    if stores and recipes:
        recipe_report = _verify_recipe_rows(recipes)
        valid += len(recipe_report.pop("valid_keys"))
    unresolved = (store_counts.get("unresolved", 0)
                  + store_counts.get("unresolved_bundle", 0)
                  + store_counts.get("missing_store", 0))
    ok_keys = not missing
    ok_stores = bool(uni) and valid == len(uni)
    if stores:
        exit_code = 0 if ok_stores else 1
        ok = ok_stores
    else:
        exit_code = 0 if ok_keys else 1
        ok = ok_keys
    return {
        "ok": ok,
        "ok_keys": ok_keys,
        "ok_stores": ok_stores,
        "n": len(uni),
        "missing_without_receipt": missing,
        "bad_receipts": bad_receipts,
        "store_counts": store_counts,
        "licence_denied": licence_denied,
        "unrestorable_blobs": unrestorable_blobs,
        "licence_problems": licence_problems,
        "unresolved": unresolved,
        "missing_evidence": _missing_evidence(uni),
        "valid_store_count": valid,
        "invalid_store_count": len(uni) - valid,
        "all_stores_restorable": ok_stores,
        "plant_drop": plant_drop,
        **recipe_report,
        "exit_code": exit_code,
    }


def restore_blob(repo: Repo, digest: str, dest: Path) -> dict:
    src = _blob_path(Path(repo.root), digest)
    if not src.is_file():
        return {"ok": False, "error": f"no blob {digest}"}
    data = src.read_bytes()
    got = _sha256(data)
    if got != digest:
        return {"ok": False, "error": "blob sha mismatch", "got": got}
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    bio = io.BytesIO(data)
    try:
        tar = tarfile.open(fileobj=bio, mode="r:")
    except tarfile.TarError:
        (dest / "payload").write_bytes(data)
        return {"ok": True, "sha256": got, "kind": "file", "dest": str(dest)}
    with tar:
        for m in tar.getmembers():
            if m.issym() or m.islnk() or m.isdev() or m.isfifo():
                return {"ok": False, "error": f"rejected tar member type {m.name}"}
            name = m.name.replace("\\", "/")
            if name.startswith("/") or name.startswith("../") or "/../" in f"/{name}/":
                return {"ok": False, "error": f"rejected tar path {m.name}"}
            target = (dest / name).resolve()
            if dest != target and dest not in target.parents:
                return {"ok": False, "error": f"tar path escapes dest: {m.name}"}
            if m.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not m.isfile():
                return {"ok": False, "error": f"rejected tar member {m.name}"}
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = tar.extractfile(m)
            if extracted is None:
                return {"ok": False, "error": f"empty tar member {m.name}"}
            target.write_bytes(extracted.read())
    return {"ok": True, "sha256": got, "kind": "bundle", "dest": str(dest)}


def _recipe_descriptor_error(store: dict) -> str | None:
    if store.get("status") != "recipe" or store.get("type") != "git":
        return "not a git recipe"
    url = store.get("url")
    if not isinstance(url, str) or not _HTTPS_GIT.fullmatch(url):
        return "recipe url must be a non-empty HTTPS URL"
    commit = store.get("commit")
    if not isinstance(commit, str) or not _SHA40.fullmatch(commit):
        return "recipe commit must be 40 lowercase hex characters"
    rel = store.get("path")
    if (not isinstance(rel, str) or not rel or "\\" in rel
            or rel.startswith("/")
            or any(p in {"", ".", ".."} for p in rel.split("/"))):
        return "recipe path must be a safe relative POSIX path"
    if any(ord(ch) < 32 for ch in rel):
        return "recipe path contains a control character"
    scope = store.get("payload_scope")
    if scope not in {"file", "tree"}:
        return "recipe payload_scope must be file or tree"
    if scope == "tree" and not DIR_DESCRIPTOR.get(store.get("kind") or ""):
        return "tree recipe kind has no descriptor"
    catalog_sha = store.get("catalog_sha")
    if not isinstance(catalog_sha, str) or not _SHA12.fullmatch(catalog_sha):
        return "recipe catalog_sha must be 12 lowercase hex characters"
    snapshot_sha = store.get("snapshot_sha")
    if not isinstance(snapshot_sha, str) or not _SHA12.fullmatch(snapshot_sha):
        return "recipe snapshot_sha must be 12 lowercase hex characters"
    n_files = store.get("n_files")
    if (not isinstance(n_files, int) or isinstance(n_files, bool)
            or n_files < 1 or (scope == "file" and n_files != 1)):
        return "recipe n_files must be a positive integer (one for file scope)"
    manifest = store.get("tree_manifest")
    if not isinstance(manifest, str) or not _SHA256.fullmatch(manifest):
        return "recipe tree_manifest must be 64 lowercase hex characters"
    return None


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = "/usr/bin/true"
    env["GIT_ALLOW_PROTOCOL"] = "https"
    return env


def _fetch_git_recipe(url: str, commit: str, work: Path) -> dict:
    env = _git_env()
    try:
        subprocess.run(["git", "init", "--quiet", str(work)], check=True,
                       capture_output=True, timeout=15, env=env)
        subprocess.run(["git", "-C", str(work), "remote", "add", "origin", url],
                       check=True, capture_output=True, timeout=15, env=env)
        fetched = subprocess.run(
            ["git", "-C", str(work), "fetch", "--quiet", "--depth", "1",
             "origin", commit],
            capture_output=True, timeout=60, env=env)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        return {"ok": False, "error": str(exc), "exit_code": 1}
    if fetched.returncode != 0:
        return {
            "ok": False,
            "error": "fetch failed",
            "stderr": (fetched.stderr or b"").decode(errors="replace")[-400:],
            "exit_code": 1,
        }
    return {"ok": True, "exit_code": 0}


def _restore_recipe_from_checkout(store: dict, dest: Path, work: Path) -> dict:
    rel = store["path"]
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    try:
        data = subprocess.check_output(
            ["git", "-C", str(work), "archive", store["commit"], "--", rel],
            stderr=subprocess.STDOUT, timeout=30, env=_git_env())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        return {"ok": False, "error": str(exc), "exit_code": 1}
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode="r:")
    except tarfile.TarError:
        return {"ok": False, "error": "git archive was not a tar", "exit_code": 1}
    n_files = 0
    seen = set()
    requested = rel.rstrip("/")
    with tar:
        for member in tar.getmembers():
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                return {"ok": False,
                        "error": f"rejected tar member type {member.name}",
                        "exit_code": 1}
            name = member.name.replace("\\", "/").rstrip("/")
            if (not name or name in seen or name.startswith("/")
                    or name.startswith("../") or "/../" in f"/{name}/"):
                return {"ok": False, "error": f"rejected tar path {member.name}",
                        "exit_code": 1}
            seen.add(name)
            inside = name == requested or name.startswith(requested + "/")
            ancestor = member.isdir() and requested.startswith(name + "/")
            if not inside and not ancestor:
                return {"ok": False,
                        "error": f"archive member outside requested path: {member.name}",
                        "exit_code": 1}
            target = (dest / name).resolve()
            if dest != target and dest not in target.parents:
                return {"ok": False,
                        "error": f"tar path escapes dest: {member.name}",
                        "exit_code": 1}
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                return {"ok": False, "error": f"rejected tar member {member.name}",
                        "exit_code": 1}
            target.parent.mkdir(parents=True, exist_ok=True)
            archived = tar.extractfile(member)
            if archived is None:
                return {"ok": False, "error": f"empty tar member {member.name}",
                        "exit_code": 1}
            target.write_bytes(archived.read())
            n_files += 1
    extracted = dest / rel
    if not extracted.exists():
        return {"ok": False, "error": f"missing {rel} after archive", "exit_code": 1}
    scope = store["payload_scope"]
    if ((scope == "file" and not extracted.is_file())
            or (scope == "tree" and not extracted.is_dir())):
        return {"ok": False, "error": "payload scope mismatch", "exit_code": 1}
    if extracted.is_file():
        got = Repo._sha_file(extracted)
    else:
        descriptor = DIR_DESCRIPTOR.get(store.get("kind") or "")
        descriptor_path = extracted / descriptor if descriptor else None
        if descriptor_path is None or not descriptor_path.is_file():
            return {"ok": False, "error": "restored tree descriptor missing",
                    "exit_code": 1}
        got = Repo._sha_file(descriptor_path)
    expect = store["catalog_sha"]
    if got != expect:
        return {"ok": False, "error": "restored sha mismatch", "got": got,
                "expect": expect, "exit_code": 1}
    expect_n = store["n_files"]
    if n_files != expect_n:
        return {"ok": False, "error": "file count mismatch", "got": n_files,
                "expect": expect_n, "exit_code": 1}
    got_manifest = _payload_tree_manifest(extracted)
    expect_manifest = store["tree_manifest"]
    if got_manifest != expect_manifest:
        return {"ok": False, "error": "tree manifest mismatch",
                "got": got_manifest, "expect": expect_manifest, "exit_code": 1}
    got_snapshot = (Repo._sha_file(extracted) if extracted.is_file()
                    else Repo._sha_dir(extracted))
    expect_snapshot = store["snapshot_sha"]
    if got_snapshot != expect_snapshot:
        return {"ok": False, "error": "snapshot sha mismatch",
                "got": got_snapshot, "expect": expect_snapshot, "exit_code": 1}
    return {
        "ok": True,
        "kind": "recipe",
        "dest": str(dest),
        "sha": got,
        "snapshot_sha": got_snapshot,
        "n_files": n_files,
        "tree_manifest": got_manifest,
        "exit_code": 0,
    }

def restore_recipe(store: dict, dest: Path) -> dict:
    """Fetch and verify one immutable recipe; batch checks share this verifier."""
    error = _recipe_descriptor_error(store)
    if error:
        return {"ok": False, "error": error, "exit_code": 1}
    with tempfile.TemporaryDirectory(prefix="skillos-git-") as td:
        work = Path(td) / "source"
        fetched = _fetch_git_recipe(store["url"], store["commit"], work)
        if not fetched.get("ok"):
            return fetched
        return _restore_recipe_from_checkout(store, dest, work)

def door_ids(repo: Repo) -> list[str]:
    text = (Path(repo.root) / TOP50).read_text()
    return re.findall(r"^\| (J\d+) \|", text, re.M)


def doors_count(repo: Repo) -> dict:
    ids = door_ids(repo)
    expect = [f"J{i:02d}" for i in range(1, 51)]
    return {"count": len(ids), "ok": ids == expect, "ids": ids}


def write_canonical_witnesses(repo: Repo) -> dict:
    root = Path(repo.root)
    d = root / WITNESS_DIR
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for a in repo.load_index().get("assets") or []:
        if a.get("source") != "canonical" or a.get("kind") != "skill":
            continue
        aid = a["id"]
        (d / f"{aid}.json").write_text(json.dumps({
            "kind": "skill",
            "id": aid,
            "check": "rig-capabilities test",
            "edge": "executable-candidate",
        }, indent=1) + "\n")
        n += 1
    return {"wrote": n, "dir": str(d)}


def witness_strict(repo: Repo, plant_remove: str | None = None) -> dict:
    from .done_tests import run_asset
    root = Path(repo.root)
    d = root / WITNESS_DIR
    wanted = [a["id"] for a in repo.load_index().get("assets") or []
              if a.get("source") == "canonical" and a.get("kind") == "skill"]
    missing_fx = [i for i in wanted if not (d / f"{i}.json").is_file()]
    if plant_remove:
        missing_fx.append(plant_remove)
    # Missing fixtures must not mask malformed ones: report both, stay red.
    present = [i for i in wanted if (d / f"{i}.json").is_file()]
    fails = []
    ran = []
    bad_fx = []
    for aid in present:
        path = d / f"{aid}.json"
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            bad_fx.append(aid)
            continue
        if (not isinstance(doc, dict) or doc.get("kind") != "skill"
                or doc.get("id") != aid
                or doc.get("check") != "rig-capabilities test"):
            bad_fx.append(aid)
            continue
        res = run_asset(repo, doc["id"])
        ran.append({"id": doc["id"], "pass": res.get("pass"),
                    "unrunnable": res.get("unrunnable")})
        if not res.get("pass"):
            fails.append(aid)
    if bad_fx or fails or missing_fx:
        return {"ok": False, "bad_fixtures": bad_fx, "fails": fails,
                "missing_fixtures": missing_fx, "ran": len(ran), "exit_code": 1}
    return {
        "ok": True,
        "ran": len(ran),
        "fails": [],
        "missing_fixtures": [],
        "unrunnable_any": sum(1 for r in ran if r.get("unrunnable")),
        "exit_code": 0,
    }



def orphan_replay(repo: Repo, corpus: Path, plant_leak: bool = False) -> dict:
    files = sorted(corpus.glob("*.json")) if corpus.is_dir() else (
        [corpus] if corpus.is_file() else [])
    if not files:
        return {"ok": False, "error": "empty corpus", "exit_code": 1}
    leaks = []
    results = []
    for f in files:
        doc = json.loads(f.read_text())
        intent = doc.get("intent") or ""
        hidden = (doc.get("hidden_baseline") or {}).get("id") or ""
        if plant_leak:
            intent = intent + " " + hidden
        if hidden and hidden in intent:
            leaks.append({"file": str(f), "id": hidden})
            continue
        hid = doc.get("hidden_baseline") or {}
        if hid.get("kind") == "skill" and hid.get("id"):
            from .done_tests import run_asset
            res = run_asset(repo, hid["id"])
            results.append({"id": hid["id"], "pass": res.get("pass")})
            if not res.get("pass"):
                return {"ok": False, "fails": results, "exit_code": 1}
    if leaks:
        return {"ok": False, "leaks": leaks, "exit_code": 1}
    return {"ok": True, "ran": len(results), "exit_code": 0}

def provenance(repo: Repo, deny: str = "tesslio/cli") -> dict:
    root = Path(repo.root)
    hits = []
    skip = {".git", "__pycache__", ".venvs", ".index.json"}
    for p in root.rglob("*"):
        if any(part in skip for part in p.parts):
            continue
        rel = str(p.relative_to(root))
        if deny in rel and p.suffix.lower() in {".go", ".rs", ".ts", ".js", ".c", ".cpp"}:
            hits.append(rel)
    return {"ok": not hits, "deny": deny, "hits": hits, "exit_code": 0 if not hits else 1}


def dispatch(repo: Repo, cmd: str, **kw) -> dict:
    if cmd == "dump":
        return dump_universe(repo)
    if cmd == "check":
        return check_universe(repo, plant_drop=kw.get("plant_drop"),
                              stores=bool(kw.get("stores")))
    if cmd == "restock":
        return restock_stores(repo)
    if cmd == "restore":
        digest = kw.get("sha") or ""
        root = Path(repo.root).resolve()
        tmp_root = (root / ".codex-tmp").resolve()
        default = tmp_root / "skillos-restore"
        if kw.get("dest"):
            dest = Path(kw["dest"]).resolve()
            if dest.exists():
                return {"ok": False, "error": "dest exists", "exit_code": 1}
        else:
            dest = default
            if dest.exists():
                shutil.rmtree(dest)
        return restore_blob(repo, digest, dest)
    if cmd == "doors":
        return doors_count(repo)
    if cmd == "witness-write":
        return write_canonical_witnesses(repo)
    if cmd == "witness":
        return witness_strict(repo, plant_remove=kw.get("plant_remove"))
    if cmd == "orphan-replay":
        corpus = Path(kw["corpus"]) if kw.get("corpus") else Path(repo.root) / ORPHAN_DIR
        if not corpus.is_absolute():
            corpus = Path(repo.root) / corpus
        return orphan_replay(repo, corpus, plant_leak=bool(kw.get("plant_leak")))
    if cmd == "provenance":
        return provenance(repo, deny=kw.get("deny") or "tesslio/cli")
    return {"ok": False, "error": f"unknown cmd {cmd}", "exit_code": 1}
