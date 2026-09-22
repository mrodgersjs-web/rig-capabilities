"""v20 outcome learning (C11) — archetype-keyed telemetry + Brier calibration.

Append-only JSONL. Every record: archetype, stakes, predicted_p (success
probability issued BEFORE delivery), outcome (0/1), plus free telemetry fields.
Promotion rule (Build Card self-breeding): a pattern may be MINTED only after
>=3 same-pattern outcomes and never by this module — minting is a human/verifier
action; we only surface eligibility. Count-aware: with n<30 we report exact
Brier, never "sigma".
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = Path.home() / ".rig" / "comms-outcomes.jsonl"


def record(pattern_id: str, archetype: str, predicted_p: float, outcome: int,
           stakes: str = "medium", log_path: Path | str | None = None, **telemetry) -> dict:
    if not 0.0 <= predicted_p <= 1.0:
        raise ValueError("predicted_p must be in [0,1]")
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1 (1 = intended recipient action completed)")
    row = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "pattern_id": pattern_id, "archetype": archetype, "stakes": stakes,
           "predicted_p": round(float(predicted_p), 4), "outcome": int(outcome), **telemetry}
    p = Path(log_path or DEFAULT_LOG)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def _rows(log_path):
    p = Path(log_path or DEFAULT_LOG)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def brier(archetype: str | None = None, log_path=None) -> dict:
    rows = [r for r in _rows(log_path) if archetype is None or r["archetype"] == archetype]
    if not rows:
        return {"n": 0, "brier": None, "note": "no outcomes recorded — honest empty, not zero"}
    b = sum((r["predicted_p"] - r["outcome"]) ** 2 for r in rows) / len(rows)
    out = {"n": len(rows), "brier": round(b, 4),
           "mean_pred": round(sum(r["predicted_p"] for r in rows) / len(rows), 4),
           "base_rate": round(sum(r["outcome"] for r in rows) / len(rows), 4)}
    if len(rows) < 30:
        out["note"] = "n<30: exact Brier only; no sigma claims (count-aware)"
    return out


def promotion_candidates(min_count: int = 3, log_path=None) -> list[dict]:
    """Build Card self-breeding: >=3 same-pattern successes; minting stays human."""
    counts: dict[str, list] = {}
    for r in _rows(log_path):
        counts.setdefault(r["pattern_id"], []).append(r)
    out = []
    for pid, rs in counts.items():
        wins = sum(r["outcome"] for r in rs)
        if wins >= min_count:
            out.append({"pattern_id": pid, "successes": wins, "attempts": len(rs),
                        "status": "eligible-for-mint (human/verifier action required)"})
    return sorted(out, key=lambda x: -x["successes"])


def demo() -> bool:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = f"{td}/o.jsonl"
        for pred, out in ((0.8, 1), (0.8, 1), (0.8, 1), (0.2, 0)):
            record("cold-outreach-v1", "cold-outreach", pred, out, log_path=p)
        b = brier("cold-outreach", p)
        assert b["n"] == 4 and b["brier"] == round((0.04 * 3 + 0.04) / 4, 4)
        cands = promotion_candidates(log_path=p)
        assert cands and cands[0]["pattern_id"] == "cold-outreach-v1"
        assert "human" in cands[0]["status"]
        assert brier("nonexistent", p)["brier"] is None
    return True


if __name__ == "__main__":
    print("outcomes demo OK" if demo() else "FAIL")
