"""v20 frozen schemas — Build Card "System boundary" (2026-09-07), stdlib only.

CommunicationIntent in, CommunicationPacket out. validate() returns named
errors, never raises on bad input. packet_hash is sha256 over canonical JSON
(sorted keys) with the hash field excluded — deterministic and replayable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict

OBJECTIVES = ("inform", "ask", "decide", "persuade", "repair",
              "appreciate", "escalate", "align")
RELATIONSHIPS = ("cold", "warm", "internal", "client", "public", "intimate")
CHANNELS = ("email", "dm", "memo", "proposal", "post", "script", "meeting_followup")
STAKES = ("low", "medium", "high", "critical")
URGENCY = ("low", "normal", "high", "immediate")
CONFIDENTIALITY = ("public", "internal", "confidential", "restricted")
VERDICTS = ("pass", "revise", "escalate", "abstain")


@dataclass
class Audience:
    identity: str = ""
    role: str = ""
    relationship: str = "cold"
    knowledge_state: list = field(default_factory=list)
    priorities: list = field(default_factory=list)
    objections: list = field(default_factory=list)
    communication_norms: list = field(default_factory=list)


@dataclass
class RecipientState:
    know: list = field(default_factory=list)
    feel: list = field(default_factory=list)
    believe: list = field(default_factory=list)
    do: list = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.know or self.feel or self.believe or self.do)


@dataclass
class Context:
    channel: str = "email"
    stakes: str = "medium"
    urgency: str = "normal"
    deadline: str | None = None


@dataclass
class Evidence:
    claims: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    proof_artifacts: list = field(default_factory=list)


@dataclass
class Constraints:
    max_words: int | None = None
    required_points: list = field(default_factory=list)
    forbidden_claims: list = field(default_factory=list)
    confidentiality: str = "public"


@dataclass
class CommunicationIntent:
    objective: str = ""
    desired_recipient_state: RecipientState = field(default_factory=RecipientState)
    audience: Audience = field(default_factory=Audience)
    context: Context = field(default_factory=Context)
    evidence: Evidence = field(default_factory=Evidence)
    constraints: Constraints = field(default_factory=Constraints)
    voice_profile: str = "fingerprint-v2"
    approval_policy: str = "external-send-requires-human"

    def validate(self) -> list[str]:
        e = []
        if self.objective not in OBJECTIVES:
            e.append(f"objective must be one of {OBJECTIVES}")
        if self.desired_recipient_state.is_empty():
            e.append("C1 proof obligation: state what must change for the recipient "
                     "(know/feel/believe/do all empty — 'make it sound better' is not an objective)")
        if self.audience.relationship not in RELATIONSHIPS:
            e.append(f"audience.relationship must be one of {RELATIONSHIPS}")
        if self.context.channel not in CHANNELS:
            e.append(f"context.channel must be one of {CHANNELS}")
        if self.context.stakes not in STAKES:
            e.append(f"context.stakes must be one of {STAKES}")
        if self.context.urgency not in URGENCY:
            e.append(f"context.urgency must be one of {URGENCY}")
        if self.constraints.confidentiality not in CONFIDENTIALITY:
            e.append(f"confidentiality must be one of {CONFIDENTIALITY}")
        return e

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CommunicationIntent":
        return cls(
            objective=d.get("objective", ""),
            desired_recipient_state=RecipientState(**(d.get("desired_recipient_state") or {})),
            audience=Audience(**(d.get("audience") or {})),
            context=Context(**(d.get("context") or {})),
            evidence=Evidence(**(d.get("evidence") or {})),
            constraints=Constraints(**(d.get("constraints") or {})),
            voice_profile=d.get("voice_profile", "fingerprint-v2"),
            approval_policy=d.get("approval_policy", "external-send-requires-human"),
        )


@dataclass
class AudienceModel:
    known: list = field(default_factory=list)
    inferred: list = field(default_factory=list)
    unknown: list = field(default_factory=list)


@dataclass
class CommunicationPacket:
    message: str = ""
    subject_options: list = field(default_factory=list)
    channel_variant: str | None = None
    audience_model: AudienceModel = field(default_factory=AudienceModel)
    claim_ledger: list = field(default_factory=list)
    risk_flags: list = field(default_factory=list)
    evaluation_scores: dict = field(default_factory=dict)
    revision_trace: list = field(default_factory=list)
    verifier_decision: str | None = None
    approval_required: bool = True
    followup_plan: list = field(default_factory=list)
    packet_hash: str = ""

    def compute_hash(self) -> str:
        body = asdict(self)
        body.pop("packet_hash")
        canon = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
        return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()

    def finalize(self) -> "CommunicationPacket":
        self.packet_hash = self.compute_hash()
        return self

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CommunicationPacket":
        return cls(
            message=d.get("message", ""),
            subject_options=list(d.get("subject_options") or []),
            channel_variant=d.get("channel_variant"),
            audience_model=AudienceModel(**(d.get("audience_model") or {})),
            claim_ledger=list(d.get("claim_ledger") or []),
            risk_flags=list(d.get("risk_flags") or []),
            evaluation_scores=dict(d.get("evaluation_scores") or {}),
            revision_trace=list(d.get("revision_trace") or []),
            verifier_decision=d.get("verifier_decision"),
            approval_required=bool(d.get("approval_required", True)),
            followup_plan=list(d.get("followup_plan") or []),
            packet_hash=d.get("packet_hash", ""),
        )


# C2 proof obligation: every personalization element has provenance and relevance.
def audience_model_errors(am: AudienceModel) -> list[str]:
    e = []
    for item in list(am.known) + list(am.inferred):
        if isinstance(item, dict):
            if not item.get("provenance"):
                e.append(f"personalization element {item.get('field', item)!r} lacks provenance (C2)")
            if item in list(am.inferred) and isinstance(item, dict) and not item.get("relevance"):
                e.append(f"inferred element {item.get('field', item)!r} lacks relevance (C2)")
    return e


def demo() -> bool:
    bad = CommunicationIntent.from_dict({"objective": "ask"})
    assert any("C1 proof obligation" in m for m in bad.validate())
    ok = CommunicationIntent.from_dict({
        "objective": "ask",
        "desired_recipient_state": {"do": ["approve the scoping call"]},
        "audience": {"identity": "COO", "relationship": "cold"},
        "context": {"channel": "email", "stakes": "high"},
    })
    assert ok.validate() == []
    p = CommunicationPacket(message="hi", evaluation_scores={"warmth": 0.8}).finalize()
    assert p.packet_hash.startswith("sha256:")
    assert CommunicationPacket.from_dict(p.to_dict()).packet_hash == p.packet_hash
    return True


if __name__ == "__main__":
    print("models demo OK" if demo() else "FAIL")
