"""Orchestrator — runs a step's atom pipeline and a lane end-to-end (full automation).

An atom is the unit of work. Three kinds:
  det    {"id","kind":"det","fn": state -> dict}          pure deterministic transform
  llm    {"id","kind":"llm","cfg": LLMStep}               model call, contained by the harness
  human  {"id","kind":"human","gate": str,"produces": s}  irreducible consent/judgment — HALTS

A pipeline is the ordered atoms for one step; a lane is ordered (step_name, pipeline) pairs.
The runner threads a `state` dict forward. It HALTS on: an llm escalate/reject, or a human gate.
A halt is not a failure — it is the machine handing the one thing it may not do to the queue.
"""
import json, os, secrets, time
from harness import run_step

QUEUE = os.path.join(os.path.dirname(__file__), "..", "..", ".data", "foundry-queue.jsonl")


def det(id, fn):
    return {"id": id, "kind": "det", "fn": fn}

def llm(cfg):
    return {"id": cfg.task, "kind": "llm", "cfg": cfg}

def human(id, gate, produces="decision"):
    return {"id": id, "kind": "human", "gate": gate, "produces": produces}


def _project(schema, state):
    out = {}
    for field in schema:
        name = field[:-1] if field.endswith("?") else field
        if name in state:
            out[name] = state[name]
    return out


def run_pipeline(pipeline, state, get_fn):
    """Run one step's atoms. Returns {status: complete|halted, ledger, state, halt?}."""
    ledger = []
    for atom in pipeline:
        k = atom["kind"]
        if k == "det":
            try:
                partial = atom["fn"](state) or {}
            except Exception as e:  # deterministic op raising = a bug, surfaced as a halt
                ledger.append({"atom": atom["id"], "kind": "det", "verdict": "error", "error": repr(e)})
                return {"status": "halted", "ledger": ledger, "state": state,
                        "halt": {"kind": "det-error", "atom": atom["id"], "error": repr(e)}}
            if isinstance(partial, dict) and "_halt" in partial:
                h = partial["_halt"]
                ledger.append({"atom": atom["id"], "kind": "det", "verdict": h.get("verdict", "reject")})
                return {"status": "halted", "ledger": ledger, "state": state,
                        "halt": {"kind": "det-reject", "atom": atom["id"], **h}}
            state.update(partial)
            ledger.append({"atom": atom["id"], "kind": "det", "verdict": "ok", "wrote": sorted(partial)})
        elif k == "llm":
            cfg = atom["cfg"]
            r = run_step(cfg, _project(cfg.input_schema, state), get_fn(cfg.task))
            ledger.append({"atom": atom["id"], "kind": "llm", "verdict": r["verdict"],
                           "attempts": r.get("attempts"), "model_calls": r.get("model_calls")})
            if r["verdict"] == "produced":
                state.update(r["output"])
            else:
                return {"status": "halted", "ledger": ledger, "state": state,
                        "halt": {"kind": "llm-" + r["verdict"], "atom": atom["id"],
                                 "reason": r.get("reason") or r.get("errors"), "detail": r.get("last_error")}}
        elif k == "human":
            # NEVER resumes from approval embedded in workflow input (injectable via Trigger payload).
            # Resume requires a signed, one-time, artifact-bound receipt — see gates.py (wired below).
            ledger.append({"atom": atom["id"], "kind": "human", "verdict": "held", "gate": atom["gate"]})
            return {"status": "halted", "ledger": ledger, "state": state,
                    "halt": {"kind": "human-gate", "atom": atom["id"], "gate": atom["gate"],
                             "produces": atom["produces"]}}
        else:
            raise ValueError("unknown atom kind: " + k)
    return {"status": "complete", "ledger": ledger, "state": state}


def run_lane(lane, state, get_fn, queue_path=None, workflow=None, receipts_path=None, receipt_id=None):
    """lane = [(step_name, pipeline), ...]. Runs until complete or the first halt. On halt, appends
    a queue entry (the ONLY human surface). Returns the run record.

    `workflow` is the KPI workflow id. When provided, EVERY terminal outcome (complete and halted)
    writes one receipt row to the separate sink (receipts_path, default RECEIPTS), projected onto
    the contract's samples_keys only — never the full lane state. Without workflow, no receipt is
    written. The human queue contract is untouched."""
    if workflow is None:
        if receipts_path is not None:
            raise ValueError("receipts_path requires workflow")
        receipts_path = None  # disables sink emission entirely
    else:
        receipts_path = receipts_path or RECEIPTS
    # Stable replay identity: caller-supplied (Trigger ctx.run.id / source event) wins; env var
    # FOUNDRY_RUN_ID next; random fallback is NOT replay-safe and is for local calls only.
    rid = receipt_id or os.environ.get("FOUNDRY_RUN_ID") or secrets.token_hex(8)
    full, state = [], dict(state)
    root_parent = os.environ.get("FOUNDRY_TRACE_PARENT") or None
    for step_name, pipeline in lane:
        # step-level trace span: child of the root, parent of any llm spans inside the step
        _step_trace = None
        try:
            import foundry_trace as _ft
            _step_trace = _ft.begin("step:" + step_name, "chain", parent_id=root_parent,
                                    inputs={"step": step_name})[0]
            os.environ["FOUNDRY_TRACE_PARENT"] = _step_trace or (root_parent or "")  # step child of root
        except Exception:
            _step_trace = None
        res = run_pipeline(pipeline, state, get_fn)
        if _step_trace is not None:
            try:
                import foundry_trace as _ft
                _ft.end(_step_trace, outputs={"status": res.get("status")})
            except Exception:
                pass
            os.environ["FOUNDRY_TRACE_PARENT"] = root_parent or ""
        for row in res["ledger"]:
            row["step"] = step_name
        full.extend(res["ledger"])
        state = res["state"]
        if res["status"] == "halted":
            hk = res["halt"]["kind"]
            q = hk in ("human-gate", "llm-escalate:human") or bool(res["halt"].get("queue"))
            entry = {"ts": os.environ.get("FOUNDRY_FROZEN_TS") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                     "step": step_name, "halt": res["halt"], "state_keys": sorted(state)}
            # human gates, LLM escalations, and det classifiers that route to a human (queue flag)
            # are human work; det-rejects are clean automated outcomes
            if q:
                _enqueue(entry, queue_path)
            _receipt(workflow, "halted", _samples_projection(workflow, state),
                     step=step_name, path=receipts_path, receipt_id=rid, state=state)
            rec = {"status": "halted", "at": step_name, "halt": res["halt"], "queued": q,
                   "ledger": full, "state": state, "receipt_id_used": rid}
            return rec
    _receipt(workflow, "complete", _samples_projection(workflow, state), path=receipts_path,
             receipt_id=rid, state=state)
    return {"status": "complete", "ledger": full, "state": state, "receipt_id_used": rid}


def _enqueue(entry, path=None):
    path = path or QUEUE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


RECEIPTS = os.path.join(os.path.dirname(QUEUE), "foundry-receipts.jsonl")


def _receipt(workflow, status, samples, step=None, path=None, receipt_id=None, state=None):
    """Write one minimized terminal receipt when a workflow identity is available. Direct
    run_lane callers (tests/self-check) without a workflow write nothing."""
    if workflow is None:
        return
    import tac_context as _tc
    receipt = {"status": status, "samples": dict(samples)}
    if state is not None:
        receipt["execution"] = _tc.execution_envelope(workflow, state)
    _enqueue(
        {"receipt_id": receipt_id or secrets.token_hex(8),
         "ts": os.environ.get("FOUNDRY_FROZEN_TS") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "workflow": workflow, "step": step,
         "receipt": receipt},
        path or RECEIPTS)


def _samples_projection(workflow, state):
    """Project state onto the samples_keys the KPI contract names for this workflow. Contract load
    failure or no entry -> empty projection (sink stores nothing sensitive by default)."""
    try:
        contract = json.loads(open(os.path.join(os.path.dirname(__file__), "..", "..",
                                                "payloads", "kpi", "contract.json")).read())
        keys = {e["samples_key"] for e in contract if e.get("workflow") == workflow}
    except Exception:
        return {}
    return {k: state[k] for k in keys if k in state}


if __name__ == "__main__":
    from harness import LLMStep
    import model
    model.register_mock("classify", lambda p, a: '{"label": "enterprise"}')
    fn = lambda task: model.mock_fn(task)
    pipe_a = [
        det("normalize", lambda s: {"topic": s["raw"].strip().lower()}),
        llm(LLMStep("classify", {"topic": "str"}, "Classify.", "Segment: {topic}",
                    {"label": "str"}, gates=[("nonempty", lambda o, i: (bool(o["label"]), "empty"))])),
        det("stamp", lambda s: {"segment": s["label"]}),
    ]
    lane = [("intake", pipe_a), ("gate", [human("send", "Mike approves the segment", "decision")])]
    q = "/tmp/foundry-queue-selfcheck.jsonl"
    open(q, "w").close()
    r = run_lane(lane, {"raw": "  ACME Corp "}, fn, queue_path=q)
    assert r["status"] == "halted" and r["at"] == "gate", r
    assert r["state"]["segment"] == "enterprise", r
    assert sum(1 for _ in open(q)) == 1, "one queue entry"
    print("orchestrator self-check OK:", r["status"], "at", r["at"], "| segment =", r["state"]["segment"])
