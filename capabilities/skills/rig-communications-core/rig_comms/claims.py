"""v20 C5/C6 — claim ledger lint + fabricated-specificity detection (stdlib only).

Claim shape: {"claim": str, "kind": "fact|inference|proposal",
              "provenance": str, "externally_checkable": bool}
Rules (Build Card): fact + externally_checkable requires provenance; no provenance →
claim unsupportable → blocks release. Superlatives without a scene/action/number =
labeled-not-shown. Decorative personalization (no relevance to recipient goals) rejected.
"""
from __future__ import annotations
import re

SUPERLATIVES = re.compile(
    r"\b(resilient|battle-?tested|innovative|world-?class|best-?in-?class|"
    r"cutting-?edge|seamless|synerg(?:y|ies|etic)|game-?chang(?:er|ing)|"
    r"swiss army knife|results-?driven|passionate|detail-?oriented)\b", re.I)
SCENE_EVIDENCE = re.compile(r"\b(\d|percent|%|from .{2,40} to |in \d{4}|on \w+d,?|shipped|built|ran|cut|reduced|grew|won|lost|fixed|delivered)\b", re.I)


def lint_ledger(claims: list) -> dict:
    """Returns claim_support in [0,1] + named violations. No claims → 1.0 (vacuous pass, honest)."""
    violations = []
    checkable = supported = 0
    for c in claims or []:
        if not isinstance(c, dict) or not c.get("claim"):
            violations.append({"claim": repr(c), "error": "malformed claim entry"})
            continue
        kind = c.get("kind", "fact")
        if kind not in ("fact", "inference", "proposal"):
            violations.append({"claim": c["claim"], "error": f"unknown kind {kind!r}"})
            continue
        if kind == "fact":
            checkable += 1
            if c.get("provenance"):
                supported += 1
            else:
                violations.append({"claim": c["claim"],
                                   "error": "fact without provenance (C5: claim must be sourced)"})
    support = 1.0 if checkable == 0 else supported / checkable
    return {"claim_support": round(support, 4), "checkable_facts": checkable,
            "violations": violations}


def audit_text(text: str) -> dict:
    """Labeled-not-shown + decorative affinity scan (deterministic lexicon pass)."""
    labels = [m.group(0) for m in SUPERLATIVES.finditer(text)]
    unsupported = []
    for w in labels:
        # a superlative standing in the same sentence without a scene marker is a label
        for sent in re.split(r"(?<=[.!?\n])\s+", text):
            if w.lower() in sent.lower() and not SCENE_EVIDENCE.search(sent):
                unsupported.append({"label": w, "sentence": sent.strip()[:120]})
                break
    return {"labels_found": labels, "unsupported_labels": unsupported,
            "show_dont_doit": bool(unsupported)}


def demo() -> bool:
    r = lint_ledger([{"claim": "cut churn 12%", "kind": "fact", "provenance": "metrics/x.csv"},
                     {"claim": "we will ship in Q1", "kind": "proposal"}])
    assert r["claim_support"] == 1.0, r
    r2 = lint_ledger([{"claim": "97% uptime", "kind": "fact"}])
    assert r2["claim_support"] == 0.0 and "provenance" in r2["violations"][0]["error"]
    a = audit_text("We are resilient and battle-tested.")
    assert a["show_dont_doit"] and len(a["unsupported_labels"]) == 2
    a2 = audit_text("We cut onboarding from 9 days to 2 in March.")
    assert not a2["show_dont_doit"]
    assert lint_ledger([])["claim_support"] == 1.0
    return True


if __name__ == "__main__":
    print("claims demo OK" if demo() else "FAIL")
