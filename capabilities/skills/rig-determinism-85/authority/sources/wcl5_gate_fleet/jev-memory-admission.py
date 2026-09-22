#!/usr/bin/env python3
"""jev-memory-admission -- System-1 admission gate for RIG Memory OS.

Sweeps recent memory items stuck in unclassified/candidate status (GBrain
shows hundreds), judges each once with the memory.admission rubric (Jev),
and appends an immutable admission_verdict event to the canonical plane:

  BLOCK    -> kind=activity/duplicate/sensitive: stays raw; never promoted.
  ESCALATE -> promote_value >= 2.5: listed in the daily admission brief for
              the promotion pipeline (frontier distillation, Gate-D stays with
              memory.promote -- this worker never promotes anything itself).
  PASS     -> left as candidate; not valuable enough to queue, not noise.

Policy lives here in code; Jev only answers the typed questions. Fail closed:
a Jev outage defers items (they re-queue next tick); nothing is dropped.
D85 status: A2 hybrid by rule (model in decision path) -- same certifier
ceiling as jev-vault-triage (see JEV_SYSTEM1_CASCADE_DOCTRINE.md); certified
NOT, live-proven instead, never promoted on its own authority.

State: ~/.rig/state/jev-admission/{seen.json,verdicts.jsonl,lock}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _vault():
    return Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/rig128gb/Documents/JakeStudio")).expanduser()

def _state():
    return Path(os.environ.get("JEVA_STATE_DIR", str(Path.home().joinpath(".rig/state/jev-admission"))))

def _seen():
    return _state().joinpath("seen.json")

def _ledger():
    return _state().joinpath("verdicts.jsonl")

def _lock():
    return _state().joinpath("lock")

def _memory_cli():
    return Path.home().joinpath("bin/rig-memory-os")

def _s1gate_cli():
    return Path("/Users/rig128gb/Developer/rig-capabilities/bin/rig-s1gate")

def _secrets_env():
    return Path.home().joinpath(".rig-secrets/typesafe.env")

def _secret_patterns():
    _p0 = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", 16)
    _p1 = re.compile(r"(?i)\b(authorization)\b\s*[:=]\s*bearer\s+[^\s`\x27\x22]+")
    _p2 = re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}")
    _p3 = re.compile(r"(?i)\b(api[_-]?key|token|secret|password|authorization|bearer)\b\s*[:=]\s*[^\s`\x27\x22]+")
    _p4 = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")
    _p5 = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")
    def apply(text):
        _r0 = _p0.sub("[REDACTED_SECRET_BLOCK]", text)
        _r1 = _p1.sub(r"\g<1>=[REDACTED]", _r0)
        _r2 = _p2.sub(r"\g<1>=[REDACTED]", _r1)
        _r3 = _p3.sub(r"\g<1>=[REDACTED]", _r2)
        _r4 = _p4.sub("[REDACTED_SECRET_BLOCK]", _r3)
        return _p5.sub("[REDACTED_SECRET_BLOCK]", _r4)
    return apply

def redact(text: str) -> str:
    return _redact_chain(text)


def _redact_chain(text: str) -> str:
    return _secret_patterns()(text)

def ensure_key() -> None:
    return [os.environ.setdefault(k, v) for k, v in re.findall(r'\s*(?:export\s+)?([A-Z_]+)=(\S+)', _secrets_env().read_text() if _secrets_env().is_file() else '')]


def cli_json(cmd: list, stdin: str = None, timeout: int = 45) -> tuple:
    try:
        r = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as exc:  # noqa: BLE001 -- provider trouble is a defer, never a guess
        return 4, "", str(exc)[:200]


def load_seen() -> dict:
    if _seen().is_file():
        try:
            return json.loads(_seen().read_text())
        except ValueError:
            pass
    return {}


def state_text(item: dict) -> str:
    content = item.get("content")
    body = json.dumps(content, ensure_ascii=False, sort_keys=True) if isinstance(content, (dict, list)) else str(content)
    return redact(
        f"status={item.get('status')} memory_type={item.get('memory_type')} "
        f"source_type={item.get('source_type')} writer={item.get('writer')} "
        f"provenance={json.dumps(item.get('provenance') or [])[:200]}\n{body[:2500]}"
    )


def verdict_event(rec: dict) -> None:
    payload = {
        "run_id": f"jev-memory-admission-{dt.date.today():%Y%m%d}",
        "mission_id": "memory-admission-gate",
        "event_type": rec.get("event_type") or "memory.admission_verdict",
        "occurred_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "sensitivity": "internal",
        "payload": rec,
        "idempotency_key": f"{rec.get('item_id') or ('funnel:' + str(rec.get('day')))}:admission:v1",
    }
    rc, out, _ = cli_json([str(_memory_cli()), "call", "memory.record_event", "--input", json.dumps(payload)], timeout=30)
    rec["event_logged"] = rc == 0


def _kw():
    return ["youtube", "recall", "rig", "agent", "memory", "design", "revenue", "gtm", "doctrine",
            "fitness", "finance", "legal", "manufacturing", "healthcare", "construction", "email",
            "linkedin", "calendar", "trading", "research"]


def knowledge_page(limit: int) -> list:
    # The real backlog is knowledge-plane items stuck source_status=unclassified
    # (thousands). The front door offers NO exhaustive listing: search_knowledge
    # returns top-<=10 relevance hits per query and offset/next_offset on items
    # pages that document's CONTENT, not the result list. Filed upstream as a
    # capacity_request event. What IS reachable: rotate the word list one query
    # per tick (20h full cycle), take each word's head hits, dedupe by
    # content_sha256 via the seen cursor, re-walk as the corpus shifts. Failures
    # stay silent-safe: empty page, cursor still advances so one bad word
    # cannot wedge the rotation.
    p = _state().joinpath("kq.json")
    kq = {"word": 0}
    if p.is_file():
        try:
            loaded = json.loads(p.read_text())
            if isinstance(loaded, dict) and "word" in loaded:
                kq = loaded
        except ValueError:
            pass
    body = {"query": _kw()[int(kq["word"]) % len(_kw())], "limit": max(1, min(10, limit))}
    rc, out, _ = cli_json([str(_memory_cli()), "call", "memory.search_knowledge", "--input", json.dumps(body)], timeout=90)
    kq["word"] = int(kq["word"]) + 1
    _state().joinpath("kq.json").write_text(json.dumps(kq))
    if rc != 0:
        return []
    try:
        d = json.loads(out)
    except ValueError:
        return []
    items = d.get("items") or []
    for it in items:
        it["id"] = "k:" + (it.get("content_sha256") or it.get("reference") or "")[:64]
        it["status"] = it.get("source_status")
        if not isinstance(it.get("content"), str):
            it["content"] = json.dumps(it.get("content"), ensure_ascii=False)
    return items


def tick(args) -> int:
    seen = load_seen()
    # Page events by ISO cursor (after = oldest learned_at from previous page).
    # Resets when the page comes back short -- the queue has caught up to head.
    cursor_path = _state().joinpath("cursor.json")
    cur = {}
    if cursor_path.is_file():
        try:
            cur = json.loads(cursor_path.read_text())
        except ValueError:
            cur = {}
    if not isinstance(cur, dict):
        cur = {}
    req_body = {"limit": min(100, args.scan)}
    if cur.get("after"):
        req_body["after"] = cur["after"]
    rc, out, err = cli_json([str(_memory_cli()), "call", "memory.recent", "--input", json.dumps(req_body)], timeout=30)
    if rc != 0:
        print(f"jev-memory-admission: memory.recent failed rc={rc}: {err[:160]}", file=sys.stderr)
        return 1
    try:
        items = json.loads(out)
    except ValueError:
        print("jev-memory-admission: memory.recent returned non-JSON", file=sys.stderr)
        return 1
    # Persist cursor: oldest learned_at of this page if full, else clear (drained).
    if items and len(items) >= min(100, args.scan):
        try:
            cursor_path.write_text(json.dumps({"after": items[-1]["learned_at"]}))
        except (OSError, KeyError):
            pass
    elif cursor_path.is_file():
        cursor_path.unlink()
    half = max(1, args.limit // 2)
    items = items + knowledge_page(half)
    fresh = [i for i in items if i.get("status") in ("unclassified", "candidate") and i.get("id") not in seen]
    fresh = fresh[:args.limit]
    if not fresh:
        if not args.quiet:
            print("jev-memory-admission: nothing new to admit-gate")
        return 0
    escalate_ids = []
    errors = 0
    for item in fresh:
        rc, out, err = cli_json([str(_s1gate_cli()), "check", "memory.admission", "--stdin", "--json"], stdin=state_text(item), timeout=45)
        try:
            res = json.loads(out)
        except ValueError:
            errors += 1
            continue  # fail closed: deferred, id stays unseen
        if res.get("error") or not res.get("answers"):
            errors += 1
            continue
        a = res.get("answers") or {}
        rec = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "item_id": item["id"],
            "status_in": item.get("status"),
            "verdict": res.get("verdict"),
            "kind": (a.get("kind") or {}).get("choice"),
            "promote_value": round(float((a.get("promote_value") or {}).get("score", 0)), 2),
            "is_duplicate": round(float((a.get("is_duplicate") or {}).get("noul", 0)), 2),
            "evidence_anchored": round(float((a.get("evidence_anchored") or {}).get("noul", 0)), 2),
            "decision_id": res.get("decision_id"),
        }
        seen[item["id"]] = rec["verdict"]
        if not args.dry_run:
            verdict_event(rec)
            with _ledger().open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
            if rec["verdict"] == "ESCALATE":
                escalate_ids.append(f"{item['id']} pv={rec['promote_value']} kind={rec['kind']}")
            if not args.quiet:
                print("%s %-9s pv=%.1f kind=%s" % (item["id"][:8], rec["verdict"], rec["promote_value"], rec["kind"]))
    if not args.dry_run:
        _state().joinpath("seen.json").write_text(json.dumps(dict(list(seen.items())[-5000:])))
        if escalate_ids:
            brief = _vault().joinpath("Memory", "Admission", f"{dt.date.today():%Y-%m-%d}.md")
            brief.parent.mkdir(parents=True, exist_ok=True)
            with brief.open("a", encoding="utf-8") as f:
                f.write("\n## %s — %d admission escalations\n" % (dt.datetime.now().strftime("%H:%M"), len(escalate_ids)))
                for line in escalate_ids:
                    f.write("- `%s`\n" % line)
    return 1 if errors == len(fresh) else 0


def funnel() -> None:
    # Outcome metric (once/day): the judge's own funnel -- verdict counts and kind
    # mix over today+yesterday, written as a canonical event so promotion data can
    # later be joined to it (proposed -> verdict -> promoted is the loop's KPI).
    # Ledger ts values are UTC; window dates must be UTC too or nothing matches.
    today = f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d}"
    marker = _state().joinpath("funnel.done")
    if marker.is_file() and marker.read_text().strip() == today:
        return
    counts: dict = {}
    kinds: dict = {}
    yesterday = f"{dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1):%Y-%m-%d}"
    for line in _ledger().read_text().splitlines():
        r = json.loads(line)
        if r["ts"].startswith(today) or r["ts"].startswith(yesterday):
            counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
            kinds[r.get("kind") or "?"] = kinds.get(r.get("kind") or "?", 0) + 1
    if not counts:
        return
    rec = {"event_type": "memory.admission_funnel", "day": today, "window": "today+yesterday",
           "verdicts": counts, "kinds": kinds,
           "escalation_brief": str(_vault().joinpath("Memory", "Admission", f"{today}.md"))}
    verdict_event(rec)
    marker.write_text(today)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Jev admission gate for Memory OS candidate/unclassified items")
    ap.add_argument("--scan", type=int, default=40, help="recent items to pull from memory.recent")
    ap.add_argument("--limit", type=int, default=25, help="max items to judge this tick")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _state().mkdir(parents=True, exist_ok=True)
    if _lock().exists():
        pid = _lock().joinpath("pid").read_text().strip() if _lock().joinpath("pid").is_file() else ""
        if pid.isdigit():
            try:
                os.kill(int(pid), 0)
            except OSError:
                shutil.rmtree(_lock(), ignore_errors=True)
    try:
        _lock().mkdir()
    except FileExistsError:
        return 0
    _lock().joinpath("pid").write_text(str(os.getpid()))
    try:
        ensure_key()
        rc = tick(args)
        if not args.dry_run:
            funnel()  # outcome metric fires on idle ticks too; self-guarded to 1/day
        return rc
    finally:
        _lock().joinpath("pid").unlink(missing_ok=True)
        _lock().rmdir()

if __name__ == "__main__":
    raise SystemExit(main())
