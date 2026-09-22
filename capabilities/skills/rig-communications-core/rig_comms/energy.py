"""v20 E_comm — Build Card objective function + hard floors (stdlib only).

E_comm = Σ w_i·E_i over 8 dimensions; energy = 1 - quality per dimension.
Hard floors OVERRIDE the weighted score: a beautiful message with an
unsupported claim fails. σ = 0.3·d_struct + 0.7·d_behavior; 5σ → deep review.

`scores` contract (all present keys in [0,1]; missing dimension → energy 1.0,
never a free pass):
  fidelity, audience, clarity, warmth, competence, evidence, voice, risk
Optional signals:
  ask_latency_secs (float), first_sentence_value (bool),
  claim_support (float, 1.0 when no checkable claims),
  fabricated_affinity/deceptive_urgency/undisclosed_uncertainty (bool, default False),
  screenshot_safety (bool), provenance_backed (bool), voice_drift (float),
  confidentiality_ok/approval_ok (bool, default True),
  archetype_floor_warmth/competence (float override, archetype policy)
"""
from __future__ import annotations

# weights from Build Card "Default weighting by stakes"
WEIGHTS_LOW = {"fidelity": 0.18, "audience": 0.18, "clarity": 0.18, "relational": 0.14,
               "evidence": 0.12, "voice": 0.12, "risk": 0.05, "moving_parts": 0.03}
WEIGHTS_HIGH = {"fidelity": 0.20, "audience": 0.15, "clarity": 0.15, "relational": 0.12,
                "evidence": 0.18, "voice": 0.07, "risk": 0.11, "moving_parts": 0.02}
SIGMA_DEEP_REVIEW = 5.0
VOICE_DRIFT_MAX = 0.25
ASK_LATENCY_MAX_SECS = 10.0
FIDELITY_FLOOR = 0.95


def weights(stakes: str) -> dict:
    return WEIGHTS_HIGH if stakes in ("high", "critical") else WEIGHTS_LOW


def composite_sigma(d_struct: float, d_behavior: float) -> float:
    """Behavioral deviation carries more weight than structural novelty."""
    return 0.3 * d_struct + 0.7 * d_behavior


def evaluate(scores: dict, stakes: str = "medium") -> dict:
    w = weights(stakes)
    dims = {
        "fidelity": scores.get("fidelity"),
        "audience": scores.get("audience"),
        "clarity": scores.get("clarity"),
        # warmth and competence are ONE relational dimension (their mean) per the
        # weight table's single relational row — but floors apply per axis.
        "relational": None if scores.get("warmth") is None or scores.get("competence") is None
                      else (scores["warmth"] + scores["competence"]) / 2.0,
        "evidence": scores.get("evidence"),
        "voice": scores.get("voice"),
        "risk": scores.get("risk"),
        "moving_parts": scores.get("moving_parts"),
    }
    contributions, missing = {}, []
    energy = 0.0
    for k, q in dims.items():
        if q is None:
            missing.append(k)
            contributions[k] = w[k]  # missing → max energy, never free pass
            energy += w[k]
        else:
            contributions[k] = round(w[k] * (1.0 - q), 6)
            energy += w[k] * (1.0 - q)

    floors = []
    def fail(cond, msg):
        if not cond:
            floors.append(msg)

    fid = scores.get("fidelity")
    fail(fid is not None and fid >= FIDELITY_FLOOR, f"intent fidelity {fid} < {FIDELITY_FLOOR}")
    cs = scores.get("claim_support", 1.0)
    fail(cs >= 1.0, f"claim support {cs} < 1.00 for externally checkable material claims")
    lat = scores.get("ask_latency_secs", 0.0)
    fail(lat <= ASK_LATENCY_MAX_SECS, f"ask not identifiable in <=10s (latency {lat}s)")
    fail(scores.get("first_sentence_value", False),
         "first useful sentence must contain new value, decision, or context")
    for flag, name in (("fabricated_affinity", "fabricated affinity"),
                       ("deceptive_urgency", "deceptive urgency"),
                       ("undisclosed_uncertainty", "undisclosed uncertainty")):
        fail(not scores.get(flag, False), f"no {name} permitted")
    fail(scores.get("provenance_backed", False), "required audience facts must be provenance-backed")
    warm_min = scores.get("archetype_floor_warmth", 0.70)
    comp_min = scores.get("archetype_floor_competence", 0.70)
    if scores.get("warmth") is not None:
        fail(scores["warmth"] >= warm_min, f"warmth {scores['warmth']} < {warm_min}")
    if scores.get("competence") is not None:
        fail(scores["competence"] >= comp_min, f"competence {scores['competence']} < {comp_min}")
    fail(scores.get("screenshot_safety", False), "screenshot/public-page safety must pass")
    vd = scores.get("voice_drift")
    fail(vd is not None and vd < VOICE_DRIFT_MAX, f"voice drift {vd} must be below {VOICE_DRIFT_MAX}")
    fail(scores.get("confidentiality_ok", True), "confidentiality policy failed")
    fail(scores.get("approval_ok", True), "approval policy failed")

    return {
        "e_comm": round(energy, 6),
        "weights": w,
        "contributions": contributions,
        "missing_dimensions": missing,
        "floors_ok": not floors,
        "floor_failures": floors,
        "ship_eligible": (not floors) and not missing,
    }


def demo() -> bool:
    good = {"fidelity": 0.97, "audience": 0.9, "clarity": 0.9, "warmth": 0.8,
            "competence": 0.85, "evidence": 0.95, "voice": 0.9, "risk": 0.95,
            "moving_parts": 0.9, "first_sentence_value": True,
            "provenance_backed": True, "screenshot_safety": True, "voice_drift": 0.1}
    r = evaluate(good, "high")
    assert r["floors_ok"] and r["ship_eligible"], r
    # hard floor beats weighted beauty: high scores + one unsupported claim → red
    beautiful = dict(good, claim_support=0.9)
    r2 = evaluate(beautiful, "low")
    assert not r2["floors_ok"] and any("claim support" in f for f in r2["floor_failures"])
    # missing dimension is never a free pass
    r3 = evaluate({k: v for k, v in good.items() if k != "clarity"}, "low")
    assert "clarity" in r3["missing_dimensions"] and not r3["ship_eligible"]
    # sigma weighting favors behavior
    assert composite_sigma(10, 0) < composite_sigma(0, 10)
    return True


if __name__ == "__main__":
    print("energy demo OK" if demo() else "FAIL")
