#!/usr/bin/env python3
"""Comms scoreboards (v10) — collect per-surface outcomes into dated,
append-only scoreboard JSONs under data/comms/scoreboards/.

Sources probed live (2026-09-06):
- emails:   /Users/rig128gb/Developer/rig-gtm-studio-v2/data/outbound_funnel.db
            (funnel_events: slug, vertical, channel, type, ts, meta)
- linkedin: alfred/scoreboards/*.json (rig-linkedin-scrape output; empty until
            the scrape cron runs -> honest DATA GAP, never a fake zero)
- resumes:  job-cockpit application packets (path configured via env; absent -> GAP)
- substack/songs/film/novels: no ingestion lane yet -> explicit GAP lines

Every metric carries a trust rank (bx-measurement-steward):
  high   = observed platform event scraped logged-out
  medium = own-system event (funnel db write)
  low    = self-report;  unvalidated = model prediction (see v11)

Honesty rule (rig-honest-scoring): an empty source yields status DATA_GAP with
the missing path named — never zeros presented as measurements.
"""
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "capabilities" / "skills" / "rig-communications-core"))
from rig_comms import ledger  # noqa: E402

FUNNEL_DB = Path(os.environ.get("OUTBOUND_FUNNEL_DB",
    "/Users/rig128gb/Developer/rig-gtm-studio-v2/data/outbound_funnel.db"))
ALFRED_SCOREBOARDS = Path(os.environ.get("ALFRED_SCOREBOARDS",
    "/Users/rig128gb/Desktop/rig-linkedin-studio-luca/alfred/scoreboards"))


def emails_funnel() -> dict:
    if not FUNNEL_DB.exists():
        return {"status": "DATA_GAP", "missing": str(FUNNEL_DB), "trust": "medium"}
    con = sqlite3.connect(f"file:{FUNNEL_DB}?mode=ro", uri=True)
    try:
        by_type = dict(con.execute("SELECT type, COUNT(*) FROM funnel_events GROUP BY type"))
        last = con.execute("SELECT MAX(ts) FROM funnel_events").fetchone()[0]
    except sqlite3.Error as e:
        return {"status": "DATA_GAP", "missing": f"unreadable: {e}", "trust": "medium"}
    finally:
        con.close()
    sent = sum(v for k, v in by_type.items() if "sent" in k or "deliver" in k)
    replied = sum(v for k, v in by_type.items() if "reply" in k)
    return {"status": "OK", "events": by_type, "sent_proxy": sent,
            "replied_proxy": replied, "reply_rate": round(replied / sent, 4) if sent else None,
            "last_event": last, "trust": "medium"}


def linkedin_alfred() -> dict:
    if not ALFRED_SCOREBOARDS.exists():
        return {"status": "DATA_GAP", "missing": str(ALFRED_SCOREBOARDS), "trust": "high"}
    rows = []
    for p in sorted(ALFRED_SCOREBOARDS.glob("*.json")):
        try:
            rows.append(json.loads(p.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    if not rows:
        return {"status": "DATA_GAP",
                "missing": "scoreboard files empty — run rig-linkedin-scrape (post engagement capture)",
                "trust": "high"}
    return {"status": "OK", "posts": len(rows), "last": str(rows[-1])[:200], "trust": "high"}


def collect() -> dict:
    board = {
        "date": time.strftime("%Y-%m-%d"),
        "surfaces": {
            "emails": emails_funnel(),
            "linkedin": linkedin_alfred(),
            "resumes": {"status": "DATA_GAP",
                        "missing": "job-cockpit outcome export not wired (set JOB_COCKPIT_OUTCOMES)",
                        "trust": "medium"},
            "substack": {"status": "DATA_GAP", "missing": "no metrics ingestion lane yet", "trust": "high"},
            "songs": {"status": "DATA_GAP", "missing": "SUNO play counts / shareable feedback lane not built", "trust": "low"},
            "film-scripts": {"status": "DATA_GAP", "missing": "coverage/feedback lane not built", "trust": "low"},
            "novels": {"status": "DATA_GAP", "missing": "reader feedback lane not built", "trust": "low"},
        },
        "drafted_vs_shipped": ledger.drafted_vs_shipped(),
        "loop_telemetry": ledger.loop_report(),
        "honesty": "DATA_GAP means the source has no data at the named path — zeros are never fabricated",
    }
    out = ledger.data_root() / "scoreboards" / f"{board['date']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(board, indent=2))
    # feed the outcomes ledger too (append-only measurement stock)
    for surface, m in board["surfaces"].items():
        if m.get("status") == "OK":
            ledger.record_outcome(surface, "scoreboard", m, m["trust"])
    return board


def weekly_markdown() -> str:
    """v10.7 weekly aggregate: latest scoreboard + ledger report as markdown."""
    b = collect()
    r = {"loop": ledger.loop_report(), "dvs": ledger.drafted_vs_shipped(),
         "cal": ledger.calibration_report(), "recal": ledger.recalibration_proposals()}
    lines = [f"# Comms weekly rollup — {time.strftime('%Y-%m-%d %H:%M')}", ""]
    lines += ["## Surface status", "| surface | status | detail |", "|---|---|---|"]
    for k, v in b["surfaces"].items():
        detail = v.get("missing") or json.dumps({x: v[x] for x in v if x not in ("status", "missing")})[:90]
        lines.append(f"| {k} | {v['status']} | {detail} |")
    lines += ["", "## Drafted vs shipped", "```json", json.dumps(r["dvs"], indent=2), "```",
              "", "## Calibration (v11)", "```json", json.dumps(r["cal"], indent=2), "```",
              "", "## Recalibration proposals (never auto-applied)", "```json",
              json.dumps(r["recal"], indent=2), "```"]
    out = ledger.data_root() / "weekly" / f"{time.strftime('%Y-W%V')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return str(out)


if __name__ == "__main__":
    if "--weekly" in sys.argv:
        print(weekly_markdown())
        raise SystemExit(0)
    b = collect()
    print(json.dumps({"written": str(ledger.data_root() / 'scoreboards' / f"{b['date']}.json"),
                      "surfaces_ok": [k for k, v in b["surfaces"].items() if v["status"] == "OK"],
                      "data_gaps": [k for k, v in b["surfaces"].items() if v["status"] == "DATA_GAP"]},
                     indent=2))
