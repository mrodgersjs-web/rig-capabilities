"""Real-time Foundry status — which process-map workflows are LIVE, BUILT, DEGRADED, or NOT.

Per board page (taxonomy from the real .tldr via design_audit; liveness from run receipts):
  live         a run receipt within the TTL reached a valid terminal (complete or an expected
               human-gate/hold); for LLM lanes the run was LIVE-mode (real inference), not mock.
  built        deep-dive atoms + KPI met on the acceptance run, but no recent run -> not proven live.
  degraded     has atoms but its KPI is not met on the acceptance run (a build regression).
  not_working  drawn on the board with no deep-dive pipeline (the A1 intake layer).
  overview     nav/overview page, not an executable workflow.

'live' is NEVER inferred from static state — only from a recent, real run recorded by
deepdive.record_run(). Acceptance/tests prove 'built', never 'live'. Recomputed every call, so a
dashboard polling status() shows real-time truth (pages fade built->live on run, live->built on TTL).
"""
import json, os, socket, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
import deepdive
import kpis

RUNLOG = os.path.join(ROOT, ".data", "foundry-runs.jsonl")


def _load(mod_path, name):
    sp = importlib.util.spec_from_file_location(name, mod_path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def model_up(host=None, port=None, timeout=0.6):
    """Informational reachability of the live model — NOT the basis for 'live'."""
    host = host or os.environ.get("FOUNDRY_MODEL_HOST", "192.168.68.90")
    port = int(port or os.environ.get("FOUNDRY_MODEL_PORT", "8011"))
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def recent_runs(ttl=600, now=None, path=None):
    """Latest run receipt per page within ttl seconds — the sole basis for 'live'."""
    p = path or RUNLOG
    now = now if now is not None else time.time()
    latest = {}
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            page, ts = r.get("page"), r.get("ts", 0)
            if page and (now - ts) <= ttl and (page not in latest or ts > latest[page]["ts"]):
                latest[page] = r
    return latest


def status(ttl=600, now=None):
    reg = deepdive.load()
    census = deepdive.census(reg)["by_page"]
    contract_list = kpis.load_contract()
    contract = {e["workflow"]: e for e in contract_list}
    acc = kpis.acceptance_run(contract_list)
    prod = kpis.evaluate_all(kpis._queue_receipts(), contract_list)
    # The design audit reads the tldraw board from .data/, which is deliberately NOT packaged into
    # a deploy image (10MB of local editor state, and it is not shared across workers). Its absence
    # is a known environment fact, not a crash: without it we cannot classify functional vs
    # overview pages, so we say so instead of guessing either way.
    buckets, board = {}, "present"
    try:
        da = _load(os.path.join(ROOT, "tools", "foundry-gaps", "design_audit.py"), "design_audit")
        buckets = da.audit()["page_lists"]
    except FileNotFoundError:
        board = "unavailable"
    except Exception as e:
        board = "error:" + type(e).__name__
    up = model_up()
    now = now if now is not None else time.time()
    runs = recent_runs(ttl, now)

    def code(pid):
        return pid.replace("page:", "").split("-")[0]

    workflows = {}

    def add(pid, functional):
        c = code(pid)
        cen = census.get(c, {})
        has_llm = cen.get("llm", 0) > 0
        acceptance_kpi = acc.get(c, {}).get("status")
        production_kpi = prod.get(c, {}).get("status", "insufficient_data")
        run = runs.get(c)
        real_infer = bool(run and run.get("mode") not in (None, "mock") and run.get("produced_llm", 0) > 0)
        live = bool(run and run.get("ok") and ((not has_llm) or real_infer))
        source = (run or {}).get("source", "local")
        if not functional:
            state = "not_working"
        elif production_kpi != "met":
            state = "built_unexercised"
        elif live and source == "trigger":
            state = "trigger-live"  # end-to-end: real inference + real Trigger dispatch
        elif live:
            state = "model-live"    # real model output, but driven locally (no Trigger proof)
        else:
            state = "det-local"     # deterministic pass, no LLM production evidence
        workflows[pid] = {"page": pid, "code": c, "state": state,
                          "kpi": acceptance_kpi,
                          "acceptance_kpi": acceptance_kpi,
                          "production_kpi": production_kpi,
                          "has_llm": has_llm,
                          "lane": (contract.get(c) or {}).get("lane", "?"),
                          "last_run": ({"terminal": run.get("terminal"), "mode": run.get("mode"),
                                        "age_s": round(now - run["ts"])} if run else None)}

    if buckets:
        for pid in buckets["functional"] + buckets["validator_only"]:
            add(pid, True)
        for item in buckets["non_functional"]:
            add(item["page"], False)
        for pid in buckets["overview"]:
            workflows[pid] = {"page": pid, "code": code(pid), "state": "overview", "lane": "nav"}
    else:
        # FAIL CLOSED. The board audit is what distinguishes functional from validator_only and
        # non_functional, so without it `functional` is UNKNOWN — not True. Asserting True here
        # would silently promote a not_working page to built/degraded, which is precisely the
        # false-green this status board exists to prevent. No page may be built or live without
        # design-audit evidence.
        for c in sorted(contract):
            run = runs.get(c)
            workflows["page:" + c] = {
                "page": "page:" + c, "code": c, "state": "audit_unavailable",
                "kpi": acc.get(c, {}).get("status"),
                "acceptance_kpi": acc.get(c, {}).get("status"),
                "production_kpi": prod.get(c, {}).get("status", "insufficient_data"),
                "has_llm": census.get(c, {}).get("llm", 0) > 0,
                "lane": (contract.get(c) or {}).get("lane", "?"),
                "reason": "design-audit input unavailable: " + board,
                "last_run": ({"terminal": run.get("terminal"), "mode": run.get("mode"),
                              "age_s": round(now - run["ts"])} if run else None)}

    summary = {}
    for v in workflows.values():
        summary[v["state"]] = summary.get(v["state"], 0) + 1
    return {"model_up": up, "ttl_s": ttl, "generated_at": now, "workflows": workflows,
            "board": board, "page_source": "board" if buckets else "kpi-contract",
            "summary": summary, "counts": {"total_pages": len(workflows)}}


if __name__ == "__main__":
    print(json.dumps(status(), indent=1, default=str))
