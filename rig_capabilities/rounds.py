"""V16: 1000x round engine.

A round: pick the weakest canonical assets in a lane by quality score,
draft a deterministic upgrade (fill missing contract fields, seed a runnable
done_when), gate it with the V15 done-test runner, and graduate ONLY on green.
Graduation = the file's frontmatter actually changes + verified_on bumps;
Draft→Stable when score >= 90 after upgrade.

LLM/deviate drafting is out of scope here (V16 is the deterministic skeleton +
graduation gates; the skill-upgrades command drives LLM rounds through it).
Nothing is ever applied without the done-tests going green.
"""
from __future__ import annotations
import json
import re
import time
from pathlib import Path

from .quality import FIELDS, check_asset, migrate_frontmatter
from . import selection


def pick_candidates(repo, lane: str, n: int = 5) -> list:
    """Weakest canonicals in `lane`, ascending quality score."""
    from .lanes import load_overlay
    from .taxonomy import classify
    ov = load_overlay(repo)
    rows = []
    for a in repo.load_index()["assets"]:
        if a["source"] != "canonical":
            continue
        if (ov.get(a["id"]) or classify(a)) != lane:
            continue
        rows.append((check_asset(a)["score"], a))
    rows.sort(key=lambda t: t[0])
    return [{"id": a["id"], "kind": a["kind"], "source": a["source"],
             "score": s} for s, a in rows[:n]]


def _upgrade_plan(asset) -> dict:
    """Deterministic contract upgrade: fill missing fields; ensure at least one
    RUNNABLE done_when entry (template prose alone never graduates)."""
    q = asset.get("quality") or {}
    fpath = asset["path"]
    if "." not in fpath.rsplit("/", 1)[-1]:
        fpath = fpath.rstrip("/") + "/SKILL.md"
    plan = {}
    if not q.get("outcome"):
        from .taxonomy import classify
        plan["outcome"] = f"{classify(asset)}: {asset.get('description') or asset['id']}"
    if not q.get("done_when"):
        plan["done_when"] = [f"file:{fpath}"]
    else:
        entries = [str(e) for e in q["done_when"]]
        if not any(e.startswith(("cmd:", "file:", "grep:", "mcp:")) for e in entries):
            plan["add_done_when"] = [f"file:{fpath}"]
    if not q.get("quality_floor"):
        plan["quality_floor"] = 0.6
    if not q.get("great_example"):
        lane = (q.get("outcome") or "").split(":")[0].strip() or "misc"
        plan["great_example"] = f"examples/great/{lane}/{asset['id']}.md"
    return plan


def _append_done_when(p: Path, entries: list) -> bool:
    text = p.read_text()
    lines = text.splitlines()
    idx = next((i for i, ln in enumerate(lines[:80])
                if re.match(r"^(?:#\s*)?done_when\s*:", ln)), None)
    if idx is None:
        return False
    j = idx + 1
    prefix = "#" if lines[idx].lstrip().startswith("#") else ""
    while j < len(lines) and re.match(r"^(" + ("#\s*" if prefix else r"\s*") + r")-\s+", lines[j]):
        j += 1
    have = "".join(lines[idx:j])
    adds = [f"{prefix}  - {e}" for e in entries if e not in have]
    if not adds:
        return False
    lines[j:j] = adds
    p.write_text("\n".join(lines) + "\n")
    return True


def _apply(repo, asset, plan: dict) -> bool:
    p = Path(repo.root) / asset["path"]
    if p.is_dir():
        p = p / "SKILL.md"
    if not p.is_file():
        return False
    fields = {k: v for k, v in plan.items() if k != "add_done_when"}
    changed = False
    if fields:
        changed = migrate_frontmatter(p, fields) or changed
    if plan.get("add_done_when"):
        changed = _append_done_when(p, plan["add_done_when"]) or changed
    return changed


def run_round(repo, lane: str, n: int = 5, dry: bool = False,
              budget: int | None = None, strategy: str = "informative") -> dict:
    """One round: select -> deterministic contract upgrade -> done-test gate.

    `strategy="informative"` (default) ranks by need x Bernoulli variance so the
    round spends its evaluations where a change can be observed; "weakest" keeps the
    original score-ascending order so an old round stays reproducible. `budget` caps
    done-test evaluations and is enforced, not advisory.

    Graduation needs green done-tests AND no regressed held-out check. An upgrade
    applied with the budget spent is `applied-unevaluated` — on disk, never run, and
    not counted as graduated.
    """
    sel = selection.select(repo, lane, n, budget, strategy)
    rows = sel["rows_by_id"]
    limit = sel["eval_budget_effective"]
    actions, spent = [], 0
    for c in sel["selected"]:
        entry = {"id": c["id"], "before": c["score"], "value": c["value"],
                 "selection": c["reason"], "action": "no-op", "plan": None}
        asset = next(a for a in repo.load_index()["assets"]
                     if a["id"] == c["id"] and a["kind"] == c["kind"]
                     and a["source"] == c["source"])
        plan = _upgrade_plan(asset)
        entry["plan"] = plan
        if not plan:
            actions.append(entry)
            continue
        if dry:
            entry["action"] = "would-apply"
            actions.append(entry)
            continue
        entry["action"] = "applied" if _apply(repo, asset, plan) else "write-failed"
        if entry["action"] != "applied":
            actions.append(entry)
            continue
        if spent >= limit:
            entry["action"] = "applied-unevaluated"
            actions.append(entry)
            continue
        from .done_tests import run_asset
        repo.build_index()  # index must see the new frontmatter
        fresh = next(a for a in repo.load_index()["assets"]
                     if a["id"] == c["id"] and a["kind"] == c["kind"]
                     and a["source"] == c["source"])
        r = run_asset(repo, c["id"], source="canonical")
        spent += 1
        bad = selection.regressed_checks(rows[c["id"]], r.get("results"))
        entry.update({"after": check_asset(fresh)["score"],
                      "done_tests": r["pass"], "regressed_checks": bad,
                      "graduated": bool(r["pass"]) and not bad})
        if bad:
            entry["action"] = "applied-regressed"
        elif not r["pass"]:
            entry["action"] = "applied-but-red"  # honest; not graduated
        actions.append(entry)
    rep = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "lane": lane,
           "dry": dry, "strategy": sel["strategy"],
           "selection_fallback": sel.get("fallback", ""),
           "uncertain_candidates": sel.get("uncertain_candidates", 0),
           "eval_budget": sel["eval_budget"],
           "eval_budget_effective": limit, "eval_spent": spent,
           "candidates": len(sel["selected"]), "deferred": sel["deferred"],
           "actions": actions,
           "unevaluated": sum(1 for a in actions
                              if a["action"] == "applied-unevaluated"),
           "regressed": sum(1 for a in actions if a.get("regressed_checks")),
           "graduated": sum(1 for a in actions if a.get("graduated"))}
    out = Path(repo.root) / ".context" / "rounds"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{rep['ts'].replace(':', '')}-{lane}.json").write_text(
        json.dumps(rep, indent=1))
    return rep
