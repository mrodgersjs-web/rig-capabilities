"""Deep-dive registry + runner. Loads lane pipelines, registers mocks, runs a page/lane end-to-end.

CLI:
  python3 deepdive.py census                 atom counts by kind, per lane
  python3 deepdive.py run <page> <state.json>  run one page's 6-step pipeline
Model mode via FOUNDRY_MODEL_MODE (mock default; ollama/openai for live).
"""
import importlib, json, os, sys, time
import model
from atoms import run_lane




def _canon():
    return ["trigger", "intake", "step1", "step2", "record", "kpi"]

def _default_lanes():
    return ["lane_a_deep", "lane_a1_deep", "lane_b_deep", "lane_c_deep", "lane_s_deep"]

def load(lanes=None):
    reg, mocks = {}, {}
    for n in (lanes or _default_lanes()):
        try:
            m = importlib.import_module(n)
        except ModuleNotFoundError:
            continue
        reg.update(m.PIPELINES)
        for t, f in getattr(m, "MOCKS", {}).items():
            model.register_mock(t, f); mocks[t] = f
    return reg

def build_lane(reg, page):
    lane = [(st, reg[(page, st)]) for st in _canon() if (page, st) in reg]
    if not lane:
        raise ValueError("unknown-page:" + str(page))
    return lane


def run_page(reg, page, state):
    import foundry_trace as _ft
    import tac_context as _tc
    import tac_specialists as _ts
    import tac_workflow as _tw
    lane = build_lane(reg, page)
    manifest = _tc.compile_context(state or {})
    state = dict(state or {})
    state["context_manifest"] = manifest
    state["context_manifest_sha256"] = manifest["manifest_sha256"]
    steps = _ts.collect_llm_steps()
    specialist_registry = _ts.validate_descriptors(_ts.default_descriptors(steps), steps)
    state["specialist_registry"] = {
        "ok": specialist_registry["ok"],
        "errors": specialist_registry["errors"],
        "descriptors": specialist_registry["descriptors"],
    }
    _root = _ft.root_trace("foundry.run_page:" + page,
                           inputs={"page": page, "context_manifest_sha256": manifest["manifest_sha256"]},
                           thread_id=(state or {}).get("thread_id"))
    _prev_parent = os.environ.get("FOUNDRY_TRACE_PARENT")
    os.environ["FOUNDRY_TRACE_PARENT"] = _root or ""
    try:
        r = run_lane(lane, state, lambda t: model.get_model_fn(t), workflow=page)
    except Exception as e:
        _ft.end(_root, error=type(e).__name__)
        os.environ["FOUNDRY_TRACE_PARENT"] = _prev_parent or ""
        raise
    r["context_manifest_sha256"] = manifest["manifest_sha256"]
    r["execution"] = _tc.execution_envelope(page, state, manifest)
    r["specialist_registry_ok"] = specialist_registry["ok"]
    if r.get("status") == "halted" and (r.get("halt") or {}).get("kind") == "human-gate":
        cursor_state = {"state_keys": sorted(r.get("state") or {})}
        r["continuation"] = _tw.continuation(
            run_id=os.environ.get("FOUNDRY_RUN_ID") or r.get("receipt_id_used") or "local",
            workflow=page,
            next_step=r.get("at"),
            state_ref=_tw.sha(cursor_state),
            artifact_digest=_tw.sha({"workflow": page, "state": cursor_state}),
        )
    if _root:
        r["trace_id"] = _root
        _ft.end(_root, outputs={"status": r.get("status")})
    os.environ["FOUNDRY_TRACE_PARENT"] = _prev_parent or ""
    return r


def census(reg):
    by_page, tot = {}, {"det": 0, "llm": 0, "human": 0}
    for (page, step), atoms in reg.items():
        d = by_page.setdefault(page, {"det": 0, "llm": 0, "human": 0})
        for a in atoms:
            d[a["kind"]] += 1; tot[a["kind"]] += 1
    return {"total": tot, "by_page": {p: by_page[p] for p in sorted(by_page)}}

def _runlog_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".data", "foundry-runs.jsonl")


def _healthy(result, expected):
    """A run is healthy only if it reached its EXPECTED terminal with no failure en route.
    Rejects det-errors and any llm-* halt (escalation/reject). expected='complete' or a gate spec
    {at, kind, verdict?}."""
    for row in result.get("ledger") or []:
        if row.get("verdict") == "error":
            return False
    halt = result.get("halt") or {}
    if str(halt.get("kind", "")).startswith("llm-") or halt.get("kind") == "det-error":
        return False
    if expected == "complete" or expected is None:
        return result.get("status") == "complete"
    if result.get("status") != "halted":
        return False
    if expected.get("at") and result.get("at") != expected["at"]:
        return False
    if expected.get("kind") and halt.get("kind") != expected["kind"]:
        return False
    v = expected.get("verdict")
    if v and v not in str(halt.get("verdict", "")) and v not in str(halt.get("gate", "")):
        return False
    return True


def record_run(page, result, expected="complete", mode=None, model_ref=None, path=None):
    """Append a run receipt — the ONLY basis status.py trusts for 'live'. ok requires the EXPECTED
    terminal (no failures); produced_llm counts real model outputs so LLM liveness needs a real call."""
    ledger = result.get("ledger") or []
    produced_llm = sum(1 for row in ledger if row.get("kind") == "llm" and row.get("verdict") == "produced")
    mode = mode or os.environ.get("FOUNDRY_MODEL_MODE", "mock")
    ok = _healthy(result, expected)
    terminal = (ledger[-1].get("step") if result.get("status") == "complete" and ledger
                else (result.get("halt") or {}).get("verdict"))
    entry = {"ts": time.time(), "page": page, "status": result.get("status"), "at": result.get("at"),
             "terminal": terminal, "ok": bool(ok), "mode": mode, "produced_llm": produced_llm,
             "expected": expected if isinstance(expected, str) else "gate:%s" % expected.get("at"),
             "model": model_ref or os.environ.get("FOUNDRY_MODEL_REF"),
             "trace_id": result.get("trace_id"),
             "context_manifest_sha256": result.get("context_manifest_sha256"),
             "execution": result.get("execution"),
             "source": "trigger" if os.environ.get("FOUNDRY_RUN_ID") else "local"}
    p = path or _runlog_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


if __name__ == "__main__":
    reg = load()
    if len(sys.argv) >= 2 and sys.argv[1] == "census":
        print(json.dumps(census(reg), indent=1))
    elif len(sys.argv) >= 4 and sys.argv[1] == "run":
        state = json.load(open(sys.argv[3]))
        try:
            r = run_page(reg, sys.argv[2], state)
        except ValueError as e:
            print(json.dumps({"status": "invalid-page", "error": str(e)}))
            sys.exit(2)
        _ft = __import__("foundry_trace")
        _ft.flush()
        record_run(sys.argv[2], r)
        print(json.dumps(r, indent=1, default=str))
    else:
        print(__doc__)
