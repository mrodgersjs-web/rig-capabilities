"""v20 golden replay suite — Build Card cases as permanent fixtures.

Every case is an evaluator transcript (the deterministic stand-in for the
evaluator agents' output) run through the REAL stack: claims.lint_ledger →
energy.evaluate → roles.issue_verifier. `expect: pass` must be admitted;
`expect: fail` must be refused on its named floor. Planted-failure doctrine:
if a gate stops firing, this suite goes red.

Run: python3 -m rig_comms.golden  (exit 0 = all 20 cases behave)
"""
from __future__ import annotations
import sys

from . import claims, energy, roles

# one shared green profile; cases mutate exactly what the card names
_GREEN = {"fidelity": 0.97, "audience": 0.9, "clarity": 0.92, "warmth": 0.8,
          "competence": 0.85, "evidence": 0.95, "voice": 0.9, "risk": 0.95,
          "moving_parts": 0.9, "first_sentence_value": True,
          "provenance_backed": True, "screenshot_safety": True,
          "voice_drift": 0.1, "ask_latency_secs": 4.0}
_GOOD_CLAIMS = [{"claim": "cut onboarding 9d→2d in July", "kind": "fact",
                 "provenance": "ops/metrics-2026-07.csv", "externally_checkable": True}]

MUST_PASS = [
    ("cold-founder-outreach", "low", {}, "unique opening, value before ask, sourced proof"),
    ("warm-introduction", "low", {}, "mutual connection stated in first sentence"),
    ("executive-escalation", "high", {"ask_latency_secs": 6.0}, "decision visible in first screen"),
    ("underperformance-feedback", "high", {"archetype_floor_warmth": 0.70,
                                           "ask_latency_secs": 8.0}, "warm but unambiguous"),
    ("client-scope-correction", "high", {"ask_latency_secs": 7.0}, "boundary + options, no blame"),
    ("crisis-update", "critical", {"archetype_floor_competence": 0.75}, "known/unknown/action separated"),
    ("meeting-followup", "low", {"ask_latency_secs": 3.0}, "every commitment has owner and date"),
    ("gratitude-note", "low", {"ask_latency_secs": 9.0}, "specific memory, durable effect"),
    ("no-send-case", "low", {}, "vehicles.choose returns no-send; no message shipped"),
    ("channel-conversion", "low", {}, "email/DM/spoken variants keep same claims+ask"),
]

MUST_FAIL = [
    ("throat-clearing-baseline", "low",
     {"first_sentence_value": False}, "first useful sentence",
     "'Hope you're well' + two paragraphs of sender background"),
    ("decorative-affinity", "low",
     {"fabricated_affinity": True}, "fabricated affinity",
     "'Like you, I believe AI will change everything'"),
    ("labeled-not-shown", "low",
     {"claim_support": 0.0}, "claim support",
     "'resilient/battle-tested/Swiss Army knife' with no evidence"),
    ("fake-urgency", "low",
     {"deceptive_urgency": True}, "deceptive urgency", "Fake 'urgent' subject line"),
    ("invasive-personalization", "low",
     {"provenance_backed": False}, "provenance-backed",
     "Personalization from sensitive/unverified data"),
    ("warm-laundered-layoff", "high",
     {"warmth": 0.95, "fidelity": 0.5}, "fidelity",
     "Praise concealing a negative employment decision"),
    ("orphan-statistic", "low",
     {"claim_support": 0.5}, "claim support", "AI statistic without provenance"),
    ("overclaimed-crisis", "critical",
     {"undisclosed_uncertainty": True}, "undisclosed uncertainty",
     "Crisis assurance exceeding known evidence"),
    ("self-certified-draft", "low", {},
     "GEV_LOCK", "Drafting agent marks its own output done"),
    ("unapproved-external-send", "low",
     {"approval_ok": False}, "approval policy",
     "External send without human approval token"),
]


def run_case(name: str, stakes: str, mutate: dict, claims_list=None) -> dict:
    scores = dict(_GREEN)
    scores.update(mutate)
    if mutate.get("claim_support") is None and "claim_support" in mutate:
        scores["claim_support"] = mutate["claim_support"]
    lint = claims.lint_ledger(claims_list or _GOOD_CLAIMS)
    scores.setdefault("claim_support", lint["claim_support"])
    ev = energy.evaluate(scores, stakes)
    # GEV case: generator tries to close its own run
    issuer = "architect" if name == "self-certified-draft" else "verifier"
    verdict = roles.issue_verdict(issuer, "pass", ev["floors_ok"] and ev["ship_eligible"])
    blockers = ev["floor_failures"] + ([verdict["reason"]] if not verdict["admitted"] else [])
    return {"case": name, "admitted": verdict["admitted"], "blockers": blockers,
            "e_comm": ev["e_comm"]}


def run_suite() -> dict:
    results, green = [], True
    for name, stakes, mutate, why in MUST_PASS:
        r = run_case(name, stakes, mutate)
        ok = r["admitted"]
        green &= ok
        results.append({**r, "expect": "pass", "ok": ok, "note": why})
    for name, stakes, mutate, floor, why in MUST_FAIL:
        r = run_case(name, stakes, mutate)
        ok = (not r["admitted"]) and any(floor.lower() in b.lower() for b in r["blockers"])
        green &= ok
        results.append({**r, "expect": "fail", "ok": ok, "note": why})
    return {"total": len(results), "green": green,
            "must_pass": len(MUST_PASS), "must_fail": len(MUST_FAIL), "results": results}


def main() -> int:
    s = run_suite()
    for r in s["results"]:
        mark = "OK " if r["ok"] else "RED"
        print(f"{mark} {r['case']:28s} expect={r['expect']:4s} admitted={r['admitted']}")
    print(f"\ngolden suite: {s['total']} cases, green={s['green']}")
    return 0 if s["green"] else 1


if __name__ == "__main__":
    sys.exit(main())
