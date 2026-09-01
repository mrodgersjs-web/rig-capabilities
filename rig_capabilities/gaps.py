"""V26: turn coverage-gap requests into draft harnesses.

`.context/requests.jsonl` records (vertical, lane, have, need). A cell with
have < need is a gap. This module ranks unique verticals by the worst cell,
then writes a compact draft harness whose done_when is file+body-grep — the
draft is executable, not a comment. Regenerating is idempotent (same path,
same bytes if the rank is unchanged).
"""
from __future__ import annotations

import json
from pathlib import Path

# One falsifiable stake per vertical — grepped in the draft body so a
# hollow template cannot pass its own done_when.
STAKES = {
    "healthcare": ("PHI", "No PHI in logs, prompts, pack markdown, or traces."),
    "dental": ("claim-denial", "Every recommendation names a claim-denial code or admits none exists."),
    "legal": ("privilege", "Attorney-client privilege boundary is named before any artifact is written."),
    "manufacturing": ("lot-genealogy", "Lot genealogy is traced before a quality claim is scored."),
    "construction": ("OSHA", "OSHA-relevant constraints are listed; silence is a finding."),
    "pe_cfo": ("working-capital", "Working-capital impact is a number or an explicit unknown."),
    "personal_brand": ("anti-thirst", "Anti-thirst guardrail: no attractiveness-as-product copy."),
    "wild_card": ("falsifiable-bet", "The bet is written so a later observation can prove it wrong."),
}


def load_requests(repo) -> list:
    p = Path(repo.root) / ".context" / "requests.jsonl"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "capability_request":
            continue
        rows.append(rec)
    return rows


PREFERRED_LANE = {
    "healthcare": "security-review",
    "dental": "revenue-gtm",
    "legal": "docs-knowledge",
    "manufacturing": "infra-ops",
    "construction": "docs-knowledge",
    "pe_cfo": "data-analytics",
    "personal_brand": "content-publishing",
    "wild_card": "agent-engineering",
}


def rank_gaps(rows: list, n: int = 8) -> list:
    """One row per vertical. Prefer the vertical's designated lane when that
    cell is still a gap; otherwise the largest (need-have)."""
    cells: dict = {}
    for r in rows:
        v, lane = r.get("vertical") or "", r.get("lane") or ""
        if not v or not lane:
            continue
        have, need = int(r.get("have") or 0), int(r.get("need") or 0)
        gap = need - have
        if gap <= 0:
            continue
        key = (v, lane)
        # jsonl is append-only; last row for a cell is current coverage
        cells[key] = {"vertical": v, "lane": lane, "have": have,
                      "need": need, "gap": gap}
    by_v: dict = {}
    for cand in cells.values():
        by_v.setdefault(cand["vertical"], []).append(cand)
    picked = []
    for v, opts in by_v.items():
        pref = PREFERRED_LANE.get(v)
        chosen = next((o for o in opts if o["lane"] == pref), None)
        if chosen is None:
            chosen = max(opts, key=lambda o: (o["gap"], o["need"], o["lane"]))
        picked.append(chosen)
    picked.sort(key=lambda x: (-x["gap"], x["vertical"]))
    return picked[:n]


def _slug(vertical: str, lane: str) -> str:
    return f"gap-{vertical}-{lane}"


def draft_text(vertical: str, lane: str, have: int, need: int) -> str:
    token, stake = STAKES.get(vertical, ("gap-cell",
                                         "This draft names the gap cell it was generated from."))
    slug = _slug(vertical, lane)
    path = f"capabilities/harnesses/{slug}.yaml"
    return (
        f"---\n"
        f"outcome: {lane}:\n"
        f"done_when:\n"
        f"  - file:{path}\n"
        f"  - grep:{path}:{token}\n"
        f"quality_floor: 0.6\n"
        f"---\n"
        f"\n"
        f"harness_id: {slug}\n"
        f"harness_name: {vertical} × {lane} gap draft\n"
        f"status: draft\n"
        f"source: requests.jsonl\n"
        f"vertical: {vertical}\n"
        f"lane: {lane}\n"
        f"coverage: {{have: {have}, need: {need}, gap: {need - have}}}\n"
        f"session_type: gap-fill-session\n"
        f"stake: |\n"
        f"  {stake}\n"
        f"identity_lock:\n"
        f"  startup_phrase: \"I am filling a measured gap, not inventing coverage.\"\n"
        f"gates:\n"
        f"  - id: G1\n"
        f"    requirement: \"Quote the requests.jsonl cell (vertical={vertical} lane={lane} have={have} need={need}) before writing any other artifact\"\n"
        f"    proof: \"Session log contains the cell verbatim\"\n"
        f"    failure_tier: halt\n"
        f"  - id: G2\n"
        f"    requirement: \"{stake}\"\n"
        f"    proof: \"The token {token} appears in the produced artifact AND in this harness body\"\n"
        f"    failure_tier: halt\n"
        f"  - id: G3\n"
        f"    requirement: \"Produce need-have = {need - have} concrete next assets (skill, hook, or command), each with a done_when that can go RED\"\n"
        f"    proof: \"A list of {need - have} paths under capabilities/ whose done_when is file: or grep: against something outside their own frontmatter\"\n"
        f"    failure_tier: halt\n"
        f"definition_of_done:\n"
        f"  - \"G1–G3 halt-green\"\n"
        f"  - \"This file remains a draft until a round graduates it\"\n"
        f"final_rule:\n"
        f"  - \"A gap harness that cannot fail is not a fill.\"\n"
        f"  - \"{token} is load-bearing — deleting it must redden done_when.\"\n"
    )


def write_gap_harnesses(repo, n: int = 8, apply: bool = True) -> dict:
    rows = rank_gaps(load_requests(repo), n=n)
    dest = Path(repo.root) / "capabilities" / "harnesses"
    dest.mkdir(parents=True, exist_ok=True)
    written, planned = [], []
    for r in rows:
        slug = _slug(r["vertical"], r["lane"])
        path = dest / f"{slug}.yaml"
        text = draft_text(r["vertical"], r["lane"], r["have"], r["need"])
        planned.append({"id": slug, "path": str(path.relative_to(repo.root)),
                        **{k: r[k] for k in ("vertical", "lane", "have", "need", "gap")}})
        if not apply:
            continue
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        path.write_text(text, encoding="utf-8")
        written.append(slug)
    return {"ok": True, "n": n, "apply": apply, "planned": planned,
            "written": written, "count": len(planned)}
