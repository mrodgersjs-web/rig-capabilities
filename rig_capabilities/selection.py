"""V53: informative-first selection for improvement rounds, with a declared budget.

`rounds.pick_candidates` ranks by weakest quality score. Weakest-first is the wrong
order for a *measurement* budget, for one reason: an asset whose checks have passed
every recorded run carries no information about whether an upgrade helped, because
nothing the round does can show up as a change. A candidate that has failed before,
or has never been exercised, is the only kind that can move. This is the
validation-task-selection result from Task-CoEvolve (arXiv 2608.20169) applied to the
asset library instead of a training pool: pick what you can learn from, spend a
declared number of evaluations, refuse to spend more.

Two more properties the papers insist on and RIG did not have:

  * a declared eval budget, recorded and enforced, so "we ran a round" cannot quietly
    mean "we ran everything";
  * held-out non-regression: an asset that gains a field while breaking a check that
    passed in every recorded run is not a graduation, it is a regression, and the
    round has to name it.

Pass history is read from .context/quality-runs/*.json — the files the done-test
runner already writes. No new state, no model, no network.
"""
from __future__ import annotations

import json
from pathlib import Path
QUALITY_RUNS = ".context/quality-runs"
STRATEGIES = ("informative", "weakest")
# Below this, a record is "decided": 4p(1-p) < 0.5 means p is outside roughly
# (0.15, 0.85), i.e. the check has settled. With nothing above the floor there is
# no information left to buy and informative ranking is not the ordering to run.
UNCERTAIN_FLOOR = 0.5


def check_history(repo, limit: int = 40) -> dict:
    """Per-asset pass history over the last `limit` quality runs.

    Returns id -> {"runs", "passes", "checks": {check_form: {"ok", "runs"}}}.
    Missing or unreadable history yields {} — reported downstream as "unproven",
    never as "passing".
    """
    root = Path(repo.root) / QUALITY_RUNS
    if not root.is_dir():
        return {}
    hist: dict = {}
    for p in sorted(root.glob("*.json"))[-limit:]:
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in doc.get("rows") or []:
            rid = row.get("id")
            if not rid:
                continue
            h = hist.setdefault(rid, {"runs": 0, "passes": 0, "checks": {}})
            h["runs"] += 1
            h["passes"] += 1 if row.get("pass") else 0
            for res in row.get("results") or []:
                form = res.get("form")
                if not form:
                    continue
                c = h["checks"].setdefault(form, {"ok": 0, "runs": 0})
                c["runs"] += 1
                c["ok"] += 1 if res.get("ok") else 0
    return hist


def informativeness(passes: int, runs: int) -> float:
    """How much a round can learn about this asset: 0..1, Laplace-smoothed.

    4*p*(1-p) is Bernoulli variance scaled to [0,1]: maximum at p=0.5 (the check
    flips), zero at p=0 or 1 (the outcome is already decided). A never-run asset
    smooths to p=0.5 and scores 1.0 — an unproven asset can genuinely go either way,
    and ranking it below a proven one would hide the risk.
    """
    p = (passes + 1) / (runs + 2)
    return 4.0 * p * (1.0 - p)


def scored_rows(repo, lane: str) -> list:
    """Every canonical asset in `lane` with score, history and information value."""
    from .lanes import load_overlay
    from .quality import check_asset
    from .taxonomy import classify
    ov = load_overlay(repo)
    hist = check_history(repo)
    rows = []
    for a in repo.load_index()["assets"]:
        if a["source"] != "canonical":
            continue
        # House lane resolution: the .lanes.json overlay wins, the keyword
        # classifier is the fallback. Inventing a second rule here would make the
        # round and the catalog disagree about which lane an asset is in.
        if lane and (ov.get(a["id"]) or classify(a)) != lane:
            continue
        q = check_asset(a)
        h = hist.get(a["id"], {"runs": 0, "passes": 0, "checks": {}})
        info = informativeness(h["passes"], h["runs"])
        need = (100.0 - float(q.get("score") or 0)) / 100.0
        rows.append({"id": a["id"], "kind": a["kind"], "source": a["source"],
                     "score": q["score"], "asset": a,
                     "runs": h["runs"], "passes": h["passes"],
                     "checks": h["checks"],
                     "informative": round(info, 4),
                     "value": round(need * info, 6),
                     "unproven": h["runs"] == 0,
                     "reason": ("unproven" if h["runs"] == 0 else
                                "flaky" if 0 < h["passes"] < h["runs"] else
                                "always-passes" if h["passes"] == h["runs"] else
                                "always-fails")})
    return rows


def _brief(r: dict, full: bool = True) -> dict:
    keys = ("id", "kind", "source", "score", "value", "informative", "runs",
            "passes", "unproven", "reason") if full else ("id", "score", "value",
                                                          "reason")
    return {k: r[k] for k in keys}


def select(repo, lane: str, n: int = 5, budget: int | None = None,
           strategy: str = "informative") -> dict:
    """Pick up to `n` assets, spending at most `budget` done-test evaluations.

    strategy="informative" orders by need x information; "weakest" keeps the original
    score-ascending order so an old round can still be reproduced.

    The budget is not advisory: candidates past it land in `deferred` with their
    value, so the next round can see what was skipped. `budget=None` means one
    evaluation per candidate (n evaluations), which keeps the old behaviour reachable
    without claiming the spend was unbounded.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy must be one of {STRATEGIES}, got {strategy!r}")
    rows = scored_rows(repo, lane)
    # A green estate has no uncertainty to buy: if nothing is flaky and nothing is
    # unproven, informative ranking degenerates to need-weighted weakest-first by
    # arithmetic and says nothing. Say which ordering actually ran.
    uncertain = [r for r in rows if r["informative"] >= UNCERTAIN_FLOOR]
    fallback = ""
    if strategy == "weakest" or not uncertain:
        rows.sort(key=lambda r: (r["score"], r["id"]))
        if strategy == "informative":
            fallback = "no-uncertain-candidates"
    else:
        rows.sort(key=lambda r: (-r["value"], r["id"]))
    limit = n if budget is None else max(0, min(n, budget))
    chosen, deferred = rows[:n][:limit], rows[:n][limit:]
    return {"strategy": strategy + "-first", "fallback": fallback,
            "uncertain_candidates": len(uncertain),
            "lane": lane, "eval_budget": budget, "eval_budget_effective": limit,
            "selected": [_brief(r) for r in chosen],
            "deferred": [_brief(r, full=False) for r in deferred],
            "rows_by_id": {r["id"]: r for r in rows}}


def regressed_checks(row: dict, results) -> list:
    """Checks that passed in every recorded run and are red now.

    Held-out non-regression: a round may add a field, it may not break a check the
    library has always seen green. Returns the offending check forms.
    """
    bad = []
    for res in results or []:
        form, ok = res.get("form"), res.get("ok")
        if ok is not False:
            continue
        seen = (row.get("checks") or {}).get(form) or {}
        if seen.get("runs", 0) > 0 and seen.get("ok") == seen.get("runs"):
            bad.append(form)
    return sorted(bad)
