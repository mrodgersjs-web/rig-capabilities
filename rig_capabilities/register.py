"""V41-P3: the machine-readable capability register (M0-M5 x w_i x A-band).

Prose cannot be scored weekly, so the Build Card corpus becomes one CSV. A row
is a claim, so a row must earn its place: no evidence path, no row; no mesh
edge (`enables_product_classes`), no row; M4+ without a named Verifier, no row
and the owner is flagged. The `booked_qualified_conversations` row is mandatory
and weighted 5 so a perfect infrastructure week with zero calls scores FAIL —
the appointment is the only KPI that matters.

Hermetic (L1): `gate_register` reads ONLY `<repo.root>/capability_register.csv`.
Nothing here reads ~/Downloads, ~/.rig, or any live-state file.
"""
from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import date
from pathlib import Path

REGISTER_STORE = "capability_register.csv"

# Criteria-card field order, verbatim, then the two additive reconciliation cells.
REGISTER_FIELDS: tuple[str, ...] = (
    "id",
    "name",
    "subsystem",
    "studio",
    "type",
    "maturity_M0_5",
    "automation_band",
    "weight_w",
    "evidence_paths",
    "harness_signed",
    "verifier_named",
    "proof_status",
    "target_M_2031",
    "target_band_2031",
    "blocking_deps",
    "enables_product_classes",
    "duplicate_of",
    "contradicts",
    "last_touched",
    "owner",
    "source_document_ids",
    "contradiction_group",
)

SUBSYSTEMS: tuple[str, ...] = (
    "chassis", "powertrain", "transmission", "turbo", "tires", "seatbelts",
    "fuel", "spark", "navigation", "sound", "shocks", "steering", "aero",
    "scrutineering",
)
STUDIOS: tuple[str, ...] = (
    "Design", "App", "GTM", "LinkedIn", "Strategy", "CompanyOSFactory",
)
TYPES: tuple[str, ...] = (
    "workflow", "harness", "doctrine", "tool", "repo", "dataset", "asset",
    "offer",
)
BANDS: tuple[str, ...] = ("A1", "A2", "A3", "A4", "manual")
# target_band_2031 has no `manual`: a 2031 target is always an automation band.
TARGET_BANDS: tuple[str, ...] = ("A1", "A2", "A3", "A4")
PROOF_STATUS: tuple[str, ...] = (
    "none", "golden_run", "proofpacket_sealed", "replay_passing",
)

BOOKED_ID = "booked_qualified_conversations"
BOOKED_WEIGHT = 5
BOOKED_STUDIO = "GTM"
BOOKED_ERROR = "booked_qualified_conversations_missing_or_underweighted"

BOOKINGS_ROOT = "data/fable2031"
BOOKINGS_FILE = "bookings-{week}.json"

LIST_FIELDS: tuple[str, ...] = (
    "evidence_paths", "blocking_deps", "enables_product_classes",
    "contradicts", "source_document_ids",
)
INT_FIELDS: tuple[str, ...] = ("maturity_M0_5", "weight_w", "target_M_2031")
BOOL_FIELDS: tuple[str, ...] = ("harness_signed",)
NULLABLE_FIELDS: tuple[str, ...] = ("verifier_named", "duplicate_of",
                                    "contradiction_group")

_VOCAB = {
    "subsystem": SUBSYSTEMS,
    "studio": STUDIOS,
    "type": TYPES,
    "automation_band": BANDS,
    "proof_status": PROOF_STATUS,
    "target_band_2031": TARGET_BANDS,
}
_RANGE = {"maturity_M0_5": (0, 5), "weight_w": (1, 5), "target_M_2031": (0, 5)}

NULL_TOKENS = ("", "null", "none", "n/a", "-")


class RegisterError(Exception):
    """A register or bookings artifact that cannot be trusted."""


# ------------------------------------------------------------------ coercion

def _repo_root(repo) -> Path:
    """Repo-shaped object, str, or Path. A bare `Path` has a `.root` attribute
    ("/"), so it must be resolved before any `getattr` probe."""
    if isinstance(repo, (str, os.PathLike)):
        return Path(repo)
    root = getattr(repo, "root", None)
    if root is None:
        raise TypeError(f"not a repo: {repo!r:.80}")
    return Path(root)


def _as_str(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def _as_null_str(value) -> str | None:
    s = _as_str(value)
    if s.lower() in NULL_TOKENS:
        return None
    return s


def _as_list(value) -> list[str]:
    """A list cell: compact sorted JSON, or `;`-delimited for hand edits."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [s for s in (_as_str(v) for v in value) if s]
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in NULL_TOKENS:
            return []
        try:
            doc = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return [s for s in (p.strip() for p in text.split(";")) if s]
        if isinstance(doc, list):
            return [s for s in (_as_str(v) for v in doc) if s]
        one = _as_str(doc)
        return [one] if one else []
    one = _as_str(value)
    return [one] if one else []


def _as_int(value) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if float(value).is_integer() else None
    text = _as_str(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _as_bool(value) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    text = _as_str(value).lower()
    if text in ("true", "1", "yes", "y"):
        return True
    if text in ("false", "0", "no", "n"):
        return False
    return None


def _is_iso_date(value) -> bool:
    text = _as_str(value)
    if not text:
        return False
    try:
        date.fromisoformat(text[:10])
    except ValueError:
        return False
    return True


def normalize_row(row: dict) -> dict:
    """One register row with every field present and cell-typed."""
    out: dict = {}
    for field in REGISTER_FIELDS:
        raw = row.get(field) if isinstance(row, dict) else None
        if field in LIST_FIELDS:
            out[field] = _as_list(raw)
        elif field in INT_FIELDS:
            out[field] = _as_int(raw)
        elif field in BOOL_FIELDS:
            out[field] = _as_bool(raw)
        elif field in NULLABLE_FIELDS:
            out[field] = _as_null_str(raw)
        else:
            out[field] = _as_str(raw)
    return out


# ---------------------------------------------------------------- validation

def validate_row(row: dict) -> list[str]:
    """Every reason this row may not count. Empty list = the row is sound.

    Schema only. Path existence is checked by `gate_register`, which is the
    function that knows a repo root.
    """
    if not isinstance(row, dict):
        return ["row_not_mapping"]
    errs: list[str] = []
    rid = _as_str(row.get("id"))
    if not rid:
        errs.append("id_missing")
    if not _as_str(row.get("name")):
        errs.append("name_missing")

    for field, vocab in _VOCAB.items():
        if _as_str(row.get(field)) not in vocab:
            errs.append(f"{field}_unknown")

    for field, (lo, hi) in _RANGE.items():
        n = _as_int(row.get(field))
        if n is None:
            errs.append(f"{field}_not_integer")
        elif not lo <= n <= hi:
            errs.append(f"{field}_out_of_range")

    maturity = _as_int(row.get("maturity_M0_5"))
    if not _as_list(row.get("evidence_paths")):
        errs.append("evidence_paths_empty")
    if not _as_list(row.get("enables_product_classes")):
        errs.append("enables_product_classes_empty")
    if _as_bool(row.get("harness_signed")) is None:
        errs.append("harness_signed_not_boolean")
    # Core law: M4 means an independent Verifier holds termination.
    if maturity is not None and maturity >= 4 and _as_null_str(row.get("verifier_named")) is None:
        errs.append("verifier_named_missing_for_M4plus")
    if not _is_iso_date(row.get("last_touched")):
        errs.append("last_touched_not_iso_date")
    if not _as_str(row.get("owner")):
        errs.append("owner_missing")
    dup = _as_null_str(row.get("duplicate_of"))
    if dup is not None and rid and dup == rid:
        errs.append("duplicate_of_self")
    return errs


def row_errors(rows: list[dict]) -> list[dict]:
    """Rows that fail validation, with their reasons: `[{id, errors}]`."""
    out = []
    for row in rows:
        errs = validate_row(row)
        if errs:
            out.append({"id": _as_str(row.get("id")) or "?", "errors": errs})
    return out


def flagged_owners(rows: list[dict]) -> list[str]:
    """Owners of M4+ rows with no named Verifier — the reject-and-flag law."""
    owners = []
    for row in rows:
        errs = validate_row(row)
        if "verifier_named_missing_for_M4plus" in errs:
            owner = _as_str(row.get("owner")) or "?"
            if owner not in owners:
                owners.append(owner)
    return owners


# --------------------------------------------------------------------- store

def register_path(repo, path=None) -> Path:
    if path is not None:
        return Path(path)
    return _repo_root(repo) / REGISTER_STORE


def _read_rows(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            clean = {k: ("" if v is None else v)
                     for k, v in raw.items() if k is not None}
            out.append(normalize_row(clean))
    return out


def load_register(repo, path=None) -> list[dict]:
    """Rows from the committed store. A missing file is an empty register —
    `gate_register` is what reports it as RED."""
    p = register_path(repo, path)
    if not p.is_file():
        return []
    try:
        return _read_rows(p)
    except (OSError, csv.Error, UnicodeDecodeError):
        return []


def _cell(row: dict, field: str) -> str:
    if field in LIST_FIELDS:
        return json.dumps(sorted(_as_list(row.get(field))),
                          separators=(",", ":"), ensure_ascii=False)
    if field in INT_FIELDS:
        n = _as_int(row.get(field))
        return "" if n is None else str(n)
    if field in BOOL_FIELDS:
        b = _as_bool(row.get(field))
        return "" if b is None else ("true" if b else "false")
    if field in NULLABLE_FIELDS:
        v = _as_null_str(row.get(field))
        return "null" if v is None else v
    return _as_str(row.get(field))


def write_register(repo, rows, path=None) -> Path:
    """Atomic write: tmp in the destination dir, then `os.replace`.

    Sorted by `id`; list cells as compact sorted JSON, so a re-write of
    unchanged rows is byte-for-byte stable.
    """
    dest = register_path(repo, path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: (_as_str(r.get("id")), _as_str(r.get("name"))))
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".register-",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(REGISTER_FIELDS),
                                    lineterminator="\n")
            writer.writeheader()
            for row in ordered:
                writer.writerow({f: _cell(row, f) for f in REGISTER_FIELDS})
        os.replace(tmp, dest)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return dest


# -------------------------------------------------------------- reconciliation

def diff_register(prev, cur) -> dict:
    """Week-over-week register delta, keyed by `id`."""
    def index(rows):
        out = {}
        for row in rows or []:
            rid = _as_str(row.get("id"))
            if rid:
                out[rid] = normalize_row(row)
        return out

    a, b = index(prev), index(cur)
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = []
    unchanged = []
    for rid in sorted(set(a) & set(b)):
        fields = {}
        for field in REGISTER_FIELDS:
            if field == "id":
                continue
            before, after = a[rid].get(field), b[rid].get(field)
            if before != after:
                fields[field] = {"from": _cell(a[rid], field),
                                 "to": _cell(b[rid], field)}
        if fields:
            changed.append({"id": rid, "fields": fields})
        else:
            unchanged.append(rid)
    maturity_moves = []
    for rid in added:
        maturity_moves.append({"id": rid, "from": None,
                               "to": b[rid].get("maturity_M0_5")})
    for entry in changed:
        mv = entry["fields"].get("maturity_M0_5")
        if mv:
            maturity_moves.append({"id": rid_of(entry), "from": _as_int(mv["from"]),
                                   "to": _as_int(mv["to"])})
    for rid in removed:
        maturity_moves.append({"id": rid, "from": a[rid].get("maturity_M0_5"),
                               "to": None})
    return {"added": added, "removed": removed, "changed": changed,
            "unchanged": unchanged, "maturity_moves": maturity_moves,
            "counts": {"added": len(added), "removed": len(removed),
                       "changed": len(changed), "unchanged": len(unchanged)}}


def rid_of(entry: dict) -> str:
    return _as_str(entry.get("id"))


def require_booked_row(rows) -> None:
    """The mandatory revenue row — weighted 5, studio GTM, no exceptions.

    A generic `booked_call` row, or the right row at weight 3, does not count:
    the week must be able to fail.
    """
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if (_as_str(row.get("id")) == BOOKED_ID
                and _as_int(row.get("weight_w")) == BOOKED_WEIGHT
                and _as_str(row.get("studio")) == BOOKED_STUDIO):
            return
    raise RegisterError(BOOKED_ERROR)


# ------------------------------------------------------------- bookings seam

def bookings_path(repo, week: str) -> Path:
    return _repo_root(repo) / BOOKINGS_ROOT / BOOKINGS_FILE.format(week=week)


def _candidate_roots(path: Path, root=None) -> list[Path]:
    bases: list[Path] = []
    if root is not None:
        bases.append(Path(root))
    else:
        for parent in (path.resolve() if path.exists() else path.absolute()).parents:
            if (parent / "capability_register.csv").is_file() or \
               (parent / "rig_capabilities").is_dir() or (parent / ".git").exists():
                bases.append(parent)
                break
    cwd = Path.cwd()
    if cwd not in bases:
        bases.append(cwd)
    bases.append(path.parent)
    return bases


def _resolve_evidence(value, bases: list[Path]) -> Path | None:
    """A booking counts only against a file that really exists."""
    text = _as_str(value)
    if not text:
        return None
    q = Path(text).expanduser()
    if q.is_absolute() and q.is_file():
        return q
    for base in bases:
        cand = base / q
        try:
            if cand.is_file():
                return cand
        except OSError:
            continue
    return None


def load_bookings(path, root=None) -> dict:
    """`{week, count, records}` from `data/fable2031/bookings-<ISO-week>.json`.

    `records` holds only qualified records — those whose
    `qualification_evidence_path` resolves to an existing file — so
    `count == len(records)` always. `invalid` names why the rest were dropped.
    A missing or unparseable artifact is an error, never a silent zero: a real
    zero-booking week is a file whose evidence paths do not resolve.
    """
    p = Path(path)
    if not p.is_file():
        raise RegisterError(f"bookings_artifact_missing:{p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RegisterError(f"bookings_artifact_unreadable:{p}:{exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("records"), list):
        raise RegisterError(f"bookings_artifact_malformed:{p}")

    bases = _candidate_roots(p, root)
    valid: list[dict] = []
    invalid: list[dict] = []
    for rec in doc["records"]:
        if not isinstance(rec, dict):
            invalid.append({"id": "?", "reason": "record_not_mapping"})
            continue
        rid = _as_str(rec.get("id")) or "?"
        missing = [k for k in ("id", "date", "account", "source_record_id",
                               "qualification_evidence_path")
                   if not _as_str(rec.get(k))]
        if missing:
            invalid.append({"id": rid, "reason": "fields_missing:" + ",".join(missing)})
            continue
        if not _is_iso_date(rec.get("date")):
            invalid.append({"id": rid, "reason": "date_not_iso"})
            continue
        resolved = _resolve_evidence(rec.get("qualification_evidence_path"), bases)
        if resolved is None:
            invalid.append({"id": rid,
                            "reason": "qualification_evidence_unresolved:"
                                      + _as_str(rec.get("qualification_evidence_path"))})
            continue
        valid.append({**rec, "qualification_evidence_resolved": str(resolved)})
    return {"week": _as_str(doc.get("week")), "count": len(valid),
            "records": valid, "total": len(doc["records"]), "invalid": invalid}


# ----------------------------------------------------------------- certifier

def _within(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
    except (ValueError, OSError):
        return False
    return True


def gate_register(repo) -> tuple[bool, str]:
    """Hermetic `certify` gate: the committed register validates on its own.

    Reads ONLY `<repo.root>/capability_register.csv`. Never raises — every
    failure comes back as `(False, detail)`. Blanking any row's
    `evidence_paths` turns this RED.
    """
    try:
        root = _repo_root(repo)
        p = root / REGISTER_STORE
        if not p.is_file():
            return False, f"register_missing:{REGISTER_STORE}"
        rows = _read_rows(p)
        if not rows:
            return False, "register_empty"

        seen: set[str] = set()
        dups = []
        for row in rows:
            rid = row.get("id") or "?"
            if rid in seen:
                dups.append(rid)
            seen.add(rid)

        bad = []
        for entry in row_errors(rows):
            bad.append(f"{entry['id']}[{','.join(entry['errors'])}]")
        if bad:
            owners = flagged_owners(rows)
            detail = ("register_rows_invalid:" + ";".join(bad[:6])
                      + (f"|flagged_owners={','.join(owners)}" if owners else ""))
            return False, _clip(detail)

        # the mandatory revenue row is the more fundamental law than path
        # resolution: name the missing KPI before the missing file
        try:
            require_booked_row(rows)
        except RegisterError as exc:
            return False, f"register_{exc}"

        unresolvable = []
        for row in rows:
            for ev in row.get("evidence_paths") or []:
                q = Path(_as_str(ev)).expanduser()
                cand = q if q.is_absolute() else root / q
                if not cand.exists() or not _within(root, cand):
                    unresolvable.append(f"{row.get('id')}:{ev}")
        if unresolvable:
            return False, _clip("evidence_path_unresolved:" + ";".join(unresolvable[:6]))

        if dups:
            return False, _clip("duplicate_row_id:" + ",".join(sorted(set(dups))[:6]))
        return True, f"register_ok rows={len(rows)} booked_qualified_conversations=weighted"
    except Exception as exc:  # a gate must never raise, whatever happened
        return False, _clip(f"register_error:{type(exc).__name__}:{exc}")


def _clip(text: str, limit: int = 400) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."
