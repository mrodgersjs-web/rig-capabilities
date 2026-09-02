"""P2: deterministic corpus scan, dedup, and the unclassified-rate refusal seam.

Nine source cards in, one honest count out. Selection is **manifest-first**: a card
that is enumerated is in the corpus even when its frontmatter says nothing — three of
the nine (PROMPT PACK, GAP REGISTER, Known Expert OS) carry no `Build Cards` tag and
are exactly the truncated ones, so a tag-only filter would silently drop the very
evidence that is weakest. Tags are the fallback, never the authority.

Classification is data, not a model: ordered rules in `data/fable2031/classify_rules.json`,
first match wins, no match stays honestly `unclassified`. When the unclassifiable share
of what was actually found exceeds `UNCLASSIFIED_HALT_RATE`, the corpus refuses to be
scored — a classifier that cannot name a tenth of the corpus has no business scoring it.

Every count is computed from files on disk. "~453 Build Cards" is prose, never a
denominator.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SOURCE_MANIFEST = "data/fable2031/source_inventory.json"
CLASSIFY_RULES = "data/fable2031/classify_rules.json"
CORPUS_ROOTS = ("~/Downloads", "~/mnt/RIGLake")
UNCLASSIFIED_HALT_RATE = 0.10

#: the committed per-card snapshot a hermetic `corpus_refusal` gate reads (Law L1)
FIXTURE_MANIFEST = "tests/fixtures/fable2031/corpus-manifest.json"

CARD_SUFFIXES = (".md", ".markdown")
#: a card is a card; anything larger is not a card
MAX_CARD_BYTES = 5_000_000

_DASHES = {"\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2192": "->",
           "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'}
_COPY_SUFFIX = re.compile(r"\s*\((\d+)\)$")
_PIPE_ROW = re.compile(r"^\s*\|")
_LIST_LEAD = re.compile(r"^(?:\*\*|__)?\s*\d+[.)](?:\*\*|__)?[\s.*/_-]|^\s*[-*+]\s")
# a sentence-closing mark with a stray single character glued to it: `register.**Z`
_GLUED_FRAGMENT = re.compile(r"(?:[.)\]}]|\*\*)[A-Za-z0-9]$")
# the line stops on a connector: the thought continues past the end of the file
_DANGLING = re.compile(r"[,;:\-—>→(/[{_]$")
_HEADING = re.compile(r"^#{1,6}\s+\S")
_OBJECTIVE = re.compile(r"^#{1,6}\s*Objective\s*$", re.I)
_SOURCES = re.compile(r"^#{1,6}\s*Sources\s*$", re.I)


class CorpusRefusal(Exception):
    """The corpus cannot be scored: too much of it is unclassifiable, or there is none."""


# --------------------------------------------------------------------------- io


def _resolve(path) -> Path:
    """Repo-relative stays repo-relative; everything else expands."""
    p = Path(str(path)).expanduser()
    return p if p.is_absolute() else (REPO_ROOT / p)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the flat `key: value` frontmatter RIG cards carry; body is returned as-is."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}, text
    meta: dict = {}
    key = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if raw[:1] in (" ", "\t") and raw.strip().startswith("-") and key == "tags":
            meta.setdefault("tags", []).append(raw.strip()[1:].strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if not val:
            meta[key] = [] if key == "tags" else ""
            continue
        if key == "tags" and val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            meta[key] = [t.strip().strip("\"'") for t in inner.split(",") if t.strip()]
        elif key == "tags":
            meta[key] = [val.strip("\"'")]
        else:
            meta[key] = val.strip("\"'")
    meta.setdefault("tags", [])
    if isinstance(meta.get("tags"), str):
        meta["tags"] = [meta["tags"]] if meta["tags"] else []
    return meta, "\n".join(lines[end + 1:])


def _stamp(value: str) -> float:
    """Best-effort timestamp for the newest-body tiebreak; unknown sorts oldest."""
    if not value:
        return 0.0
    text = str(value).strip()
    iso = re.sub(r"\s+GMT[+-]\d{4}.*$", "", text).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%a %b %d %Y %H:%M:%S",
                "%a %b %d %H:%M:%S %Y"):
        try:
            dt = datetime.strptime(iso[:26], fmt)
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


# ------------------------------------------------------------------ card identity


def normalize_title(title: str) -> str:
    """One canonical spelling per title: casefolded, dash-folded, whitespace-collapsed."""
    text = str(title or "")
    for src, dst in _DASHES.items():
        text = text.replace(src, dst)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold().strip(". ")


def card_key(path, text: str | None = None) -> str:
    """Frontmatter `title:` when present, else the file stem minus a ` (N)` copy suffix.

    `text` lets a scan reuse bytes it already read instead of opening the card twice.
    """
    p = Path(path)
    title = ""
    if text is None:
        try:
            text = _read_text(p)
        except OSError:
            text = ""
    title = str(split_frontmatter(text)[0].get("title") or "")
    stem = p.stem
    return normalize_title(title) if title else normalize_title(_COPY_SUFFIX.sub("", stem))


def _cells(line: str) -> int:
    return len([c for c in line.strip().strip("|").split("|")])


def _in_table_block(lines: list[str]) -> bool:
    """True when the final non-empty line belongs to a pipe table that runs to EOF."""
    tail = [l for l in lines if l.strip()]
    return bool(tail) and bool(_PIPE_ROW.match(tail[-1]))


def _table_rows(lines: list[str]) -> tuple[int, int]:
    """(header cells, last row cells) of the table block that ends the document."""
    tail = [l.strip() for l in lines if l.strip()]
    block: list[str] = []
    for line in reversed(tail):
        if not _PIPE_ROW.match(line):
            break
        block.insert(0, line)
    if len(block) < 2:
        return 0, 0
    return _cells(block[0]), _cells(block[-1])


def detect_truncation(text: str) -> tuple[bool, str]:
    """Structural only: (truncated, anchor).

    ANCHOR RULE — the anchor MARKS the truncation. It is the last content line before
    the cut; or, when the cut sits mid-document and a structural marker immediately
    follows it, that marker. A marker outranks whatever survives beneath it: Known
    Expert OS is cut with one line of Phase 11's objective left standing and `## Sources`
    immediately after, so the anchor is `## Sources` — the heading that proves the body
    is gone — and NOT the `- [website](…)` bullet that survives under that heading.

    The three real cards are the acceptance values. `data/fable2031/source_inventory.json`
    and `docs/TRUNCATED-SOURCES.md` must agree with them in both directions
    (`tests/fable2031_corpus.py::TruncationLedgerTests`):
      PROMPT PACK     -> (True, "| QNA |")                         cut at EOF, table
      GAP REGISTER    -> (True, "**3. No capability register.**Z") cut at EOF, list item
      Known Expert OS -> (True, "## Sources")                      marker after the cut

    Three shapes are recognised — none of them needs the missing content, all of them
    are visible in what survives:
      1. an unterminated markdown table: a pipe row sits at EOF, and/or has fewer
         cells than its header (PROMPT PACK ends mid-table at `| QNA |`);
      2. a body that ends mid-list-item: an item line whose last token is a stray
         character glued to a closing mark, or that stops on a connector
         (GAP REGISTER ends `**3. No capability register.**Z`);
      3. a `## Objective` whose whole body is one line immediately followed by
         `## Sources` (Known Expert OS Phase 11 — the phase body is gone).
    """
    lines = str(text or "").split("\n")
    meaningful = [l.strip() for l in lines if l.strip()]
    if not meaningful:
        return False, ""
    anchor = meaningful[-1]

    head_cells, last_cells = _table_rows(lines)
    # a pipe table that runs to EOF is a table nobody finished writing
    if _in_table_block(lines) and (last_cells < head_cells or head_cells <= 1):
        return True, anchor

    last = anchor
    if _LIST_LEAD.match(last) and (_GLUED_FRAGMENT.search(last) or _DANGLING.search(last)):
        return True, anchor

    heads = [i for i, l in enumerate(lines) if _HEADING.match(l)]
    starts = [heads[i] for i, h in enumerate(heads) if _OBJECTIVE.match(lines[h])]
    if starts:
        start = starts[-1]
        nxt = [h for h in heads if h > start]
        body_lines = [l for l in lines[start + 1:(nxt[0] if nxt else len(lines))] if l.strip()]
        # one surviving line of objective, then the card runs straight into its Sources.
        # the heading is the marker that proves the phase body is gone, so the heading is
        # the anchor — never the source bullets that survive beneath it.
        if len(body_lines) == 1 and nxt and _SOURCES.match(lines[nxt[0]]):
            return True, lines[nxt[0]].strip()
    return False, anchor


# ------------------------------------------------------------------- corpus scan


def _manifest_paths(manifest) -> dict[str, dict]:
    """{resolved path -> inventory entry}; accepts a path, a list, or a dict."""
    data = manifest
    if data is None:
        return {}
    if isinstance(data, (str, Path)):
        p = _resolve(data)
        if not p.is_file():
            return {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
    if isinstance(data, dict):
        data = data.get("cards") or data.get("sources") or []
    out: dict[str, dict] = {}
    for entry in data or []:
        if isinstance(entry, str):
            entry = {"path": entry}
        if not isinstance(entry, dict) or not entry.get("path"):
            continue
        try:
            out[str(_resolve(entry["path"]).resolve())] = entry
        except OSError:
            out[str(_resolve(entry["path"]))] = entry
    return out


def _roots(roots) -> list[str]:
    if roots is None:
        seq = list(CORPUS_ROOTS)
    elif isinstance(roots, (str, Path)):
        seq = [str(roots)]
    else:
        seq = [str(r) for r in roots]
    return seq


def _tag_selected(meta: dict) -> bool:
    return any(normalize_title(t) == normalize_title("Build Cards")
               for t in (meta.get("tags") or []))


def _head_frontmatter(path: Path, limit: int = 65_536) -> dict:
    """Read the frontmatter only — a root can hold a hundred thousand non-cards.

    A file with no closing fence inside its first `limit` bytes has no frontmatter,
    which is exactly what the caller needs to know.
    """
    try:
        with path.open("rb") as handle:
            blob = handle.read(limit)
    except OSError:
        return {}
    if not blob.startswith(b"---"):
        return {}
    lines = blob.decode("utf-8", errors="replace").split("\n")
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return split_frontmatter("\n".join(lines[:i + 1]))[0]
    return {}


def scan_corpus(roots=CORPUS_ROOTS, manifest=SOURCE_MANIFEST) -> dict:
    """Scan roots, select by manifest-or-tag, collapse duplicates, keep contradictions honest.

    `raw` counts every selected file; `unique` counts distinct card keys. The arithmetic
    is an identity: raw == unique + len(duplicates) + len(contradiction_variants). A root
    that is absent reports `present: false` with zero cards and never shrinks the
    denominator of anything.
    """
    indexed = _manifest_paths(manifest)
    root_rows, selected = [], []
    for root in _roots(roots):
        path = Path(str(root)).expanduser()
        if not path.is_dir():
            root_rows.append({"root": str(root), "present": False, "cards": 0})
            continue
        found = 0
        for f in sorted(p for suffix in CARD_SUFFIXES
                        for p in path.rglob(f"*{suffix}")):
            if not f.is_file() or f.stat().st_size > MAX_CARD_BYTES:
                continue
            try:
                resolved = str(f.resolve())
            except OSError:
                resolved = str(f)
            in_manifest = resolved in indexed
            if not in_manifest and not _tag_selected(_head_frontmatter(f)):
                continue
            try:
                raw = f.read_bytes()
            except OSError:
                continue
            if len(raw) > MAX_CARD_BYTES:
                continue
            text = raw.decode("utf-8", errors="replace")
            meta, body = split_frontmatter(text)
            found += 1
            selected.append({"path": f, "bytes": raw, "text": text, "meta": meta,
                             "body": body, "in_manifest": in_manifest,
                             "manifest": indexed.get(resolved)})
        root_rows.append({"root": str(root), "present": True, "cards": found})

    groups: dict[str, list[dict]] = {}
    for card in selected:
        p, raw, meta, body = card["path"], card["bytes"], card["meta"], card["body"]
        truncated, anchor = detect_truncation(body or card["text"])
        key = card_key(p, card["text"])
        groups.setdefault(key, []).append({
            "path": str(p), "title": str(meta.get("title") or key),
            "tags": list(meta.get("tags") or []),
            "updated_at": str(meta.get("updatedAt") or ""),
            "stamp": _stamp(str(meta.get("updatedAt") or "")),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "body_len": len(body or ""), "truncated": truncated,
            "end_anchor": anchor if truncated else None,
            "in_manifest": bool(card["in_manifest"]),
            "inventory": card["manifest"],
        })

    duplicates: list[dict] = []
    contradictions: list[dict] = []
    cards: list[dict] = []
    for key in sorted(groups):
        members = sorted(groups[key],
                         key=lambda c: (-c["body_len"], -c["stamp"], c["path"]))
        primary = members[0]
        for extra in members[1:]:
            if extra["sha256"] == primary["sha256"]:
                duplicates.append({"key": key, "path": extra["path"],
                                   "sha256": extra["sha256"], "bytes": extra["bytes"],
                                   "kept": primary["path"]})
            else:
                contradictions.append({"key": key, "path": extra["path"],
                                       "sha256": extra["sha256"],
                                       "kept": primary["path"],
                                       "kept_sha256": primary["sha256"]})
        cards.append({
            "key": key, "path": primary["path"], "sha256": primary["sha256"],
            "bytes": primary["bytes"], "truncated": primary["truncated"],
            "in_manifest": any(m["in_manifest"] for m in members),
            "title": primary["title"], "tags": primary["tags"],
            "updated_at": primary["updated_at"], "end_anchor": primary["end_anchor"],
            "variants": sorted({m["sha256"] for m in members}),
        })

    return {"raw": len(selected), "unique": len(cards),
            "duplicates": duplicates, "contradiction_variants": contradictions,
            "roots": root_rows, "cards": cards}


# ------------------------------------------------------------------ classification


def load_rules(path=CLASSIFY_RULES) -> list[dict]:
    """Ordered classification rules; a missing or broken file means nothing classifies."""
    p = _resolve(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rules = data.get("rules") if isinstance(data, dict) else data
    return [r for r in (rules or []) if isinstance(r, dict) and r.get("match")]


def _field_text(card: dict, field: str) -> str:
    if field == "tags":
        return "\n".join(str(t) for t in (card.get("tags") or []))
    if field == "body":
        path = card.get("path")
        if path:
            try:
                return _read_text(Path(path))
            except OSError:
                return ""
        return str(card.get("body") or "")
    return str(card.get(field if field in card else "title") or "")


def classify(card: dict, rules: list[dict] | None = None) -> dict:
    """First matching rule wins. No match is reported as unclassified, never guessed."""
    for idx, rule in enumerate(rules if rules is not None else load_rules()):
        match = rule.get("match") or {}
        field = str(match.get("field") or "title")
        needles = match.get("contains") or []
        if isinstance(needles, str):
            needles = [needles]
        if not needles:
            continue
        haystack = _field_text(card, field).casefold()
        if any(str(n).casefold() in haystack for n in needles):
            return {"subsystem": rule.get("subsystem"), "studio": rule.get("studio"),
                    "type": rule.get("type"), "unclassified": False,
                    "reason": "rule_matched", "rule_index": idx,
                    "rule_id": rule.get("id")}
    return {"subsystem": None, "studio": None, "type": None,
            "unclassified": True, "reason": "no_rule_matched"}


def _report(roots=None, manifest=SOURCE_MANIFEST) -> dict:
    scan = scan_corpus(roots=roots if roots is not None else list(CORPUS_ROOTS),
                       manifest=manifest)
    cards = scan["cards"]
    verdicts = [classify(c) for c in cards]
    unclassified = sum(1 for v in verdicts if v["unclassified"])
    unique = len(cards)
    out = {"raw": scan["raw"], "unique": unique,
           "classified": unique - unclassified, "unclassified": unclassified,
           "unclassified_rate": 0.0,
           "truncated": sum(1 for c in cards if c["truncated"]),
           "duplicates": len(scan["duplicates"]),
           "contradiction_variants": len(scan["contradiction_variants"]),
           "roots": scan["roots"], "halt_rate": UNCLASSIFIED_HALT_RATE}
    if unique == 0:
        # never a division, never a pass
        out.update({"ok": False, "reason": "empty_corpus", "unclassified_rate": 0.0})
        return out
    out["unclassified_rate"] = round(unclassified / unique, 6)
    if out["unclassified_rate"] > UNCLASSIFIED_HALT_RATE:
        out.update({"ok": False, "reason": "unclassified_rate_exceeded"})
        return out
    out["ok"] = True
    out["reason"] = "scorable"
    return out


def corpus_report(roots=None, manifest=SOURCE_MANIFEST) -> dict:
    """{raw, unique, classified, unclassified, unclassified_rate, truncated, ok}."""
    return _report(roots=roots, manifest=manifest)


def assert_scorable(report: dict) -> dict:
    """The refusal seam a weekly score must pass through before it computes anything."""
    if not report.get("ok"):
        raise CorpusRefusal(str(report.get("reason") or "corpus_not_scorable"))
    return report


# ----------------------------------------------------------------- hermetic gate


def _repo_root(repo) -> Path:
    """Repo-shaped, str, or PathLike — never `Path("/abs").root == "/"`."""
    if isinstance(repo, (str, os.PathLike)):
        return Path(str(repo) or ".").expanduser()
    root = getattr(repo, "root", None)
    if root is not None:
        return Path(str(root) or ".").expanduser()
    return REPO_ROOT


def gate_corpus_refusal(repo) -> tuple[bool, str]:
    """`certify` gate `corpus_refusal` — hermetic: reads one committed snapshot only.

    The unclassified rate comes from `tests/fixtures/fable2031/corpus-manifest.json`,
    a committed {key, classified} snapshot, so the gate never touches ~/Downloads or a
    model (Law L1) and a planted copy of the fixture turns it RED.
    """
    root = _repo_root(repo)
    path = root / FIXTURE_MANIFEST
    if not path.is_file():
        return False, f"corpus_manifest_missing:{path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"corpus_manifest_unreadable:{type(exc).__name__}"
    cards = data.get("cards") if isinstance(data, dict) else data
    if not isinstance(cards, list) or not cards:
        return False, "corpus_manifest_empty"
    unclassified = sum(1 for c in cards if not (isinstance(c, dict) and c.get("classified")))
    total = len(cards)
    rate = unclassified / total
    detail = (f"rate={rate:.4f} unclassified={unclassified}/{total} "
              f"halt={UNCLASSIFIED_HALT_RATE} source={FIXTURE_MANIFEST}")
    return rate <= UNCLASSIFIED_HALT_RATE, detail
