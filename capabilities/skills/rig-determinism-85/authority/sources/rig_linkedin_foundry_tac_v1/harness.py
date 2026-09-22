"""Foundry LLM-step harness — the deterministic container around a single model call (v20 doctrine).

Every LLM step in the process map runs through run_step(). The model call is the ONLY
non-deterministic atom; validate-input, render-prompt, parse, schema-check, semantic gates,
retry, and escalate are all deterministic and unit-tested with a mock model_fn.

A step is FULLY SPECIFIED by an LLMStep config:
  task           short id
  input_schema   {field: type}; 'field?' = optional. types: str,int,num,bool,list,obj
  system         system prompt (deterministic)
  template       user prompt; .format(**inp)
  output_schema  {field: type}; validates the parsed model JSON
  gates          [(name, fn(out, inp)->(bool,msg))]  deterministic semantic checks
  max_retries    int; on each fail the error is fed back into the prompt
  escalation     human instruction emitted when retries are exhausted
"""
import json, hashlib

TYPES = {"str": str, "int": int, "num": (int, float), "bool": bool, "list": list, "obj": dict}


def _typecheck(schema, obj):
    """Deterministic: returns list of error strings ([] = valid)."""
    errs = []
    if not isinstance(obj, dict):
        return ["not an object"]
    for field, typ in schema.items():
        opt = field.endswith("?")
        name = field[:-1] if opt else field
        if name not in obj or obj[name] is None:
            if not opt:
                errs.append("missing:" + name)
            continue
        py = TYPES.get(typ)
        val = obj[name]
        # bool is a subclass of int — keep them distinct
        if typ in ("int", "num") and isinstance(val, bool):
            errs.append("type:%s=bool!=%s" % (name, typ)); continue
        if py and not isinstance(val, py):
            errs.append("type:%s=%s!=%s" % (name, type(val).__name__, typ))
    return errs


class LLMStep:
    def __init__(self, task, input_schema, system, template, output_schema,
                 gates=None, max_retries=3, escalation="route to human"):
        self.task = task
        self.input_schema = input_schema
        self.system = system
        self.template = template
        self.output_schema = output_schema
        self.gates = gates or []
        self.max_retries = max_retries
        self.escalation = escalation

    def render(self, inp, feedback=None):
        fmt = {(k[:-1] if k.endswith("?") else k): inp.get(k[:-1] if k.endswith("?") else k, "") for k in self.input_schema}
        p = self.system + "\n\n" + self.template.format(**fmt)
        if feedback:
            p += "\n\nYour previous output was rejected: " + feedback + "\nReturn corrected JSON only."
        return p


def receipt(task, verdict, **kw):
    r = {"task": task, "verdict": verdict}
    r.update(kw)
    return r


def run_step(cfg, inp, model_fn):
    """Deterministic harness. model_fn(prompt, attempt)->str is the sole non-deterministic atom.
    Returns a receipt dict; never raises on model output (only escalates)."""
    ierr = _typecheck(cfg.input_schema, inp)
    if ierr:
        return receipt(cfg.task, "reject:invalid-input", errors=ierr, model_calls=0)

    feedback, last = None, None
    for attempt in range(1, cfg.max_retries + 1):
        prompt = cfg.render(inp, feedback)
        raw = model_fn(prompt, attempt)
        try:
            out = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            feedback = last = "output was not valid JSON"
            continue
        serr = _typecheck(cfg.output_schema, out)
        if serr:
            feedback = last = "schema errors: " + ", ".join(serr)
            continue
        gate_fail = None
        for name, fn in cfg.gates:
            ok, msg = fn(out, inp)
            if not ok:
                gate_fail = "%s: %s" % (name, msg)
                break
        if gate_fail:
            feedback = last = gate_fail
            continue
        import tac_context as _tc
        return receipt(cfg.task, "produced", output=out, attempts=attempt,
                       prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:12],
                       prompt_contract_sha256=_tc.prompt_contract_hash(cfg))

    return receipt(cfg.task, "escalate:human", reason=cfg.escalation,
                   last_error=last, model_calls=cfg.max_retries)


if __name__ == "__main__":
    # self-check (planted failures) — run: python3 harness.py
    good = LLMStep(
        task="demo", input_schema={"topic": "str"},
        system="You classify.", template="Classify {topic}. Return JSON {{\"label\": <str>}}.",
        output_schema={"label": "str"},
        gates=[("nonempty", lambda o, i: (bool(o["label"].strip()), "label empty"))],
        max_retries=3, escalation="human labels it")

    calls = {"n": 0}
    def mock_ok(p, a): calls["n"] += 1; return '{"label": "ok"}'
    def mock_badjson(p, a): return "not json"
    def mock_retry(p, a): return "nope" if a == 1 else '{"label": "fixed"}'
    def mock_gatefail(p, a): return '{"label": "   "}'

    assert run_step(good, {"topic": "x"}, mock_ok)["verdict"] == "produced"
    assert run_step(good, {}, mock_ok)["verdict"] == "reject:invalid-input"
    r = run_step(good, {"topic": "x"}, mock_badjson); assert r["verdict"] == "escalate:human" and r["model_calls"] == 3, r
    r = run_step(good, {"topic": "x"}, mock_retry); assert r["verdict"] == "produced" and r["attempts"] == 2, r
    assert run_step(good, {"topic": "x"}, mock_gatefail)["verdict"] == "escalate:human"
    # input typecheck: model must never be called on bad input
    calls["n"] = 0; run_step(good, {"topic": 5}, mock_ok); assert calls["n"] == 0
    print("harness self-check OK")
