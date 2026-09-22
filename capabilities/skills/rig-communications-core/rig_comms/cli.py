"""`rig-comm` — one CLI: route | packet | score | voice-check | loop | ledger | media | doctor.

Deterministic stdlib. Exit codes: 0 ok/green · 2 gate red · 3 privacy lock ·
4 bad input. Writes are appended to the ledgers in rig_comms.ledger.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import ledger, packets, surfaces, voice
from .gates import run as gate_run


def _read_artifact(path: str) -> str:
    return Path(path).read_text(encoding="utf-8") if path and path != "-" else sys.stdin.read()


def cmd_surfaces(_a):
    print(json.dumps({s.id: {"lane": s.lane, "agf_min": s.agf_min, "sigma": s.sigma_target,
                             "rubric": s.rubric, "budget": s.budget, "bx": list(s.bx),
                             "engines": list(s.engines)}
                      for s in surfaces.SURFACES.values()}, indent=2))
    return 0


def cmd_route(a):
    hits = surfaces.route(a.intent)
    print(json.dumps(hits or [{"fallback": "no keyword hit", "hint": "name the surface explicitly"}],
                     indent=2))
    return 0


def cmd_packet(a):
    s = surfaces.resolve(a.surface)
    if s is None:
        print(f"unknown surface: {a.surface}", file=sys.stderr)
        return 4
    if s.lane == "private" and not a.human:
        print("PRIVATE LANE: love-notes packets require --human (never autonomous).", file=sys.stderr)
        return 3
    persona = ""
    if a.persona:
        pp = ledger.data_root() / "personas" / f"{a.persona}.md"
        if s.id == "love-notes":  # private personas live OUTSIDE the repo, always
            pp = Path.home() / ".rig" / "comms" / "personas-private" / f"{a.persona}.md"
        persona = pp.read_text(encoding="utf-8") if pp.exists() else f"(persona file missing: {pp})"
    print(packets.build_packet(s.id, _read_artifact(a.brief), persona, surface=s))
    return 0


def cmd_score(a):
    return gate_run(a.surface, _read_artifact(a.artifact))


def cmd_voice(a):
    card = voice.score_voice(_read_artifact(a.artifact))
    if a.baseline:
        card = voice.drift(_read_artifact(a.artifact), json.loads(Path(a.baseline).read_text()))
    print(json.dumps(card, indent=2))
    return {"BLOCK": 2, "REVISE": 2}.get(card.get("verdict", card.get("scorecard", {}).get("verdict")), 0)


def _trace(surface: str, kind: str, artifact: str, result: str) -> None:
    """v18.1: one RLM-compatible trace line per loop event, per surface-agent
    (rig-comms-<surface>), into ~/.rig/prime-agent-traces/. Deterministic."""
    import time
    rows = [r for r in ledger._read("loops.jsonl") if r.get("artifact") == artifact]
    line = {"agent": f"rig-comms-{surface}", "task": f"{kind}:{artifact}",
            "turn": len(rows) + 1, "tool": "gate_stack", "result": result,
            "duration_ms": 0, "ts": int(time.time())}
    d = Path.home() / ".rig" / "prime-agent-traces"
    d.mkdir(parents=True, exist_ok=True)
    with (d / "rig-comms.jsonl").open("a") as fh:
        fh.write(json.dumps(line) + "\n")


def cmd_loop(a):
    """v8 closed loop: start/correction/ship/escalate telemetry with the
    max-3 correction latch. A 4th correction on the same artifact REFUSES
    and forces human escalation (tac-closing-loop rule, enforced in code)."""
    detail = json.loads(a.detail) if a.detail else {}
    if a.kind == "correction":
        prior = sum(1 for r in ledger._read("loops.jsonl")
                    if r.get("event") == "correction" and r.get("artifact") == a.artifact
                    and r.get("surface") == a.surface)
        if prior >= 3:
            ledger.loop_event("escalate", a.surface, a.artifact,
                              {"reason": "max-3 corrections reached"})
            print(json.dumps({"refused": True, "corrections_so_far": prior,
                              "escalated": True,
                              "instruction": "Loop budget spent. Stop the build loop and "
                                             "escalate to Mike — a 4th auto-correction is "
                                             "not permitted (v8.3)."}))
            _trace(a.surface, "correction_refused", a.artifact, "error")
            return 5
    p = ledger.loop_event(a.kind, a.surface, a.artifact, detail)
    if a.trace:
        _trace(a.surface, a.kind, a.artifact, "success")
    print(str(p))
    return 0


def cmd_ship(a):
    """v8.4/8.8/8.9: nothing is 'shipped' without a sealed artifact packet.
    Re-runs the gate stack NOW (fresh evidence, not a past verdict), stamps
    sha256 + gate JSON + real_path=PENDING, appends ship telemetry. Red = refused."""
    text = _read_artifact(a.artifact)
    code = gate_run(a.surface, text)
    if code != 0:
        print(json.dumps({"shipped": False, "reason": f"gate exit {code} — fix or escalate, then ship"}))
        return code
    import hashlib, time as _t
    from .gates import evaluate_stack
    from . import surfaces as _sur
    s = _sur.resolve(a.surface)
    out = evaluate_stack(s, text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    packet = {"surface": s.id, "sha256": digest, "gate": out,
              "real_path_status": "PENDING",  # v8.8: flip after published URL fetched logged-out
              "ts": _t.strftime("%Y-%m-%dT%H:%M:%S%z")}
    path = ledger.data_root() / "ships" / f"{_t.strftime('%Y%m%d-%H%M%S')}-{s.id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2))
    ledger.loop_event("ship", s.id, a.artifact, {"sha256": digest, "packet": str(path)})
    print(json.dumps({"shipped": True, "packet": str(path), "sha256": digest,
                      "gate_d": out["gate_d_required"]}))
    return 0


def cmd_ledger(a):
    if a.op == "outcome":
        p = ledger.record_outcome(a.surface, a.channel, json.loads(a.metrics), a.source)
    elif a.op == "predict":
        p = ledger.predict(a.surface, a.id, json.loads(a.p), a.claim)
    elif a.op == "resolve":
        p = ledger.resolve(a.surface, a.id, a.outcome, a.evidence)
    elif a.op == "report":
        print(json.dumps({"loop_telemetry": ledger.loop_report(),
                          "drafted_vs_shipped": ledger.drafted_vs_shipped(),
                          **ledger.calibration_report(),
                          "recalibration": ledger.recalibration_proposals()}, indent=2))
        return 0
    else:
        print(f"unknown op: {a.op}", file=sys.stderr)
        return 4
    print(str(p))
    return 0


def cmd_media(a):
    print(str(ledger.media_record(a.artifact, a.kind, a.path, a.generator, a.provenance)))
    return 0


HARNESS_ROOTS = {"claude": ".claude", "codex": ".codex", "hermes": ".hermes", "agents": ".agents"}
COMMS_SKILLS = ["rig-communications-core", "rig-communications-doctrine", "rig-communications-wounds",
                "rig-communications-behavior", "rig-communications-voice"]


def cmd_doctor(_a):
    """v9.9: every harness must load the identical comms version. Drift = red."""
    report, red = {}, False
    for skill in COMMS_SKILLS:
        canon = Path(__file__).resolve().parents[2] / skill / "SKILL.md"
        want = hashlib.sha256(canon.read_bytes()).hexdigest()[:12] if canon.exists() else None
        per = {}
        for harness, root in HARNESS_ROOTS.items():
            p = Path.home() / root / "skills" / skill / "SKILL.md"
            if not p.exists():
                per[harness] = "MISSING"
                red = True
            else:
                got = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                per[harness] = "OK" if got == want else f"DRIFT({got})"
                red = red or got != want
        report[skill] = {"canonical": want, "harnesses": per}
    print(json.dumps({"drift": red, "skills": report}, indent=2))
    return 2 if red else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="rig-comm")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("surfaces").set_defaults(fn=cmd_surfaces)
    r = sub.add_parser("route"); r.add_argument("intent")
    r.set_defaults(fn=cmd_route)
    p = sub.add_parser("packet"); p.add_argument("--surface", required=True)
    p.add_argument("--brief", default="-"); p.add_argument("--persona", default="")
    p.add_argument("--human", action="store_true")
    p.set_defaults(fn=cmd_packet)
    s = sub.add_parser("score"); s.add_argument("--surface", required=True)
    s.add_argument("--artifact", default="-"); s.set_defaults(fn=cmd_score)
    l = sub.add_parser("loop"); l.add_argument("kind", choices=["start", "correction", "ship", "escalate"])
    l.add_argument("--surface", required=True); l.add_argument("--artifact", default="")
    l.add_argument("--detail", default="")
    l.add_argument("--trace", action="store_true", help="append RLM trace line (v18.1)")
    l.set_defaults(fn=cmd_loop)
    sh = sub.add_parser("ship"); sh.add_argument("--surface", required=True)
    sh.add_argument("--artifact", required=True); sh.set_defaults(fn=cmd_ship)
    g = sub.add_parser("ledger")
    g.add_argument("op", choices=["outcome", "predict", "resolve", "report"])
    g.add_argument("--surface", default=""); g.add_argument("--channel", default="")
    g.add_argument("--metrics", default="{}"); g.add_argument("--source", default="")
    g.add_argument("--id", default=""); g.add_argument("--p", default="{}")
    g.add_argument("--claim", default=""); g.add_argument("--outcome", default="")
    g.add_argument("--evidence", default=""); g.set_defaults(fn=cmd_ledger)
    m = sub.add_parser("media"); m.add_argument("--artifact", required=True)
    m.add_argument("--kind", required=True); m.add_argument("--path", required=True)
    m.add_argument("--generator", required=True); m.add_argument("--provenance", default="")
    m.set_defaults(fn=cmd_media)
    d = sub.add_parser("doctor"); d.set_defaults(fn=cmd_doctor)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
