"""V15: runnable done-tests.

`done_when` entries (V7 quality contract) become executable checks. Four forms:
  cmd:<shell>            exit 0 in repo.root (15 s timeout)
  file:<relative/path>   exists under repo.root
  grep:<path>:<regex>    regex found in file
  mcp:<tool>             MCP handler returns without raising
Anything else is `unrunnable` (not a failure) — honest, not green-on-noise.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path


def parse_form(entry: str) -> tuple:
    for form in ("cmd", "file", "grep", "mcp"):
        if entry.startswith(form + ":"):
            rest = entry[len(form) + 1:]
            if form == "grep":
                parts = rest.split(":", 1)
                if len(parts) == 2:
                    return form, (parts[0], parts[1])
                return "unknown", entry
            return form, rest
    return "unknown", entry


def _run_form(repo, form: str, arg, mcp_call=None) -> dict:
    ok, detail = False, ""
    try:
        if form == "cmd":
            r = subprocess.run(arg, shell=True, cwd=repo.root,
                               capture_output=True, text=True, timeout=15)
            ok, detail = r.returncode == 0, (r.stderr or r.stdout)[:200]
        elif form == "file":
            p = Path(repo.root) / arg
            ok = p.exists()
            detail = str(p) if ok else f"missing: {p}"
        elif form == "grep":
            path, rx = arg
            p = Path(repo.root) / path
            if p.exists():
                ok = re.search(rx, p.read_text(errors="ignore")) is not None
                detail = f"pattern {'found' if ok else 'not found'} in {path}"
            else:
                detail = f"missing: {path}"
        elif form == "mcp":
            if mcp_call is None:
                return {"form": "mcp:" + str(arg), "ok": None,
                        "detail": "mcp executor not wired"}
            mcp_call(arg, {})
            ok, detail = True, "handler ok"
    except Exception as e:  # noqa: BLE001 — failure detail is the product
        detail = f"{type(e).__name__}: {e}"
    return {"form": f"{form}:{arg if isinstance(arg, str) else ':'.join(arg)}",
            "ok": ok, "detail": detail}


# Handlers that mutate the estate — never invoked from done-tests.
# mcp:capabilities_certify used to re-enter quality_run (V24 hang).
MCP_MUTATING = frozenset({
    "capabilities_certify", "capabilities_round", "capabilities_db_sync",
    "capabilities_reindex", "capabilities_issue_token",
})

_IN_QUALITY_RUN = False


def run_asset(repo, asset_id: str, source: str | None = None) -> dict:
    a = None
    for x in repo.load_index()["assets"]:
        if x["id"] == asset_id and (source is None or x["source"] == source):
            a = x
            break
    if a is None:
        return {"id": asset_id, "pass": False,
                "results": [{"form": "lookup", "ok": False, "detail": "asset not found"}]}
    entries = (a.get("quality") or {}).get("done_when") or []
    mcp_call = None
    needs_mcp = any(str(e).startswith("mcp:") and
                    str(e)[4:] not in MCP_MUTATING for e in entries)
    if needs_mcp:
        from .server import build_server
        srv = build_server(repo)
        def mcp_call(tool, args):  # noqa: E301
            srv.handlers[tool](args)
    results = []
    for e in entries:
        form, arg = parse_form(str(e))
        if form == "unknown":
            results.append({"form": str(e), "ok": None, "detail": "unrunnable"})
            continue
        if form == "mcp" and arg in MCP_MUTATING:
            results.append({"form": str(e), "ok": None,
                            "detail": "mutating mcp not invoked from done-tests"})
            continue
        results.append(_run_form(repo, form, arg, mcp_call))
    runnable = [r for r in results if r["ok"] is not None]
    # `pass: true` must say how much of it was actually executed. An entry the runner
    # cannot parse (house convention allows prose done_when rows, and mutating MCP
    # entries are deliberately never invoked) is skipped, so without this count a
    # green verdict silently hides the checks that never ran.
    unrunnable = [{"form": r.get("form"), "detail": r.get("detail")}
                  for r in results if r["ok"] is None]
    return {"id": asset_id, "pass": bool(runnable) and all(r["ok"] for r in runnable),
            "ran": len(runnable), "unrunnable": len(unrunnable),
            "unrunnable_forms": unrunnable, "results": results}


def quality_run(repo, lane: str | None = None) -> dict:
    """Run done-tests for every canonical with any; write scorecard artifact."""
    global _IN_QUALITY_RUN
    if _IN_QUALITY_RUN:
        return {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "lane": lane,
                "ran": 0, "passed": 0, "pass_rate": None,
                "failures": ["reentrant"], "reentrant": True}
    _IN_QUALITY_RUN = True
    try:
        return _quality_run(repo, lane)
    finally:
        _IN_QUALITY_RUN = False


def _quality_run(repo, lane: str | None = None) -> dict:
    doc = repo.load_index()
    from .lanes import load_overlay
    from .taxonomy import classify
    ov = load_overlay(repo)
    rows = []
    for a in doc["assets"]:
        if a["source"] != "canonical":
            continue
        if lane and (ov.get(a["id"]) or classify(a)) != lane:
            continue
        if not (a.get("quality") or {}).get("done_when"):
            continue
        r = run_asset(repo, a["id"], source="canonical")
        rows.append(r)
    passed = sum(1 for r in rows if r["pass"])
    rep = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "lane": lane,
           "ran": len(rows), "passed": passed,
           "pass_rate": round(passed / len(rows), 3) if rows else None,
           "failures": [r["id"] for r in rows if not r["pass"]]}
    out = Path(repo.root) / ".context" / "quality-runs"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{rep['ts'].replace(':', '')}.json").write_text(
        json.dumps({"summary": rep, "rows": rows}, indent=1))
    return rep
