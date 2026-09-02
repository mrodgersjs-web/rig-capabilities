"""V41-P3 / V52: the weekly Realign driver — five artifacts, opt-in real sealing.

A weekly review that produces prose is a diary. This produces a signed delta on
a weighted capability register. The five artifacts per week are the Build
Card's list, unchanged: the register diff, `convergence_report.md`, proof
JSON, the Doctrine Update Phrase (Artifact 27), and Operator's Weekly.

Sealing is real but explicit: `seal=True` hashes the artifacts and lands a
`proof_hash` through `afproof`, recording it in `proof/sealing.json` — the one file
that may claim a week is sealed. A first week is honestly `BASELINE_ONLY`, a real
zero-booking week is honestly `FAIL`, and an unsealed week says so in words that do
not rot when the sealing module changes. Nothing is ever sealed by assertion.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

from . import convergence, register
from .register import _repo_root

REALIGN_DIR = convergence.REALIGN_DIR
ARTIFACT_KINDS = ("register-diff.json", "convergence_report.md", "proof/*.json",
                  "doctrine-update-phrase.md", "operators-weekly.md")

# Honest default. The earlier string ("afproof_not_landed (P7)") went stale the moment
# V48 landed the sealing module: a reason that no longer describes the system is a
# false claim sitting inside the artifact, so this names the actual missing step and
# is replaced with "sealed" only when a hash exists.
SEAL_PENDING = "not_sealed (pass seal=True; no proof_hash exists)"
# The receipt is the one file in the week directory that may say `sealed: true`, and
# only when it carries a hash `afproof.verify_seal` recomputes.
SEAL_RECEIPT = "proof/sealing.json"


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


def _rel(path: Path, root: Path) -> str:
    """The path as an operator would type it from the repo root.

    Relative normally. A week directory relocated by `RIG_REALIGN_ROOT` is not under the
    repo at all, and a driver that raised `ValueError` there would make the override
    unusable — so it reports the absolute path rather than crashing.
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def week_dir(repo, week: str) -> Path:
    """The week's artifact directory (relocatable via `RIG_REALIGN_ROOT`)."""
    return convergence.realign_root(repo) / week


def run_week(repo, week: str | None = None, apply: bool = False,
             roots=None, seal: bool = False) -> dict:
    """Score the week and write its five artifacts (`apply=True` only).

    Returns `sealed: False` and never a fabricated hash. An invalid register —
    or a corpus unclassified rate past the halt — writes nothing.

    `seal=True` (with `apply=True`) hashes the five artifacts and seals them through
    `afproof`, which lands a real `proof_hash` in the proof chain and records it in
    the week's own `proof/sealing.json`. It is opt-in, not default: sealing writes to
    the live proof root, so a gate, a replay, or a unit test calling `run_week` must
    never touch it by accident. Sealing is never faked on failure — an exception
    leaves `sealed: False` and names itself in `seal_reason`.
    """
    root = _repo_root(repo)
    week = week or week_id()
    out = {"week": week, "apply": bool(apply), "dry_run": not apply,
           "artifact_kinds": list(ARTIFACT_KINDS), "artifacts": [],
           "sealed": False, "seal_reason": SEAL_PENDING}

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
    out["artifacts"] = sorted(_rel(p, root) for p in paths.values())

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
        "seal_receipt": SEAL_RECEIPT})
    _write_json(proof / "weekly-gate.json", gate)
    _write_json(proof / "bookings.json", scored["bookings"])
    _write_json(proof / "register-validation.json",
                {"rows": len(rows), "row_errors": errors,
                 "flagged_owners": flagged})
    _write_json(proof / "register-rows.json",
                {"week": week, "rows": [register.normalize_row(r) for r in rows]})
    _write(paths["report"], _report(week, scored, diff, prior, seal=seal))
    _write(paths["doctrine"], _doctrine_phrase(week, gate, metrics, seal=seal))
    _write(paths["weekly"], _operators_weekly(week, scored, diff, prior, seal=seal))
    if seal:
        return {**out, **_seal(root, week, scored), "wrote": True}
    return {**out, "wrote": True}


def _seal(root, week: str, scored: dict) -> dict:
    """Hash the week's artifacts and land a real proof_hash through `afproof`.

    The receipt is written AFTER the hashing on purpose, and it is never sealed
    content. Both halves matter. A seal that hashes its own receipt cannot be
    recomputed by anyone else — and sealing twice proved the concrete failure: the
    second pass hashed the first pass's `proof/sealing.json`, then overwrote that same
    file, so the new receipt recorded a hash for its own path that no longer matched
    the bytes under it. A receipt that cannot re-verify its own listing is worse than
    no receipt. So the receipt is the only place a truthy `sealed` appears in the week
    directory, and it appears in no hash list at all.
    """
    base = week_dir(root, week)
    files = sorted(p for p in base.rglob("*")
                   if p.is_file() and p != base / SEAL_RECEIPT)
    body = {
        "week": week,
        "verdict": scored["gate"]["verdict"],
        "c_t": scored["metrics"]["c_t"], "a_t": scored["metrics"]["a_t"],
        "bookings": scored["gate"]["bookings"],
        "artifacts": [{"path": str(p.relative_to(base)), "sha256": _sha_of(p)}
                      for p in files],
    }
    task_id = f"realign-{week}"
    try:
        from . import afproof
        packet = afproof.seal_packet("realign-week", body, task_id=task_id)
        located = str(afproof.packet_dir() / afproof.packet_name(
            task_id, packet["proof_hash"]))
    except Exception as exc:                       # never a fake seal
        return {"sealed": False,
                "seal_reason": f"seal_failed:{type(exc).__name__}: {exc}"}
    _write_json(base / SEAL_RECEIPT, {
        "sealed": True, "proof_hash": packet["proof_hash"],
        "previous_hash": packet["previous_hash"], "sealed_at": packet["sealed_at"],
        # The pointer, not a guess at the formula: an auditor holding this receipt must
        # be able to find the packet and recompute the hash without reimplementing
        # afproof's naming. The packet verifies; the receipt is not the packet.
        "proof_packet": located,
        "artifacts": body["artifacts"]})
    return {"sealed": True, "proof_hash": packet["proof_hash"],
            "seal_reason": "sealed", "seal_receipt": SEAL_RECEIPT,
            "proof_packet": located, "sealed_artifacts": len(body["artifacts"])}


# ------------------------------------------------------------------ rendering

def _report(week: str, scored: dict, diff: dict, prior: list, *, seal: bool = False) -> str:
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
              f"- {_seal_sentence(seal)}",
              "- Sentinel Prime holds fleet termination authority and is "
              "specification-only.", ""]
    return "\n".join(lines)


def _doctrine_phrase(week: str, gate: dict, metrics: dict, *, seal: bool = False) -> str:
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
            f"{', '.join(gate['escalations']) or 'none'} · {_seal_sentence(seal)}\n")


def _operators_weekly(week: str, scored: dict, diff: dict, prior: list,
                      *, seal: bool = False) -> str:
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
        f"- {_seal_sentence(seal)}",
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


def _sha_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seal_sentence(seal: bool) -> str:
    """The truth about sealing, in all three outcomes.

    The prose artifacts are rendered before the seal runs, so they cannot name a hash
    that does not exist yet — and they must not repeat the old hardcoded `sealed:
    false`, which became a false claim the moment V48 landed `afproof`. The sentence
    therefore points at the receipt and names who decides: the receipt file, written
    after the hashing, is the only artefact that states whether a week is sealed.
    """
    if not seal:
        return ("sealed: false — no seal requested for this run; "
                "`realign --apply --seal` is what lands a proof_hash")
    return ("seal requested — `proof/sealing.json` is written after the artifacts are "
            "hashed and is the only file that states the sealed verdict; if it is "
            "absent or says `sealed: false`, this week is unsealed")
