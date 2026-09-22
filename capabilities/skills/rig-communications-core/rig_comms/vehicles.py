"""v20 C3+C22 — vehicle selection + no-send advisory (Build Card C3 architectures)."""
from __future__ import annotations

VEHICLES = {
    "bluf": "conclusion → evidence → action",
    "value-first": "relevant observation → useful contribution → competence proof → low-friction ask",
    "decision-memo": "decision → why now → options → recommendation → risks → owner/date",
    "feedback": "observed strength → specific delta → consequence → requested behavior → checkpoint",
    "repair": "acknowledge impact → own contribution → corrective action → invitation",
    "crisis": "known → unknown → action underway → recipient action → next update",
    "gratitude": "specific memory → impact → enduring consequence → thanks",
    "no-send": "recommend silence, a call, a meeting, or delayed delivery",
}

# objective × stakes → vehicle (cheap-first ladder: the lowest-complexity
# vehicle that can cause the transformation is chosen, ties → fewer parts)
_MAP = {
    ("decide", "high"): "decision-memo", ("decide", "low"): "bluf",
    ("escalate", "high"): "crisis", ("escalate", "low"): "bluf",
    ("repair", "high"): "repair", ("repair", "low"): "repair",
    ("appreciate", "high"): "gratitude", ("appreciate", "low"): "gratitude",
    ("persuade", "high"): "value-first", ("persuade", "low"): "value-first",
    ("ask", "high"): "bluf", ("ask", "low"): "bluf",
    ("inform", "high"): "bluf", ("inform", "low"): "bluf",
    ("align", "high"): "decision-memo", ("align", "low"): "bluf",
}


def choose(intent) -> dict:
    """intent: CommunicationIntent (or duck-typed). Returns vehicle + why + no-send flag."""
    obj = intent.objective
    stakes = "high" if intent.context.stakes in ("high", "critical") else "low"
    vehicle = _MAP.get((obj, stakes), "bluf")

    # C22 no-send triggers (deterministic, text is the wrong vehicle):
    reasons = []
    acts = " ".join(str(a).lower() for a in intent.desired_recipient_state.do)
    feels = " ".join(str(f).lower() for f in intent.desired_recipient_state.feel)
    if obj == "repair" and ("angry" in feels or "conflict" in feels or "fired" in acts):
        reasons.append("written tone would amplify conflict — recommend a call")
    if obj == "escalate" and intent.context.urgency == "immediate" and stakes == "high":
        reasons.append("immediate high-stakes news belongs in a call, not text")
    if not intent.evidence.claims and obj == "persuade":
        reasons.append("abstain-then-research (C12): persuade with zero claims is spin — gather evidence first")
    if reasons:
        vehicle = "no-send"

    return {"vehicle": vehicle, "structure": VEHICLES[vehicle],
            "why": f"cheapest valid vehicle for {obj}/{intent.context.stakes} stakes",
            "no_send_reasons": reasons}


def demo() -> bool:
    from .models import CommunicationIntent, RecipientState, Context, Evidence
    i = CommunicationIntent(objective="decide",
                            desired_recipient_state=RecipientState(do=["approve"]),
                            context=Context(stakes="high"))
    assert choose(i)["vehicle"] == "decision-memo"
    hot = CommunicationIntent(
        objective="repair",
        desired_recipient_state=RecipientState(feel=["angry about the missed deadline"]),
        context=Context(stakes="high"))
    r = choose(hot)
    assert r["vehicle"] == "no-send" and "call" in r["no_send_reasons"][0]
    spin = CommunicationIntent(objective="persuade",
                               desired_recipient_state=RecipientState(believe=["we should move"]),
                               evidence=Evidence(claims=[]))
    assert choose(spin)["vehicle"] == "no-send"
    return True


if __name__ == "__main__":
    print("vehicles demo OK" if demo() else "FAIL")
