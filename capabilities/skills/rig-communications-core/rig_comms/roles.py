"""v20 GEV role topology — Build Card's 11 agents, with the "cannot" rules in code.

The server enforces separation structurally: a verdict token issued by any
role other than `verifier` (or the human approver) is rejected, no matter who
asks. Prompts (mcp.py) carry the same rules in text; this module is the code gate.
"""
from __future__ import annotations

ROLES = {
    "conductor":      {"kind": "router",    "cannot": ["verify its own run", "author message text"]},
    "cartographer":   {"kind": "researcher", "cannot": ["draft persuasive copy"]},
    "evidence-clerk": {"kind": "custodian",  "cannot": ["draft", "score voice"]},
    "architect":      {"kind": "generator",  "cannot": ["score its draft", "release its draft"]},
    "voice-smith":    {"kind": "generator",  "cannot": ["alter facts", "alter commitments",
                                                        "alter prices", "alter dates", "alter risk posture"]},
    "simulator":      {"kind": "evaluator",  "cannot": ["rewrite the message"]},
    "critic-clarity": {"kind": "evaluator",  "cannot": ["rewrite the message"]},
    "critic-warmth":  {"kind": "evaluator",  "cannot": ["rewrite the message"]},
    "redteam":        {"kind": "evaluator",  "cannot": ["rewrite the message"]},
    "verifier":       {"kind": "termination", "cannot": ["draft", "repair the message"]},
    "human":          {"kind": "approver",   "cannot": []},
}

# Which role may issue which decision (build card: sole termination authority).
MAY_ISSUE = {
    "pass": ("verifier", "human"),
    "revise": ("verifier",),
    "escalate": ("verifier", "human"),
    "abstain": ("verifier", "human"),
}


def role_cannot(role: str) -> list[str]:
    return ROLES.get(role, [])


def may_issue(role: str, decision: str) -> bool:
    """Structural no-self-verification: only verifier/human close a run."""
    return decision in MAY_ISSUE and role in MAY_ISSUE[decision]


def issue_verdict(role: str, decision: str, floors_ok: bool) -> dict:
    """The ONLY emitter of an admitted verdict. Any other caller gets REFUSED."""
    if not may_issue(role, decision):
        return {"admitted": False,
                "reason": f"GEV_LOCK: role {role!r} may not issue {decision!r}; "
                          f"termination belongs to verifier/human only (no self-verification)"}
    if decision == "pass" and not floors_ok:
        return {"admitted": False,
                "reason": "HARD_FLOOR: pass refused while hard floors are red (beauty cannot buy an unsupported claim)"}
    return {"admitted": True, "role": role, "decision": decision}


def demo() -> bool:
    assert not may_issue("architect", "pass")            # builder can't certify
    assert may_issue("verifier", "pass")
    assert issue_verdict("conductor", "pass", True)["admitted"] is False  # conductor can't verify its own run
    assert issue_verdict("verifier", "pass", False)["admitted"] is False  # floors beat the verifier too
    ok = issue_verdict("verifier", "pass", True)
    assert ok["admitted"]
    assert "self-verification" in issue_verdict("architect", "pass", True)["reason"]
    return True


if __name__ == "__main__":
    print("roles demo OK" if demo() else "FAIL")
