"""Foundry KPI system — the honest measurement layer over the deep-dive lanes.

Every A/B/C/S workflow has ONE KPI declared in payloads/kpi/contract.json:
  {workflow, lane, metric, samples_key, min_n, dir, target, baseline, source, cadence, unit[, reduce]}

The KPI VALUE is computed by the lane's OWN `*_kpi` deterministic atom (single source of
truth — no duplicated math). evaluate() returns one honest status:
  insufficient_data   fewer than min_n receipts (the atom returns 'baseline-open')
  met                 computed value satisfies target per dir
  unmet               computed value misses target

'met' is only ever COMPUTED from supplied receipts; it is never hard-coded. `report` runs
against the REAL run queue and will honestly say insufficient_data until production receipts
accrue. `acceptance` runs the designed operating point (payloads/kpi/acceptance.json) — the
go-live acceptance gate that proves the targets are reachable and the checker actually fires.

CLI:
  python3 kpis.py acceptance   run the go-live acceptance dataset; exit 1 if any workflow not met
  python3 kpis.py report       honest production status from the real run queue
  python3 kpis.py contract     print the contract
"""
import json, os, importlib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
CONTRACT = os.path.join(ROOT, "payloads", "kpi", "contract.json")
ACCEPTANCE = os.path.join(ROOT, "payloads", "kpi", "acceptance.json")
QUEUE = os.path.join(ROOT, ".data", "foundry-queue.jsonl")
LANES = ["lane_a_deep", "lane_a1_deep", "lane_b_deep", "lane_c_deep", "lane_s_deep"]

_ATOM_CACHE = None


def atoms():
    """workflow -> its kpi atom fn, harvested from each lane's PIPELINES 'kpi' step."""
    global _ATOM_CACHE
    if _ATOM_CACHE is not None:
        return _ATOM_CACHE
    m = {}
    for name in LANES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        for (page, step), pipeline in getattr(mod, "PIPELINES", {}).items():
            if step == "kpi":
                for a in pipeline:
                    if a["kind"] == "det":
                        m[page] = a["fn"]
    _ATOM_CACHE = m
    return m


def load_contract(path=None):
    return json.load(open(path or CONTRACT))


_REDUCE = {"min": min, "max": max, "mean": lambda v: sum(v) / len(v)}


def evaluate(entry, state):
    """Honest per-workflow verdict. Value comes from the lane's own kpi atom."""
    fn = atoms().get(entry["workflow"])
    if fn is None:
        return {"status": "no_atom", "workflow": entry["workflow"]}
    out = fn(dict(state)) or {}
    if out.get("kpi") != "computed":
        return {"status": "insufficient_data", "min_n": entry["min_n"],
                "have": out.get("n", out.get("booked", 0))}
    val = out[entry["metric"]]
    if isinstance(val, dict):  # per-mode dict (c3) -> reduce to a scalar
        val = _REDUCE[entry.get("reduce", "min")](list(val.values()))
    d = entry["dir"]
    if d == "eq":
        met = val == entry["target"]
    elif d == "min":
        met = val <= entry["target"]
    else:
        met = val >= entry["target"]
    return {"status": "met" if met else "unmet", "value": val,
            "target": entry["target"], "dir": d}


def evaluate_all(receipts, contract=None):
    """receipts: {workflow: state}. Returns {workflow: verdict}."""
    contract = contract or load_contract()
    return {e["workflow"]: evaluate(e, receipts.get(e["workflow"], {})) for e in contract}


def acceptance_run(contract=None, acc_path=None):
    contract = contract or load_contract()
    acc = json.load(open(acc_path or ACCEPTANCE))
    return {e["workflow"]: evaluate(e, acc[e["workflow"]]["met"]) for e in contract}


def _queue_receipts(include_unproven=False):
    """Real production receipts from the run queue, grouped by workflow's samples_key.
    Rows carrying the v1 execution envelope are production evidence only when source=trigger
    and fixture=false. Legacy rows without an envelope remain readable for local diagnosis, but
    are excluded from the production KPI report by default — never silently promoted."""
    import atoms
    receipts = {}
    path = os.environ.get("FOUNDRY_RECEIPTS_PATH") or atoms.RECEIPTS
    if not os.path.exists(path):
        return {}
    seen_ids = set()
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        rid = row.get("receipt_id")
        if rid:
            if rid in seen_ids:
                continue  # replayed receipt (same run identity): never double-count
            seen_ids.add(rid)
        wf = row.get("workflow")
        if not (wf and row.get("receipt")):
            continue
        execution = row["receipt"].get("execution")
        if execution is not None:
            if execution.get("source") != "trigger" or execution.get("fixture") is True:
                continue
        elif not include_unproven:
            continue
        acc = receipts.setdefault(wf, {})
        for k, v in row["receipt"].get("samples", {}).items():
            # ACCRUE list samples across terminal receipts: each row is one run's FRESH state slice
            # (state resets per run), so plain concatenation is correct accrual — recurring
            # identical verdicts are legitimate new samples. Scalars: latest wins.
            if isinstance(v, list):
                acc.setdefault(k, []).extend(v)
            else:
                acc[k] = v
    return receipts


def summary(verdicts):
    c = {"met": 0, "unmet": 0, "insufficient_data": 0, "no_atom": 0}
    for v in verdicts.values():
        c[v["status"]] = c.get(v["status"], 0) + 1
    return c


if __name__ == "__main__":
    contract = load_contract()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "contract":
        print(json.dumps(contract, indent=1))
    elif cmd == "acceptance":
        res = acceptance_run(contract)
        print(json.dumps({"summary": summary(res), "verdicts": res}, indent=1))
        sys.exit(1 if any(r["status"] != "met" for r in res.values()) else 0)
    else:  # report: honest production status
        res = evaluate_all(_queue_receipts(), contract)
        print(json.dumps({"summary": summary(res), "verdicts": res,
                          "note": "insufficient_data is honest pre-launch state, not a failure"}, indent=1))
