"""Evidence Ledger — rule 15's table and rule 3's prohibition, made executable.

Transcribed from "RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI
Strategist & Engineer.md": rule 15 mandates the ledger (``Maintain an Evidence Ledger:``)
with exactly these columns — ID, Claim, Evidence, Type, Confidence, Allowed use — and rule
3 forbids the one thing a ledger exists to prevent: ``Never place an unverified claim on a
résumé.``

Rule 3 in code: a row whose ``allowed_use`` includes ``resume`` must be ``type: direct``,
carry ``confidence`` at or above ``RESUME_MIN_CONFIDENCE``, and name an ``evidence`` path
that resolves on disk. Any of those three missing collapses to the single reason
``unverified_claim_on_resume`` — a résumé claim never gets a partial pass. A non-résumé row
with an unresolvable path reports ``evidence_missing`` instead.

Reason vocabulary (``validate_claim`` returns [] only when a row is clean):
``missing_field:<col>``, ``unknown_claim_type:<v>``, ``unknown_allowed_use:<v>``,
``confidence_not_numeric:<v>``, ``confidence_out_of_range:<v>``,
``unverified_claim_on_resume``, ``evidence_missing``.

Lanes are the declared ASCII set. The card's own accented spelling of the lane is NOT an
alias: a row written ``allowed_use: résumé`` is rejected as an unknown lane rather than
slipping past rule 3, so the ledger fails closed and never open.

Register linkage (documented here; ``register.py`` owns the rows, this module writes
none): Phase 1-10 deliverables become register rows with studio ``Strategy`` or ``GTM``,
subsystem ``steering`` for intake and offer work and ``aero`` for the public surface, and
the Phase-11 offering is a row of ``type: offer`` pinned at ``maturity_M0_5: 0`` while its
source section stays truncated. The card's lagging indicator "qualified conversations" is
the EXISTING ``booked_qualified_conversations`` register row — never a second revenue KPI.
"""
from __future__ import annotations

import csv
import os
import stat
import tempfile
from pathlib import Path
from typing import Any

LEDGER_PATH = "evidence_ledger.csv"
LEDGER_COLUMNS: tuple[str, ...] = ("id", "claim", "evidence", "type", "confidence", "allowed_use")

CLAIM_TYPES: tuple[str, ...] = ("direct", "inferred", "planned")
ALLOWED_USES: tuple[str, ...] = ("resume", "interview", "content", "internal")
RESUME_MIN_CONFIDENCE = 0.8

# The hermetic fixture the certify gate reads — nothing else, ever.
FIXTURE_LEDGER = Path("tests") / "fixtures" / "fable2031" / "evidence-ledger-valid.csv"

USE_SEPARATORS = ",;/|"
_ALIAS = {"allowed use": "allowed_use", "allowed-use": "allowed_use"}


def _repo_root(repo: Any) -> Path:
    """Accept a catalog Repo, a Path, or a string; always give back a Path root.

    A ``Path`` has its own ``.root`` attribute (``"/"`` for any absolute path), so it is
    matched before falling back to the Repo-shaped attribute.
    """
    if isinstance(repo, (str, os.PathLike)):
        return Path(repo)
    return Path(getattr(repo, "root", repo))


def _norm_key(key: Any) -> str:
    k = str(key or "").strip().lower()
    return _ALIAS.get(k, k)


def _clean(row: Any) -> dict:
    """Stringify and strip a raw row so header casing/spacing can't leak downstream."""
    out = {}
    for k, v in (row or {}).items():
        if k is None:
            continue
        out[_norm_key(k)] = "" if v is None else str(v).strip()
    return out


def _uses(row: Any) -> list[str]:
    raw = str((row or {}).get("allowed_use") or "")
    for ch in USE_SEPARATORS:
        raw = raw.replace(ch, " ")
    return [t.strip().lower() for t in raw.split() if t.strip()]


def _confidence(value: Any) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _resolve(evidence: Any, base: Path) -> Path | None:
    """An evidence cell is a path. Relative paths resolve against ``base``."""
    raw = str(evidence or "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = base / p
    return p if p.exists() else None


def validate_claim(row: Any, root: Any = None) -> list[str]:
    """Every rule this ledger can break, as reasons. Empty list means the row is clean.

    Relative ``evidence`` paths resolve against ``root`` (default: the working directory),
    so a fixture can name repo-rooted artifacts and stay checkable from anywhere.
    """
    r = _clean(row) if isinstance(row, dict) else {}
    base = _repo_root(root) if root is not None else Path.cwd()
    missing = [c for c in LEDGER_COLUMNS if not r.get(c)]
    if missing:
        return [f"missing_field:{c}" for c in missing]

    ctype = r["type"].lower()
    if ctype not in CLAIM_TYPES:
        return [f"unknown_claim_type:{r['type']}"]

    uses = _uses(r)
    unknown = sorted({u for u in uses if u not in ALLOWED_USES})
    if unknown:
        return [f"unknown_allowed_use:{u}" for u in unknown]

    conf = _confidence(r["confidence"])
    if conf is None:
        return [f"confidence_not_numeric:{r['confidence']}"]
    if not 0.0 <= conf <= 1.0:
        return [f"confidence_out_of_range:{r['confidence']}"]

    # Rule 3. All three conditions fail into one reason so a résumé claim is never
    # half-cleared: direct, at/above the floor, and an evidence path on disk.
    if "resume" in uses:
        if ctype != "direct" or conf < RESUME_MIN_CONFIDENCE or _resolve(r["evidence"], base) is None:
            return ["unverified_claim_on_resume"]
        return []

    if _resolve(r["evidence"], base) is None:
        return ["evidence_missing"]
    return []


def _read_csv(path: Path) -> tuple[list[dict], list[str]]:
    """Rows plus any ledger columns the file's own header fails to declare."""
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = [_norm_key(h) for h in (reader.fieldnames or [])]
        rows = [_clean(r) for r in reader]
    return rows, [c for c in LEDGER_COLUMNS if c not in header]


def load_ledger(repo: Any, path: Any = None) -> list[dict]:
    """Read a ledger. A missing file reads as an empty ledger, never an exception."""
    p = Path(path) if path is not None else _repo_root(repo) / LEDGER_PATH
    if not p.is_file():
        return []
    try:
        rows, _ = _read_csv(p)
    except (OSError, UnicodeDecodeError, csv.Error):
        return []
    return rows


def _file_mode(target: Path) -> int:
    """Keep the file's own mode when overwriting; fall back to umask when creating.

    ``mkstemp`` creates 0600, which would make a committed ledger unreadable to anything
    but its owner. The ledger is a shared artifact, so it gets normal file permissions.
    """
    try:
        return stat.S_IMODE(target.stat().st_mode)
    except OSError:
        mask = os.umask(0)
        os.umask(mask)
        return 0o666 & ~mask


def write_ledger(repo: Any, rows: Any, path: Any = None) -> None:
    """Write the ledger atomically, sorted by id, in the card's column order."""
    p = Path(path) if path is not None else _repo_root(repo) / LEDGER_PATH
    ordered = sorted((_clean(r) for r in rows), key=lambda r: r.get("id", ""))
    p.parent.mkdir(parents=True, exist_ok=True)
    mode = _file_mode(p)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=f".{p.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(LEDGER_COLUMNS)
            for row in ordered:
                writer.writerow([row.get(c, "") for c in LEDGER_COLUMNS])
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, p)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def resume_claims(rows: Any, root: Any = None) -> list[dict]:
    """Only the rows rule 3 permits on a résumé: labelled for it and clean on the checks."""
    return [r for r in rows if "resume" in _uses(r) and not validate_claim(r, root=root)]


def gate_evidence_ledger(repo: Any) -> tuple[bool, str]:
    """Hermetic certify gate: reads ONLY the committed valid fixture. Never raises.

    Green means every fixture row clears rule 3. Flipping a ``type: planned`` row's
    ``allowed_use`` to include ``resume`` must turn this RED — a gate that stays green
    under that plant is theater.
    """
    try:
        root = _repo_root(repo)
        path = root / FIXTURE_LEDGER
        if not path.is_file():
            return False, f"fixture_missing:{FIXTURE_LEDGER.as_posix()}"
        rows, header_missing = _read_csv(path)
        if header_missing:
            return False, "header_missing:" + ",".join(header_missing)
        if not rows:
            return False, "empty_ledger"
        bad = []
        for row in rows:
            errors = validate_claim(row, root=root)
            if errors:
                bad.append(f"{row.get('id') or '?'}:{','.join(errors)}")
        if bad:
            return False, "invalid[" + "; ".join(bad) + "]"
        return True, f"ok:{len(rows)} rows cleared rule 3"
    except Exception as exc:  # a gate reports, it never propagates
        return False, f"gate_error:{type(exc).__name__}:{exc}"
