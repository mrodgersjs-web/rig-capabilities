"""Ledgers (v8 telemetry, v10 measurement, v11 calibration, v14 media).

Append-only JSONL under <repo>/data/comms/. Every writer takes plain dicts and
adds ts + surface. Brier scoring is frozen multiclass: one row per resolution,
`p` = predicted probability vector (or scalar for binary), `y` = one-hot outcome.
Honesty rule: reports NEVER print a score with fewer than MIN_RESOLUTIONS —
they print UNMEASURED with the deficit named.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

MIN_RESOLUTIONS = 10  # per surface, below this calibration is UNMEASURED


def data_root() -> Path:
    """Repo data/comms dir. RIG_COMMS_DATA overrides (tests/cron); else walk
    up from the package looking for the repo marker."""
    import os
    if os.environ.get("RIG_COMMS_DATA"):
        return Path(os.environ["RIG_COMMS_DATA"])
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "capabilities" / "skills").is_dir():
            return p / "data" / "comms"
    return Path.home() / ".rig" / "comms"


def _append(name: str, rec: dict) -> Path:
    path = data_root() / name
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = dict(rec, ts=rec.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def _read(name: str) -> list[dict]:
    path = data_root() / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --- v8 loop telemetry -------------------------------------------------------

def loop_event(kind: str, surface: str, artifact: str = "", detail: dict | None = None) -> Path:
    return _append("loops.jsonl", {"event": kind, "surface": surface,
                                   "artifact": artifact, "detail": detail or {}})


def loop_report() -> dict:
    rows = [r for r in _read("loops.jsonl") if r.get("surface")]
    per: dict[str, dict] = {}
    for r in rows:
        s = per.setdefault(r["surface"], {"started": 0, "corrections": 0, "shipped": 0, "escalated": 0})
        ev = r.get("event")
        if ev == "start":
            s["started"] += 1
        elif ev == "correction":
            s["corrections"] += 1
        elif ev == "ship":
            s["shipped"] += 1
        elif ev == "escalate":
            s["escalated"] += 1
    for s in per.values():
        s["corrections_per_ship"] = round(s["corrections"] / s["shipped"], 2) if s["shipped"] else None
    return {"per_surface": per, "honest": "counts are telemetry, not quality"}


# --- v10 measurement ---------------------------------------------------------

def record_outcome(surface: str, channel: str, metrics: dict, source: str) -> Path:
    return _append("outcomes.jsonl", {"surface": surface, "channel": channel,
                                      "metrics": metrics, "source": source})


def drafted_vs_shipped() -> dict:
    starts = {}
    ships = {}
    for r in _read("loops.jsonl"):
        if r.get("event") == "start":
            starts[r.get("surface")] = starts.get(r.get("surface"), 0) + 1
        elif r.get("event") == "ship":
            ships[r.get("surface")] = ships.get(r.get("surface"), 0) + 1
    surfaces = sorted(set(starts) | set(ships))
    return {"per_surface": [{"surface": s, "drafted": starts.get(s, 0), "shipped": ships.get(s, 0),
                             "filter_rate": (round(1 - ships.get(s, 0) / starts[s], 2) if starts.get(s) else None)}
                            for s in surfaces]}


# --- v11 calibration ---------------------------------------------------------

def predict(surface: str, prediction_id: str, p: dict, claim: str) -> Path:
    """p: outcome->probability (must sum ~1); claim: human-readable forecast."""
    return _append("predictions.jsonl", {"id": prediction_id, "surface": surface,
                                         "p": p, "claim": claim, "resolved": False})


def resolve(surface: str, prediction_id: str, outcome: str, evidence: str) -> Path:
    return _append("resolutions.jsonl", {"id": prediction_id, "surface": surface,
                                         "outcome": outcome, "evidence": evidence})


def recalibration_proposals() -> dict:
    """v11.3/11.7: PROPOSALS only — never auto-applied. A surface with Brier
    > 0.25 and >= MIN_RESOLUTIONS gets a named sigma-target review suggestion."""
    out = {}
    for surface, c in calibration_report()["calibration"].items():
        if c["status"] == "UNMEASURED":
            out[surface] = {"proposal": "NONE", "reason": f"UNMEASURED (deficit {c['deficit']})"}
        elif c["brier"] > 0.25:
            out[surface] = {"proposal": "REVIEW_SIGMA_TARGET",
                            "reason": f"Brier {c['brier']} > 0.25 — predictions barely beat coin-flip; "
                                      "lower the sigma target or retire the template that produced them",
                            "auto_applied": False}
        elif c["brier"] < 0.11:
            out[surface] = {"proposal": "RAISE_SIGMA_TARGET",
                            "reason": f"Brier {c['brier']} < 0.11 — predictions sharp; try the next sigma rung",
                            "auto_applied": False}
        else:
            out[surface] = {"proposal": "HOLD", "reason": f"Brier {c['brier']} in calibrated band"}
    return {"proposals": out, "note": "proposals go to Mike/verifier; nothing auto-applies (v18.9 rule)"}


def _brier(p: dict, y: str) -> float | None:
    if y not in p or any(v < 0 or v > 1 for v in p.values()):
        return None
    return sum((p[o] - (1.0 if o == y else 0.0)) ** 2 for o in set(p) | {y}) / max(len(p), 1)


def calibration_report() -> dict:
    preds = {r["id"]: r for r in _read("predictions.jsonl")}
    res: dict[str, list] = {}
    for r in _read("resolutions.jsonl"):
        res.setdefault(r["surface"], []).append(r)
    out = {}
    for surface, rows in res.items():
        vals = []
        for r in rows:
            p = preds.get(r["id"], {}).get("p")
            b = _brier(p, r["outcome"]) if p else None
            if b is not None:
                vals.append(b)
        if len(vals) < MIN_RESOLUTIONS:
            out[surface] = {"status": "UNMEASURED",
                            "resolved": len(vals), "needs": MIN_RESOLUTIONS,
                            "deficit": MIN_RESOLUTIONS - len(vals)}
        else:
            out[surface] = {"status": "SCORED", "brier": round(sum(vals) / len(vals), 4),
                            "resolved": len(vals), "lower_is_better": True}
    return {"calibration": out, "method": "frozen multiclass Brier; no reweighting until recalibration"}


# --- v14 media ledger --------------------------------------------------------

def media_record(artifact: str, kind: str, path: str, generator: str,
                 provenance: str = "") -> Path:
    import os
    return _append("media.jsonl", {"artifact": artifact, "kind": kind, "path": path,
                                   "generator": generator, "provenance": provenance,
                                   "path_exists": os.path.exists(path)})
