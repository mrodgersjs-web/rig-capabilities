"""V41-P3: the weekly Realign driver — five artifacts, honest `sealed: false`.

A weekly review that produces prose is a diary. This produces a signed delta on
a weighted capability register. The five artifacts per week are the Build
Card's list, unchanged: the register diff, `convergence_report.md`, proof
JSON, the Doctrine Update Phrase (Artifact 27), and Operator's Weekly.

Nothing is sealed here: `sealed` stays `False` until P7's `afproof` lands a real
`proof_hash`. A first week is honestly `BASELINE_ONLY`, and a real zero-booking
week is honestly `FAIL` — named, complete, and never retried.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from . import convergence, register
from .register import _repo_root

REALIGN_DIR = convergence.REALIGN_DIR
ARTIFACT_KINDS = ("register-diff.json", "convergence_report.md", "proof/*.json",
                  "doctrine-update-phrase.md", "operators-weekly.md")


def week_id(ts=None) -> str:
    """ISO week key `%G-W%V`. 2026-09-01 is `2026-W36`."""
    if ts is None:
        moment = date.today()
    elif isinstance(ts, datetime):
        moment = ts.date()
    elif isinstance(ts, date):
        moment = ts
    else:
        moment = date.fromisoformat(str(ts).strip()[:10])
    return moment.strftime("%G-W%V")


def week_dir(repo, week: str) -> Path:
    return _repo_root(repo) / REALIGN_DIR / week


def run_week(repo, week: str | None = None, apply: bool = False,
             roots=None) -> dict:
    """Score the week and write its five artifacts (`apply=True` only).

    Returns `sealed: False` and never a fabricated hash. An invalid register —
    or a corpus unclassified rate past the halt — writes nothing.
    """
    root = _repo_root(repo)
    week = week or week_id()
    out = {"week": week, "apply": bool(apply), "dry_run": not apply,
           "artifact_kinds": list(ARTIFACT_KINDS), "artifacts": [],
           "sealed": False, "seal_reason": "afproof_not_landed (P7)"}

    rows = register.load_register(repo)
    errors = register.row_errors(rows)
    flagged = register.flagged_owners(rows)
    out["rows"] = len(rows)
    out["row_errors"] = errors
    out["flagged_owners"] = flagged
    if not rows:
        return {**out, "ok": False, "verdict": "REGISTER_EMPTY",
                "reason": f"no rows in {register.REGISTER_STORE}"}
    if errors:
        return {**out, "ok": False, "verdict": "REGISTER_INVALID",
                "reason": "row_errors:" + json.dumps(errors[:3],
                                                     separators=(",", ":"))}
    try:
        register.require_booked_row(rows)
    except register.RegisterError as exc:
        return {**out, "ok": False, "verdict": "REGISTER_INVALID",
                "reason": str(exc)}

    # The corpus is consulted once, here, and handed to the scorer: a scan that
    # dies on a mounted root must not take the driver down with it — an unknown
    # unclassified rate makes the week FAIL, never PASS.
    corpus_error = None
    try:
        report = convergence.corpus_report(roots)
    except (ImportError, OSError) as exc:
        report, corpus_error = None, f"{type(exc).__name__}:{exc}"
    try:
        scored = convergence.score_week(repo, week=week, report=report)
    except (convergence.CorpusHalt, convergence._corpus_refusal()) as exc:
        return {**out, "ok": False, "verdict": "CORPUS_REFUSAL",
                "reason": str(exc)}
    if corpus_error:
        scored["corpus_error"] = corpus_error
        scored["corpus"]["error"] = corpus_error

    gate = scored["gate"]
    metrics = scored["metrics"]
    prev_rows = convergence._previous_rows(repo, None, week)
    diff = register.diff_register(prev_rows if isinstance(prev_rows, list) else [],
                                 rows)
    prior = scored.get("sealed_weeks_prior") or []

    out.update({"ok": gate["verdict"] == "PASS", "verdict": gate["verdict"],
                "causes": gate["causes"], "escalations": gate["escalations"],
                "c_t": metrics["c_t"], "a_t": metrics["a_t"],
                "d_c_t": gate["d_c_t"], "d_a_t": gate["d_a_t"],
                "bookings": gate["bookings"], "prior_weeks": prior})

    paths = {
        "diff": week_dir(root, week) / "register-diff.json",
        "report": week_dir(root, week) / "convergence_report.md",
        "proof": week_dir(root, week) / "proof",
        "doctrine": week_dir(root, week) / "doctrine-update-phrase.md",
        "weekly": week_dir(root, week) / "operators-weekly.md",
    }
    out["artifacts"] = sorted(str(p.relative_to(root))
                              for p in paths.values())

    if not apply:
        return {**out, "wrote": False, "would_write": out["artifacts"]}

    proof = paths["proof"]
    proof.mkdir(parents=True, exist_ok=True)
    _write_json(paths["diff"], {
        "week": week, "previous_weeks": prior,
        "previous_rows_available": isinstance(prev_rows, list),
        "diff": diff})
    _write_json(proof / "convergence.json", {
        "week": week,
        "exact": {"e_cap": metrics["e_cap"], "c_t": metrics["c_t"],
                  "a_t": metrics["a_t"]},
        "metrics": metrics,
        "corpus": scored["corpus"],
        "gate": {"verdict": gate["verdict"], "bookings": gate["bookings"],
                 "d_c_t": gate["d_c_t"], "d_a_t": gate["d_a_t"]},
        "sealed": False})
    _write_json(proof / "weekly-gate.json", gate)
    _write_json(proof / "bookings.json", scored["bookings"])
    _write_json(proof / "register-validation.json",
                {"rows": len(rows), "row_errors": errors,
                 "flagged_owners": flagged})
    _write_json(proof / "register-rows.json",
                {"week": week, "rows": [register.normalize_row(r) for r in rows]})
    _write(paths["report"], _report(week, scored, diff, prior))
    _write(paths["doctrine"], _doctrine_phrase(week, gate, metrics))
    _write(paths["weekly"], _operators_weekly(week, scored, diff, prior))
    return {**out, "wrote": True}


# ------------------------------------------------------------------ rendering

def _report(week: str, scored: dict, diff: dict, prior: list) -> str:
    g = scored["gate"]
    m = scored["metrics"]
    c = scored["corpus"]
    lines = [
        f"# Convergence Report — {week}",
        "",
        f"- Verdict: **{g['verdict']}**",
        f"- C_t: `{m['c_t']}` (previous `{g['c_t_previous']}`, dC_t `{g['d_c_t']}`)",
        f"- A_t: `{m['a_t']}` (previous `{g['a_t_previous']}`, dA_t `{g['d_a_t']}`)",
        f"- E_cap: `{m['e_cap']}` over `{m['weight_scored']}` scored weight "
        f"({m['rows_scored']}/{m['rows_total']} rows)",
        f"- Booked qualified conversations: {g['bookings']}",
        f"- Corpus unclassified rate: `{c.get('unclassified_rate')}` "
        f"(halt `{c.get('halt')}`, ok `{c.get('ok')}`)",
        f"- Sealed prior weeks: {', '.join(prior) if prior else 'none — no baseline yet'}",
        "",
        "## Gate checks",
        "",
        "| check | value |",
        "| --- | --- |",
    ]
    for name, value in g["checks"].items():
        lines.append(f"| {name} | {value} |")
    lines += ["", "## Causes", ""]
    lines += ([f"- {cause}" for cause in g["causes"]]
              or ["- none — every gate condition held"])
    if g["escalations"]:
        lines += ["", "## Escalations", ""]
        lines += [f"- {e}" for e in g["escalations"]]
    lines += ["", "## MADZ flags", ""]
    if g["madz_flags"]:
        lines += [f"- {f['capability']}: `{f['flag']}` z=`{f['z']}` "
                  f"resolved={f['resolved']}" for f in g["madz_flags"]]
    else:
        lines.append("- none")
    if m["degenerate_targets"]:
        lines += ["", "## Degenerate targets (target_M_2031 == 0, contribute 0)", ""]
        lines += [f"- {d['id']} (w={d['weight_w']}, M={d['maturity_M0_5']})"
                  for d in m["degenerate_targets"]]
    counts = diff["counts"]
    lines += ["", "## Register diff", "",
              f"- added {counts['added']} · removed {counts['removed']} · "
              f"changed {counts['changed']} · unchanged {counts['unchanged']}", ""]
    for entry in diff["changed"][:20]:
        fields = ", ".join(sorted(entry["fields"]))
        lines.append(f"- `{entry['id']}`: {fields}")
    for rid in diff["added"][:20]:
        lines.append(f"- + `{rid}`")
    for rid in diff["removed"][:20]:
        lines.append(f"- - `{rid}`")
    lines += ["", "---",
              "No ProofPacket is sealed for this week: `sealed: false` until "
              "`rig_capabilities/afproof.py` lands (P7). Sentinel Prime holds "
              "fleet termination authority and is specification-only.", ""]
    return "\n".join(lines)


def _doctrine_phrase(week: str, gate: dict, metrics: dict) -> str:
    """Artifact 27 — the phrase committed back to the system. On FAIL it must
    name the cause, so the cause is the sentence."""
    if gate["verdict"] == "FAIL":
        lead = (f"Week {week} FAILED on {', '.join(gate['causes'])}. "
                f"C_t {metrics['c_t']} (dC_t {gate['d_c_t']}), "
                f"A_t {metrics['a_t']} (dA_t {gate['d_a_t']}).")
        remedy = ("The next build is the one that moves the named cause, not the "
                  "next infrastructure idea.")
    elif gate["verdict"] == "BASELINE_ONLY":
        lead = (f"Week {week} is the baseline: C_t {metrics['c_t']}, "
                f"A_t {metrics['a_t']}, with no prior sealed week to move from.")
        remedy = ("A baseline is not progress. Next week must show dC_t > 0 and "
                  "at least one booked qualified conversation.")
    else:
        lead = (f"Week {week} cleared the gate: dC_t {gate['d_c_t']} on C_t "
                f"{metrics['c_t']}, dA_t {gate['d_a_t']} on A_t "
                f"{metrics['a_t']}, {gate['bookings']} booked qualified "
                "conversations.")
        remedy = "The register, not the calendar, decides what is next."
    return (f"# Doctrine Update Phrase — {week}\n\n"
            f"> {lead} {remedy}\n\n"
            f"Verdict: `{gate['verdict']}` · escalations: "
            f"{', '.join(gate['escalations']) or 'none'} · sealed: false\n")


def _operators_weekly(week: str, scored: dict, diff: dict, prior: list) -> str:
    g, m, b = scored["gate"], scored["metrics"], scored["bookings"]
    return "\n".join([
        f"# Operator's Weekly — {week}",
        "",
        f"**Verdict:** {g['verdict']}",
        "",
        "## The scoreboard",
        "",
        f"- C_t `{m['c_t']}` → dC_t `{g['d_c_t']}`",
        f"- A_t `{m['a_t']}` → dA_t `{g['d_a_t']}`",
        f"- E_cap `{m['e_cap']}` remaining, weighted",
        f"- Booked qualified conversations: **{g['bookings']}** "
        f"(of {b.get('total')} claimed records)",
        "",
        "## What moved",
        "",
        f"- Register rows: {m['rows_total']} ({m['rows_scored']} scored against a 2031 target)",
        f"- Diff vs last week: +{diff['counts']['added']} "
        f"-{diff['counts']['removed']} ~{diff['counts']['changed']}",
        f"- Prior sealed weeks on disk: {len(prior)}",
        "",
        "## Honest gaps",
        "",
        "- No ProofPacket sealed this week (`sealed: false`, P7 pending).",
        "- Sentinel Prime is specification-only: no fleet termination was issued.",
        f"- Weekly scheduling stays DORMANT: `.context/realign/cron-job.json` is "
        "P8's, gated, and was not registered.",
        "",
        f"Cause list: {', '.join(g['causes']) or 'none'}",
        "",
    ])


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, doc) -> None:
    _write(path, json.dumps(doc, indent=1, sort_keys=True,
                            ensure_ascii=False) + "\n")
