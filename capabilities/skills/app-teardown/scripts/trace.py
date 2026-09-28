#!/usr/bin/env python3
"""trace.py - one ledger row per thing we reverse-engineered, and a gate that fails until every
row has a build (or an explicit, reasoned decision) behind it.

Rows come from: a doc capability map (help center / marketing), phone captures (jev-phone runs),
and the builder's gap audit. Each row carries a status and evidence that the gate re-checks:

  OPEN      nothing decided yet
  TRIAGED   priority set (must / should / could)                 needs: priority
  PLANNED   assigned to a slice or ticket                         needs: ticket
  BUILT     code landed                                           needs: a commit that exists in the target repo
  VERIFIED  code landed and proven                                needs: commit + a test file or screen that exists
  EXISTS    the target app already had it                         needs: a file/test that exists in the target repo
  SKIP      deliberately not building                             needs: a reason (8+ chars)
  MAPPED    a screen or audit item covered by other rows          needs: covers=[ids]; done when all of those are done

Done = VERIFIED, EXISTS, SKIP, or MAPPED-with-all-covered-done.
Exit codes (coverage): 0 complete, 1 valid but incomplete, 2 invalid ledger or evidence.
Stdlib only. Jev (TypeSafe System One) is used by `link` to route rows to landed slices; its
answer is triage, never proof: a Jev-routed row lands as BUILT (commit evidence), not VERIFIED.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import subprocess
import sys
import urllib.request

STATUSES = ["OPEN", "TRIAGED", "PLANNED", "BUILT", "VERIFIED", "EXISTS", "SKIP", "MAPPED"]
DONE = {"VERIFIED", "EXISTS", "SKIP"}
PRIORITY = {"must": 0, "should": 1, "could": 2}


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ---- ledger io ---------------------------------------------------------------------------
def load(path: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if os.path.exists(path):
        with open(path) as f:
            for n, line in enumerate(f, 1):
                if line.strip():
                    r = json.loads(line)
                    if r["id"] in rows:
                        raise SystemExit(f"duplicate id {r['id']} at line {n}")
                    rows[r["id"]] = r
    return rows


def save(path: str, rows: dict[str, dict]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in rows.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def new_row(rid: str, **kw) -> dict:
    base = {"id": rid, "source_app": "", "target_app": "", "kind": "", "area": "", "item": "", "detail": "",
            "source_ref": "", "confidence": "", "status": "OPEN", "priority": None, "ticket": None,
            "evidence": [], "covers": [], "reason": None, "note": "", "updated": now(), "by": "import"}
    base.update(kw)
    return base


def upsert(rows: dict, row: dict) -> str:
    """Imports never overwrite a decision already made on a row; they only refresh text."""
    old = rows.get(row["id"])
    if old is None:
        rows[row["id"]] = row
        return "new"
    for k in ("item", "detail", "source_ref", "confidence", "area"):
        old[k] = row[k]
    return "kept"


# ---- importers ---------------------------------------------------------------------------
def cmd_import_map(a) -> int:
    """Markdown capability map: '# Section N: <App>' / '## N.M <Area>' / 5-column tables."""
    apps = dict(x.split("=", 1) for x in a.apps.split(","))          # "MacroFactor Workouts=macrofactor-workouts"
    prefix = dict(x.split("=", 1) for x in a.prefix.split(","))      # "MacroFactor Workouts=MFW"
    rows = load(a.ledger)
    app = area = None
    sec = sub = "0"
    k = 0
    stats = {"new": 0, "kept": 0}
    for line in open(a.map, encoding="utf-8"):
        m = re.match(r"^#\s+Section\s+(\d+):\s*(.+?)\s*$", line)
        if m:
            name = m.group(2).strip()
            app = name if name in apps else None
            sec, sub, k = m.group(1), "0", 0
            continue
        m = re.match(r"^##\s+(\d+)\.(\d+)\s+(.+?)\s*$", line)
        if m:
            sec, sub, area, k = m.group(1), m.group(2), m.group(3).strip(), 0
            continue
        if not app or not line.startswith("|") or re.match(r"^\|\s*-", line) or "Source URL" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        k += 1
        rid = f"{prefix[app]}-D{sec}.{sub}-{k:02d}"
        stats[upsert(rows, new_row(rid, source_app=apps[app], target_app=a.target, kind="doc",
                                   area=cells[0] or area, item=cells[1], detail=cells[2],
                                   source_ref=cells[3], confidence=cells[4]))] += 1
    save(a.ledger, rows)
    print(f"import-map: {stats['new']} new, {stats['kept']} kept -> {a.ledger} ({len(rows)} rows)")
    return 0


def cmd_import_audit(a) -> int:
    """Builder gap audit: '## Must items (1-17)' + '### N. Title - STATUS', and the D-xx table."""
    rows = load(a.ledger)
    prio, stats = None, {"new": 0, "kept": 0}
    for line in open(a.audit, encoding="utf-8"):
        m = re.match(r"^##\s+(Must|Should|Could)\s+items", line, re.I)
        if m:
            prio = m.group(1).lower()
            continue
        if re.match(r"^##\s", line) and not re.match(r"^##\s+(Must|Should|Could)", line, re.I):
            prio = None if not line.lower().startswith("## device") else prio
        m = re.match(r"^###\s+(\d+)\.\s+(.+?)\s+[—-]+\s+([A-Z][A-Z +()a-z0-9-]*)", line)
        if m and prio:
            n, title, state = int(m.group(1)), m.group(2), m.group(3).strip()
            r = new_row(f"{a.prefix}-A{prio[0].upper()}{n:02d}", source_app=a.app, target_app=a.target, kind="audit",
                        area=f"audit {prio}", item=title, detail=f"audit status: {state}", source_ref=a.audit,
                        confidence="builder audit", priority=prio, status="TRIAGED")
            stats[upsert(rows, r)] += 1
            continue
        m = re.match(r"^\|\s*(D-\d+)\s*\|\s*(.+?)\s*\|\s*\**([a-z]+)", line)
        if m:
            did, title, p = m.group(1), m.group(2), m.group(3).lower()
            p = p if p in PRIORITY else None
            r = new_row(f"{a.prefix}-{did}", source_app=a.app, target_app=a.target, kind="audit",
                        area="device-confirmed", item=re.sub(r"\*", "", title), detail="device capture addition",
                        source_ref=a.audit, confidence="on-device", priority=p,
                        status="TRIAGED" if p else "SKIP", reason=None if p else "map correction, not a build item")
            stats[upsert(rows, r)] += 1
    save(a.ledger, rows)
    print(f"import-audit: {stats['new']} new, {stats['kept']} kept -> {a.ledger} ({len(rows)} rows)")
    return 0


def cmd_import_run(a) -> int:
    """A jev-phone run: one row per captured screen (+ its controls when the run has a text tree)."""
    cat = json.load(open(os.path.join(a.run, "catalog.json")))
    rows = load(a.ledger)
    tag = a.tag or os.path.basename(os.path.normpath(a.run))[:24]
    stats = {"new": 0, "kept": 0}
    for s in cat["screens"]:
        pages = s.get("pages") or []
        lines = [ln for p in pages for ln in p.get("lines", [])]
        png = os.path.join(os.path.abspath(a.run), pages[0]["png"]) if pages else ""
        r = new_row(f"{a.prefix}-S-{tag}-{s['id']:03d}", source_app=a.app, target_app=a.target, kind="screen",
                    area=a.area or "screens", item=s.get("title") or f"screen {s['id']}",
                    detail=" | ".join(lines[:12])[:600], source_ref=png, confidence=cat["meta"].get("mode", ""),
                    note=f"viewer: {a.viewer}#{s['id']}" if a.viewer else "")
        stats[upsert(rows, r)] += 1
    for sk in cat.get("skips", []):  # controls the crawler saw but did not tap = settings/actions to rebuild
        if sk.get("verdict") in ("BLOCK", "MUTATE") and sk.get("label") and not re.fullmatch(r"[\d\W]+", sk["label"]):
            rid = f"{a.prefix}-C-{tag}-{sk['screen']:03d}-{re.sub(r'[^a-z0-9]+', '-', sk['label'].lower())[:32]}"
            r = new_row(rid, source_app=a.app, target_app=a.target, kind="control", area=a.area or "controls",
                        item=sk["label"], detail=f"{sk.get('type')} on screen {sk['screen']}: {sk.get('reason')}",
                        source_ref=f"{a.run}#screen-{sk['screen']}", confidence="on-device")
            stats[upsert(rows, r)] += 1
    save(a.ledger, rows)
    print(f"import-run: {stats['new']} new, {stats['kept']} kept -> {a.ledger} ({len(rows)} rows)")
    return 0


# ---- updates -----------------------------------------------------------------------------
def parse_evidence(items: list[str]) -> list[dict]:
    out = []
    for it in items or []:
        typ, _, ref = it.partition(":")
        if typ not in ("commit", "test", "file", "screen", "url", "jev") or not ref:
            raise SystemExit(f"bad --evidence '{it}' (use commit:<sha> test:<path> file:<path[:line]> screen:<png> url:<u>)")
        out.append({"type": typ, "ref": ref})
    return out


def cmd_set(a) -> int:
    rows = load(a.ledger)
    ids = [i for x in a.id for i in x.split(",") if i]
    missing = [i for i in ids if i not in rows]
    if missing:
        raise SystemExit(f"unknown ids: {missing[:10]}")
    for i in ids:
        r = rows[i]
        if a.status:
            if a.status not in STATUSES:
                raise SystemExit(f"status must be one of {STATUSES}")
            r["status"] = a.status
        if a.priority:
            r["priority"] = a.priority
        if a.ticket:
            r["ticket"] = a.ticket
        if a.reason:
            r["reason"] = a.reason
        if a.covers:
            r["covers"] = [c for c in a.covers.split(",") if c]
        if a.note:
            r["note"] = a.note
        r["evidence"] = r.get("evidence", []) + parse_evidence(a.evidence)
        r["updated"], r["by"] = now(), a.by
    save(a.ledger, rows)
    print(f"set: {len(ids)} row(s) -> {a.status or 'fields updated'}")
    return 0


# ---- the gate ----------------------------------------------------------------------------
def commit_exists(repo: str, sha: str, cache: dict) -> bool:
    if sha not in cache:
        r = subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True)
        cache[sha] = r.returncode == 0
    return cache[sha]


def path_exists(repo: str | None, ref: str, ledger_dir: str) -> bool:
    p = ref.split(":")[0] if not os.path.isabs(ref) else ref.rsplit(":", 1)[0] if re.search(r":\d+$", ref) else ref
    for base in ([repo] if repo else []) + [ledger_dir, ""]:
        if base is not None and os.path.exists(os.path.join(base, p) if base else p):
            return True
    return False


def validate(rows: dict, repo: str | None, ledger_dir: str) -> tuple[list[str], dict[str, bool]]:
    """Return (problems, done_by_id). Problems make the ledger invalid (exit 2)."""
    problems, cache = [], {}
    good = {}
    for r in rows.values():
        st, ev = r["status"], r.get("evidence") or []
        if st not in STATUSES:
            problems.append(f"{r['id']}: unknown status {st}")
            continue
        commits = [e for e in ev if e["type"] == "commit"]
        proofs = [e for e in ev if e["type"] in ("test", "screen")]
        files = [e for e in ev if e["type"] in ("file", "test")]
        if st in ("BUILT", "VERIFIED"):
            if not repo:
                problems.append(f"{r['id']}: {st} needs --repo to check its commit")
            elif not commits:
                problems.append(f"{r['id']}: {st} has no commit evidence")
            else:
                bad = [e["ref"] for e in commits if not commit_exists(repo, e["ref"], cache)]
                if bad:
                    problems.append(f"{r['id']}: commit(s) not in target repo: {bad}")
        if st == "VERIFIED":
            if not proofs:
                problems.append(f"{r['id']}: VERIFIED needs a test or screen as proof")
            elif not all(path_exists(repo, e["ref"], ledger_dir) for e in proofs):
                problems.append(f"{r['id']}: proof path missing: {[e['ref'] for e in proofs]}")
        if st == "EXISTS":
            if not files or not all(path_exists(repo, e["ref"], ledger_dir) for e in files):
                problems.append(f"{r['id']}: EXISTS needs file/test evidence that exists in the target repo")
        if st == "SKIP" and len((r.get("reason") or "").strip()) < 8:
            problems.append(f"{r['id']}: SKIP needs a reason")
        if st == "PLANNED" and not r.get("ticket"):
            problems.append(f"{r['id']}: PLANNED needs a ticket/slice")
        if st == "TRIAGED" and r.get("priority") not in PRIORITY:
            problems.append(f"{r['id']}: TRIAGED needs priority must/should/could")
        if st == "MAPPED":
            unknown = [c for c in r.get("covers") or [] if c not in rows]
            if not r.get("covers") or unknown:
                problems.append(f"{r['id']}: MAPPED needs covers=[existing ids] (unknown: {unknown[:5]})")
        good[r["id"]] = st in DONE

    def done(i: str, seen: frozenset = frozenset()) -> bool:
        r = rows[i]
        if r["status"] != "MAPPED":
            return good.get(i, False)
        if i in seen:
            return False
        return bool(r.get("covers")) and all(c in rows and done(c, seen | {i}) for c in r["covers"])

    return problems, {i: done(i) for i in rows}


def summarize(rows: dict, done: dict) -> dict:
    by_app: dict = {}
    for r in rows.values():
        app = by_app.setdefault(r["source_app"] or "?", {"rows": 0, "done": 0, "status": {}, "areas": {}})
        app["rows"] += 1
        app["done"] += done[r["id"]]
        app["status"][r["status"]] = app["status"].get(r["status"], 0) + 1
        ar = app["areas"].setdefault(r["area"] or "?", [0, 0])
        ar[0] += 1
        ar[1] += done[r["id"]]
    return by_app


def cmd_coverage(a) -> int:
    rows = load(a.ledger)
    if a.app:
        rows = {k: v for k, v in rows.items() if v["source_app"] == a.app}
    problems, done = validate(rows, a.repo, os.path.dirname(os.path.abspath(a.ledger)))
    s = summarize(rows, done)
    total, finished = len(rows), sum(done.values())
    unverified = sum(1 for r in rows.values() if r["status"] == "BUILT")
    out = {"rows": total, "done": finished, "open": total - finished, "built_unverified": unverified,
           "problems": problems, "apps": s}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"coverage: {finished}/{total} rows done ({(100 * finished // total) if total else 0}%), "
              f"{total - finished} not done, {unverified} built but unverified, {len(problems)} evidence problems")
        for app, v in s.items():
            st = ", ".join(f"{k} {n}" for k, n in sorted(v["status"].items(), key=lambda kv: STATUSES.index(kv[0])))
            print(f"  {app}: {v['done']}/{v['rows']} done  [{st}]")
        for p in problems[:25]:
            print(f"  INVALID {p}")
    if problems:
        return 2
    return 0 if finished == total else 1


# ---- Jev routing of rows to landed slices -------------------------------------------------
def _jev_key() -> str | None:
    k = os.environ.get("TYPESAFE_API_KEY")
    if k:
        return k
    try:
        return subprocess.run(["security", "find-generic-password", "-s", "com.rig.env.TYPESAFE_API_KEY", "-w"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        return None


def _jev(body: dict, key: str) -> dict:
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def cmd_link(a) -> int:
    """Ask Jev which landed slice (or NONE) implements each open row. p >= min_p and the commit
    exists -> BUILT with commit + jev evidence. Everything else is left as it was."""
    rows = load(a.ledger)
    greps = [f"--grep={g}" for g in a.grep]
    log = subprocess.run(["git", "-C", a.repo, "log", "--format=%h\t%s", *greps, "-n", "200"],
                         capture_output=True, text=True).stdout.strip().splitlines()
    slices = {}
    for ln in log:
        sha, subj = ln.split("\t", 1)
        slices[f"C_{sha}"] = subj[:220]
    if not slices:
        raise SystemExit(f"no commits matching --grep {a.grep!r} in {a.repo}")
    criteria = {k: v for k, v in slices.items()}
    criteria["NONE"] = "No listed commit implements this capability."
    key = _jev_key()
    if not key:
        print("BLOCKED: no TypeSafe key (keychain com.rig.env.TYPESAFE_API_KEY); nothing changed")
        return 3
    kinds = set(a.kinds.split(","))
    todo = [r for r in rows.values() if r["kind"] in kinds and r["status"] in ("OPEN", "TRIAGED")]
    moved, asked, decisions = 0, 0, []
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        qs = {f"r{j}": {"type": "choice", "criteria": criteria, "instructions": {
            "capability": {"area": r["area"], "name": r["item"], "behaviour": r["detail"][:400]},
            "rules": "Pick the commit whose change implements this capability in the target app. A commit that "
                     "only touches a neighbouring feature does not count. If none clearly does, pick NONE."}}
              for j, r in enumerate(chunk)}
        try:
            res = _jev({"model": "jev-latest", "state": {"target_app": a.target_desc}, "questions": qs}, key)
        except Exception as e:  # fail closed: rows stay as they were
            print(f"DEFERRED: Jev unavailable ({type(e).__name__}); {len(todo) - i} rows left untouched")
            break
        asked += len(chunk)
        for j, r in enumerate(chunk):
            ans = (res.get("answers") or {}).get(f"r{j}") or {}
            ch, p = ans.get("choice"), (ans.get("probabilities") or {}).get(ans.get("choice"), 0.0)
            ok = isinstance(p, (int, float)) and math.isfinite(p)
            decisions.append({"id": r["id"], "choice": ch, "p": round(p, 3) if ok else None})
            if ch and ch != "NONE" and ok and p >= a.min_p:
                sha = ch[2:]
                if commit_exists(a.repo, sha, {}):
                    r["status"] = "BUILT"
                    r["evidence"] = r.get("evidence", []) + [
                        {"type": "commit", "ref": sha}, {"type": "jev", "ref": f"link p={p:.2f} model={res.get('model')}"}]
                    r["note"] = (r.get("note") or "") + f" jev-routed to {sha}; verify before VERIFIED"
                    r["updated"], r["by"] = now(), "trace.link"
                    moved += 1
    save(a.ledger, rows)
    with open(a.ledger + ".link-decisions.json", "w") as f:
        json.dump({"at": now(), "min_p": a.min_p, "slices": slices, "decisions": decisions}, f, indent=1)
    print(f"link: asked Jev about {asked} rows against {len(slices)} commits; {moved} moved to BUILT (p >= {a.min_p})")
    return 0


# ---- views -------------------------------------------------------------------------------
def cmd_next(a) -> int:
    rows = load(a.ledger)
    open_rows = [r for r in rows.values() if r["status"] in ("OPEN", "TRIAGED", "PLANNED")]
    open_rows.sort(key=lambda r: (PRIORITY.get(r.get("priority") or "", 9), {"audit": 0, "doc": 1, "control": 2, "screen": 3}.get(r["kind"], 4), r["id"]))
    for r in open_rows[: a.n]:
        print(f"{r['id']:<22} {r['status']:<8} {(r.get('priority') or '-'):<6} {r['area'][:22]:<22} {r['item'][:70]}")
    print(f"({len(open_rows)} not built yet)")
    return 0


CHIP = {"OPEN": "#6e7681", "TRIAGED": "#9e6a03", "PLANNED": "#1f6feb", "BUILT": "#8957e5", "VERIFIED": "#238636",
        "EXISTS": "#2ea043", "SKIP": "#484f58", "MAPPED": "#0969da"}


def cmd_render(a) -> int:
    rows = load(a.ledger)
    problems, done = validate(rows, a.repo, os.path.dirname(os.path.abspath(a.ledger)))
    s = summarize(rows, done)
    os.makedirs(a.out, exist_ok=True)
    md = [f"# Trace ledger: {os.path.basename(a.ledger)}", "",
          f"{sum(done.values())}/{len(rows)} rows done. Done = VERIFIED, EXISTS, SKIP (reasoned), or MAPPED to done rows. "
          f"BUILT rows still need proof. Regenerate: `trace.py render`.", ""]
    for app, v in s.items():
        md += [f"## {app}: {v['done']}/{v['rows']} done", "", "| Area | Done | Rows |", "|---|---|---|"]
        md += [f"| {ar} | {d} | {n} |" for ar, (n, d) in sorted(v["areas"].items())]
        md.append("")
    md += ["## Rows", "", "| ID | Status | Pri | Area | Item | Evidence |", "|---|---|---|---|---|---|"]
    for r in rows.values():
        ev = ", ".join(f"{e['type']}:{e['ref'][:40]}" for e in r.get("evidence") or [])
        md.append(f"| {r['id']} | {r['status']} | {r.get('priority') or ''} | {r['area'][:30]} | "
                  f"{r['item'][:80].replace('|', '/')} | {ev or r.get('reason') or ''} |")
    with open(os.path.join(a.out, "TRACE.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    trs = []
    for r in rows.values():
        src = r["source_ref"]
        link = (f'<a href="{html.escape(src)}" target="_blank">source</a>' if src.startswith("http")
                else html.escape(os.path.basename(src)))
        note = r.get("note") or ""
        m = re.search(r"viewer: (\S+)", note)
        if m:
            link += f' · <a href="{html.escape(m.group(1))}" target="_blank">screen</a>'
        ev = " ".join(html.escape(f"{e['type']}:{e['ref'][:18]}") for e in r.get("evidence") or [])
        trs.append(f'<tr data-s="{r["status"]}" data-a="{html.escape(r["source_app"])}"><td>{html.escape(r["id"])}</td>'
                   f'<td><span class=c style="background:{CHIP.get(r["status"], "#333")}">{r["status"]}</span></td>'
                   f'<td>{html.escape(r.get("priority") or "")}</td><td>{html.escape(r["kind"])}</td>'
                   f'<td>{html.escape(r["area"][:40])}</td><td>{html.escape(r["item"][:110])}</td>'
                   f'<td class=d>{ev or html.escape(r.get("reason") or "")}</td><td>{link}</td></tr>')
    head = " ".join(f'<button onclick="f(\'{st}\')">{st} {sum(1 for r in rows.values() if r["status"] == st)}</button>'
                    for st in STATUSES if any(r["status"] == st for r in rows.values()))
    page = f"""<!doctype html><meta charset=utf-8><title>Trace: {sum(done.values())}/{len(rows)} done</title>
<style>body{{font:13px -apple-system,system-ui;background:#0d1117;color:#e6edf3;margin:16px}}table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid #30363d;padding:4px 6px;text-align:left;vertical-align:top}}.c{{padding:1px 6px;border-radius:8px;font-size:11px}}
.d{{color:#8b949e;font-size:11px}}a{{color:#58a6ff}}button{{background:#21262d;color:#e6edf3;border:1px solid #30363d;border-radius:6px;margin:2px;padding:3px 8px;cursor:pointer}}
input{{background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:5px;width:260px}}</style>
<h2>{sum(done.values())}/{len(rows)} reverse-engineered rows have a build or a decision behind them</h2>
<p>{head} <button onclick="f('')">all</button> <input id=q placeholder="search" oninput="g()"></p>
<table><tr><th>ID</th><th>Status</th><th>Pri</th><th>Kind</th><th>Area</th><th>Item</th><th>Evidence / reason</th><th>Source</th></tr>{''.join(trs)}</table>
<script>let S='';function f(s){{S=s;g()}}function g(){{const q=document.getElementById('q').value.toLowerCase();
document.querySelectorAll('tr[data-s]').forEach(t=>t.style.display=((!S||t.dataset.s===S)&&(!q||t.textContent.toLowerCase().includes(q)))?'':'none')}}</script>"""
    with open(os.path.join(a.out, "trace.html"), "w") as f:
        f.write(page)
    print(f"render: {os.path.join(a.out, 'TRACE.md')} + trace.html ({len(problems)} evidence problems)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("import-map"); s.add_argument("--ledger", required=True); s.add_argument("--map", required=True)
    s.add_argument("--apps", required=True); s.add_argument("--prefix", required=True); s.add_argument("--target", required=True)
    s.set_defaults(fn=cmd_import_map)
    s = sub.add_parser("import-audit"); s.add_argument("--ledger", required=True); s.add_argument("--audit", required=True)
    s.add_argument("--app", required=True); s.add_argument("--target", required=True); s.add_argument("--prefix", required=True)
    s.set_defaults(fn=cmd_import_audit)
    s = sub.add_parser("import-run"); s.add_argument("--ledger", required=True); s.add_argument("--run", required=True)
    s.add_argument("--app", required=True); s.add_argument("--target", required=True); s.add_argument("--prefix", required=True)
    s.add_argument("--tag"); s.add_argument("--area"); s.add_argument("--viewer", help="base URL of the run's index.html")
    s.set_defaults(fn=cmd_import_run)
    s = sub.add_parser("set"); s.add_argument("--ledger", required=True); s.add_argument("--id", required=True, action="append")
    s.add_argument("--status"); s.add_argument("--priority", choices=list(PRIORITY)); s.add_argument("--ticket")
    s.add_argument("--reason"); s.add_argument("--covers"); s.add_argument("--note"); s.add_argument("--by", default="manual")
    s.add_argument("--evidence", action="append", default=[]); s.set_defaults(fn=cmd_set)
    s = sub.add_parser("coverage"); s.add_argument("--ledger", required=True); s.add_argument("--repo")
    s.add_argument("--app"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_coverage)
    s = sub.add_parser("link"); s.add_argument("--ledger", required=True); s.add_argument("--repo", required=True)
    s.add_argument("--grep", required=True, action="append", help="commit subject pattern; repeat to OR")
    s.add_argument("--kinds", default="doc,audit")
    s.add_argument("--min-p", type=float, default=0.9); s.add_argument("--target-desc", default="the target app")
    s.set_defaults(fn=cmd_link)
    s = sub.add_parser("next"); s.add_argument("--ledger", required=True); s.add_argument("--n", type=int, default=20)
    s.set_defaults(fn=cmd_next)
    s = sub.add_parser("render"); s.add_argument("--ledger", required=True); s.add_argument("--out", required=True)
    s.add_argument("--repo"); s.set_defaults(fn=cmd_render)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
