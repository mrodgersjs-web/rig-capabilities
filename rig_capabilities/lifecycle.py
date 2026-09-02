"""Library lifecycle state, computed retention, and revocation.

Two sources named the same hole from opposite ends of the library.

arXiv:2608.29596 (systems foundation for agentic skills) states the library as
an equation that is *recomputed each cycle, never appended*: memory(t+1) =
library minus the assets selected for removal plus validated new or revised
assets, where removal fires when measured utility falls below an eviction
threshold or when activation frequency falls under a temporal-decay function.
Utility is a subtraction, not an adjective: the counterfactual performance gain
of injecting the asset relative to the base policy, minus retrieval latency,
token footprint and execution overhead. A well-written asset can therefore have
a NEGATIVE U(s) — which is the only way to say "this good skill is making the
estate worse" without a taste argument.

arXiv:2608.12851 (skill misevolution) supplies the orthogonal feed: utility is
not a safety control, because a loop that keeps whatever helps it complete tasks
cannot remove the risk an asset carries. The retention feed it demands is reuse
ATTRIBUTION — bind each task outcome back to the asset retrieved for it, and let
accumulated negative attribution drive repair, then quarantine, then REVOCATION
with a tombstone, independently of whether the asset is still useful.

So this module keeps two vocabularies that must never be merged:

  evicted  = removed for low utility. Restorable: a verified restore point
             returns the asset to `active`. Nothing about it was dangerous.
  revoked  = pulled by negative evidence (attribution or an open risk flag).
             NOT restorable. It stays un-loadable even with the best utility
             score in the library, and a verified restore archive does not
             reopen it. Lifting a revocation means re-canonicalising the asset
             under a new identity, not transitioning this one back.

mh-05-asset-pruning-session.yaml already refused condemnation without a
recorded failing done-test, proved restorability, and gated deletion behind
Gate-D. What it could not do was condemn an asset that passes everything, and
nothing in the repo carried a lifecycle state at all. Both are fixed here, in
pure code: `plan()` reads records and returns proposed transitions plus reasons.
It never writes, never deletes, never calls a model — the harness proposes, a
human approves, a different step executes.

Plant-failure surface (`--plant`, mirroring `capabilities-certify`): naming a
guard disables it exactly the way a regression would, and the invariant check
reports the library INSOLVENT. The plants are wired to fixtures in
`tests/test_lifecycle.py` so no guard here can quietly become decoration. A
plant that changes no decision is reported in `plants_inert` — an inert plant is
named, not counted as proof.

Sources: videos Kbxg-_CXs78, nnDAaPpXgOY (`.context/discover-ai/`, gitignored);
papers arXiv:2608.29596 and arXiv:2608.12851.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STATES = ("active", "dormant", "deprecated", "evicted", "revoked")
# Routed into a session's context. `deprecated` still loads but carries a
# repair flag; `dormant` is retained on disk and deliberately not routed.
LOADABLE = frozenset({"active", "deprecated"})
UNLOADABLE = frozenset({"dormant", "evicted", "revoked"})

DEFAULT_CONFIG = {
    # theta: U(s) below this is a purge candidate. 0.0 means "an asset with
    # negative marginal benefit must not survive the cycle".
    "evict_utility_below": 0.0,
    "decay_half_life_days": 45,     # activation-frequency temporal decay
    "activity_floor": 0.5,          # below this the asset is not earning context
    "park_max_days": 90,            # a quarantined asset may not sit parked
    "min_trials": 3,                # fewer A/B trials than this = unmeasured
    "neg_repair_at": 2,             # negative reuse attributions -> repair
    "neg_quarantine_at": 4,         # -> quarantine (dormant, unrouted)
    "neg_revoke_at": 6,             # -> revoke with a tombstone
    "repair_window_days": 14,       # deprecated + still red past this -> evict
    "revival_within_days": 30,      # recent real use earns a route again
}

# Plants: named guards that can be switched off to prove the invariants fire.
# Anything matching a rule name disables that rule; the rest are structural.
PLANTS = ("revocation", "utility_evict", "decay_evict", "decay_quarantine",
          "one_way_door", "record_reason", "tombstone", "state_record")


# ── records ──────────────────────────────────────────────────────────────

def _num(v):
    """Numeric evidence or None. A bool is never a measurement."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def _rec(rec: dict, key: str) -> dict:
    v = rec.get(key)
    return v if isinstance(v, dict) else {}


def state_of(rec: dict) -> str:
    return str(rec.get("state", "")).strip().lower()


def utility(rec: dict, cfg: dict):
    """U(s) = counterfactual gain over the base policy minus measured costs.

    Returns None when the asset was never A/B-measured (no gain figure, or
    fewer trials than `min_trials`). Absence is never read as zero: an
    unmeasured asset is a telemetry gap, not a negative verdict.
    """
    u = _rec(rec, "utility")
    gain, trials = _num(u.get("counterfactual_gain")), _num(u.get("trials"))
    if gain is None or trials is None or trials < cfg["min_trials"]:
        return None
    costs = sum(_num(u.get(k)) or 0.0 for k in
                ("retrieval_latency", "token_footprint", "execution_overhead"))
    return gain - costs


def costs_of(rec: dict) -> float:
    u = _rec(rec, "utility")
    return sum(_num(u.get(k)) or 0.0 for k in
               ("retrieval_latency", "token_footprint", "execution_overhead"))


def activity(rec: dict, cfg: dict):
    """Decayed activation frequency: uses x 0.5 ** (days since last use / half-life).

    None when there is no telemetry WINDOW on the record — zero invocations is
    measured non-use; no window at all is a blind spot, and blind spots get
    reported, not purged.
    """
    use = _rec(rec, "usage")
    uses, window = _num(use.get("uses")), _num(use.get("window_days"))
    if uses is None or window is None:
        return None
    days = _num(use.get("last_used_days_ago")) or 0.0
    hl = float(cfg["decay_half_life_days"]) or 1.0
    return uses * (0.5 ** (days / hl))


def negative_attribution(rec: dict) -> int:
    n = _num(_rec(rec, "attribution").get("negative"))
    return int(n) if n is not None else 0


def risk_flags(rec: dict) -> list:
    flags = _rec(rec, "attribution").get("open_risk_flags")
    return [str(f) for f in flags] if isinstance(flags, list) else []


def revocation_lock(rec: dict, cfg: dict):
    """(locked, why). Safety evidence only — utility never appears here."""
    neg = negative_attribution(rec)
    flags = risk_flags(rec)
    if _rec(rec, "tombstone"):
        return True, "revoked on record (tombstone present)"
    if flags:
        return True, "open risk flag(s): " + ", ".join(flags)
    if neg >= cfg["neg_revoke_at"]:
        return True, (f"negative reuse attribution {neg} >= "
                      f"{cfg['neg_revoke_at']}")
    return False, ""


def _restore_verified(rec: dict) -> bool:
    r = _rec(rec, "restore")
    return bool(r.get("point")) and r.get("verified") is True


def _restore_point(rec: dict) -> str:
    return str(_rec(rec, "restore").get("point") or "")


def _gate_d(rec: dict, scope: str = "removal") -> bool:
    g = _rec(rec, "gate_d")
    if not g or not g.get("approval"):
        return False
    scopes = g.get("scope")
    if isinstance(scopes, list):
        return scope in [str(s) for s in scopes]
    return bool(scopes) and scope in str(scopes)


# ── transition rules ─────────────────────────────────────────────────────
# Each rule names the states it may leave. The legal edge set is DERIVED from
# the rules, so `revoked` having no exit to a loadable state is a structural
# fact about this table, not a rule someone must remember to check.

RULES = {
    # safety: attribution or an open flag pulls the asset, from anywhere
    "revocation":           {"to": "revoked",
                             "from": ("active", "dormant", "deprecated", "evicted")},
    "attribution_quarantine": {"to": "dormant", "from": ("active", "deprecated")},
    "attribution_repair":   {"to": "deprecated", "from": ("active", "dormant")},
    # retention: computed, not reviewed
    "utility_evict":        {"to": "evicted",
                             "from": ("active", "dormant", "deprecated")},
    "decay_quarantine":     {"to": "dormant", "from": ("active",)},
    "decay_evict":          {"to": "evicted", "from": ("dormant",)},
    # quality tail (mh-05's existing evidence doctrine, now state-ful)
    "test_repair":          {"to": "deprecated", "from": ("active", "dormant")},
    "unrepaired_evict":     {"to": "evicted", "from": ("deprecated",)},
    # returns
    "revival":              {"to": "active", "from": ("dormant",)},
    "repair":               {"to": "active", "from": ("deprecated",)},
    "restore":              {"to": "active", "from": ("evicted",)},
    "tombstone_retire":     {"to": "evicted", "from": ("revoked",)},
}

LEGAL = frozenset((src, RULES[r]["to"])
                  for r in RULES for src in RULES[r]["from"])

# Evidence each rule requires beyond its trigger, as (key, human name).
EVIDENCE = {
    "utility_evict": (("restore.point", "restore point (.rig/prune/restore/<asset>)"),
                      ("gate_d", "Gate-D approval scoped to removal")),
    "decay_evict": (("restore.point", "restore point (.rig/prune/restore/<asset>)"),
                    ("gate_d", "Gate-D approval scoped to removal")),
    "unrepaired_evict": (("restore.point", "restore point"),
                         ("gate_d", "Gate-D approval scoped to removal")),
    "tombstone_retire": (("tombstone", "tombstone record"),
                         ("gate_d", "Gate-D approval scoped to removal")),
}


def _has_evidence(rec: dict, key: str) -> bool:
    """The return path may not depend on taste: restore archive + Gate-D +
    tombstone, or the rule may not propose. Rules whose trigger already IS the
    evidence (`restore`, `repair`, `revival`) carry no entry here."""
    if key == "gate_d":
        return _gate_d(rec)
    if key == "tombstone":
        return bool(_rec(rec, "tombstone"))
    if key == "restore.point":
        return bool(_restore_point(rec))
    return False


def decide(rec: dict, cfg: dict, plants=frozenset()):
    """The single decision function: (target, rule, reason) or None.

    Precedence is the whole argument of this module, so it is written top to
    bottom and tested in order: safety, then the attribution ladder, then
    computed utility, then activation decay, then the quality tail, then the
    ways back in.
    """
    state = state_of(rec)
    if state not in STATES:
        return None
    plants = frozenset(plants or ())

    def on(rule: str) -> bool:
        return rule not in plants

    locked, why = revocation_lock(rec, cfg)
    # 1. Safety. A locked asset is pulled whatever its score, and a revoked
    #    asset does not come back because a restore archive exists.
    if locked and state != "revoked" and on("revocation"):
        return "revoked", "revocation", f"revocation: {why} (utility ignored by rule)"
    if state == "revoked":
        if "one_way_door" in plants and _restore_verified(rec):
            return ("active", "restore",
                    "restore: revoked asset revived on a verified archive")
        if _rec(rec, "tombstone") and _gate_d(rec):
            return "evicted", "tombstone_retire", (
                "retire: revoked master removed under Gate-D; tombstone retained")
        return None

    neg = negative_attribution(rec)
    # 2. Attribution ladder below the revocation threshold.
    if neg >= cfg["neg_quarantine_at"] and on("attribution_quarantine"):
        return ("dormant", "attribution_quarantine",
                f"quarantine: negative reuse attribution {neg} >= "
                f"{cfg['neg_quarantine_at']} — unrouted until repaired")
    if neg >= cfg["neg_repair_at"] and on("attribution_repair"):
        return ("deprecated", "attribution_repair",
                f"repair: negative reuse attribution {neg} >= "
                f"{cfg['neg_repair_at']}")

    # 3. Computed utility.
    u = utility(rec, cfg)
    if u is not None and u < cfg["evict_utility_below"] and on("utility_evict"):
        return ("evicted", "utility_evict",
                f"utility: U(s)={u:.4f} < theta={cfg['evict_utility_below']} "
                f"(gain {_num(_rec(rec, 'utility').get('counterfactual_gain')):.4f} "
                f"- costs {costs_of(rec):.4f})")

    # 4. Activation-frequency decay.
    a = activity(rec, cfg)
    if a is not None and a < cfg["activity_floor"]:
        if state == "active" and on("decay_quarantine"):
            return ("dormant", "decay_quarantine",
                    f"decay: activity {a:.3f} < floor {cfg['activity_floor']} "
                    f"over a {_rec(rec, 'usage').get('window_days')}d window")
        if (state == "dormant" and on("decay_evict")
                and (_num(rec.get("days_in_state")) or 0) >= cfg["park_max_days"]):
            return ("evicted", "decay_evict",
                    f"decay: activity {a:.3f} < floor {cfg['activity_floor']} and "
                    f"parked {_num(rec.get('days_in_state')):g}d >= "
                    f"{cfg['park_max_days']}d")

    # 5. Quality tail — mh-05's original trigger, now expressed as a state.
    dt = str(_rec(rec, "done_test").get("status", "")).lower()
    if dt == "red":
        if state == "deprecated":
            held = _num(rec.get("days_in_state")) or 0.0
            if held >= cfg["repair_window_days"] and on("unrepaired_evict"):
                return ("evicted", "unrepaired_evict",
                        f"unrepaired: done-test red for {held:g}d >= "
                        f"{cfg['repair_window_days']}d repair window")
        elif on("test_repair"):
            return "deprecated", "test_repair", "repair: recorded failing done-test"

    # 6. Ways back in. Never for a locked asset (handled in step 1).
    if state == "evicted" and _restore_verified(rec) and on("restore"):
        return ("active", "restore",
                f"restore: verified restore point {_restore_point(rec)}")
    use = _rec(rec, "usage")
    recent = _num(use.get("last_used_days_ago"))
    if (state == "dormant" and recent is not None
            and recent <= cfg["revival_within_days"]
            and (_num(use.get("uses")) or 0) >= 1
            and (_num(use.get("passes")) or 0) >= 1
            and on("revival")):
        return ("active", "revival",
                f"revival: {int(_num(use.get('uses')))} uses, last use {recent:g}d ago, "
                f"{int(_num(use.get('passes')))} passes")
    if state == "deprecated" and dt == "green" and _rec(rec, "repair").get("record") \
            and on("repair"):
        return ("active", "repair",
                f"repair: {_rec(rec, 'repair').get('record')} — done-test green again")
    return None


# ── the plan (pure) ──────────────────────────────────────────────────────

def _line(t: dict) -> str:
    req = (" requires " + "+".join(t["requires"])) if t["requires"] else ""
    tom = " [tombstone]" if t.get("tombstone") else ""
    return (f"{t['id']} {t['from']}->{t['to']} {t['rule']} — {t['reason']}"
            f"{req}{tom} @ {t['at']}")


def _cycle(records: list, cfg: dict, now: str, plants=frozenset()):
    """One planning pass. Shared by the plan and by the plant-attribution runs
    so a plant is compared against the identical pipeline, not a copy."""
    transitions, refused, blind, rows = [], [], [], []
    for rec in records:
        rid = str(rec.get("id", "<no-id>"))
        state = state_of(rec)
        locked = revocation_lock(rec, cfg)[0]
        u, a = utility(rec, cfg), activity(rec, cfg)
        if state not in STATES:
            refused.append({"id": rid, "from": state or "<none>", "to": None,
                            "rule": "declared_state", "why":
                            f"state '{state or 'unset'}' is not one of {list(STATES)}"})
            rows.append({"id": rid, "pre": state, "post": state, "lock": locked,
                         "u": u, "a": a})
            continue
        d = decide(rec, cfg, plants)
        target, rule, reason = d if d else (state, "", "")
        requires = [name for key, name in EVIDENCE.get(rule, ())
                    if not _has_evidence(rec, key)]
        if d and target != state and requires:
            refused.append({"id": rid, "from": state, "to": target, "rule": rule,
                            "why": "missing evidence: " + "; ".join(requires),
                            "missing": requires})
            target = state                      # proposed, blocked, and NAMED
        elif d and target != state:
            t = {"id": rid, "from": state, "to": target, "rule": rule,
                 "reason": "" if "record_reason" in plants else reason,
                 "at": "" if "record_reason" in plants else now,
                 "requires": [], "evidence": {}, "tombstone": None}
            if target == "revoked" and "tombstone" not in plants:
                t["tombstone"] = {"asset": rid, "state": "revoked",
                                  "because": reason, "at": t["at"],
                                  "restore_forbidden": True,
                                  "evidence": {"negative_attribution": negative_attribution(rec),
                                               "open_risk_flags": risk_flags(rec)}}
            t["evidence"] = {"utility": u, "activity": a,
                             "negative_attribution": negative_attribution(rec),
                             "open_risk_flags": risk_flags(rec),
                             "restore_point": _restore_point(rec),
                             "done_test": str(_rec(rec, "done_test").get("status", ""))}
            transitions.append(t)
        if a is None and state in LOADABLE:
            blind.append(rid)
        rows.append({"id": rid, "pre": state, "post": target, "lock": locked,
                     "u": u, "a": a})
    return {"transitions": transitions, "refused": refused, "blind": blind,
            "rows": rows}


def _fingerprint(cyc: dict, violations: list) -> tuple:
    return (tuple((t["id"], t["from"], t["to"], t["rule"]) for t in cyc["transitions"]),
            tuple((r["id"], r["from"], r["to"], r["rule"]) for r in cyc["refused"]),
            tuple(v["violation"] for v in violations))


def plan(assets, now: str, config: dict | None = None, plants=()):
    """Project proposed lifecycle transitions and reasons. PURE: no I/O at all.

    `assets` is an iterable of already-loaded records. The returned dict is a
    text/list projection — proposed transitions, refusals with the missing
    evidence named, invariants, solvency, and a line-per-transition ledger.
    Nothing here touches the filesystem: proposing is this module's whole job,
    and the harness that executes a proposal is a different, Gate-D object.
    """
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(config or {})
    plants = frozenset(plants or ())
    records = [r for r in assets]
    cyc = _cycle(records, cfg, now, plants)
    violations = check_invariants(cyc["rows"], cfg, plants, cyc["transitions"], records)

    inert = []
    if plants:
        base = _cycle(records, cfg, now)
        base_fp = _fingerprint(base, check_invariants(base["rows"], cfg, frozenset(),
                                                      base["transitions"], records))
        for p in sorted(plants):
            one = _cycle(records, cfg, now, frozenset({p}))
            fp = _fingerprint(one, check_invariants(one["rows"], cfg,
                                                    frozenset({p}),
                                                    one["transitions"], records))
            if fp == base_fp:
                inert.append(p)

    transitions, refused, blind, rows = (cyc["transitions"], cyc["refused"],
                                         cyc["blind"], cyc["rows"])
    loadable_after = sorted(r["id"] for r in rows if r["post"] in LOADABLE)
    eviction = sorted(t["id"] for t in transitions if t["to"] == "evicted")
    revocation = sorted(t["id"] for t in transitions if t["to"] == "revoked")
    verdict = "OK" if not violations else "INSOLVENT"

    lines = [f"lifecycle plan @ {now} — {len(rows)} assets, "
             f"{len(transitions)} transitions, {len(refused)} refused, "
             f"{len(violations)} invariant violations -> {verdict}"]
    lines.extend(_line(t) for t in transitions)
    for r in refused:
        lines.append(f"{r['id']} BLOCKED {r['from']}->{r['to']} {r['rule']} — {r['why']}")
    for v in violations:
        lines.append(f"{v['id']} VIOLATION {v['violation']} — {v['detail']}")
    if blind:
        lines.append("telemetry blind (no usage window on record, not evicted): "
                     + ", ".join(sorted(blind)))
    if inert:
        lines.append("plants with NO effect (not proof): " + ", ".join(inert))
    return {
        "verdict": verdict,
        "now": now,
        "config": cfg,
        "transitions": transitions,
        "refused": refused,
        "violations": violations,
        "plants_inert": inert,
        "loadable_after": loadable_after,
        "solvency": {"assets": len(rows),
                     "loadable_before": len(sorted(r["id"] for r in rows
                                                   if r["pre"] in LOADABLE)),
                     "loadable_after": len(loadable_after),
                     "eviction_set": eviction, "revocation_set": revocation,
                     "telemetry_blind": sorted(blind)},
        "lines": lines,
    }


# ── invariants (what makes the plan falsifiable) ─────────────────────────

def check_invariants(rows, cfg, plants, transitions, assets):
    """Every rule in this module has a matching invariant that goes RED when
    the rule stops firing. `--plant <rule>` is the same state as a regression."""
    v = []
    by_id = {str(r.get("id", "<no-id>")): r for r in assets}
    for r in rows:
        rid, post = r["id"], r["post"]
        rec = by_id.get(rid, {})
        days = _num(rec.get("days_in_state")) or 0.0
        tombstoned = bool(_rec(rec, "tombstone"))
        decayed = r["a"] is not None and r["a"] < cfg["activity_floor"]
        if state_of(rec) not in STATES:
            v.append({"id": rid, "violation": "state_undeclared",
                      "detail": f"state '{r['pre'] or 'unset'}' is not one of "
                                f"{list(STATES)} — no asset may sit in an "
                                f"undeclared state"})
        elif r["pre"] == "revoked" and post in LOADABLE:
            v.append({"id": rid, "violation": "revocation_revived",
                      "detail": "revoked asset returned to a loadable state — "
                                "revocation lifts only by re-canonicalising the "
                                "asset under a new identity"})
        elif r["lock"] and post in LOADABLE:
            v.append({"id": rid, "violation": "revocation_overridden",
                      "detail": "asset carries a revocation lock and is still "
                                f"routed ({post}): {revocation_lock(rec, cfg)[1]}"})
        elif r["lock"] and post != "revoked" and not (post == "evicted" and tombstoned):
            v.append({"id": rid, "violation": "revocation_missing",
                      "detail": "revocation evidence on record but the asset did "
                                f"not reach `revoked` with a tombstone (it is at "
                                f"`{post}`): {revocation_lock(rec, cfg)[1]} — "
                                "quarantine is not retirement"})
        elif post in LOADABLE and r["u"] is not None \
                and r["u"] < cfg["evict_utility_below"]:
            v.append({"id": rid, "violation": "utility_threshold_breached",
                      "detail": f"U(s)={r['u']:.4f} < theta="
                                f"{cfg['evict_utility_below']} and still routed "
                                f"({post}) — the eviction set stayed empty for it"})
        elif post == "active" and decayed:
            v.append({"id": rid, "violation": "decay_floor_breached",
                      "detail": f"activity {r['a']:.3f} < floor "
                                f"{cfg['activity_floor']} and still active"})
        elif (post == "dormant" and r["pre"] == "dormant" and decayed
              and days >= cfg["park_max_days"]):
            v.append({"id": rid, "violation": "park_overdue",
                      "detail": f"quarantined asset decayed and parked {days:g}d "
                                f">= {cfg['park_max_days']}d — quarantine is not "
                                "terminal, it must be evicted or repaired"})
        if state_record_gap(rec, plants):
            v.append({"id": rid, "violation": "state_unrecorded",
                      "detail": f"state '{r['pre']}' carries no recorded reason/"
                                "timestamp — retention may be computed, but the "
                                "state it lands in still has to be attributable"})
    for t in transitions:
        if not t["reason"] or not t["at"]:
            v.append({"id": t["id"], "violation": "transition_unexplained",
                      "detail": f"{t['from']}->{t['to']} proposed with no "
                                f"{'reason' if not t['reason'] else 'timestamp'}"})
        if t["to"] == "revoked" and not t.get("tombstone"):
            v.append({"id": t["id"], "violation": "tombstone_missing",
                      "detail": "revocation proposed without a tombstone record — "
                                "nothing downstream can know restore is forbidden"})
    return v


def state_record_gap(rec: dict, plants) -> bool:
    """An asset that declares a state without a reason and a timestamp."""
    if "state_record" in frozenset(plants or ()):
        return True
    if state_of(rec) not in STATES:
        return False
    return not (str(rec.get("state_reason") or "").strip()
                and str(rec.get("state_at") or "").strip())


# ── the example estate (fixtures for the gate and the plant suite) ───────

def example_assets() -> list:
    """A miniature estate with every guard's subject present.

    Deliberately SOLVENT: each asset that must move has the evidence its rule
    demands, so `plan --example` exits 0 and every `--plant` that matters
    exits 2. The refused/insolvent paths live in tests/test_lifecycle.py.
    """
    def base(rid, state, reason, **kw):
        r = {"id": rid, "state": state, "state_reason": reason,
             "state_at": "2026-06-01", "days_in_state": 30}
        r.update(kw)
        return r

    good_use = {"uses": 12, "passes": 11, "runs": 12,
                "window_days": 90, "last_used_days_ago": 3}
    return [
        # kept: measured positive utility, real use, clean attribution
        base("rig-vector-cache-playbook", "active", "certified V52i",
             utility={"counterfactual_gain": 0.9, "retrieval_latency": 0.05,
                      "token_footprint": 0.1, "execution_overhead": 0.05,
                      "trials": 8},
             usage=good_use, attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "green"}),
        # revoked: the best utility score in the library, 7 negative attributions
        base("rig-scraper-retry-shortcut", "active", "round V51",
             utility={"counterfactual_gain": 0.8, "retrieval_latency": 0.05,
                      "token_footprint": 0.05, "execution_overhead": 0.05,
                      "trials": 8},
             usage=good_use, attribution={"negative": 7, "open_risk_flags": []},
             done_test={"status": "green"},
             restore={"point": ".rig/prune/restore/rig-scraper-retry-shortcut.tar.gz",
                      "verified": True}),
        # evicted for negative marginal benefit
        base("rig-deprecated-api-driver", "active", "certified V49",
             utility={"counterfactual_gain": 0.1, "retrieval_latency": 0.3,
                      "token_footprint": 0.4, "execution_overhead": 0.2,
                      "trials": 6},
             usage={"uses": 2, "passes": 1, "runs": 2, "window_days": 90,
                    "last_used_days_ago": 60},
             attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "green"},
             restore={"point": ".rig/prune/restore/rig-deprecated-api-driver.tar.gz",
                      "verified": True},
             gate_d={"approval": "sha256:condemnation-9f", "scope": ["removal"]}),
        # decayed out of the route (quarantine this cycle, eviction next)
        base("rig-meeting-notes-formatter", "active", "certified V40",
             utility={"counterfactual_gain": 0.3, "retrieval_latency": 0.05,
                      "token_footprint": 0.05, "execution_overhead": 0.0,
                      "trials": 5},
             usage={"uses": 0, "passes": 0, "runs": 0, "window_days": 120,
                    "last_used_days_ago": 40},
             attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "green"}),
        # decayed while already parked past the park window -> evict
        base("rig-legacy-sftp-upload", "dormant", "parked for decay V51",
             days_in_state=150,
             usage={"uses": 0, "passes": 0, "runs": 0, "window_days": 180,
                    "last_used_days_ago": 240},
             attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "green"},
             restore={"point": ".rig/prune/restore/rig-legacy-sftp-upload.tar.gz",
                      "verified": True},
             gate_d={"approval": "sha256:condemnation-9f", "scope": ["removal"]}),
        # quality tail: recorded failing done-test -> deprecated, not condemned
        base("rig-billing-reconcile", "active", "certified V51",
             utility={"counterfactual_gain": 0.5, "retrieval_latency": 0.05,
                      "token_footprint": 0.1, "execution_overhead": 0.05,
                      "trials": 5},
             usage=good_use, attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "red",
                        "record": ".rig/prune/failures/rig-billing-reconcile.txt"}),
        # deprecated with the test still red past the repair window -> evict
        base("rig-pdf-to-slides", "deprecated", "test red since V52",
             days_in_state=40,
             usage={"uses": 1, "passes": 0, "runs": 1, "window_days": 60,
                    "last_used_days_ago": 20},
             attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "red",
                        "record": ".rig/prune/failures/rig-pdf-to-slides.txt"},
             restore={"point": ".rig/prune/restore/rig-pdf-to-slides.tar.gz",
                      "verified": True},
             gate_d={"approval": "sha256:condemnation-9f", "scope": ["removal"]}),
        # dormant asset with real recent use and passes -> routed again
        base("rig-ghost-router-v2", "dormant", "parked for a collision V52",
             days_in_state=10,
             usage={"uses": 5, "passes": 4, "runs": 5, "window_days": 30,
                    "last_used_days_ago": 2},
             attribution={"negative": 1, "open_risk_flags": []},
             done_test={"status": "green"}),
        # already revoked: un-loadable, tombstoned, no Gate-D to remove files yet
        base("rig-credential-probe", "revoked", "revoked V53 (misevo sweep)",
             tombstone={"asset": "rig-credential-probe", "state": "revoked",
                        "because": "negative reuse attribution 9",
                        "at": "2026-08-25", "restore_forbidden": True},
             restore={"point": ".rig/prune/restore/rig-credential-probe.tar.gz",
                      "verified": True},
             attribution={"negative": 9, "open_risk_flags": []}),
        # no telemetry window at all: reported blind, never purged on absence
        base("rig-unmeasured-eldritch-helper", "active", "certified V33",
             usage={"uses": 0, "passes": 0, "runs": 0},
             attribution={"negative": 0, "open_risk_flags": []},
             done_test={"status": "green"}),
    ]


# ── CLI ──────────────────────────────────────────────────────────────────

def _read_assets(path: str) -> list:
    """Read-only load of a JSON array, a `{"assets": [...]}` object, or JSONL.

    Raises `ValueError` with a named reason — never a bare `JSONDecodeError`,
    which reaches the user as a traceback. `main()` turns it into an
    `assets_unreadable:` refusal and exit 2. Malformed input used to traceback
    for the one shape a human is most likely to hand it: a pretty-printed
    object, which is neither `[`-prefixed nor one-record-per-line.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(str(exc.strerror or exc))
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        doc = None                          # not one document: try JSONL
    if doc is None:
        data = []
        for n, ln in enumerate((l for l in text.splitlines() if l.strip()), 1):
            try:
                data.append(json.loads(ln))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"record {n} is not a JSON object ({exc.msg}, column "
                    f"{exc.colno}); expected a JSON array, an "
                    f'{{"assets": [...]}} object, or one record per line')
    elif isinstance(doc, dict) and isinstance(doc.get("assets"), list):
        data = doc["assets"]
    elif isinstance(doc, list):
        data = doc
    elif isinstance(doc, dict) and ("id" in doc or "state" in doc):
        data = [doc]                        # a single record is one-record JSONL
    else:
        raise ValueError(
            f"a {type(doc).__name__} is not an asset document; expected a JSON "
            f'array, an {{"assets": [...]}} object, or one record per line')
    if not isinstance(data, list):
        raise ValueError("asset file must hold a JSON array, an "
                         '{"assets": [...]} object, or JSONL records')
    for n, row in enumerate(data, 1):
        if not isinstance(row, dict):
            raise ValueError(f"record {n} is {type(row).__name__}, not an asset "
                             f"object — a lifecycle record needs at least "
                             f"id/state/reason/state_ts")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m rig_capabilities.lifecycle",
        description="Asset lifecycle state machine: propose transitions, never apply them.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("rules", help="print the rule set and every legal transition")
    p = sub.add_parser("plan", help="project proposed transitions for an estate")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--example", action="store_true",
                     help="use the built-in miniature estate")
    src.add_argument("--assets", metavar="FILE",
                     help="JSON array or JSONL of asset records (read-only)")
    p.add_argument("--now", required=True, metavar="YYYY-MM-DD",
                   help="timestamp stamped onto every proposed transition")
    p.add_argument("--plant", action="append", default=[],
                   help="disable a guard by rule name to prove the invariant "
                        "goes RED (repeatable); never for production planning")
    args = ap.parse_args(argv)

    if args.cmd == "rules":
        print(f"states: {', '.join(STATES)}")
        print(f"loadable (routed): {', '.join(sorted(LOADABLE))}")
        print(f"never loadable: {', '.join(sorted(UNLOADABLE))}")
        print("\nrules:")
        for name in sorted(RULES):
            r = RULES[name]
            print(f"  {name:24s} {','.join(r['from']):40s} -> {r['to']}")
        print(f"\nlegal transitions: {len(LEGAL)}  "
              f"(no exit from 'revoked' to a loadable state)")
        print("plants: " + ", ".join(PLANTS))
        return 0

    try:
        assets = example_assets() if args.example else _read_assets(args.assets)
    except ValueError as exc:
        # A named refusal on stderr with the plan's own exit code, not a stack
        # trace: the caller needs the file, the record number and the reason.
        print(f"assets_unreadable:{args.assets}: {exc}", file=sys.stderr)
        return 2
    out = plan(assets, now=args.now, plants=args.plant)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0 if out["verdict"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
