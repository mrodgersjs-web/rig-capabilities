#!/usr/bin/env python3
"""jev-vault-triage -- Jev System-1 cascade for the JakeStudio Obsidian vault.

Drops land in Inbox/ (or --folder). Every ~100ms a note is judged by the
vault.triage rubric (TypeSafe Jev via the rig-s1gate CLI, whose exit codes are
the contract) and routed:

  PASS      -> frontmatter tagged, file moved to its destination folder,
               one memory.record_event for Memory OS / GBrain. No LLM call.
  ESCALATE  -> moved to Inbox/_needs-reasoning/, appended to the escalation
               queue jsonl. A frontier agent distills from there.
  BLOCK     -> noise: Inbox/_archive/ ; credentials: Inbox/_quarantine/
               (quarantine records path + hash only, never content).

Policy lives HERE in code; Jev only supplies the typed judgments. Fail-closed:
if Jev is down the file stays untouched for the next tick.

State: ~/.rig/state/jev-triage/{triage.jsonl,escalations.jsonl,lock}
Log:   ~/.rig/logs/jev-vault-triage.log (via cron)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Cron runs without LANG; reconfigure stdout so a non-ASCII filename cannot
# crash the tick under LC_ALL=C (Python >=3.7 on both runtimes, proven live).
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/rig128gb/Documents/JakeStudio")).expanduser()
STATE = Path(os.environ.get("JEVT_STATE_DIR", Path.home() / ".rig/state/jev-triage"))
LEDGER = STATE / "triage.jsonl"
ESCALATIONS = STATE / "escalations.jsonl"
LOCK = STATE / "lock"
MEMORY_CLI = Path.home() / "bin/rig-memory-os"
S1GATE_CLI = Path("/Users/rig128gb/Developer/rig-capabilities/bin/rig-s1gate")
SECRETS_ENV = Path.home() / ".rig-secrets/typesafe.env"

INTAKE = "Inbox"
QUARANTINE = "_quarantine"
NEEDS_REASONING = "_needs-reasoning"
ARCHIVE = "_archive"
# destination.choice -> vault folder (existing areas; Memory/Imports is ours)
DESTS = {
    "transcripts": "transcripts",
    "knowledge": "Knowledge",
    "research": "Research",
    "memory": "Memory/Imports",
    "archive": f"{INTAKE}/{ARCHIVE}",
}
MAX_STATE_CHARS = 4000
MARKER = "jev-triage:"

# ---------------------------------------------------------------- redaction
# Copy of SECRET_PATTERNS/redact from ~/.rig/bin/obsidian-memory-bridge (lines
# 25-84, 2026-09-20). Inlined deliberately: the bridge is an extensionless
# script, not an importable module, so a dynamic import cannot be proven to
# any loader-bound verifier (D85 runtime_loader_proof). If the bridge patterns
# change, change them here too -- the patterns, not the import, are the contract.
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"(?i)\b(authorization)\b\s*[:=]\s*bearer\s+[^\s`'\"]+"),
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password|authorization|bearer)\b\s*[:=]\s*[^\s`'\"]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
]


def redact(text: str) -> str:
    safe = text or ""
    for pattern in SECRET_PATTERNS:
        safe = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED]" if m.groups() else "[REDACTED_SECRET_BLOCK]", safe)
    return safe


def ensure_key() -> None:
    if os.environ.get("TYPESAFE_API_KEY", "").strip():
        return
    if SECRETS_ENV.is_file():
        for line in SECRETS_ENV.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?([A-Z_]+)=(\S+)", line)
            if m:
                os.environ.setdefault(m.group(1), m.group(2))


# ---------------------------------------------------------------- frontmatter
def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (fm_lines, body); fm_lines empty when there is no frontmatter block."""
    if not text.startswith("---"):
        return [], text
    lines = text.splitlines()
    for i in range(1, min(len(lines), 60)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return [], text


def tagged(text: str) -> bool:
    fm, _ = split_frontmatter(text)
    return any(ln.strip().startswith(MARKER) for ln in fm)


def apply_frontmatter(path: Path, extra: dict) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    keys = {ln.split(":", 1)[0].strip() for ln in fm if ":" in ln}
    for k, v in extra.items():
        if k not in keys:
            fm.append(f"{k}: {v}")
    path.write_text("---\n" + "\n".join(fm) + "\n---\n" + body, encoding="utf-8")


def move(path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / path.name
    n = 1
    while target.exists():
        target = dest_dir / f"{path.stem}-{n}{path.suffix}"
        n += 1
    os.replace(path, target)
    return target


# ---------------------------------------------------------------- memory os
SENS_MAP = {"public": "public", "internal": "internal", "private": "confidential", "secret": "restricted"}


def record_event(rec: dict) -> str:
    payload = {
        "run_id": "jev-vault-triage",
        "mission_id": "vault-triage",
        "event_type": "vault.triaged",
        "occurred_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "sensitivity": SENS_MAP.get(rec.get("sensitivity", "internal"), "internal"),
        "payload": rec,
        "idempotency_key": rec["sha256"],
    }
    try:
        r = subprocess.run(
            [str(MEMORY_CLI), "call", "memory.record_event", "--input", json.dumps(payload)],
            capture_output=True, text=True, timeout=30,
        )
        return "ok" if r.returncode == 0 else f"memory-cli-rc{r.returncode}:{r.stderr.strip()[:120]}"
    except Exception as exc:  # noqa: BLE001 - the note is already filed; ledger records the miss
        return f"memory-error:{exc}"


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def calls_today() -> int:
    if not LEDGER.is_file():
        return 0
    today = dt.date.today().isoformat()
    n = 0
    for line in LEDGER.read_text().splitlines():
        if f'"{today}' in line:
            n += 1
    return n


# ---------------------------------------------------------------- triage
def jview(path: Path) -> str:
    """Redacted head of the note -- what Jev sees (and the decision log previews)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    return redact(f"filename: {path.name}\n\n{raw[:MAX_STATE_CHARS]}")


def jev_check(state: str) -> dict:
    """One rig-s1gate call. Exit codes are the contract: 0 PASS, 1 BLOCK, 2 ESCALATE, 3 usage."""
    if not S1GATE_CLI.is_file():
        return {"error": "s1gate-cli-missing"}
    try:
        r = subprocess.run(
            [str(S1GATE_CLI), "check", "vault.triage", "--stdin", "--json"],
            input=state, capture_output=True, text=True, timeout=45,
            cwd=str(S1GATE_CLI.parent.parent),
        )
    except Exception as exc:  # noqa: BLE001 -- provider trouble is a defer, never a guess
        return {"error": f"s1gate-{type(exc).__name__}:{str(exc)[:160]}"}
    try:
        res = json.loads(r.stdout)
    except ValueError:
        return {"error": f"s1gate-bad-json-rc{r.returncode}:{r.stderr.strip()[:160]}"}
    if r.returncode not in (0, 1, 2):
        return {"error": f"s1gate-rc{r.returncode}:{r.stderr.strip()[:160]}"}
    return res


def triage_one(path: Path, args) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if tagged(text) or len(text.strip()) < 20:
        return {"file": str(path), "action": "skip"}
    res = jev_check(jview(path))

    def pick(q, default=""):
        a = (res.get("answers") or {}).get(q) or {}
        return a.get("choice") or default

    def noul(q, default=0.5):
        return float((res.get("answers") or {}).get(q, {}).get("noul", default))

    rec = {
        "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "file": str(path),
        "sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
        "verdict": res.get("verdict") or res.get("error") or "?",
        "error": res.get("error"),
        "kind": pick("kind"),
        "destination": pick("destination"),
        "needs_reasoning": round(noul("needs_reasoning"), 2),
        "is_noise": round(noul("is_noise"), 2),
        "sensitivity": pick("sensitivity"),
        "decision_id": res.get("decision_id"),
        "latency_ms": res.get("latency_ms"),
    }
    if args.dry_run:
        rec["action"] = "dry-run"
        return rec

    if res.get("error") or not res.get("answers"):
        # Fail closed: Jev unavailable or unanswered -- leave the file untouched.
        rec["action"] = "deferred-jev-unavailable"
        return rec

    stamp = {
        MARKER.rstrip(":"): rec["ts"][:10],
        "jev-verdict": rec["verdict"],
        "jev-kind": rec["kind"] or "unknown",
        "jev-decision": str(res.get("decision_id") or ""),
    }
    if pick("sensitivity") == "secret":
        apply_frontmatter(path, {**stamp, "jev-route": QUARANTINE})
        rec["moved_to"] = str(move(path, VAULT / INTAKE / QUARANTINE))
        rec["action"] = "quarantined"
        rec["memory"] = record_event({k: rec[k] for k in ("file", "sha256", "verdict", "sensitivity", "decision_id")})
        return rec

    if rec["verdict"] == "BLOCK":
        apply_frontmatter(path, {**stamp, "jev-route": ARCHIVE})
        rec["moved_to"] = str(move(path, VAULT / INTAKE / ARCHIVE))
        rec["action"] = "archived-noise"
    elif rec["verdict"] == "ESCALATE":
        apply_frontmatter(path, {**stamp, "jev-route": NEEDS_REASONING, "jev-status": "needs-reasoning"})
        rec["moved_to"] = str(move(path, VAULT / INTAKE / NEEDS_REASONING))
        rec["action"] = "escalated"
        append_jsonl(ESCALATIONS, rec)
    else:
        dest = DESTS.get(rec["destination"], "Knowledge")
        apply_frontmatter(path, {**stamp, "jev-route": dest})
        rec["moved_to"] = str(move(path, VAULT / dest))
        rec["action"] = "filed"
        rec["memory"] = record_event(rec)
    return rec


def scan(args) -> list:
    root = (VAULT / (args.folder or INTAKE)).resolve()
    if not root.is_dir():
        raise SystemExit(f"jev-vault-triage: intake folder missing: {root}")
    cutoff = time.time() - args.age
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".md", ".txt", ".vtt", ".json", ".csv", ".log"):
            continue
        if any(part.startswith("_") for part in p.relative_to(root).parts):
            continue  # _archive / _quarantine / _needs-reasoning are outputs, not intake
        if p.stat().st_mtime > cutoff or p.stat().st_size > args.max_bytes:
            continue
        out.append(p)
    return out


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Jev triage cascade for the JakeStudio vault Inbox")
    ap.add_argument("--folder", default=None, help="intake folder relative to vault (default: Inbox)")
    ap.add_argument("--limit", type=int, default=int(os.environ.get("JEVT_RUN_LIMIT", "20")))
    ap.add_argument("--daily-cap", type=int, default=int(os.environ.get("JEVT_DAILY_CALLS", "400")))
    ap.add_argument("--age", type=int, default=60, help="skip files modified in the last N seconds (iCloud settle)")
    ap.add_argument("--max-bytes", type=int, default=200_000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    STATE.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        pid = (LOCK / "pid").read_text().strip() if (LOCK / "pid").is_file() else ""
        if not (pid.isdigit() and _alive(int(pid))):
            shutil.rmtree(LOCK, ignore_errors=True)  # stale lock from a dead run
    try:
        LOCK.mkdir()
    except FileExistsError:
        print("jev-vault-triage: another run holds the lock; skipping tick", file=sys.stderr)
        return 0
    (LOCK / "pid").write_text(str(os.getpid()))

    try:
        ensure_key()
        files = scan(args)
        budget = max(0, min(args.limit, args.daily_cap - calls_today()))
        files = files[:budget]
        if not files:
            if not args.quiet:
                print("jev-vault-triage: nothing to triage")
            return 0
        errors = 0
        for f in files:
            try:
                rec = triage_one(f, args)
            except Exception as exc:  # noqa: BLE001 -- one bad file must not kill the tick
                rec = {"file": str(f), "action": "error", "error": str(exc)[:300]}
                errors += 1
            if rec.get("action") != "skip":
                append_jsonl(LEDGER, rec)
                if not args.quiet:
                    print("%-28s %s -> %s" % (Path(rec["file"]).name[:28], str(rec.get("verdict", rec.get("action", "?")))[:9].ljust(9), rec.get("action")))
        return 1 if errors == len(files) else 0
    finally:
        (LOCK / "pid").unlink(missing_ok=True)
        LOCK.rmdir()


if __name__ == "__main__":
    raise SystemExit(main())
