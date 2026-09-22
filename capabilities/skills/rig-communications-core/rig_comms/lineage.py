"""v20 lineage — hash-chained typed stage events (Build Card: every pass = one
hash-chained event; no hidden retries). Stdlib only; append-only JSONL.
"""
from __future__ import annotations
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("INTAKE", "RESEARCH", "ARCHITECT", "GENERATE", "EVALUATE",
          "REVISE", "VERIFY", "APPROVE", "DELIVER", "LEARN")


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     default=str).encode()).hexdigest()


def append_event(log_path: str | Path, run_id: str, stage: str, role: str,
                 payload: dict, status: str = "ok") -> dict:
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    prev = ""
    if p.exists():
        lines = [l for l in p.read_text().splitlines() if l.strip()]
        if lines:
            prev = json.loads(lines[-1])["event_hash"]
    ev = {"run_id": run_id, "stage": stage, "role": role, "status": status,
          "payload": payload, "prev_hash": prev, "ts": "", "seq": len(_run_events(p, run_id))}
    ev["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ev["event_hash"] = _sha(ev)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, sort_keys=True, default=str) + "\n")
    return ev


def _run_events(p: Path, run_id: str) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()
            and json.loads(l).get("run_id") == run_id]


def verify_chain(log_path: str | Path, run_id: str) -> dict:
    evs = _run_events(Path(log_path), run_id)
    if not evs:
        return {"intact": False, "events": 0, "reason": "no events for run"}
    prev = ""
    for ev in evs:
        h = ev.pop("event_hash")
        if _sha(ev) != h:
            return {"intact": False, "events": len(evs), "reason": f"tampered event seq {ev['seq']}"}
        if ev["prev_hash"] != prev:
            return {"intact": False, "events": len(evs), "reason": f"chain break at seq {ev['seq']}"}
        prev = h
    # per-stage uniqueness: no hidden retries (REVISE may repeat; others may not)
    seen = {}
    for ev in evs:
        if ev["stage"] != "REVISE":
            seen[ev["stage"]] = seen.get(ev["stage"], 0) + 1
    dupes = [s for s, n in seen.items() if n > 1]
    if dupes:
        return {"intact": False, "events": len(evs), "reason": f"hidden retry in {dupes}"}
    return {"intact": True, "events": len(evs), "last_hash": prev}


def demo() -> bool:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "lineage.jsonl"
        append_event(p, "r1", "INTAKE", "conductor", {"objective": "ask"})
        append_event(p, "r1", "GENERATE", "architect", {"v": 1})
        append_event(p, "r1", "REVISE", "architect", {"v": 2})
        append_event(p, "r1", "REVISE", "architect", {"v": 3})
        append_event(p, "r1", "VERIFY", "verifier", {"decision": "pass"})
        assert verify_chain(p, "r1")["intact"]
        # tamper
        lines = p.read_text().splitlines()
        tampered = json.loads(lines[1]); tampered["payload"] = {"v": 999}
        lines[1] = json.dumps(tampered, sort_keys=True)
        p.write_text("\n".join(lines) + "\n")
        assert not verify_chain(p, "r1")["intact"]
    return True


if __name__ == "__main__":
    print("lineage demo OK" if demo() else "FAIL")
