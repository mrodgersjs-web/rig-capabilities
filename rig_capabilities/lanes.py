"""V11 — embedding lane overlay to burn down the `misc` backlog.

Uses the cached `.embeddings.json` (nomic-embed vectors, keyed id@sha) to
reassign `misc` assets to their nearest semantic lane. Writes `.lanes.json`
(id -> lane) which the catalog stamps onto assets at index time; `classify`
prefers the overlay. External-root files are never edited — the overlay lives
in `.lanes.json`. Canonical assets additionally get a real `outcome:` line.

Deterministic: lane centroids are the mean of the highest-trust embedded
members of each keyword-classified lane; a misc asset moves only when its best
centroid cosine clears MARGIN.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from .taxonomy import classify, dedupe

MARGIN = 0.70
_CENTROID_CAP = 60

def _load_vectors(repo) -> dict:
    p = Path(repo.root) / ".embeddings.json"
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    vecs = raw.get("vectors", raw)
    out = {}
    for key, vec in vecs.items():
        aid = key.split("@", 1)[0]
        out[aid] = vec  # last write wins (newest sha)
    return out


def _cos(a, b) -> float:
    s = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return s / (na * nb)


def _centroids(assets, vecs) -> dict:
    buckets: dict = {}
    for a in assets:
        lane = classify(a)
        if lane == "misc":
            continue
        v = vecs.get(a["id"])
        if not v:
            continue
        trust = (a.get("okf") or {}).get("trust", 0.6)
        buckets.setdefault(lane, []).append((trust, v))
    cents = {}
    for lane, rows in buckets.items():
        rows.sort(key=lambda r: -r[0])
        top = [v for _t, v in rows[:_CENTROID_CAP]]
        if not top:
            continue
        dim = len(top[0])
        cent = [sum(v[i] for v in top) / len(top) for i in range(dim)]
        cents[lane] = cent
    return cents


def classify_overlay(repo) -> dict:
    """Compute {id: lane} reassignments for misc assets. Pure — no writes."""
    vecs = _load_vectors(repo)
    if not vecs:
        return {}
    assets = dedupe(repo.load_index()["assets"])
    cents = _centroids(assets, vecs)
    if not cents:
        return {}
    overlay = {}
    for a in assets:
        if classify(a) != "misc":
            continue
        v = vecs.get(a["id"])
        if not v:
            continue
        best_lane, best_cos = None, 0.0
        for lane, cent in cents.items():
            c = _cos(v, cent)
            if c > best_cos:
                best_lane, best_cos = lane, c
        if best_lane and best_cos >= MARGIN:
            overlay[a["id"]] = best_lane
    return overlay


def load_overlay(repo) -> dict:
    p = Path(repo.root) / ".lanes.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def apply_overlay(repo) -> dict:
    """Write .lanes.json and stamp canonical frontmatter with outcome:."""
    from .quality import migrate_frontmatter
    overlay = classify_overlay(repo)
    p = Path(repo.root) / ".lanes.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(overlay, indent=1))
    tmp.replace(p)
    # canonical assets are ours: write a real outcome line
    canon_edits = 0
    by_id = {a["id"]: a for a in repo.load_index()["assets"]
             if a["source"] == "canonical"}
    for aid, lane in overlay.items():
        a = by_id.get(aid)
        if not a or not a.get("abs_path"):
            continue
        path = Path(a["abs_path"])
        if path.is_dir():
            path = path / "SKILL.md"
        if path.exists() and migrate_frontmatter(path, {"outcome": f"{lane}: reclassified"}):
            canon_edits += 1
    repo.build_index()
    return {"reassigned": len(overlay), "canonical_frontmatter_edits": canon_edits}
