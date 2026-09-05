"""V16/V54: the round engine, with a memory.

A round: pick the weakest canonical assets in a lane, draft a deterministic
upgrade, gate it with the V15 done-test runner, and graduate ONLY on green.
Graduation = the file's frontmatter actually changes; Draft→Stable when score
>= 90 after upgrade.

V54 closes the gap that made every earlier round amnesic. Before this file grew a
record, a round picked candidates, patched frontmatter, ran done-tests and reported
a score — nothing else. No failure-analysis artifact, no hypothesis artifact, no
persistent optimization record, so the next mutator re-proposed diffs the evidence
had already refuted (the symptom `intel/frontier/2026-08-31-self-improvement-loops.md`
reports as rounds re-patching the same weakest asset every cycle). One round now runs
five deterministic stages and each writes one artifact under `.context/rounds/`:

  1. rollouts          — the recorded done-test evidence this round reads
  2. failure analysis  — which checks are red, how often, on which assets
  3. hypothesis        — one stated hypothesis per proposal, citing that failure and
                         carrying a diff-hash of the bounded modification
  4. modification      — the bounded contract edit, applied or refused
  5. score + selection — before/after score, done-test verdict, graduated or not
                         (the round report itself is stage 5)

And before stage 3 proposes, the round loads the persistent optimization record
(`.context/rounds/record.jsonl`: previous hypotheses, diffs, scores, verdicts). A
modification whose diff-hash is already recorded REJECTED is refused rather than
re-applied — `action="rejected-repeat"`, no evaluation spent — and the round reports
`exit_code=1`, so a replay that forgot its history cannot read as a clean round. The
attempt budget, routing and stopping rule are read from a declared, versioned knob
block (`.context/rounds/knobs.json` overrides `KNOBS`; no code edit is needed to
retune a round).

Source for the shape of this loop (Discover AI, LEsKxMfRFjA, on arXiv:2608.13560
AutoDesign): "We have rollouts, then we have a failure analysis, then the AI comes
up with some hypothesis"; "a persistent optimization history, the previous
hypothesis, the previous changes"; "attempt budget routing, stopping, candidate
selection, fallback routes". Each is a verbatim substring of
`.context/discover-ai/transcripts/LEsKxMfRFjA.txt`.

Honest scope. The hypothesis here is derived from recorded evidence by
`_statement()`, not authored by a model, and the modification is the deterministic
contract edit, not an arbitrary code change. The artifacts and the record make a
model-authored round checkable later; they do not make a hypothesis good — hypothesis
quality remains the bottleneck and this file does not fix it. LLM/deviate drafting is
still out of scope (the skill-upgrades command drives LLM rounds through it).
Nothing is ever applied without the done-tests going green.
"""
from __future__ import annotations
import hashlib
import json
import re
import time
from pathlib import Path

from .quality import (
    FIELDS,
    _assert_unique_exemplar_slugs,
    _slug,
    check_asset,
    migrate_frontmatter,
)
from . import selection

ROUNDS_DIR = ".context/rounds"
RECORD_FILE = "record.jsonl"
KNOBS_FILE = "knobs.json"
QUALITY_RUNS = selection.QUALITY_RUNS  # the rollouts a round reads

ACCEPTED = "ACCEPTED"        # green done-tests AND no held-out regression
REJECTED = "REJECTED"        # the evidence refuted the modification
UNEVALUATED = "UNEVALUATED"  # applied with the budget spent: on disk, never run
BLOCKED = "BLOCKED-REPLAY"   # refused because this diff is already REJECTED
VERDICTS = (ACCEPTED, REJECTED, UNEVALUATED, BLOCKED)

KNOB_VERSION = 1
# Declared orchestration knobs. AutoDesign treats attempt budget, routing, the
# stopping rule and candidate selection as editable config; welding them into the
# loop is what makes a round un-tunable and a regression unnameable. Overridable per
# repo by `.context/rounds/knobs.json` — same keys, no code edit.
KNOBS = {"version": KNOB_VERSION,
         "eval_budget_default": None,           # None = one evaluation per candidate
         "strategy_default": "informative",
         "stopping_rule": "budget-exhausted",   # or "first-reject"
         "recurring_failure_min": 2}
STOPPING_RULES = ("budget-exhausted", "first-reject")
STAGES = ("rollouts", "failure_analysis", "hypothesis", "modification",
          "score_select")


def pick_candidates(repo, lane: str, n: int = 5) -> list:
    """Weakest canonicals in `lane`, ascending quality score."""
    from .lanes import load_overlay
    from .taxonomy import classify
    ov = load_overlay(repo)
    rows = []
    for a in repo.load_index()["assets"]:
        if a["source"] != "canonical":
            continue
        if (ov.get(a["id"]) or classify(a)) != lane:
            continue
        rows.append((check_asset(a)["score"], a))
    rows.sort(key=lambda t: t[0])
    return [{"id": a["id"], "kind": a["kind"], "source": a["source"],
             "score": s} for s, a in rows[:n]]


def _upgrade_plan(asset) -> dict:
    """Deterministic contract upgrade: fill missing fields; ensure at least one
    RUNNABLE done_when entry (template prose alone never graduates)."""
    q = asset.get("quality") or {}
    fpath = asset["path"]
    if "." not in fpath.rsplit("/", 1)[-1]:
        fpath = fpath.rstrip("/") + "/SKILL.md"
    plan = {}
    if not q.get("outcome"):
        from .taxonomy import classify
        plan["outcome"] = f"{classify(asset)}: {asset.get('description') or asset['id']}"
    if not q.get("done_when"):
        plan["done_when"] = [f"file:{fpath}"]
    else:
        entries = [str(e) for e in q["done_when"]]
        if not any(e.startswith(("cmd:", "file:", "grep:", "mcp:")) for e in entries):
            plan["add_done_when"] = [f"file:{fpath}"]
    if not q.get("quality_floor"):
        plan["quality_floor"] = 0.6
    if not q.get("great_example"):
        lane = (q.get("outcome") or "").split(":")[0].strip() or "misc"
        plan["great_example"] = f"examples/great/{lane}/{_slug(asset['id'])}.md"
    return plan


def _append_done_when(p: Path, entries: list) -> bool:
    text = p.read_text()
    lines = text.splitlines()
    idx = next((i for i, ln in enumerate(lines[:80])
                if re.match(r"^(?:#\s*)?done_when\s*:", ln)), None)
    if idx is None:
        return False
    j = idx + 1
    prefix = "#" if lines[idx].lstrip().startswith("#") else ""
    while j < len(lines) and re.match(r"^(" + ("#\s*" if prefix else r"\s*") + r")-\s+", lines[j]):
        j += 1
    have = "".join(lines[idx:j])
    adds = [f"{prefix}  - {e}" for e in entries if e not in have]
    if not adds:
        return False
    lines[j:j] = adds
    p.write_text("\n".join(lines) + "\n")
    return True


def _apply(repo, asset, plan: dict) -> bool:
    p = Path(repo.root) / asset["path"]
    if p.is_dir():
        p = p / "SKILL.md"
    if not p.is_file():
        return False
    fields = {k: v for k, v in plan.items() if k != "add_done_when"}
    changed = False
    if fields:
        changed = migrate_frontmatter(p, fields) or changed
    if plan.get("add_done_when"):
        changed = _append_done_when(p, plan["add_done_when"]) or changed
    return changed


# --------------------------------------------------------------------------
# the persistent optimization record (AutoDesign CAP-08 / CAP-12)
# --------------------------------------------------------------------------

def rounds_dir(repo) -> Path:
    return Path(repo.root) / ROUNDS_DIR


def record_path(repo) -> Path:
    """The optimization record. Repo-local by construction: `.context/` is inside the
    tree the round already mutates, so round state can never grow in ~/.rig."""
    return rounds_dir(repo) / RECORD_FILE


def load_record(repo, limit: int = 2000) -> list:
    """Previous hypotheses, diffs, scores and verdicts, oldest first.

    The mutator reads this BEFORE proposing. An unreadable line is skipped, never
    fatal and never counted: an absent record is reported as "no prior verdict",
    which is a different claim from "never tried".
    """
    p = record_path(repo)
    if not p.is_file():
        return []
    rows = []
    for ln in p.read_text(encoding="utf-8").splitlines()[-limit:]:
        ln = ln.strip()
        if not ln:
            continue
        try:
            d = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and d.get("asset"):
            rows.append(d)
    return rows


def append_record(repo, rows: list) -> int:
    """Append verdicts. Append-only: a round never rewrites its own history, and a
    rejected hypothesis stays rejected until a human override deletes the line and
    says so in the round artifact."""
    rows = [r for r in rows if isinstance(r, dict) and r.get("asset")]
    if not rows:
        return 0
    p = record_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    with p.open("a", encoding="utf-8") as f:
        for r in rows:
            e = dict(r)
            e.setdefault("ts", ts)
            f.write(json.dumps(e, sort_keys=True) + "\n")
    return len(rows)


def diff_hash(asset_id: str, kind: str, source: str, plan: dict) -> str:
    """Identity of a bounded modification: the canonical form of the edit itself.

    A different field value is a different hash, and the same edit aimed at a
    different asset is a different hash — so one rejection never blocks an unrelated
    proposal."""
    blob = json.dumps({"asset": asset_id, "kind": kind, "source": source,
                       "plan": plan}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _rejected_by_hash(record: list) -> dict:
    """diff_hash -> the rejection carrying it. BLOCKED-REPLAY lines cite a prior
    rejection; they do not create a new one."""
    out = {}
    for r in record:
        if r.get("verdict") == REJECTED and r.get("diff_hash"):
            out[r["diff_hash"]] = r
    return out


# --------------------------------------------------------------------------
# declared knobs + stage artifacts
# --------------------------------------------------------------------------

def load_knobs(repo) -> dict:
    """Declared knobs, versioned, overridable per repo without a code edit.

    An unknown key or a bad `stopping_rule` is NAMED in the report — never silently
    applied, never silently dropped."""
    out = {"version": KNOB_VERSION, "source": "declared", "unknown": [],
           "version_mismatch": False, "values": dict(KNOBS)}
    p = rounds_dir(repo) / KNOBS_FILE
    if not p.is_file():
        return out
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        out["unreadable"] = f"{type(e).__name__}: {e}"
        return out
    if not isinstance(doc, dict):
        out["unreadable"] = "knobs.json is not an object"
        return out
    out["source"] = "file"
    for k, v in doc.items():
        if k == "version":
            if v != KNOB_VERSION:
                out["version_mismatch"] = True
                out["file_version"] = v
            continue
        if k not in KNOBS or (k == "stopping_rule" and v not in STOPPING_RULES):
            out["unknown"].append(k)
            continue
        out["values"][k] = v
    return out


def _stage_dir(repo, ts: str, lane: str) -> Path:
    p = rounds_dir(repo) / f"{ts.replace(':', '')}-{lane}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _write_stage(repo, ts: str, lane: str, stage: str, doc: dict) -> str:
    body = {"ts": ts, "lane": lane, "stage": stage}
    body.update(doc)
    p = _stage_dir(repo, ts, lane) / f"{stage}.json"
    p.write_text(json.dumps(body, indent=1, sort_keys=True), encoding="utf-8")
    return str(p)


def _selected_rows(sel: dict) -> list:
    """Full scored rows (with per-check history) for the chosen candidates.

    `select()["selected"]` is a brief; per-check counts live in `rows_by_id`. Failure
    analysis needs the counts, so it reads full rows in the order the selector chose."""
    return [sel["rows_by_id"][s["id"]] for s in sel["selected"]]


def _rollouts_doc(repo, sel: dict) -> dict:
    """Stage 1: the recorded rollouts this round is allowed to reason from."""
    rows = [{"id": r["id"], "kind": r["kind"], "score": r["score"],
             "runs": r["runs"], "passes": r["passes"], "checks": r["checks"],
             "reason": r["reason"]} for r in _selected_rows(sel)]
    return {"source": QUALITY_RUNS, "rows": rows, "candidates": len(rows),
            "deferred": len(sel["deferred"]),
            "note": "recorded done-test runs, not model rollouts: this round writes "
                    "no harness and calls no model"}


def _failure_analysis(lane: str, sel: dict, knobs: dict) -> dict:
    """Stage 2: name the recurring failures in the recorded rollouts.

    `failing` is every check ever seen red, with its counts and the assets it failed
    on; `held_out_green` is every check the library has ALWAYS seen green — the set a
    round must not break. Both are arithmetic over `.context/quality-runs`, not
    judgment. An empty `failing` list stays empty and reads "no recorded failure in
    this lane", which is not the claim "the lane is healthy".
    """
    floor = knobs.get("recurring_failure_min", KNOBS["recurring_failure_min"])
    failing: dict = {}
    held_out: dict = {}
    for r in _selected_rows(sel):
        for form, c in (r.get("checks") or {}).items():
            runs = int(c.get("runs") or 0)
            ok = int(c.get("ok") or 0)
            fails = max(0, runs - ok)
            bucket = failing if fails else held_out
            e = bucket.setdefault(form, {"check": form, "runs": 0, "assets": []})
            if fails:
                e["fails"] = e.get("fails", 0) + fails
            e["runs"] += runs
            if r["id"] not in e["assets"]:
                e["assets"].append(r["id"])
    rows = sorted(failing.values(), key=lambda e: (-e.get("fails", 0), e["check"]))
    for e in rows:
        e["recurring"] = e.get("fails", 0) >= floor
    return {"lane": lane, "source": QUALITY_RUNS, "failing": rows,
            "held_out_green": sorted(held_out.values(), key=lambda e: e["check"]),
            "recurring_failure_min": floor,
            "assets_with_failures": sorted({a for e in rows for a in e["assets"]})}


def _statement(asset_id: str, plan: dict, cited: list) -> str:
    """The hypothesis in one sentence a reviewer can disagree with.

    Deterministic on purpose: it names what will change and which recorded failure it
    claims to address. It does not claim the change is good — stage 5 decides that."""
    fields = "+".join(sorted(plan)) or "no field"
    why = (f"recurring red check(s): {', '.join(cited)}" if cited
           else "no recorded failure in this lane, so this is a completeness-only edit")
    return (f"{asset_id}: filling {fields} closes the contract gap; "
            f"evidence addressed: {why}")


def _hypothesis(asset, plan: dict, failures: list, record: list,
                knobs: dict) -> dict:
    """Stage 3: state the hypothesis before a file is touched, citing stage 2 and
    carrying the diff-hash the record is checked against."""
    aid = asset["id"]
    cited = [f["check"] for f in failures if aid in f["assets"]]
    return {"asset": aid, "kind": asset["kind"], "source": asset["source"],
            "statement": _statement(aid, plan, cited), "plan": plan,
            "diff_hash": diff_hash(aid, asset["kind"], asset["source"], plan),
            "cited_failures": cited, "version": knobs["version"],
            "prior_verdicts": [r.get("verdict") for r in record
                               if r.get("asset") == aid]}


def _entry(c: dict) -> dict:
    return {"id": c["id"], "before": c["score"], "after": c["score"],
            "value": c["value"], "selection": c["reason"], "action": "no-op",
            "plan": None, "diff_hash": None, "rolled_back": False}


def _pending(e: dict, hypo: dict, verdict: str, done_tests=None, bad=None,
             rolled_back: bool = False) -> dict:
    """One record line: the hypothesis, its diff-hash, the scores, the verdict."""
    row = {"asset": e["id"], "kind": hypo["kind"], "source": hypo["source"],
           "hypothesis": hypo["statement"], "diff_hash": hypo["diff_hash"],
           "before": e["before"], "after": e["after"], "done_tests": done_tests,
           "verdict": verdict, "action": e["action"]}
    if bad:
        row["regressed_checks"] = bad
    if rolled_back:
        row["rolled_back"] = True
    return row


# --------------------------------------------------------------------------
# the round
# --------------------------------------------------------------------------

def run_round(repo, lane: str, n: int = 5, dry: bool = False,
              budget: int | None = None, strategy: str = "informative") -> dict:
    """One round: rollouts -> failure analysis -> hypothesis -> modification -> score.

    `strategy="informative"` (default) ranks by need x Bernoulli variance so the
    round spends its evaluations where a change can be observed; "weakest" keeps the
    original score-ascending order so an old round stays reproducible. `budget` caps
    done-test evaluations and is enforced, not advisory; `budget=None` takes the
    declared knob `eval_budget_default`, itself None (= one evaluation per candidate)
    so pre-V54 behaviour is unchanged until a knobs file says otherwise.

    Graduation needs green done-tests AND no regressed held-out check. A modification
    whose diff-hash is already recorded REJECTED is refused
    (`action="rejected-repeat"`, nothing spent) and the round reports `exit_code=1`: a
    round that re-proposes a refuted edit is not a clean round.

    The `applied-unevaluated` / UNEVALUATED path names an edit that is on disk but was
    never run. Under today's selector it cannot occur: `select()` caps candidate COUNT
    at the evaluation budget, so extra candidates land in `deferred` (asserted by
    `tests/test_round_record.py::test_unevaluated_is_reported_and_still_unreachable`).
    The branch and the report key stay so that state is named rather than counted as
    graduated if that coupling ever changes — not because a round has produced it.

    A REJECTED modification is rolled back — the command's own promise, "if any
    candidate fails its done-tests, it stays untouched". The file state a rejected
    edit leaves behind is exactly what lets a later round propose it again, so
    rollback and record are one mechanism, not two.

    Returns the V53 report keys unchanged (bin/rig-capabilities, the MCP handler and
    test_catalog read them) plus: stages, record, rejected, replay_rejected,
    stopped_reason, knobs, exit_code.
    """
    assets = repo.load_index()["assets"]
    _assert_unique_exemplar_slugs(
        a["id"] for a in assets if a.get("source") == "canonical"
    )
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    knobs = load_knobs(repo)
    vals = knobs["values"]
    record = load_record(repo)                 # read BEFORE proposing, always
    rejected = _rejected_by_hash(record)
    sel = selection.select(repo, lane, n,
                           budget if budget is not None
                           else vals["eval_budget_default"], strategy)
    rows = sel["rows_by_id"]
    limit = sel["eval_budget_effective"]
    roll_doc = _rollouts_doc(repo, sel)
    failures = _failure_analysis(lane, sel, vals)

    stages, actions, hypo_docs, pending = {}, [], [], []
    spent, stopped_reason = 0, ""

    for c in sel["selected"]:
        entry = _entry(c)
        asset = next(a for a in assets
                     if a["id"] == c["id"] and a["kind"] == c["kind"]
                     and a["source"] == c["source"])
        plan = _upgrade_plan(asset)
        if not plan:
            actions.append(entry)
            continue
        if stopped_reason:                      # the stopping rule outranks the work
            entry["action"] = "stopped-by-rule"
            actions.append(entry)
            continue
        hypo = _hypothesis(asset, plan, failures["failing"], record, vals)
        hypo_docs.append(hypo)
        entry["diff_hash"] = hypo["diff_hash"]
        prior = rejected.get(hypo["diff_hash"])
        if prior:
            # The evidence already refuted THIS modification: refuse it, spend
            # nothing, and record the refusal so the re-patch stays countable.
            entry["action"] = "rejected-repeat"
            entry["prior_rejection_ts"] = prior.get("ts")
            actions.append(entry)
            pending.append(_pending(entry, hypo, BLOCKED))
            continue
        entry["plan"] = plan
        actions.append(entry)
        if dry:
            entry["action"] = "would-apply"     # a dry run proposes, never judges
            continue

        target = Path(repo.root) / asset["path"]
        if target.is_dir():
            target = target / "SKILL.md"
        was = target.read_text(encoding="utf-8") if target.is_file() else None
        entry["action"] = "applied" if _apply(repo, asset, plan) else "write-failed"
        if entry["action"] == "write-failed":
            pending.append(_pending(entry, hypo, UNEVALUATED))
            continue
        if spent >= limit:
            entry["action"] = "applied-unevaluated"
            pending.append(_pending(entry, hypo, UNEVALUATED))
            continue
        from .done_tests import run_asset
        repo.build_index()                      # index must see the new frontmatter
        fresh = next(a for a in repo.load_index()["assets"]
                     if a["id"] == c["id"] and a["kind"] == c["kind"]
                     and a["source"] == c["source"])
        r = run_asset(repo, c["id"], source="canonical")
        spent += 1
        bad = selection.regressed_checks(rows[c["id"]], r.get("results"))
        entry["after"] = check_asset(fresh)["score"]
        entry.update({"done_tests": r["pass"], "regressed_checks": bad,
                      "graduated": bool(r["pass"]) and not bad})
        if bad:
            entry["action"] = "applied-regressed"
        elif not r["pass"]:
            entry["action"] = "applied-but-red"   # honest; not graduated
        refuted = bool(bad) or not r["pass"]
        if refuted and was is not None:
            target.write_text(was, encoding="utf-8")   # leave the asset untouched
            entry["rolled_back"] = True
            repo.build_index()                        # index matches what is on disk
        pending.append(_pending(entry, hypo,
                                REJECTED if refuted else ACCEPTED, bool(r["pass"]),
                                bad, entry["rolled_back"]))
        if refuted and vals["stopping_rule"] == "first-reject":
            stopped_reason = "first-reject"

    # stage artifacts 1-4; stage 5 is the round report written below
    stages["rollouts"] = _write_stage(repo, ts, lane, "rollouts", roll_doc)
    stages["failure_analysis"] = _write_stage(repo, ts, lane, "failure_analysis",
                                              failures)
    stages["hypothesis"] = _write_stage(repo, ts, lane, "hypothesis", {
        "hypotheses": [{k: h[k] for k in ("asset", "kind", "statement",
                                          "diff_hash", "cited_failures",
                                          "prior_verdicts", "version")}
                       for h in hypo_docs],
        "refused": [e["id"] for e in actions
                    if e["action"] in ("rejected-repeat", "stopped-by-rule")]})
    stages["modification"] = _write_stage(repo, ts, lane, "modification", {
        "dry_run": dry,
        "modifications": [{"asset": e["id"], "diff_hash": e["diff_hash"],
                           "action": e["action"], "rolled_back": e["rolled_back"],
                           "plan": e["plan"]}
                          for e in actions
                          if e["plan"] or e["action"] in ("rejected-repeat",
                                                          "stopped-by-rule")]})
    appended = 0 if dry else append_record(
        repo, [dict(p, lane=lane, round_ts=ts) for p in pending])
    replay_rejected = sum(1 for e in actions if e["action"] == "rejected-repeat")
    rep = {"ts": ts, "lane": lane, "dry": dry,
           "strategy": sel["strategy"],
           "selection_fallback": sel.get("fallback", ""),
           "uncertain_candidates": sel.get("uncertain_candidates", 0),
           "eval_budget": sel["eval_budget"],
           "eval_budget_effective": limit, "eval_spent": spent,
           "candidates": len(sel["selected"]), "deferred": sel["deferred"],
           "actions": actions,
           "unevaluated": sum(1 for a in actions
                              if a["action"] == "applied-unevaluated"),
           "regressed": sum(1 for a in actions if a.get("regressed_checks")),
           "graduated": sum(1 for a in actions if a.get("graduated")),
           # --- V54: the memory, plus the two artifacts that used to be missing ---
           "stages": stages,
           "record": {"path": str(record_path(repo)), "loaded": len(record),
                      "appended": appended, "rejected_known": len(rejected),
                      "blocked": replay_rejected},
           "rejected": sum(1 for p in pending if p["verdict"] == REJECTED),
           "replay_rejected": replay_rejected,
           "stopped_reason": stopped_reason,
           "knobs": {"version": knobs["version"], "source": knobs["source"],
                     "unknown": knobs["unknown"],
                     "version_mismatch": knobs["version_mismatch"],
                     "values": knobs["values"]},
           # 1 = this round re-proposed a modification the record says was REJECTED.
           # main() exits with this, so a replay cannot read as a clean round.
           "exit_code": 1 if replay_rejected else 0}
    stages["score_select"] = _write_stage(repo, ts, lane, "score_select", {
        "evaluations": {"spent": spent, "limit": limit,
                        "budget": sel["eval_budget"]},
        "graduated": rep["graduated"], "rejected": rep["rejected"],
        "replay_rejected": replay_rejected, "exit_code": rep["exit_code"],
        "stopped_reason": stopped_reason,
        "scores": [{"asset": e["id"], "before": e["before"], "after": e["after"],
                    "verdict": (ACCEPTED if e.get("graduated") else
                                REJECTED if e.get("regressed_checks")
                                or e["action"] == "applied-but-red" else
                                UNEVALUATED if e["action"] in
                                ("applied-unevaluated", "rejected-repeat",
                                 "stopped-by-rule", "write-failed") else "UNSCORED")}
                   for e in actions]})
    out = rounds_dir(repo)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{ts.replace(':', '')}-{lane}.json").write_text(
        json.dumps(rep, indent=1), encoding="utf-8")
    return rep


# --------------------------------------------------------------------------
# the blocking fixture and the passing fixture, as processes with exit codes
# --------------------------------------------------------------------------

def _sized_check(head: str, tail: str, rel: str) -> tuple:
    """Fixed point for a byte-budget check: the threshold is the size of the file
    that actually contains the check, so the check is GREEN before an upgrade and RED
    after ANY inserted byte. The threshold's own digit count feeds the file size, so
    it is solved rather than guessed (it settles in three iterations at any real
    frontmatter length)."""
    threshold = len((head + tail).encode()) + 64
    body = head + tail
    for _ in range(8):
        body = head + f"  - cmd:test $(wc -c < {rel}) -lt {threshold}\n" + tail
        want = len(body.encode()) + 1
        if want == threshold:
            return body, threshold
        threshold = want
    return body, threshold


def _plant_repo(root: Path, mode: str = "rejected"):
    """A throwaway estate for the two fixtures — never the live tree.

    mode="rejected": one asset carrying an always-red check (the recurring failure
    stage 2 must name) plus a byte-budget check that ANY upgrade line breaks, recorded
    in history as always-green. That is a genuine held-out regression, so round 1 must
    return REJECTED and round 2 over the same evidence must REFUSE the same diff —
    exit 1. mode="novel": the same asset with a `file:` check that stays green and no
    prior rejection, so both rounds must exit 0. A guard that always blocks fails the
    second fixture; a guard that never blocks fails the first."""
    rel = "capabilities/skills/weak-skill/SKILL.md"
    (root / "capabilities" / "skills" / "weak-skill").mkdir(parents=True,
                                                            exist_ok=True)
    (root / ".lanes.json").write_text('{"weak-skill": "misc"}', encoding="utf-8")
    (root / "config.json").write_text(json.dumps(
        {"defaults": False, "external_roots": [], "install_roots": {}}),
        encoding="utf-8")
    head = ("---\nname: weak-skill\ndescription: weak-skill contract is thin\n"
            "done_when:\n")
    tail = "---\n# weak-skill\nThe asset body.\n"
    if mode == "rejected":
        body, threshold = _sized_check(head + "  - cmd:false\n", tail, rel)
        checks = ["cmd:false", f"cmd:test $(wc -c < {rel}) -lt {threshold}"]
        green = [False, True]
    else:
        body = head + f"  - file:{rel}\n"
        checks, green = [f"file:{rel}"], [True]
    (root / rel).write_text(body + tail, encoding="utf-8")
    hist = root / ".context" / "quality-runs"
    hist.mkdir(parents=True, exist_ok=True)
    for day in ("2026-09-01T000000", "2026-09-02T000000"):
        (hist / f"{day}.json").write_text(json.dumps({"rows": [
            {"id": "weak-skill", "pass": all(green),
             "results": [{"form": c, "ok": g} for c, g in zip(checks, green)]}]}),
            encoding="utf-8")
    from .catalog import Repo
    return Repo(root)


def plant_fixture(mode: str = "rejected") -> dict:
    """Run a round twice over one evidence set in a scratch tree; report both exit
    codes. `rejected` must end 1 (the guard refused the replay); `novel` must end 0
    (the guard did not become a wall)."""
    import tempfile
    root = Path(tempfile.mkdtemp(prefix=f"round-plant-{mode}-"))
    repo = _plant_repo(root, mode)
    first = run_round(repo, "misc", n=1, budget=1, strategy="weakest")
    second = run_round(repo, "misc", n=1, budget=1, strategy="weakest")
    return {"root": str(root), "mode": mode,
            "first_action": first["actions"][0]["action"] if first["actions"] else "",
            "first_exit_code": first["exit_code"],
            "second_action": second["actions"][0]["action"] if second["actions"] else "",
            "second_exit_code": second["exit_code"],
            "record": str(record_path(repo)),
            "verdicts": [r["verdict"] for r in load_record(repo)]}


def main(argv=None) -> int:
    """`python3 -m rig_capabilities.rounds [lane] [--n N] [--dry] [--budget B]
    [--strategy S] [--root DIR]` — prints the round report and exits on
    `exit_code`: 0 clean, 1 when the round re-proposed a modification the record
    already rejected.

    `--plant rejected` / `--plant novel` run the two fixtures against a scratch tree
    and exit with the SECOND round's code — 1 and 0 respectively."""
    import argparse
    ap = argparse.ArgumentParser(prog="rig_capabilities.rounds")
    ap.add_argument("lane", nargs="?", default="misc")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--strategy", default="informative")
    ap.add_argument("--root", default=None)
    ap.add_argument("--plant", choices=("rejected", "novel"), default=None)
    a = ap.parse_args(argv)
    if a.plant:
        out = plant_fixture(a.plant)
        print(json.dumps(out, indent=1))
        return out["second_exit_code"]
    from .catalog import Repo
    root = Path(a.root) if a.root else Path(__file__).resolve().parent.parent
    rep = run_round(Repo(root), a.lane, n=a.n, dry=a.dry, budget=a.budget,
                    strategy=a.strategy)
    print(json.dumps(rep, indent=1))
    return rep["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
