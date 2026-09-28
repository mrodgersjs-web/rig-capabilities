#!/usr/bin/env python3
"""Build the App Studio inventory: every skill, agent, harness, loop and hook in the
estate that serves building, testing, shipping or operating a web or mobile app.

Two signals, fail-closed (CODE -> JEV, per jev-everywhere):
  1. CODE: keyword rules on name + description pick candidates and a fallback stage.
  2. JEV:  rubric app.inventory-fit (rig-s1gate) confirms membership and stage.

Decision per candidate:
  include   JEV primary_app_building noul > 0.9 (0.90 does not pass) and
            generic_agent_infra noul < 0.7
  exclude   JEV primary_app_building noul < 0.4
  review    anything between - listed by name, never silently included
  deferred  classifier unavailable or errored twice - never guessed

Stage: the JEV stage choice when its confidence > 0.9, else the CODE keyword stage,
else "cross-cutting". The family's own members (read from ../hierarchy.json) are
excluded so the inventory lists what the estate already had.

Usage:
  build_inventory.py [--no-jev] [--workers N] [--out DIR] [--limit N]
Writes <out>/inventory.json and <out>/inventory.md (default out: ../references).
Stdlib only. Exit 0 on success, 2 when zero candidates were found (a silent-empty
run is a bug, not a result).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
REPO = SKILL_DIR.parents[2]
HOME = Path.home()
GATE = REPO / "bin" / "rig-s1gate"
RUBRIC = "app.inventory-fit"
KINDS = ("skill", "agent", "harness", "loop", "hook")
# Not capabilities: exemplars, scraped creator cards, observation cells, intel notes.
EXCLUDED_SOURCES = {"great", "gtm-studio-corpus", "gtm-studio-examples", "obs-cells", "intel"}
_EXCERPTS: dict[str, str] = {}
SOURCE_RANK = ["canonical", "aside-user", "claude-skills", "claude-agents", "codex-skills",
               "codex-agents", "hermes-skills", "hermes-agents", "claude-hooks", "aside-builtin"]

APP_CORE = re.compile(
    r"\b(apps?|applications?|web ?apps?|mobile ?apps?|saas|full[- ]?stack|frontend|front-end|"
    r"backend|back-end|next\.?js|react native|react|expo|flutter|swift ?ui|ios|android|website|"
    r"landing pages?|vercel|netlify|supabase|firebase|pwa|ui components?|app store|play store)\b", re.I)
EXCLUDE = re.compile(
    r"\b(linkedin|instagram|tiktok|twitter|tweets?|newsletters?|podcasts?|resumes?|cover letters?|"
    r"job (search|applications?|hunt)|recruit(er|ing)|gtm|go-to-market|outreach|cold emails?|"
    r"prospect(ing|s)?|lead gen|sales calls?|google ads|unemployment|nil deals?|ideawake|eden\.so|"
    r"copywriting|music|songs?|lyrics)\b", re.I)
STAGES = {
    "intake-spec": r"\b(prd|product requirements?|specs?|specifications?|user stor(y|ies)|acceptance criteria|requirements|mvp|feature list|clone)\b",
    "architecture-stack": r"\b(architecture|tech stack|stack selection|system design|monorepo|project structure|boilerplate|starter kit)\b",
    "design-ux": r"\b(ui|ux|design systems?|figma|wireframes?|mockups?|components? library|tailwind|shadcn|typography|responsive|accessibility|a11y|wcag|dark mode|animations?|motion design)\b",
    "scaffold-setup": r"\b(scaffold(ing)?|bootstrap(ping)?|create-next-app|project setup|init(ialize)? (a |the )?(project|repo)|dev environment|env vars?|\.env)\b",
    "backend-data": r"\b(backend|back-end|apis?|rest|graphql|databases?|schemas?|migrations?|orm|prisma|drizzle|postgres(ql)?|sql|supabase|firebase|convex|neon|auth(entication)?|oauth|clerk|stripe|payments?|webhooks?|background jobs?|queues?|inngest|cron)\b",
    "web-frontend": r"\b(next\.?js|react|vue|svelte|nuxt|remix|astro|vite|frontend|front-end|web ?apps?|spa|ssr|pwa|html|css|typescript|javascript|websites?|landing pages?|pages? router|app router)\b",
    "mobile": r"\b(mobile|react native|expo|flutter|dart|swift|swiftui|ios|android|kotlin|jetpack|xcode|simulators?|testflight|app store|play store|eas)\b",
    "ai-features": r"\b(llms?|openai|gemini|rag|embeddings?|vector (db|store|search)|ai sdk|chatbots?|voice agents?|vapi|tts|speech|image generation|ai features?)\b",
    "verify-qa": r"\b(tests?|testing|tdd|e2e|end-to-end|playwright|cypress|jest|vitest|pytest|qa|regression|coverage|lint(ing)?|type ?check|code review|security|vulnerabilit(y|ies)|performance|lighthouse|web vitals|bugs?|debug(ging)?)\b",
    "ship-release": r"\b(deploy(ment|ing|s)?|vercel|netlify|cloudflare|docker|kubernetes|ci/?cd|github actions|releases?|app store|play store|testflight|domains?|dns|hosting|ship(ping)?)\b",
    "operate-learn": r"\b(observability|monitoring|sentry|logging|analytics|incidents?|postmortems?|maintenance|tech debt|changelogs?|uptime)\b",
}
STAGES = {k: re.compile(v, re.I) for k, v in STAGES.items()}
STAGE_ORDER = list(STAGES) + ["cross-cutting"]


def norm(name: str) -> str:
    n = name.lower().strip()
    n = re.sub(r"\.(md|toml|yaml|yml|sh|py|ts|json)$", "", n)
    n = re.sub(r"^agency-", "", n)
    return n


def frontmatter(p: Path) -> tuple[str, str]:
    try:
        t = p.read_text(errors="ignore")[:6000]
    except OSError:
        return "", ""
    m = re.match(r"---\n(.*?)\n---", t, re.S)
    name = desc = ""
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("\"'")
            elif line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip("\"'")
    return name, desc


def display_path(a: dict) -> str:
    """Repo-relative for canonical assets, ~/... for installed roots, and a skill's directory
    rather than its SKILL.md. Installed roots index `path` relative to the root, which is
    ambiguous on its own, so abs_path wins whenever it exists."""
    raw = a.get("abs_path") or a.get("path") or ""
    p = Path(raw) if raw.startswith("/") else REPO / raw
    if a.get("kind") == "skill" and p.name == "SKILL.md":
        p = p.parent
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        s = str(p)
        return "~/" + s[len(str(HOME)) + 1:] if s.startswith(str(HOME) + "/") else s


def fix_paths(rows: list[dict]) -> None:
    """Re-derive display paths for recorded rows from the index (render-from runs)."""
    idx = json.loads((REPO / ".index.json").read_text())["assets"]
    by = {}
    for a in idx:
        by.setdefault((a.get("kind"), (a.get("name") or "").lower(), a.get("source")), a)
    for r in rows:
        p = r.get("path") or ""
        if p.startswith(("/", "~/", "capabilities/")):
            continue
        a = by.get((r["kind"], (r.get("name") or "").lower(), r.get("source")))
        if a:
            r["path"] = display_path(a)


def asset_file(a: dict) -> Path | None:
    raw = a.get("abs_path") or a.get("path") or ""
    p = Path(raw) if raw.startswith("/") else REPO / raw
    if p.is_dir():
        p = p / "SKILL.md"
    return p if p.is_file() else None


def excerpt(a: dict, n: int = 1500) -> str:
    """The asset's own words: index text is thin (agency agents carry one-liners, harness,
    loop and hook rows carry none), so classification reads the file head."""
    key = str(a.get("abs_path") or a.get("path"))
    if key in _EXCERPTS:
        return _EXCERPTS[key]
    p = asset_file(a)
    txt = ""
    if p is not None:
        try:
            txt = p.read_bytes()[:6000].decode("utf-8", "ignore")
        except OSError:
            txt = ""
    txt = re.sub(r"^---\n", "", txt)
    txt = re.sub(r"\s+", " ", txt)[:n]
    _EXCERPTS[key] = txt
    return txt


def load_assets() -> list[dict]:
    idx = json.loads((REPO / ".index.json").read_text())["assets"]
    out = []
    for a in idx:
        if a.get("kind") not in KINDS or a.get("source") in EXCLUDED_SOURCES:
            continue
        name = a.get("name") or a.get("id") or ""
        if a["kind"] in ("hook", "harness", "loop") or name.startswith("!") or not name.strip():
            base = Path(a.get("path") or a.get("abs_path") or name).name
            a = {**a, "name": base if a["kind"] != "loop" else (name if not name.startswith("!") else base)}
        out.append(a)
    for root, src in ((HOME / ".aside/u/0/skills/user", "aside-user"),
                      (HOME / ".aside/u/0/skills/builtin", "aside-builtin")):
        if not root.is_dir():
            continue
        for p in sorted(root.glob("**/SKILL.md")):
            if any(part in {"references", "node_modules", "__pycache__"} for part in p.parts):
                continue
            n, d = frontmatter(p)
            out.append({"id": n or p.parent.name, "name": n or p.parent.name, "kind": "skill",
                        "source": src, "description": d, "path": str(p.parent),
                        "abs_path": str(p.parent), "tags": []})
    return out


def family_members() -> set[str]:
    h = SKILL_DIR / "hierarchy.json"
    if not h.is_file():
        return set()
    data = json.loads(h.read_text())
    names = set()
    for kind in data.get("tiers", {}).values():
        for tier in ("meta", "sub"):
            v = kind.get(tier)
            for e in (v if isinstance(v, list) else [v] if v else []):
                if e.get("new"):
                    names.add(norm(e["id"]))
    return names


def code_signal(a: dict) -> tuple[bool, str, int]:
    text = (f"{a.get('name','')} {a.get('description','')} {' '.join(a.get('tags') or [])} "
            f"{excerpt(a, 900)}")
    core = len(APP_CORE.findall(text))
    hits = {s: len(rx.findall(text)) for s, rx in STAGES.items()}
    total = sum(hits.values())
    if EXCLUDE.search(text) and core == 0:
        return False, "", 0
    distinct = sum(1 for v in hits.values() if v)
    # Small kinds skip the prefilter: 77 harnesses + 17 loops + 26 hooks are cheap to send
    # to JEV whole, and a keyword miss there drops real gates (s1gate-stage-gate, coding loop).
    cand = a.get("kind") in ("harness", "loop", "hook") or (core >= 1 and total >= 1) or distinct >= 2
    stage = max(hits, key=lambda s: hits[s]) if total else "cross-cutting"
    return cand, stage, core + total


def rank(src: str) -> int:
    return SOURCE_RANK.index(src) if src in SOURCE_RANK else len(SOURCE_RANK)


def jev(a: dict) -> dict:
    text = (f"Asset kind: {a['kind']}\nName: {a['name']}\nSource: {a['source']}\n"
            f"Description: {(a.get('description') or '')[:600]}\n"
            f"File excerpt: {excerpt(a, 1400)}")
    sha = hashlib.sha256(text.encode()).hexdigest()[:12]
    subject = f"inventory:{a['kind']}:{a['name']} sha={sha}"
    last = "no attempt"
    for _ in range(2):
        try:
            r = subprocess.run([sys.executable, str(GATE), "check", RUBRIC, "--text", text,
                                "--subject", subject, "--json"],
                               capture_output=True, text=True, timeout=90)
            d = json.loads(r.stdout)
            if d.get("error"):
                last = str(d["error"])[:160]
                continue
            ans = d["answers"]
            return {"noul": ans["primary_app_building"]["noul"],
                    "infra": ans["generic_agent_infra"]["noul"],
                    "stage": ans["stage"].get("choice"),
                    "stage_conf": ans["stage"].get("confidence"),
                    "decision_id": d.get("decision_id"), "sha": sha}
        except Exception as e:  # classifier unavailable -> DEFER, never guess
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return {"error": last, "sha": sha}


def decide(row: dict) -> None:
    j = row.get("jev") or {}
    if "noul" not in j:
        row["decision"] = "deferred"
    elif j["noul"] > 0.9 and j["infra"] < 0.7:
        row["decision"] = "include"
    elif j["noul"] < 0.4:
        row["decision"] = "exclude"
    else:
        row["decision"] = "review"
    if j.get("stage") and j.get("stage_conf", 0) > 0.9 and j["stage"] != "not-app-building":
        row["stage"], row["stage_by"] = j["stage"], "jev"
    else:
        row["stage"], row["stage_by"] = row["code_stage"], "code"


def md_row(r: dict) -> str:
    desc = re.sub(r"\s+", " ", (r.get("description") or "")).replace("|", "/")[:140]
    j = r.get("jev") or {}
    noul = f"{j['noul']:.2f}" if "noul" in j else "-"
    return f"| {r['name']} | {r['source']} | {desc} | {noul} | `{r['path']}` |"


def write_md(rows: list[dict], out: Path, meta: dict) -> None:
    L = ["# App Studio inventory (generated - do not hand-edit)", "",
         f"Generated by `scripts/build_inventory.py` from `.index.json` ({meta['index_count']} assets) "
         f"plus Aside skill roots. Rubric `{RUBRIC}`: include above 0.9, exclude below 0.4, "
         "review between, deferred when the classifier was unavailable.", "",
         "| kind | candidates | include | review | exclude | deferred |", "|---|---|---|---|---|---|"]
    for k in KINDS:
        c = Counter(r["decision"] for r in rows if r["kind"] == k)
        L.append(f"| {k} | {sum(c.values())} | {c['include']} | {c['review']} | {c['exclude']} | {c['deferred']} |")
    for k in KINDS:
        inc = [r for r in rows if r["kind"] == k and r["decision"] == "include"]
        if not inc:
            continue
        L += ["", f"## {k}s: included ({len(inc)})"]
        by = defaultdict(list)
        for r in inc:
            by[r["stage"]].append(r)
        for s in STAGE_ORDER:
            if not by.get(s):
                continue
            L += ["", f"### {s} ({len(by[s])})", "", "| name | source | one-liner | JEV | path |", "|---|---|---|---|---|"]
            L += [md_row(r) for r in sorted(by[s], key=lambda r: r["name"])]
    rev = [r for r in rows if r["decision"] in ("review", "deferred")]
    if rev:
        L += ["", f"## Review and deferred ({len(rev)}) - named, not included", "",
              "| kind | name | source | one-liner | JEV | path |", "|---|---|---|---|---|---|"]
        for r in sorted(rev, key=lambda r: (r["kind"], r["name"])):
            L.append(f"| {r['kind']} " + md_row(r))
    out.write_text("\n".join(L) + "\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-jev", action="store_true", help="CODE only; every candidate becomes deferred")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="classify only the first N candidates (smoke test)")
    ap.add_argument("--out", default=str(SKILL_DIR / "references"))
    ap.add_argument("--render-from", help="re-render outputs from a recorded inventory.json; no JEV calls")
    args = ap.parse_args(argv)

    if args.render_from:
        rec = json.loads(Path(args.render_from).read_text())
        fix_paths(rec["rows"])
        return write_outputs(rec["rows"], Path(args.out), rec["meta"])

    assets = load_assets()
    members = family_members()
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for a in assets:
        groups[(a["kind"], norm(a.get("name") or a.get("id") or ""))].append(a)

    rows = []
    for (kind, key), items in groups.items():
        if not key or key in members:
            continue
        items.sort(key=lambda a: rank(a.get("source", "")))
        best = items[0]
        cand, stage, score = code_signal(best)
        if not cand:
            continue
        rows.append({"kind": kind, "name": best.get("name") or best.get("id"), "id": best.get("id"),
                     "source": best.get("source"), "sources": sorted({i.get("source") for i in items}),
                     "path": display_path(best),
                     "description": (best.get("description") or "")[:600],
                     "code_stage": stage, "code_score": score})
    rows.sort(key=lambda r: (KINDS.index(r["kind"]), r["name"]))
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("ZERO candidates - refusing to write an empty inventory", file=sys.stderr)
        return 2

    if args.no_jev:
        for r in rows:
            r["jev"] = {"error": "--no-jev"}
    else:
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            for r, j in zip(rows, ex.map(jev, rows)):
                r["jev"] = j
    for r in rows:
        decide(r)

    meta = {"index_count": len(assets), "rubric": RUBRIC, "family_excluded": sorted(members)}
    return write_outputs(rows, Path(args.out), meta)


def write_outputs(rows: list[dict], out: Path, meta: dict) -> int:
    """Compact on disk: excluded rows keep their decision and JEV receipt, not their text."""
    out.mkdir(parents=True, exist_ok=True)
    slim = []
    for r in rows:
        if r["decision"] == "exclude":
            r = {k: r[k] for k in ("kind", "name", "source", "path", "decision", "stage", "stage_by", "jev") if k in r}
        slim.append(r)
    body = ",\n".join(json.dumps(r, sort_keys=True) for r in slim)
    (out / "inventory.json").write_text('{"meta": ' + json.dumps(meta, sort_keys=True) + ',\n"rows": [\n' + body + "\n]}\n")
    write_md(rows, out / "inventory.md", meta)
    c = Counter((r["kind"], r["decision"]) for r in rows)
    print(json.dumps({"assets_scanned": meta.get("index_count"), "candidates": len(rows),
                      "by_kind_decision": {f"{k}:{d}": n for (k, d), n in sorted(c.items())}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
