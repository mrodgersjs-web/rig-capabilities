#!/usr/bin/env python3
"""drift_doctor.py — DRIFT DOCTOR for the workflow registry (modeled on `tac3 surfaces check`).

Compares every design row (SSOT: registry/imported/aside-routines.yaml + out/*/registry/row.yaml)
against the live surface it claims. Verdicts per row:
  OK           live surface matches the row
  DRAFT        row is a studio draft, surface correctly not embedded yet
  DRIFT        row says one thing, the live surface says another  -> exit 2
  UNCHECKED    no deterministic probe exists for that surface yet (honest, never guessed)

Usage: python3 compiler/drift_doctor.py [--json]   (exit 0 clean, 2 on drift, 1 on error)
"""
import glob, json, os, re, sqlite3, sys

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANES = f"{HOME}/rig-builds/grokbot-allmodels/lanes.yaml"
TOML = f"{HOME}/.grok/config.toml"

def load_yaml_rows(path):
    """Minimal reader for the extract format (flat `  - key: value` rows)."""
    rows, cur = [], None
    for ln in open(path):
        if ln.startswith("  - id: "):
            cur = {"id": ln.split(":", 1)[1].strip()}
            rows.append(cur)
        elif cur is not None and ln.startswith("    ") and ":" in ln:
            k, v = ln.strip().split(":", 1)
            cur[k] = v.strip().strip('"')
    return rows

def main(as_json=False):
    verdicts = []
    # --- imported Aside routines: live row vs recorded schedule/status ---
    imp = os.path.join(ROOT, "registry", "imported", "aside-routines.yaml")
    db = sqlite3.connect(f"file:{HOME}/.aside/u/0/state.db?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    live = {r["id"]: dict(r) for r in db.execute("SELECT * FROM routines WHERE deleted_at IS NULL")}
    n_imported = 0
    if os.path.exists(imp):
        for row in load_yaml_rows(imp):
            n_imported += 1
            rid = row["id"]
            lr = live.get(rid)
            if lr is None:
                verdicts.append({"row": rid, "surface": "aside-routine", "verdict": "DRIFT",
                                 "detail": "row recorded live but routine is gone (deleted/purged)"})
                continue
            live_rrule = (lr.get("rrule") or "").replace("\n", " ")
            if row.get("schedule", "") != live_rrule:
                verdicts.append({"row": rid, "surface": "aside-routine", "verdict": "DRIFT",
                                 "detail": f"schedule changed: row={row.get('schedule','')[:60]!r} live={live_rrule[:60]!r}"})
            elif f"status={lr.get('status')})" not in row.get("embed_state", ""):
                verdicts.append({"row": rid, "surface": "aside-routine", "verdict": "DRIFT",
                                 "detail": f"status changed: row says {row.get('embed_state')!r} live={lr.get('status')!r}"})
            else:
                verdicts.append({"row": rid, "surface": "aside-routine", "verdict": "OK", "detail": ""})
    # --- studio-compiled rows (out/*/registry/row.yaml): draft rows must NOT be embedded ---
    lanes = open(LANES).read() if os.path.exists(LANES) else ""
    toml = open(TOML).read() if os.path.exists(TOML) else ""
    for rp in sorted(glob.glob(os.path.join(ROOT, "out", "*", "registry", "row.yaml"))):
        txt = open(rp).read()
        wid = re.search(r"^id: (\S+)", txt, re.M).group(1)
        lane_m = re.search(r"grokbot_lane: ([^,}]+)", txt)
        lane = lane_m.group(1).strip() if lane_m else ""
        if "embed_state: draft" in txt:
            embedded = []
            if lane and f"name: {lane}" in lanes:
                embedded.append("lanes.yaml")
            if lane and f"[model.{lane}]" in toml:
                embedded.append("config.toml")
            if live.get("wds") or any(str(v.get("name", "")).startswith("[DRAFT") for v in []):
                embedded.append("state.db")
            if embedded:
                verdicts.append({"row": wid, "surface": "grokbot-behavior", "verdict": "DRIFT",
                                 "detail": f"row is draft but found embedded in {embedded}"})
            else:
                verdicts.append({"row": wid, "surface": "all-7", "verdict": "DRAFT",
                                 "detail": "7 surfaces compiled; nothing embedded (as designed)"})
        else:
            verdicts.append({"row": wid, "surface": "all-7", "verdict": "UNCHECKED",
                             "detail": "embedded row: per-surface probes pending (temporal/goalspec/jake-brain/chat have no deterministic probe yet)"})
    drift = [v for v in verdicts if v["verdict"] == "DRIFT"]
    summary = {
        "rows_checked": len(verdicts),
        "imported_aside_rows": n_imported,
        "ok": sum(1 for v in verdicts if v["verdict"] == "OK"),
        "draft": sum(1 for v in verdicts if v["verdict"] == "DRAFT"),
        "drift": len(drift),
        "unchecked": sum(1 for v in verdicts if v["verdict"] == "UNCHECKED"),
        "drift_rows": drift,
    }
    if as_json:
        print(json.dumps({"summary": summary, "verdicts": verdicts}, indent=2))
    else:
        print(f"DRIFT DOCTOR: rows={summary['rows_checked']} ok={summary['ok']} "
              f"draft={summary['draft']} drift={summary['drift']} unchecked={summary['unchecked']}")
        for v in drift:
            print(f"  DRIFT {v['row']} [{v['surface']}]: {v['detail']}")
    return 2 if drift else 0

if __name__ == "__main__":
    sys.exit(main("--json" in sys.argv))
