"""E_stage: the per-Studio promotion gate for a candidate model.

From `Claude Fable 5.1 — RIG Fleet Install, Routing Policy & Breaking-Change
Audit` (shipped Sept 1, 2026), Promotion gate — nothing ships at 0σ: "Fable 5.1
enters a Studio's tool-allowlist only when a golden-run replay shows strictly
lower `E_stage` than Opus 5 on that Studio's own missions."

E_stage is the loss the Studio actually pays, in three terms, lower is better:
  fail   0.60 — gates the mission was required to pass
  cost   0.25 — spend against the mission's declared ceiling
  turns  0.15 — turns against the mission's declared turn budget

Budgets in `capabilities/golden/<Studio>/missions.json` are DECLARED ceilings,
not measurements. Measured cost/turns/gates arrive only in replay records.
A run scored against a zero or missing ceiling is not a measurement, it is a
hole, so it raises rather than silently contributing a free term.

No automatic Fable-to-earlier-family fallback exists. The card's breaking
change 2 is explicit: earlier models cannot read Fable 5.1 thinking blocks, so
a Fable 5.1 → Opus 4.8 ladder "will silently lose reasoning state mid-mission".
Therefore a failed Fable mission terminates FAIL/BLOCKED — it is never silently
re-run on an earlier family. Any later Opus attempt is a NEW mission started
from non-thinking artifacts, with its own mission_id and its own E_stage.
`AUTO_FALLBACK_TO_EARLIER_FAMILY` is pinned False and exported so the route
layer can assert it instead of restating it.

Gate weights are pinned in each manifest for provenance and signature
stability; the fail term is the plain mean over the scored gates, exactly as the
frozen contract specifies. Nothing here is weighted behind the contract's back.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

E_STAGE_WEIGHTS = {"fail": 0.6, "cost": 0.25, "turns": 0.15}

# Pinned: cross-family downgrade is a governance incident, not a retry strategy.
AUTO_FALLBACK_TO_EARLIER_FAMILY = False

# Kill criteria, verbatim from the card: "Token spend rises >30% with no C_t
# movement over two weeks → revert to Opus 5 default and re-open the eval".
SPEND_GROWTH_REVOKE = 0.30
REVOKE_WINDOW_WEEKS = 2
REVOKE_REMEDY = "revert to Opus 5"

GOLDEN_ROOT = "capabilities/golden"
MANIFEST_SCHEMA = "rig.golden.missions.v1"
SIGNATURE_FIELD = "manifest_signature"
GOLDEN_STATUSES = ("DORMANT", "ACTIVE", "REVOKED")
# Mirrors register.STUDIOS (owned by rig_capabilities/register.py) for the
# golden-set loader; the register enum stays authoritative.
GOLDEN_STUDIOS = ("Design", "App", "GTM", "LinkedIn", "Strategy",
                  "CompanyOSFactory")

_FAMILIES = ("fable", "opus", "sonnet", "haiku", "gpt", "kimi", "gemini")
_PASS = ("PASS", "PASSED", "GREEN", "OK")


class GoldenSetInvalid(Exception):
    """The golden set or a replay against it is unusable — never guess through."""


# ------------------------------------------------------------------ primitives
def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def _num(value, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GoldenSetInvalid(f"{what}_not_a_number")
    return float(value)


def family_of(name) -> str:
    """Model id or model name -> family token. `claude-fable-5-1` and `Fable 5.1`
    both resolve to `fable`; an unknown/empty name resolves to ''."""
    s = str(name or "").strip().lower()
    if not s:
        return ""
    for fam in _FAMILIES:
        if fam in s:
            return fam
    return s


# ------------------------------------------------------------------ the math
def _mission_of(run) -> dict:
    if not isinstance(run, dict):
        raise GoldenSetInvalid("run_not_an_object")
    man = run.get("mission")
    return man if isinstance(man, dict) else run


def _budgets(run) -> tuple[float, float]:
    """(cost_budget_usd, turn_budget) — zero or absent is a broken golden set."""
    man = _mission_of(run)
    mid = str(run.get("mission_id") or man.get("id") or "?")
    out = []
    for key in ("cost_budget_usd", "turn_budget"):
        if key not in man or man[key] in (None, ""):
            raise GoldenSetInvalid(f"budget_missing:{key}:{mid}")
        val = _num(man[key], f"{key}:{mid}")
        if val <= 0:
            raise GoldenSetInvalid(f"budget_not_positive:{key}:{mid}")
        out.append(val)
    return out[0], out[1]


def _gates(run) -> list[dict]:
    gates = run.get("gates")
    if gates is None:
        gates = run.get("gate_results")
    if not isinstance(gates, list):
        raise GoldenSetInvalid(
            f"gates_missing:{run.get('mission_id', '?')}")
    out = []
    for g in gates:
        if not isinstance(g, dict) or not g.get("id"):
            raise GoldenSetInvalid(f"gate_unnamed:{run.get('mission_id', '?')}")
        out.append(g)
    return out


def fail_loss(run) -> float:
    """1.0 if any blocking gate missed; else the mean of (1 - score) over the
    scored gates; 0.0 when nothing was scored and nothing failed."""
    gates = _gates(run)
    for g in gates:
        if not bool(g.get("blocking")):
            continue
        status = str(g.get("status") or "").strip().upper()
        if not status:
            raise GoldenSetInvalid(f"gate_status_missing:{g['id']}")
        if status not in _PASS:
            return 1.0
    scored = [g for g in gates
              if isinstance(g.get("score"), (int, float))
              and not isinstance(g.get("score"), bool)]
    if not scored:
        return 0.0
    return sum(1.0 - _clamp(_num(g["score"], f"score:{g['id']}"))
               for g in scored) / len(scored)


def e_stage(run) -> float:
    """Weighted loss for one mission run. Lower is better."""
    cost_budget, turn_budget = _budgets(run)
    mid = str(run.get("mission_id") or "?")
    for key in ("cost_usd", "turns"):
        if key not in run or run[key] in (None, ""):
            raise GoldenSetInvalid(f"measurement_missing:{key}:{mid}")
    cost_loss = _clamp(_num(run["cost_usd"], f"cost_usd:{mid}") / cost_budget)
    turns_loss = _clamp(_num(run["turns"], f"turns:{mid}") / turn_budget)
    losses = {"fail": fail_loss(run), "cost": cost_loss, "turns": turns_loss}
    return sum(E_STAGE_WEIGHTS[k] * losses[k] for k in E_STAGE_WEIGHTS)


# ------------------------------------------------------------------ compare
def _mission_index(missions) -> dict:
    """Golden manifests list missions; replay docs key them by id. Either shape."""
    out: dict = {}
    if isinstance(missions, dict):
        for key, val in missions.items():
            if isinstance(val, dict):
                out[str(key)] = val
    elif isinstance(missions, list):
        for m in missions:
            if isinstance(m, dict) and m.get("id"):
                out[str(m["id"])] = m
    return out


def _mission_id(run) -> str:
    mid = str(run.get("mission_id") or run.get("id") or "")
    if not mid:
        raise GoldenSetInvalid("run_missing_mission_id")
    return mid


def _runs(spec, side: str) -> list[dict]:
    """Accept a run list or a replay doc {runs, missions}; bind each run to the
    mission entry that carries its declared ceilings."""
    if isinstance(spec, dict):
        runs = spec.get("runs")
        if not isinstance(runs, list):
            raise GoldenSetInvalid(f"{side}_runs_missing")
        idx = _mission_index(spec.get("missions"))
        out = []
        for raw in runs:
            if not isinstance(raw, dict):
                raise GoldenSetInvalid(f"{side}_run_not_an_object")
            run = dict(raw)
            mid = _mission_id(run)
            if not isinstance(run.get("mission"), dict) and mid in idx:
                run["mission"] = idx[mid]
            out.append(run)
        return out
    if isinstance(spec, list):
        out = []
        for raw in spec:
            if not isinstance(raw, dict):
                raise GoldenSetInvalid(f"{side}_run_not_an_object")
            _mission_id(raw)
            out.append(dict(raw))
        return out
    raise GoldenSetInvalid(f"{side}_runs_invalid")


def _by_mission(runs, side: str) -> dict:
    out = {}
    for run in runs:
        mid = _mission_id(run)
        if mid in out:
            raise GoldenSetInvalid(f"duplicate_mission_id:{mid}")
        out[mid] = run
    if not out:
        raise GoldenSetInvalid(f"empty_golden_set:{side}")
    return out


def compare(baseline_runs, candidate_runs) -> dict:
    """Pairwise E_stage over one frozen mission set, matched by mission_id.

    A mission present on one side only is a broken golden set, never a skip.
    """
    base = _by_mission(_runs(baseline_runs, "baseline"), "baseline")
    cand = _by_mission(_runs(candidate_runs, "candidate"), "candidate")
    only_base = sorted(set(base) - set(cand))
    only_cand = sorted(set(cand) - set(base))
    if only_base or only_cand:
        raise GoldenSetInvalid(
            "mission_set_mismatch:"
            f"missing_in_candidate={','.join(only_base) or '-'}"
            f"|extra_in_candidate={','.join(only_cand) or '-'}")
    rows = []
    for mid in sorted(base):
        b_cost, b_turn = _budgets(base[mid])
        c_cost, c_turn = _budgets(cand[mid])
        if (b_cost, b_turn) != (c_cost, c_turn):
            raise GoldenSetInvalid(f"budget_mismatch:{mid}")
        e_base = e_stage(base[mid])
        e_cand = e_stage(cand[mid])
        rows.append({"mission_id": mid, "e_baseline": e_base,
                     "e_candidate": e_cand,
                     "strictly_lower": e_cand < e_base})
    n = len(rows)
    mean_base = sum(r["e_baseline"] for r in rows) / n
    mean_cand = sum(r["e_candidate"] for r in rows) / n
    return {"per_mission": rows, "mean_baseline": mean_base,
            "mean_candidate": mean_cand, "n": n,
            "strictly_lower_everywhere": all(r["strictly_lower"]
                                             for r in rows)}


# ------------------------------------------------------------- promotion gate
def _flag(value) -> bool:
    """A signal can arrive as a bool or as the list of things that tripped it."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, set)):
        return bool(value)
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in ("", "no", "false", "none", "clean")
    return bool(value)


def promotion_verdict(studio, cmp, spend) -> dict:
    """Per-Studio promotion decision. promote True only on a clean sweep.

    `spend` is the promotion evidence packet the dispatcher hands over:
      candidate_family / verifier_family — model families (id or name, either)
      manifest_signature — signature pinned in the golden manifest
      replay_signature   — signature the replay declares it ran under
      blocking_gate_regression — bool or list of mission ids (default False)
      forced_tool_choice — audit verdict for reachable harnesses (default False)
    The two regression signals default absent=False; the caller that actually
    ran `model_route.audit_forced_tool_choice` MUST pass its verdict, because
    this function cannot see the harness tree from here.
    """
    if not str(studio or "").strip():
        raise GoldenSetInvalid("studio_missing")
    if not isinstance(cmp, dict) or not isinstance(spend, dict):
        raise GoldenSetInvalid("compare_result_invalid")
    rows = cmp.get("per_mission")
    if not isinstance(rows, list) or not rows:
        raise GoldenSetInvalid("compare_result_invalid")
    reasons: list[str] = []

    worse, lowered = [], 0
    for row in rows:
        if not isinstance(row, dict) or not row.get("mission_id"):
            raise GoldenSetInvalid("compare_result_invalid")
        e_base = _num(row.get("e_baseline"), "e_baseline")
        e_cand = _num(row.get("e_candidate"), "e_candidate")
        if e_cand < e_base:
            lowered += 1
        else:
            worse.append(str(row["mission_id"]))
    strictly_everywhere = bool(cmp.get("strictly_lower_everywhere"))
    if strictly_everywhere != (lowered == len(rows)):
        raise GoldenSetInvalid("compare_result_inconsistent")
    if worse:
        reasons.extend(f"not_strictly_lower:{mid}" for mid in worse)

    mean_base = _num(cmp.get("mean_baseline"), "mean_baseline")
    mean_cand = _num(cmp.get("mean_candidate"), "mean_candidate")
    if abs(sum(r["e_candidate"] for r in rows) / len(rows) - mean_cand) > 1e-9 \
            or abs(sum(r["e_baseline"] for r in rows) / len(rows)
                   - mean_base) > 1e-9:
        raise GoldenSetInvalid("compare_result_inconsistent")
    if not mean_cand < mean_base:
        reasons.append("mean_not_improved")

    if _flag(spend.get("blocking_gate_regression")):
        reasons.append("blocking_gate_regression")

    cand_fam = family_of(spend.get("candidate_family"))
    ver_fam = family_of(spend.get("verifier_family"))
    if not cand_fam:
        reasons.append("candidate_family_missing")
    if not ver_fam:
        reasons.append("verifier_family_missing")
    if cand_fam and ver_fam and cand_fam == ver_fam:
        reasons.append("same_family_collusion")

    pinned = str(spend.get("manifest_signature") or "")
    ran = str(spend.get("replay_signature") or "")
    if not pinned or not ran:
        reasons.append("manifest_signature_missing")
    elif pinned != ran:
        reasons.append("manifest_signature_mismatch")

    if str(spend.get("studio") or "").strip() and \
            str(spend.get("studio")).strip() != str(studio).strip():
        reasons.append("studio_mismatch")

    if _flag(spend.get("forced_tool_choice")):
        reasons.append("forced_tool_choice_harness")

    return {"promote": not reasons, "reasons": reasons}


def revocation_check(studio, spend_series, c_t_series) -> dict:
    """Post-promotion circuit-breaker over the trailing two weeks.

    Revoke when token spend grew more than 30% across the window while C_t did
    not move up. Fewer than three weekly observations cannot conclude either
    way, so it reports not-revoked with `insufficient_history` rather than
    inventing a baseline.
    """
    spend = [float(x) for x in (spend_series or [])]
    ct = [float(x) for x in (c_t_series or [])]
    if len(spend) != len(ct):
        raise ValueError("spend_series and c_t_series must be the same length")
    need = REVOKE_WINDOW_WEEKS + 1
    out = {"studio": studio, "revoked": False, "spend_growth": None,
           "delta_c_t": None, "window_weeks": REVOKE_WINDOW_WEEKS,
           "observations": len(spend), "reasons": [], "remedy": None}
    if len(spend) < need:
        out["reasons"] = ["insufficient_history"]
        return out
    w_spend, w_ct = spend[-need:], ct[-need:]
    if w_spend[0] <= 0:
        out["reasons"] = ["spend_baseline_non_positive"]
        return out
    growth = (w_spend[-1] - w_spend[0]) / w_spend[0]
    delta = w_ct[-1] - w_ct[0]
    out["spend_growth"] = growth
    out["delta_c_t"] = delta
    if growth > SPEND_GROWTH_REVOKE and delta <= 0:
        out["revoked"] = True
        out["remedy"] = REVOKE_REMEDY
        out["reasons"] = [f"spend_growth_{round(growth * 100)}pct_no_ct_movement"]
    return out


def rebaseline_required(recorded_under, candidate_family) -> bool:
    """True when the golden set was not recorded under the candidate's family.

    Breaking change 3: editing earlier turns invalidates thinking blocks, so a
    baseline recorded under another family "must be re-baselined or it reports
    false divergence". Unknown provenance (recorded_under missing) is treated as
    requiring a re-baseline — an unlabelled baseline certifies nothing.
    """
    recorded = family_of(recorded_under)
    candidate = family_of(candidate_family)
    return not recorded or not candidate or recorded != candidate


# --------------------------------------------------------- golden manifests
def load_manifest(path):
    """Read a golden manifest and prove it is intact before anyone trusts it."""
    man = json.loads(Path(path).read_text(encoding="utf-8"))
    ok, reason = verify_manifest(man)
    if not ok:
        raise GoldenSetInvalid(f"manifest_invalid:{reason}:{path}")
    return man


def input_hash(mission: dict) -> str:
    """sha256 over the mission's declared inputs — the replay feeds exactly
    these, or it is a different mission."""
    return hashlib.sha256(
        _canonical(list(mission.get("inputs") or [])).encode("utf-8")).hexdigest()


def manifest_signature(manifest: dict) -> str:
    """sha256 over the manifest with the signature field removed."""
    body = {k: v for k, v in manifest.items() if k != SIGNATURE_FIELD}
    return "sha256:" + hashlib.sha256(
        _canonical(body).encode("utf-8")).hexdigest()


def verify_manifest(manifest: dict) -> tuple[bool, str]:
    """Structural + integrity check on one golden manifest."""
    if not isinstance(manifest, dict):
        return False, "manifest_not_an_object"
    if manifest.get("schema") != MANIFEST_SCHEMA:
        return False, "schema_unsupported"
    if str(manifest.get("status") or "") not in GOLDEN_STATUSES:
        return False, "status_unknown"
    missions = manifest.get("missions")
    if not isinstance(missions, list) or not missions:
        return False, "missions_empty"
    ids = set()
    for m in missions:
        if not isinstance(m, dict) or not m.get("id"):
            return False, "mission_unnamed"
        if m["id"] in ids:
            return False, f"mission_duplicate:{m['id']}"
        ids.add(m["id"])
        for key in ("cost_budget_usd", "turn_budget"):
            try:
                if _num(m.get(key), f"{key}:{m['id']}") <= 0:
                    return False, f"budget_not_positive:{key}:{m['id']}"
            except GoldenSetInvalid:
                return False, f"budget_missing:{key}:{m['id']}"
        if str(m.get("input_sha256") or "") != input_hash(m):
            return False, f"input_hash_mismatch:{m['id']}"
        if not isinstance(m.get("gates"), list) or not m["gates"]:
            return False, f"gates_empty:{m['id']}"
    if str(manifest.get(SIGNATURE_FIELD) or "") != manifest_signature(manifest):
        return False, "signature_mismatch"
    return True, "ok"
