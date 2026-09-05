#!/usr/bin/env python3
"""Seed examples/great/<lane>/ with real exemplars ("what great looks like").

Sources, in order of preference:
  1. Hand-authored JakeStudio agent-vault "Great Output Examples.md" files that
     are NON-EMPTY (the pipeline-generated ones are all `## Items (0)` due to an
     upstream bug — those are skipped honestly).
  2. Curated pointers to high-trust canonical assets in this repo.

Each exemplar is normalized to examples/great/<lane>/<slug>.md with frontmatter
(name, lane, source, exemplar_of). Cap 5 per lane. Deterministic, re-runnable.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from rig_capabilities.quality import _assert_unique_exemplar_slugs, _slug

VAULT = Path.home() / "Documents" / "JakeStudio" / "Agent Vaults"
OUT = REPO / "examples" / "great"

# hand-authored vault exemplars -> lane
VAULT_EXEMPLARS = {
    "product-head": "business-ops",
    "marcus-head": "content-publishing",
    "nadia-head": "data-analytics",
    "excellence-ingestion": "research-intel",
}


def _empty_items(text: str) -> bool:
    return bool(re.search(r"##\s*Items\s*\(0\)", text)) and "### " not in text


def seed() -> dict:
    # Validate every generated asset filename before creating any output.
    canon = []
    idx_path = REPO / ".index.json"
    if idx_path.exists():
        idx = json.loads(idx_path.read_text())
        canon = [a for a in idx["assets"]
                 if a.get("source") == "canonical"
                 and (a.get("okf") or {}).get("trust", 0) >= 0.9]
        canon.sort(key=lambda a: -(a.get("okf") or {}).get("trust", 0))
        _assert_unique_exemplar_slugs(a["id"] for a in canon)

    OUT.mkdir(parents=True, exist_ok=True)
    per_lane: dict = {}
    written = 0
    skipped_empty = 0

    for agent, lane in VAULT_EXEMPLARS.items():
        src = VAULT / agent / "Great Output Examples.md"
        if not src.exists():
            continue
        body = src.read_text(errors="replace")
        if _empty_items(body) or len(body.strip()) < 300:
            skipped_empty += 1
            continue
        lane_dir = OUT / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        if len(list(lane_dir.glob("*.md"))) >= 5:
            continue
        # strip the vault frontmatter, keep the content
        content = re.sub(r"\A---\n.*?\n---\n", "", body, count=1, flags=re.S).strip()
        fm = (f"---\nname: great-{agent}\nlane: {lane}\nsource: jakestudio-vault\n"
              f"exemplar_of: {agent}\ndescription: Reference exemplar — what great "
              f"looks like for {lane} ({agent}).\n---\n\n")
        (lane_dir / f"{_slug(agent)}.md").write_text(fm + content + "\n")
        per_lane[lane] = per_lane.get(lane, 0) + 1
        written += 1

    # curated pointers to high-trust canonical assets
    for a in canon:
        lane = (a.get("quality") or {}).get("outcome", "").split(":", 1)[0].strip() \
            or "meta"
        lane_dir = OUT / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        if len(list(lane_dir.glob("*.md"))) >= 5:
            continue
        slug = _slug(a["id"])
        dst = lane_dir / f"{slug}.md"
        if dst.exists():
            continue
        fm = (f"---\nname: great-{slug}\nlane: {lane}\nsource: canonical-curated\n"
              f"exemplar_of: {a['id']}\ndescription: Reference exemplar — "
              f"{a.get('description','')[:140]}\n---\n\n")
        dst.write_text(fm + f"# {a['id']} — reference\n\n"
                       f"Canonical asset `{a['id']}` ({a['kind']}, trust "
                       f"{(a.get('okf') or {}).get('trust')}). "
                       f"Path: `{a.get('path')}`.\n\n"
                       f"> {a.get('description','')}\n")
        per_lane[lane] = per_lane.get(lane, 0) + 1
        written += 1

    return {"written": written, "skipped_empty_vault": skipped_empty,
            "per_lane": per_lane}


if __name__ == "__main__":
    print(json.dumps(seed(), indent=1))
    sys.exit(0)
