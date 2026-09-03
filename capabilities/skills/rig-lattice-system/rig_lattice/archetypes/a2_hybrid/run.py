"""A2 run.py — schema-bounded HYBRID orchestrator.

The rung between frozen A1 (no LLM) and approval-gated A3/A4. A2 runs the SAME
IQRSQPI shape as A1 but the Solution step (A2.4) calls a MOCKABLE LLM at
temperature 0 constrained to a strict output schema, then forces every byte
of model output through a validator chain before anything becomes a Draft:

    Intent -> [UNKNOWN? escalate to A3]
    Question -> Research
    Solution: LLM(temp=0, schema) -> parse -> validate -> [bad schema? stop]
                                                        -> [low confidence? escalate]
    Quality -> [fail? stop]
    Proof  -> Integrate

Runs with NO API key: LLMClient defaults to OfflineMockLLM, which returns
deterministic, schema-valid JSON derived from the research rows. Swap in a
real client (callable matching LLMClient) without touching the chain.

Run as a module from platform/:

    python3 -m archetypes.a2_hybrid.run        # offline demo, no key
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Optional, Protocol

# Reuse the FROZEN A1 steps that A2 does not change (intent/question/research
# are deterministic at this band; only Solution/Quality/Proof differ).
try:  # package-root import
    from a1_python_only import a1_1_intent, a1_2_question, a1_3_research
    from a1_python_only.a1_3_research import DeterministicFetcher, Fetcher
    from a1_python_only.a1_7_integrate import (
        Approver,
        Executor,
        run as integrate_run,
    )
    from a1_python_only.a1_5_quality import SHIM_WORD_LIMIT
except ImportError:  # relative import
    from ..a1_python_only import a1_1_intent, a1_2_question, a1_3_research
    from ..a1_python_only.a1_3_research import DeterministicFetcher, Fetcher
    from ..a1_python_only.a1_7_integrate import (
        Approver,
        Executor,
        run as integrate_run,
    )
    from ..a1_python_only.a1_5_quality import SHIM_WORD_LIMIT

from . import proof as a2_proof
from .contract import (
    A2Schema,
    CONFIDENCE_FLOOR,
    Draft,
    IntentKey,
    LLMRequest,
    LLMResponse,
    PipelineInput,
    PipelineOutput,
    QualityResult,
    ResearchPack,
    Source,
)

ESCALATION_TARGET = "A3"


# --------------------------------------------------------------------------- #
# LLM client surface — temperature-0, schema-constrained, MOCKABLE.
# --------------------------------------------------------------------------- #
class LLMClient(Protocol):
    def complete(self, request: LLMRequest) -> LLMResponse:
        ...


class OfflineMockLLM:
    """Deterministic offline LLM. Returns schema-valid JSON with NO API key
    and NO network. The output is a pure function of the prompt, so the whole
    A2 chain is reproducible — the same research rows always yield the same
    draft and therefore the same artifact_hash."""

    model = "offline-mock"

    def __init__(self, *, force_invalid: bool = False, confidence: float | None = None):
        # Test hooks: force a schema-breaking response, or pin a confidence.
        self._force_invalid = force_invalid
        self._confidence = confidence

    def complete(self, request: LLMRequest) -> LLMResponse:
        if self._force_invalid:
            # Simulate a model that ignored the schema (raw prose, no JSON).
            return LLMResponse(
                raw_text="Sure! Here is your summary in plain prose.",
                parsed={},
                model=self.model,
            )
        # Deterministic "generation": derive a headline from the prompt's first
        # quoted record, a personalization line, and a confidence score that
        # rises with how much signal the prompt carries.
        headline = _extract_headline(request.prompt)
        record_count = _extract_count(request.prompt)
        confidence = (
            self._confidence
            if self._confidence is not None
            else _score_confidence(record_count, headline)
        )
        obj = {
            "headline": headline,
            "personalization": f"Tailored for the {record_count}-record context.",
            "confidence": round(confidence, 3),
        }
        return LLMResponse(
            raw_text=json.dumps(obj, sort_keys=True),
            parsed=obj,
            model=self.model,
        )


def _extract_headline(prompt: str) -> str:
    m = re.search(r"HEADLINE=([^\n|]+)", prompt)
    return m.group(1).strip() if m else "no records found"


def _extract_count(prompt: str) -> int:
    m = re.search(r"RECORDS=(\d+)", prompt)
    return int(m.group(1)) if m else 0


def _score_confidence(record_count: int, headline: str) -> float:
    # No records or an empty headline => collapse below the floor (escalate).
    if record_count == 0 or headline == "no records found":
        return 0.30
    base = 0.70 + min(record_count, 3) * 0.08
    return min(base, 0.97)


# --------------------------------------------------------------------------- #
# A2.4 Solution — LLM behind parser -> validator -> Draft.
# --------------------------------------------------------------------------- #
def _build_prompt(pack: ResearchPack) -> str:
    headline = "no records found"
    if pack.rows:
        first = pack.rows[0]
        for k, v in first.items():
            if not k.startswith("_") and isinstance(v, str):
                headline = v
                break
        else:
            headline = "record available"
    return (
        "Summarize the sourced records as strict JSON matching the schema "
        "{headline, personalization, confidence}. Temperature 0.\n"
        f"RECORDS={len(pack.rows)}\nHEADLINE={headline}"
    )


def parse_llm(response: LLMResponse) -> Optional[dict]:
    """Parse model output to a dict. Prefer the structured `parsed` field; fall
    back to parsing raw_text as JSON. Returns None if it is not parseable —
    which the validator treats as a schema failure (NOT an exception/crash)."""
    if response.parsed:
        return dict(response.parsed)
    try:
        obj = json.loads(response.raw_text)
        return obj if isinstance(obj, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def validate_schema(obj: Optional[dict]) -> Optional[A2Schema]:
    """Strict validator: every schema key present with the right type, no
    raw text leaking through. Returns a typed A2Schema or None (reject)."""
    if not isinstance(obj, dict):
        return None
    if not {"headline", "personalization", "confidence"} <= set(obj):
        return None
    headline = obj.get("headline")
    personalization = obj.get("personalization")
    confidence = obj.get("confidence")
    if not isinstance(headline, str) or not headline.strip():
        return None
    if not isinstance(personalization, str):
        return None
    if not isinstance(confidence, (int, float)):
        return None
    if not (0.0 <= float(confidence) <= 1.0):
        return None
    return A2Schema(
        headline=headline.strip(),
        personalization=personalization.strip(),
        confidence=float(confidence),
    )


def _clamp_shim(text: str) -> str:
    words = text.split()
    if len(words) <= SHIM_WORD_LIMIT:
        return text.strip()
    return " ".join(words[:SHIM_WORD_LIMIT]).strip()


def solution(
    pack: ResearchPack, client: LLMClient
) -> tuple[Optional[Draft], LLMResponse, Optional[A2Schema]]:
    """A2.4: call the schema-constrained LLM, parse, validate, build a Draft.
    Returns (draft_or_None, raw_response, validated_schema_or_None). A None
    draft means schema validation failed and the run layer must stop."""
    request = LLMRequest(prompt=_build_prompt(pack), temperature=0.0)
    response = client.complete(request)
    validated = validate_schema(parse_llm(response))
    if validated is None:
        return None, response, None
    body = (
        f"Summary based on {len(pack.rows)} sourced record(s): "
        f"{validated.headline}"
    )
    draft = Draft(
        body=body,
        personalization=_clamp_shim(validated.personalization),
        sources=list(pack.sources),
    )
    return draft, response, validated


# --------------------------------------------------------------------------- #
# A2.5 Quality — A1's hard gates PLUS a schema_valid gate.
# --------------------------------------------------------------------------- #
def quality(draft: Draft, schema_valid: bool) -> QualityResult:
    passed: list[str] = []
    if not schema_valid:
        return QualityResult(
            passed=False, gates_passed=passed, reason="llm output failed strict schema"
        )
    passed.append("schema_valid")

    if draft.body and draft.body.strip():
        passed.append("non_empty_body")
    else:
        return QualityResult(passed=False, gates_passed=passed, reason="empty body")

    if draft.sources:
        passed.append("source_per_claim")
    else:
        return QualityResult(
            passed=False, gates_passed=passed, reason="no source backs the draft"
        )

    if len((draft.personalization or "").split()) <= SHIM_WORD_LIMIT:
        passed.append("shim_within_limit")
    else:
        return QualityResult(
            passed=False,
            gates_passed=passed,
            reason=f"shim exceeds {SHIM_WORD_LIMIT} words",
        )
    return QualityResult(passed=True, gates_passed=passed, reason=None)


# --------------------------------------------------------------------------- #
# The A2 pipeline.
# --------------------------------------------------------------------------- #
class A2Pipeline:
    """Schema-bounded HYBRID IQRSQPI pipeline. Default LLM is the offline mock,
    so it runs reproducibly with NO API key."""

    def __init__(
        self,
        *,
        fetcher: Optional[Fetcher] = None,
        llm: Optional[LLMClient] = None,
        executor: Optional[Executor] = None,
        approver: Optional[Approver] = None,
        audit_path: Optional[Path] = None,
        confidence_floor: float = CONFIDENCE_FLOOR,
        signer: str = "a2_hybrid",
    ) -> None:
        self.fetcher = fetcher or DeterministicFetcher()
        self.llm = llm or OfflineMockLLM()
        self.executor = executor
        self.approver = approver
        self.audit_path = audit_path
        self.confidence_floor = confidence_floor
        self.signer = signer

    def run(self, pin: PipelineInput) -> PipelineOutput:
        model = getattr(self.llm, "model", "unknown")

        # A2.1 Intent (deterministic, reused from A1).
        intent = a1_1_intent.run(pin.payload)
        if intent == IntentKey.UNKNOWN:
            return PipelineOutput(
                status="escalate",
                intent=intent.value,
                escalation_target=ESCALATION_TARGET,
                model=model,
            )

        # A2.2 Question + A2.3 Research (deterministic, reused from A1).
        query = a1_2_question.run(intent, pin.context)
        pack = a1_3_research.run(query, self.fetcher)

        # A2.4 Solution: schema-constrained LLM -> parse -> validate.
        draft, response, validated = solution(pack, self.llm)
        if draft is None or validated is None:
            return PipelineOutput(
                status="schema_failed",
                intent=intent.value,
                schema_valid=False,
                model=model,
            )

        # Confidence collapse -> escalate to A3 (don't ship a low-trust draft).
        if validated.confidence < self.confidence_floor:
            return PipelineOutput(
                status="escalate",
                intent=intent.value,
                confidence=validated.confidence,
                schema_valid=True,
                escalation_target=ESCALATION_TARGET,
                model=model,
            )

        # A2.5 Quality (A1 hard gates + schema_valid).
        q = quality(draft, schema_valid=True)
        if not q.passed:
            return PipelineOutput(
                status="quality_failed",
                intent=intent.value,
                confidence=validated.confidence,
                schema_valid=True,
                quality=q,
                model=model,
            )

        # A2.6 Proof (SHA-256, binds the artifact to the exact model bytes).
        proof = a2_proof.run(draft, q, response, self.signer)

        # A2.7 Integrate (conditional approval + append-only audit; reuse A1).
        integration = None
        if pin.action is not None:
            result = integrate_run(
                proof,
                pin.action,
                executor=self.executor,
                approver=self.approver,
                audit_path=self.audit_path,
            )
            integration = result.status

        return PipelineOutput(
            status="completed",
            intent=intent.value,
            confidence=validated.confidence,
            schema_valid=True,
            proof=proof,
            quality=q,
            integration_status=integration,
            model=model,
        )


def _demo() -> PipelineOutput:
    from .contract import Action, InboundPayload

    fetcher = DeterministicFetcher(
        {"sql://crm/leads": [{"name": "Acme Corp", "score": 87}]}
    )
    pipeline = A2Pipeline(fetcher=fetcher)
    pin = PipelineInput(
        payload=InboundPayload(
            source="inbound_form", raw={"text": "please score this lead for me"}
        ),
        context={"lead_id": 42},
        action=Action(kind="noop", payload={}, requires_approval=False),
    )
    return pipeline.run(pin)


if __name__ == "__main__":
    out = _demo()
    print("status:", out.status)
    print("intent:", out.intent)
    print("model:", out.model)
    print("confidence:", out.confidence)
    print("schema_valid:", out.schema_valid)
    if out.proof is not None:
        print("artifact_hash:", out.proof.artifact_hash)
        print("gates:", out.proof.gates)
        print("sources:", out.proof.sources)
    print("integration:", out.integration_status)
