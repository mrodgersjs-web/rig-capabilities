"""A1 run.py — deterministic NO-LLM IQRSQPI orchestrator.

Chains the 7 A1 steps with gates between them, matching the run_iqrsqpi loop
from the lattice card but specialized for PYTHON_ONLY:

    Intent -> [UNKNOWN? escalate to A3.1]
    Question -> Research -> Solution -> Quality -> [fail? stop]
    Proof -> Integrate

There is NO model in the decision path. The optional <=60-word shim at A1.4 is
injectable and defaults to None (fully deterministic). Run as a module:

    python3 -m platform.archetypes.a1_python_only.run        # demo
or via the importable A1Pipeline.run() API.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from . import a1_1_intent, a1_2_question, a1_3_research, a1_4_solution
from . import a1_5_quality, a1_6_proof, a1_7_integrate
from .a1_3_research import DeterministicFetcher, Fetcher
from .a1_4_solution import ShimFn
from .a1_7_integrate import Approver, Executor
from .contract import IntentKey, PipelineInput, PipelineOutput

ESCALATION_TARGET = "A3.1"


class A1Pipeline:
    """Deterministic A1 IQRSQPI pipeline."""

    def __init__(
        self,
        *,
        fetcher: Optional[Fetcher] = None,
        shim: Optional[ShimFn] = None,
        executor: Optional[Executor] = None,
        approver: Optional[Approver] = None,
        audit_path: Optional[Path] = None,
        signer: str = "a1_python_only",
    ) -> None:
        self.fetcher = fetcher or DeterministicFetcher()
        self.shim = shim  # None => no LLM touch at all
        self.executor = executor
        self.approver = approver
        self.audit_path = audit_path
        self.signer = signer

    def run(self, pin: PipelineInput) -> PipelineOutput:
        # A1.1 Intent
        intent = a1_1_intent.run(pin.payload)
        if intent == IntentKey.UNKNOWN:
            return PipelineOutput(
                status="escalate",
                intent=intent.value,
                escalation_target=ESCALATION_TARGET,
            )

        # A1.2 Question (canned)
        query = a1_2_question.run(intent, pin.context)

        # A1.3 Research (deterministic fan-out)
        pack = a1_3_research.run(query, self.fetcher)

        # A1.4 Solution (templated body + optional shim)
        draft = a1_4_solution.run(pack, self.shim)

        # A1.5 Quality (hard gates)
        quality = a1_5_quality.run(draft)
        if not quality.passed:
            return PipelineOutput(
                status="quality_failed",
                intent=intent.value,
                quality=quality,
            )

        # A1.6 Proof (SHA-256 ProofPacket)
        proof = a1_6_proof.run(draft, quality, self.signer)

        # A1.7 Integrate (conditional approval + append-only audit)
        integration = None
        if pin.action is not None:
            result = a1_7_integrate.run(
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
            proof=proof,
            quality=quality,
            integration_status=integration,
        )


def _demo() -> PipelineOutput:
    from .contract import Action, InboundPayload

    fetcher = DeterministicFetcher(
        {"sql://crm/leads": [{"name": "Acme Corp", "score": 87}]}
    )
    pipeline = A1Pipeline(fetcher=fetcher)
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
    if out.proof is not None:
        print("artifact_hash:", out.proof.artifact_hash)
        print("gates:", out.proof.gates)
        print("sources:", out.proof.sources)
    print("integration:", out.integration_status)
