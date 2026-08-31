#!/usr/bin/env python3
"""V12 — RIG coverage matrix + per-agent skill packs.

Reads agents/roster.json (agent -> lanes, the 8 verticals) and the live index.
Emits:
  docs/COVERAGE.md         lane asset counts + per-agent lane coverage + gaps
  agents/<id>/pack.json    per-agent pack: lanes + top-5 assets/lane by trust
  .context/requests.jsonl  capability requests for thin cells (< MIN_ASSETS)

Deterministic; re-runnable.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MIN_ASSETS = 3


def _load():
    roster = json.loads((REPO / "agents" / "roster.json").read_text())
    idx = json.loads((REPO / ".index.json").read_text())
    return roster, idx


def _lane_of(a: dict) -> str:
    import sys as _sys
    _sys.path.insert(0, str(REPO))
    from rig_capabilities.taxonomy import classify
    return classify(a)


def build() -> dict:
    roster, idx = _load()
    assets = idx["assets"]
    lane_counts = Counter(_lane_of(a) for a in assets)
    lanes = sorted(lane_counts, key=lambda l: -lane_counts[l])

    # per-agent packs
    packs_written = 0
    top_by_lane: dict = {}
    for lane in lanes:
        rows = [a for a in assets if _lane_of(a) == lane]
        rows.sort(key=lambda a: -((a.get("okf") or {}).get("trust", 0)))
        top_by_lane[lane] = rows[:5]

    for agent, alanes in roster["agents"].items():
        d = REPO / "agents" / agent
        d.mkdir(parents=True, exist_ok=True)
        skills = []
        for lane in alanes:
            for a in top_by_lane.get(lane, []):
                skills.append({"id": a["id"], "kind": a["kind"], "lane": lane,
                               "trust": (a.get("okf") or {}).get("trust")})
        (d / "pack.json").write_text(json.dumps(
            {"agent": agent, "lanes": alanes, "skills": skills}, indent=1))
        packs_written += 1

    # vertical x lane gaps -> requests
    req_path = REPO / ".context"
    req_path.mkdir(exist_ok=True)
    gaps = []
    for v in roster["verticals"]:
        # a vertical is "covered" in a lane if any asset id/desc mentions it
        for lane in lanes:
            hits = sum(1 for a in assets if _lane_of(a) == lane
                       and v.replace("_", " ") in (a.get("description", "") + a["id"]).lower())
            if hits < MIN_ASSETS:
                gaps.append({"type": "capability_request", "vertical": v,
                             "lane": lane, "have": hits, "need": MIN_ASSETS})
    with (req_path / "requests.jsonl").open("a") as f:
        for g in gaps:
            f.write(json.dumps(g) + "\n")

    # COVERAGE.md
    md = ["# RIG coverage matrix\n",
          f"Generated from {len(assets)} assets, {len(roster['agents'])} agents, "
          f"{len(roster['verticals'])} verticals.\n",
          "## Assets per lane\n", "| lane | assets |", "|---|---|"]
    for lane in lanes:
        md.append(f"| {lane} | {lane_counts[lane]} |")
    md.append("\n## Agent lane coverage\n")
    md.append("| agent | lanes | pack skills |")
    md.append("|---|---|---|")
    for agent, alanes in roster["agents"].items():
        n = sum(len(top_by_lane.get(l, [])) for l in alanes)
        md.append(f"| {agent} | {', '.join(alanes)} | {n} |")
    md.append(f"\n## Gaps (< {MIN_ASSETS} assets for a vertical in a lane)\n")
    md.append(f"{len(gaps)} thin cells recorded to `.context/requests.jsonl`. "
              "Top verticals by gap count:")
    gc = Counter(g["vertical"] for g in gaps)
    for v, c in gc.most_common():
        md.append(f"- {v}: {c} thin lanes")
    (REPO / "docs" / "COVERAGE.md").write_text("\n".join(md) + "\n")

    return {"lanes": len(lanes), "agents": len(roster["agents"]),
            "packs_written": packs_written, "gaps": len(gaps)}


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
