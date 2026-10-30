#!/usr/bin/env python3
"""calibrate_all -- move s1gate rubrics from advisory to ENFORCING, in waves,
and say exactly why the rest cannot move yet.

Motivation (measured 2026-10-01 09:13 MDT):
    109 rubrics, 0 ENFORCING, 41.7% overall escalation.
    2,019 whole-decision labels and 624 signal labels exist in total.
    MIN_LABELLED = 30, and a rule needs >=5 good AND >=5 bad to certify.

That last line is the whole constraint. Calibration is not something to
"finish" by pressing harder -- it is gated on ground truth, and ground truth is
a thing a human has to supply. So this driver does three honest things:

  1. CERTIFY what has ground truth (writes the threshold + certification).
  2. SKIP the five gap packs that tests/test_s1gate.py requires to stay
     uncalibrated. Hard-coded, with the test cited, so nobody "fixes" it.
  3. Emit one BLOCKED line per remaining rubric with its exact label budget.

It never invents a label. The two legal label sources are:
  * a human, via `rig-s1gate label <id> good|bad [--signal Q.ATTR]`;
  * a human-authored expected answer in a case file, transcribed mechanically
    the way jev-levels/calibrate_waves.py already does it (labelled_by
    `suite:...`). The expected answer is human; only the transcription is code.

A model writing its own answer key is the corruption this whole harness exists
to prevent, so there is no path here that does that.

Usage
-----
  calibrate_all.py               scan + report (writes nothing)
  calibrate_all.py --write       certify everything READY, report the rest
  calibrate_all.py --waves       also run jev-levels/calibrate_waves.py --write
                                 (the 10 jev.* rubrics, 336 human-authored cases)
  calibrate_all.py --report F    write the machine-readable report to F

Exit: 0 everything in scope certified, 1 anything BLOCKED, 3 usage/config.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from rig_capabilities.s1gate import (  # noqa: E402
    DecisionLog, list_rubrics, load_rubric, _rule_signal,
)
from rig_capabilities.s1gate_calibrate import MIN_LABELLED, _extract, calibrate_rubric  # noqa: E402

HERE = Path(__file__).resolve().parent
LEVELS = HERE / "jev-levels"

# tests/test_s1gate.py::test_work_criteria_map_covers_every_rubric_and_rejects_unknown
# asserts these five are NOT calibrated. Calibrating them breaks a shipped test.
# If you believe that has changed, change the TEST first, with Mike's yes.
MUST_STAY_UNCALIBRATED = {
    "routine.run", "youtube.scrape", "board.card", "fusion.check", "form.field",
}

# The 10 rubrics with a human-authored 336-case suite in jev-levels/.
# (question, attr, direction, bad-options) -- mirrors calibrate_waves.PLAN.
SUITE_PLAN = {
    "jev.escalation":       ("needs_reasoning", "p.yes", "above", {"yes"}),
    "jev.triage":           ("lane", "confidence", "below", set()),
    "jev.scrape-classify":  ("category", "confidence", "below", set()),
    "jev.auto-approve":     ("risk", "p.yes", "above", {"yes"}),
    "jev.skill-router":     ("skill", "confidence", "below", set()),
    "jev.bash-gate":        ("destructive_irreversible", "p.yes", "above", {"yes"}),
    "jev.file-triage":      ("credential_bearing", "p.yes", "above", {"cred"}),
    "jev.compact-read":     ("compact_is_safe", "p.no", "above", {"no"}),
    "jev.injection-screen": ("instruction_override", "p.yes", "above", {"yes"}),
    "jev.gate-d":           ("outward_or_irreversible", "p.yes", "above", {"yes"}),
}


def scan() -> dict:
    """Classify every RULE SIGNAL independently. Read-only.

    Signal-first, not rubric-first: `calibrate_rubric` certifies one rule signal
    at a time and only rolls up to whole-rubric `calibrated` when every signal
    has its own entry. Scanning per-rubric understated readiness badly -- a
    first pass reported 2 ready when 11 signals were actually certifiable,
    because one unlabelled sibling signal dragged the whole rubric down.
    """
    log = DecisionLog()
    signals_ready, signals_blocked = [], []
    skipped = []
    rubric_meta: dict = {}
    try:
        for name in sorted(list_rubrics()):
            if name in MUST_STAY_UNCALIBRATED:
                skipped.append({
                    "rubric": name,
                    "why": "tests/test_s1gate.py requires this to stay uncalibrated",
                })
                continue
            try:
                rb = load_rubric(name)
            except Exception as exc:  # noqa: BLE001
                signals_blocked.append({"rubric": name, "signal": "-",
                                        "reason": f"load error: {exc}",
                                        "need": 0, "label_scope": "-"})
                continue
            if not rb.rules:
                signals_blocked.append({"rubric": name, "signal": "-",
                                        "reason": "no rules to certify",
                                        "need": 0, "label_scope": "-"})
                continue

            needs_sig = (len(rb.questions) > 1
                         or len({_rule_signal(r) for r in rb.rules}) > 1)
            label_scope = "signal" if needs_sig else "decision"
            rubric_meta[name] = {"label_scope": label_scope,
                                 "n_signals": len(rb.rules),
                                 "in_suite": name in SUITE_PLAN}

            for r in rb.rules:
                sig = _rule_signal(r)
                base = {"rubric": name, "signal": sig or "-",
                        "label_scope": label_scope,
                        "in_suite": name in SUITE_PLAN}
                if not sig:
                    signals_blocked.append({**base, "need": 0,
                                            "reason": "rule has no bindable signal"})
                    continue
                qname, attr = sig.split(".", 1)
                rows = (log.labelled_signal(name, sig) if needs_sig
                        else log.labelled(name))
                pairs = _extract(rows, qname, attr)
                n_bad = sum(1 for _, l in pairs if l == "bad")
                n_good = len(pairs) - n_bad
                models = sorted({x["model"] or "" for x in rows})
                need = max(0, MIN_LABELLED - len(pairs))
                base.update({"labelled": len(pairs), "good": n_good,
                             "bad": n_bad, "need": need, "models": models})

                if len(pairs) < MIN_LABELLED:
                    base["reason"] = (f"{len(pairs)} labelled, need {MIN_LABELLED} "
                                      f"(good {n_good}/bad {n_bad})")
                    signals_blocked.append(base)
                elif n_bad < 5 or n_good < 5:
                    base["reason"] = (f"good={n_good} bad={n_bad}, need >=5 of each "
                                      f"to tell the classes apart")
                    signals_blocked.append(base)
                elif len(models) != 1 or not models[0]:
                    base["reason"] = (f"mixed or missing judge model {models} -- "
                                      f"calibrate each model separately")
                    signals_blocked.append(base)
                else:
                    signals_ready.append(base)
    finally:
        log.close()

    ready_rubrics = sorted({s["rubric"] for s in signals_ready})
    return {
        "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "min_labelled": MIN_LABELLED,
        "signals_ready": signals_ready,
        "signals_blocked": signals_blocked,
        "ready": [{"rubric": n, **rubric_meta.get(n, {})} for n in ready_rubrics],
        "blocked": signals_blocked,
        "skipped": skipped,
        "rubric_meta": rubric_meta,
    }


def run_waves(write: bool) -> dict:
    """Delegate to the existing, tested wave driver for the 10 suite rubrics.

    Reused rather than reimplemented: calibrate_waves.py already handles
    load-shedding, the ambiguous-case merge, and the per-signal label
    transcription from human-authored expectations.
    """
    script = LEVELS / "calibrate_waves.py"
    if not script.exists():
        return {"ran": False, "why": f"missing {script}"}
    args = [sys.executable, str(script)] + (["--write"] if write else [])
    proc = subprocess.run(args, capture_output=True, text=True, cwd=str(LEVELS))
    return {
        "ran": True,
        "write": write,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def certify_ready(ready_signals: list, write: bool) -> list:
    """Sweep and certify each READY signal independently."""
    out = []
    for s in ready_signals:
        name, sig = s["rubric"], s["signal"]
        qname, attr = sig.split(".", 1)
        direction = "below" if attr == "confidence" else "above"
        try:
            res = calibrate_rubric(name, (qname, attr),
                                   direction=direction,
                                   tie=("declared" if attr == "confidence" else "middle"),
                                   write=write)
        except Exception as exc:  # noqa: BLE001
            out.append({"rubric": name, "signal": sig, "ok": False,
                        "reason": f"calibrate refused: {exc}"})
            continue
        out.append({
            "rubric": name, "signal": sig,
            "ok": bool(res.get("certified")),
            "certified": res.get("certified"),
            "rubric_calibrated": res.get("rubric_calibrated"),
            "n_labelled": res.get("n_labelled"),
            "n_good": res.get("n_good"), "n_bad": res.get("n_bad"),
            "threshold": (res.get("operating_point") or {}).get("threshold"),
            "reason": res.get("reason", ""),
        })
    return out


def label_queue(blocked: list, limit: int = 20) -> list:
    """The exact next action per blocked SIGNAL, cheapest first.

    A signal with some labels needs topping up; one with none needs its first
    key. That distinction decides whether Mike is transcribing intent or
    building the answer key from scratch.
    """
    rows = []
    for b in blocked:
        if b.get("need", 0) <= 0:
            continue
        rows.append({
            "rubric": b["rubric"],
            "signal": b.get("signal", "-"),
            "label_scope": b.get("label_scope"),
            "have": b.get("labelled", 0),
            "good": b.get("good", 0),
            "bad": b.get("bad", 0),
            "need": b["need"],
            "reason": b.get("reason", ""),
            "route": ("rig-s1gate label <id> good|bad --signal %s" % b.get("signal")
                      if b.get("label_scope") == "signal" else
                      "rig-s1gate label <id> good|bad"),
        })
    rows.sort(key=lambda r: (-r["have"], r["need"]))
    return rows[:limit]


def render(rep: dict, write: bool, waves: dict | None) -> str:
    o = []
    o.append("=" * 70)
    o.append("S1GATE CALIBRATION RUN  %s   write=%s" % (rep["scanned_at"], write))
    o.append("=" * 70)
    o.append("")
    sr, sb = rep.get("signals_ready", []), rep.get("signals_blocked", [])
    o.append("SCOPE      signal-level. MIN_LABELLED=%d, need >=5 good AND >=5 bad"
             % rep["min_labelled"])
    o.append("           %d signal(s) READY across %d rubric(s)"
             % (len(sr), len({s['rubric'] for s in sr})))
    o.append("           %d signal(s) BLOCKED on ground truth" % len(sb))
    o.append("           %d rubric(s) SKIP (must stay uncalibrated by test)"
             % len(rep["skipped"]))
    o.append("")

    if sr:
        o.append("CERTIFIABLE NOW")
        for s in sorted(sr, key=lambda x: -x.get("labelled", 0)):
            o.append("  + %-22s %-34s n=%-4d good=%-3d bad=%-3d %s" % (
                s["rubric"], s["signal"], s.get("labelled", 0),
                s.get("good", 0), s.get("bad", 0),
                "[suite]" if s.get("in_suite") else ""))
        o.append("")

    if waves and waves.get("ran"):
        o.append("SUITE WAVES (10 jev.* rubrics, 336 human-authored cases)")
        o.append("  exit=%s" % waves.get("exit_code"))
        tail = (waves.get("stdout_tail") or "").strip().splitlines()
        for line in tail[-14:]:
            o.append("  | " + line)
        if waves.get("stderr_tail"):
            o.append("  ! stderr: " + waves["stderr_tail"].strip().splitlines()[-1])
        o.append("")

    if rep.get("certified"):
        o.append("CERTIFICATION RESULTS")
        for c in rep["certified"]:
            reason = c.get("reason", "")
            holds = "meets the ceiling" in reason
            if c.get("certified"):
                mark = "CERTIFIED"
            elif holds and not write:
                # dry run: the sweep found a threshold that holds, but nothing
                # was written. 'NOT CERTIFIED' here would be read as a failure.
                mark = "WOULD CERTIFY"
            else:
                mark = "CANNOT CERTIFY"
            o.append("  %-22s %-34s %-15s n=%-5s good=%-5s bad=%-4s t=%s" % (
                c["rubric"], c.get("signal", "-"), mark,
                c.get("n_labelled"), c.get("n_good"), c.get("n_bad"),
                c.get("threshold")))
            if mark != "CERTIFIED":
                o.append("      %s" % reason[:120])
        o.append("")

    o.append("-" * 70)
    o.append("BLOCKED -- cannot certify without ground truth. One line each:")
    for b in sb:
        o.append("BLOCKED: %-22s %-34s %s" % (
            b["rubric"], b.get("signal", "-"), b.get("reason", "")))
    o.append("")

    q = rep.get("label_queue") or []
    if q:
        o.append("LABELLING QUEUE (highest existing coverage first -- cheapest wins)")
        o.append("  %-24s %-9s %5s %5s  %s" % ("RUBRIC", "SCOPE", "HAVE", "NEED", "COMMAND"))
        for r in q:
            o.append("  %-24s %-9s %5d %5d  %s" % (
                r["rubric"], r["label_scope"], r["have"], r["need"], r["route"]))
        o.append("")
        o.append("  Every label comes from a person or from a human-authored")
        o.append("  expected answer. Nothing here lets a model write its own key.")
    o.append("")
    n_block = len(sb)
    o.append("VERDICT    %s" % ("ALL IN SCOPE CERTIFIED" if n_block == 0
                                else f"{n_block} signal(s) BLOCKED on ground truth"))
    return "\n".join(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="s1gate calibration driver")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--waves", action="store_true",
                    help="also run jev-levels/calibrate_waves.py for the 10 suite rubrics")
    ap.add_argument("--report", default=None)
    ap.add_argument("--queue", type=int, default=20)
    args = ap.parse_args(argv)

    rep = scan()
    waves = run_waves(args.write) if args.waves else None
    # When --waves runs, calibrate_waves.py owns the suite rubrics: it labels
    # from the human-authored expectations and then certifies. Certifying them
    # again here would overwrite its result with one computed on the staler
    # pre-wave labels. Hand off cleanly instead of double-owning.
    signals = [s for s in rep.get("signals_ready", [])
               if not (args.waves and s.get("in_suite"))]
    rep["certified"] = certify_ready(signals, args.write)
    rep["label_queue"] = label_queue(rep.get("signals_blocked", []), args.queue)

    if args.report:
        Path(args.report).write_text(json.dumps(rep, indent=2, default=str) + "\n",
                                     encoding="utf-8")
        print(f"report written: {args.report}")

    print(render(rep, args.write, waves))
    return 1 if rep.get("signals_blocked") else 0


if __name__ == "__main__":
    sys.exit(main())
