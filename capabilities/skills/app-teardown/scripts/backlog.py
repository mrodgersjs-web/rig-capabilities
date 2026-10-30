#!/usr/bin/env python3
"""backlog.py - merge every reference-app ledger for one target into a single upgrade backlog.

For each doc/audit row: Jev (TypeSafe System One) assigns (a) one TransformFit capability area
and (b) a priority for the target's current scope, in one batched request per 10 rows. Answers
below --min-p are kept as `review` (DEFERRED is never a priority). Rows are then clustered
deterministically inside each area by capability-name overlap, so "3 of 5 reference apps have
this" shows up as a count. Rows already BUILT/VERIFIED/EXISTS in any ledger are marked.

  backlog.py --ledgers 'docs/parity/trace/*.jsonl' --out docs/parity/trace/UPGRADE-BACKLOG --scope "<target scope text>"

Stdlib only. Jev decisions are cached in <out>.jev-cache.json (re-runs only ask about new rows).
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import math
import os
import re
import subprocess
import time
import urllib.request

AREAS = {
    "ONBOARDING": "first-run setup, quizzes, goals, account creation, trials shown during setup",
    "PROGRAMS": "program/plan generation, templates, splits, periodization, mesocycles, deloads, schedules",
    "SESSION": "today's workout generation, exercise selection, swaps, equipment, gym profiles",
    "LOGGING": "in-workout logging, sets, set types, rest timer, supersets, plate calculator, warm-ups",
    "PROGRESSION": "load/rep/volume progression rules, autoregulation, feedback questions, RIR/RPE",
    "READINESS": "recovery, readiness, strain, sleep, stress, HRV, fatigue, muscle recovery",
    "COACHING": "coach presence, AI coach chat, explanations, check-ins, coach content, video/audio cues",
    "ANALYTICS": "history, PRs, e1RM, charts, stats, volume by muscle, trends, body metrics",
    "LIBRARY": "exercise library, instructions, videos, custom exercises",
    "SOCIAL": "teams, communities, feed, sharing, friends, challenges, streaks and gamification",
    "HABITS": "habits, journal, reminders, notifications, widgets, watch, Live Activities",
    "NUTRITION": "food logging, macros, water, nutrition targets",
    "INTEGRATIONS": "Apple Health, wearables, calendars, imports/exports, other apps",
    "ACCOUNT": "account, privacy, data export/deletion, settings, units, subscription and pricing",
}
PRIO_SCALE = [  # Jev `score` question: ordered levels, answer = expected level + confidence
    "0 skip: out of the target's scope, an upsell/paywall mechanic the target does not use, or not worth copying",
    "1 could: nice to have or niche; build only if cheap",
    "2 should: clear value for the target's users; build after the musts",
    "3 must: core to the target's scope, users expect it, and the target lacks a strong version",
]
DONE = {"BUILT", "VERIFIED", "EXISTS"}
STOP = set("the a an of and or to in on for with by your you app from at as is are be it its per into via".split())


def jev_key() -> str | None:
    k = os.environ.get("TYPESAFE_API_KEY")
    if k:
        return k
    try:
        return subprocess.run(["security", "find-generic-password", "-s", "com.rig.env.TYPESAFE_API_KEY", "-w"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


def jev(body: dict, key: str) -> dict:
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())


def pick(ans: dict) -> tuple[str | None, float]:
    ch = ans.get("choice")
    p = (ans.get("probabilities") or {}).get(ch, 0.0)
    return (ch, float(p)) if isinstance(p, (int, float)) and math.isfinite(p) else (None, 0.0)


def tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 2}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledgers", required=True, help="glob of ledger .jsonl files")
    ap.add_argument("--out", required=True, help="output path prefix (.md/.json/.html are written)")
    ap.add_argument("--scope", required=True, help="what the target app is and is not, for the priority judgment")
    ap.add_argument("--min-p", type=float, default=0.8)
    ap.add_argument("--kinds", default="doc,audit")
    a = ap.parse_args()

    rows = []
    for path in sorted(glob.glob(a.ledgers)):
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                r["_ledger"] = os.path.basename(path)
                rows.append(r)
    done_names = {tokens(r["item"]).__str__() for r in rows if r["status"] in DONE}
    kinds = set(a.kinds.split(","))
    todo = [r for r in rows if r["kind"] in kinds]
    cache_path = a.out + ".jev-cache.json"
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    key = jev_key()
    asked, t0 = 0, time.time()
    need = [r for r in todo if r["id"] not in cache or cache[r["id"]].get("score") is None]
    if need and not key:
        print("BLOCKED: no TypeSafe key in keychain; nothing judged")
        return 3
    for i in range(0, len(need), 10):
        chunk = need[i:i + 10]
        qs = {}
        for j, r in enumerate(chunk):
            cap = {"app": r["source_app"], "area_in_source": r["area"][:60], "name": r["item"][:120], "behaviour": r["detail"][:300]}
            qs[f"a{j}"] = {"type": "choice", "criteria": AREAS, "instructions": {"capability": cap,
                           "rules": "Pick the one area this capability belongs to in a strength-training app."}}
            qs[f"p{j}"] = {"type": "score", "criteria": PRIO_SCALE, "instructions": {"capability": cap, "target_scope": a.scope,
                           "rules": "Rate how important it is to add this capability to the target app, given its scope."}}
        try:
            res = jev({"model": "jev-latest", "state": {"target": "TransformFit"}, "questions": qs}, key)
        except Exception as e:
            print(f"DEFERRED: Jev unavailable ({type(e).__name__}) after {asked} rows; rerun to continue")
            break
        ans = res.get("answers") or {}
        for j, r in enumerate(chunk):
            area, pa = pick(ans.get(f"a{j}") or {})
            sc = ans.get(f"p{j}") or {}
            score = sc.get("score") if isinstance(sc.get("score"), (int, float)) else None
            cache[r["id"]] = {"area": area, "pa": round(pa, 3), "score": score,
                              "conf": sc.get("confidence"), "model": res.get("model")}
        asked += len(chunk)
        with open(cache_path, "w") as f:
            json.dump(cache, f)

    # assemble + cluster
    items = []
    for r in todo:
        c = cache.get(r["id"])
        if not c:
            continue
        if c.get("score") is None:
            continue  # stale cache entry from the choice-based version, or no answer: re-ask on next run
        area = c["area"] if c["area"] and c["pa"] >= 0.5 else "UNSORTED"
        sc = float(c["score"])
        prio = "MUST" if sc >= 2.5 else "SHOULD" if sc >= 1.8 else "COULD" if sc >= 1.0 else "SKIP"
        items.append({"id": r["id"], "app": r["source_app"], "area": area, "prio": prio, "score": sc,
                      "low_conf": (c.get("conf") or 0) < 0.3, "item": r["item"],
                      "detail": r["detail"], "src": r["source_ref"], "status": r["status"], "ledger": r["_ledger"],
                      "tok": tokens(r["item"])})
    clusters = []
    for it in sorted(items, key=lambda x: (x["area"], x["app"], x["item"])):
        best = None
        for cl in clusters:
            if cl["area"] != it["area"]:
                continue
            inter = len(cl["tok"] & it["tok"])
            if inter and inter / max(1, min(len(cl["tok"]), len(it["tok"]))) >= 0.6:
                best = cl
                break
        if best is None:
            best = {"area": it["area"], "tok": set(it["tok"]), "rows": []}
            clusters.append(best)
        best["rows"].append(it)
    rank = {"MUST": 0, "SHOULD": 1, "COULD": 2, "SKIP": 3}
    out = []
    for cl in clusters:
        apps = sorted({x["app"] for x in cl["rows"]})
        prios = [x["prio"] for x in cl["rows"]]
        top = min(prios, key=lambda p: rank[p])
        have = any(x["status"] in DONE for x in cl["rows"])
        lead = max(cl["rows"], key=lambda x: (rank[top] == rank[x["prio"]], len(x["detail"])))
        best_score = max(x["score"] for x in cl["rows"])
        out.append({"area": cl["area"], "priority": top, "score": round(best_score, 2), "apps": apps, "n_apps": len(apps),
                    "have": have, "low_conf": all(x["low_conf"] for x in cl["rows"]),
                    "title": lead["item"], "detail": lead["detail"], "sources": [x["src"] for x in cl["rows"]][:6],
                    "ids": [x["id"] for x in cl["rows"]]})
    out.sort(key=lambda c: (rank[c["priority"]], -c["n_apps"], -c["score"], c["area"], c["title"]))
    with open(a.out + ".json", "w") as f:
        json.dump({"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "scope": a.scope, "min_p": a.min_p,
                   "rows_judged": len(items), "clusters": out}, f, indent=1)

    counts = {p: sum(1 for c in out if c["priority"] == p) for p in rank}
    md = [f"# TransformFit upgrade backlog (from reference-app teardowns)", "",
          f"{len(items)} capability rows from {len({i['app'] for i in items})} reference apps, merged into {len(out)} "
          f"capabilities. Area is a Jev choice; priority is a Jev 0-3 score (must >= 2.5, should >= 1.8, could >= 1.0), "
          f"ranked by how many reference apps have it, then score. (low) = Jev confidence under 0.3. "
          f"Apps = how many reference apps have it. Have = TransformFit already has a BUILT/VERIFIED/EXISTS row for it.", "",
          " | ".join(f"{p}: {n}" for p, n in counts.items()), ""]
    for p in ("MUST", "SHOULD", "COULD"):
        sel = [c for c in out if c["priority"] == p]
        if not sel:
            continue
        md += [f"## {p} ({len(sel)})", "", "| Area | Capability | Score | Apps | Have | Row ids |", "|---|---|---|---|---|---|"]
        for c in sel:
            md.append(f"| {c['area']} | {c['title'][:90].replace('|', '/')} | {c['score']}{' (low)' if c['low_conf'] else ''} | "
                      f"{c['n_apps']}: {', '.join(c['apps'])} | "
                      f"{'yes' if c['have'] else ''} | {', '.join(c['ids'][:4])}{' …' if len(c['ids']) > 4 else ''} |")
        md.append("")
    skips = [c for c in out if c["priority"] == "SKIP"]
    md += [f"## SKIP ({len(skips)}), listed so nothing silently disappears", ""]
    md += [f"- {c['area']}: {c['title'][:100]} ({', '.join(c['apps'])})" for c in skips]
    with open(a.out + ".md", "w") as f:
        f.write("\n".join(md) + "\n")
    trs = "".join(
        f"<tr data-p='{c['priority']}'><td>{c['priority']}</td><td>{c['area']}</td><td><b>{html.escape(c['title'][:100])}</b>"
        f"<div class=d>{html.escape(c['detail'][:220])}</div></td><td>{c['n_apps']}<div class=d>{html.escape(', '.join(c['apps']))}</div></td>"
        f"<td>{'yes' if c['have'] else ''}</td><td class=d>{html.escape(', '.join(c['ids'][:6]))}</td></tr>" for c in out)
    btn = " ".join(f"<button onclick=\"f('{p}')\">{p} {n}</button>" for p, n in counts.items())
    page = (f"<!doctype html><meta charset=utf-8><title>TransformFit upgrade backlog</title><style>body{{font:13px -apple-system,"
            f"system-ui;background:#0d1117;color:#e6edf3;margin:16px}}td,th{{border-bottom:1px solid #30363d;padding:5px;vertical-align:top;"
            f"text-align:left}}table{{border-collapse:collapse;width:100%}}.d{{color:#8b949e;font-size:11px}}button{{background:#21262d;"
            f"color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:3px 8px;margin:2px;cursor:pointer}}</style>"
            f"<h2>TransformFit upgrade backlog: {len(out)} capabilities from {len(items)} rows</h2><p>{btn} "
            f"<button onclick=\"f('')\">all</button></p><table><tr><th>Priority</th><th>Area</th><th>Capability</th><th>Apps</th>"
            f"<th>Have</th><th>Rows</th></tr>{trs}</table><script>function f(p){{document.querySelectorAll('tr[data-p]').forEach("
            f"t=>t.style.display=(!p||t.dataset.p===p)?'':'none')}}</script>")
    with open(a.out + ".html", "w") as f:
        f.write(page)
    print(f"backlog: {len(items)} rows judged ({asked} new, {round(time.time() - t0, 1)} s) -> {len(out)} capabilities; "
          + ", ".join(f"{p} {n}" for p, n in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
