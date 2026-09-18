"""Bridge from this MCP server to the System-1 gate (Jev / s1gate) runtime.

Why a bridge and not a re-implementation: the gate's rules, thresholds,
confidence floors and fail-closed behaviour live in ``rig_capabilities.s1gate``
and are exercised by ``bin/rig-s1gate``. This module calls those same library
functions, so an MCP answer can never disagree with the CLI -- the same
principle ``capabilities_verdict`` and ``comms_bridge`` follow.

Three constraints carried through the bridge, not weakened by it:

* **stdout is the JSON-RPC channel.** Nothing here prints; every verb returns a
  dict. Any stray stdout/stderr from a callee is captured and reported, never
  written to the transport.
* **Law 3 stays human-only.** ``calibrate`` is exposed as a dry measurement.
  Flipping a rubric to enforcing writes into a governed artifact, so there is
  deliberately no ``write`` argument on this tool.
* **Law 6 unchanged.** A PASS returned here is "the measured bar was met",
  never an authorisation to publish, spend, or deploy.

Cost note for callers: ``check``, ``rank`` and ``improve`` make live Jev calls
(measured 200-910 ms each from Denver, a fraction of a cent). ``list``,
``show``, ``stats``, ``recent``, ``review``, ``label``, ``calibrate`` and
``selftest`` are free -- and ``selftest`` is the one to call when the question
is "is the gate actually wired up?".
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .mcp_stdio import ToolError

ACTIONS = ("list", "show", "check", "rank", "improve", "stats", "recent",
           "review", "label", "calibrate", "selftest")

#: Verbs that spend a live Jev call. One place, so the tool description and the
#: caps below cannot drift apart.
BILLABLE = ("check", "rank", "improve")

MAX_ARTIFACT_CHARS = 60_000
MAX_RANK_CANDIDATES = 25
MAX_IMPROVE_ITERATIONS = 5

_ALLOWED_KEYS = {"action", "rubric", "text", "subject", "model", "candidates",
                 "context", "max_iterations", "accept", "decision_id", "label",
                 "signal", "direction", "max_false_block_rate", "min_recall",
                 "limit", "unlabelled"}


# ---------------------------------------------------------------- helpers --

def _state(args: Dict[str, Any]) -> str:
    text = args.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ToolError("`text` is required and must be a non-empty string: the "
                        "artifact being judged (a draft, a diff, a plan).")
    if len(text) > MAX_ARTIFACT_CHARS:
        raise ToolError(f"artifact too large for one gate call ({len(text)} "
                        f"chars > {MAX_ARTIFACT_CHARS}). Score a section, or use "
                        "the CLI on a file.")
    return text


def _with_log(fn):
    """Run fn(log) with a DecisionLog open, closing it whatever happens."""
    from .s1gate import DecisionLog
    log = DecisionLog()
    try:
        return fn(log)
    finally:
        log.close()


# ------------------------------------------------------------------ reads --

def _list(_args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate import S1GateError, list_rubrics, load_rubric
    rows: List[Dict[str, Any]] = []
    for name in list_rubrics():
        try:
            rb = load_rubric(name)
        except S1GateError as exc:
            rows.append({"rubric": name, "error": str(exc)})
            continue
        rows.append({"rubric": rb.name, "stage": rb.stage, "lane": rb.lane,
                     "mode": "ENFORCING" if rb.calibrated else "advisory",
                     "never_auto": rb.never_auto,
                     "questions": len(rb.questions),
                     "description": rb.description})
    return {"count": len(rows), "rubrics": rows,
            "enforcing": [r["rubric"] for r in rows
                          if r.get("mode") == "ENFORCING"]}


def _show(args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate import load_rubric
    rb = load_rubric(args["rubric"])
    return {"name": rb.name, "stage": rb.stage, "lane": rb.lane,
            "calibrated": rb.calibrated, "never_auto": rb.never_auto,
            "confidence_floor": rb.confidence_floor,
            "questions": list(rb.questions), "rules": rb.rules,
            "calibration": rb.calibration,
            "law_5_note": "Thresholds are visible here because the CLI shows "
                          "them. An artifact's author still must not tune a "
                          "draft against them -- the calibration set stays "
                          "on the human side."}


def _stats(args: Dict[str, Any]) -> Dict[str, Any]:
    def run(log):
        rubric = args.get("rubric") or None
        counts = log.counts(rubric)
        if not counts:
            return {"rubric": rubric or "ALL", "total": 0, "verdicts": {},
                    "labelled": 0, "note": "no decisions recorded yet"}
        total = sum(counts.values())
        if rubric:
            labelled = len(log.labelled(rubric))
        else:
            from .s1gate import list_rubrics
            labelled = sum(len(log.labelled(r)) for r in list_rubrics())
        return {"rubric": rubric or "ALL", "total": total, "verdicts": counts,
                "labelled": labelled,
                "unlabelled": total - labelled,
                "calibration_note": "a rubric is calibratable once its labelled "
                                    "corpus is big enough to measure against; "
                                    "see action=calibrate (dry run)"}
    return _with_log(run)


def _recent(args: Dict[str, Any]) -> Dict[str, Any]:
    def run(log):
        rows = log.recent(rubric=args.get("rubric") or None,
                          n=min(int(args.get("limit", 20)), 100),
                          unlabelled=bool(args.get("unlabelled")))
        return {"count": len(rows), "rows": [
            {"id": r["id"], "ts": r["ts"], "rubric": r["rubric"],
             "verdict": r["verdict"], "label": r["label"],
             "subject": r["subject"], "advisory": bool(r["advisory"]),
             "model": r["model"], "latency_ms": r["latency_ms"]} for r in rows]}
    return _with_log(run)


def _review(args: Dict[str, Any]) -> Dict[str, Any]:
    def run(log):
        r = log.get(int(args["decision_id"]))
        if not r:
            raise ToolError(f"no decision with id {args['decision_id']}")
        return {"id": r["id"], "rubric": r["rubric"], "verdict": r["verdict"],
                "advisory": bool(r["advisory"]), "label": r["label"],
                "subject": r["subject"], "model": r["model"],
                "latency_ms": r["latency_ms"], "error": r["error"],
                "state_sha256": r["state_sha256"],
                "state_preview": r["state_preview"],
                "answers": json.loads(r["answers_json"] or "{}"),
                "reasons": json.loads(r["reasons_json"] or "[]")}
    return _with_log(run)


def _label(args: Dict[str, Any]) -> Dict[str, Any]:
    lab = str(args.get("label") or "").strip().lower()
    if lab not in ("good", "bad"):
        raise ToolError("label must be 'good' or 'bad'")

    def run(log):
        did = int(args["decision_id"])
        if not log.get(did):
            raise ToolError(f"no decision with id {did}")
        log.label(did, lab, by="mcp-agent")
        return {"decision_id": did, "label": lab, "labelled_by": "mcp-agent",
                "note": "labelled for calibration, and stamped as an agent label "
                        "rather than a human one -- law 5 puts the calibration set "
                        "on the human side, so a human review of this label is "
                        "still what makes a threshold trustworthy"}
    return _with_log(run)


# ----------------------------------------------------------------- spend --

def _check(args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate import evaluate
    text = _state(args)

    def run(log):
        return evaluate(args["rubric"], text, subject=args.get("subject"),
                        log=log, model=args.get("model") or None)

    res = _with_log(run)
    out = res.to_dict()
    out["verdict_contract"] = {"PASS": "bar met, proceed",
                               "ESCALATE": "hand to a human or a System 2 model",
                               "BLOCK": "stop"}
    out["enforced_note"] = ("advisory: annotates only, cannot stop anything"
                            if res.advisory else "enforcing")
    out["law_6"] = "a machine PASS is not an authorisation to publish, spend or deploy"
    return out


def _rank(args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate_improve import rank
    cands = [str(c) for c in (args.get("candidates") or []) if str(c).strip()]
    if len(cands) < 2:
        raise ToolError("rank needs at least 2 candidates. One artifact is "
                        "`check`, not `rank`.")
    if len(cands) > MAX_RANK_CANDIDATES:
        raise ToolError(f"rank capped at {MAX_RANK_CANDIDATES} candidates, got "
                        f"{len(cands)} -- that would be {len(cands)} live Jev "
                        "calls inside one tool turn.")

    def run(log):
        return rank(args["rubric"], cands, subject=args.get("subject"), log=log)

    rows = _with_log(run)
    return {"rubric": args["rubric"], "count": len(rows),
            "best_index": rows[0]["index"] if rows else None,
            "results": [{"rank": i + 1, "index": r["index"],
                         "verdict": r["verdict"], "tripped": r["tripped"],
                         "reasons": r["reasons"], "preview": r["text"][:180]}
                        for i, r in enumerate(rows)],
            "note": "ranked best-first by verdict severity. Ranking needs no "
                    "calibration -- it is the safest verb to call first."}


def _improve(args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate import ESCALATE, PASS
    from .s1gate_improve import improve
    text = _state(args)
    accept = {"PASS": PASS, "ESCALATE": ESCALATE}.get(
        str(args.get("accept") or "PASS").upper())
    if accept is None:
        raise ToolError("accept must be PASS or ESCALATE")
    mx = int(args.get("max_iterations", 3))
    if not 1 <= mx <= MAX_IMPROVE_ITERATIONS:
        raise ToolError(f"max_iterations capped at 1..{MAX_IMPROVE_ITERATIONS} "
                        "(each loop is live Jev calls plus a rewriter run)")

    def run(log):
        return improve(args["rubric"], text,
                       context=str(args.get("context") or ""),
                       max_iterations=mx, accept=accept,
                       subject=args.get("subject"), log=log)

    res = _with_log(run)
    out = res.to_dict()
    out.pop("original", None)
    out["rewriter"] = "local ladder first, claude CLI only as fallback"
    out["law_6"] = "the returned text is a draft, not a clearance"
    return out


def _calibrate(args: Dict[str, Any]) -> Dict[str, Any]:
    from .s1gate_calibrate import calibrate_rubric, report
    signal = str(args.get("signal") or "")
    if "." not in signal:
        raise ToolError("signal must look like question.attr, e.g. "
                        "weakened_test.noul")
    q, attr = signal.split(".", 1)
    result = calibrate_rubric(
        args["rubric"], (q, attr),
        direction=str(args.get("direction") or "above"),
        max_false_block_rate=float(args.get("max_false_block_rate", 0.05)),
        min_recall=float(args.get("min_recall", 0.50)),
        write=False)
    return {"rubric": args["rubric"], "signal": signal, "dry_run": True,
            "certified": result["certified"], "report": report(result),
            "to_enforce": "this tool cannot flip a gate to enforcing (law 3). "
                          f"A human runs: rig-s1gate calibrate {args['rubric']} "
                          f"--signal {signal} --write"}


def _selftest(_args: Dict[str, Any]) -> Dict[str, Any]:
    """The gate's own no-network proof, run through its CLI unchanged.

    Subprocess, not import: stdout here is the JSON-RPC channel and the CLI
    prints. Captured output is reported, never forwarded.
    """
    script = Path(__file__).resolve().parent.parent / "bin" / "rig-s1gate"
    if not script.is_file():
        raise ToolError(f"selftest needs the CLI at {script}")
    try:
        cp = subprocess.run([str(script), "selftest"], capture_output=True,
                            text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"ran": False, "reason": "selftest timed out (60s)",
                "fail_closed": True}
    return {"ran": cp.returncode == 0, "exit_code": cp.returncode,
            "stdout": cp.stdout[-3000:], "stderr": cp.stderr[-1500:],
            "meaning": "exit 0 = rule engine and the fail-closed path both "
                       "verified without a single Jev call"}


# -------------------------------------------------------------- dispatch --

_HANDLERS = {"list": _list, "show": _show, "check": _check, "rank": _rank,
             "improve": _improve, "stats": _stats, "recent": _recent,
             "review": _review, "label": _label, "calibrate": _calibrate,
             "selftest": _selftest}


def s1gate(args: Dict[str, Any]) -> Dict[str, Any]:
    """One tool, eleven verbs, each one the gate's own implementation."""
    action = str(args.get("action") or "")
    if action not in ACTIONS:
        return {"ran": False, "action": action or "(missing)",
                "reason": f"unknown_action:{action or '(missing)'}",
                "actions": list(ACTIONS), "billable": list(BILLABLE)}
    if action in ("show", "check", "rank", "improve", "calibrate") \
            and not str(args.get("rubric") or "").strip():
        raise ToolError(f"`rubric` is required for action={action}. "
                        "Call action=list to see the live pack set.")
    if action in ("show", "check", "rank", "improve", "calibrate"):
        # Name the rubric before spending a live call or failing on a later
        # argument: an agent that typos `post.linkeind` should be told which
        # packs exist, not asked for the text it already sent.
        from .s1gate import list_rubrics
        if args["rubric"] not in list_rubrics():
            raise ToolError(f"no rubric named {args['rubric']!r}. Packs: "
                            + ", ".join(list_rubrics()))
    extra = set(args) - _ALLOWED_KEYS
    if extra:
        raise ToolError(f"s1gate: unknown keys {sorted(extra)} refused "
                        "(closed schema)")

    so, se = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
            out = _HANDLERS[action](args)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001 -- a gate failure is data, not a crash
        return {"ran": False, "action": action, "rubric": args.get("rubric"),
                "reason": f"{type(exc).__name__}: {exc}",
                "fail_closed": True,
                "stdout": so.getvalue()[-2000:], "stderr": se.getvalue()[-2000:],
                "hint": "fail-closed: an unrun gate is never a pass. If the "
                        "reason names a provider error, check the Jev API and "
                        "the TYPESAFE_API_KEY keychain item, then action=selftest."}
    out["ran"] = True
    out["action"] = action
    if so.getvalue() or se.getvalue():
        out["stray_output"] = (so.getvalue() + se.getvalue())[-2000:]
    return out
