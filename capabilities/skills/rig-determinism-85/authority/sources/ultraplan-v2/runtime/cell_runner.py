"""W07 cell runner: execute a validated cell's done_when + gates over a workspace
and attach the receipt through the ledger. No new state authority -- the runner
PRODUCES EVENTS, never mutates missions directly."""
from __future__ import annotations
import json, os, re, subprocess, sys
from pathlib import Path



def _ensure_repo_path():
    """Lazy, idempotent: direct-script imports of runtime.* need the repo root."""
    root = str(Path(__file__).resolve().parent.parent)
    if root not in sys.path:
        sys.path.insert(0, root)

RIG_ULTRA = str(Path.home().parent / "rig128gb" / "Developer" / "rig-capabilities" / "bin" / "rig-ultra")


def parse_done_when(skill_md: Path):
    import yaml
    text = skill_md.read_text()
    if not text.startswith("---"):
        return []
    block = text.split("---", 2)[1]
    try:
        fm = yaml.safe_load(block) or {}
    except Exception:
        return []
    checks = fm.get("done_when") or []
    return [str(c) for c in checks]


def run_check(check: str, workspace: Path) -> tuple[bool, str]:
    if check.startswith("file:"):
        p = workspace / check[5:].strip()
        return p.is_file(), ("exists" if p.is_file() else "missing: %s" % p)
    if check.startswith("grep:"):
        rest = check[5:].strip()
        path, pat = rest.split(":", 1)
        f = workspace / path
        if not f.is_file():
            return False, "missing: %s" % path
        found = re.search(pat, f.read_text(), re.M) is not None
        return found, ("match %r" % pat) if found else ("NO match %r in %s" % (pat, path))
    if check.startswith("cmd:"):
        r = subprocess.run(check[4:], shell=True, cwd=workspace, capture_output=True, text=True, timeout=300)
        return r.returncode == 0, "exit %d %s" % (r.returncode, (r.stdout or r.stderr)[-120:])
    return False, "unregistered check form %r (file:/grep:/cmd: only)" % check[:20]


def done_when_is_vacuous(checks) -> bool:
    """A cell whose every check is 'the file exists' cannot go red when the
    outcome is false -- the exact theater the proof pack names."""
    return bool(checks) and all(c.startswith("file:") for c in checks)


def run_cell(cell_dir: str | Path, workspace: str | Path, *, ledger_db: str | None = None,
             mission_id: str | None = None) -> dict:
    cell = Path(cell_dir)
    checks = parse_done_when(cell / "SKILL.md")
    if not checks:
        return {"ok": False, "cell": str(cell), "why": "no done_when checks declared"}
    if done_when_is_vacuous(checks):
        return {"ok": False, "cell": str(cell), "why": "done_when is all file-existence: theater",
                "checks": checks}
    results = []
    for c in checks:
        ok, note = run_check(c, Path(workspace))
        results.append({"check": c, "ok": ok, "note": note})
    passed = all(r["ok"] for r in results)
    out = {"ok": passed, "cell": cell.name, "results": results}
    if passed and ledger_db and mission_id:
        _ensure_repo_path()
        from runtime.ledger import Ledger
        import hashlib, tempfile, os
        rec = {"kind": "cell-completion", "cell": str(cell), "results": results,
               "mission_id": mission_id, "workspace": str(workspace),
               "workspace_sha256": hashlib.sha256(json.dumps(
                   sorted(str(x) for x in Path(workspace).rglob("*") if x.is_file())
               ).encode()).hexdigest(),
               "producer": os.environ.get("ULTRA_PRODUCER", "unknown")}
        p = Path(ledger_db).parent / ("receipt-%s.json" % cell.name)
        p.write_text(json.dumps(rec, indent=1, sort_keys=True))
        lg = Ledger(ledger_db)
        try:
            lg.apply_command(mission_id, "receipt.attach", {
                "artifact": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "cell": str(cell)})
            out["receipt"] = str(p)
        except Exception as exc:
            # a refused receipt is a REPORTED failure, never a silently dropped one
            out["receipt_error"] = str(exc)
        finally:
            lg.db.close()
    return out
