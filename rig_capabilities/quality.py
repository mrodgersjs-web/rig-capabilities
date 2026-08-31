"""V7 — skill quality contract.

Every canonical asset should declare, in frontmatter:
  outcome        one-line result the asset produces (maps to an outcome lane)
  done_when      list of criteria; a subset are runnable (see done_tests.py)
  great_example  path to a reference exemplar (examples/great/<lane>/<id>.md)
  quality_floor  float 0..1 — the minimum quality bar for this asset

Quality is a separate axis from OKF trust: trust = provenance confidence,
quality = specification completeness. Score is deterministic.
"""
from __future__ import annotations

import re
from pathlib import Path

FIELDS = ("outcome", "done_when", "great_example", "quality_floor")
_WEIGHT = {"outcome": 30, "done_when": 30, "great_example": 25, "quality_floor": 15}
_FENCE = re.compile(r"^---\s*$")


def check_asset(a: dict) -> dict:
    """Score one indexed asset's quality-field completeness (0..100)."""
    okf = a.get("okf") or {}
    fm = a.get("quality") or {}  # populated by catalog when present
    present = {}
    score = 0
    for f in FIELDS:
        val = fm.get(f) if f in fm else okf.get(f)
        has = bool(val) if f != "quality_floor" else (val not in (None, "", 0))
        present[f] = has
        if has:
            score += _WEIGHT[f]
    done = fm.get("done_when") or okf.get("done_when") or []
    has_done_test = any(
        isinstance(d, str) and d.split(":", 1)[0] in ("cmd", "file", "grep", "mcp")
        for d in (done if isinstance(done, list) else [done])
    )
    return {
        "id": a.get("id"),
        "kind": a.get("kind"),
        "score": score,
        "missing": [f for f in FIELDS if not present[f]],
        "has_done_test": has_done_test,
    }


def quality_report(repo, canonical_only: bool = True) -> dict:
    doc = repo.load_index()
    rows = []
    per_kind: dict = {}
    fully = 0
    for a in doc.get("assets") or []:
        if canonical_only and a.get("source") != "canonical":
            continue
        r = check_asset(a)
        rows.append(r)
        k = per_kind.setdefault(a["kind"], {"n": 0, "sum": 0, "full": 0})
        k["n"] += 1
        k["sum"] += r["score"]
        if r["score"] == 100:
            k["full"] += 1
            fully += 1
    rows.sort(key=lambda r: r["score"])
    for k, v in per_kind.items():
        v["avg"] = round(v["sum"] / v["n"], 1) if v["n"] else 0
        v.pop("sum", None)
    return {
        "total": len(rows),
        "fully_specified": fully,
        "avg_score": round(sum(r["score"] for r in rows) / len(rows), 1) if rows else 0,
        "per_kind": per_kind,
        "weakest": rows[:20],
    }


def _split_fence(text: str):
    """Return (frontmatter_lines, body) if a leading --- fence exists, else (None, text)."""
    lines = text.splitlines(keepends=True)
    if not lines or not _FENCE.match(lines[0].rstrip("\n")):
        return None, text
    for i in range(1, min(len(lines), 200)):
        if _FENCE.match(lines[i].rstrip("\n")):
            return lines[1:i], "".join(lines[i + 1:])
    return None, text


def migrate_frontmatter(path: Path, fields: dict) -> bool:
    """Insert any missing quality keys into a file's leading --- fence.

    Returns True if the file was changed. List values render as YAML block lists.
    Never overwrites an existing key. Creates a fence if the file has none.
    """
    path = Path(path)
    text = path.read_text()
    # scripts: comment-metadata after the shebang, never a YAML fence (which
    # would sit above the shebang and break execution)
    if text.startswith("#!"):
        return _migrate_script_comments(path, text, fields)
    fm_lines, body = _split_fence(text)
    existing_keys = set()
    if fm_lines is not None:
        for ln in fm_lines:
            m = re.match(r"^([A-Za-z0-9_\-]+)\s*:", ln)
            if m:
                existing_keys.add(m.group(1).lower())
    additions = []
    for key, val in fields.items():
        if key.lower() in existing_keys:
            continue
        if isinstance(val, (list, tuple)):
            additions.append(f"{key}:\n")
            for item in val:
                additions.append(f"  - {item}\n")
        else:
            additions.append(f"{key}: {val}\n")
    if not additions:
        return False
    if fm_lines is None:
        new = "---\n" + "".join(additions) + "---\n\n" + text
    else:
        new = "---\n" + "".join(fm_lines) + "".join(additions) + "---\n" + body
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new)
    tmp.replace(path)
    return True


def _migrate_script_comments(path: Path, text: str, fields: dict) -> bool:
    lines = text.splitlines()
    shebang, rest = lines[0], lines[1:]
    existing = set()
    for ln in rest[:40]:
        m = re.match(r"^#\s*([A-Za-z0-9_\-]+)\s*:", ln)
        if m:
            existing.add(m.group(1).lower())
    adds = []
    for key, val in fields.items():
        if key.lower() in existing:
            continue
        if isinstance(val, (list, tuple)):
            adds.append(f"# {key}: " + " || ".join(str(v) for v in val))
        else:
            adds.append(f"# {key}: {val}")
    if not adds:
        return False
    new = shebang + "\n" + "\n".join(adds) + "\n" + "\n".join(rest) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new)
    tmp.replace(path)
    return True


_KIND_DONE = {
    "skill": ["file:{path}", "the skill's stated outcome is achievable end-to-end"],
    "harness": ["file:{path}", "a session of this type completes with its gate green"],
    "loop": ["file:{path}", "the loop file parses and declares a termination test"],
    "hook": ["file:{path}", "hook is registered and fires on its trigger fixture"],
    "command": ["file:{path}", "command routes to the documented MCP tool"],
    "agent": ["file:{path}", "agent yields its declared artifact"],
}


def migrate_canonical(repo) -> dict:
    """Seed outcome/done_when/great_example/quality_floor on every canonical asset."""
    from .taxonomy import route
    doc = repo.load_index()
    changed = 0
    for a in doc.get("assets") or []:
        if a.get("source") != "canonical":
            continue
        abs_path = a.get("abs_path")
        if not abs_path:
            continue
        p = Path(abs_path)
        if p.is_dir():
            main = p / "SKILL.md"
            p = main if main.exists() else next(
                (f for f in sorted(p.rglob("*")) if f.is_file()), None)
        if p is None or not p.exists():
            continue
        try:
            lane = route(repo, f"{a['id']} {a.get('description','')}", per=1)["lanes"]
            lane_name = lane[0]["outcome"] if lane else "misc"
        except Exception:
            lane_name = "misc"
        rel = a.get("path", a["id"])
        done = [d.replace("{path}", rel) for d in _KIND_DONE.get(a["kind"], ["file:" + rel])]
        great = f"examples/great/{lane_name}/{a['id']}.md"
        fields = {"outcome": f"{lane_name}: {a.get('description','')[:120]}".strip(),
                  "done_when": done,
                  "great_example": great,
                  "quality_floor": 0.6}
        if migrate_frontmatter(p, fields):
            changed += 1
    repo.build_index()
    return {"canonical_migrated": changed}
