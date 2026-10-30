"""Pipeline runner: portable-JSON pipeline specs (RocketRide-shaped), run in-process.

Spec: {"name": str, "nodes": [{"id": str, "fn": str, "args": {...}, "retries": int}]}
Nodes run in order; each node result feeds the next node's args["prev"].
Every run and per-node outcome is appended to state/runs.jsonl.
"""
import importlib
import json
import time
from pathlib import Path

STATE = Path(__file__).parent / "state"
RUNS = STATE / "runs.jsonl"


def _log(rec):
    STATE.mkdir(exist_ok=True)
    with RUNS.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def run_pipeline(spec_path, input_args=None):
    spec = json.loads(Path(spec_path).read_text())
    # pick up node edits without a server restart (nodes.py is edited while the shell runs)
    if "nodes" in importlib.sys.modules:
        importlib.reload(importlib.sys.modules["nodes"])
    run_id = f"{spec['name']}-{int(time.time())}"
    started = time.time()
    _log({"event": "run_start", "run_id": run_id, "pipeline": spec["name"]})
    prev = dict(input_args or {})
    try:
        for node in spec["nodes"]:
            fn = getattr(importlib.import_module("nodes"), node["fn"])
            retries = int(node.get("retries", 1))
            t0 = time.time()
            last_err = None
            for attempt in range(1, retries + 1):
                try:
                    prev = fn(**{**node.get("args", {}), "prev": prev})
                    last_err = None
                    break
                except Exception as e:  # noqa: BLE001 — retry budget is the policy
                    last_err = e
                    if attempt < retries:
                        time.sleep(0.2 * attempt)
            dur = round(time.time() - t0, 3)
            if last_err is not None:
                raise last_err
            _log({"event": "node_ok", "run_id": run_id, "node": node["id"],
                  "fn": node["fn"], "attempts": attempt, "seconds": dur})
        _log({"event": "run_ok", "run_id": run_id, "pipeline": spec["name"],
              "seconds": round(time.time() - started, 3), "result": prev})
        return {"ok": True, "run_id": run_id, "result": prev}
    except Exception as e:  # noqa: BLE001 — surface failure in run history, don't hide it
        _log({"event": "run_fail", "run_id": run_id, "pipeline": spec["name"],
              "error": f"{type(e).__name__}: {e}"})
        return {"ok": False, "run_id": run_id, "error": f"{type(e).__name__}: {e}"}


def run_history(limit=50):
    if not RUNS.exists():
        return []
    lines = RUNS.read_text().splitlines()[-limit:]
    return [json.loads(x) for x in lines]
